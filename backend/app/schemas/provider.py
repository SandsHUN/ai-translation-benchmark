"""
AI Translation Benchmark - Provider Schemas

Author: Zoltan Tamas Toth
Date: 2025-12-25

Pydantic models for translation providers and results.
"""

from typing import Any

from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Configuration for a translation provider."""

    type: str = Field(..., description="Provider type (openai, local_openai, etc.)")
    name: str = Field(..., description="Provider display name")
    model: str = Field(..., description="Model identifier")
    base_url: str | None = Field(None, description="Base URL for API (local providers)")
    api_key: str | None = Field(None, description="API key (for cloud providers)")
    timeout: int = Field(30, description="Request timeout in seconds")
    enabled: bool = Field(True, description="Whether provider is enabled")


class TranslationResult(BaseModel):
    """Unified translation result from any provider."""

    provider_name: str = Field(..., description="Provider name")
    model_id: str = Field(..., description="Model identifier")
    output_text: str = Field(..., description="Translated text")
    latency_ms: float = Field(..., description="Translation latency in milliseconds")
    usage_tokens: int | None = Field(None, description="Token usage (if available)")
    raw_response: dict[str, Any] | None = Field(None, description="Raw API response")
    error: str | None = Field(None, description="Error message if translation failed")


class ProviderInfo(BaseModel):
    """Provider metadata for frontend display."""

    type: str = Field(..., description="Provider type")
    name: str = Field(..., description="Provider display name")
    model: str = Field(..., description="Model identifier")
    enabled: bool = Field(..., description="Whether provider is enabled")
