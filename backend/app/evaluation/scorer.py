"""
AI Translation Benchmark - Score Fusion

Author: Zoltan Tamas Toth

Weighted combination of metrics to produce overall quality score.
"""

from typing import Any

from app.core.config import config_manager
from app.core.constants import CATEGORY_HEURISTICS, CATEGORY_SEMANTIC, METRIC_OVERALL
from app.core.logging import get_logger
from app.schemas.evaluation import MetricResult, ScoreBreakdown

logger = get_logger(__name__)


class ScoreFusion:
    """Score fusion and aggregation system."""

    def __init__(self):
        """Initialize score fusion."""
        self.config = config_manager

    def fuse_scores(
        self,
        metric_results: dict[str, dict[str, Any]],
    ) -> ScoreBreakdown:
        """
        Fuse multiple metric scores into overall score.

        Args:
            metric_results: Dictionary of metric results
                Format: {metric_name: {score: float, ...}}

        Returns:
            ScoreBreakdown with overall score and details
        """
        weighted_scores = []
        metric_list = []
        warnings = []

        # Process heuristic metrics
        for metric_name, result in metric_results.items():
            if metric_name == METRIC_OVERALL:
                continue

            score = result.get("score", 0.0)
            warning = result.get("warning")

            # Get weight from configuration
            weight = self._get_metric_weight(metric_name)

            if weight > 0:
                weighted_scores.append(score * weight)

                metric_list.append(
                    MetricResult(
                        name=metric_name,
                        value=score,
                        weight=weight,
                        details=result,
                    )
                )

                if warning:
                    warnings.append(f"{metric_name}: {warning}")

        # Calculate overall score
        if weighted_scores:
            total_weight = sum(m.weight for m in metric_list)
            if total_weight > 0:
                overall_score = sum(weighted_scores) / total_weight
            else:
                overall_score = 0.0
        else:
            overall_score = 0.0

        # Generate explanation
        explanation = self._generate_explanation(metric_list, overall_score)

        logger.info(f"Score fusion complete: overall={overall_score:.2f}")

        return ScoreBreakdown(
            overall_score=overall_score,
            metrics=metric_list,
            warnings=warnings,
            explanation=explanation,
        )

    def _get_metric_weight(self, metric_name: str) -> float:
        """
        Get weight for a metric from configuration.

        Args:
            metric_name: Metric name

        Returns:
            Metric weight
        """
        # Map metric names to config paths
        metric_config_map = {
            "language_detection": (CATEGORY_HEURISTICS, "language_detection"),
            "length_ratio": (CATEGORY_HEURISTICS, "length_ratio"),
            "repetition": (CATEGORY_HEURISTICS, "repetition"),
            "preservation": (CATEGORY_HEURISTICS, "preservation"),
            "semantic_similarity": (CATEGORY_SEMANTIC, ""),
        }

        if metric_name in metric_config_map:
            category, metric = metric_config_map[metric_name]
            if metric:
                return self.config.get_metric_weight(category, metric)
            else:
                # For semantic, weight is at category level
                return self.config.get(f"metrics.{category}.weight", 0.0)

        return 0.0

    def _generate_explanation(
        self,
        metrics: list[MetricResult],
        overall_score: float,
    ) -> str:
        """
        Generate human-readable explanation of score.

        Args:
            metrics: List of metric results
            overall_score: Overall score

        Returns:
            Explanation string
        """
        if overall_score >= 90:
            quality = "Excellent"
        elif overall_score >= 75:
            quality = "Good"
        elif overall_score >= 60:
            quality = "Fair"
        else:
            quality = "Poor"

        # Find top contributing metrics
        sorted_metrics = sorted(
            metrics,
            key=lambda m: m.value * m.weight,
            reverse=True,
        )

        top_metrics = sorted_metrics[:3]
        top_names = [m.name.replace("_", " ").title() for m in top_metrics]

        explanation = f"{quality} translation quality (score: {overall_score:.1f}/100). "
        explanation += f"Top factors: {', '.join(top_names)}."

        return explanation
