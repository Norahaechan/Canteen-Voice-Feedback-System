from __future__ import annotations

import re

from app.schemas.text_clean import TextCleanResult

FILLER_WORDS = [
    "嗯",
    "那个",
    "就是",
    "然后",
    "这个",
    "吧",
    "啊",
    "呢",
]


class TextCleanService:
    def clean_text(self, text: str) -> TextCleanResult:
        original_text = text.strip()
        cleaned_text = original_text
        removed_fillers: list[str] = []

        for filler in FILLER_WORDS:
            if filler in cleaned_text:
                removed_fillers.append(filler)
                cleaned_text = cleaned_text.replace(filler, "")

        cleaned_text = self._normalize_cafeteria_reference(cleaned_text)
        cleaned_text = self._collapse_duplicates(cleaned_text)
        cleaned_text = self._normalize_spaces(cleaned_text)

        return TextCleanResult(
            original_text=original_text,
            cleaned_text=cleaned_text,
            shop_candidates=[],
            removed_fillers=removed_fillers,
        )

    @staticmethod
    def _collapse_duplicates(text: str) -> str:
        text = re.sub(r"([^\s，。,！!？?；;]{2,})\1+", r"\1", text)
        text = re.sub(r"([，。,！!？?；;])\1+", r"\1", text)
        return text

    @staticmethod
    def _normalize_cafeteria_reference(text: str) -> str:
        normalized_text = text
        replacements = [
            (r"(?:^|[^0-9])1[、,\.\s]*食堂", "一食堂"),
            (r"(?:^|[^0-9])2[、,\.\s]*食堂", "二食堂"),
            (r"(?:^|[^0-9])3[、,\.\s]*食堂", "三食堂"),
            (r"一楼食堂", "一食堂"),
            (r"二楼食堂", "二食堂"),
            (r"三楼食堂", "三食堂"),
        ]
        for pattern, replacement in replacements:
            normalized_text = re.sub(pattern, replacement, normalized_text)
        return normalized_text

    @staticmethod
    def _normalize_spaces(text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\s*([，。,！!？?；;])\s*", r"\1", text)
        return text
