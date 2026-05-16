from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app import models  # noqa: F401
from app.db import Base


@pytest_asyncio.fixture(scope="session")
async def pgvector_url() -> AsyncIterator[str]:
    container = PostgresContainer("pgvector/pgvector:pg16", username="t", password="t", dbname="t")
    container.start()
    try:
        url = container.get_connection_url().replace("postgresql+psycopg2", "postgresql+asyncpg")
        engine = create_async_engine(url)
        async with engine.begin() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector")
            )
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        yield url
    finally:
        container.stop()


@pytest_asyncio.fixture
async def session(pgvector_url: str) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(pgvector_url)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as s:
        yield s
        await s.rollback()
    await engine.dispose()
