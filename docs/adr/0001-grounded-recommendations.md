# Recommendations are grounded in tool data, not parsed from prose

The map must pin exactly the cafes the agent recommends, and clicking a pin must
highlight its matching chat bubble — so each Recommendation needs a structured
`{id, name, lat, lng}`, not just a name buried in the LLM's prose answer. We
decided the agent's final act is to **declare its chosen cafe ids** (via a
`present_recommendations` tool), and the backend **hydrates those ids into the
`final` payload from the cafes the tools actually returned this turn**. The prose
rides alongside as cosmetic `rationale`; correctness lives in the structured rows.
A pin can therefore only appear for a cafe a tool genuinely surfaced, which
structurally eliminates the "pin says X, bubble says Y" class of bug.

## Considered options

- **Parse the prose** (regex / LLM name-extraction back to ids) — rejected: brittle,
  and the failure mode is a pin that matches no bubble.
- **Two-pass** (prose, then a second LLM call to structure it) — rejected: doubles
  LLM latency on the streaming critical path.

## Consequences

Because the `final` event's producer is an LLM choosing to call a tool — and LLMs
sometimes answer in prose and stop — the `final` event is **guaranteed
server-side**: declared ids when `present_recommendations` fires (the happy path),
otherwise a fallback to the last `search_shops` results, otherwise `[]`. The
invariant is: *a turn that ran `search_shops` always yields pinnable cafes.* See
also the [[recommendation]] term in `CONTEXT.md` (the declared subset, distinct
from cafes merely considered).
