import pytest

from app.models import Cafe
from app.search.retriever import RetrievalRequest, Retriever


def _seed_cafe(**overrides):
    base = dict(
        google_place_id="g",
        name="Cafe",
        address="addr",
        lat=34.0,
        lng=-118.0,
        rating=4.0,
        review_count=10,
        price_level=2,
        categories=["cafe"],
        opening_hours={"periods": []},
        has_wifi=True,
        has_outlet=True,
        noise_level="quiet",
        good_for_studying=True,
        ambience_text="Quiet study spot",
        embedding=[0.1] * 1536,
    )
    base.update(overrides)
    return Cafe(**base)


@pytest.mark.asyncio
async def test_retriever_filters_by_outlet_and_orders_by_similarity(session):
    # Three cafes:
    #  A: has_outlet=True, embedding close to query
    #  B: has_outlet=True, embedding far from query
    #  C: has_outlet=False
    query_vec = [0.2] + [0.0] * 1535
    a_vec = [0.2] + [0.0] * 1535  # cosine sim ~ 1.0
    b_vec = [0.0, 0.2] + [0.0] * 1534
    c_vec = [0.2] + [0.0] * 1535
    session.add(_seed_cafe(google_place_id="A", name="A", embedding=a_vec, has_outlet=True))
    session.add(_seed_cafe(google_place_id="B", name="B", embedding=b_vec, has_outlet=True))
    session.add(_seed_cafe(google_place_id="C", name="C", embedding=c_vec, has_outlet=False))
    await session.commit()

    retriever = Retriever(session)
    results = await retriever.search(
        RetrievalRequest(
            embedding=query_vec, has_outlet=True, open_now=None, price_max=None, top_k=5
        )
    )

    names = [r.name for r in results]
    assert "C" not in names
    assert names[0] == "A"  # closest similarity first


@pytest.mark.asyncio
async def test_retriever_filters_by_price_max(session):
    session.add(_seed_cafe(google_place_id="X", name="X", price_level=3, embedding=[0.1] * 1536))
    session.add(_seed_cafe(google_place_id="Y", name="Y", price_level=2, embedding=[0.1] * 1536))
    await session.commit()
    retriever = Retriever(session)
    results = await retriever.search(
        RetrievalRequest(
            embedding=[0.1] * 1536, has_outlet=None, open_now=None, price_max=2, top_k=5
        )
    )
    names = [r.name for r in results]
    assert names == ["Y"]
