"""Tests for password reset flow."""
from __future__ import annotations

PASSWORD = "S3cure-Pass!"


def test_password_reset_request_returns_token_in_debug(client, unique_email):
    """In debug mode, the reset token is returned so tests can use it."""
    email = unique_email()
    client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Reset Test"},
    )

    resp = client.post(
        "/api/auth/password-reset/request",
        json={"email": email},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "reset_token" in body  # debug mode


def test_password_reset_confirm_changes_password(client, unique_email):
    email = unique_email()
    client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Reset Test"},
    )

    resp = client.post(
        "/api/auth/password-reset/request",
        json={"email": email},
    )
    token = resp.json()["reset_token"]

    resp = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "New-Pass-456!"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # Old password should fail
    resp = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 401

    # New password should work
    resp = client.post(
        "/api/auth/login", json={"email": email, "password": "New-Pass-456!"}
    )
    assert resp.status_code == 200


def test_password_reset_rejects_garbage_token(client):
    resp = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": "garbage", "new_password": "New-Pass-456!"},
    )
    assert resp.status_code == 401


def test_password_reset_rejects_short_password(client, unique_email):
    email = unique_email()
    client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Reset Test"},
    )

    resp = client.post(
        "/api/auth/password-reset/request",
        json={"email": email},
    )
    token = resp.json()["reset_token"]

    resp = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "short"},
    )
    assert resp.status_code == 422
