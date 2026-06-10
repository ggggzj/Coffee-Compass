from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Cafe
from app.search.opening_hours import LA, is_open_at


@dataclass(frozen=True)
class RetrievalRequest:
    embedding: list[float]
    has_outlet: bool | None
    open_now: bool | None
    price_max: int | None
    top_k: int = 5


@dataclass(frozen=True)
class RetrievalResult:
    id: int
    name: str
    address: str
    lat: float
    lng: float
    rating: float | None
    price_level: int | None
    has_outlet: bool | None
    has_wifi: bool | None
    noise_level: str | None
    good_for_studying: bool | None
    open_now: bool
    similarity: float
    ambience_text: str


class Retriever:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, req: RetrievalRequest) -> list[RetrievalResult]:
        candidate_k = max(req.top_k * 4, 20)
        stmt = select(
            Cafe,
            (1 - Cafe.embedding.cosine_distance(req.embedding)).label("similarity"),
        )
        if req.has_outlet is not None:
            stmt = stmt.where(Cafe.has_outlet == req.has_outlet)
        if req.price_max is not None:
            stmt = stmt.where(Cafe.price_level <= req.price_max)
        stmt = stmt.order_by(Cafe.embedding.cosine_distance(req.embedding)).limit(candidate_k)

        rows = (await self._session.execute(stmt)).all()
        now = datetime.now(tz=LA)

        results: list[RetrievalResult] = []
        for cafe, similarity in rows:
            open_now = is_open_at(cafe.opening_hours, now)
            if req.open_now is True and not open_now:
                continue
            results.append(
                RetrievalResult(
                    id=cafe.id,
                    name=cafe.name,
                    address=cafe.address,
                    lat=cafe.lat,
                    lng=cafe.lng,
                    rating=cafe.rating,
                    price_level=cafe.price_level,
                    has_outlet=cafe.has_outlet,
                    has_wifi=cafe.has_wifi,
                    noise_level=cafe.noise_level,
                    good_for_studying=cafe.good_for_studying,
                    open_now=open_now,
                    similarity=float(similarity),
                    ambience_text=cafe.ambience_text,
                )
            )
            if len(results) >= req.top_k:
                break
        return results
