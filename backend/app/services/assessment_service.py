"""Run a complete assessment: prepare inputs, run each available model, add suggestions."""

from app.schemas.assessment_schemas import (
    AssessmentRequest,
    AssessmentResponse,
    BmiSummary,
    ModelResult,
    ProfileAnswer,
    ProfileSummary,
)
from app.services.input_preprocessing_service import (
    ANSWER_FIELDS,
    PreparedAssessment,
    answer_label,
    prepare_assessment,
    who_bmi_category,
)
from app.services.model_registry import ModelRegistry
from app.services.result_interpretation_service import (
    DATA_ATTRIBUTION,
    DISCLAIMER,
    insufficient_input_result,
    interpret,
    unavailable_result,
)
from app.services.suggestion_service import build_suggestions
from ml.feature_definitions.feature_schema import feature_definition


class NoModelsAvailableError(RuntimeError):
    """Neither model can produce an estimate, so there is nothing honest to return."""


def _profile_summary(prepared: PreparedAssessment) -> ProfileSummary:
    request = prepared.request
    answers = prepared.answers()
    return ProfileSummary(
        age_years=request.age_years,
        age_group=prepared.age_group,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        bmi=BmiSummary(value=prepared.bmi, who_category=who_bmi_category(prepared.bmi)) if prepared.has_bmi else None,
        answers=[
            ProfileAnswer(field=name, question=feature_definition(name)["question"], value=str(answers[name]),
                          label=answer_label(name, answers[name]))
            for name in ANSWER_FIELDS
        ],
    )


def _model_result(registry: ModelRegistry, model_id: str, prepared: PreparedAssessment) -> ModelResult:
    slot = registry.get(model_id)
    if not slot.available:
        return unavailable_result(model_id, slot.unavailable_reason or "")
    if not prepared.has_bmi:
        return insufficient_input_result(slot.model)
    return interpret(slot.model, prepared)


def run_assessment(request: AssessmentRequest, registry: ModelRegistry) -> AssessmentResponse:
    prepared = prepare_assessment(request)  # may raise BmiOutOfRangeError
    if not registry.any_available:
        raise NoModelsAvailableError()
    results = [_model_result(registry, model_id, prepared) for model_id in registry.slots]
    return AssessmentResponse(
        profile_summary=_profile_summary(prepared),
        results=results,
        suggestions=build_suggestions(prepared, results),
        disclaimer=DISCLAIMER,
        data_attribution=DATA_ATTRIBUTION,
    )
