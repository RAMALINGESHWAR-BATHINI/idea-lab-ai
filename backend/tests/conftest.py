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
os.environ.setdefault("RATE_LIMIT_DEFAULT", "10000/minute")
os.environ.setdefault("RATE_LIMIT_AUTH", "10000/minute")
os.environ.setdefault("GEMINI_VERIFY_MODELS_ON_START", "false")

import asyncpg  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402

TEST_EMAIL_PREFIX = "test"
PASSWORD = "S3cure-Pass!"

# Raw asyncpg connection string (no asyncpg async lib)
_DSN = settings.database_url.replace("+asyncpg", "")


@pytest.fixture(scope="session", autouse=True)
def ensure_reference_data():
    """Run bootstrap once per test session to populate roles and permissions."""
    _run_bootstrap()
    yield


def _run_bootstrap():
    """Bootstrap using a raw asyncpg connection (outside SQLAlchemy pool)."""
    asyncio.run(_bootstrap_async())


async def _bootstrap_async() -> None:
    """Insert default roles and permissions using raw SQL (no ORM)."""
    conn = await asyncpg.connect(_DSN)
    try:
        # Check if roles already exist
        existing = await conn.fetchval("SELECT COUNT(*) FROM roles")
        if existing > 0:
            return

        role_names = ["admin", "student", "faculty", "staff", "idealab_member",
                      "global_admin", "idealab_admin", "chief_mentor",
                      "faculty_coordinator", "tech_guru", "student_coordinator",
                      "student_ambassador", "contributor", "public_visitor"]

        for i, name in enumerate(role_names):
            await conn.execute(
                "INSERT INTO roles (id, name, description, is_system, created_at, updated_at) "
                "VALUES (gen_random_uuid(), $1, $2, TRUE, NOW(), NOW()) "
                "ON CONFLICT (name) DO NOTHING",
                name, f"Role: {name}",
            )

        # Insert permissions
        permissions = [
            ("events.read", "Read event records"),
            ("events.create", "Create event drafts"),
            ("events.update", "Update event records"),
            ("events.publish", "Publish events"),
            ("events.review", "Review and approve events"),
            ("projects.read", "Read project records"),
            ("projects.create", "Create project drafts"),
            ("projects.update", "Update project records"),
            ("projects.publish", "Publish projects"),
            ("projects.review", "Review and approve projects"),
            ("people.read", "Read people profiles"),
            ("people.manage", "Manage people profiles"),
            ("equipment.read", "Read equipment records"),
            ("equipment.manage", "Manage equipment inventory"),
            ("equipment.book", "Book equipment"),
            ("equipment.approve_booking", "Approve equipment bookings"),
            ("documents.upload", "Upload documents"),
            ("documents.read", "Read documents"),
            ("documents.manage", "Manage documents"),
            ("ai.tools.execute", "Execute AI tools"),
            ("ai.tools.execute_sensitive", "Execute sensitive AI actions"),
            ("ai.chat", "Use the AI chat interface"),
            ("ai.voice", "Use voice interface"),
            ("users.invite", "Invite users"),
            ("users.manage", "Manage user accounts"),
            ("users.deactivate", "Deactivate user accounts"),
            ("roles.assign", "Assign roles to users"),
            ("roles.manage", "Manage roles and permissions"),
            ("audit.read", "Read audit logs"),
            ("reports.export", "Export reports"),
            ("reports.read", "Read reports"),
            ("system.settings.manage", "Manage system settings"),
            ("devices.manage", "Manage device tokens"),
            ("devices.register", "Register new devices"),
            ("invitations.manage", "Create and manage invitations"),
            ("invitations.redeem", "Redeem access codes"),
            ("access_grants.read", "Read access grants"),
            ("access_grants.manage", "Manage access grants"),
            ("web.search", "Perform web searches"),
            ("web.fetch", "Fetch web pages"),
        ]

        for name, desc in permissions:
            await conn.execute(
                "INSERT INTO permissions (id, name, description, created_at, updated_at) "
                "VALUES (gen_random_uuid(), $1, $2, NOW(), NOW()) "
                "ON CONFLICT (name) DO NOTHING",
                name, desc,
            )

        # Assign admin all permissions
        admin_row = await conn.fetchrow("SELECT id FROM roles WHERE name = 'admin'")
        for name, _ in permissions:
            perm_row = await conn.fetchrow("SELECT id FROM permissions WHERE name = $1", name)
            if admin_row and perm_row:
                await conn.execute(
                    "INSERT INTO role_permissions (role_id, permission_id) "
                    "VALUES ($1::uuid, $2::uuid) ON CONFLICT DO NOTHING",
                    admin_row["id"], perm_row["id"],
                )

    finally:
        await conn.close()


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


async def _create_user_async(email: str, role_name: str | None = None, superuser: bool = False) -> str:
    """Insert a user directly via asyncpg (separate connection, no pool issues)."""
    conn = await asyncpg.connect(_DSN)
    try:
        role_id = None
        if role_name:
            row = await conn.fetchrow("SELECT id FROM roles WHERE name = $1", role_name)
            role_id = str(row["id"]) if row else None

        await conn.execute(
            "INSERT INTO users (id, email, hashed_password, full_name, role_id, "
            "is_active, is_superuser, is_email_verified, created_at, updated_at) "
            "VALUES (gen_random_uuid(), $1, $2, $3, $4::uuid, TRUE, $5, TRUE, NOW(), NOW())",
            email, hash_password(PASSWORD), "Test User",
            role_id, superuser,
        )
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
        return str(row["id"])
    finally:
        await conn.close()


def create_user_sync(email: str, role_name: str | None = None, superuser: bool = False) -> str:
    """Sync wrapper for creating test users via direct DB insert."""
    return asyncio.run(_create_user_async(email, role_name, superuser))


def login(client: TestClient, email: str) -> str:
    """Log in as a previously created user and return the access token."""
    resp = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 200, resp.json()
    return resp.json()["access_token"]


async def _purge_async() -> None:
    """Delete every account (and audit row) in the test namespace."""
    conn = await asyncpg.connect(_DSN)
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
