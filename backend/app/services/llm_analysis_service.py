from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import get_settings
from app.schemas.analysis import (
    AnalysisResultData,
    AnalysisResultEnvelope,
    SentimentScores,
)
from app.schemas.text_clean import TextCleanResult
from app.utils.localization import build_summary_en
from app.utils.prompt_builder import build_analysis_prompt
from app.utils.shop_alias import load_shop_catalog, load_standard_shop_names, normalize_english_alias

logger = logging.getLogger(__name__)


class LlmAnalysisService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def analyze(self, clean_result: TextCleanResult) -> AnalysisResultEnvelope:
        if not self.settings.dashscope_api_key:
            return self._fallback(clean_result, reason="missing_api_key")

        try:
            from openai import OpenAI
        except ModuleNotFoundError:
            return self._fallback(clean_result, reason="missing_openai_dependency")

        prompt = build_analysis_prompt(clean_result)
        client = OpenAI(
            api_key=self.settings.dashscope_api_key,
            base_url=self.settings.llm_api_base,
        )

        for _ in range(2):
            try:
                response = client.chat.completions.create(
                    model=self.settings.llm_model_name,
                    temperature=0.2,
                    response_format={"type": "json_object"},
                    messages=[
                        {
                            "role": "system",
                            "content": "你是严谨的食堂反馈结构化分析助手。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
                content = response.choices[0].message.content or "{}"
                payload = json.loads(content)
                result = self._coerce_payload(payload)
                return AnalysisResultEnvelope(
                    result=result,
                    source="llm",
                    fallback_used=False,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM analysis failed, retrying: %s", exc)

        return self._fallback(clean_result, reason="llm_error")

    @staticmethod
    def _coerce_payload(payload: dict[str, Any]) -> AnalysisResultData:
        raw_shop_name = str(payload.get("shop_name", "未知商铺")).strip() or "未知商铺"
        shop_name = LlmAnalysisService._resolve_shop_name(raw_shop_name)

        issue_categories = [
            str(item).strip()
            for item in list(payload.get("issue_categories", []))
            if str(item).strip()
        ]
        if not issue_categories:
            issue_categories = ["其他"]

        scores = payload.get("sentiment_scores", {})
        sentiment_scores = LlmAnalysisService._normalize_sentiment_scores(scores)
        issue_weights = LlmAnalysisService._normalize_issue_weights(
            issue_categories,
            payload.get("issue_weights", {}),
        )

        return AnalysisResultData(
            shop_name=shop_name,
            sentiment_label=payload.get("sentiment_label", "中性"),
            sentiment_scores=sentiment_scores,
            issue_categories=issue_categories,
            issue_weights=issue_weights,
            urgency=payload.get("urgency", "低"),
            summary=payload.get("summary", "暂无摘要。"),
            summary_en=payload.get("summary_en", "").strip()
            or build_summary_en(
                shop_name=shop_name,
                summary=payload.get("summary", "暂无摘要。"),
                sentiment_label=payload.get("sentiment_label", "中性"),
                issue_categories=issue_categories,
                urgency=payload.get("urgency", "低"),
            ),
        )

    @staticmethod
    def _resolve_shop_name(value: str) -> str:
        if value == "未知商铺":
            return value

        standard_shop_names = set(load_standard_shop_names())
        if value in standard_shop_names:
            return value

        normalized_value = normalize_english_alias(value)
        normalized_compact = normalized_value.replace(" ", "")

        for item in load_shop_catalog():
            standard_name = str(item["name"])
            name_en = str(item.get("name_en", "")).strip()
            category = str(item.get("category", "")).strip()
            category_en = str(item.get("category_en", "")).strip()
            aliases = [str(alias).strip() for alias in item.get("aliases", [])]
            aliases_en = [str(alias).strip() for alias in item.get("aliases_en", [])]

            if value in {name_en, category, category_en} or value in aliases:
                return standard_name

            normalized_candidates = [
                normalize_english_alias(name_en),
                normalize_english_alias(category_en),
                *(normalize_english_alias(alias) for alias in aliases_en),
            ]
            normalized_candidates = [
                candidate for candidate in normalized_candidates if candidate
            ]
            for candidate in normalized_candidates:
                if normalized_value == candidate:
                    return standard_name
                if normalized_compact and normalized_compact == candidate.replace(" ", ""):
                    return standard_name

        return "未知商铺"

    @staticmethod
    def _normalize_sentiment_scores(raw_scores: Any) -> SentimentScores:
        scores = dict(raw_scores or {})
        normalized = {
            "positive": max(0.0, float(scores.get("positive", 0.0) or 0.0)),
            "negative": max(0.0, float(scores.get("negative", 0.0) or 0.0)),
            "neutral": max(0.0, float(scores.get("neutral", 0.0) or 0.0)),
        }
        total = sum(normalized.values())
        if total <= 0:
            return SentimentScores(positive=0.33, negative=0.33, neutral=0.34)

        ordered_keys = ["positive", "negative", "neutral"]
        normalized_values = {
            key: round(normalized[key] / total, 4) for key in ordered_keys
        }
        normalized_values["neutral"] = round(
            max(
                0.0,
                1
                - normalized_values["positive"]
                - normalized_values["negative"],
            ),
            4,
        )
        return SentimentScores(**normalized_values)

    @staticmethod
    def _normalize_issue_weights(
        issue_categories: list[str],
        raw_weights: Any,
    ) -> dict[str, float]:
        weights = {
            category: max(
                0.0,
                float(dict(raw_weights or {}).get(category, 0.0) or 0.0),
            )
            for category in issue_categories
        }
        total = sum(weights.values())
        if total <= 0:
            average_weight = round(1 / len(issue_categories), 4)
            weights = {category: average_weight for category in issue_categories}
        else:
            weights = {
                category: round(value / total, 4)
                for category, value in weights.items()
            }

        if issue_categories:
            last_category = issue_categories[-1]
            previous_total = sum(
                weights[category] for category in issue_categories[:-1]
            )
            weights[last_category] = round(max(0.0, 1 - previous_total), 4)
        return weights

    def _fallback(
        self, clean_result: TextCleanResult, reason: str
    ) -> AnalysisResultEnvelope:
        text = clean_result.cleaned_text
        shop_name = "未知商铺"
        positive_keywords = ["不错", "好", "香", "快", "满意", "干净"]
        negative_keywords = ["咸", "慢", "久", "差", "一般", "少", "贵", "脏"]
        positive_keywords_en = [
            "good",
            "great",
            "nice",
            "fast",
            "clean",
            "satisfied",
            "delicious",
            "tasty",
            "yummy",
            "fresh",
            "convenient",
        ]
        negative_keywords_en = [
            "salty",
            "slow",
            "long",
            "bad",
            "small",
            "expensive",
            "dirty",
            "bland",
            "stale",
            "cold",
            "unpalatable",
            "awful",
            "terrible",
        ]
        text_lower = text.lower()

        positive_hits = sum(keyword in text for keyword in positive_keywords) + sum(
            keyword in text_lower for keyword in positive_keywords_en
        )
        negative_hits = sum(keyword in text for keyword in negative_keywords) + sum(
            keyword in text_lower for keyword in negative_keywords_en
        )
        if negative_hits > positive_hits:
            sentiment_label = "负面"
            scores = SentimentScores(positive=0.1, negative=0.8, neutral=0.1)
        elif positive_hits > negative_hits:
            sentiment_label = "正面"
            scores = SentimentScores(positive=0.75, negative=0.1, neutral=0.15)
        else:
            sentiment_label = "中性"
            scores = SentimentScores(positive=0.25, negative=0.25, neutral=0.5)

        issues = {
            "口味": [
                "咸",
                "淡",
                "辣",
                "味道",
                "香",
                "taste",
                "flavor",
                "delicious",
                "tasty",
                "yummy",
                "broth",
                "unpalatable",
            ],
            "价格": ["贵", "便宜", "价格", "price", "expensive", "cheap", "value"],
            "卫生": ["脏", "卫生", "不干净", "hygiene", "dirty", "cleanliness"],
            "服务态度": ["态度", "服务", "service", "staff", "friendly", "rude", "convenient"],
            "排队效率": [
                "排队",
                "久",
                "慢",
                "等待",
                "queue",
                "line",
                "wait",
                "slow",
                "quick",
                "fast",
            ],
            "分量": ["少", "分量", "portion", "size", "filling"],
            "食材新鲜度": ["不新鲜", "新鲜", "变味", "fresh", "stale"],
            "出餐速度": ["出餐", "上餐", "快", "慢", "served", "serving speed", "ready quickly"],
        }
        issue_categories = [
            category
            for category, keywords in issues.items()
            if any(keyword in text or keyword in text_lower for keyword in keywords)
        ]
        if not issue_categories:
            if any(
                keyword in text_lower
                for keyword in ["delicious", "tasty", "yummy", "taste", "flavor"]
            ):
                issue_categories = ["口味"]
            elif any(
                keyword in text_lower
                for keyword in ["fast", "quick", "queue", "wait", "line", "slow"]
            ):
                issue_categories = ["排队效率"]
            elif any(keyword in text_lower for keyword in ["fresh", "stale"]):
                issue_categories = ["食材新鲜度"]
            elif any(keyword in text_lower for keyword in ["price", "expensive", "cheap"]):
                issue_categories = ["价格"]
            elif any(
                keyword in text_lower
                for keyword in ["service", "staff", "friendly", "rude", "convenient"]
            ):
                issue_categories = ["服务态度"]
        if not issue_categories:
            issue_categories = ["其他"]

        weight = round(1 / len(issue_categories), 2)
        issue_weights = {category: weight for category in issue_categories}
        issue_weights[issue_categories[-1]] = round(
            1 - sum(list(issue_weights.values())[:-1]), 2
        )

        urgency = "高" if any(word in text for word in ["卫生", "变味", "投诉"]) else "中"
        if any(word in text_lower for word in ["hygiene", "stale", "complaint"]):
            urgency = "高"
        if sentiment_label == "正面":
            urgency = "低"

        summary = text[:70] if len(text) > 70 else text
        if not summary.endswith(("。", "！", "？")):
            summary = f"{summary}。"
        summary_en = build_summary_en(
            shop_name=shop_name,
            summary=summary,
            sentiment_label=sentiment_label,
            issue_categories=issue_categories,
            urgency=urgency,
        )

        return AnalysisResultEnvelope(
            result=AnalysisResultData(
                shop_name=shop_name,
                sentiment_label=sentiment_label,
                sentiment_scores=scores,
                issue_categories=issue_categories,
                issue_weights=issue_weights,
                urgency=urgency,
                summary=summary,
                summary_en=summary_en,
            ),
            source=reason,
            fallback_used=True,
        )
