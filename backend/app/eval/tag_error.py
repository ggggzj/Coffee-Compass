"""Tag-error A/B: how often does each slot extractor emit a WRONG hard SQL filter?

A 'tag error' is a hard-constraint slot (has_outlet / open_now / price_max) whose
value would produce a different WHERE clause than the gold label for that query --
a false-positive (over-firing a filter the user never asked for), a false-negative
(dropping one they did), or a wrong value. semantic_query is free text, not a tag,
and is not scored.

The metric mirrors app/search/retriever.py EXACTLY so each counted error is a real
retrieval defect, not a cosmetic slot diff:
  - has_outlet / price_max: the retriever filters whenever the slot is not None, so
    any non-None value is a distinct filter -> strict inequality vs gold.
  - open_now: the retriever filters ONLY when the slot is True, so False and None are
    identical in effect -> we normalize both to None before comparing. This is the
    conservative choice: it never inflates the naive baseline's error count.

We compare the naive 'vibe-into-SQL' extractor (app/search/naive_slot_extractor.py)
against the current separated design (app/search/slot_extractor.py) over the labeled
set, and report the real measured error-reduction %. Run with OpenAI keys:

    cd backend && uv run python -m app.eval.tag_error \
        --output ../docs/eval-results/$(date +%F)-tag-error.json
"""

from __future__ import annotations

import asyncio
import json
import subprocess
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path

import click
from openai import AsyncOpenAI

from app.config import get_settings
from app.eval.tag_error_set import GoldSlots, TagErrorItem, TagErrorSet, load_tag_error_set
from app.search.naive_slot_extractor import extract_naive_slots
from app.search.slot_extractor import ParsedQuery, extract_slots

Extractor = Callable[[str], Awaitable[ParsedQuery]]

_HARD_SLOTS = ("has_outlet", "open_now", "price_max")


def _effective(slot: str, value: object) -> object:
    """Map a predicted slot to the value the retriever would actually filter on."""
    # open_now only filters when True; False and None both mean 'no filter'.
    if slot == "open_now" and value is not True:
        return None
    return value


def slot_errors(gold: GoldSlots, pred: ParsedQuery) -> list[str]:
    """Return the names of hard slots where pred would produce a wrong SQL filter."""
    wrong: list[str] = []
    for slot in _HARD_SLOTS:
        g = _effective(slot, getattr(gold, slot))
        p = _effective(slot, getattr(pred, slot))
        if g != p:
            wrong.append(slot)
    return wrong


def reduction_pct(naive_total: int, separated_total: int) -> float | None:
    """Percent fewer tag errors; None when the naive baseline made none (undefined)."""
    if naive_total == 0:
        return None
    return round((naive_total - separated_total) / naive_total * 100, 1)


def score_predictions(
    items: list[TagErrorItem],
    naive_preds: list[ParsedQuery],
    separated_preds: list[ParsedQuery],
) -> dict:
    """Pure scoring: given both extractors' outputs, compute per-query + aggregate errors."""
    per_query: list[dict] = []
    naive_total = 0
    separated_total = 0
    for item, np, sp in zip(items, naive_preds, separated_preds, strict=True):
        n_wrong = slot_errors(item.gold, np)
        s_wrong = slot_errors(item.gold, sp)
        naive_total += len(n_wrong)
        separated_total += len(s_wrong)
        per_query.append(
            {
                "id": item.id,
                "lang": item.lang,
                "category": item.category,
                "query": item.query,
                "gold": item.gold.model_dump(),
                "naive": {"slots": _slots(np), "errors": n_wrong},
                "separated": {"slots": _slots(sp), "errors": s_wrong},
            }
        )

    by_cat = _per_category(per_query)
    return {
        "totals": {
            "queries": len(items),
            "slots_scored": len(items) * len(_HARD_SLOTS),
            "naive_errors": naive_total,
            "separated_errors": separated_total,
            "error_reduction_pct": reduction_pct(naive_total, separated_total),
        },
        "by_category": by_cat,
        "per_query": per_query,
    }


def _slots(p: ParsedQuery) -> dict:
    return {"has_outlet": p.has_outlet, "open_now": p.open_now, "price_max": p.price_max}


def _per_category(per_query: list[dict]) -> dict:
    cats: dict[str, dict] = {}
    for row in per_query:
        c = cats.setdefault(row["category"], {"naive_errors": 0, "separated_errors": 0})
        c["naive_errors"] += len(row["naive"]["errors"])
        c["separated_errors"] += len(row["separated"]["errors"])
    for c in cats.values():
        c["error_reduction_pct"] = reduction_pct(c["naive_errors"], c["separated_errors"])
    return cats


async def run_tag_error_eval(
    *,
    tag_set: TagErrorSet,
    naive: Extractor,
    separated: Extractor,
) -> dict:
    """Run both extractors over every query (sequentially, temp=0) and score."""
    naive_preds: list[ParsedQuery] = []
    separated_preds: list[ParsedQuery] = []
    for item in tag_set.items:
        naive_preds.append(await naive(item.query))
        separated_preds.append(await separated(item.query))
    return score_predictions(tag_set.items, naive_preds, separated_preds)


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[3], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


@click.command()
@click.option(
    "--tag-set",
    "tag_set_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to tag_error_set.json (default: bundled)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Write full results JSON here (e.g. ../docs/eval-results/2026-06-09-tag-error.json)",
)
def main(tag_set_path: Path | None, output: Path | None) -> None:
    settings = get_settings()
    tag_set = load_tag_error_set(tag_set_path)
    oai = AsyncOpenAI(api_key=settings.openai_api_key)
    model = settings.slot_extractor_model

    async def naive(q: str) -> ParsedQuery:
        return await extract_naive_slots(openai_client=oai, model=model, query=q)

    async def separated(q: str) -> ParsedQuery:
        return await extract_slots(openai_client=oai, model=model, query=q)

    async def _go() -> dict:
        try:
            return await run_tag_error_eval(tag_set=tag_set, naive=naive, separated=separated)
        finally:
            await oai.close()

    result = asyncio.run(_go())
    result["meta"] = {
        "run_at": datetime.now(tz=UTC).isoformat(),
        "tag_error_set": "backend/app/eval/tag_error_set.json",
        "tag_error_set_version": tag_set.version,
        "commit": _git_sha(),
        "model": model,
        "metric": "hard-constraint slot vs gold, normalized to retriever WHERE-clause effect",
    }

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    t = result["totals"]
    by_cat = {k: v["error_reduction_pct"] for k, v in result["by_category"].items()}
    click.echo(
        json.dumps(
            {
                "naive_errors": t["naive_errors"],
                "separated_errors": t["separated_errors"],
                "error_reduction_pct": t["error_reduction_pct"],
                "by_category": by_cat,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
