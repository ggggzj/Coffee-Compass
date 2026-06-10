# 09 — Cafe detail page

Status: ready-for-agent
Type: AFK

## What to build

A per-Cafe detail view. Add a small REST route `GET /cafes/{id}` that returns the
full Cafe (name, address, rating, attributes/tags, ambience text, hours, `lat`/
`lng`), and a frontend `/cafe/[id]` page that renders it as a detail card. Link
map pins and chat results through to it.

The backend route reuses the Cafe-loading logic already wrapped by the
`get_shop_detail` tool — one way to load a Cafe by id, shared by the tool and the
REST route.

See the `Cafe` glossary term.

## Acceptance criteria

- [ ] `GET /cafes/{id}` returns the full Cafe (including `lat`/`lng`, hours, ambience) or 404 for an unknown id.
- [ ] `/cafe/[id]` renders a detail card from that route.
- [ ] Pins and chat results link to the detail page.
- [ ] Backend route and the `get_shop_detail` tool share one Cafe-by-id load path.
- [ ] A test covers the route (hit + 404); `pnpm build` clean.

## Blocked by

- 01 — Search service + cafe coordinates
- 06 — Frontend scaffold + CORS + Mapbox token
