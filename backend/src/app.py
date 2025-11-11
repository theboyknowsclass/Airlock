from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .api.version import router as version_router, ErrorResponse
from .core.limiter import limiter
from .telemetry.version_logging import (
    log_https_violation,
    log_rate_limit_block,
)


async def _https_enforcement_middleware(
    request: Request, call_next
):  # type: ignore[override]
    forwarded_proto = request.headers.get("x-forwarded-proto")
    scheme = forwarded_proto or request.url.scheme
    if scheme.lower() != "https":
        request_id = request.headers.get("x-request-id") or str(uuid4())
        log_https_violation(
            request_id=request_id, client_ip=get_remote_address(request)
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "https_required",
                "message": "HTTPS is required for this endpoint.",
            },
        )
    return await call_next(request)


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    limit = getattr(exc, "limit", None)
    limit_description = getattr(limit, "display", "60 per minute")
    log_rate_limit_block(
        request_id=request_id,
        client_ip=get_remote_address(request),
        limit=str(limit_description),
    )
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "rate_limited",
            "message": "Too many requests. Please retry later.",
        },
    )
    retry_after = getattr(exc, "retry_after", None)
    if retry_after is not None:
        response.headers["Retry-After"] = str(retry_after)
    return response


def create_app() -> FastAPI:
    app = FastAPI(title="Initial Site Backend")
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.middleware("http")(_https_enforcement_middleware)
    app.include_router(version_router, prefix="/api")
    return app


app = create_app()

