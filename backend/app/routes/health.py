"""Liveness, readiness and service-info endpoints (public, rate-limit exempt)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.core.config import settings
from app.core.logging import get_logger
from app.core.rate_limit import limiter
from app.db.session import get_session

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/")
@limiter.exempt
async def service_root() -> dict:
    """Basic service identification (no configuration details)."""
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs_url": "/docs" if settings.debug else None,
    }


@router.get("/health")
@limiter.exempt
async def health() -> dict:
    """Liveness probe: process is up and serving requests. Touches no deps."""
    return {"status": "ok", "environment": settings.environment}


@router.get("/health/ready", response_model=None)
@limiter.exempt
async def readiness(session: AsyncSession = Depends(get_session)) -> dict | JSONResponse:
    """Readiness probe: verifies the database is reachable."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - probe must report, not crash
        logger.warning("readiness_db_failed", error=str(exc))
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "not_ready",
                    "message": "Database is unavailable",
                }
            },
        )
    return {"status": "ready", "database": "ok"}