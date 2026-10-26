"""Integration test for GET /api/health."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_reports_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "Vytal"
    assert isinstance(body["version"], str) and body["version"]


def test_unknown_route_returns_404_without_internal_details():
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert "Traceback" not in response.text
