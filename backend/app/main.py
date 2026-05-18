from fastapi import FastAPI

from app.api.search import router as search_router

app = FastAPI(title="CoffeeCompass", version="0.1.0")
app.include_router(search_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
