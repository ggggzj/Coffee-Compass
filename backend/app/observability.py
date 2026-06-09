from __future__ import annotations

import time
import uuid
from types import TracebackType

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = structlog.get_logger()


class Timer:
    """Context manager that records wall-clock elapsed time in milliseconds.

    >>> with Timer() as t:
    ...     do_work()
    >>> t.ms  # elapsed milliseconds
    """

    def __init__(self) -> None:
        self.ms: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> Timer:
        self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.ms = (time.perf_counter() - self._start) * 1000.0


class TimingMiddleware(BaseHTTPMiddleware):
    """Attach a request id and total-latency header to every response.

    Per-stage timings (LLM, embedding, pgvector) are added by the /search
    handler itself; this middleware owns the end-to-end ``X-Total-Ms`` number
    that the k6 load test reads to compute p50/p95.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        start = time.perf_counter()
        response = await call_next(request)
        total_ms = (time.perf_counter() - start) * 1000.0
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Total-Ms"] = f"{total_ms:.1f}"
        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            request_id=request_id,
            total_ms=round(total_ms, 1),
        )
        return response
