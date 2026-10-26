# Vytal

Personalized health-risk assessment web application, built as a final-year undergraduate project and engineered to be maintainable and deployment-ready.

> **Not a diagnosis.** Vytal has not been clinically validated and is not suitable for clinical decisions. Its results describe patterns in US adult survey data and must not replace advice from a qualified healthcare professional. If you have chest pain, severe breathlessness or other urgent symptoms, seek medical care immediately.

## What it does

A user answers 11 health and lifestyle questions (no name or contact details). A FastAPI backend validates the answers and runs two logistic-regression models trained on about 1.1 million responses to the CDC Behavioral Risk Factor Surveillance System (BRFSS) 2022–2024:

| Model | Estimates how often people with similar answers had reported… | Test ROC-AUC |
|---|---|---|
| Heart | coronary heart disease or a heart attack | 0.810 |
| Respiratory | COPD, emphysema or chronic bronchitis | 0.836 |

The results page shows each model's estimate next to the US survey average, a band (Low/Moderate/Elevated/High, positions among survey respondents, not clinical categories), the answers that moved the estimate, limitations, and general suggestions linked to WHO guidance.

Engineering: strict input validation, security headers, rate and size limits, no storage or logging of answers, hash-checked model files, model cards, 160 automated tests (unit, API, data, browser), CI on GitHub, and a one-command production mode.

**Status:** all planned tasks complete; see [`PROJECT_STATUS.md`](PROJECT_STATUS.md). Model results: [`docs/model_evaluation/`](docs/model_evaluation/).

## Requirements

- Windows 10/11 (other systems should work with adjusted commands)
- Python 3.10 or newer (developed on 3.13)
- Node.js 20.19 or newer (required by Vite 8; tested on 24 in CI and 26 locally)
- Git

Check them with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
```

## Setup (first time)

From the project root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r ml\requirements.txt -r requirements-dev.txt
cd frontend
npm install
cd ..
```

## Run

Use two terminals, both starting in the project root.

Terminal 1 (backend, http://127.0.0.1:8000, docs at `/docs`):

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Terminal 2 (frontend, http://localhost:5173):

```powershell
cd frontend
npm run dev
```

Open http://localhost:5173. The header shows **Models online** when the backend has loaded both models; click **Start the assessment**.

## Test

```powershell
.venv\Scripts\python.exe -m pytest                 # backend, ML and data (118 tests)
cd frontend
npm run lint; npm run build; npm test              # frontend (25 tests)
npm run test:e2e                                   # browser tests in Edge against the real models (11 tests)
cd ..
.venv\Scripts\python.exe scripts\run_demo_profiles.py   # with the backend running
```

## Project layout

## Production mode

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1      # all checks + frontend build
powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1   # website + API at http://127.0.0.1:8000
```

Configuration, health checks, troubleshooting, rollback and what is needed before any public deployment: [`docs/deployment/DEPLOYMENT.md`](docs/deployment/DEPLOYMENT.md). Demo walkthrough: [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md). All documentation: [`docs/PROJECT_DOCUMENTATION.md`](docs/PROJECT_DOCUMENTATION.md).

| Path | Purpose |
|---|---|
| `backend/` | FastAPI application |
| `frontend/` | React + Vite + TypeScript application (Vitest unit tests, Playwright browser tests in `e2e/`) |
| `ml/` | Data download, verification, preprocessing, training, evaluation, shared inference |
| `models/` | Trained model files and metadata (committed) |
| `datasets/` | Data documentation; raw and processed data are recreated by script (not committed) |
| `tests/` | Python tests (`unit/`, `integration/`, `data/`) |
| `scripts/` | Environment check, dev/production start, release build, demo profiles |
| `.github/workflows/ci.yml` | Continuous integration |
| `docs/implementation/MASTER_IMPLEMENTATION_PLAN.md` | The approved plan for all 13 tasks |
| `docs/decisions/DECISION_LOG.md` | Important technical and data decisions |
| `docs/phase_reports/` | One report per phase |
| `docs/VIVA_NOTES.md` | Beginner-friendly explanations for the viva |
| `PROJECT_STATUS.md` | Current progress (single source of truth) |
| `CHANGELOG.md` | Chronological list of changes |


## Data

Vytal uses CDC BRFSS 2022, 2023 and 2024 (public domain; source: CDC). The files are large (about 1.1 GB each unzipped) and are **not** stored in this repository. To recreate them:

```powershell
.venv\Scripts\python.exe -m pip install -r ml\requirements.txt
.venv\Scripts\python.exe -m ml.preprocessing.download_brfss_data
.venv\Scripts\python.exe -m ml.preprocessing.inspect_brfss_variables
```

Details, terms of use and limitations: [`datasets/DATA_SOURCES.md`](datasets/DATA_SOURCES.md) and [`datasets/README.md`](datasets/README.md). Vytal's use of BRFSS data does not imply endorsement by CDC, HHS or the U.S. Government.
