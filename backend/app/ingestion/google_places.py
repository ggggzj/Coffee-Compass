from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

_BASE_URL = "https://places.googleapis.com"

_PRICE_MAP = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}

_NEARBY_FIELDS = (
    "places.id,places.displayName,places.formattedAddress,places.location,"
    "places.rating,places.userRatingCount,places.priceLevel,places.types"
)

_DETAILS_FIELDS = (
    "id,displayName,formattedAddress,location,rating,userRatingCount,priceLevel,types,"
    "regularOpeningHours,reviews"
)


@dataclass
class NormalizedPlace:
    google_place_id: str
    name: str
    address: str
    lat: float
    lng: float
    rating: float | None
    review_count: int | None
    price_level: int | None
    categories: list[str]
    opening_hours: dict[str, Any] | None
    reviews: list[str] = field(default_factory=list)


def _from_raw(raw: dict[str, Any]) -> NormalizedPlace:
    price = raw.get("priceLevel")
    return NormalizedPlace(
        google_place_id=raw["id"],
        name=raw.get("displayName", {}).get("text", ""),
        address=raw.get("formattedAddress", ""),
        lat=raw["location"]["latitude"],
        lng=raw["location"]["longitude"],
        rating=raw.get("rating"),
        review_count=raw.get("userRatingCount"),
        price_level=_PRICE_MAP.get(price) if price else None,
        categories=list(raw.get("types", [])),
        opening_hours=raw.get("regularOpeningHours"),
        reviews=[r.get("text", {}).get("text", "") for r in raw.get("reviews", [])],
    )


class GooglePlacesClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.AsyncClient(base_url=_BASE_URL, timeout=15.0)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def nearby_search(
        self, *, lat: float, lng: float, radius_m: int
    ) -> list[NormalizedPlace]:
        headers = {
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": _NEARBY_FIELDS,
            "Content-Type": "application/json",
        }
        body = {
            "includedTypes": ["cafe"],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": float(radius_m),
                }
            },
        }
        r = await self._client.post("/v1/places:searchNearby", json=body, headers=headers)
        r.raise_for_status()
        return [_from_raw(p) for p in r.json().get("places", [])]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def place_details(self, place_id: str) -> NormalizedPlace:
        headers = {
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": _DETAILS_FIELDS,
        }
        r = await self._client.get(f"/v1/places/{place_id}", headers=headers)
        r.raise_for_status()
        return _from_raw(r.json())
