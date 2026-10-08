"""Auth endpoint tests: register, login, refresh, /me (live database)."""
from __future__ import annotations

PASSWORD = "S3cure-Pass!"


def _register(client, email: str, password: str = PASSWORD, name: str = "Test User"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": name},
    )


def test_register_creates_account_and_returns_tokens(client, unique_email):
    email = unique_email()
    resp = _register(client, email)
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["expires_in"] > 0


def test_register_rejects_duplicate_email(client, unique_email):
    email = unique_email()
    assert _register(client, email).status_code == 201
    resp = _register(client, email)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "conflict"


def test_register_rejects_weak_password(client, unique_email):
    resp = _register(client, unique_email(), password="short")
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


def test_register_normalises_email_case(client, unique_email):
    email = unique_email()
    assert _register(client, email.upper()).status_code == 201
    # Login with the original mixed-case form must still succeed.
    resp = client.post(
        "/api/auth/login", json={"email": email.upper(), "password": PASSWORD}
    )
    assert resp.status_code == 200


def test_me_returns_profile_with_token(client, unique_email):
    email = unique_email()
    tokens = _register(client, email).json()
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == email
    assert body["role"] == "student"
    assert body["is_superuser"] is False
    assert "hashed_password" not in resp.text


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "authentication_error"


def test_me_rejects_garbage_token(client):
    resp = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"}
    )
    assert resp.status_code == 401


def test_me_rejects_refresh_token_used_as_access_token(client, unique_email):
    tokens = _register(client, unique_email()).json()
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["message"] == "Access token required"


def test_login_success_and_failure_are_uniform(client, unique_email):
    email = unique_email()
    _register(client, email)

    ok = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert ok.status_code == 200

    bad = client.post("/api/auth/login", json={"email": email, "password": "wrong-pass"})
    assert bad.status_code == 401
    message = bad.json()["error"]["message"]

    unknown = client.post(
        "/api/auth/login", json={"email": unique_email(), "password": PASSWORD}
    )
    assert unknown.status_code == 401
    # Uniform message: must not reveal whether the email exists.
    assert unknown.json()["error"]["message"] == message


def test_refresh_issues_new_pair(client, unique_email):
    tokens = _register(client, unique_email()).json()
    resp = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_refresh_rejects_access_token(client, unique_email):
    tokens = _register(client, unique_email()).json()
    resp = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["message"] == "Refresh token required"


def test_refresh_rejects_garbage_token(client):
    resp = client.post("/api/auth/refresh", json={"refresh_token": "garbage"})
    assert resp.status_code == 401
