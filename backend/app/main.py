"""
AI Translation Benchmark - FastAPI Application

Author: Zoltan Tamas Toth

Main FastAPI application with routes, middleware, and lifecycle management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, providers, translation
from app.core.config import settings
from app.core.constants import API_PREFIX
from app.core.logging import setup_logging
from app.db.database import db

# Setup logging
logger = setup_logging(settings.log_level, settings.log_dir)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Translation Benchmark API")
    logger.info(f"Log level: {settings.log_level}")

    # Initialize database
    try:
        await db.create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Translation Benchmark API")
    await db.close()


# Create FastAPI application
app = FastAPI(
    title="AI Translation Benchmark",
    description="Multi-provider AI translation evaluation platform with quality estimation",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix=API_PREFIX, tags=["Health"])
app.include_router(providers.router, prefix=API_PREFIX, tags=["Providers"])
app.include_router(translation.router, prefix=API_PREFIX, tags=["Translation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Translation Benchmark API",
        "version": "0.1.0",
        "author": "Zoltan Tamas Toth",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
