"""Unit tests for BRFSS recoding and splitting. All rows here are SYNTHETIC test values."""

import json

import numpy as np
import pandas as pd
import pytest

from ml.feature_definitions.brfss_candidate_variables import INVALID_CODES, SURVEY_YEARS, candidate_by_name
from ml.feature_definitions.feature_schema import categorical_values, load_schema
from ml.preprocessing.dataset_split import assign_splits
from ml.preprocessing.inspect_brfss_variables import SUMMARY_PATH
from ml.preprocessing.recode_functions import recode_bmi, recode_categorical, recode_target


def test_smoking_codes_map_to_canonical_values_and_unusable_becomes_missing():
    synthetic = pd.Series([1.0, 2.0, 3.0, 4.0, 9.0, np.nan])
    result = recode_categorical(synthetic, "smoking_status")
    assert result.iloc[:4].tolist() == ["current_daily", "current_some_days", "former", "never"]
    assert result.iloc[4:].isna().all()


def test_dont_know_and_refused_are_never_recoded_to_no():
    synthetic = pd.Series([1.0, 2.0, 7.0, 9.0])
    result = recode_categorical(synthetic, "stroke_history")
    assert result.tolist()[:2] == ["yes", "no"]
    assert result.iloc[2:].isna().all()


def test_ecigarette_calculated_variable_meaning_is_preserved():
    # _CURECI: 1 = not currently using, 2 = current user. Easy to reverse by mistake.
    result = recode_categorical(pd.Series([1.0, 2.0]), "ecigarette_current_use")
    assert result.tolist() == ["no", "yes"]


def test_bmi_uses_two_implied_decimals_and_rejects_implausible_values():
    result = recode_bmi(pd.Series([2534.0, 1199.0, 7001.0, np.nan]))
    assert result.iloc[0] == pytest.approx(25.34)
    assert result.iloc[1:].isna().all()


def test_target_coding_is_one_for_reported_condition():
    result = recode_target(pd.Series([1.0, 2.0, 7.0, np.nan]), "respiratory")
    assert result.iloc[0] == 1 and result.iloc[1] == 0
    assert result.iloc[2:].isna().all()


def test_split_is_reproducible_stratified_and_complete():
    rng = np.random.default_rng(0)
    target = pd.Series(rng.random(20_000) < 0.09).astype(int)
    years = pd.Series(rng.choice(list(SURVEY_YEARS), 20_000))
    first, second = assign_splits(target, years), assign_splits(target, years)
    assert first.equals(second)
    shares = first.value_counts(normalize=True)
    assert shares["train"] == pytest.approx(0.70, abs=0.005)
    assert shares["validation"] == pytest.approx(0.15, abs=0.005)
    assert shares["test"] == pytest.approx(0.15, abs=0.005)
    prevalence = target.groupby(first).mean()
    assert prevalence.max() - prevalence.min() < 0.002


@pytest.mark.skipif(not SUMMARY_PATH.exists(), reason="inspection summary not generated")
def test_every_codebook_answer_is_either_mapped_or_explicitly_unusable():
    """No genuine answer may be dropped silently or mapped to the wrong value."""
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    by_name = {v["canonical_name"]: v for v in summary["variables"]}
    for feature, definition in load_schema()["features"].items():
        if definition["type"] != "categorical":
            continue
        mapped = set(definition["brfss_codes"])
        for year in SURVEY_YEARS:
            codebook_codes = set(by_name[feature]["by_year"][str(year)]["codes"]) - {""}
            unaccounted = codebook_codes - mapped - INVALID_CODES[feature]
            assert not unaccounted, (feature, year, unaccounted)
            assert not mapped & INVALID_CODES[feature], feature
            assert candidate_by_name(feature).source(year)


def test_schema_categories_are_unique_per_feature():
    for feature, definition in load_schema()["features"].items():
        if definition["type"] == "categorical":
            values = categorical_values(feature)
            assert len(values) == len(set(values)), feature
            assert set(definition["labels"]) == set(values), feature
