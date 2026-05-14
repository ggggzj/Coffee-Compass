import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ingestion.tagger import CafeTags, tag_cafe


@pytest.mark.asyncio
async def test_tag_cafe_calls_openai_and_parses_json():
    fake_payload = {
        "has_wifi": True,
        "has_outlet": True,
        "noise_level": "quiet",
        "good_for_studying": True,
        "ambience_text": (
            "A calm specialty cafe steps from USC. Students love the abundant outlets, "
            "fast wifi, and quiet corners. Pastries are a highlight."
        ),
    }
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=json.dumps(fake_payload)))]
    fake_client = MagicMock()
    fake_client.chat.completions.create = AsyncMock(return_value=response)

    tags = await tag_cafe(
        openai_client=fake_client,
        model="gpt-4o-mini",
        name="Bricks & Scones",
        categories=["cafe", "bakery"],
        rating=4.5,
        price_level=2,
        reviews=["Quiet and great outlets.", "Wifi is fast."],
    )

    assert tags == CafeTags(
        has_wifi=True,
        has_outlet=True,
        noise_level="quiet",
        good_for_studying=True,
        ambience_text=fake_payload["ambience_text"],
    )
    args = fake_client.chat.completions.create.call_args
    assert args.kwargs["model"] == "gpt-4o-mini"
    assert args.kwargs["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_tag_cafe_handles_missing_fields_gracefully():
    response = MagicMock()
    response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({"ambience_text": "Cozy place."})))
    ]
    fake_client = MagicMock()
    fake_client.chat.completions.create = AsyncMock(return_value=response)
    tags = await tag_cafe(
        openai_client=fake_client,
        model="gpt-4o-mini",
        name="X",
        categories=[],
        rating=None,
        price_level=None,
        reviews=[],
    )
    assert tags.has_wifi is None
    assert tags.has_outlet is None
    assert tags.noise_level is None
    assert tags.good_for_studying is None
    assert tags.ambience_text == "Cozy place."
