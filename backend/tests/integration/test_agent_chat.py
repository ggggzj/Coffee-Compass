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


async def _final_event(pgvector_url, monkeypatch, *, scripted, message="find me a quiet cafe"):
    """POST /agent/chat (SSE) and return the single final event's data dict."""
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

    assert r.status_code == 200
    finals = events_of(parse_sse(r.text), "final")
    assert len(finals) == 1
    return finals[0]["data"]


@pytest.mark.asyncio
async def test_agent_chat_returns_grounded_declared_recommendations(pgvector_url, monkeypatch):
    scripted = [
        calls("search_shops", {"query": "quiet study spot"}),
        calls("present_recommendations", {"cafe_ids": [1], "rationale": "Bricks is quiet."}, "c2"),
        final("I recommend Bricks — a quiet study spot."),
    ]
    data = await _final_event(pgvector_url, monkeypatch, scripted=scripted)

    assert "Bricks" in data["reply"]
    recs = data["recommendations"]
    assert [c["id"] for c in recs] == [1]  # grounded: declared id that the tool surfaced
    assert recs[0]["name"] == "Bricks"
    assert recs[0]["lat"] == pytest.approx(34.0205)
    assert recs[0]["lng"] == pytest.approx(-118.2855)


@pytest.mark.asyncio
async def test_agent_chat_falls_back_to_last_search_when_no_declaration(
    pgvector_url, monkeypatch
):
    # The model searches, then answers in prose WITHOUT calling
    # present_recommendations. The final payload must still be populated from the
    # last search_shops batch — the map is never left empty.
    scripted = [
        calls("search_shops", {"query": "quiet study spot"}),
        final("There are a couple of nice quiet spots near campus."),
    ]
    data = await _final_event(pgvector_url, monkeypatch, scripted=scripted)

    recs = data["recommendations"]
    assert len(recs) >= 1  # fallback populated from the last search batch
    assert {c["name"] for c in recs} <= {"Bricks", "Dinosaur"}
    assert all(c["lat"] is not None and c["lng"] is not None for c in recs)


@pytest.mark.asyncio
async def test_agent_chat_drops_ungrounded_declared_ids(pgvector_url, monkeypatch):
    # The model declares id 999, which the tools never surfaced. A pin can only
    # exist for a cafe a tool genuinely returned (ADR-0001), so 999 is dropped.
    scripted = [
        calls("search_shops", {"query": "quiet study spot"}),
        calls("present_recommendations", {"cafe_ids": [1, 999], "rationale": "picks"}, "c2"),
        final("Here is my pick."),
    ]
    data = await _final_event(pgvector_url, monkeypatch, scripted=scripted)

    ids = [c["id"] for c in data["recommendations"]]
    assert ids == [1]  # 999 was never surfaced by a tool, so it is dropped
