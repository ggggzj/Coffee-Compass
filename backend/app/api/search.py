from __future__ import annotations

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.schemas import (
    ParsedFilters,
    ParsedQuerySchema,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.search.embedder import Embedder
from app.search.retriever import RetrievalRequest, Retriever
from app.search.slot_extractor import extract_slots

router = APIRouter()


def _openai_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.openai_api_key)


@router.post("/search", response_model=SearchResponse)
async def search(
    req: SearchRequest,
    session: AsyncSession = Depends(get_session),
) -> SearchResponse:
    settings = get_settings()
    oai = _openai_client()
    try:
        parsed = await extract_slots(
            openai_client=oai, model=settings.slot_extractor_model, query=req.query
        )
        embedder = Embedder(openai_client=oai, model=settings.embedding_model)
        embedding = await embedder.embed(parsed.semantic_query)
    finally:
        await oai.close()

    retriever = Retriever(session)
    results = await retriever.search(
        RetrievalRequest(
            embedding=embedding,
            has_outlet=parsed.has_outlet,
            open_now=parsed.open_now,
            price_max=parsed.price_max,
            top_k=req.top_k,
        )
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
