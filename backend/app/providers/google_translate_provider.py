"""
AI Translation Benchmark - Google Cloud Translation Provider

Author: Zoltan Tamas Toth
Date: 2025-12-26

Translation provider implementation for Google Cloud Translation API.
Google Cloud offers 500,000 characters/month free tier.
"""

from typing import Any

from google.cloud import translate_v2 as translate

from app.core.logging import get_logger
from app.providers.base import TranslatorProvider
from app.schemas.provider import TranslationResult

logger = get_logger(__name__)


class GoogleTranslateProvider(TranslatorProvider):
    """Google Cloud Translation provider."""

    def __init__(
        self,
        name: str,
        model: str,
        api_key: str,
        timeout: int = 30,
    ):
        """
        Initialize Google Cloud Translation provider.

        Args:
            name: Provider display name
            model: Model identifier (basic/advanced)
            api_key: Google Cloud API key
            timeout: Request timeout in seconds
        """
        super().__init__(name, model, timeout)

        if not api_key:
            raise ValueError("Google Cloud API key not provided")

        # Initialize client with API key
        self.client = translate.Client(api_key=api_key)

    async def translate(
        self,
        text: str,
        source_lang: str | None,
        target_lang: str,
        **options: Any,
    ) -> TranslationResult:
        """
        Translate text using Google Cloud Translation API.

        Args:
            text: Source text to translate
            source_lang: Source language code (optional)
            target_lang: Target language code
            **options: Additional options

        Returns:
            TranslationResult with translation

        Raises:
            Exception: If API call fails
        """
        try:
            logger.info(f"Calling Google Translate API - Target: {target_lang}")
            logger.debug(f"Request text: {text[:100]}...")

            # Call Google Translate API (synchronous)
            result = self.client.translate(
                text,
                target_language=target_lang,
                source_language=source_lang,
                model=self.model if self.model != "default" else None,
            )

            logger.info("Google Translate API response received")

            output_text = result["translatedText"]
            detected_source = result.get("detectedSourceLanguage")

            logger.info(
                f"Google Translate successful - Output length: {len(output_text)} chars, "
                f"Detected source: {detected_source}"
            )

            return TranslationResult(
                provider_name=self.name,
                model_id=self.model,
                output_text=output_text.strip(),
                latency_ms=0.0,  # Will be set by translate_with_timing
                usage_tokens=None,  # Google doesn't provide token count
                raw_response={
                    "detected_source_language": detected_source,
                    "model": result.get("model"),
                },
            )

        except Exception as e:
            logger.error(f"Google Translate API error: {str(e)}")
            logger.exception("Full Google Translate error traceback:")
            raise
