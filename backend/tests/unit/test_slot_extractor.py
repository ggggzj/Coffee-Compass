import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.search.slot_extractor import ParsedQuery, extract_slots


@pytest.mark.asyncio
async def test_extracts_outlet_and_price():
    payload = {
        "semantic_query": "quiet, good for reading",
        "has_outlet": True,
        "open_now": None,
        "price_max": 2,
    }
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)

    parsed = await extract_slots(
        openai_client=client, model="gpt-4o-mini", query="安静适合读书有插座 别太贵"
    )

    assert parsed == ParsedQuery(
        semantic_query="quiet, good for reading",
        has_outlet=True,
        open_now=None,
        price_max=2,
    )


@pytest.mark.asyncio
async def test_open_now_extracted():
    payload = {
        "semantic_query": "cafes near campus",
        "has_outlet": None,
        "open_now": True,
        "price_max": None,
    }
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    parsed = await extract_slots(
        openai_client=client, model="gpt-4o-mini", query="open now near USC"
    )
    assert parsed.open_now is True


@pytest.mark.asyncio
async def test_no_filters_returns_only_semantic():
    payload = {
        "semantic_query": "study spot",
        "has_outlet": None,
        "open_now": None,
        "price_max": None,
    }
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    parsed = await extract_slots(openai_client=client, model="gpt-4o-mini", query="study spot")
    assert parsed.has_outlet is None
    assert parsed.price_max is None
