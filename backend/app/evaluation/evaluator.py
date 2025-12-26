"""
AI Translation Benchmark - Evaluation Orchestrator

Author: Zoltan Tamas Toth

Main evaluation engine that coordinates all metrics.
"""

from typing import Any

from app.core.config import config_manager
from app.core.logging import get_logger
from app.evaluation.heuristics.language_detection import LanguageDetectionMetric
from app.evaluation.heuristics.length_ratio import LengthRatioMetric
from app.evaluation.heuristics.preservation import PreservationMetric
from app.evaluation.heuristics.repetition import RepetitionMetric
from app.evaluation.scorer import ScoreFusion
from app.evaluation.semantic.embedding_similarity import SemanticSimilarityMetric
from app.schemas.evaluation import EvaluationResult

logger = get_logger(__name__)


class Evaluator:
    """Main evaluation orchestrator."""

    def __init__(self):
        """Initialize evaluator with all metrics."""
        self.config = config_manager

        # Initialize heuristic metrics
        self.language_detection = LanguageDetectionMetric()
        self.length_ratio = LengthRatioMetric(
            min_ratio=self.config.get("metrics.heuristics.length_ratio.min_ratio", 0.5),
            max_ratio=self.config.get("metrics.heuristics.length_ratio.max_ratio", 2.0),
        )
        self.repetition = RepetitionMetric()
        self.preservation = PreservationMetric(
            check_numbers=self.config.get("metrics.heuristics.preservation.check_numbers", True),
            check_punctuation=self.config.get(
                "metrics.heuristics.preservation.check_punctuation", True
            ),
            check_entities=self.config.get("metrics.heuristics.preservation.check_entities", True),
        )

        # Initialize semantic metric
        self.semantic_similarity = None
        if self.config.is_metric_enabled("semantic", ""):
            model_name = self.config.get(
                "metrics.semantic.model",
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            )
            self.semantic_similarity = SemanticSimilarityMetric(model_name)

        # Initialize score fusion
        self.scorer = ScoreFusion()

    async def evaluate_translation(
        self,
        translation_id: int,
        provider_name: str,
        model_id: str,
        source_text: str,
        target_text: str,
        target_lang: str,
        source_lang: str | None = None,
        reference_translation: str | None = None,
    ) -> EvaluationResult:
        """
        Evaluate a translation using all applicable metrics.

        Args:
            translation_id: Translation ID
            provider_name: Provider name
            model_id: Model identifier
            source_text: Source text
            target_text: Translated text
            target_lang: Target language code
            source_lang: Source language code (optional)
            reference_translation: Reference translation (optional)

        Returns:
            EvaluationResult with scores and breakdown
        """
        logger.info(f"Evaluating translation {translation_id} from {provider_name}")

        metric_results: dict[str, dict[str, Any]] = {}

        # Run heuristic metrics
        if self.config.is_metric_enabled("heuristics", "language_detection"):
            metric_results["language_detection"] = self.language_detection.evaluate(
                source_text, target_text, target_lang
            )

        if self.config.is_metric_enabled("heuristics", "length_ratio"):
            metric_results["length_ratio"] = self.length_ratio.evaluate(source_text, target_text)

        if self.config.is_metric_enabled("heuristics", "repetition"):
            metric_results["repetition"] = self.repetition.evaluate(source_text, target_text)

        if self.config.is_metric_enabled("heuristics", "preservation"):
            metric_results["preservation"] = self.preservation.evaluate(source_text, target_text)

        # Run semantic similarity
        if self.semantic_similarity:
            metric_results["semantic_similarity"] = self.semantic_similarity.evaluate(
                source_text, target_text
            )

        # TODO: Add reference-based metrics if reference is provided
        # if reference_translation:
        #     metric_results["bleu"] = self.bleu.evaluate(...)
        #     metric_results["chrf"] = self.chrf.evaluate(...)

        # Fuse scores
        score_breakdown = self.scorer.fuse_scores(metric_results)

        logger.info(
            f"Evaluation complete for translation {translation_id}: "
            f"score={score_breakdown.overall_score:.2f}"
        )

        return EvaluationResult(
            translation_id=translation_id,
            provider_name=provider_name,
            model_id=model_id,
            score_breakdown=score_breakdown,
        )
