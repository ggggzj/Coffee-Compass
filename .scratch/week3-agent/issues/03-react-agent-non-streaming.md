# 03 — ReAct agent + non-streaming /agent/chat

Status: ready-for-agent
Type: AFK

## What to build

A LangChain ReAct (tool-calling) agent wired to the two tools from card 02, with a
concise CoffeeCompass system prompt and `temperature=0`. Expose it at
`POST /agent/chat` accepting `{session_id, user_id, message}` and returning a
**plain JSON** response (no streaming yet) so correctness is verifiable before SSE.

The response carries grounded Recommendations, not prose-parsed names. The agent's
final act is to **declare its chosen cafe ids** (via a `present_recommendations`
step); the backend hydrates those ids into structured rows (id, name, `lat`/`lng`)
from the cafes the tools actually returned this turn. Prose rides alongside as
`rationale`. Pins/recommendations are grounded in tool data.

Because an LLM may answer in prose and forget to declare ids, the structured
`final` payload is **guaranteed server-side**: declared ids when present, else a
fallback to the last `search_shops` results, else empty. (This guarantee logic
lands here and is reused unchanged when streaming is added in card 05.)

See ADR-0001 (grounded recommendations) and the `Recommendation` glossary term.

## Acceptance criteria

- [ ] `POST /agent/chat` accepts `{session_id, user_id, message}` and returns grounded Recommendations as JSON.
- [ ] Every recommended cafe id exists in `cafes` and carries `lat`/`lng`; the answer is built from tool data, not name-matched from prose.
- [ ] When the agent declares ids via `present_recommendations`, those are the Recommendations.
- [ ] When it does not, the response falls back to the last `search_shops` results (or empty) — the payload is never missing.
- [ ] Agent + tools are constructed per request (per card 02).
- [ ] An integration test asserts a single message yields grounded ids; the fallback path is covered.

## Blocked by

- 02 — Agent tools over the search service
