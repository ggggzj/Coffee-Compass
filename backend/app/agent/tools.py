from __future__ import annotations

from collections.abc import Callable

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.search.service import get_cafe, search_cafes


class SearchShopsArgs(BaseModel):
    query: str = Field(
        ...,
        description=(
            "A natural-language description of the kind of coffee shop the user "
            "wants — vibe, use case, and any constraints like cheap, has outlets, "
            "or open now. Phrase follow-ups as a full standalone query."
        ),
    )
    top_k: int = Field(5, ge=1, le=20, description="How many shops to return.")


class GetShopDetailArgs(BaseModel):
    cafe_id: int = Field(..., description="The id of a cafe returned by search_shops.")


def _cafe_detail(cafe) -> dict:
    return {
        "id": cafe.id,
        "name": cafe.name,
        "address": cafe.address,
        "lat": cafe.lat,
        "lng": cafe.lng,
        "rating": cafe.rating,
        "price_level": cafe.price_level,
        "has_wifi": cafe.has_wifi,
        "has_outlet": cafe.has_outlet,
        "noise_level": cafe.noise_level,
        "good_for_studying": cafe.good_for_studying,
        "ambience_text": cafe.ambience_text,
        "opening_hours": cafe.opening_hours,
    }


def _shop_summary(r) -> dict:
    return {
        "id": r.id,
        "name": r.name,
        "similarity": round(r.similarity, 4),
        "price_level": r.price_level,
        "has_outlet": r.has_outlet,
        "noise_level": r.noise_level,
        "ambience_text": r.ambience_text,
        "lat": r.lat,
        "lng": r.lng,
        "open_now": r.open_now,
    }


DEFAULT_MAX_SEARCHES = 3


def build_agent_tools(
    session: AsyncSession,
    *,
    on_results: Callable[[list[dict]], None] | None = None,
    max_searches: int = DEFAULT_MAX_SEARCHES,
) -> list[BaseTool]:
    """Build the agent's tools, closing over this request's database session.

    Constructed per request (not a process-wide singleton) because data access is
    request-scoped — every tool call runs inside the caller's session.

    ``on_results`` is invoked with each search_shops result batch so the agent
    layer can track which cafes were surfaced this turn (for grounded
    recommendations + the guaranteed-final fallback).

    ``max_searches`` hard-caps how many real searches one turn may run. Past the
    cap, search_shops short-circuits with a message telling the model to stop and
    present what it has — preventing the synonym-retry loop where an LLM re-runs
    the same search reworded ("cheap" -> "affordable" -> ...).
    """
    search_count = 0

    async def search_shops(query: str, top_k: int = 5) -> list[dict] | str:
        nonlocal search_count
        if search_count >= max_searches:
            return (
                f"Search limit reached ({max_searches} searches this turn). Do NOT "
                "search again or reword the query. Present the cafes you have "
                "already found — fewer than 3 is fine."
            )
        search_count += 1
        outcome = await search_cafes(query=query, top_k=top_k, session=session)
        summaries = [_shop_summary(r) for r in outcome.results]
        if on_results is not None:
            on_results(summaries)
        return summaries

    async def get_shop_detail(cafe_id: int) -> dict:
        cafe = await get_cafe(cafe_id=cafe_id, session=session)
        if cafe is None:
            return {"id": cafe_id, "error": "not_found"}
        return _cafe_detail(cafe)

    search_shops_tool = StructuredTool.from_function(
        coroutine=search_shops,
        name="search_shops",
        description=(
            "Find coffee shops matching a natural-language query about vibe, use "
            "case, price, outlets, or open-now. Returns grounded shops with ids and "
            "coordinates. Use this to answer any recommendation request."
        ),
        args_schema=SearchShopsArgs,
    )
    get_shop_detail_tool = StructuredTool.from_function(
        coroutine=get_shop_detail,
        name="get_shop_detail",
        description=(
            "Look up the full details of one coffee shop by its id (address, rating, "
            "hours, amenities, ambience). Use after search_shops when the user asks "
            "about a specific shop."
        ),
        args_schema=GetShopDetailArgs,
    )

    return [search_shops_tool, get_shop_detail_tool]
