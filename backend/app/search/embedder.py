from openai import AsyncOpenAI


class Embedder:
    def __init__(self, *, openai_client: AsyncOpenAI, model: str) -> None:
        self._client = openai_client
        self._model = model

    async def embed(self, text: str) -> list[float]:
        r = await self._client.embeddings.create(model=self._model, input=text)
        return list(r.data[0].embedding)
