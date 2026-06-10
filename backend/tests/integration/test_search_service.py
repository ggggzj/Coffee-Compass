import pytest

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


def _patch_pipeline(monkeypatch, *, semantic_query="quiet study spot", **slots):
    parsed = ParsedQuery(
        semantic_query=semantic_query,
        has_outlet=slots.get("has_outlet"),
        open_now=slots.get("open_now"),
        price_max=slots.get("price_max"),
    )

    async def fake_extract(**kwargs):
        return parsed

    async def fake_embed(self, text: str):
        return [0.1] * 1536

    monkeypatch.setattr("app.search.service.extract_slots", fake_extract)
    monkeypatch.setattr("app.search.embedder.Embedder.embed", fake_embed)


@pytest.mark.asyncio
async def test_search_cafes_returns_cafe_coordinates(session, monkeypatch):
    from app.search.service import search_cafes

    _patch_pipeline(monkeypatch)
    session.add(_seed_cafe(google_place_id="A", name="Bricks", lat=34.0205, lng=-118.2855))
    await session.commit()

    outcome = await search_cafes(query="quiet with outlets", top_k=5, session=session)

    assert [r.name for r in outcome.results] == ["Bricks"]
    only = outcome.results[0]
    assert only.lat == pytest.approx(34.0205)
    assert only.lng == pytest.approx(-118.2855)


@pytest.mark.asyncio
async def test_repeated_query_hits_shared_cache_and_skips_extraction(session, monkeypatch):
    from app.search import service
    from app.search.service import search_cafes

    extract_calls = 0
    parsed = ParsedQuery(
        semantic_query="quiet study spot", has_outlet=None, open_now=None, price_max=None
    )

    async def counting_extract(**kwargs):
        nonlocal extract_calls
        extract_calls += 1
        return parsed

    async def fake_embed(self, text: str):
        return [0.1] * 1536

    monkeypatch.setattr(service, "extract_slots", counting_extract)
    monkeypatch.setattr("app.search.embedder.Embedder.embed", fake_embed)

    session.add(_seed_cafe(google_place_id="A", name="Bricks"))
    await session.commit()

    first = await search_cafes(query="same query", top_k=5, session=session)
    second = await search_cafes(query="same query", top_k=5, session=session)

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert extract_calls == 1  # the second call reused the cached parse + embedding
