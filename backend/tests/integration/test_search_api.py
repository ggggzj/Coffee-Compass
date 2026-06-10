import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import get_session
from app.main import app
from app.models import Cafe
from app.search.slot_extractor import ParsedQuery


def _seed_cafe(**overrides):
    base = dict(
        google_place_id="g",
        name="Cafe",
        address="addr",
        lat=34.0,
        lng=-118.0,
        rating=4.0,
        review_count=10,
        price_level=2,
        categories=["cafe"],
        opening_hours={"periods": []},
        has_wifi=True,
        has_outlet=True,
        noise_level="quiet",
        good_for_studying=True,
        ambience_text="Quiet study spot",
        embedding=[0.1] * 1536,
    )
    base.update(overrides)
    return Cafe(**base)


@pytest.mark.asyncio
async def test_search_endpoint_end_to_end(pgvector_url, monkeypatch):
    test_engine = create_async_engine(pgvector_url)
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE cafes RESTART IDENTITY CASCADE"))

    async with TestSession() as s:
        s.add(_seed_cafe(google_place_id="A", name="Bricks", has_outlet=True))
        s.add(_seed_cafe(google_place_id="B", name="NoOutlet", has_outlet=False))
        await s.commit()

    async def override_session():
        async with TestSession() as s:
            yield s

    app.dependency_overrides[get_session] = override_session

    async def fake_extract(**kwargs):
        return ParsedQuery(
            semantic_query="quiet study spot",
            has_outlet=True,
            open_now=None,
            price_max=None,
        )

    async def fake_embed(self, text: str):
        return [0.1] * 1536

    monkeypatch.setattr("app.search.service.extract_slots", fake_extract)
    monkeypatch.setattr("app.search.embedder.Embedder.embed", fake_embed)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/search", json={"query": "quiet with outlets", "top_k": 5})

    app.dependency_overrides.clear()
    await test_engine.dispose()

    assert r.status_code == 200
    body = r.json()
    assert body["parsed"]["semantic_query"] == "quiet study spot"
    assert body["parsed"]["filters"]["has_outlet"] is True
    names = [x["name"] for x in body["results"]]
    assert names == ["Bricks"]  # NoOutlet was filtered out


@pytest.mark.asyncio
async def test_search_endpoint_returns_coordinates(pgvector_url, monkeypatch):
    test_engine = create_async_engine(pgvector_url)
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE cafes RESTART IDENTITY CASCADE"))

    async with TestSession() as s:
        s.add(_seed_cafe(google_place_id="A", name="Bricks", lat=34.0205, lng=-118.2855))
        await s.commit()

    async def override_session():
        async with TestSession() as s:
            yield s

    app.dependency_overrides[get_session] = override_session

    async def fake_extract(**kwargs):
        return ParsedQuery(
            semantic_query="quiet study spot", has_outlet=None, open_now=None, price_max=None
        )

    async def fake_embed(self, text: str):
        return [0.1] * 1536

    monkeypatch.setattr("app.search.service.extract_slots", fake_extract)
    monkeypatch.setattr("app.search.embedder.Embedder.embed", fake_embed)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/search", json={"query": "quiet", "top_k": 5})

    app.dependency_overrides.clear()
    await test_engine.dispose()

    assert r.status_code == 200
    result = r.json()["results"][0]
    assert result["lat"] == pytest.approx(34.0205)
    assert result["lng"] == pytest.approx(-118.2855)
