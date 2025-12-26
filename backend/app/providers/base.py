"""
AI Translation Benchmark - Base Provider Interface

Author: Zoltan Tamas Toth

Abstract base class for all translation providers.
"""

import time
from abc import ABC, abstractmethod
from typing import Any

from app.core.logging import get_logger
from app.schemas.provider import TranslationResult

logger = get_logger(__name__)


class TranslatorProvider(ABC):
    """Abstract base class for translation providers."""

    def __init__(self, name: str, model: str, timeout: int = 30):
        """
        Initialize provider.

        Args:
            name: Provider display name
            model: Model identifier
            timeout: Request timeout in seconds
        """
        self.name = name
        self.model = model
        self.timeout = timeout

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str | None,
        target_lang: str,
        **options: Any,
    ) -> TranslationResult:
        """
        Translate text from source to target language.

        Args:
            text: Source text to translate
            source_lang: Source language code (optional)
            target_lang: Target language code
            **options: Additional provider-specific options

        Returns:
            TranslationResult with translation and metadata

        Raises:
            Exception: If translation fails
        """
        pass

    async def translate_with_timing(
        self,
        text: str,
        source_lang: str | None,
        target_lang: str,
        **options: Any,
    ) -> TranslationResult:
        """
        Translate text and measure latency.

        Args:
            text: Source text to translate
            source_lang: Source language code (optional)
            target_lang: Target language code
            **options: Additional provider-specific options

        Returns:
            TranslationResult with translation and latency
        """
        start_time = time.time()

        try:
            logger.info(
                f"Starting translation with {self.name} ({self.model}) " f"to '{target_lang}'"
            )

            result = await self.translate(text, source_lang, target_lang, **options)

            latency_ms = (time.time() - start_time) * 1000
            result.latency_ms = latency_ms

            logger.info(f"Translation completed with {self.name} in {latency_ms:.2f}ms")

            return result

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            logger.error(f"Translation failed with {self.name}: {error_msg}")

            return TranslationResult(
                provider_name=self.name,
                model_id=self.model,
                output_text="",
                latency_ms=latency_ms,
                error=error_msg,
            )

    def __str__(self) -> str:
        """String representation of provider."""
        return f"{self.name} ({self.model})"
