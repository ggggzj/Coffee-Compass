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
    """Scripted chat model that also captures the messages of its first call."""

    responses: list
    i: int = 0
    captured: list | None = None

    @property
    def _llm_type(self) -> str:
        return "fake-tool-calling"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        if self.captured is None:
            self.captured = list(messages)
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


async def _fake_extract(**kwargs):
    return ParsedQuery(
        semantic_query="quiet study spot", has_outlet=None, open_now=None, price_max=None
    )


async def _fake_embed(self, text: str):
    return [0.1] * 1536


@pytest.mark.asyncio
async def test_prior_turn_is_replayed_and_persisted(pgvector_url, monkeypatch):
    from app.agent.memory import InProcessMemory, get_memory
    from app.api.agent import get_agent_model

    test_engine = create_async_engine(pgvector_url)
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE cafes RESTART IDENTITY CASCADE"))
    async with TestSession() as s:
        s.add(_seed_cafe(google_place_id="A", name="Bricks"))
        await s.commit()

    async def override_session():
        async with TestSession() as s:
            yield s

    monkeypatch.setattr("app.search.service.extract_slots", _fake_extract)
    monkeypatch.setattr("app.search.embedder.Embedder.embed", _fake_embed)

    memory = InProcessMemory()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_memory] = lambda: memory

    # --- Turn 1 ---
    fake1 = FakeToolCallingModel(
        responses=[
            _calls("search_shops", {"query": "quiet study spot"}),
            _calls("present_recommendations", {"cafe_ids": [1], "rationale": "x"}, "c2"),
            _final("Bricks is a great quiet spot."),
        ]
    )
    app.dependency_overrides[get_agent_model] = lambda: fake1
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r1 = await client.post(
            "/agent/chat",
            json={"session_id": "s1", "user_id": "demo-user", "message": "quiet study spot"},
        )
    assert r1.status_code == 200

    # The Turn was persisted (append-after-respond): user message + assistant reply.
    hist = memory.load("s1")
    assert [m.content for m in hist] == ["quiet study spot", "Bricks is a great quiet spot."]

    # --- Turn 2 (same session) ---
    fake2 = FakeToolCallingModel(responses=[_final("Sure, here are cheaper ones.")])
    app.dependency_overrides[get_agent_model] = lambda: fake2
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r2 = await client.post(
            "/agent/chat",
            json={"session_id": "s1", "user_id": "demo-user", "message": "anything cheaper?"},
        )
    assert r2.status_code == 200

    # The agent for Turn 2 received the prior Turn in its input message history.
    contents = [getattr(m, "content", "") for m in (fake2.captured or [])]
    assert "quiet study spot" in contents
    assert "Bricks is a great quiet spot." in contents
    assert "anything cheaper?" in contents

    app.dependency_overrides.clear()
    await test_engine.dispose()


class RaisingModel(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "raising"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        raise RuntimeError("model boom")


@pytest.mark.asyncio
async def test_failed_turn_does_not_poison_memory(pgvector_url, monkeypatch):
    from app.agent.memory import InProcessMemory, get_memory
    from app.api.agent import get_agent_model

    test_engine = create_async_engine(pgvector_url)
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE cafes RESTART IDENTITY CASCADE"))

    async def override_session():
        async with TestSession() as s:
            yield s

    memory = InProcessMemory()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_memory] = lambda: memory
    app.dependency_overrides[get_agent_model] = lambda: RaisingModel()

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/agent/chat",
            json={"session_id": "s1", "user_id": "demo-user", "message": "this will fail"},
        )

    app.dependency_overrides.clear()
    await test_engine.dispose()

    assert r.status_code == 500
    # The Turn never completed, so nothing was appended — no half-Turn poisoning.
    assert memory.load("s1") == []
