"""Content endpoint tests: events, projects, equipment, people, documents."""
from __future__ import annotations

import asyncio

import asyncpg

from app.core.config import settings
from tests.conftest import PASSWORD, create_user_sync, login, unique_email  # noqa: F401


def _make_user(client, email: str) -> str:
    """Register a student user via the API and return an access token."""
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Test User"},
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()["access_token"]


async def _insert_event(title: str = "Test Event", status_str: str = "PUBLISHED",
                         access_level: str = "PUBLIC", is_published: bool = True) -> str:
    conn = await asyncpg.connect(settings.database_url.replace("+asyncpg", ""))
    try:
        result = await conn.fetchrow(
            """
            INSERT INTO events (id, title, kind, description, venue, starts_at, ends_at,
                organizer, capacity, is_active, status, access_level, is_published,
                created_at, updated_at)
            VALUES (gen_random_uuid(), $1, 'EVENT', 'A test event', 'Test Venue',
                NOW(), NOW(), 'Test Org', 100, TRUE, $2::event_status, $3::access_level, $4, NOW(), NOW())
            RETURNING id
            """,
            title, status_str, access_level, is_published,
        )
        return str(result["id"])
    finally:
        await conn.close()


async def _insert_project(title: str = "Test Project",
                          is_published: bool = True,
                          access_level: str = "PUBLIC") -> str:
    conn = await asyncpg.connect(settings.database_url.replace("+asyncpg", ""))
    try:
        result = await conn.fetchrow(
            """
            INSERT INTO projects (id, title, summary, description, status, domain,
                technologies, is_active, is_published, started_at, access_level,
                created_at, updated_at)
            VALUES (gen_random_uuid(), $1, 'Summary', 'Description', 'active',
                'AI', 'Python', TRUE, $2, NOW(), $3::access_level, NOW(), NOW())
            RETURNING id
            """,
            title, is_published, access_level,
        )
        return str(result["id"])
    finally:
        await conn.close()


def test_list_events_shows_only_published_public(client):
    event_id =     asyncio.run(_insert_event("Public Published Event", "PUBLISHED", "PUBLIC", True))
    asyncio.run(_insert_event("Draft Event", "DRAFT", "INTERNAL", False))

    resp = client.get("/api/content/events")
    assert resp.status_code == 200
    events = resp.json()
    titles = [e["title"] for e in events]
    assert "Public Published Event" in titles
    assert "Draft Event" not in titles


def test_list_events_not_found(client):
    import uuid as _uuid
    resp = client.get(f"/api/content/events/{_uuid.uuid4()}")
    assert resp.status_code == 404


def test_create_event_requires_auth(client):
    resp = client.post("/api/content/events", json={"title": "New Event", "kind": "event"})
    assert resp.status_code == 401


def test_create_event_as_user(client, unique_email):
    token = _make_user(client, unique_email())

    resp = client.post(
        "/api/content/events",
        json={"title": "New Event", "kind": "event", "description": "A test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "New Event"
    assert body["kind"] == "event"


def test_update_event(client, unique_email):
    token = _make_user(client, unique_email())

    resp = client.post(
        "/api/content/events",
        json={"title": "Original", "kind": "event"},
        headers={"Authorization": f"Bearer {token}"},
    )
    event_id = resp.json()["id"]

    resp = client.patch(
        f"/api/content/events/{event_id}",
        json={"title": "Updated", "status": "published"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"
    assert resp.json()["status"] == "published"


def test_delete_event(client, unique_email):
    token = _make_user(client, unique_email())

    resp = client.post(
        "/api/content/events",
        json={"title": "To Delete", "kind": "event"},
        headers={"Authorization": f"Bearer {token}"},
    )
    event_id = resp.json()["id"]

    resp = client.delete(
        f"/api/content/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204


def test_list_projects_shows_only_published(client):
    asyncio.run(_insert_project("Public Project", is_published=True, access_level="PUBLIC"))
    asyncio.run(_insert_project("Hidden Project", is_published=False, access_level="INTERNAL"))

    resp = client.get("/api/content/projects")
    assert resp.status_code == 200
    projects = resp.json()
    titles = [p["title"] for p in projects]
    assert "Public Project" in titles
    assert "Hidden Project" not in titles


def test_list_equipment(client):
    resp = client.get("/api/content/equipment")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_booking_requires_auth(client):
    resp = client.post("/api/content/equipment/00000000-0000-0000-0000-000000000000/bookings",
                       json={"purpose": "test"})
    assert resp.status_code == 401


def test_create_equipment_booking(client, unique_email):
    token = _make_user(client, unique_email())

    resp = client.post(
        "/api/content/equipment",
        json={"name": "3D Printer", "category": "printer"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    eq_id = resp.json()["id"]

    resp = client.post(
        f"/api/content/equipment/{eq_id}/bookings",
        json={"purpose": "Printing project parts"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["equipment_id"] == eq_id
    assert body["status"] == "pending"


def test_search_endpoint(client, unique_email):
    token = _make_user(client, unique_email())

    client.post(
        "/api/content/projects",
        json={"title": "Searchable Project", "is_published": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    resp = client.get("/api/content/search?q=Searchable")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1


def test_departments_require_auth(client):
    resp = client.get("/api/content/departments")
    assert resp.status_code == 401
