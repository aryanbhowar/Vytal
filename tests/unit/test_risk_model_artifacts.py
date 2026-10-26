"""Checks on the saved model artifacts. These run without the survey data.

The feature rows below are SYNTHETIC example answers, used only to exercise the models.
"""

import json
import shutil

import numpy as np
import pandas as pd
import pytest

from ml.feature_definitions.feature_schema import categorical_values, is_categorical, load_schema, model_features
from ml.inference.risk_model import ModelIntegrityError, load_risk_model, metadata_path_for
from ml.training.model_training_config import BAND_ORDER
from ml.training.train_binary_risk_model import artifact_path

MODEL_IDS = ["heart", "respiratory"]

SYNTHETIC_PROFILE = {
    "age_group": "60-64", "sex": "male", "bmi": 31.2, "smoking_status": "former",
    "ecigarette_current_use": "no", "physical_activity_past_30_days": "no", "heavy_alcohol_use": "no",
    "diabetes_status": "yes", "stroke_history": "no", "kidney_disease_history": "no", "asthma_status": "never",
}


def synthetic_rows(model_id: str, count: int = 1) -> pd.DataFrame:
    return pd.DataFrame([{f: SYNTHETIC_PROFILE[f] for f in model_features(model_id)}] * count)


@pytest.fixture(scope="module", params=MODEL_IDS)
def model(request):
    path = artifact_path(request.param)
    if not path.exists():
        pytest.skip(f"{path.name} not trained")
    return load_risk_model(path)


def test_artifact_loads_and_matches_schema(model):
    assert model.features == model_features(model.model_id)
    assert model.metadata["feature_schema_version"] == load_schema()["schema_version"]
    for feature in model.features:
        if is_categorical(feature):
            assert model.metadata["feature_categories"][feature] == categorical_values(feature)


def test_fitted_encoder_categories_equal_schema(model):
    encoder = model.pipeline.named_steps["preprocess"].named_transformers_["categorical"]
    categorical = [f for f in model.features if is_categorical(f)]
    for feature, fitted in zip(categorical, encoder.categories_):
        assert list(fitted) == categorical_values(feature)


def test_predictions_have_correct_shape_and_are_valid_probabilities(model):
    rows = synthetic_rows(model.model_id, 3)
    assert model.pipeline.predict_proba(rows[model.features]).shape == (3, 2)
    probability = model.probability(rows)
    assert probability.shape == (3,)
    assert np.isfinite(probability).all() and ((probability >= 0) & (probability <= 1)).all()


def test_unknown_category_is_rejected_not_guessed(model):
    rows = synthetic_rows(model.model_id)
    rows.loc[0, "smoking_status"] = "sometimes"
    with pytest.raises(ValueError):
        model.probability(rows)


def test_contributions_reconstruct_the_raw_log_odds_exactly(model):
    rows = synthetic_rows(model.model_id)
    raw = model.raw_probability(rows)[0]
    log_odds = np.log(raw / (1 - raw))
    total = model.average_respondent_log_odds() + model.contributions(rows).iloc[0].sum()
    assert total == pytest.approx(log_odds, abs=1e-8)


def test_bands_and_percentiles_are_ordered(model):
    cutoffs = model.metadata["bands"]["probability_cutoffs"]
    assert cutoffs["moderate"] <= cutoffs["elevated"] <= cutoffs["high"]
    assert [model.band(p) for p in (0.0, cutoffs["moderate"], cutoffs["elevated"], cutoffs["high"])] == BAND_ORDER
    assert model.percentile(np.array([0.0]))[0] < model.percentile(np.array([cutoffs["high"]]))[0]


def test_metrics_were_computed_on_held_out_test_rows(model):
    evaluation = model.metadata["evaluation"]
    rows = model.metadata["training_data"]["rows"]
    assert evaluation["test"]["rows"] == rows["test"]
    assert evaluation["validation"]["rows"] == rows["validation"]
    assert 0.5 < evaluation["test"]["roc_auc"] <= 1.0
    assert evaluation["test"]["pr_auc"] > evaluation["test_prevalence_baseline"]["pr_auc"]


def test_tampered_artifact_is_refused(model, tmp_path):
    source = artifact_path(model.model_id)
    copy = tmp_path / source.name
    shutil.copy(source, copy)
    shutil.copy(metadata_path_for(source), metadata_path_for(copy))
    with copy.open("ab") as handle:
        handle.write(b"tampered")
    with pytest.raises(ModelIntegrityError):
        load_risk_model(copy)


def test_metadata_records_dependency_versions(model):
    import sklearn

    assert model.metadata["dependencies"]["scikit-learn"] == sklearn.__version__
    json.dumps(model.metadata)  # serialisable
