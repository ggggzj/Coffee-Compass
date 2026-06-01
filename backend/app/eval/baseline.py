"""Run retrieval + Week 2 baseline metrics; write docs/eval-results JSON."""

from __future__ import annotations

import asyncio
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import click
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import SessionLocal
from app.eval.golden_set import GoldenSet, load_golden_set
from app.eval.metrics import context_precision_score, cosine_similarity, mean
from app.models import Cafe
from app.search.embedder import Embedder
from app.search.retriever import RetrievalRequest, Retriever
from app.search.slot_extractor import extract_slots


async def _embed_text(embedder: Embedder, text: str) -> list[float]:
    return await embedder.embed(text)


async def retrieve_top_k(
    *,
    session: AsyncSession,
    openai_client: AsyncOpenAI,
    slot_model: str,
    embed_model: str,
    query: str,
    top_k: int,
) -> tuple[list[int], list[str], list[list[str]]]:
    """Returns (cafe_ids, ambience_texts, review_bundles per cafe)."""
    parsed = await extract_slots(openai_client=openai_client, model=slot_model, query=query)
    embedder = Embedder(openai_client=openai_client, model=embed_model)
    embedding = await embedder.embed(parsed.semantic_query)
    retriever = Retriever(session)
    rows = await retriever.search(
        RetrievalRequest(
            embedding=embedding,
            has_outlet=parsed.has_outlet,
            open_now=parsed.open_now,
            price_max=parsed.price_max,
            top_k=top_k,
        )
    )
    ids = [r.id for r in rows]
    ambiences = [r.ambience_text for r in rows]
    bundles: list[list[str]] = []
    for r in rows:
        c = await session.get(Cafe, r.id)
        bundles.append(list(c.review_snippets) if c and c.review_snippets else [])
    return ids, ambiences, bundles


async def evaluate_single_query(
    *,
    session: AsyncSession,
    openai_client: AsyncOpenAI,
    settings: Settings,
    query: str,
    expected_ids: set[int],
    top_k: int,
) -> dict:
    ids, ambiences, review_bundles = await retrieve_top_k(
        session=session,
        openai_client=openai_client,
        slot_model=settings.slot_extractor_model,
        embed_model=settings.embedding_model,
        query=query,
        top_k=top_k,
    )
    cp = context_precision_score(expected_ids, ids)
    embedder = Embedder(openai_client=openai_client, model=settings.embedding_model)
    q_emb = await _embed_text(embedder, query)
    rel_scores: list[float] = []
    for amb in ambiences:
        if not amb.strip():
            rel_scores.append(0.0)
            continue
        a_emb = await _embed_text(embedder, amb)
        rel_scores.append(cosine_similarity(q_emb, a_emb))
    ar = mean(rel_scores)

    faith_scores: list[float] = []
    for amb, reviews in zip(ambiences, review_bundles, strict=True):
        if not reviews:
            faith_scores.append(0.0)
            continue
        ctx = "\n".join(reviews[:5])
        a_emb = await _embed_text(embedder, amb)
        c_emb = await _embed_text(embedder, ctx)
        faith_scores.append(cosine_similarity(a_emb, c_emb))
    fn = mean(faith_scores)

    return {
        "query": query,
        "retrieved_ids": ids,
        "context_precision": cp,
        "answer_relevancy": ar,
        "faithfulness": fn,
    }


def _git_sha() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[3], text=True
            ).strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


async def run_baseline(
    *,
    golden: GoldenSet,
    top_k: int = 5,
    output_path: Path | None = None,
) -> dict:
    settings = get_settings()
    oai = AsyncOpenAI(api_key=settings.openai_api_key)
    per_query: list[dict] = []
    try:
        async with SessionLocal() as session:
            for item in golden.items:
                row = await evaluate_single_query(
                    session=session,
                    openai_client=oai,
                    settings=settings,
                    query=item.query,
                    expected_ids=set(item.expected_cafe_ids),
                    top_k=top_k,
                )
                per_query.append(row)
    finally:
        await oai.close()

    cps = [float(p["context_precision"]) for p in per_query]
    ars = [float(p["answer_relevancy"]) for p in per_query]
    fns = [float(p["faithfulness"]) for p in per_query]
    out = {
        "meta": {
            "run_at": datetime.now(tz=UTC).isoformat(),
            "golden_set": "backend/app/eval/golden_set.json",
            "golden_version": golden.version,
            "commit": _git_sha(),
            "models": {
                "slot_extractor": settings.slot_extractor_model,
                "review_tagger": f"{settings.review_tagger_model} {settings.review_tagger_impl}",
                "embedding": settings.embedding_model,
            },
            "notes": "faithfulness/answer_relevancy use embedding cosine (Week 2 baseline). "
            "Populate review_snippets on cafes (ingest/retag) for faithfulness signal.",
        },
        "metrics": {
            "context_precision": mean(cps),
            "faithfulness": mean(fns),
            "answer_relevancy": mean(ars),
        },
        "per_query": per_query,
    }
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
        output_path.write_text(payload, encoding="utf-8")
    return out


@click.command()
@click.option(
    "--golden",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to golden_set.json (default: bundled)",
)
@click.option("--top-k", type=int, default=5)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Write JSON here (e.g. docs/eval-results/2026-05-18-v1.json from repo root)",
)
def main(golden: Path | None, top_k: int, output: Path | None) -> None:
    g = load_golden_set(golden)
    out = asyncio.run(run_baseline(golden=g, top_k=top_k, output_path=output))
    click.echo(json.dumps(out["metrics"], indent=2))


if __name__ == "__main__":
    main()
