"""Security and privacy behaviour of the API."""

import logging

PREDICT = "/api/assessment/predict"


def test_security_headers_present(client):
    headers = client.get("/api/health").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


def test_assessment_responses_are_not_cached(client, valid_assessment):
    headers = client.post(PREDICT, json=valid_assessment).headers
    assert headers["Cache-Control"] == "no-store"


def test_oversized_body_is_rejected(client):
    response = client.post(PREDICT, content=b"{" + b" " * 20_000 + b"}", headers={"Content-Type": "application/json"})
    assert response.status_code == 413


def test_malformed_json_gets_a_friendly_error(client):
    response = client.post(PREDICT, content=b"{not json", headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert "Traceback" not in response.text


def test_rate_limit_returns_429(make_client, valid_assessment):
    client = make_client(predict_rate_limit_per_minute=2)
    statuses = [client.post(PREDICT, json=valid_assessment).status_code for _ in range(3)]
    assert statuses == [200, 200, 429]


def test_unexpected_errors_reveal_nothing_internal(client, valid_assessment, monkeypatch):
    from app.api import assessment_routes

    def explode(*_args, **_kwargs):
        raise RuntimeError("secret internal detail C:\\vytal_ty\\models")

    monkeypatch.setattr(assessment_routes, "run_assessment", explode)
    response = client.post(PREDICT, json=valid_assessment)
    assert response.status_code == 500
    assert response.json() == {"detail": "Something went wrong on our side. Please try again."}
    assert "secret" not in response.text and "vytal_ty" not in response.text


def test_health_answers_are_not_written_to_logs(client, valid_assessment, caplog):
    distinctive = dict(valid_assessment, age_years=87, height_cm=163.7, weight_kg=71.3)
    with caplog.at_level(logging.DEBUG):
        client.post(PREDICT, json=distinctive)
    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "163.7" not in logged and "71.3" not in logged


def test_docs_can_be_disabled_for_production(make_client):
    client = make_client(enable_api_docs=False)
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
