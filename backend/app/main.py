"""FastAPI application entry point.

Run from ``backend/``:

    uvicorn app.main:app --reload

Wires together, in order: logging, lifespan (startup/shutdown), rate limiting,
CORS, JSON error handlers, and the API routers.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
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
from app.routes import admin as admin_routes
from app.routes import auth as auth_routes
from app.routes import chat as chat_routes
from app.routes import content as content_routes
from app.routes import devices as device_routes
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

    # --- Security headers ----------------------------------------------------
    @app.middleware("http")
    async def _set_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    # --- JSON error envelopes ---------------------------------------------
    register_exception_handlers(app)

    # --- routers -----------------------------------------------------------
    app.include_router(health_routes.router)
    app.include_router(auth_routes.router, prefix=f"{settings.api_prefix}/auth")
    app.include_router(content_routes.router, prefix=f"{settings.api_prefix}/content")
    app.include_router(chat_routes.router, prefix=f"{settings.api_prefix}/ai")
    app.include_router(admin_routes.router, prefix=f"{settings.api_prefix}/admin")
    app.include_router(device_routes.router, prefix=f"{settings.api_prefix}/devices")

    return app


app = create_app()