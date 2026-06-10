# 04 — Multi-turn Conversation memory

Status: ready-for-agent
Type: AFK

## What to build

In-process Conversation memory so follow-ups stay on topic. A `Memory` protocol
(`load`/`append`) with an `InProcessMemory` implementation keyed by `session_id`
(a `dict[session_id, list[message]]`). On each request, the prior Turns of the
Conversation are replayed **raw** into the agent's message history (not the
scratchpad — the scratchpad is the current turn's tool trace), capped at the last
~10 Turns. The new Turn is appended **only after** the agent responds, so a
mid-turn failure never poisons the Conversation with a half-Turn.

`user_id` is accepted and threaded through but **dormant** in v1 — nothing reads
it yet. Keep the seam; do not remove the unused parameter (see ADR-0002).

Zep / the User-scoped Preference Summary is out of scope here (see card 11).

See glossary terms Conversation, Turn, User, Preference Summary, and ADR-0002.

## Acceptance criteria

- [ ] A `Memory` protocol exists with an `InProcessMemory` keyed by `session_id`.
- [ ] Prior Turns are replayed into the agent's message history (not the scratchpad), capped at the last ~10 Turns.
- [ ] The new Turn is appended only after a successful response.
- [ ] `user_id` is plumbed through `/agent/chat` but unused (dormant seam intact).
- [ ] A test of the demo flow ("quiet study spot" → "anything cheaper?" → "open now?") shows follow-ups stay on the same cafes within one `session_id`, and are isolated across different `session_id`s.

## Blocked by

- 03 — ReAct agent + non-streaming /agent/chat
