# 02 — Agent tools over the search service

Status: ready-for-agent
Type: AFK

## What to build

Two LangChain tools that wrap existing capabilities — the agent re-implements
nothing, it calls the service from card 01.

- `search_shops` — runs the search service and returns a compact list of cafes
  (id, name, similarity, price, attributes, ambience, `lat`/`lng`, `open_now`).
- `get_shop_detail` — loads one full Cafe by id.

Each tool has a clear natural-language description and a typed args schema (the
description is what the model reads to decide when to call it). Tools are built
**per request**, closing over that request's database session — there is no
process-wide tool singleton, because data access is inherently request-scoped.

Note: a third "filter by hours" tool was deliberately cut for v1 — `search_shops`
already carries `open_now`, and an arbitrary-day/time tool introduced a
date-anchoring footgun. Do not add it.

See ADR/grill decisions Q3 (tool set) and Q7 (per-request session).

## Acceptance criteria

- [ ] `search_shops` and `get_shop_detail` exist as LangChain tools with descriptions + typed arg schemas.
- [ ] Tools are constructed per request and use the request's session (no module-level/global session, no contextvars).
- [ ] `search_shops` output includes `lat`/`lng` and `open_now` per cafe.
- [ ] No `filter_by_hours` tool is present.
- [ ] Unit tests exercise each tool against a seeded test DB and assert grounded ids/coordinates.

## Blocked by

- 01 — Search service + cafe coordinates
