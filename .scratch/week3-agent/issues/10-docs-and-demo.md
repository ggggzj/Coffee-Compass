# 10 — Docs + demo script

Status: ready-for-human
Type: HITL

## What to build

Document how to run the full stack and capture the demo that is the Week 3 success
criterion. HITL because recording the demo is a human act.

- README "Week 3 — Agent + Frontend" section: run the DB, backend (`uvicorn`), and
  frontend (`pnpm dev`) together; required env vars; the demo flow.
- Note the Zep-optional fallback (in-process memory works without it) and that the
  Mapbox token is a **public** token (restrict by domain in the Mapbox dashboard).
- Record the demo: the three-turn Conversation ("quiet study spot" → "anything
  cheaper?" → "open now?") with recommendations appearing as map pins.

## Acceptance criteria

- [ ] README documents running DB + backend + frontend together, with env vars.
- [ ] README notes the in-process memory fallback and the public-Mapbox-token posture.
- [ ] The three-turn demo (chat + matching map pins) is recorded.
- [ ] `uv run pytest` green and `pnpm build` green at the time of recording.

## Blocked by

- 07 — Chat panel (streaming UI)
- 08 — Map panel (Mapbox pins)
- 09 — Cafe detail page
