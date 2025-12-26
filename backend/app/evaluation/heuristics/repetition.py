"""
AI Translation Benchmark - Repetition Detection Metric

Author: Zoltan Tamas Toth

Detects excessive repetition in translations using n-gram analysis.
"""

from collections import Counter

from app.core.constants import MAX_NGRAM_SIZE, REPETITION_THRESHOLD, WARN_HIGH_REPETITION
from app.core.logging import get_logger

logger = get_logger(__name__)


class RepetitionMetric:
    """Repetition detection metric using n-gram analysis."""

    def __init__(
        self,
        max_ngram_size: int = MAX_NGRAM_SIZE,
        threshold: float = REPETITION_THRESHOLD,
    ):
        """
        Initialize repetition metric.

        Args:
            max_ngram_size: Maximum n-gram size to check
            threshold: Repetition threshold for warnings
        """
        self.max_ngram_size = max_ngram_size
        self.threshold = threshold

    def _get_ngrams(self, text: str, n: int) -> list[tuple[str, ...]]:
        """
        Extract n-grams from text.

        Args:
            text: Input text
            n: N-gram size

        Returns:
            List of n-grams
        """
        words = text.lower().split()
        if len(words) < n:
            return []

        return [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]

    def _calculate_repetition_score(self, ngrams: list[tuple[str, ...]]) -> float:
        """
        Calculate repetition score for n-grams.

        Args:
            ngrams: List of n-grams

        Returns:
            Repetition score (0-1, higher means more repetition)
        """
        if not ngrams:
            return 0.0

        # Count n-gram frequencies
        ngram_counts = Counter(ngrams)

        # Calculate repetition as ratio of repeated n-grams
        total_ngrams = len(ngrams)
        unique_ngrams = len(ngram_counts)

        if total_ngrams == 0:
            return 0.0

        # Repetition score: 1 - (unique / total)
        repetition = 1.0 - (unique_ngrams / total_ngrams)

        # Weight by maximum frequency
        max_count = max(ngram_counts.values())
        if max_count > 1:
            # Increase score if some n-grams are very frequent
            frequency_factor = min(max_count / total_ngrams, 1.0)
            repetition = max(repetition, frequency_factor)

        return repetition

    def evaluate(self, source_text: str, target_text: str) -> dict:
        """
        Evaluate repetition in translation.

        Args:
            source_text: Source text
            target_text: Translated text

        Returns:
            Dictionary with score and repetition details
        """
        if not target_text or not target_text.strip():
            return {
                "score": 0.0,
                "repetition_score": 0.0,
                "warning": "Empty translation",
            }

        # Calculate repetition for different n-gram sizes
        repetition_scores = {}
        max_repetition = 0.0

        for n in range(2, self.max_ngram_size + 1):
            ngrams = self._get_ngrams(target_text, n)
            if ngrams:
                rep_score = self._calculate_repetition_score(ngrams)
                repetition_scores[f"{n}-gram"] = rep_score
                max_repetition = max(max_repetition, rep_score)

        # Calculate overall score (inverse of repetition)
        # 0 repetition = 100 score, high repetition = low score
        score = (1.0 - max_repetition) * 100.0

        # Generate warning if repetition is high
        warning = None
        if max_repetition > self.threshold:
            warning = f"{WARN_HIGH_REPETITION} (score: {max_repetition:.2f})"

        logger.debug(f"Repetition analysis: max={max_repetition:.2f}, score={score:.2f}")

        return {
            "score": score,
            "repetition_score": max_repetition,
            "ngram_scores": repetition_scores,
            "warning": warning,
        }
