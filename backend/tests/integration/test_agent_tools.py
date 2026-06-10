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


def _tool(tools, name):
    return next(t for t in tools if t.name == name)


@pytest.mark.asyncio
async def test_search_shops_returns_grounded_cafes(session, monkeypatch):
    from app.agent.tools import build_agent_tools

    _patch_pipeline(monkeypatch)
    session.add(_seed_cafe(google_place_id="A", name="Bricks", lat=34.0205, lng=-118.2855))
    await session.commit()

    tools = build_agent_tools(session)
    result = await _tool(tools, "search_shops").ainvoke({"query": "quiet with outlets"})

    assert len(result) == 1
    shop = result[0]
    assert shop["name"] == "Bricks"
    assert shop["id"] == 1  # grounded: a real cafe id from the seeded DB
    assert shop["lat"] == pytest.approx(34.0205)
    assert shop["lng"] == pytest.approx(-118.2855)
    assert shop["open_now"] is False  # opening_hours has no periods


@pytest.mark.asyncio
async def test_get_shop_detail_returns_full_cafe(session):
    from app.agent.tools import build_agent_tools

    session.add(
        _seed_cafe(
            google_place_id="A",
            name="Bricks",
            address="123 Trousdale Pkwy",
            lat=34.0205,
            lng=-118.2855,
            rating=4.6,
        )
    )
    await session.commit()

    tools = build_agent_tools(session)
    detail = await _tool(tools, "get_shop_detail").ainvoke({"cafe_id": 1})

    assert detail["id"] == 1
    assert detail["name"] == "Bricks"
    assert detail["address"] == "123 Trousdale Pkwy"
    assert detail["rating"] == pytest.approx(4.6)
    assert detail["lat"] == pytest.approx(34.0205)
    assert detail["lng"] == pytest.approx(-118.2855)


@pytest.mark.asyncio
async def test_get_shop_detail_handles_unknown_id(session):
    from app.agent.tools import build_agent_tools

    tools = build_agent_tools(session)
    # No cafes seeded — id 999 does not exist. The tool must degrade to an
    # LLM-readable result, not raise, so the agent can recover.
    detail = await _tool(tools, "get_shop_detail").ainvoke({"cafe_id": 999})

    assert detail["id"] == 999
    assert detail["error"] == "not_found"
