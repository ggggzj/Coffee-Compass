"""Week 2: richer review tagger using editorialSummary + up to 5 review texts."""

from __future__ import annotations

import json

from openai import AsyncOpenAI

from app.ingestion.tagger import CafeTags, _parse

# Registered alongside DB row + JSON mirror via app.eval.prompt_registry
REVIEW_TAGGER_V2_BODY = """You are an analyst who reads coffee shop metadata, Google's
editorial summary (if present), and customer reviews. Produce:
1) Structured tags about amenities and vibe (conservative — use null when uncertain).
2) A 60–110 word natural-language "ambience description" that captures the place so a
search system can match queries like "quiet study" or "first date".

Evidence is limited (often ≤5 short reviews). Weight explicit statements over guesses.
Only set has_wifi/has_outlet=true when the text clearly supports it.

Return a single JSON object with exactly these keys:
{{
  "has_wifi": true | false | null,
  "has_outlet": true | false | null,
  "noise_level": "quiet" | "moderate" | "lively" | null,
  "good_for_studying": true | false | null,
  "ambience_text": "..."
}}

Coffee shop input:
- name: {name}
- categories: {categories}
- rating: {rating}
- price_level (1=cheap, 4=expensive): {price_level}
- editorial_summary (may be empty):
{editorial_block}
- customer reviews:
{review_block}
"""


def _build_prompt_v2(
    *,
    name: str,
    categories: list[str],
    rating: float | None,
    price_level: int | None,
    editorial_summary: str | None,
    reviews: list[str],
) -> str:
    ed = (editorial_summary or "").strip()
    editorial_block = f"  {ed}" if ed else "  (none)"
    review_block = (
        "\n".join(f"  - {r}" for r in reviews[:8])
        if reviews
        else "  (no reviews available)"
    )
    return REVIEW_TAGGER_V2_BODY.format(
        name=name,
        categories=", ".join(categories) or "(none)",
        rating=rating if rating is not None else "(unknown)",
        price_level=price_level if price_level is not None else "(unknown)",
        editorial_block=editorial_block,
        review_block=review_block,
    )


async def tag_cafe_v2(
    *,
    openai_client: AsyncOpenAI,
    model: str,
    name: str,
    categories: list[str],
    rating: float | None,
    price_level: int | None,
    editorial_summary: str | None,
    reviews: list[str],
) -> CafeTags:
    prompt = _build_prompt_v2(
        name=name,
        categories=categories,
        rating=rating,
        price_level=price_level,
        editorial_summary=editorial_summary,
        reviews=reviews,
    )
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    payload = json.loads(response.choices[0].message.content or "{}")
    return _parse(payload)
