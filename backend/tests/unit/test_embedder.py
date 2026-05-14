from unittest.mock import AsyncMock, MagicMock

import pytest

from app.search.embedder import Embedder


@pytest.mark.asyncio
async def test_embed_returns_floats():
    response = MagicMock()
    response.data = [MagicMock(embedding=[0.1] * 1536)]
    fake_client = MagicMock()
    fake_client.embeddings.create = AsyncMock(return_value=response)
    e = Embedder(openai_client=fake_client, model="text-embedding-3-small")
    v = await e.embed("quiet study spot")
    assert len(v) == 1536
    assert all(isinstance(x, float) for x in v)
    fake_client.embeddings.create.assert_awaited_once_with(
        model="text-embedding-3-small", input="quiet study spot"
    )
