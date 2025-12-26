"""
AI Translation Benchmark - Test Configuration

Author: Zoltan Tamas Toth
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base


@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "Hello, world! This is a test translation."


@pytest.fixture
def sample_translation():
    """Sample translation for testing."""
    return "¡Hola, mundo! Esta es una traducción de prueba."
