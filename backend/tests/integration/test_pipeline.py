from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select

from app.ingestion.google_places import NormalizedPlace
from app.ingestion.pipeline import run_pipeline
from app.models import Cafe


@pytest.mark.asyncio
async def test_pipeline_persists_enriched_cafes(session, monkeypatch, tmp_path):
    google_place = NormalizedPlace(
        google_place_id="g1",
        name="Bricks & Scones",
        address="403 N Larchmont Blvd",
        lat=34.075,
        lng=-118.323,
        rating=4.6,
        review_count=1200,
        price_level=2,
        categories=["cafe"],
        opening_hours={"periods": []},
        reviews=[
            "Quiet study spot with plenty of outlets.",
            "Fast wifi and laptop-friendly tables.",
        ],
    )

    google_client = MagicMock()
    google_client.nearby_search = AsyncMock(return_value=[google_place])
    google_client.place_details = AsyncMock(return_value=google_place)

    from app.ingestion.tagger import CafeTags

    async def fake_tagger(**kwargs):
        return CafeTags(
            has_wifi=True,
            has_outlet=True,
            noise_level="quiet",
            good_for_studying=True,
            ambience_text="A quiet study spot with outlets and fast wifi.",
        )

    async def fake_embed_many(self, texts, *, batch_size=128):
        return [[0.1] * 1536 for _ in texts]

    monkeypatch.setattr("app.ingestion.pipeline.tag_cafe", fake_tagger)
    monkeypatch.setattr("app.ingestion.pipeline.Embedder.embed_many", fake_embed_many)
    monkeypatch.setattr("app.ingestion.pipeline.PLACES_CACHE_DIR", tmp_path / "places_raw")

    await run_pipeline(
        session=session,
        google_client=google_client,
        openai_client=MagicMock(),
        lat=34.022,
        lng=-118.286,
        radius_m=5000,
        limit=10,
        tagger_model="gpt-4o-mini",
        embedding_model="text-embedding-3-small",
        review_tagger_impl="v1",
    )
    await session.commit()

    row = (await session.execute(select(Cafe))).scalar_one()
    assert row.google_place_id == "g1"
    assert row.has_outlet is True
    assert row.rating == pytest.approx(4.6)  # rating column is REAL (float32) → tolerate epsilon
    assert row.price_level == 2
    assert row.ambience_text.startswith("A quiet study spot")
    assert row.embedding is not None
    assert len(row.embedding) == 1536
    assert (tmp_path / "places_raw" / "g1.json").exists()
