"""
AI Translation Benchmark - Content Preservation Metric

Author: Zoltan Tamas Toth

Checks preservation of numbers, punctuation, and other content elements.
"""

import re
import string

from app.core.constants import WARN_CONTENT_LOSS, WARN_FORMAT_DRIFT
from app.core.logging import get_logger

logger = get_logger(__name__)


class PreservationMetric:
    """Content preservation metric."""

    def __init__(
        self,
        check_numbers: bool = True,
        check_punctuation: bool = True,
        check_entities: bool = True,
    ):
        """
        Initialize preservation metric.

        Args:
            check_numbers: Check number preservation
            check_punctuation: Check punctuation preservation
            check_entities: Check named entity preservation (basic)
        """
        self.check_numbers = check_numbers
        self.check_punctuation = check_punctuation
        self.check_entities = check_entities

    def _extract_numbers(self, text: str) -> list[str]:
        """Extract numbers from text."""
        # Match integers, decimals, percentages, dates
        pattern = r"\b\d+(?:[.,]\d+)?%?\b"
        return re.findall(pattern, text)

    def _extract_punctuation_pattern(self, text: str) -> str:
        """Extract punctuation pattern from text."""
        # Get sequence of punctuation marks
        return "".join(c for c in text if c in string.punctuation)

    def _extract_capitalized_words(self, text: str) -> list[str]:
        """Extract capitalized words (potential named entities)."""
        # Simple heuristic: words that start with capital letter
        words = text.split()
        return [w for w in words if w and w[0].isupper()]

    def _calculate_preservation_score(
        self,
        source_items: list[str],
        target_items: list[str],
    ) -> float:
        """
        Calculate preservation score for a set of items.

        Args:
            source_items: Items from source text
            target_items: Items from target text

        Returns:
            Preservation score (0-100)
        """
        if not source_items:
            # No items to preserve, perfect score
            return 100.0

        # Count how many source items appear in target
        source_set = set(source_items)
        target_set = set(target_items)

        preserved = len(source_set & target_set)
        total = len(source_set)

        return (preserved / total) * 100.0 if total > 0 else 100.0

    def evaluate(self, source_text: str, target_text: str) -> dict:
        """
        Evaluate content preservation.

        Args:
            source_text: Source text
            target_text: Translated text

        Returns:
            Dictionary with score and preservation details
        """
        if not target_text or not target_text.strip():
            return {
                "score": 0.0,
                "warning": "Empty translation",
            }

        scores = {}
        warnings = []

        # Check number preservation
        if self.check_numbers:
            source_numbers = self._extract_numbers(source_text)
            target_numbers = self._extract_numbers(target_text)
            number_score = self._calculate_preservation_score(source_numbers, target_numbers)
            scores["numbers"] = number_score

            if number_score < 100.0:
                missing = len(source_numbers) - len(set(source_numbers) & set(target_numbers))
                warnings.append(f"{WARN_CONTENT_LOSS}: {missing} number(s) not preserved")

        # Check punctuation preservation
        if self.check_punctuation:
            source_punct = self._extract_punctuation_pattern(source_text)
            target_punct = self._extract_punctuation_pattern(target_text)

            # Calculate similarity of punctuation patterns
            if source_punct:
                # Simple ratio of matching punctuation
                matches = sum(1 for c in source_punct if c in target_punct)
                punct_score = (matches / len(source_punct)) * 100.0
            else:
                punct_score = 100.0

            scores["punctuation"] = punct_score

            if punct_score < 80.0:
                warnings.append(f"{WARN_FORMAT_DRIFT}: punctuation pattern differs")

        # Check named entity preservation (basic)
        if self.check_entities:
            source_entities = self._extract_capitalized_words(source_text)
            target_entities = self._extract_capitalized_words(target_text)
            entity_score = self._calculate_preservation_score(source_entities, target_entities)
            scores["entities"] = entity_score

            if entity_score < 80.0:
                warnings.append(f"{WARN_CONTENT_LOSS}: some capitalized words not preserved")

        # Calculate overall score (average of all checks)
        if scores:
            overall_score = sum(scores.values()) / len(scores)
        else:
            overall_score = 100.0

        logger.debug(f"Preservation scores: {scores}, overall: {overall_score:.2f}")

        return {
            "score": overall_score,
            "component_scores": scores,
            "warning": "; ".join(warnings) if warnings else None,
        }
