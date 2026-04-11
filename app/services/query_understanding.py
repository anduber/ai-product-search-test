from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

SYNONYMS: dict[str, str] = {
    "smart phone": "smartphone",
    "tv": "television",
    "fridge": "refrigerator",
    "bike": "bicycle",
}

EXPANSIONS: dict[str, str] = {
    "smartphone": "smartphone mobile device electronics",
    "laptop": "laptop computer electronics",
    "camera": "camera photography device electronics",
    "shoes": "shoes footwear fashion",
    "television": "television tv display screen electronics",
    "refrigerator": "refrigerator fridge kitchen appliance",
    "bicycle": "bicycle bike cycling sports",
    "headphones": "headphones audio sound electronics",
    "tablet": "tablet portable computer electronics",
    "watch": "watch wearable smartwatch accessories",
}


class QueryUnderstandingService:
    def __init__(self) -> None:
        self._synonym_patterns: list[tuple[re.Pattern[str], str]] = [
            (re.compile(re.escape(phrase), re.IGNORECASE), replacement)
            for phrase, replacement in SYNONYMS.items()
        ]

    def normalize(self, query: str) -> str:
        query = query.strip().lower()
        query = re.sub(r"\s+", " ", query)
        return query

    def apply_synonyms(self, query: str) -> str:
        for pattern, replacement in self._synonym_patterns:
            query = pattern.sub(replacement, query)
        return query

    def expand(self, query: str) -> str:
        tokens = query.split()
        expanded_tokens: list[str] = []

        for token in tokens:
            expansion = EXPANSIONS.get(token)
            if expansion:
                expanded_tokens.append(expansion)
            else:
                expanded_tokens.append(token)

        return " ".join(expanded_tokens)

    def process(self, query: str) -> str:
        original = query
        query = self.normalize(query)
        query = self.apply_synonyms(query)
        query = self.expand(query)

        logger.debug("Query understanding: '%s' → '%s'", original, query)

        if not query.strip():
            raise ValueError("Query became empty after processing")

        return query
