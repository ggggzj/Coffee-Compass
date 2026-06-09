import time

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.observability import Timer, TimingMiddleware


def test_timer_measures_elapsed():
    with Timer() as t:
        time.sleep(0.01)
    assert t.ms >= 9.0  # ~10ms, allow scheduler slop


def test_timer_zero_before_use():
    t = Timer()
    assert t.ms == 0.0


@pytest.mark.asyncio
async def test_middleware_adds_timing_headers():
    app = FastAPI()
    app.add_middleware(TimingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/ping")

    assert r.status_code == 200
    assert "X-Request-Id" in r.headers
    assert "X-Total-Ms" in r.headers
    float(r.headers["X-Total-Ms"])  # must be parseable as a number


@pytest.mark.asyncio
async def test_middleware_preserves_inbound_request_id():
    app = FastAPI()
    app.add_middleware(TimingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/ping", headers={"x-request-id": "abc123"})

    assert r.headers["X-Request-Id"] == "abc123"
