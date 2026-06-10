import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import get_session
from app.main import app
from tests.integration.agent_helpers import (
    FakeToolCallingModel,
    calls,
    events_of,
    fake_embed,
    fake_extract,
    final,
    parse_sse,
    seed_cafe,
)


async def _stream_agent(pgvector_url, monkeypatch, *, scripted, message="find a quiet cafe"):
    from app.api.agent import get_agent_model

    test_engine = create_async_engine(pgvector_url)
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE cafes RESTART IDENTITY CASCADE"))
    async with TestSession() as s:
        s.add(seed_cafe(google_place_id="A", name="Bricks", lat=34.0205, lng=-118.2855))
        s.add(seed_cafe(google_place_id="B", name="Dinosaur", lat=34.03, lng=-118.27))
        await s.commit()

    async def override_session():
        async with TestSession() as s:
            yield s

    monkeypatch.setattr("app.search.service.extract_slots", fake_extract)
    monkeypatch.setattr("app.search.embedder.Embedder.embed", fake_embed)

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_agent_model] = lambda: FakeToolCallingModel(responses=scripted)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post(
                "/agent/chat",
                json={"session_id": "s1", "user_id": "demo-user", "message": message},
            )
    finally:
        app.dependency_overrides.clear()
        await test_engine.dispose()
    return r


@pytest.mark.asyncio
async def test_agent_chat_streams_steps_then_one_final(pgvector_url, monkeypatch):
    scripted = [
        calls("search_shops", {"query": "quiet study spot"}),
        calls("present_recommendations", {"cafe_ids": [1], "rationale": "Bricks is quiet."}, "c2"),
        final("I recommend Bricks — a quiet study spot."),
    ]
    r = await _stream_agent(pgvector_url, monkeypatch, scripted=scripted)

    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    events = parse_sse(r.text)

    # The search tool was surfaced as an action + observation.
    actions = events_of(events, "action")
    assert any(a["data"]["tool"] == "search_shops" for a in actions)
    assert events_of(events, "observation")

    # Exactly one final event, carrying the grounded recommendation.
    finals = events_of(events, "final")
    assert len(finals) == 1
    data = finals[0]["data"]
    assert "Bricks" in data["reply"]
    assert [c["id"] for c in data["recommendations"]] == [1]
    assert data["recommendations"][0]["lat"] == pytest.approx(34.0205)


@pytest.mark.asyncio
async def test_final_event_is_last_and_unique(pgvector_url, monkeypatch):
    scripted = [
        calls("search_shops", {"query": "quiet study spot"}),
        calls("present_recommendations", {"cafe_ids": [1], "rationale": "x"}, "c2"),
        final("Bricks it is."),
    ]
    r = await _stream_agent(pgvector_url, monkeypatch, scripted=scripted)
    types = [e["event"] for e in parse_sse(r.text)]

    # Exactly one final, and it is the terminal event — all reasoning precedes it.
    assert types.count("final") == 1
    assert types[-1] == "final"
    assert "action" in types[: types.index("final")]
    assert "observation" in types[: types.index("final")]
