# 06 — Frontend scaffold + CORS + Mapbox token

Status: ready-for-human
Type: HITL

## What to build

Stand up the frontend workspace and the cross-origin + secrets plumbing the UI
cards depend on. HITL because it needs human-only steps: a Mapbox account + public
token, and a local Node/pnpm toolchain with an interactive `create-next-app`.

- Scaffold a Next.js (App Router, TypeScript, pnpm) app in `frontend/`, with
  `mapbox-gl` / `react-map-gl` added.
- Add CORS to the backend allowing the frontend origin (`http://localhost:3000`).
- Create `frontend/.env.local` (gitignored) + a committed `.env.local.example`
  with the API base and the **public** Mapbox token (`pk.…`).

## Acceptance criteria

- [ ] `frontend/` is a runnable Next.js + TypeScript app managed with pnpm; `pnpm build` succeeds.
- [ ] Backend allows requests from `http://localhost:3000` (CORS).
- [ ] A public Mapbox token is available to the frontend via env; `.env.local.example` documents the required vars.
- [ ] The Mapbox token is the public `pk.` token only (safe for the browser); no secret token is shipped to the client.

## Blocked by

None — can start immediately (runs in parallel with the backend spine).
