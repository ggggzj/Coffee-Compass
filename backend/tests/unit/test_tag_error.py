"""Tag-error harness: scoring math (no keys) + Chinese I/O plumbing (mocked LLM)."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.eval.tag_error import (
    reduction_pct,
    run_tag_error_eval,
    score_predictions,
    slot_errors,
)
from app.eval.tag_error_set import GoldSlots, TagErrorItem, TagErrorSet, load_tag_error_set
from app.search.slot_extractor import ParsedQuery, extract_slots


def _pq(has_outlet=None, open_now=None, price_max=None, semantic="x"):
    return ParsedQuery(
        semantic_query=semantic,
        has_outlet=has_outlet,
        open_now=open_now,
        price_max=price_max,
    )


# --- slot_errors: mirrors the retriever's WHERE-clause behavior -----------------


def test_perfect_match_has_no_errors():
    gold = GoldSlots(has_outlet=True, open_now=True, price_max=1)
    assert slot_errors(gold, _pq(has_outlet=True, open_now=True, price_max=1)) == []


def test_over_firing_counts_each_wrong_filter():
    # gold asks for nothing; naive sets all three -> three wrong filters.
    gold = GoldSlots()
    wrong = slot_errors(gold, _pq(has_outlet=True, open_now=True, price_max=2))
    assert set(wrong) == {"has_outlet", "open_now", "price_max"}


def test_has_outlet_false_is_a_distinct_filter_error():
    # retriever filters whenever has_outlet is not None, so False (no-outlet) != None.
    assert slot_errors(GoldSlots(), _pq(has_outlet=False)) == ["has_outlet"]


def test_open_now_false_is_normalized_to_no_filter():
    # retriever only filters open_now when True, so False == None in effect: NOT an error.
    assert slot_errors(GoldSlots(), _pq(open_now=False)) == []


def test_open_now_true_against_null_gold_is_an_error():
    assert slot_errors(GoldSlots(), _pq(open_now=True)) == ["open_now"]


def test_wrong_price_value_is_an_error():
    assert slot_errors(GoldSlots(price_max=1), _pq(price_max=3)) == ["price_max"]


def test_missed_constraint_is_an_error():
    assert slot_errors(GoldSlots(has_outlet=True), _pq(has_outlet=None)) == ["has_outlet"]


# --- reduction_pct --------------------------------------------------------------


def test_reduction_pct_basic():
    assert reduction_pct(10, 2) == 80.0


def test_reduction_pct_zero_baseline_is_undefined():
    assert reduction_pct(0, 0) is None


# --- score_predictions: aggregate + per-category --------------------------------


def test_score_predictions_aggregates_and_reduces():
    items = [
        TagErrorItem(
            id="a", lang="en", category="trap", query="cheap thrills vibe", gold=GoldSlots()
        ),
        TagErrorItem(
            id="b", lang="en", category="constraint", query="outlets please",
            gold=GoldSlots(has_outlet=True),
        ),
    ]
    # naive over-fires on the trap (3 wrong) and nails the real constraint (0 wrong) = 3.
    naive = [_pq(has_outlet=True, open_now=True, price_max=2), _pq(has_outlet=True)]
    # separated stays clean on the trap (0) and nails the constraint (0) = 0.
    separated = [_pq(), _pq(has_outlet=True)]

    out = score_predictions(items, naive, separated)

    assert out["totals"]["naive_errors"] == 3
    assert out["totals"]["separated_errors"] == 0
    assert out["totals"]["error_reduction_pct"] == 100.0
    assert out["totals"]["slots_scored"] == 6
    assert out["by_category"]["trap"]["naive_errors"] == 3
    assert out["by_category"]["constraint"]["naive_errors"] == 0


@pytest.mark.asyncio
async def test_run_tag_error_eval_with_injected_extractors():
    items = [
        TagErrorItem(
            id="a", lang="zh", category="trap", query="插画风格的咖啡馆", gold=GoldSlots()
        ),
    ]
    tag_set = TagErrorSet(version=1, items=items)

    async def naive(_q):
        return _pq(has_outlet=True)  # trap: 插 -> wrongly sets outlet

    async def separated(_q):
        return _pq()  # separated design keeps it out of SQL

    out = await run_tag_error_eval(tag_set=tag_set, naive=naive, separated=separated)
    assert out["totals"]["naive_errors"] == 1
    assert out["totals"]["separated_errors"] == 0


# --- the bundled set loads and is internally consistent -------------------------


def test_bundled_tag_error_set_loads_and_has_chinese():
    ts = load_tag_error_set()
    assert len(ts.items) >= 20
    langs = {i.lang for i in ts.items}
    assert langs == {"en", "zh"}
    # every 'vibe' and 'trap' query must have all-null gold (the separation invariant).
    for i in ts.items:
        if i.category in {"vibe", "trap"}:
            assert i.gold == GoldSlots(), f"{i.id} should have no hard constraint"


# --- Chinese I/O plumbing: extract_slots round-trips unicode + zh-trigger JSON ---


@pytest.mark.asyncio
async def test_extract_slots_handles_chinese_query_and_unicode_json():
    payload = {
        "semantic_query": "quiet, good for reading",
        "has_outlet": True,
        "open_now": True,
        "price_max": 1,
    }
    response = MagicMock()
    response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(payload, ensure_ascii=False)))
    ]
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)

    parsed = await extract_slots(
        openai_client=client, model="gpt-4o-mini", query="安静有插座 现在营业 便宜"
    )

    # the Chinese query is passed through verbatim to the model...
    sent = client.chat.completions.create.await_args.kwargs["messages"][0]["content"]
    assert "安静有插座 现在营业 便宜" in sent
    # ...and zh-trigger filters parse into the typed schema.
    assert parsed == ParsedQuery(
        semantic_query="quiet, good for reading",
        has_outlet=True,
        open_now=True,
        price_max=1,
    )
