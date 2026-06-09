# Two identities; `user_id` plumbed but dormant in v1

CoffeeCompass distinguishes a **Conversation** (one chat thread, keyed by
`session_id`, scoped to a browser tab) from a **User** (the person, keyed by
`user_id`, persisting across Conversations). v1 ships **in-process Conversation
memory only** — keyed by `session_id` — which fully satisfies the locked 3-turn
demo. The User-scoped Preference Summary (Zep) is deferred behind the `Memory`
protocol. We nonetheless **thread `user_id` through the `/agent/chat` API and the
frontend from day one**, even though nothing reads it yet.

## Why record this

`user_id` will look like dead code — a parameter that is accepted, passed around,
and never used. It is deliberate: keeping the seam means adding Zep / the
Preference Summary later is a swap-in behind the `Memory` protocol that touches
**neither the API contract nor the frontend**. Collapsing to a single id for v1
would be less plumbing now but would force a breaking change to the request shape
and the client when long-term memory lands. Do not "clean up" the unused
`user_id`. See the [[user]] and [[conversation]] terms in `CONTEXT.md`.
