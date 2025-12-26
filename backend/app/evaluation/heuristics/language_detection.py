"""
AI Translation Benchmark - Language Detection Metric

Author: Zoltan Tamas Toth

Verifies that the translation output matches the target language.
"""

from langdetect import LangDetectException, detect, detect_langs

from app.core.constants import WARN_LOW_CONFIDENCE
from app.core.logging import get_logger

logger = get_logger(__name__)


class LanguageDetectionMetric:
    """Language detection and verification metric."""

    def __init__(self, confidence_threshold: float = 0.8):
        """
        Initialize language detection metric.

        Args:
            confidence_threshold: Minimum confidence for language detection
        """
        self.confidence_threshold = confidence_threshold

    def evaluate(
        self,
        source_text: str,
        target_text: str,
        target_lang: str,
    ) -> dict:
        """
        Evaluate language detection for translation.

        Args:
            source_text: Source text
            target_text: Translated text
            target_lang: Expected target language code

        Returns:
            Dictionary with score, detected language, and confidence
        """
        if not target_text or not target_text.strip():
            return {
                "score": 0.0,
                "detected_lang": None,
                "confidence": 0.0,
                "matches_target": False,
                "warning": "Empty translation",
            }

        try:
            # Detect language with confidence scores
            lang_probs = detect_langs(target_text)

            if not lang_probs:
                return {
                    "score": 0.0,
                    "detected_lang": None,
                    "confidence": 0.0,
                    "matches_target": False,
                    "warning": "Could not detect language",
                }

            # Get most likely language
            detected_lang = lang_probs[0].lang
            confidence = lang_probs[0].prob

            # Check if detected language matches target
            matches_target = detected_lang == target_lang

            # Calculate score
            if matches_target:
                # Full score if confidence is high
                if confidence >= self.confidence_threshold:
                    score = 100.0
                else:
                    # Reduced score for low confidence
                    score = confidence * 100.0
            else:
                # No score if language doesn't match
                score = 0.0

            # Generate warning if needed
            warning = None
            if not matches_target:
                warning = f"Language mismatch: expected '{target_lang}', detected '{detected_lang}'"
            elif confidence < self.confidence_threshold:
                warning = WARN_LOW_CONFIDENCE

            logger.debug(
                f"Language detection: {detected_lang} (confidence: {confidence:.2f}), "
                f"target: {target_lang}, score: {score:.2f}"
            )

            return {
                "score": score,
                "detected_lang": detected_lang,
                "confidence": confidence,
                "matches_target": matches_target,
                "warning": warning,
                "all_probabilities": [{"lang": lp.lang, "prob": lp.prob} for lp in lang_probs],
            }

        except LangDetectException as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return {
                "score": 50.0,  # Neutral score when detection fails
                "detected_lang": None,
                "confidence": 0.0,
                "matches_target": None,
                "warning": f"Language detection error: {str(e)}",
            }
