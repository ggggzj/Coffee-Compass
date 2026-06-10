# 11 — Zep / Preference Summary

Status: ready-for-human
Type: HITL

> **Update:** Triaged "feature now, Zep as adapter." The cross-Conversation
> Preference Summary now ships **in-process** (keyed by `user_id`, prepended to
> the agent's system prompt, tested end-to-end). The Memory protocol carries
> `user_id`; the API contract and frontend were untouched (ADR-0002). What
> remains (HITL): wire the `ZepMemory` adapter stub against the real Zep SDK once
> a Zep account + key exist — `AGENT_MEMORY_IMPL=zep` already selects it and falls
> back to in-process until then.

## What to build

> Original scope below — deferred Zep portion only remains.

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
