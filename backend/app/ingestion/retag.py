"""Re-run review tagger + embedding from cached place JSON or DB row (no Google search)."""

from __future__ import annotations

import json

import structlog
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.google_places import NormalizedPlace
from app.ingestion.pipeline import PLACES_CACHE_DIR, _upsert_cafe, tag_cafe_for_place
from app.models import Cafe
from app.search.embedder import Embedder

log = structlog.get_logger()


def _place_from_cache(google_place_id: str) -> NormalizedPlace | None:
    path = PLACES_CACHE_DIR / f"{google_place_id}.json"
    if not path.exists():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    return NormalizedPlace(
        google_place_id=d["google_place_id"],
        name=d["name"],
        address=d["address"],
        lat=d["lat"],
        lng=d["lng"],
        rating=d.get("rating"),
        review_count=d.get("review_count"),
        price_level=d.get("price_level"),
        categories=d.get("categories") or [],
        opening_hours=d.get("opening_hours"),
        editorial_summary=d.get("editorial_summary"),
        reviews=list(d.get("reviews") or []),
    )


def _place_from_cafe_row(cafe: Cafe) -> NormalizedPlace:
    return NormalizedPlace(
        google_place_id=cafe.google_place_id,
        name=cafe.name,
        address=cafe.address,
        lat=cafe.lat,
        lng=cafe.lng,
        rating=cafe.rating,
        review_count=cafe.review_count,
        price_level=cafe.price_level,
        categories=cafe.categories or [],
        opening_hours=cafe.opening_hours,
        editorial_summary=cafe.editorial_summary,
        reviews=list(cafe.review_snippets or []),
    )


def resolve_place(cafe: Cafe) -> NormalizedPlace:
    cached = _place_from_cache(cafe.google_place_id)
    if cached is not None:
        return cached
    return _place_from_cafe_row(cafe)


async def run_retag(
    *,
    session: AsyncSession,
    openai_client: AsyncOpenAI,
    tagger_model: str,
    embedding_model: str,
    review_tagger_impl: str,
    limit: int | None,
) -> int:
    embedder = Embedder(openai_client=openai_client, model=embedding_model)
    stmt = select(Cafe).order_by(Cafe.id)
    if limit is not None:
        stmt = stmt.limit(limit)
    rows = (await session.execute(stmt)).scalars().all()
    n = 0
    for cafe in rows:
        place = resolve_place(cafe)
        tags = await tag_cafe_for_place(
            openai_client=openai_client,
            model=tagger_model,
            impl=review_tagger_impl,
            place=place,
        )
        embedding = await embedder.embed(tags.ambience_text)
        await _upsert_cafe(session, place=place, tags=tags, embedding=embedding)
        n += 1
        log.info("cafe_retagged", name=place.name)
    await session.commit()
    return n
