# Vytal: project status

_Last updated: 2026-10-26 (Day 1), end of Task 1._

## Objective

A locally runnable, educational health-risk-awareness web app. A questionnaire feeds a FastAPI backend that runs two trained scikit-learn models (reported heart disease from BRFSS 2023; reported COPD from BRFSS 2022–2024) and shows results with explanations, suggestions and limitations. Full plan: [`docs/implementation/MASTER_IMPLEMENTATION_PLAN.md`](docs/implementation/MASTER_IMPLEMENTATION_PLAN.md).

## Current phase

**Phase 1 (Day 1): Foundation and dataset decisions.** Task 1 is done; Task 2 (BRFSS download and variable verification) is next.

## Overall completion estimate: about 6%

Method: the 13 planned tasks are weighted by expected effort (Tasks 3–6 and 9–10 count double, giving 19 units). Task 1 is about 1 unit of 19 ≈ 5%, rounded up slightly for the tracking files that later tasks reuse. This is an estimate of planned work done, not of features working.

## Deliverables

| Status | Deliverable |
|---|---|
| Done (tested) | Python environment with pinned packages; `GET /api/health`; frontend connects to backend via Vite proxy; environment check script; Git repo with remote and identity configured |
| Done | Master plan, decision log, README, changelog, viva notes (Task 1 sections), phase report standard, detailed Phase 1 report (Task 1 part) |
| Not started | Tasks 2–13: dataset download and verification, preprocessing, both models, prediction API, suggestions, design system, questionnaire, dashboard, methodology page, demo scripts, final docs |

## Known blockers

None. (Git identity was set on 2026-10-26 for this repository: `aryanbhowar` / `aryanbhowar45.sphs@gmail.com`.)

## Component status

| Area | Status |
|---|---|
| Frontend | Vite 8 + React 19 + TypeScript skeleton; shows API connection state. `npm run build` passes. No design system or pages yet. |
| Backend | FastAPI app with `GET /api/health` only. 2 tests pass. |
| Datasets | Not downloaded. Zenodo cleaned dataset rejected (D-002). BRFSS variable availability not yet verified. |
| Heart model | Not started. |
| Respiratory model | Not started. |
| Tests | pytest: 2 passed (health endpoint, 404 without leak). Frontend: build passes; Vitest not yet set up (Task 8). |

## Latest working commands (from project root)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
cd frontend; npm run dev      # http://localhost:5173
cd frontend; npm run build
```

## Latest known-good commit

`e77e07f` (chore: initialize Vytal project structure), pushed to GitHub.

## Next three actions

1. Task 2: add `ml/requirements.txt` and the BRFSS download script; download 2022, 2023, 2024 (scripted, or manual fallback).
2. Task 2: inspect candidate variables; confirm 2023 has blood pressure and cholesterol questions.
3. Task 2: finalize feature lists in the decision log; write `datasets/DATA_SOURCES.md`; complete the Phase 1 report.

## Decisions needing user input

None right now. Task 2 may need one (if 2023 lacks blood pressure or cholesterol).

## Final success criteria (from the brief)

| # | Criterion | Status |
|---|---|---|
| 1 | Frontend runs locally | Done (skeleton) |
| 2 | Backend runs locally | Done (skeleton) |
| 3 | Frontend can communicate with backend | Done: `/api/health` via proxy returned 200; user confirmed "API connected" in the browser |
| 4 | Questionnaire validates inputs | Not started |
| 5 | BMI calculated correctly where possible | Not started |
| 6 | Dataset provenance documented | Not started (rejection of Zenodo recorded in decision log) |
| 7 | Heart model training reproducible | Not started |
| 8 | Respiratory model training reproducible | Not started |
| 9 | Model artifacts load successfully | Not started |
| 10 | Both prediction paths use correct preprocessing | Not started |
| 11 | Model evaluation documented honestly | Not started |
| 12 | Prediction endpoints return validated structured results | Not started |
| 13 | Dashboard uses actual model outputs | Not started |
| 14 | Unsupported predictions produce honest error states | Not started |
| 15 | Factor explanations technically defensible | Not started (method decided: D-011) |
| 16 | Suggestions follow documented rules | Not started |
| 17 | Glassmorphism styling consistent and responsive | Not started |
| 18 | Important functionality has tests | Partial: health endpoint only |
| 19 | End-to-end workflow demonstrated | Not started |
| 20 | Project starts with documented commands | Done for skeleton (README) |
| 21 | Git history and status maintained | Partial: first commit made (see Git section) |
| 22 | Phase reports allow resuming work | Partial: Phase 1 report covers Task 1 |
| 23 | Viva notes explain implementation | Partial: Task 1 sections written |
| 24 | Medical limitations visible and accurate | Partial: README disclaimer only |

## Git

| Commit | Message | Pushed |
|---|---|---|
| `e77e07f` | chore: initialize Vytal project structure | Yes, to `origin/main` on 2026-10-26 (verified with `git ls-remote`) |
