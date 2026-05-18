from __future__ import annotations

import math
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


def _offset_meters(lat: float, lng: float, north_m: float, east_m: float) -> tuple[float, float]:
    """Approximate WGS84 offset; good enough for city-scale search."""
    dlat = north_m / 111_320.0
    dlng = east_m / (111_320.0 * math.cos(math.radians(lat)))
    return lat + dlat, lng + dlng


def _multi_search_centers(lat: float, lng: float, radius_m: int) -> list[tuple[float, float]]:
    """Places API (New) searchNearby returns at most 20 places per request and has NO pageToken.

    We sample multiple circle centers (anchor + 8 compass offsets) so overlapping searches
    can surface more unique places than a single request allows (design: ~100 cafes in radius).
    """
    if radius_m <= 0:
        return [(lat, lng)]
    step_m = min(radius_m * 0.35, 2_500.0)
    centers: list[tuple[float, float]] = [(lat, lng)]
    for bearing_deg in range(0, 360, 45):
        rad = math.radians(bearing_deg)
        north = step_m * math.cos(rad)
        east = step_m * math.sin(rad)
        centers.append(_offset_meters(lat, lng, north, east))
    return centers


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
    async def _nearby_search_single(
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

    async def nearby_search(
        self,
        *,
        lat: float,
        lng: float,
        radius_m: int,
        limit: int = 100,
    ) -> list[NormalizedPlace]:
        """Aggregate nearby cafes from multiple circle centers (see _multi_search_centers)."""
        seen: set[str] = set()
        merged: list[NormalizedPlace] = []
        for clat, clng in _multi_search_centers(lat, lng, radius_m):
            batch = await self._nearby_search_single(lat=clat, lng=clng, radius_m=radius_m)
            for p in batch:
                if p.google_place_id in seen:
                    continue
                seen.add(p.google_place_id)
                merged.append(p)
                if len(merged) >= limit:
                    return merged
        return merged

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def place_details(self, place_id: str) -> NormalizedPlace:
        headers = {
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": _DETAILS_FIELDS,
        }
        r = await self._client.get(f"/v1/places/{place_id}", headers=headers)
        r.raise_for_status()
        return _from_raw(r.json())
