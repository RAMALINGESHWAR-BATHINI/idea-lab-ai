"""Health / readiness / service-info endpoint tests (no database writes)."""
from __future__ import annotations


def test_root_returns_service_info(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "IdeaLab AI"
    assert body["version"]


def test_health_liveness(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health_ready_reports_database(client):
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"


def test_docs_available_in_debug(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/health" in paths
    assert "/api/auth/register" in paths
    assert "/api/auth/login" in paths
    assert "/api/auth/me" in paths
