from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent import router as agent_router
from app.api.cafes import router as cafes_router
from app.api.search import router as search_router
from app.observability import TimingMiddleware

app = FastAPI(title="CoffeeCompass", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-LLM-Ms", "X-Embed-Ms", "X-Pgvector-Ms", "X-Cache"],
)
app.add_middleware(TimingMiddleware)
app.include_router(search_router)
app.include_router(agent_router)
app.include_router(cafes_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
