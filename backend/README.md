# Vytal backend

FastAPI + Pydantic. Runs locally with no database, cloud service or API key. Loads the two saved models at startup and serves assessments.

## Run (from the project root)

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

API at http://127.0.0.1:8000; interactive docs at http://127.0.0.1:8000/docs. Settings: `.env.example`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness: the server is running |
| GET | `/api/health/ready` | Readiness: 200 if both models loaded, otherwise 503 with which one is missing |
| GET | `/api/models/status` | Per-model availability, version, training data and test-set metrics |
| POST | `/api/assessment/predict` | Validate answers, run both models, return estimates, bands, factors and suggestions |

### Example request

```json
{"age_years": 62, "sex": "male", "height_cm": 175, "weight_kg": 92,
 "smoking_status": "current_daily", "ecigarette_current_use": "no",
 "physical_activity_past_30_days": "no", "diabetes_status": "yes",
 "stroke_history": "no", "kidney_disease_history": "no", "asthma_status": "never"}
```

Allowed values for every answer are in `ml/feature_definitions/vytal_feature_schema.json`. `height_cm`/`weight_kg` may be `null`; the models then return `insufficient_input` instead of guessing.

### Responses

| Status | When |
|---|---|
| 200 | Results. Each model's `status` is `ok`, `insufficient_input` (no BMI) or `unavailable` (model not loaded) |
| 413 / 411 | Body over 16 KB / no Content-Length |
| 422 | Invalid answers: `{"detail": "...", "errors": [{"field", "message"}]}`; also BMI outside 12–70 |
| 429 | Over the per-minute limit |
| 503 | No model loaded |
| 500 | Unexpected error; generic message only |

## Layout

| Path | Responsibility |
|---|---|
| `app/main.py` | App factory, middleware, routers, startup model loading, optional frontend serving |
| `app/core/config.py` | Settings from environment variables |
| `app/core/security.py` | Security headers, body size limit, rate limiter |
| `app/core/errors.py` | Friendly validation errors; generic 500s |
| `app/schemas/assessment_schemas.py` | Request and response models |
| `app/api/health_routes.py`, `assessment_routes.py` | Endpoints |
| `app/services/model_registry.py` | Load models (hash check first), track availability |
| `app/services/input_preprocessing_service.py` | Age → age group, BMI, feature rows |
| `app/services/result_interpretation_service.py` | Estimate, percentile, band, factors, limitations, disclaimer |
| `app/services/health_suggestion_rules.py`, `suggestion_service.py` | Rule-based suggestions with WHO sources |
| `app/services/assessment_service.py` | Orchestrates one assessment |

The backend imports `ml/feature_definitions` and `ml/inference` so the served numbers are computed by the same code that was evaluated.

## Privacy

No names or identifiers are collected. Answers are used only to build the response: they are not stored, not logged and not sent anywhere. Assessment responses carry `Cache-Control: no-store`.
