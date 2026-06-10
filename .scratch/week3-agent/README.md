# Week 3 — Agent + Multi-turn UI

Tickets sliced from the resolved Week 3 design (see
`docs/superpowers/plans/2026-06-03-week3-plan.md`, `CONTEXT.md`, and
`docs/adr/0001`–`0002`). Vertical tracer-bullet slices; each is verifiable on its
own.

## Cards

| # | Title | Type | Blocked by |
|---|-------|------|-----------|
| [01](issues/01-search-service-and-coordinates.md) | Search service + cafe coordinates | AFK | — |
| [02](issues/02-agent-tools.md) | Agent tools over the search service | AFK | 01 |
| [03](issues/03-react-agent-non-streaming.md) | ReAct agent + non-streaming /agent/chat | AFK | 02 |
| [04](issues/04-conversation-memory.md) | Multi-turn Conversation memory | AFK | 03 |
| [05](issues/05-sse-streaming.md) | Stream /agent/chat over SSE | AFK | 04 |
| [06](issues/06-frontend-scaffold-cors-mapbox.md) | Frontend scaffold + CORS + Mapbox token | HITL | — |
| [07](issues/07-chat-panel.md) | Chat panel (streaming UI) | AFK | 05, 06 |
| [08](issues/08-map-panel.md) | Map panel (Mapbox pins) | AFK | 07 |
| [09](issues/09-cafe-detail-page.md) | Cafe detail page | AFK | 01, 06 |
| [10](issues/10-docs-and-demo.md) | Docs + demo script | HITL | 07, 08, 09 |
| [11](issues/11-zep-preference-summary.md) | Zep / Preference Summary | deferred (needs-triage) | 04 |

## Dependency spine

```
01 → 02 → 03 → 04 → 05 ┐
                        ├→ 07 → 08 ┐
06 ─────────────────────┘          ├→ 10
01, 06 → 09 ───────────────────────┘
04 → 11 (deferred)
```

Backend spine `01→05` runs while `06` (HITL scaffold) proceeds in parallel.
`07`/`08`/`09` are the frontend; `10` closes the week. `11` is parked behind triage.
