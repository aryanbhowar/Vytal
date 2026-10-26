"""Integration tests for the health, readiness and model-status endpoints."""

import shutil


def test_health_endpoint_reports_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "Vytal"
    assert isinstance(body["version"], str) and body["version"]


def test_unknown_route_returns_404_without_internal_details(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert "Traceback" not in response.text


def test_ready_when_both_models_load(client):
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json() == {"ready": True, "models": {"heart": True, "respiratory": True}}


def test_models_status_reports_real_evaluation_figures(client):
    models = {m["model_id"]: m for m in client.get("/api/models/status").json()["models"]}
    assert set(models) == {"heart", "respiratory"}
    for model in models.values():
        assert model["available"] is True
        assert model["training_years"] == [2022, 2023, 2024]
        assert 0.5 < model["evaluation"]["roc_auc"] < 1
        assert 0 < model["survey_prevalence"] < 0.2


def test_not_ready_and_honest_status_when_a_model_is_missing(make_client, tmp_path):
    from app.core.config import PROJECT_ROOT

    shutil.copytree(PROJECT_ROOT / "models" / "heart", tmp_path / "heart")  # respiratory deliberately missing
    client = make_client(models_dir=tmp_path)
    response = client.get("/api/health/ready")
    assert response.status_code == 503
    assert response.json()["models"] == {"heart": True, "respiratory": False}
    status = {m["model_id"]: m for m in client.get("/api/models/status").json()["models"]}
    assert status["respiratory"]["available"] is False
    assert "not installed" in status["respiratory"]["unavailable_reason"]
    assert str(tmp_path) not in client.get("/api/models/status").text
