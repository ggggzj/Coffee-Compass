from __future__ import annotations

from typing import Protocol

import structlog
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.config import get_settings

log = structlog.get_logger()

# A Turn is a user message plus the assistant's reply, so it is two messages.
MESSAGES_PER_TURN = 2


class Memory(Protocol):
    """Conversation memory plus a cross-Conversation Preference Summary.

    Keyed two ways: ``session_id`` scopes one Conversation's recent Turns, while
    ``user_id`` scopes a User's standing preferences across all their
    Conversations (see CONTEXT.md: Conversation vs User)."""

    def load(self, *, session_id: str, user_id: str) -> list[BaseMessage]: ...

    def append(self, *, session_id: str, user_id: str, role: str, content: str) -> None: ...

    def preference_preamble(self, *, user_id: str) -> str | None:
        """A system-prompt preamble describing what this User tends to want, drawn
        from earlier Conversations. None when the User is new."""
        ...


def _to_message(role: str, content: str) -> BaseMessage:
    if role == "user":
        return HumanMessage(content=content)
    if role == "assistant":
        return AIMessage(content=content)
    raise ValueError(f"unknown role: {role!r}")


class InProcessMemory:
    """In-process memory — the always-works default.

    Holds two stores: recent Turns per ``session_id`` (the Conversation), and the
    most recent requests per ``user_id`` (a heuristic Preference Summary that
    persists across Conversations). Not durable across restarts, which is fine for
    the v1 demo. Zep is the deferred, LLM-distilled swap-in (see ADR-0002)."""

    def __init__(self, max_turns: int = 10, max_profile: int = 5) -> None:
        self._store: dict[str, list[BaseMessage]] = {}
        self._profiles: dict[str, list[str]] = {}
        self._max_turns = max_turns
        self._max_profile = max_profile

    def load(self, *, session_id: str, user_id: str) -> list[BaseMessage]:
        messages = self._store.get(session_id, [])
        return list(messages[-self._max_turns * MESSAGES_PER_TURN :])

    def append(self, *, session_id: str, user_id: str, role: str, content: str) -> None:
        self._store.setdefault(session_id, []).append(_to_message(role, content))
        # A User's stated requests (their messages) accumulate into the profile,
        # keyed by user_id — so they carry across Conversations.
        if role == "user":
            self._profiles.setdefault(user_id, []).append(content)

    def preference_preamble(self, *, user_id: str) -> str | None:
        past = self._profiles.get(user_id, [])
        if not past:
            return None
        recent = past[-self._max_profile :]
        joined = "; ".join(f'"{p}"' for p in recent)
        return (
            f"This returning user has previously asked for: {joined}. Take these "
            "standing preferences into account when they are relevant to the "
            "current request, but always defer to what they ask for now."
        )

    def clear(self) -> None:
        self._store.clear()
        self._profiles.clear()


class ZepMemory:
    """Adapter stub: cross-Conversation Preference Summary backed by Zep Cloud.

    Intended mapping (wire up when a Zep account + key are available):
      - ``user_id``  -> a Zep user; Zep distills an LLM Preference Summary from
        that user's history across every session.
      - ``session_id`` -> a Zep session/thread holding the Conversation's Turns.
      - ``preference_preamble(user_id)`` -> Zep's user-level memory summary.

    Requires the ``zep-cloud`` package (intentionally not a dependency yet, per
    ADR-0002) and ``ZEP_API_KEY``. Until implemented, ``get_memory`` falls back to
    InProcessMemory, so selecting it never breaks the app."""

    def __init__(self, api_key: str) -> None:
        raise NotImplementedError(
            "ZepMemory is an adapter stub. Add the zep-cloud dependency, implement "
            "load/append/preference_preamble against the Zep SDK, and remove this "
            "guard. Until then AGENT_MEMORY_IMPL=zep falls back to in-process."
        )


_DEFAULT_MEMORY = InProcessMemory()


def get_memory() -> Memory:
    """FastAPI dependency selecting the memory implementation from config.

    Defaults to the in-process implementation. If ``AGENT_MEMORY_IMPL=zep`` and a
    key is set, it tries ZepMemory and falls back to in-process if Zep is not yet
    available — so the app works regardless."""
    settings = get_settings()
    if settings.agent_memory_impl == "zep" and settings.zep_api_key:
        try:
            return ZepMemory(settings.zep_api_key)
        except Exception:
            log.warning("zep_memory_unavailable_falling_back_to_in_process")
    return _DEFAULT_MEMORY
