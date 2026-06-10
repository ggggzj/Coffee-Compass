# 05 — Stream /agent/chat over SSE

Status: ready-for-agent
Type: AFK

## What to build

Convert `POST /agent/chat` from a plain JSON response into a Server-Sent Events
stream that surfaces the agent's reasoning as it happens. Emit `thought`,
`action`, and `observation` events as the ReAct loop runs (via LangChain
`astream_events` / callbacks), terminating in exactly one `final` event.

The `final` event reuses the server-side guarantee already built in card 03:
declared ids → else last `search_shops` results → else empty. The stream therefore
**always** ends with a `final` payload, even on a tool-less or partially-failed
turn — the map can never be left empty by a misbehaving LLM.

This card sits after card 04 because both edit the `/agent/chat` handler; keep the
changes serial to avoid a collision.

See grill decision Q8 (guaranteed final event).

## Acceptance criteria

- [ ] `/agent/chat` responds as an SSE stream of `thought`/`action`/`observation` events followed by exactly one `final`.
- [ ] Reasoning events arrive incrementally (verifiable with `curl -N`).
- [ ] The `final` payload is the same grounded structure as card 03, including the fallback — always emitted.
- [ ] Conversation memory (card 04) still works over the streamed handler.
- [ ] A test asserts the event ordering and that a `final` is always produced.

## Blocked by

- 04 — Multi-turn Conversation memory
