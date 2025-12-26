"""
AI Translation Benchmark - API Schemas

Author: Zoltan Tamas Toth
Date: 2025-12-25

Pydantic models for API requests and responses.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.evaluation import EvaluationResult
from app.schemas.provider import TranslationResult


class ProviderRequest(BaseModel):
    """Provider selection in translation request."""

    type: str = Field(..., description="Provider type")
    model: str = Field(..., description="Model identifier")
    base_url: str | None = Field(None, description="Base URL (for local providers)")
    api_key: str | None = Field(None, description="API key (for cloud providers)")


class TranslationRequest(BaseModel):
    """Request to translate text."""

    text: str = Field(..., description="Source text to translate", min_length=1, max_length=5000)
    target_lang: str = Field(..., description="Target language code", min_length=2, max_length=10)
    source_lang: str | None = Field(None, description="Source language code (optional)")
    providers: list[ProviderRequest] = Field(..., description="Providers to use", min_length=1)
    reference_translation: str | None = Field(
        None, description="Reference translation for comparison (optional)"
    )
    timeout: int | None = Field(None, description="Request timeout override")


class TranslationWithEvaluation(BaseModel):
    """Translation result with evaluation."""

    translation: TranslationResult = Field(..., description="Translation result")
    evaluation: EvaluationResult = Field(..., description="Evaluation result")


class RunSummary(BaseModel):
    """Summary of translation run with rankings."""

    total_providers: int = Field(..., description="Number of providers used")
    rankings: list[dict[str, Any]] = Field(..., description="Provider rankings")
    best_provider: str | None = Field(None, description="Best performing provider")
    best_score: float | None = Field(None, description="Best overall score")


class TranslationResponse(BaseModel):
    """Response from translation endpoint."""

    run_id: int = Field(..., description="Run ID for this translation")
    source_text: str = Field(..., description="Original source text")
    target_lang: str = Field(..., description="Target language")
    source_lang: str | None = Field(None, description="Source language")
    results: list[TranslationWithEvaluation] = Field(..., description="Translation results")
    summary: RunSummary = Field(..., description="Run summary")
    created_at: str = Field(..., description="Timestamp of run creation")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(default="0.1.0", description="API version")


class RunListItem(BaseModel):
    """Summary of a translation run for list view."""

    id: int
    created_at: str
    source_lang: str | None
    target_lang: str
    source_text_preview: str
    provider_count: int
    avg_score: float | None
