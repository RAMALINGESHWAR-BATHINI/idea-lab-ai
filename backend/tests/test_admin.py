"""Admin endpoint tests: users, roles, permissions, invitations, devices."""
from __future__ import annotations

from tests.conftest import PASSWORD, create_user_sync, login, unique_email  # noqa: F401


def _make_superuser(client, email: str) -> str:
    """Create a superuser via direct DB insert and return an access token."""
    create_user_sync(email, superuser=True)
    return login(client, email)


def _make_student(client, email: str) -> str:
    """Create a student user via API register and return an access token."""
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Test Student"},
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()["access_token"]


def test_list_users_requires_permission(client, unique_email):
    token = _make_student(client, unique_email())
    resp = client.get(
        "/api/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403


def test_list_users_as_superuser(client, unique_email):
    token = _make_superuser(client, unique_email())
    resp = client.get(
        "/api/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    users = resp.json()
    assert len(users) >= 1


def test_list_roles_requires_permission(client, unique_email):
    token = _make_student(client, unique_email())
    resp = client.get(
        "/api/admin/roles", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403


def test_list_roles_as_superuser(client, unique_email):
    token = _make_superuser(client, unique_email())
    resp = client.get(
        "/api/admin/roles", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    roles = resp.json()
    role_names = [r["name"] for r in roles]
    assert "admin" in role_names
    assert "student" in role_names


def test_list_permissions_as_superuser(client, unique_email):
    token = _make_superuser(client, unique_email())
    resp = client.get(
        "/api/admin/permissions", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    perms = resp.json()
    perm_names = [p["name"] for p in perms]
    assert "events.create" in perm_names
    assert "web.search" in perm_names


def test_create_invitation_as_admin(client, unique_email):
    token = _make_superuser(client, unique_email())
    resp = client.post(
        "/api/admin/invitations",
        json={"email": "invitee@example.com", "role_name": "faculty", "max_uses": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["used_count"] == 0


def test_create_device_token_as_admin(client, unique_email):
    token = _make_superuser(client, unique_email())
    resp = client.post(
        "/api/admin/devices",
        json={"name": "Test Device", "permissions": ["events.read"], "access_level": "public"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Test Device"
    assert body["permissions"] == ["events.read"]
    assert body["is_active"] is True


def test_list_devices_as_admin(client, unique_email):
    token = _make_superuser(client, unique_email())
    resp = client.get(
        "/api/admin/devices", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_audit_logs_as_admin(client, unique_email):
    """Logins generate audit entries that an admin can read."""
    email = unique_email()
    token = _make_superuser(client, email)
    resp = client.get(
        "/api/admin/audit-logs", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    logs = resp.json()
    assert any(l["action"] == "auth.login" for l in logs)


def test_settings_as_admin(client, unique_email):
    token = _make_superuser(client, unique_email())
    resp = client.get(
        "/api/admin/settings", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
