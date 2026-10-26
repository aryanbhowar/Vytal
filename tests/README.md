# Tests

## Python (backend, ML, data): from the project root

```powershell
.venv\Scripts\python.exe -m pytest
```

`pytest.ini` puts `backend/` and the project root on the import path. `tests/conftest.py` provides a test client that runs the real app startup (loading the real models) and a factory for apps with changed settings (missing or tampered models, low rate limits).

| Folder | Contents |
|---|---|
| `unit/` | Codebook parsing, recoding, splitting, model artifacts (hash, schema, contributions), backend services, suggestion rules |
| `integration/` | API via FastAPI's `TestClient`: health/readiness, assessments, error paths, missing/tampered models, security and privacy |
| `data/` | Checks on the BRFSS inspection summary and processed datasets (dataset tests skip if the data has not been built) |

## Frontend: inside `frontend/`

```powershell
npm test            # Vitest: utilities and pages, using labelled TEST FIXTURE responses
npm run test:e2e    # Playwright in Microsoft Edge against the real backend and models
```

## Live API demo

With the backend running: `.venv\Scripts\python.exe scripts\run_demo_profiles.py` (four documented example profiles, checked automatically).
