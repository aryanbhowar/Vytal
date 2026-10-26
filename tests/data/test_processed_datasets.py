"""Checks on the processed model datasets. Skipped when the data has not been built."""

import json

import pandas as pd
import pytest

from ml.feature_definitions.feature_schema import bmi_range, categorical_values, is_categorical, model_features
from ml.preprocessing.build_model_dataset import DATASET_NAMES, TARGET_COLUMN, dataset_path, summary_path

FORBIDDEN_COLUMNS = {"heart_target", "copd_target", "heart_attack_ever", "coronary_heart_disease_ever",
                     "_MICHD", "CHCCOPD3", "CVDINFR4", "CVDCRHD4"}


@pytest.fixture(scope="module", params=sorted(DATASET_NAMES))
def dataset(request):
    model_id = request.param
    if not dataset_path(model_id).exists():
        pytest.skip(f"{dataset_path(model_id).name} not built")
    return model_id, pd.read_csv(dataset_path(model_id))


def test_expected_columns_and_no_target_leakage(dataset):
    model_id, data = dataset
    expected = ["survey_year", "split", TARGET_COLUMN, *model_features(model_id), "pooled_weight"]
    assert list(data.columns) == expected
    assert not FORBIDDEN_COLUMNS & set(data.columns)


def test_target_is_binary_and_no_missing_values(dataset):
    _, data = dataset
    assert set(data[TARGET_COLUMN].unique()) == {0, 1}
    assert not data.isna().any().any()


def test_categorical_values_match_schema_and_bmi_in_range(dataset):
    model_id, data = dataset
    for feature in model_features(model_id):
        if is_categorical(feature):
            assert set(data[feature].astype(str)) == set(categorical_values(feature)), feature
    low, high = bmi_range()
    assert data["bmi"].between(low, high).all()


def test_splits_are_disjoint_proportional_and_stratified(dataset):
    _, data = dataset
    shares = data["split"].value_counts(normalize=True)
    assert set(shares.index) == {"train", "validation", "test"}
    assert shares["train"] == pytest.approx(0.70, abs=0.001)
    prevalence = data.groupby("split")[TARGET_COLUMN].mean()
    assert prevalence.max() - prevalence.min() < 0.001
    # Every row belongs to exactly one split by construction (one label per row).
    assert data["split"].notna().all()


def test_summary_matches_dataset(dataset):
    model_id, data = dataset
    summary = json.loads(summary_path(model_id).read_text(encoding="utf-8"))
    assert summary["total_rows"] == len(data)
    assert summary["total_positives"] == int(data[TARGET_COLUMN].sum())
    for year, info in summary["by_year"].items():
        steps = info["drop_steps"]
        assert steps[-1]["remaining"] == info["final_rows"]
        assert steps[0]["remaining"] - sum(s["removed"] for s in steps) == info["final_rows"], year
