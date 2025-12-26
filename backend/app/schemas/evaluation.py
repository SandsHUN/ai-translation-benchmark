"""
AI Translation Benchmark - Evaluation Schemas

Author: Zoltan Tamas Toth

Pydantic models for evaluation metrics and results.
"""

from typing import Any

from pydantic import BaseModel, Field


class MetricResult(BaseModel):
    """Individual metric evaluation result."""

    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric score (0-100)")
    weight: float = Field(..., description="Metric weight in overall score")
    details: dict[str, Any] | None = Field(None, description="Additional metric details")


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of evaluation scores."""

    overall_score: float = Field(..., description="Overall weighted score (0-100)")
    metrics: list[MetricResult] = Field(..., description="Individual metric results")
    warnings: list[str] = Field(default_factory=list, description="Evaluation warnings")
    explanation: str | None = Field(None, description="Score explanation")


class EvaluationResult(BaseModel):
    """Complete evaluation result for a translation."""

    translation_id: int = Field(..., description="Translation ID")
    provider_name: str = Field(..., description="Provider name")
    model_id: str = Field(..., description="Model identifier")
    score_breakdown: ScoreBreakdown = Field(..., description="Score breakdown")
