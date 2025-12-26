"""
AI Translation Benchmark - DeepL Provider

Author: Zoltan Tamas Toth
Date: 2025-12-26

Translation provider implementation for DeepL API.
DeepL offers 500,000 characters/month free tier.
"""

from typing import Any

import deepl

from app.core.logging import get_logger
from app.providers.base import TranslatorProvider
from app.schemas.provider import TranslationResult

logger = get_logger(__name__)

# Language code mapping for DeepL
DEEPL_LANGUAGE_CODES = {
    'en': 'EN',
    'de': 'DE',
    'fr': 'FR',
    'es': 'ES',
    'it': 'IT',
    'pt': 'PT-PT',
    'ru': 'RU',
    'zh': 'ZH',
    'ja': 'JA',
    'ko': 'KO',
}


class DeepLProvider(TranslatorProvider):
    """DeepL translation provider."""

    def __init__(
        self,
        name: str,
        model: str,
        api_key: str,
        timeout: int = 30,
    ):
        """
        Initialize DeepL provider.

        Args:
            name: Provider display name
            model: Model identifier (not used by DeepL, kept for consistency)
            api_key: DeepL API key
            timeout: Request timeout in seconds
        """
        super().__init__(name, model, timeout)

        if not api_key:
            raise ValueError("DeepL API key not provided")

        self.translator = deepl.Translator(api_key)

    async def translate(
        self,
        text: str,
        source_lang: str | None,
        target_lang: str,
        **options: Any,
    ) -> TranslationResult:
        """
        Translate text using DeepL API.

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
            # Convert language codes to DeepL format
            target_lang_deepl = DEEPL_LANGUAGE_CODES.get(target_lang, target_lang.upper())
            source_lang_deepl = DEEPL_LANGUAGE_CODES.get(source_lang) if source_lang else None

            logger.info(f"Calling DeepL API - Target: {target_lang_deepl}")
            logger.debug(f"Request text: {text[:100]}...")

            # Call DeepL API (synchronous, but we're in async context)
            # DeepL SDK doesn't have async support yet
            result = self.translator.translate_text(
                text,
                target_lang=target_lang_deepl,
                source_lang=source_lang_deepl,
            )

            logger.info(f"DeepL API response received")

            output_text = result.text

            logger.info(
                f"DeepL translation successful - Output length: {len(output_text)} chars"
            )

            return TranslationResult(
                provider_name=self.name,
                model_id=self.model,
                output_text=output_text.strip(),
                latency_ms=0.0,  # Will be set by translate_with_timing
                usage_tokens=None,  # DeepL doesn't provide token count
                raw_response={"detected_source_lang": result.detected_source_lang} if hasattr(result, 'detected_source_lang') else None,
            )

        except Exception as e:
            logger.error(f"DeepL API error: {str(e)}")
            logger.exception("Full DeepL error traceback:")
            raise
