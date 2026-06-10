# CoffeeCompass

A RAG-powered coffee shop finder around USC / LA. Built as a 5-week solo project.

See `docs/superpowers/specs/2026-05-13-coffeecompass-design.md` for the full design.

## Quickstart (Week 1)

```bash
cd infra && docker compose up -d
cd ../backend && cp .env.example .env  # fill in API keys
uv sync --group dev --group eval
uv run alembic upgrade head
uv run python -m app.ingestion.pipeline
uv run uvicorn app.main:app --reload
```

Then `POST http://localhost:8000/search` with `{"query": "quiet place with outlets"}`.

## Week 2 — Review tagger v2, prompt versions, eval baseline

**Google Places (New)** returns at most **5 reviews per place** in Place Details; there is no supported way to pull dozens of reviews per cafe from the official API alone.

1. Apply migrations (adds `prompt_versions`, `editorial_summary`, `review_snippets` on `cafes`):

   ```bash
   cd backend && uv sync --group dev --group eval && uv run alembic upgrade head
   ```

2. Optional: register the `review_tagger` v2 prompt in the DB + JSON mirror (first time only, if empty):

   ```bash
   uv run python -m app.eval.seed_prompts
   ```

3. Set **`REVIEW_TAGGER_IMPL=v2`** in `backend/.env` and re-tag existing rows (uses `data/places_raw/*.json` when present, else DB `review_snippets`):

   ```bash
   uv run python -m app.ingestion.pipeline --retag-only
   ```

4. Edit `backend/app/eval/golden_set.json` so `expected_cafe_ids` match **your** `cafes.id` values (30 queries). The committed `golden_set.json` (version 2) is already labelled against the 52 cafes ingested for this build; relabel if you re-ingest.

5. Run the Week 2 baseline (calls OpenAI; requires real DB + keys):

   ```bash
   uv run python -m app.eval.baseline --output ../docs/eval-results/2026-06-01-v1.json
   ```

   A real baseline run ships at `docs/eval-results/2026-06-01-v1.json`
   (context_precision 0.17, faithfulness 0.63, answer_relevancy 0.36 across 30
   queries, golden set v2). These are the **starting** numbers; Week 4 iterates to
   improve `context_precision`. Re-run the command to reproduce after repopulating the DB.

## Week 3 — Conversational agent + web UI

Week 3 turns the search backend into a demo-able product: a multi-turn
**LangChain agent** at `POST /agent/chat` that wraps the Week 1 retriever as
tools and streams its reasoning, plus a **Next.js + Mapbox** frontend with a
streaming chat panel and a map that pins the recommended cafes.

### Run the full stack

```bash
# 1. Database (Postgres + pgvector)
cd infra && docker compose up -d

# 2. Backend (terminal A) — uv installs the agent group by default now
cd backend && uv sync && uv run alembic upgrade head
uv run uvicorn app.main:app --reload          # http://localhost:8000

# 3. Frontend (terminal B)
cd frontend
cp .env.local.example .env.local              # then paste your Mapbox token
npm install
npm run dev                                   # http://localhost:3000
```

### Environment

- **Backend** (`backend/.env`): `AGENT_MODEL` (default `gpt-4o-mini`) plus the
  existing `OPENAI_API_KEY` / `DATABASE_URL`. Multi-turn memory is **in-process**
  by default; Zep is intentionally deferred (see ADR-0002), so no extra service
  is required for the demo.
- **Frontend** (`frontend/.env.local`, gitignored): `NEXT_PUBLIC_API_BASE` and
  `NEXT_PUBLIC_MAPBOX_TOKEN`. Use the Mapbox **public** token (`pk.…`) — it is
  safe to ship to the browser; restrict it by domain in the Mapbox dashboard.

### Demo flow

Open `http://localhost:3000` and run the three-turn conversation — the map pins
update to match each answer:

1. *"a quiet place to study with outlets near USC"*
2. *"anything cheaper?"* — stays on the same need, just adds the price constraint
3. *"open now?"*

### How it works

- **Grounded recommendations.** The agent's final act is to declare the cafe ids
  it recommends; the backend hydrates those into the `final` event from the cafes
  the tools actually returned — pins are never parsed from prose, so a pin can
  only exist for a cafe that was really retrieved (see `docs/adr/0001`).
- **Streaming.** `POST /agent/chat` is Server-Sent Events: `thought` / `action` /
  `observation` steps followed by exactly one guaranteed `final`. Verify raw with
  `curl -N`:

  ```bash
  curl -N -X POST http://localhost:8000/agent/chat \
    -H 'Content-Type: application/json' \
    -d '{"session_id":"demo","user_id":"demo-user","message":"quiet study spot with outlets"}'
  ```

- **One search per turn.** A system-prompt rule plus a hard per-turn search cap
  stop the agent from re-running the same search reworded with synonyms.
- **Detail pages.** `GET /cafes/{id}` backs `/cafe/[id]`; chat chips and map pins
  link to it. The route and the agent's `get_shop_detail` tool share one
  cafe-by-id load path.

Domain vocabulary lives in `CONTEXT.md`; architectural decisions in `docs/adr/`.

### Measured numbers

Honest, reproducible figures for this build (52-cafe DB):

- **Dataset:** 52 curated USC-area cafes, all embedded.
- **Slot-tagging A/B** (`uv run python -m app.eval.tag_error`): **~92% fewer
  hard-filter errors** vs a naive single-prompt extractor (39 → 3 over 24
  queries / 72 slots).
- **Latency** (`k6 run backend/loadtest/search.js`): pgvector retrieval-stage
  **p95 ≈ 73ms**; cached request **p95 ≈ 25ms** vs ~1.4s uncached (the
  in-process slot cache skips the OpenAI calls on repeated queries).

## Week 1 verification (Postman or curl)

After running ingestion against real APIs (or the smoke seeder for a quick check):

```bash
curl -s -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "quiet place with outlets near USC", "top_k": 5}' | jq .
```

You should see 5 results, all with `has_outlet=true`, ordered by `similarity`.

Try variations:

- `{"query": "cheap latte open now"}` → results filtered by `price_max <= 2` and `open_now`
- `{"query": "first date spot"}` → no SQL filters, pure vector ranking on vibe

### Smoke script (no Google ingestion)

From `backend/` with Postgres up, migrations applied, and API on port 8000:

```bash
uv run python -m scripts.smoke_search
```

Requires `OPENAI_API_KEY` in `.env`.

## Ingestion limits (Google Places API New)

`searchNearby` returns at most **20 places per HTTP request** and does not support `pageToken` pagination. The client runs **several overlapping circle searches** (anchor + 8 offsets) and **deduplicates** by `google_place_id` so `uv run python -m app.ingestion.pipeline --limit 100` can collect more than 20 rows when the area has enough cafes (still capped by what Google returns).

## Remove local smoke-test rows (optional)

If you ran `scripts.smoke_search` and no longer want `(smoke)` cafes in `/search` results:

```bash
docker exec coffeecompass-postgres psql -U coffee -d coffeecompass \
  -c "DELETE FROM cafes WHERE google_place_id LIKE 'smoke-%';"
```
