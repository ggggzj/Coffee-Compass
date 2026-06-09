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


@pytest.mark.asyncio
async def test_embed_many_one_call_preserves_order():
    # Return data out of order to prove we sort by .index, not list position.
    d0 = MagicMock(embedding=[0.1] * 1536, index=0)
    d1 = MagicMock(embedding=[0.2] * 1536, index=1)
    response = MagicMock()
    response.data = [d1, d0]
    fake_client = MagicMock()
    fake_client.embeddings.create = AsyncMock(return_value=response)

    e = Embedder(openai_client=fake_client, model="m")
    out = await e.embed_many(["a", "b"])

    assert len(out) == 2
    assert out[0][0] == 0.1
    assert out[1][0] == 0.2
    fake_client.embeddings.create.assert_awaited_once_with(model="m", input=["a", "b"])


@pytest.mark.asyncio
async def test_embed_many_chunks_into_batches():
    calls: list[list[str]] = []

    async def fake_create(*, model, input):
        calls.append(input)
        data = [MagicMock(embedding=[float(i)] * 3, index=i) for i in range(len(input))]
        resp = MagicMock()
        resp.data = data
        return resp

    fake_client = MagicMock()
    fake_client.embeddings.create = AsyncMock(side_effect=fake_create)

    e = Embedder(openai_client=fake_client, model="m")
    out = await e.embed_many(["a", "b", "c"], batch_size=2)

    assert len(out) == 3
    assert calls == [["a", "b"], ["c"]]  # two batched calls, not three


@pytest.mark.asyncio
async def test_embed_many_empty_makes_no_call():
    fake_client = MagicMock()
    fake_client.embeddings.create = AsyncMock()
    e = Embedder(openai_client=fake_client, model="m")
    assert await e.embed_many([]) == []
    fake_client.embeddings.create.assert_not_awaited()
