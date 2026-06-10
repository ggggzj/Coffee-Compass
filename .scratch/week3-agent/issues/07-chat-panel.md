# 07 — Chat panel (streaming UI)

Status: ready-for-agent
Type: AFK

## What to build

The chat UI: a message list + input box that, on submit, opens an `EventSource` to
`/agent/chat` and renders the stream. The agent's `thought`/`action`/`observation`
steps render as **collapsible** sub-blocks; the `final` event renders as the main
answer bubble.

Identity per grill decision Q5: a stable per-tab `session_id` (e.g. a UUID
generated once per tab) so a Conversation stays coherent, and a fixed
`user_id="demo-user"` for now.

See glossary terms Conversation, Turn; identity decision in ADR-0002.

## Acceptance criteria

- [ ] Submitting a message opens an SSE connection to `/agent/chat` and streams the response.
- [ ] Reasoning steps appear as collapsible blocks; the `final` answer is the main bubble.
- [ ] A stable `session_id` persists for the tab across multiple messages (follow-ups stay in one Conversation); `user_id` is `demo-user`.
- [ ] `pnpm build` and `pnpm lint` are clean.

## Blocked by

- 05 — Stream /agent/chat over SSE
- 06 — Frontend scaffold + CORS + Mapbox token
