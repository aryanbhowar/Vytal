"""POST /api/assessment/predict: the main endpoint.

The request body is validated by Pydantic before this code runs. Answers are used
only to compute the response; they are not logged, stored or sent anywhere.
"""

from fastapi import APIRouter, HTTPException, Request

from app.schemas.assessment_schemas import AssessmentRequest, AssessmentResponse, ErrorResponse
from app.services.assessment_service import NoModelsAvailableError, run_assessment
from app.services.input_preprocessing_service import BmiOutOfRangeError

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


def _client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post(
    "/predict",
    response_model=AssessmentResponse,
    responses={422: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def predict(assessment: AssessmentRequest, request: Request) -> AssessmentResponse:
    if not request.app.state.rate_limiter.allow(_client_key(request)):
        raise HTTPException(status_code=429, detail="Too many assessments in a short time. Please wait a minute.",
                            headers={"Retry-After": "60"})
    try:
        return run_assessment(assessment, request.app.state.model_registry)
    except BmiOutOfRangeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from None
    except NoModelsAvailableError:
        raise HTTPException(status_code=503, detail="Assessments are temporarily unavailable because no model is loaded.") from None
