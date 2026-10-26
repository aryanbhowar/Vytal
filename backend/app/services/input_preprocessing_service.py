"""Turn a validated assessment request into model-ready feature rows.

This is the only place where the user's answers are converted, and it produces
exactly the canonical values the models were trained on (see the feature schema).
"""

from dataclasses import dataclass

import pandas as pd

from app.schemas.assessment_schemas import AssessmentRequest
from ml.feature_definitions.feature_schema import bmi_range, feature_definition, model_features

# BRFSS _AGEG5YR groups: (lowest age, canonical value). 80 and over is one group.
AGE_GROUP_STARTS = [(18, "18-24"), (25, "25-29"), (30, "30-34"), (35, "35-39"), (40, "40-44"),
                    (45, "45-49"), (50, "50-54"), (55, "55-59"), (60, "60-64"), (65, "65-69"),
                    (70, "70-74"), (75, "75-79"), (80, "80+")]

# WHO adult BMI categories (kg/m2). WHO notes lower cut-offs may suit some Asian populations.
WHO_BMI_CATEGORIES = [(18.5, "Underweight"), (25.0, "Healthy weight"), (30.0, "Overweight"), (float("inf"), "Obesity")]

ANSWER_FIELDS = ["sex", "smoking_status", "ecigarette_current_use", "physical_activity_past_30_days",
                 "diabetes_status", "stroke_history", "kidney_disease_history", "asthma_status"]


class BmiOutOfRangeError(ValueError):
    """Height and weight give a BMI outside the range the models were trained on."""


def age_group_for(age_years: int) -> str:
    group = AGE_GROUP_STARTS[0][1]
    for start, label in AGE_GROUP_STARTS:
        if age_years >= start:
            group = label
    return group


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 1)


def who_bmi_category(bmi: float) -> str:
    for upper, label in WHO_BMI_CATEGORIES:
        if bmi < upper:
            return label
    return WHO_BMI_CATEGORIES[-1][1]


@dataclass(frozen=True)
class PreparedAssessment:
    request: AssessmentRequest
    age_group: str
    bmi: float | None

    def answers(self) -> dict[str, object]:
        values = {name: getattr(self.request, name) for name in ANSWER_FIELDS}
        values["age_group"] = self.age_group
        values["bmi"] = self.bmi
        return values

    def feature_row(self, model_id: str) -> pd.DataFrame:
        answers = self.answers()
        return pd.DataFrame([{feature: answers[feature] for feature in model_features(model_id)}])

    @property
    def has_bmi(self) -> bool:
        return self.bmi is not None


def prepare_assessment(request: AssessmentRequest) -> PreparedAssessment:
    bmi = None
    if request.height_cm is not None and request.weight_kg is not None:
        bmi = calculate_bmi(request.height_cm, request.weight_kg)
        low, high = bmi_range()
        if not low <= bmi <= high:
            raise BmiOutOfRangeError(
                f"Height and weight give a BMI of {bmi}, outside the range {low:g}–{high:g} the models can use. "
                "Please check both values and their units."
            )
    return PreparedAssessment(request, age_group_for(request.age_years), bmi)


def answer_label(feature: str, value: object) -> str:
    definition = feature_definition(feature)
    if definition["type"] == "numeric":
        return f"{value:.1f}"
    return definition["labels"][str(value)]
