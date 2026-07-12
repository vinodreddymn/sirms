from collections.abc import Awaitable, Callable
from time import perf_counter

import structlog
from fastapi import Request, Response

logger = structlog.get_logger()


async def logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started_at = perf_counter()
    response = await call_next(request)
    duration_ms = round((perf_counter() - started_at) * 1000, 2)

    if request.url.path not in {"/health", "/api/v1/health"}:
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

    return response
