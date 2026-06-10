import os

# Disable testcontainers' Ryuk sidecar before importing testcontainers.
# Ryuk's port mapping is unreliable on macOS Docker Desktop and is the leading
# cause of "Port mapping for container ... is not available" failures. The
# container fixtures below already clean up via try/finally, so we don't need
# Ryuk's auto-cleanup.
os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")

from collections.abc import AsyncIterator  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer  # noqa: E402

from app import models  # noqa: F401, E402
from app.db import Base  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_slot_cache():
    """Clear the shared search-pipeline slot cache between tests so a cached query
    from one test cannot leak a result into another. The cache is the single
    instance in app.search.service, shared by /search and the agent tools."""
    from app.search.service import reset_slot_cache

    reset_slot_cache()
    yield
    reset_slot_cache()


@pytest_asyncio.fixture(scope="session")
async def pgvector_url() -> AsyncIterator[str]:
    container = PostgresContainer("pgvector/pgvector:pg16", username="t", password="t", dbname="t")
    container.start()
    try:
        url = container.get_connection_url().replace("postgresql+psycopg2", "postgresql+asyncpg")
        engine = create_async_engine(url)
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        yield url
    finally:
        container.stop()


@pytest_asyncio.fixture
async def session(pgvector_url: str) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(pgvector_url)
    # Truncate user tables before each test so commits in earlier tests do not
    # leak rows into later ones. RESTART IDENTITY also resets sequence values
    # so primary keys start over at 1 in each test.
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE prompt_versions, cafes RESTART IDENTITY CASCADE"))
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as s:
        yield s
    await engine.dispose()
