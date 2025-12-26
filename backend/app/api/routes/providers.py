"""
AI Translation Benchmark - Providers Route

Author: Zoltan Tamas Toth

Provider information endpoint.
"""

from fastapi import APIRouter

from app.core.config import config_manager
from app.core.constants import ROUTE_PROVIDERS
from app.schemas.provider import ProviderInfo

router = APIRouter()


@router.get(ROUTE_PROVIDERS, response_model=list[ProviderInfo])
async def get_providers() -> list[ProviderInfo]:
    """
    Get list of available providers.

    Returns:
        List of ProviderInfo (anonymized, no API keys)
    """
    providers = config_manager.get_providers()

    provider_list = [
        ProviderInfo(
            type=p.get("type", ""),
            name=p.get("name", ""),
            model=p.get("model", ""),
            enabled=p.get("enabled", False),
        )
        for p in providers
    ]

    return provider_list
