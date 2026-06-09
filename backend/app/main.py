from fastapi import FastAPI

from app.api.search import router as search_router
from app.observability import TimingMiddleware

app = FastAPI(title="CoffeeCompass", version="0.1.0")
app.add_middleware(TimingMiddleware)
app.include_router(search_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
