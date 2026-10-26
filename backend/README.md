# Vytal backend

FastAPI + Pydantic API. Runs locally; no database, no cloud services, no API keys.

## Run (from the project root)

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger): http://127.0.0.1:8000/docs

## Layout

| Path | Responsibility |
|---|---|
| `app/main.py` | Creates the FastAPI app, CORS, and registers routers |
| `app/core/config.py` | Settings (app name, version, allowed origins) |
| `app/api/health_routes.py` | `GET /api/health` |

Planned (Task 6–7): `app/schemas/` (request/response models), `app/services/` (preprocessing, model registry, prediction, interpretation, suggestions), `app/core/errors.py`.

## Endpoints

| Method | Path | Status |
|---|---|---|
| GET | `/api/health` | Implemented: returns `{"status":"ok","app":"Vytal","version":"0.1.0"}` |
| GET | `/api/models/status` | Planned (Task 6) |
| POST | `/api/assessment/predict` | Planned (Task 6) |
