import pytest
from httpx import ASGITransport, AsyncClient
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import get_session
from app.main import app
from tests.integration.agent_helpers import (
    FakeToolCallingModel,
    calls,
    fake_embed,
    fake_extract,
    final,
    seed_cafe,
)


@pytest.mark.asyncio
async def test_prior_turn_is_replayed_and_persisted(pgvector_url, monkeypatch):
    from app.agent.memory import InProcessMemory, get_memory
    from app.api.agent import get_agent_model

    test_engine = create_async_engine(pgvector_url)
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE cafes RESTART IDENTITY CASCADE"))
    async with TestSession() as s:
        s.add(seed_cafe(google_place_id="A", name="Bricks"))
        await s.commit()

    async def override_session():
        async with TestSession() as s:
            yield s

    monkeypatch.setattr("app.search.service.extract_slots", fake_extract)
    monkeypatch.setattr("app.search.embedder.Embedder.embed", fake_embed)

    memory = InProcessMemory()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_memory] = lambda: memory

    # --- Turn 1 ---
    fake1 = FakeToolCallingModel(
        responses=[
            calls("search_shops", {"query": "quiet study spot"}),
            calls("present_recommendations", {"cafe_ids": [1], "rationale": "x"}, "c2"),
            final("Bricks is a great quiet spot."),
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
    fake2 = FakeToolCallingModel(responses=[final("Sure, here are cheaper ones.")])
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

    # The model raises before any event is produced, so the stream errors out
    # before the final event. Tolerate however the aborted stream surfaces.
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                "/agent/chat",
                json={"session_id": "s1", "user_id": "demo-user", "message": "this will fail"},
            )
    except Exception:
        pass
    finally:
        app.dependency_overrides.clear()
        await test_engine.dispose()

    # The Turn never completed, so nothing was appended — no half-Turn poisoning.
    assert memory.load("s1") == []
