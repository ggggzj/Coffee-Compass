import json
from pathlib import Path

import httpx
import pytest
import respx

from app.ingestion.google_places import GooglePlacesClient, NormalizedPlace

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.asyncio
async def test_nearby_search_returns_normalized_places():
    nearby = json.loads((FIXTURES / "google_nearby_search.json").read_text())
    with respx.mock(base_url="https://places.googleapis.com") as mock:
        mock.post("/v1/places:searchNearby").mock(return_value=httpx.Response(200, json=nearby))
        async with GooglePlacesClient(api_key="fake") as client:
            places = await client.nearby_search(lat=34.022, lng=-118.286, radius_m=5000)
    assert len(places) == 2
    assert places[0] == NormalizedPlace(
        google_place_id="ChIJabc1",
        name="Bricks & Scones",
        address="403 N Larchmont Blvd, Los Angeles, CA",
        lat=34.075,
        lng=-118.323,
        rating=4.6,
        review_count=1200,
        price_level=2,
        categories=["cafe", "bakery"],
        opening_hours=None,
        reviews=[],
    )


@pytest.mark.asyncio
async def test_place_details_merges_hours_and_reviews():
    details = json.loads((FIXTURES / "google_place_details.json").read_text())
    with respx.mock(base_url="https://places.googleapis.com") as mock:
        mock.get("/v1/places/ChIJabc1").mock(return_value=httpx.Response(200, json=details))
        async with GooglePlacesClient(api_key="fake") as client:
            place = await client.place_details("ChIJabc1")
    assert place.opening_hours is not None
    assert place.opening_hours["periods"][0]["open"]["hour"] == 7
    assert len(place.reviews) == 2
    assert "outlets" in place.reviews[0].lower()
