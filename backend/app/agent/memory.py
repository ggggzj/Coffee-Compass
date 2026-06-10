from __future__ import annotations

from typing import Protocol

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# A Turn is a user message plus the assistant's reply, so it is two messages.
MESSAGES_PER_TURN = 2


class Memory(Protocol):
    """Conversation memory keyed by session_id. Holds the recent Turns of one
    Conversation so follow-ups stay on topic."""

    def load(self, session_id: str) -> list[BaseMessage]: ...

    def append(self, session_id: str, role: str, content: str) -> None: ...


def _to_message(role: str, content: str) -> BaseMessage:
    if role == "user":
        return HumanMessage(content=content)
    if role == "assistant":
        return AIMessage(content=content)
    raise ValueError(f"unknown role: {role!r}")


class InProcessMemory:
    """In-process, per-session Conversation memory — the always-works fallback.

    Keyed by session_id; keeps the last ``max_turns`` Turns. Not durable across
    process restarts, which is fine for the v1 demo (see ADR-0002; Zep is the
    deferred User-scoped swap-in)."""

    def __init__(self, max_turns: int = 10) -> None:
        self._store: dict[str, list[BaseMessage]] = {}
        self._max_turns = max_turns

    def load(self, session_id: str) -> list[BaseMessage]:
        messages = self._store.get(session_id, [])
        return list(messages[-self._max_turns * MESSAGES_PER_TURN :])

    def append(self, session_id: str, role: str, content: str) -> None:
        self._store.setdefault(session_id, []).append(_to_message(role, content))

    def clear(self) -> None:
        self._store.clear()


_DEFAULT_MEMORY = InProcessMemory()


def get_memory() -> Memory:
    """FastAPI dependency returning the process-wide Conversation memory."""
    return _DEFAULT_MEMORY
