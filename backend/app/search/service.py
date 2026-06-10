from __future__ import annotations

from dataclasses import dataclass

import structlog
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Cafe
from app.observability import Timer
from app.search.cache import TTLLRUCache
from app.search.embedder import Embedder
from app.search.retriever import RetrievalRequest, RetrievalResult, Retriever
from app.search.slot_extractor import ParsedQuery, extract_slots

log = structlog.get_logger()

# Single source of truth for the search pipeline (slot-extract -> embed -> retrieve).
# Both the /search endpoint and the agent tools call search_cafes, so they can never
# drift and they share one cache.
#
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


async def get_cafe(*, cafe_id: int, session: AsyncSession) -> Cafe | None:
    """Load a single Cafe by id, or None if it does not exist.

    Shared by the get_shop_detail agent tool and the GET /cafes/{id} route so
    there is one cafe-by-id load path.
    """
    return await session.get(Cafe, cafe_id)


@dataclass(frozen=True)
class SearchOutcome:
    parsed: ParsedQuery
    results: list[RetrievalResult]
    llm_ms: float
    embed_ms: float
    pgvector_ms: float
    cache_hit: bool


async def search_cafes(*, query: str, top_k: int, session: AsyncSession) -> SearchOutcome:
    settings = get_settings()
    cache_key = (settings.slot_extractor_model, settings.embedding_model, query)

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
                    openai_client=oai, model=settings.slot_extractor_model, query=query
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
                top_k=top_k,
            )
        )

    log.info(
        "search_latency",
        cache=("hit" if cache_hit else "miss"),
        llm_ms=round(llm_ms, 1),
        embed_ms=round(embed_ms, 1),
        pgvector_ms=round(t_db.ms, 1),
        results=len(results),
    )

    return SearchOutcome(
        parsed=parsed,
        results=results,
        llm_ms=llm_ms,
        embed_ms=embed_ms,
        pgvector_ms=t_db.ms,
        cache_hit=cache_hit,
    )
