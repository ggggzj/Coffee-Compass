# 08 — Map panel (Mapbox pins)

Status: ready-for-agent
Type: AFK

## What to build

A map panel that pins the Recommendations from each `final` event. Render a map
centered on USC main campus as the default "near me" reference, and when a `final`
event arrives, drop one pin per recommended Cafe using its `lat`/`lng`. Clicking a
pin highlights the matching chat bubble, and vice-versa.

Only **Recommendations** (the ids the agent declared / the final payload) are
pinned — not every cafe the tools considered. Pins come straight from the grounded
`final` payload, so a pin can never reference a cafe the bubble doesn't.

Keep the provider behind a small `MapAdapter` boundary so Mapbox can be swapped
later without touching the chat/recommendation flow.

See ADR-0001 (grounded recommendations) and the `Recommendation` glossary term.

## Acceptance criteria

- [ ] The map renders centered on USC using the public Mapbox token.
- [ ] Each `final` event drops one pin per Recommendation from its `lat`/`lng`.
- [ ] Only declared Recommendations are pinned (not all considered cafes).
- [ ] Clicking a pin highlights its chat bubble and vice-versa.
- [ ] Mapbox access is isolated behind a `MapAdapter` boundary.
- [ ] `pnpm build` / `pnpm lint` clean.

## Blocked by

- 07 — Chat panel (streaming UI)
