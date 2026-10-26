"""Request and response shapes for the assessment API.

Answer values are the canonical values from ml/feature_definitions/vytal_feature_schema.json.
A test checks these Literal types match the schema exactly, so the API, the
training data and the saved models can never drift apart.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Sex = Literal["male", "female"]
SmokingStatus = Literal["current_daily", "current_some_days", "former", "never"]
YesNo = Literal["yes", "no"]
DiabetesStatus = Literal["yes", "gestational_only", "no", "prediabetes"]
AsthmaStatus = Literal["current", "former", "never"]
ModelId = Literal["heart", "respiratory"]
ResultStatus = Literal["ok", "unavailable", "insufficient_input"]
Band = Literal["low", "moderate", "elevated", "high"]


class AssessmentRequest(BaseModel):
    """One person's answers. Nothing here identifies the person, and nothing is stored."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    age_years: int = Field(ge=18, le=120, description="Age in whole years (adults only)")
    sex: Sex
    height_cm: float | None = Field(default=None, ge=100, le=250, description="Height in centimetres, or null if unknown")
    weight_kg: float | None = Field(default=None, ge=25, le=350, description="Weight in kilograms, or null if unknown")
    smoking_status: SmokingStatus
    ecigarette_current_use: YesNo
    physical_activity_past_30_days: YesNo
    diabetes_status: DiabetesStatus
    stroke_history: YesNo
    kidney_disease_history: YesNo
    asthma_status: AsthmaStatus


class BmiSummary(BaseModel):
    value: float
    who_category: str
    source: str = "derived from height and weight"


class ProfileAnswer(BaseModel):
    field: str
    question: str
    value: str
    label: str


class ProfileSummary(BaseModel):
    age_years: int
    age_group: str
    height_cm: float | None
    weight_kg: float | None
    bmi: BmiSummary | None
    answers: list[ProfileAnswer]


class ContributingFactor(BaseModel):
    feature: str
    label: str
    answer: str
    direction: Literal["raised", "lowered"]
    log_odds_contribution: float
    modifiable: bool


class BandValidation(BaseModel):
    """How often held-out survey respondents in this band reported the condition."""

    observed_rate: float
    share_of_respondents: float


class ModelResult(BaseModel):
    model_id: ModelId
    title: str
    outcome_description: str
    status: ResultStatus
    message: str | None = None
    estimated_probability: float | None = None
    survey_prevalence: float | None = None
    percentile: float | None = None
    category: Band | None = None
    category_explanation: str | None = None
    band_validation: BandValidation | None = None
    contributing_factors: list[ContributingFactor] = Field(default_factory=list)
    explanation_note: str | None = None
    limitations: list[str] = Field(default_factory=list)
    model_version: str | None = None


class Suggestion(BaseModel):
    id: str
    theme: str
    title: str
    body: str
    triggered_by: list[str]
    priority: Literal["urgent", "high", "normal"]
    source_name: str
    source_url: str


class AssessmentResponse(BaseModel):
    profile_summary: ProfileSummary
    results: list[ModelResult]
    suggestions: list[Suggestion]
    disclaimer: str
    data_attribution: str


class FieldError(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    detail: str
    errors: list[FieldError] = Field(default_factory=list)
