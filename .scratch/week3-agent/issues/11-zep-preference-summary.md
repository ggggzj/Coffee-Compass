# 11 — Zep / Preference Summary (deferred)

Status: needs-triage
Type: HITL

## What to build

> Deliberately deferred from the Week 3 v1 scope (see ADR-0002). Captured here so
> it is not lost. **Not ready for an AFK agent** — needs triage / a Zep account
> decision first.

A `ZepMemory` implementation behind the existing `Memory` protocol that gives a
**User** (keyed by `user_id`) a cross-Conversation **Preference Summary** — a
long-lived distillation of what they tend to want (e.g. "usually wants cheap,
quiet, near USC"), prepended to the system prompt. Selected when configured
(`AGENT_MEMORY_IMPL=zep` + a Zep API key); in-process Conversation memory remains
the always-works fallback.

Because the `user_id` seam is already plumbed (card 04 / ADR-0002), landing this
should touch neither the API contract nor the frontend.

See glossary terms User, Preference Summary, Conversation; ADR-0002.

## Acceptance criteria

- [ ] Decide whether to adopt Zep Cloud (account / free-tier) or an alternative store — triage first.
- [ ] `ZepMemory` implements the `Memory` protocol; selected by config, with in-process memory as fallback.
- [ ] A User's Preference Summary persists across Conversations and influences recommendations.
- [ ] No change to the `/agent/chat` API contract or the frontend.

## Blocked by

- 04 — Multi-turn Conversation memory (the `Memory` protocol + dormant `user_id` seam)
