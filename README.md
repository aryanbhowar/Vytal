# Vytal

Personalized health-risk assessment web application, built as a final-year undergraduate project and engineered to be maintainable and deployment-ready.

> **Not a diagnosis.** Vytal has not been clinically validated and is not suitable for clinical decisions. Its results describe patterns in US adult survey data and must not replace advice from a qualified healthcare professional. If you have chest pain, severe breathlessness or other urgent symptoms, seek medical care immediately.

## What it does (planned)

A user completes a health and lifestyle questionnaire. A local FastAPI backend validates the answers and runs two scikit-learn models trained on the CDC Behavioral Risk Factor Surveillance System (BRFSS):

- **Heart model:** reported coronary heart disease or heart attack (BRFSS 2023).
- **Respiratory model:** reported COPD, emphysema or chronic bronchitis (BRFSS 2022–2024).

A React dashboard shows each result as a category with the model's estimate, the factors behind it, and general health-awareness suggestions.

Planned engineering features include strict input validation, security headers, no storage of answers, integrity-checked model files, model cards, automated unit, API and browser tests, CI, and a one-command production build.

**Current status:** see [`PROJECT_STATUS.md`](PROJECT_STATUS.md). The data pipeline, both trained models and the prediction API are built and tested; the user interface is next. Model results: [`docs/model_evaluation/`](docs/model_evaluation/).

## Requirements

- Windows 10/11 (other systems should work with adjusted commands)
- Python 3.10 or newer (developed on 3.13)
- Node.js 18 or newer (developed on 26)
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

Open http://localhost:5173. The page should say **API connected**.

## Test

```powershell
.venv\Scripts\python.exe -m pytest
cd frontend; npm run build
```

## Project layout

| Path | Purpose |
|---|---|
| `backend/` | FastAPI application |
| `frontend/` | React + Vite + TypeScript application |
| `tests/` | Python tests (`integration/`, later `unit/` and `data/`) |
| `scripts/` | Helper scripts (environment check; later start and demo scripts) |
| `docs/implementation/MASTER_IMPLEMENTATION_PLAN.md` | The approved plan for all 13 tasks |
| `docs/decisions/DECISION_LOG.md` | Important technical and data decisions |
| `docs/phase_reports/` | One report per phase |
| `docs/VIVA_NOTES.md` | Beginner-friendly explanations for the viva |
| `PROJECT_STATUS.md` | Current progress (single source of truth) |
| `CHANGELOG.md` | Chronological list of changes |

Planned folders (`ml/`, `datasets/`, `models/`) are created when the tasks that use them start.

## Data

Vytal uses CDC BRFSS 2022, 2023 and 2024 (public domain; source: CDC). The files are large (about 1.1 GB each unzipped) and are **not** stored in this repository. To recreate them:

```powershell
.venv\Scripts\python.exe -m pip install -r ml\requirements.txt
.venv\Scripts\python.exe -m ml.preprocessing.download_brfss_data
.venv\Scripts\python.exe -m ml.preprocessing.inspect_brfss_variables
```

Details, terms of use and limitations: [`datasets/DATA_SOURCES.md`](datasets/DATA_SOURCES.md) and [`datasets/README.md`](datasets/README.md). Vytal's use of BRFSS data does not imply endorsement by CDC, HHS or the U.S. Government.
