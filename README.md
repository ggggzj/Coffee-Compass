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
