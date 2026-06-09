from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Response
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.observability import Timer
from app.schemas import (
    ParsedFilters,
    ParsedQuerySchema,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.search.cache import TTLLRUCache
from app.search.embedder import Embedder
from app.search.retriever import RetrievalRequest, Retriever
from app.search.slot_extractor import ParsedQuery, extract_slots

router = APIRouter()
log = structlog.get_logger()

# Cache key: (slot_model, embed_model, query) -> (parsed query, embedding).
# A hit skips BOTH the slot-extractor and embedding OpenAI calls, so the request
# latency collapses to the pgvector retrieval stage. 10-minute TTL per design.
_SLOT_CACHE: TTLLRUCache[tuple[str, str, str], tuple[ParsedQuery, list[float]]] = TTLLRUCache(
    maxsize=512, ttl_seconds=600.0
)


def reset_slot_cache() -> None:
    """Clear the module-level slot cache (used by tests for isolation)."""
    _SLOT_CACHE.clear()


def _openai_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.openai_api_key)


@router.post("/search", response_model=SearchResponse)
async def search(
    req: SearchRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchResponse:
    settings = get_settings()
    cache_key = (settings.slot_extractor_model, settings.embedding_model, req.query)

    cached = _SLOT_CACHE.get(cache_key)
    if cached is not None:
        parsed, embedding = cached
        llm_ms = embed_ms = 0.0
        cache_hit = True
    else:
        oai = _openai_client()
        try:
            with Timer() as t_llm:
                parsed = await extract_slots(
                    openai_client=oai, model=settings.slot_extractor_model, query=req.query
                )
            embedder = Embedder(openai_client=oai, model=settings.embedding_model)
            with Timer() as t_embed:
                embedding = await embedder.embed(parsed.semantic_query)
        finally:
            await oai.close()
        llm_ms, embed_ms = t_llm.ms, t_embed.ms
        cache_hit = False
        _SLOT_CACHE.set(cache_key, (parsed, embedding))

    retriever = Retriever(session)
    with Timer() as t_db:
        results = await retriever.search(
            RetrievalRequest(
                embedding=embedding,
                has_outlet=parsed.has_outlet,
                open_now=parsed.open_now,
                price_max=parsed.price_max,
                top_k=req.top_k,
            )
        )

    response.headers["X-LLM-Ms"] = f"{llm_ms:.1f}"
    response.headers["X-Embed-Ms"] = f"{embed_ms:.1f}"
    response.headers["X-Pgvector-Ms"] = f"{t_db.ms:.1f}"
    response.headers["X-Cache"] = "hit" if cache_hit else "miss"
    log.info(
        "search_latency",
        cache=("hit" if cache_hit else "miss"),
        llm_ms=round(llm_ms, 1),
        embed_ms=round(embed_ms, 1),
        pgvector_ms=round(t_db.ms, 1),
        results=len(results),
    )

    return SearchResponse(
        parsed=ParsedQuerySchema(
            semantic_query=parsed.semantic_query,
            filters=ParsedFilters(
                has_outlet=parsed.has_outlet,
                open_now=parsed.open_now,
                price_max=parsed.price_max,
            ),
        ),
        results=[SearchResult(**r.__dict__) for r in results],
    )
