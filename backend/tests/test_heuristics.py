"""
AI Translation Benchmark - Heuristics Tests

Author: Zoltan Tamas Toth
"""

import pytest

from app.evaluation.heuristics.language_detection import LanguageDetectionMetric
from app.evaluation.heuristics.length_ratio import LengthRatioMetric
from app.evaluation.heuristics.preservation import PreservationMetric
from app.evaluation.heuristics.repetition import RepetitionMetric


class TestLanguageDetection:
    """Test language detection metric."""

    def test_correct_language(self):
        metric = LanguageDetectionMetric()
        result = metric.evaluate(
            source_text="Hello, world!",
            target_text="¡Hola, mundo!",
            target_lang="es",
        )
        assert result["matches_target"] is True
        assert result["score"] > 0

    def test_wrong_language(self):
        metric = LanguageDetectionMetric()
        result = metric.evaluate(
            source_text="Hello, world!",
            target_text="Bonjour, monde!",
            target_lang="es",
        )
        assert result["matches_target"] is False
        assert result["score"] == 0.0


class TestLengthRatio:
    """Test length ratio metric."""

    def test_normal_ratio(self):
        metric = LengthRatioMetric()
        result = metric.evaluate(
            source_text="Hello, world!",
            target_text="¡Hola, mundo!",
        )
        assert result["score"] > 50.0
        assert result["warning"] is None

    def test_too_short(self):
        metric = LengthRatioMetric()
        result = metric.evaluate(
            source_text="This is a very long sentence with many words.",
            target_text="Short",
        )
        assert result["score"] < 50.0
        assert result["warning"] is not None


class TestRepetition:
    """Test repetition detection metric."""

    def test_no_repetition(self):
        metric = RepetitionMetric()
        result = metric.evaluate(
            source_text="Hello, world!",
            target_text="This is a unique translation.",
        )
        assert result["score"] > 70.0

    def test_high_repetition(self):
        metric = RepetitionMetric()
        result = metric.evaluate(
            source_text="Hello, world!",
            target_text="test test test test test test",
        )
        assert result["score"] < 50.0
        assert result["warning"] is not None


class TestPreservation:
    """Test content preservation metric."""

    def test_number_preservation(self):
        metric = PreservationMetric()
        result = metric.evaluate(
            source_text="The price is $100 and 50 cents.",
            target_text="El precio es $100 y 50 centavos.",
        )
        assert result["component_scores"]["numbers"] == 100.0

    def test_number_loss(self):
        metric = PreservationMetric()
        result = metric.evaluate(
            source_text="The price is $100.",
            target_text="The price is high.",
        )
        assert result["component_scores"]["numbers"] < 100.0
