"""FastAPI application entry point.

Run from ``backend/``:

    uvicorn app.main:app --reload

Wires together, in order: logging, lifespan (startup/shutdown), rate limiting,
CORS, JSON error handlers, and the API routers.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import __version__
from app.ai.registry import reset_providers, validate_gemini_models
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.db.session import dispose_engine
from app.routes import auth as auth_routes
from app.routes import health as health_routes

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201 - FastAPI signature
    """Startup: logging + optional Gemini model verification. Shutdown: cleanup."""
    configure_logging()
    logger.info(
        "startup",
        version=__version__,
        environment=settings.environment,
        debug=settings.debug,
    )
    if settings.gemini_api_key and settings.gemini_verify_models_on_start:
        try:
            result = await validate_gemini_models()
            logger.info("gemini_model_check", result=result)
        except Exception as exc:  # noqa: BLE001 - startup must not fail on this
            logger.warning("gemini_model_check_failed", error=str(exc))
    yield
    logger.info("shutdown")
    await reset_providers()
    await dispose_engine()


def create_app() -> FastAPI:
    """Application factory (used by tests and by ``app.main:app``)."""
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        lifespan=lifespan,
        # Interactive docs are development aids; hidden outside debug mode.
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # --- rate limiting -----------------------------------------------------
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    # Applies default limits to undecorated routes; decorated routes handle
    # themselves and exempt routes (health) are skipped entirely.
    app.add_middleware(SlowAPIMiddleware)

    # --- CORS (outermost, so even 429/500 responses carry CORS headers) ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- JSON error envelopes ---------------------------------------------
    register_exception_handlers(app)

    # --- routers -----------------------------------------------------------
    app.include_router(health_routes.router)
    app.include_router(auth_routes.router, prefix=f"{settings.api_prefix}/auth")

    return app


app = create_app()