"""
AI Translation Benchmark - Local OpenAI-Compatible Provider

Author: Zoltan Tamas Toth
Date: 2025-12-25

Translation provider for OpenAI-compatible local endpoints (e.g., LM Studio).
"""

from typing import Any

from openai import AsyncOpenAI

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


class LocalOpenAIProvider(TranslatorProvider):
    """Local OpenAI-compatible endpoint provider."""

    def __init__(
        self,
        name: str,
        model: str,
        base_url: str,
        timeout: int = 300,
    ):
        """
        Initialize local OpenAI-compatible provider.

        Args:
            name: Provider display name
            model: Model identifier
            base_url: Base URL for the local API (e.g., 'http://localhost:1234/v1')
            timeout: Request timeout in seconds
        """
        super().__init__(name, model, timeout)

        self.base_url = base_url

        # Auto-detect model if needed
        if not model or model == "local-model":
            try:
                import httpx
                response = httpx.get(f"{base_url.rstrip('/v1')}/v1/models", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        self.model = data["data"][0]["id"]
                        logger.info(f"Auto-detected model: {self.model}")
            except Exception as e:
                logger.warning(f"Could not auto-detect model: {e}")

        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="not-needed",
            timeout=timeout,
        )

    async def translate(
        self,
        text: str,
        source_lang: str | None,
        target_lang: str,
        **options: Any,
    ) -> TranslationResult:
        """
        Translate text using local OpenAI-compatible endpoint.

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
            logger.info(f"Calling LM Studio API - URL: {self.base_url}, Model: {self.model}, Target: {target_lang}")
            logger.debug(f"Request text: {text[:100]}...")
            # Call local API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
            )
            logger.info(f"LM Studio API response received from {self.base_url}")

            # Extract translation
            output_text = response.choices[0].message.content or ""

            # Get token usage if available
            usage_tokens = None
            if response.usage:
                usage_tokens = response.usage.total_tokens

            logger.info(
                f"LM Studio translation successful - URL: {self.base_url}, Tokens: {usage_tokens}, Output length: {len(output_text)} chars"
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
            logger.error(f"LM Studio API error ({self.base_url}): {str(e)}")
            logger.exception("Full LM Studio error traceback:")
            raise
