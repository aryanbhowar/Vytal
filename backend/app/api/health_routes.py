"""Liveness, readiness and model-status endpoints.

/api/health        -> the server process is running (liveness)
/api/health/ready  -> both models are loaded, so assessments can be served (readiness)
/api/models/status -> per-model availability plus the evaluation figures shown on the methodology page
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.model_registry import MODEL_TITLES

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str


class ReadinessResponse(BaseModel):
    ready: bool
    models: dict[str, bool]


class ModelEvaluationSummary(BaseModel):
    test_rows: int
    roc_auc: float
    pr_auc: float
    brier_score: float
    expected_calibration_error: float
    sensitivity: float
    specificity: float
    precision: float
    reporting_threshold: float


class ModelStatus(BaseModel):
    model_id: str
    title: str
    available: bool
    unavailable_reason: str | None = None
    model_version: str | None = None
    outcome_description: str | None = None
    training_years: list[int] = []
    training_rows: int | None = None
    features: list[str] = []
    survey_prevalence: float | None = None
    calibration_method: str | None = None
    evaluation: ModelEvaluationSummary | None = None


class ModelsStatusResponse(BaseModel):
    models: list[ModelStatus]


@router.get("/health", response_model=HealthResponse)
def get_health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(status="ok", app=settings.app_name, version=settings.app_version)


@router.get("/health/ready", response_model=ReadinessResponse, responses={503: {"model": ReadinessResponse}})
def get_readiness(request: Request):
    registry = request.app.state.model_registry
    body = ReadinessResponse(ready=registry.all_available,
                             models={model_id: slot.available for model_id, slot in registry.slots.items()})
    return JSONResponse(body.model_dump(), status_code=200 if body.ready else 503)


def _status_for(slot) -> ModelStatus:
    if not slot.available:
        return ModelStatus(model_id=slot.model_id, title=MODEL_TITLES[slot.model_id], available=False,
                           unavailable_reason=slot.unavailable_reason)
    metadata = slot.model.metadata
    test = metadata["evaluation"]["test"]
    return ModelStatus(
        model_id=slot.model_id,
        title=MODEL_TITLES[slot.model_id],
        available=True,
        model_version=metadata["model_version"],
        outcome_description=metadata["outcome_description"],
        training_years=metadata["training_data"]["survey_years"],
        training_rows=metadata["training_data"]["rows"]["train"],
        features=metadata["features"],
        survey_prevalence=metadata["training_data"]["weighted_us_adult_prevalence"],
        calibration_method=metadata["calibration_method"],
        evaluation=ModelEvaluationSummary(
            test_rows=test["rows"], roc_auc=test["roc_auc"], pr_auc=test["pr_auc"], brier_score=test["brier_score"],
            expected_calibration_error=test["expected_calibration_error"], sensitivity=test["recall_sensitivity"],
            specificity=test["specificity"], precision=test["precision"], reporting_threshold=test["threshold"],
        ),
    )


@router.get("/models/status", response_model=ModelsStatusResponse)
def get_models_status(request: Request) -> ModelsStatusResponse:
    registry = request.app.state.model_registry
    return ModelsStatusResponse(models=[_status_for(slot) for slot in registry.slots.values()])
