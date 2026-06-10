from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import (
    ParsedFilters,
    ParsedQuerySchema,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.search.service import search_cafes

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(
    req: SearchRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchResponse:
    outcome = await search_cafes(query=req.query, top_k=req.top_k, session=session)

    response.headers["X-LLM-Ms"] = f"{outcome.llm_ms:.1f}"
    response.headers["X-Embed-Ms"] = f"{outcome.embed_ms:.1f}"
    response.headers["X-Pgvector-Ms"] = f"{outcome.pgvector_ms:.1f}"
    response.headers["X-Cache"] = "hit" if outcome.cache_hit else "miss"

    return SearchResponse(
        parsed=ParsedQuerySchema(
            semantic_query=outcome.parsed.semantic_query,
            filters=ParsedFilters(
                has_outlet=outcome.parsed.has_outlet,
                open_now=outcome.parsed.open_now,
                price_max=outcome.parsed.price_max,
            ),
        ),
        results=[SearchResult(**r.__dict__) for r in outcome.results],
    )
