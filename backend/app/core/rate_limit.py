"""Rate limiting (slowapi).

A single process-wide ``Limiter`` keyed by client IP. Default limits apply to
every route unless a route declares its own ``@limiter.limit(...)`` (the
middleware steps aside then and lets the decorator handle it) or is explicitly
exempted (e.g. health probes). All limits come from ``backend/.env``.
"""
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
    headers_enabled=True,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return 429 responses in the application's standard error envelope.

    Kept synchronous so the slowapi middleware can invoke it directly.
    """
    message = str(getattr(exc, "detail", None) or "Rate limit exceeded")
    response = JSONResponse(
        status_code=429,
        content={"error": {"code": "rate_limited", "message": message}},
    )
    # Best-effort X-RateLimit-* headers; requires the limiter + request state.
    try:
        response = request.app.state.limiter._inject_headers(
            response, request.state.view_rate_limit
        )
    except Exception:  # noqa: BLE001 - never fail the response over headers
        pass
    return response