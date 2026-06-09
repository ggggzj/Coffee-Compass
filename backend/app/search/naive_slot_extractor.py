"""Naive 'before' slot extractor: the day-one prompt that does NOT separate vibe
terms from SQL constraints. Kept ONLY as the baseline arm of the tag-error eval
(app/eval/tag_error.py) so the resume's error-reduction number is a real A/B vs the
current separated design in app/search/slot_extractor.py. Not wired into /search.
"""

from __future__ import annotations

import json

from openai import AsyncOpenAI

from app.search.slot_extractor import ParsedQuery

# Deliberately the kind of first draft a developer writes before discovering that
# vibe words leak into hard filters: it guesses each field from keyword cues and
# does NOT require an explicit mention, so it over-fires on trap queries like
# "cheap thrills vibe" (price) or "outlet mall area" (outlet).
_PROMPT = """Extract coffee-shop search filters from the query (any language).
Return one JSON object with keys:
{{
  "semantic_query": "<short English description of what they want>",
  "has_outlet": true | false,
  "open_now": true | false,
  "price_max": 1 | 2 | 3 | 4
}}

Guidance:
- has_outlet: true when the query is about outlets, charging, power, plugs,
  laptops, working, studying, or 插座 — anything work-ish.
- open_now: true when the query mentions open, late, hours, now, available,
  finals, or 营业 — anything time/availability-ish.
- price_max: pick a number from any price/value/budget/cheap/affordable wording
  (cheap/便宜 -> 1, moderate -> 2, nicer -> 3, splurge -> 4). Default 2.
- Always fill every field with your best guess. Do not return null.

Query: {query}
"""


async def extract_naive_slots(
    *, openai_client: AsyncOpenAI, model: str, query: str
) -> ParsedQuery:
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": _PROMPT.format(query=query)}],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    payload = json.loads(response.choices[0].message.content or "{}")
    return ParsedQuery(
        semantic_query=payload.get("semantic_query", query),
        has_outlet=payload.get("has_outlet"),
        open_now=payload.get("open_now"),
        price_max=payload.get("price_max"),
    )
