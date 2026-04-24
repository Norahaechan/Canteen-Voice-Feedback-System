from __future__ import annotations

from collections.abc import Callable

SUPPORTED_LOCALES = {"zh", "en"}

ISSUE_TRANSLATIONS = {
    "口味": "taste",
    "价格": "price",
    "卫生": "hygiene",
    "服务态度": "service attitude",
    "排队效率": "queue efficiency",
    "分量": "portion size",
    "食材新鲜度": "ingredient freshness",
    "出餐速度": "serving speed",
    "其他": "other",
}

SENTIMENT_TRANSLATIONS = {
    "正面": "Positive",
    "负面": "Negative",
    "中性": "Neutral",
}

URGENCY_TRANSLATIONS = {
    "高": "High",
    "中": "Medium",
    "低": "Low",
}


def translate_issue_category(value: str) -> str:
    return ISSUE_TRANSLATIONS.get(value, value)


def translate_sentiment(value: str) -> str:
    return SENTIMENT_TRANSLATIONS.get(value, value)


def translate_urgency(value: str) -> str:
    return URGENCY_TRANSLATIONS.get(value, value)


def normalize_locale(value: str | None) -> str:
    normalized = (value or "zh").strip().lower()
    return normalized if normalized in SUPPORTED_LOCALES else "zh"


def build_summary_en(
    *,
    shop_name: str,
    shop_name_en: str = "",
    summary: str = "",
    sentiment_label: str,
    issue_categories: list[str],
    urgency: str,
) -> str:
    normalized_summary = summary.strip()
    if normalized_summary and normalized_summary.isascii():
        return normalized_summary.rstrip(".!?") + "."

    display_name = shop_name_en or shop_name or "the target shop"
    issue_text = ", ".join(translate_issue_category(item) for item in issue_categories)
    sentiment_text = {
        "正面": "positive",
        "负面": "negative",
        "中性": "mixed or neutral",
    }.get(sentiment_label, "mixed or neutral")
    urgency_text = {
        "高": "high",
        "中": "medium",
        "低": "low",
    }.get(urgency, "medium")

    if issue_text:
        return (
            f"Feedback for {display_name} is {sentiment_text}, mainly involving "
            f"{issue_text}, with {urgency_text} urgency."
        )
    return f"Feedback for {display_name} is {sentiment_text} with {urgency_text} urgency."


def format_distribution(
    distribution: dict[str, int],
    *,
    key_formatter: Callable[[str], str] | None = None,
) -> str:
    if not distribution:
        return "None"
    formatter = key_formatter or (lambda item: item)
    parts = [f"{formatter(key)}: {value}" for key, value in distribution.items()]
    return ", ".join(parts)
