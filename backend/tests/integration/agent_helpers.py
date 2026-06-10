"""Shared test helpers for the agent endpoint tests (chat, memory, streaming).

Not a test module (no test_ prefix), so pytest does not collect it.
"""

from __future__ import annotations

import json

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.models import Cafe
from app.search.slot_extractor import ParsedQuery


class FakeToolCallingModel(BaseChatModel):
    """Scripted chat model: replays a list of AIMessages, one per call, and
    captures the messages of its first call (to assert what history it saw)."""

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


def calls(name, args, call_id="c1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


def final(text):
    return AIMessage(content=text)


def seed_cafe(**overrides):
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


async def fake_extract(**kwargs):
    return ParsedQuery(
        semantic_query="quiet study spot", has_outlet=None, open_now=None, price_max=None
    )


async def fake_embed(self, text: str):
    return [0.1] * 1536


def parse_sse(text: str) -> list[dict]:
    """Parse an SSE response body into a list of {"event", "data"} dicts, with
    data JSON-decoded."""
    events: list[dict] = []
    cur: dict = {}
    for line in text.splitlines():
        if line.startswith("event:"):
            cur["event"] = line[len("event:") :].strip()
        elif line.startswith("data:"):
            cur["data"] = json.loads(line[len("data:") :].strip())
        elif line == "":
            if cur:
                events.append(cur)
                cur = {}
    if cur:
        events.append(cur)
    return events


def events_of(events: list[dict], event_type: str) -> list[dict]:
    return [e for e in events if e.get("event") == event_type]
