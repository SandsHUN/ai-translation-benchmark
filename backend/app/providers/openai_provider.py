"""
AI Translation Benchmark - OpenAI Provider

Author: Zoltan Tamas Toth
Date: 2025-12-25

Translation provider implementation for OpenAI API.
"""

from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.constants import TRANSLATION_SYSTEM_PROMPT
from app.core.logging import get_logger
from app.providers.base import TranslatorProvider
from app.schemas.provider import TranslationResult

logger = get_logger(__name__)

# Language code to full name mapping
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'hu': 'Hungarian',
    'vi': 'Vietnamese',
    'th': 'Thai',
}

def get_language_name(lang_code: str) -> str:
    """Get full language name from code."""
    return LANGUAGE_NAMES.get(lang_code, lang_code)


class OpenAIProvider(TranslatorProvider):
    """OpenAI translation provider."""

    def __init__(
        self,
        name: str,
        model: str,
        api_key: str | None = None,
        timeout: int = 30,
    ):
        """
        Initialize OpenAI provider.

        Args:
            name: Provider display name
            model: OpenAI model identifier (e.g., 'gpt-4', 'gpt-3.5-turbo')
            api_key: OpenAI API key (defaults to settings)
            timeout: Request timeout in seconds
        """
        super().__init__(name, model, timeout)

        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = AsyncOpenAI(api_key=self.api_key, timeout=timeout)

    async def translate(
        self,
        text: str,
        source_lang: str | None,
        target_lang: str,
        **options: Any,
    ) -> TranslationResult:
        """
        Translate text using OpenAI API.

        Args:
            text: Source text to translate
            source_lang: Source language code (optional)
            target_lang: Target language code
            **options: Additional options (temperature, etc.)

        Returns:
            TranslationResult with translation

        Raises:
            Exception: If API call fails
        """
        # Prepare system prompt
        source_lang_str = get_language_name(source_lang) if source_lang else "the source language"
        target_lang_str = get_language_name(target_lang)
        
        system_prompt = TRANSLATION_SYSTEM_PROMPT.format(
            source_lang=source_lang_str,
            target_lang=target_lang_str,
        )

        # Prepare user message with full language name
        user_message = f"Translate to {target_lang_str}:\n\n{text}"

        # Get temperature from options or use default
        temperature = options.get("temperature", 0.3)

        try:
            logger.info(f"Calling OpenAI API - Model: {self.model}, Target: {target_lang}")
            logger.debug(f"Request text: {text[:100]}...")
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
            )
            
            logger.info(f"OpenAI API response received")

            # Extract translation
            output_text = response.choices[0].message.content or ""

            # Get token usage
            usage_tokens = None
            if response.usage:
                usage_tokens = response.usage.total_tokens

            logger.info(
                f"OpenAI translation successful - Tokens: {usage_tokens}, Output length: {len(output_text)} chars"
            )

            return TranslationResult(
                provider_name=self.name,
                model_id=self.model,
                output_text=output_text.strip(),
                latency_ms=0.0,  # Will be set by translate_with_timing
                usage_tokens=usage_tokens,
                raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            logger.exception("Full OpenAI error traceback:")
            raise
