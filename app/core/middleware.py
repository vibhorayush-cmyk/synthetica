"""Request identity, access logging, and conservative local rate limiting."""

import logging
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from time import monotonic, perf_counter
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.settings import Settings


logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach request IDs and emit structured access logs."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", uuid4().hex)
        request.state.request_id = request_id
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                },
            )
            raise
        duration_ms = round((perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_complete",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply an in-memory IP rate limit to mutating API requests.

    Deployments with multiple workers should replace this adapter with a shared
    Redis-backed limiter while retaining the same middleware contract.
    """

    def __init__(self, app, settings: Settings) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._limit = settings.rate_limit_requests
        self._window = settings.rate_limit_window_seconds
        self._generation_limit = settings.generation_rate_limit_requests
        self._generation_window = settings.generation_rate_limit_window_seconds
        self._requests: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        is_generation = request.method == "POST" and request.url.path.rstrip().endswith(
            "/generate"
        )
        scope = "generation" if is_generation else "mutating"
        limit = self._generation_limit if is_generation else self._limit
        window = self._generation_window if is_generation else self._window
        now = monotonic()
        timestamps = self._requests[(client, scope)]
        while timestamps and now - timestamps[0] >= window:
            timestamps.popleft()
        if len(timestamps) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Too many generation requests. Please wait before trying again."
                        if is_generation
                        else "Rate limit exceeded. Please wait before trying again."
                    )
                },
                headers={"Retry-After": str(window)},
            )
        timestamps.append(now)
        return await call_next(request)
