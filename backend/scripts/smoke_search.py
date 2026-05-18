"""Local smoke test: seeds 3 cafes with REAL embeddings, queries /search.

Cost: ~$0.0001 (3 embedding calls + 1 slot extractor + 1 query embedding).
Usage:
  1) docker compose up -d   (from infra/ or compose project root)
  2) uv run alembic upgrade head
  3) uv run uvicorn app.main:app --port 8000 &
  4) uv run python -m scripts.smoke_search
"""

from __future__ import annotations

import asyncio

import httpx
from openai import AsyncOpenAI
from sqlalchemy import delete

from app.config import get_settings
from app.db import SessionLocal
from app.models import Cafe
from app.search.embedder import Embedder

SEED_TEXTS = [
    dict(
        google_place_id="smoke-A",
        name="Quiet Bean (smoke)",
        address="123 Quiet St",
        lat=34.02,
        lng=-118.28,
        rating=4.7,
        review_count=300,
        price_level=2,
        categories=["cafe"],
        opening_hours={"periods": []},
        has_wifi=True,
        has_outlet=True,
        noise_level="quiet",
        good_for_studying=True,
        ambience_text=(
            "A serene specialty cafe near USC favored by graduate students. "
            "Plentiful outlets, fast wifi, soft acoustic music, and large communal "
            "tables make it ideal for focused reading and laptop work."
        ),
    ),
    dict(
        google_place_id="smoke-B",
        name="Loud Latte (smoke)",
        address="456 Loud Ave",
        lat=34.03,
        lng=-118.29,
        rating=4.2,
        review_count=120,
        price_level=2,
        categories=["cafe"],
        opening_hours={"periods": []},
        has_wifi=True,
        has_outlet=False,
        noise_level="lively",
        good_for_studying=False,
        ambience_text=(
            "A buzzy social cafe popular for weekend brunch and friend meetups. "
            "Music is loud, seating is tight, and there are no laptop-friendly outlets. "
            "Great vibes for hanging out, poor for focused work."
        ),
    ),
    dict(
        google_place_id="smoke-C",
        name="Power Pourover (smoke)",
        address="789 Power Rd",
        lat=34.01,
        lng=-118.27,
        rating=4.5,
        review_count=200,
        price_level=3,
        categories=["cafe"],
        opening_hours={"periods": []},
        has_wifi=True,
        has_outlet=True,
        noise_level="moderate",
        good_for_studying=True,
        ambience_text=(
            "Specialty pourover bar with plenty of plugs and laptop-friendly tables. "
            "Modest hum of conversation; tolerable for coding sessions. Higher prices "
            "reflect single-origin offerings."
        ),
    ),
]


async def seed() -> None:
    settings = get_settings()
    oai = AsyncOpenAI(api_key=settings.openai_api_key)
    embedder = Embedder(openai_client=oai, model=settings.embedding_model)
    try:
        async with SessionLocal() as s:
            await s.execute(delete(Cafe).where(Cafe.google_place_id.like("smoke-%")))
            for row in SEED_TEXTS:
                row = dict(row)
                row["embedding"] = await embedder.embed(row["ambience_text"])
                s.add(Cafe(**row))
            await s.commit()
    finally:
        await oai.close()


async def query() -> None:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "http://localhost:8000/search",
            json={"query": "quiet place to study with outlets", "top_k": 3},
            timeout=30.0,
        )
        r.raise_for_status()
        body = r.json()
        print("Parsed:", body["parsed"])
        print("Results:")
        for x in body["results"]:
            print(
                f"  {x['name']:30s}  outlet={x['has_outlet']}  noise={x['noise_level']}  "
                f"sim={x['similarity']:.3f}"
            )


async def main() -> None:
    await seed()
    print("Seeded 3 smoke cafes (with real embeddings).")
    await query()


if __name__ == "__main__":
    asyncio.run(main())
