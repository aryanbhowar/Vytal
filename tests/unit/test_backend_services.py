"""Unit tests for input preprocessing, interpretation and the rate limiter."""

import typing

import pytest

from app.core.security import SlidingWindowRateLimiter
from app.schemas.assessment_schemas import AssessmentRequest
from app.services.input_preprocessing_service import (
    BmiOutOfRangeError,
    age_group_for,
    calculate_bmi,
    prepare_assessment,
    who_bmi_category,
)
from ml.feature_definitions.feature_schema import categorical_values, load_schema
from tests.conftest import VALID_ASSESSMENT


@pytest.mark.parametrize("age,group", [(18, "18-24"), (24, "18-24"), (25, "25-29"), (64, "60-64"),
                                       (79, "75-79"), (80, "80+"), (120, "80+")])
def test_age_groups_match_brfss_bands(age, group):
    assert age_group_for(age) == group


def test_bmi_calculation_and_who_categories():
    assert calculate_bmi(180, 81) == 25.0
    assert who_bmi_category(18.4) == "Underweight"
    assert who_bmi_category(18.5) == "Healthy weight"
    assert who_bmi_category(25.0) == "Overweight"
    assert who_bmi_category(30.0) == "Obesity"


def test_bmi_outside_training_range_is_rejected():
    with pytest.raises(BmiOutOfRangeError):
        prepare_assessment(AssessmentRequest(**dict(VALID_ASSESSMENT, height_cm=250, weight_kg=60)))


def test_missing_weight_means_no_bmi_rather_than_a_guess():
    prepared = prepare_assessment(AssessmentRequest(**dict(VALID_ASSESSMENT, weight_kg=None)))
    assert prepared.bmi is None and not prepared.has_bmi


def test_api_answer_options_equal_feature_schema():
    """The API, the training data and the models must use identical answer values."""
    fields = AssessmentRequest.model_fields
    for feature, definition in load_schema()["features"].items():
        if definition["type"] != "categorical" or feature == "age_group":
            continue
        allowed = typing.get_args(fields[feature].annotation)
        assert sorted(allowed) == sorted(categorical_values(feature)), feature


def test_rate_limiter_window():
    limiter = SlidingWindowRateLimiter(limit=2)
    assert limiter.allow("a", now=0) and limiter.allow("a", now=1)
    assert not limiter.allow("a", now=2)
    assert limiter.allow("b", now=2)
    assert limiter.allow("a", now=61)
    assert SlidingWindowRateLimiter(limit=0).allow("a")
