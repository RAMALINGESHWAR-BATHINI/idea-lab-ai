"""Shared test fixtures.

Environment MUST be configured before the application is imported because
``Settings`` is a module-level singleton created on first import.
"""
from __future__ import annotations

import asyncio
import os
import uuid

# ---- test environment (before any app import) -----------------------------
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
# Keep limits high so suites never trip the limiter accidentally.
os.environ.setdefault("RATE_LIMIT_DEFAULT", "10000/minute")
os.environ.setdefault("RATE_LIMIT_AUTH", "10000/minute")
os.environ.setdefault("GEMINI_VERIFY_MODELS_ON_START", "false")

import asyncpg  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402

# All test accounts live in this namespace so cleanup cannot touch real data.
TEST_EMAIL_PREFIX = "test"


@pytest.fixture()
def client() -> TestClient:
    """Session-bound HTTP client that runs the ASGI lifespan."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def unique_email():
    """Factory for collision-free test emails in the ``test.`` namespace."""

    def _make(prefix: str = TEST_EMAIL_PREFIX) -> str:
        return f"{prefix}.{uuid.uuid4().hex[:12]}@example.com"

    return _make


async def _purge_async() -> None:
    """Delete every account (and audit row) in the test namespace."""
    dsn = settings.database_url.replace("+asyncpg", "")
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute(
            "DELETE FROM audit_logs WHERE actor LIKE $1",
            f"{TEST_EMAIL_PREFIX}.%@example.com",
        )
        await conn.execute(
            "DELETE FROM users WHERE email LIKE $1",
            f"{TEST_EMAIL_PREFIX}.%@example.com",
        )
    finally:
        await conn.close()


def purge_test_data() -> None:
    """Synchronous helper to remove all test accounts (idempotent)."""
    asyncio.run(_purge_async())


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Remove test accounts after every test that ran."""
    yield
    purge_test_data()
