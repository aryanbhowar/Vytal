"""Integration tests for POST /api/assessment/predict using the real saved models."""

import math
import shutil

import numpy as np
import pytest

from app.core.config import MODEL_ARTIFACTS, PROJECT_ROOT
from app.schemas.assessment_schemas import AssessmentResponse

PREDICT = "/api/assessment/predict"


def test_valid_assessment_returns_real_results_for_both_models(client, valid_assessment):
    response = client.post(PREDICT, json=valid_assessment)
    assert response.status_code == 200
    body = AssessmentResponse.model_validate(response.json())
    assert [r.model_id for r in body.results] == ["heart", "respiratory"]
    for result in body.results:
        assert result.status == "ok"
        assert 0 < result.estimated_probability < 1 and math.isfinite(result.estimated_probability)
        assert 0 <= result.percentile <= 100
        assert result.category in {"low", "moderate", "elevated", "high"}
        assert result.contributing_factors and result.limitations
    assert body.profile_summary.bmi.value == pytest.approx(30.0, abs=0.05)
    assert body.profile_summary.bmi.source == "derived from height and weight"
    assert "not a diagnosis" in body.disclaimer
    assert body.suggestions[0].id == "urgent_symptoms"


def test_api_estimate_equals_direct_pipeline_output(client, valid_assessment):
    """The backend's preprocessing must give exactly what the trained pipeline gives."""
    from app.main import app as _  # noqa: F401  (ensures ml is importable)
    from ml.inference.risk_model import load_risk_model

    body = client.post(PREDICT, json=valid_assessment).json()
    direct_row = {"age_group": "60-64", "sex": "male", "bmi": 30.0, "smoking_status": "current_daily",
                  "ecigarette_current_use": "no", "physical_activity_past_30_days": "no", "diabetes_status": "yes",
                  "stroke_history": "no", "kidney_disease_history": "no", "asthma_status": "never"}
    import pandas as pd

    for result in body["results"]:
        model = load_risk_model(PROJECT_ROOT / "models" / MODEL_ARTIFACTS[result["model_id"]])
        expected = model.probability(pd.DataFrame([direct_row]))[0]
        assert result["estimated_probability"] == pytest.approx(round(float(expected), 4), abs=1e-4)


def test_same_input_gives_identical_output(client, valid_assessment):
    first = client.post(PREDICT, json=valid_assessment).json()
    second = client.post(PREDICT, json=valid_assessment).json()
    assert first == second


def test_higher_risk_answers_raise_estimates(client, valid_assessment):
    lower = dict(valid_assessment, age_years=30, smoking_status="never", physical_activity_past_30_days="yes",
                 diabetes_status="no", weight_kg=70)
    high = {r["model_id"]: r["estimated_probability"] for r in client.post(PREDICT, json=valid_assessment).json()["results"]}
    low = {r["model_id"]: r["estimated_probability"] for r in client.post(PREDICT, json=lower).json()["results"]}
    assert all(high[m] > low[m] for m in high)


@pytest.mark.parametrize("field,value", [
    ("age_years", 17), ("age_years", 121), ("height_cm", 50), ("weight_kg", 400),
    ("smoking_status", "sometimes"), ("sex", "unknown"), ("age_years", "sixty"),
])
def test_out_of_range_or_unknown_values_are_rejected(client, valid_assessment, field, value):
    response = client.post(PREDICT, json=dict(valid_assessment, **{field: value}))
    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Some answers need attention."
    assert any(error["field"] == field for error in body["errors"])


def test_missing_required_answer_and_extra_fields_are_rejected(client, valid_assessment):
    missing = dict(valid_assessment)
    del missing["smoking_status"]
    errors = client.post(PREDICT, json=missing).json()["errors"]
    assert {"field": "smoking_status", "message": "This answer is required."} in errors
    extra = client.post(PREDICT, json=dict(valid_assessment, name="Alice")).json()["errors"]
    assert {"field": "name", "message": "This field is not accepted."} in extra


def test_implausible_bmi_is_rejected_with_a_clear_message(client, valid_assessment):
    response = client.post(PREDICT, json=dict(valid_assessment, height_cm=100, weight_kg=300))
    assert response.status_code == 422
    assert "BMI" in response.json()["detail"]


def test_missing_height_gives_insufficient_input_not_a_guess(client, valid_assessment):
    body = client.post(PREDICT, json=dict(valid_assessment, height_cm=None)).json()
    assert body["profile_summary"]["bmi"] is None
    for result in body["results"]:
        assert result["status"] == "insufficient_input"
        assert result["estimated_probability"] is None


def test_one_missing_model_is_reported_unavailable(make_client, tmp_path, valid_assessment):
    shutil.copytree(PROJECT_ROOT / "models" / "heart", tmp_path / "heart")
    body = make_client(models_dir=tmp_path).post(PREDICT, json=valid_assessment).json()
    results = {r["model_id"]: r for r in body["results"]}
    assert results["heart"]["status"] == "ok"
    assert results["respiratory"]["status"] == "unavailable"
    assert results["respiratory"]["estimated_probability"] is None


def test_no_models_gives_503(make_client, tmp_path, valid_assessment):
    response = make_client(models_dir=tmp_path).post(PREDICT, json=valid_assessment)
    assert response.status_code == 503


def test_tampered_model_is_not_used(make_client, tmp_path, valid_assessment):
    shutil.copytree(PROJECT_ROOT / "models", tmp_path / "models")
    artifact = tmp_path / "models" / MODEL_ARTIFACTS["heart"]
    artifact.write_bytes(artifact.read_bytes() + b"x")
    body = make_client(models_dir=tmp_path / "models").post(PREDICT, json=valid_assessment).json()
    heart = next(r for r in body["results"] if r["model_id"] == "heart")
    assert heart["status"] == "unavailable" and "integrity" in heart["message"]


def test_contributions_reported_match_model(client, valid_assessment):
    body = client.post(PREDICT, json=valid_assessment).json()
    for result in body["results"]:
        for factor in result["contributing_factors"]:
            assert factor["direction"] == ("raised" if factor["log_odds_contribution"] > 0 else "lowered")
            assert np.isfinite(factor["log_odds_contribution"])
