from __future__ import annotations

import json
from dataclasses import dataclass

from openai import AsyncOpenAI

_PROMPT_TEMPLATE = """You are an analyst who reads coffee shop metadata and reviews and produces:
1) A short list of structured boolean / categorical tags about amenities and vibe.
2) A 60-90 word natural-language "ambience description" that captures the place's
character so a search system can match it against queries like "quiet place to study"
or "good first-date spot".

Be conservative. If a tag cannot be confidently determined from the input, set it to null.
Only set has_wifi=true if reviews or metadata explicitly say so. Same for has_outlet.

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
- recent reviews:
{review_block}
"""


@dataclass(frozen=True)
class CafeTags:
    has_wifi: bool | None
    has_outlet: bool | None
    noise_level: str | None
    good_for_studying: bool | None
    ambience_text: str


def _build_prompt(
    *,
    name: str,
    categories: list[str],
    rating: float | None,
    price_level: int | None,
    reviews: list[str],
) -> str:
    review_block = (
        "\n".join(f"  - {r}" for r in reviews[:8]) if reviews else "  (no reviews available)"
    )
    return _PROMPT_TEMPLATE.format(
        name=name,
        categories=", ".join(categories) or "(none)",
        rating=rating if rating is not None else "(unknown)",
        price_level=price_level if price_level is not None else "(unknown)",
        review_block=review_block,
    )


def _parse(payload: dict) -> CafeTags:
    return CafeTags(
        has_wifi=payload.get("has_wifi"),
        has_outlet=payload.get("has_outlet"),
        noise_level=payload.get("noise_level"),
        good_for_studying=payload.get("good_for_studying"),
        ambience_text=payload.get("ambience_text", ""),
    )


async def tag_cafe(
    *,
    openai_client: AsyncOpenAI,
    model: str,
    name: str,
    categories: list[str],
    rating: float | None,
    price_level: int | None,
    reviews: list[str],
) -> CafeTags:
    prompt = _build_prompt(
        name=name,
        categories=categories,
        rating=rating,
        price_level=price_level,
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
