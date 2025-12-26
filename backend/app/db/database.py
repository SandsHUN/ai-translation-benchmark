"""
AI Translation Benchmark - Database Connection

Author: Zoltan Tamas Toth

Database engine setup and session management for SQLite.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import Base

logger = get_logger(__name__)


class Database:
    """Database connection manager."""

    def __init__(self, database_url: str | None = None):
        """
        Initialize database connection.

        Args:
            database_url: Database connection URL (defaults to settings)
        """
        self.database_url = database_url or settings.database_url

        # Convert sqlite:/// to sqlite+aiosqlite:/// for async support
        if self.database_url.startswith("sqlite:///"):
            self.database_url = self.database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

        # Create database directory if it doesn't exist
        if "sqlite" in self.database_url:
            db_path = self.database_url.split("///")[-1]
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create async engine
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            poolclass=StaticPool,  # Use StaticPool for SQLite
        )

        # Create session factory
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self) -> None:
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

    async def drop_tables(self) -> None:
        """Drop all database tables (use with caution)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("Database tables dropped")

    async def close(self) -> None:
        """Close database connection."""
        await self.engine.dispose()
        logger.info("Database connection closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session context manager.

        Yields:
            AsyncSession instance
        """
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database instance
db = Database()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session.

    Yields:
        AsyncSession instance
    """
    async with db.get_session() as session:
        yield session
