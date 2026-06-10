# 01 — Search service + cafe coordinates

Status: ready-for-agent
Type: AFK

## What to build

Extract the search pipeline (slot extraction → embedding → retrieval) out of the
`/search` HTTP handler into a single reusable service function, so both the REST
endpoint and (later) the agent tools call one code path and can never drift. The
slot/embedding cache moves into the service module and is shared across all
callers. The endpoint keeps only HTTP concerns (request parsing, latency headers,
response shaping).

Also project a Cafe's coordinates (`lat`/`lng`) through the retrieval result.
Today the result shape carries name, attributes, similarity, and ambience text but
**not** coordinates — even though the Cafe has them — which blocks the map-first
product downstream. Coordinates are intrinsic to a Cafe for this product, so they
belong on the canonical result shape, not fetched separately.

See ADR-0001 background and the `Cafe` glossary term in `CONTEXT.md`.

## Acceptance criteria

- [ ] A single service function performs slot-extract → embed → retrieve and is the only place that logic lives.
- [ ] The slot/embedding cache lives in the service module; a repeated query is a cache hit regardless of which caller invoked it.
- [ ] `/search` is rewired onto the service and its existing behavior (filters, `open_now`, latency headers, `X-Cache`) is unchanged.
- [ ] The retrieval result carries `lat` and `lng` for every Cafe; `/search` responses include them.
- [ ] Existing search/integration tests stay green; a test asserts coordinates are present and correct for a seeded Cafe.

## Blocked by

None — can start immediately.
