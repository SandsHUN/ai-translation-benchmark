"""
AI Translation Benchmark - Length Ratio Metric

Author: Zoltan Tamas Toth

Analyzes the length ratio between source and target text.
"""

from app.core.constants import LENGTH_RATIO_MAX, LENGTH_RATIO_MIN, WARN_LENGTH_ANOMALY
from app.core.logging import get_logger

logger = get_logger(__name__)


class LengthRatioMetric:
    """Length ratio analysis metric."""

    def __init__(
        self,
        min_ratio: float = LENGTH_RATIO_MIN,
        max_ratio: float = LENGTH_RATIO_MAX,
    ):
        """
        Initialize length ratio metric.

        Args:
            min_ratio: Minimum acceptable length ratio
            max_ratio: Maximum acceptable length ratio
        """
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

    def evaluate(
        self,
        source_text: str,
        target_text: str,
    ) -> dict:
        """
        Evaluate length ratio between source and target.

        Args:
            source_text: Source text
            target_text: Translated text

        Returns:
            Dictionary with score and ratio details
        """
        source_len = len(source_text)
        target_len = len(target_text)

        if source_len == 0:
            return {
                "score": 0.0,
                "ratio": 0.0,
                "source_length": 0,
                "target_length": target_len,
                "warning": "Empty source text",
            }

        if target_len == 0:
            return {
                "score": 0.0,
                "ratio": 0.0,
                "source_length": source_len,
                "target_length": 0,
                "warning": "Empty translation",
            }

        # Calculate length ratio (target / source)
        ratio = target_len / source_len

        # Calculate score based on ratio
        if self.min_ratio <= ratio <= self.max_ratio:
            # Ratio is within acceptable range
            # Score is 100 at ideal ratio (1.0), decreases towards boundaries
            if ratio < 1.0:
                # Shorter translation
                score = ((ratio - self.min_ratio) / (1.0 - self.min_ratio)) * 100.0
            else:
                # Longer translation
                score = ((self.max_ratio - ratio) / (self.max_ratio - 1.0)) * 100.0

            score = max(50.0, score)  # Minimum 50 if within range
        else:
            # Ratio is outside acceptable range
            if ratio < self.min_ratio:
                # Too short
                score = (ratio / self.min_ratio) * 50.0
            else:
                # Too long
                score = (self.max_ratio / ratio) * 50.0

            score = max(0.0, min(50.0, score))

        # Generate warning if needed
        warning = None
        if ratio < self.min_ratio:
            warning = f"{WARN_LENGTH_ANOMALY}: translation too short (ratio: {ratio:.2f})"
        elif ratio > self.max_ratio:
            warning = f"{WARN_LENGTH_ANOMALY}: translation too long (ratio: {ratio:.2f})"

        logger.debug(
            f"Length ratio: {ratio:.2f} (source: {source_len}, target: {target_len}), "
            f"score: {score:.2f}"
        )

        return {
            "score": score,
            "ratio": ratio,
            "source_length": source_len,
            "target_length": target_len,
            "warning": warning,
        }
