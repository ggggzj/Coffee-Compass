from __future__ import annotations

import asyncio
import dataclasses
import json
from pathlib import Path

import click
import structlog
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import SessionLocal
from app.ingestion.google_places import GooglePlacesClient, NormalizedPlace
from app.ingestion.tagger import CafeTags, tag_cafe
from app.models import Cafe
from app.search.embedder import Embedder

log = structlog.get_logger()
PLACES_CACHE_DIR = Path("data/places_raw")


def _review_texts(place: NormalizedPlace) -> list[str]:
    return [r for r in place.reviews if r and str(r).strip()]


async def tag_cafe_for_place(
    *,
    openai_client: AsyncOpenAI,
    model: str,
    impl: str,
    place: NormalizedPlace,
) -> CafeTags:
    if impl == "v2":
        from app.ingestion.review_tagger_v2 import tag_cafe_v2

        return await tag_cafe_v2(
            openai_client=openai_client,
            model=model,
            name=place.name,
            categories=place.categories,
            rating=place.rating,
            price_level=place.price_level,
            editorial_summary=place.editorial_summary,
            reviews=_review_texts(place),
        )
    return await tag_cafe(
        openai_client=openai_client,
        model=model,
        name=place.name,
        categories=place.categories,
        rating=place.rating,
        price_level=place.price_level,
        reviews=_review_texts(place),
    )


def _cache_place_details(place: NormalizedPlace) -> None:
    PLACES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (PLACES_CACHE_DIR / f"{place.google_place_id}.json").write_text(
        json.dumps(dataclasses.asdict(place), ensure_ascii=False, indent=2)
    )


async def _upsert_cafe(
    session: AsyncSession,
    *,
    place: NormalizedPlace,
    tags,
    embedding: list[float],
) -> None:
    existing = await session.execute(
        select(Cafe).where(Cafe.google_place_id == place.google_place_id)
    )
    cafe = existing.scalar_one_or_none()
    fields = dict(
        google_place_id=place.google_place_id,
        name=place.name,
        address=place.address,
        lat=place.lat,
        lng=place.lng,
        rating=place.rating,
        review_count=place.review_count,
        price_level=place.price_level,
        categories=place.categories,
        opening_hours=place.opening_hours,
        has_wifi=tags.has_wifi,
        has_outlet=tags.has_outlet,
        noise_level=tags.noise_level,
        good_for_studying=tags.good_for_studying,
        ambience_text=tags.ambience_text,
        embedding=embedding,
        editorial_summary=place.editorial_summary,
        review_snippets=_review_texts(place) or None,
    )
    if cafe is None:
        session.add(Cafe(**fields))
    else:
        for k, v in fields.items():
            setattr(cafe, k, v)


async def run_pipeline(
    *,
    session: AsyncSession,
    google_client: GooglePlacesClient,
    openai_client: AsyncOpenAI,
    lat: float,
    lng: float,
    radius_m: int,
    limit: int,
    tagger_model: str,
    embedding_model: str,
    review_tagger_impl: str,
) -> int:
    embedder = Embedder(openai_client=openai_client, model=embedding_model)

    nearby = await google_client.nearby_search(
        lat=lat, lng=lng, radius_m=radius_m, limit=limit
    )
    log.info("nearby_fetched", count=len(nearby))

    for raw in nearby:
        details = await google_client.place_details(raw.google_place_id)
        _cache_place_details(details)
        log.info(
            "place_details_fetched",
            id=details.google_place_id,
            name=details.name,
            review_count_pulled=len(details.reviews),
        )

        tags = await tag_cafe_for_place(
            openai_client=openai_client,
            model=tagger_model,
            impl=review_tagger_impl,
            place=details,
        )
        embedding = await embedder.embed(tags.ambience_text)

        await _upsert_cafe(session, place=details, tags=tags, embedding=embedding)
        log.info("cafe_upserted", name=details.name, has_outlet=tags.has_outlet)

    await session.commit()
    return len(nearby)


@click.command()
@click.option("--lat", type=float, default=None)
@click.option("--lng", type=float, default=None)
@click.option("--radius-m", type=int, default=None)
@click.option("--retag-only", is_flag=True, help="Skip Google fetch; re-tag from DB/cache only")
@click.option("--limit", type=int, default=None)
def main(
    lat: float | None,
    lng: float | None,
    radius_m: int | None,
    limit: int | None,
    retag_only: bool,
) -> None:
    settings = get_settings()
    lat = lat or settings.usc_lat
    lng = lng or settings.usc_lng
    radius_m = radius_m or settings.ingest_radius_meters
    limit = limit or settings.ingest_limit

    async def _go() -> None:
        oai = AsyncOpenAI(api_key=settings.openai_api_key)
        try:
            async with SessionLocal() as session:
                if retag_only:
                    from app.ingestion.retag import run_retag

                    n = await run_retag(
                        session=session,
                        openai_client=oai,
                        tagger_model=settings.review_tagger_model,
                        embedding_model=settings.embedding_model,
                        review_tagger_impl=settings.review_tagger_impl,
                        limit=limit,
                    )
                    print(f"Re-tagged {n} cafes.")
                    return
            async with GooglePlacesClient(api_key=settings.google_places_api_key) as g:
                async with SessionLocal() as session:
                    n = await run_pipeline(
                        session=session,
                        google_client=g,
                        openai_client=oai,
                        lat=lat,
                        lng=lng,
                        radius_m=radius_m,
                        limit=limit,
                        tagger_model=settings.review_tagger_model,
                        embedding_model=settings.embedding_model,
                        review_tagger_impl=settings.review_tagger_impl,
                    )
                    print(f"Ingested {n} cafes.")
        finally:
            await oai.close()

    asyncio.run(_go())


if __name__ == "__main__":
    main()
