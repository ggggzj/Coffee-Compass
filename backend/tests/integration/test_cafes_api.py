import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import get_session
from app.main import app
from tests.integration.agent_helpers import seed_cafe


async def _get(pgvector_url, path, *, seed=None):
    test_engine = create_async_engine(pgvector_url)
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE cafes RESTART IDENTITY CASCADE"))
    if seed is not None:
        async with TestSession() as s:
            s.add(seed)
            await s.commit()

    async def override_session():
        async with TestSession() as s:
            yield s

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            return await client.get(path)
    finally:
        app.dependency_overrides.clear()
        await test_engine.dispose()


@pytest.mark.asyncio
async def test_get_cafe_returns_detail(pgvector_url):
    cafe = seed_cafe(
        google_place_id="A",
        name="Bricks",
        address="123 Trousdale Pkwy",
        lat=34.0205,
        lng=-118.2855,
        rating=4.6,
        ambience_text="Quiet study spot",
    )
    r = await _get(pgvector_url, "/cafes/1", seed=cafe)

    assert r.status_code == 200
    body = r.json()
    assert body["id"] == 1
    assert body["name"] == "Bricks"
    assert body["address"] == "123 Trousdale Pkwy"
    assert body["lat"] == pytest.approx(34.0205)
    assert body["lng"] == pytest.approx(-118.2855)
    assert body["rating"] == pytest.approx(4.6)
    assert body["ambience_text"] == "Quiet study spot"
    assert "opening_hours" in body


@pytest.mark.asyncio
async def test_get_cafe_unknown_returns_404(pgvector_url):
    r = await _get(pgvector_url, "/cafes/999")
    assert r.status_code == 404
