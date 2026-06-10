import pytest
from httpx import ASGITransport, AsyncClient
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import get_session
from app.main import app
from app.models import Cafe
from app.search.slot_extractor import ParsedQuery


class FakeToolCallingModel(BaseChatModel):
    """A chat model that replays a scripted list of AIMessages, one per call.

    Lets us drive the agent's tool-calling loop deterministically with no network.
    """

    responses: list
    i: int = 0

    @property
    def _llm_type(self) -> str:
        return "fake-tool-calling"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        msg = self.responses[self.i]
        self.i += 1
        return ChatResult(generations=[ChatGeneration(message=msg)])


def _calls(name, args, call_id="c1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


def _final(text):
    return AIMessage(content=text)


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


async def _call_agent(pgvector_url, monkeypatch, *, scripted, message="find me a quiet cafe"):
    from app.api.agent import get_agent_model

    test_engine = create_async_engine(pgvector_url)
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE cafes RESTART IDENTITY CASCADE"))
    async with TestSession() as s:
        s.add(_seed_cafe(google_place_id="A", name="Bricks", lat=34.0205, lng=-118.2855))
        s.add(_seed_cafe(google_place_id="B", name="Dinosaur", lat=34.03, lng=-118.27))
        await s.commit()

    async def override_session():
        async with TestSession() as s:
            yield s

    async def fake_extract(**kwargs):
        return ParsedQuery(
            semantic_query="quiet study spot", has_outlet=None, open_now=None, price_max=None
        )

    async def fake_embed(self, text: str):
        return [0.1] * 1536

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
async def test_agent_chat_returns_grounded_declared_recommendations(pgvector_url, monkeypatch):
    scripted = [
        _calls("search_shops", {"query": "quiet study spot"}),
        _calls("present_recommendations", {"cafe_ids": [1], "rationale": "Bricks is quiet."}, "c2"),
        _final("I recommend Bricks — a quiet study spot."),
    ]
    r = await _call_agent(pgvector_url, monkeypatch, scripted=scripted)

    assert r.status_code == 200
    body = r.json()
    assert "Bricks" in body["reply"]
    recs = body["recommendations"]
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
        _calls("search_shops", {"query": "quiet study spot"}),
        _final("There are a couple of nice quiet spots near campus."),
    ]
    r = await _call_agent(pgvector_url, monkeypatch, scripted=scripted)

    assert r.status_code == 200
    recs = r.json()["recommendations"]
    assert len(recs) >= 1  # fallback populated from the last search batch
    assert {c["name"] for c in recs} <= {"Bricks", "Dinosaur"}
    assert all(c["lat"] is not None and c["lng"] is not None for c in recs)


@pytest.mark.asyncio
async def test_agent_chat_drops_ungrounded_declared_ids(pgvector_url, monkeypatch):
    # The model declares id 999, which the tools never surfaced. A pin can only
    # exist for a cafe a tool genuinely returned (ADR-0001), so 999 is dropped.
    scripted = [
        _calls("search_shops", {"query": "quiet study spot"}),
        _calls(
            "present_recommendations",
            {"cafe_ids": [1, 999], "rationale": "picks"},
            "c2",
        ),
        _final("Here is my pick."),
    ]
    r = await _call_agent(pgvector_url, monkeypatch, scripted=scripted)

    assert r.status_code == 200
    ids = [c["id"] for c in r.json()["recommendations"]]
    assert ids == [1]  # 999 was never surfaced by a tool, so it is dropped
