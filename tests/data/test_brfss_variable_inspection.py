"""Checks on the committed BRFSS inspection summary (aggregate counts only).

These tests guard the data decisions D-022 to D-026: if the inspection is re-run
on a different download and something important changes, they fail.
"""

import json

import pytest

from ml.feature_definitions.brfss_candidate_variables import (
    MODEL_TARGETS,
    PROPOSED_MODEL_FEATURES,
    SURVEY_YEARS,
)
from ml.preprocessing.inspect_brfss_variables import SUMMARY_PATH


@pytest.fixture(scope="module")
def summary():
    if not SUMMARY_PATH.exists():
        pytest.skip("Run ml.preprocessing.inspect_brfss_variables first")
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def variables(summary):
    return {v["canonical_name"]: v for v in summary["variables"]}


def test_every_year_file_has_cdc_published_record_count(summary):
    for year in SURVEY_YEARS:
        info = summary["files"][str(year)]
        assert info["records"] == info["expected_records"], year


@pytest.mark.parametrize("model", sorted(MODEL_TARGETS))
def test_target_exists_with_identical_definition_in_all_years(variables, model):
    target = variables[MODEL_TARGETS[model]]
    assert target["in_all_years"]
    assert target["question_identical_across_years"]
    assert target["codes_identical_across_years"]
    assert target["codebook_counts_match_file"]


@pytest.mark.parametrize("model", sorted(PROPOSED_MODEL_FEATURES))
def test_model_features_are_compatible_across_all_years(variables, model):
    for feature in PROPOSED_MODEL_FEATURES[model]:
        record = variables[feature]
        assert record["in_all_years"], feature
        assert record["question_identical_across_years"], feature
        assert record["codes_identical_across_years"], feature
        assert record["codebook_counts_match_file"], feature


def test_blood_pressure_and_cholesterol_are_only_in_2023(variables):
    # Evidence for excluding them from the pooled models (D-025).
    for name in ("high_blood_pressure", "cholesterol_checked", "high_cholesterol"):
        assert variables[name]["available_years"] == [2023], name


def test_models_do_not_use_each_others_target_or_design_variables():
    forbidden = {"heart_target", "copd_target", "heart_attack_ever", "coronary_heart_disease_ever",
                 "survey_weight", "sampling_stratum", "primary_sampling_unit"}
    for features in PROPOSED_MODEL_FEATURES.values():
        assert not forbidden & set(features)


@pytest.mark.parametrize("model", sorted(MODEL_TARGETS))
def test_each_year_has_enough_positive_cases(summary, model):
    for year in SURVEY_YEARS:
        record = summary["model_samples"][model]["by_year"][str(year)]
        positives = record["complete_cases"] * record["complete_case_prevalence_percent"] / 100
        assert positives > 20_000, (model, year)
