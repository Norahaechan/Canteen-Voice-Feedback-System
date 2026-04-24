from __future__ import annotations

import json
import re
from functools import lru_cache

from app.core.config import BACKEND_DIR

SEED_FILE = BACKEND_DIR / "data" / "seeds" / "shops.json"


def normalize_english_alias(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower())
    return re.sub(r"\s+", " ", normalized).strip()


@lru_cache(maxsize=1)
def load_shop_alias_map() -> dict[str, str]:
    items = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    alias_map: dict[str, str] = {}
    for item in items:
        standard_name = item["name"]
        alias_map[standard_name] = standard_name
        for alias in item.get("aliases", []):
            alias_map[alias] = standard_name
        for alias in item.get("aliases_en", []):
            normalized_alias = normalize_english_alias(alias)
            if normalized_alias:
                alias_map[normalized_alias] = standard_name
    return alias_map


@lru_cache(maxsize=1)
def load_standard_shop_names() -> list[str]:
    items = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    return [str(item["name"]) for item in items]


@lru_cache(maxsize=1)
def load_shop_catalog() -> list[dict[str, str | list[str]]]:
    items = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    catalog: list[dict[str, str | list[str]]] = []
    for item in items:
        catalog.append(
            {
                "name": str(item["name"]),
                "name_en": str(item.get("name_en", "")),
                "category": str(item.get("category", "")),
                "category_en": str(item.get("category_en", "")),
                "aliases": [str(alias) for alias in item.get("aliases", [])],
                "aliases_en": [
                    normalize_english_alias(alias)
                    for alias in item.get("aliases_en", [])
                    if normalize_english_alias(alias)
                ],
            }
        )
    return catalog


@lru_cache(maxsize=1)
def load_shop_alias_patterns() -> list[tuple[re.Pattern[str], str]]:
    items = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    patterns: list[tuple[re.Pattern[str], str]] = []
    for item in items:
        standard_name = item["name"]
        for alias in item.get("aliases_en", []):
            cleaned_alias = str(alias).strip()
            if not cleaned_alias:
                continue
            pattern = re.compile(rf"\b{re.escape(cleaned_alias)}\b", re.IGNORECASE)
            patterns.append((pattern, standard_name))
    patterns.sort(key=lambda item: len(item[0].pattern), reverse=True)
    return patterns


@lru_cache(maxsize=1)
def load_shop_alias_entries_en() -> list[tuple[str, str]]:
    items = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    aliases: list[tuple[str, str]] = []
    for item in items:
        standard_name = item["name"]
        for alias in item.get("aliases_en", []):
            normalized_alias = normalize_english_alias(alias)
            if normalized_alias:
                aliases.append((normalized_alias, standard_name))
    aliases.sort(key=lambda item: len(item[0]), reverse=True)
    return aliases
