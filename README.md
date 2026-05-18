# CoffeeCompass

A RAG-powered coffee shop finder around USC / LA. Built as a 5-week solo project.

See `docs/superpowers/specs/2026-05-13-coffeecompass-design.md` for the full design.

## Quickstart (Week 1)

```bash
cd infra && docker compose up -d
cd ../backend && cp .env.example .env  # fill in API keys
uv sync
uv run alembic upgrade head
uv run python -m app.ingestion.pipeline
uv run uvicorn app.main:app --reload
```

Then `POST http://localhost:8000/search` with `{"query": "quiet place with outlets"}`.

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
