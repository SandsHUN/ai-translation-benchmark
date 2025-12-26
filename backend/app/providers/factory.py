"""
AI Translation Benchmark - Provider Factory

Author: Zoltan Tamas Toth
Date: 2025-12-25

Factory for creating translation provider instances from configuration.
"""

from typing import Any

from app.core.config import settings
from app.core.constants import (
    PROVIDER_TYPE_DEEPL,
    PROVIDER_TYPE_GOOGLE,
    PROVIDER_TYPE_LOCAL_OPENAI,
    PROVIDER_TYPE_OPENAI,
)
from app.core.logging import get_logger
from app.providers.base import TranslatorProvider
from app.providers.deepl_provider import DeepLProvider
from app.providers.google_translate_provider import GoogleTranslateProvider
from app.providers.local_openai_provider import LocalOpenAIProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas.provider import ProviderConfig

logger = get_logger(__name__)


class ProviderFactory:
    """Factory for creating translation providers."""

    @staticmethod
    def create_provider(config: ProviderConfig | dict[str, Any]) -> TranslatorProvider:
        """
        Create a provider instance from configuration.

        Args:
            config: Provider configuration (ProviderConfig or dict)

        Returns:
            TranslatorProvider instance

        Raises:
            ValueError: If provider type is unsupported
        """
        # Convert dict to ProviderConfig if needed
        if isinstance(config, dict):
            config = ProviderConfig(**config)

        provider_type = config.type.lower()

        logger.info(f"Creating provider: {config.name} (type: {provider_type})")

        if provider_type == PROVIDER_TYPE_OPENAI:
            # Get API key from config or request
            api_key = config.api_key if hasattr(config, 'api_key') and config.api_key else settings.openai_api_key

            return OpenAIProvider(
                name=config.name,
                model=config.model,
                api_key=api_key,
                timeout=config.timeout,
            )

        elif provider_type == PROVIDER_TYPE_LOCAL_OPENAI:
            if not config.base_url:
                raise ValueError(f"base_url required for local_openai provider: {config.name}")

            return LocalOpenAIProvider(
                name=config.name,
                model=config.model,
                base_url=config.base_url,
                timeout=config.timeout,
            )

        elif provider_type == PROVIDER_TYPE_DEEPL:
            # Get API key from config or request
            api_key = config.api_key if hasattr(config, 'api_key') and config.api_key else None
            if not api_key:
                raise ValueError(f"API key required for DeepL provider: {config.name}")

            return DeepLProvider(
                name=config.name,
                model=config.model or "deepl",
                api_key=api_key,
                timeout=config.timeout,
            )

        elif provider_type == PROVIDER_TYPE_GOOGLE:
            # Get API key from config or request
            api_key = config.api_key if hasattr(config, 'api_key') and config.api_key else None
            if not api_key:
                raise ValueError(f"API key required for Google Translate provider: {config.name}")

            return GoogleTranslateProvider(
                name=config.name,
                model=config.model or "default",
                api_key=api_key,
                timeout=config.timeout,
            )

        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    @staticmethod
    def create_from_request(provider_request: dict[str, Any]) -> TranslatorProvider:
        """
        Create provider from API request data.

        Args:
            provider_request: Provider request data from API

        Returns:
            TranslatorProvider instance
        """
        provider_type = provider_request.get("type", "").lower()
        model = provider_request.get("model", "")
        base_url = provider_request.get("base_url")
        api_key = provider_request.get("api_key")

        # Generate name from type and model
        name = f"{provider_type.upper()} - {model}"

        config = ProviderConfig(
            type=provider_type,
            name=name,
            model=model,
            base_url=base_url,
            api_key=api_key,
            timeout=provider_request.get("timeout", 30),
            enabled=True,
        )

        return ProviderFactory.create_provider(config)


# Provider registry for extensibility
PROVIDER_REGISTRY: dict[str, type[TranslatorProvider]] = {
    PROVIDER_TYPE_OPENAI: OpenAIProvider,
    PROVIDER_TYPE_LOCAL_OPENAI: LocalOpenAIProvider,
}


def register_provider(provider_type: str, provider_class: type[TranslatorProvider]) -> None:
    """
    Register a new provider type.

    Args:
        provider_type: Provider type identifier
        provider_class: Provider class
    """
    PROVIDER_REGISTRY[provider_type.lower()] = provider_class
    logger.info(f"Registered provider type: {provider_type}")
