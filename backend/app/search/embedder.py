from openai import AsyncOpenAI


class Embedder:
    def __init__(self, *, openai_client: AsyncOpenAI, model: str) -> None:
        self._client = openai_client
        self._model = model

    async def embed(self, text: str) -> list[float]:
        r = await self._client.embeddings.create(model=self._model, input=text)
        return list(r.data[0].embedding)

    async def embed_many(self, texts: list[str], *, batch_size: int = 128) -> list[list[float]]:
        """Embed many texts using batched API calls.

        The OpenAI embeddings endpoint accepts a list ``input``, so N texts cost
        ceil(N / batch_size) round-trips instead of N. This is the ingestion hot
        path: embedding 100 cafes in one call instead of 100 calls is the bulk of
        the "100 shops in under 10 minutes" budget. Order is preserved.
        """
        if not texts:
            return []
        out: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            chunk = texts[start : start + batch_size]
            r = await self._client.embeddings.create(model=self._model, input=chunk)
            # The API returns results in request order, but sort by index
            # defensively so a provider change can't silently misalign rows.
            ordered = sorted(r.data, key=lambda d: d.index)
            out.extend(list(d.embedding) for d in ordered)
        return out
