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
