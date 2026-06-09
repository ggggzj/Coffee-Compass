from __future__ import annotations

import json
from dataclasses import dataclass

from openai import AsyncOpenAI

_PROMPT = """You convert a coffee-shop search query (any language) into a structured filter.
Return a single JSON object with exactly these keys:
{{
  "semantic_query": "<English phrase capturing the vibe / mood / use case, suitable for embedding>",
  "has_outlet": true | false | null,
  "open_now": true | false | null,
  "price_max": 1 | 2 | 3 | 4 | null
}}

Rules:
- Put vibe descriptors ("quiet", "good for reading", "cozy", "first-date")
  into semantic_query in ENGLISH.
- ONLY set has_outlet=true if the user explicitly asks for outlets / charging / 插座.
- ONLY set open_now=true if the user explicitly says open now / 营业中 / 现在开门.
- ONLY set price_max if the user mentions cheap / budget / 便宜 / under $X / $$. Map:
  cheap / 便宜 / $ → 1; moderate / $$ → 2; pricey / $$$ → 3.
- If a filter is not mentioned, set it to null (DO NOT guess).

Query: {query}
"""


@dataclass(frozen=True)
class ParsedQuery:
    semantic_query: str
    has_outlet: bool | None
    open_now: bool | None
    price_max: int | None


async def extract_slots(
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
