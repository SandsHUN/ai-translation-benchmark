"""
AI Translation Benchmark - Health Check Route

Author: Zoltan Tamas Toth

Health check endpoint for monitoring and CI/CD.
"""

from fastapi import APIRouter

from app.core.constants import MSG_HEALTH_OK, ROUTE_HEALTH
from app.schemas.api import HealthResponse

router = APIRouter()


@router.get(ROUTE_HEALTH, response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with status
    """
    return HealthResponse(status=MSG_HEALTH_OK, version="0.1.0")
