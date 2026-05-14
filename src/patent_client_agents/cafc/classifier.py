"""Patent case classifier for CAFC opinions.

Uses multi-level keyword matching with confidence scoring to identify
patent-related cases from case names and text content.
"""

from __future__ import annotations

import re

# Keyword categories with weights for confidence scoring.
_KEYWORD_CATEGORIES: dict[str, dict] = {
    "strong_indicators": {
        "keywords": [
            "patent",
            "patents",
            "patented",
            "patentee",
            "patentability",
            "uspto",
            "patent and trademark office",
            "patent office",
            "ptab",
            "patent trial and appeal board",
            "ipr",
            "inter partes review",
            "pgr",
            "post-grant review",
            "post grant review",
            "cbm",
            "covered business method",
            "iancu",
            "vidal",
        ],
        "weight": 0.9,
    },
    "statute_references": {
        "keywords": [
            "35 u.s.c",
            "35 usc",
            "section 101",
            "section 102",
            "section 103",
            "section 112",
            "§ 101",
            "§ 102",
            "§ 103",
            "§ 112",
            "§101",
            "§102",
            "§103",
            "§112",
        ],
        "weight": 0.8,
    },
    "technical_terms": {
        "keywords": [
            "obviousness",
            "non-obvious",
            "nonobvious",
            "infringement",
            "infringed",
            "infringing",
            "claims",
            "claim construction",
            "claim interpretation",
            "prior art",
            "novelty",
            "anticipation",
            "anticipated",
            "enablement",
            "written description",
            "indefiniteness",
            "inventive step",
            "prosecution history",
        ],
        "weight": 0.65,
    },
    "parties": {
        "keywords": [
            "andrei iancu",
            "katherine vidal",
            "kathi vidal",
            "director of the united states patent",
            "commissioner for patents",
            "commissioner of patents",
            "board of patent appeals",
        ],
        "weight": 0.7,
    },
    "case_types": {
        "keywords": [
            "reexamination",
            "reissue",
            "interference",
            "derivation proceeding",
            "patent term adjustment",
            "patent term extension",
        ],
        "weight": 0.7,
    },
}

_FALSE_POSITIVE_PATTERNS = [
    r"patient\s+care",
    r"patient\s+treatment",
    r"patient\s+safety",
    r"medical\s+patient",
    r"patent\s+leather",
]


class PatentClassifier:
    """Classify CAFC cases as patent-related using keyword confidence scoring.

    Example::

        classifier = PatentClassifier()
        is_patent, confidence, keywords = classifier.classify(
            "Apple Inc. v. Samsung Electronics Co., Ltd."
        )
    """

    def __init__(self) -> None:
        self._keyword_patterns: dict[str, re.Pattern[str]] = {}
        for category, config in _KEYWORD_CATEGORIES.items():
            patterns = []
            for keyword in config["keywords"]:
                if keyword in ("ipr", "pgr", "cbm"):
                    patterns.append(r"\b" + re.escape(keyword) + r"(?=\d|\b)")
                else:
                    patterns.append(r"\b" + re.escape(keyword) + r"\b")
            self._keyword_patterns[category] = re.compile("|".join(patterns), re.IGNORECASE)

        self._false_positive_pattern = re.compile("|".join(_FALSE_POSITIVE_PATTERNS), re.IGNORECASE)

    def classify(
        self,
        case_name: str,
        text_content: str | None = None,
    ) -> tuple[bool, float, list[str]]:
        """Classify a case as patent-related.

        Args:
            case_name: The case name.
            text_content: Optional full text or snippet (first 5000 chars used).

        Returns:
            ``(is_patent_case, confidence_score, matched_keywords)``
        """
        text = case_name.lower()
        if text_content:
            text += " " + text_content[:5000].lower()

        if self._false_positive_pattern.search(text):
            return False, 0.0, []

        all_matches: list[str] = []
        category_scores: dict[str, float] = {}

        for category, pattern in self._keyword_patterns.items():
            matches = pattern.findall(text)
            if matches:
                unique = list({m.lower() for m in matches})
                all_matches.extend(unique)
                weight = _KEYWORD_CATEGORIES[category]["weight"]
                multiplier = min(0.8 + (len(unique) - 1) * 0.1, 1.0)
                category_scores[category] = weight * multiplier

        confidence = self._score(category_scores, all_matches)
        return confidence >= 0.5, confidence, list(set(all_matches))

    def _score(self, category_scores: dict[str, float], all_matches: list[str]) -> float:
        if not category_scores:
            return 0.0
        confidence = max(category_scores.values())
        if len(category_scores) >= 2:
            confidence = min(confidence * 1.1, 0.95)
        if len(all_matches) >= 5:
            confidence = min(confidence * 1.1, 0.95)
        elif len(all_matches) >= 3:
            confidence = min(confidence * 1.05, 0.95)
        if "strong_indicators" in category_scores:
            strong = {"uspto", "ptab", "inter partes review"}
            if any(p in all_matches for p in strong):
                confidence = max(confidence, 0.9)
        return round(confidence, 3)
