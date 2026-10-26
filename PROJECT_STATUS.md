# Vytal: project status

_Last updated: 2026-10-27 (Day 2 of 7), end of Phase 3 (Tasks 1–7 complete)._

## Objective

A maintainable, deployment-ready personalized health-risk assessment web application. A questionnaire feeds a FastAPI backend that runs two trained scikit-learn models (reported coronary heart disease or heart attack; reported COPD, emphysema or chronic bronchitis), both trained on pooled CDC BRFSS 2022–2024 data, and shows results with explanations, suggestions and limitations. It runs without paid services and is **not** clinically validated or suitable for clinical decisions. Plan: [`docs/implementation/MASTER_IMPLEMENTATION_PLAN.md`](docs/implementation/MASTER_IMPLEMENTATION_PLAN.md) (Revision 1).

## Current phase

**Phases 1–3 complete.** Next: **Phase 4** (Task 8 design system and landing page, Task 9 questionnaire).

## Overall completion estimate: about 50%

Method: 13 tasks weighted by effort, about 21 units in total (Revision 1). Done: Tasks 1, 2 (1 unit each), 3, 4, 5, 6 (2 each), 7 (1) ≈ 11 units ≈ 52%, rounded down because the user-facing frontend (the most visible part) has not started. This estimates planned work done, not features working.

## Deliverables

| Status | Deliverable |
|---|---|
| Done (tested) | BRFSS 2022–2024 verified; reproducible preprocessing; heart model (test ROC-AUC 0.810) and COPD model (0.836), calibrated, evaluated, saved with integrity hashes; prediction API with honest failure states, security and privacy controls; 12 sourced suggestion rules; 118 automated tests |
| Done | Data sources, model evaluation reports, model cards, decision log D-001–D-035, Phase 1–3 reports, viva notes for Tasks 1–7 |
| Not started | Tasks 8–13: frontend design system, landing page, questionnaire, results dashboard, methodology page, browser end-to-end tests, production build, Dockerfile, CI, deployment guide, final documentation |

## Known blockers

None.

## Component status

| Area | Status |
|---|---|
| Frontend | Still the Task 1 connection page. Build and lint pass. |
| Backend | `GET /api/health`, `GET /api/health/ready`, `GET /api/models/status`, `POST /api/assessment/predict`. Verified on a live server. |
| Datasets | Verified; processed tables built (not in Git). Heart 1,130,510 rows; COPD 1,127,220 rows. |
| Heart model | v1.0.0. Test: ROC-AUC 0.810, PR-AUC 0.299, Brier 0.0723, calibration error 0.22 points (isotonic calibration). Inputs: age group, sex, BMI, smoking, exercise, diabetes, stroke, kidney disease. |
| Respiratory model | v1.0.0. Test: ROC-AUC 0.836, PR-AUC 0.363, Brier 0.0609, calibration error 0.47 points (no calibration needed). Inputs: age group, sex, BMI, smoking, e-cigarettes, exercise, diabetes, asthma status. |
| Tests | **118 passed** (pytest): API, security, error paths, missing/tampered models, data checks, model artifacts, schema consistency, suggestion rules. Frontend tests not yet set up. |
| Deployment | Not started. No public deployment without explicit approval. |

## Latest working commands (from project root)

```powershell
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r ml\requirements.txt -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload     # API + docs at :8000/docs
cd frontend; npm run dev
# Data and models (only to regenerate): see datasets/README.md steps 1-6
```

## Latest known-good commit

See the Git table.

## Next three actions

1. Task 8: design tokens, glass components, routing, landing page; Vitest setup.
2. Task 9: five-step questionnaire with validation and session persistence, submitting to the real API.
3. Task 10: results dashboard rendering real API responses.

## Decisions needing user input

None.

## Success criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Frontend runs locally | Done (skeleton) |
| 2 | Backend runs locally | **Done** (full API) |
| 3 | Frontend can communicate with backend | Done (health check); assessment flow pending Task 9 |
| 4 | Questionnaire validates inputs | Partial: backend validation done and tested; frontend form pending |
| 5 | BMI calculated correctly where possible | **Done** in backend (tested); frontend preview pending |
| 6 | Dataset provenance documented | **Done** |
| 7 | Heart model training reproducible | **Done** (scripted, seeded) |
| 8 | Respiratory model training reproducible | **Done** |
| 9 | Model artifacts load successfully | **Done** (tested, hash-checked) |
| 10 | Both prediction paths use correct preprocessing | **Done** (API output equals direct model output, tested) |
| 11 | Model evaluation documented honestly | **Done** (generated reports and model cards) |
| 12 | Prediction endpoints return validated structured results | **Done** |
| 13 | Dashboard uses actual model outputs | Not started |
| 14 | Unsupported predictions produce honest error states | **Done** in API (tested); UI pending |
| 15 | Factor explanations technically defensible | **Done** (exact contributions, tested) |
| 16 | Suggestions follow documented rules | **Done** |
| 17 | Design system consistent and responsive | Not started |
| 18 | Important functionality has tests | Partial: backend and ML complete; frontend pending |
| 19 | End-to-end workflow demonstrated | Partial: API end to end on a live server; browser flow pending |
| 20 | Project starts with documented commands | Done for current scope |
| 21 | Git history and status maintained | Ongoing |
| 22 | Phase reports allow resuming work | Phases 1–3 done |
| 23 | Viva notes explain implementation | Partial: Tasks 1–7 |
| 24 | Medical limitations visible and accurate | Partial: API responses and docs; UI pending |
| 25 | Security controls tested | **Done** for the API; HTTPS/proxy for public deployment pending (Task 12) |
| 26 | Privacy controls tested | **Done** for the API |
| 27 | Model artifacts integrity-checked before loading | **Done** |
| 28 | Model cards and data dictionary published | **Done** (model cards, DATA_SOURCES, feature schema) |
| 29 | Subgroup performance reported | **Done** |
| 30 | Production build runs from documented commands | Not started |
| 31 | CI runs tests and build on GitHub | Not started |
| 32 | Browser end-to-end tests pass against real models | Not started |

## Git

| Commit | Message | Pushed |
|---|---|---|
| `e77e07f` | chore: initialize Vytal project structure | Yes |
| `a242a78`, `550b834` | Task 1 status records | Yes |
| `5369140` | docs: adopt Revision 1 production-readiness direction | Yes |
| `aede5e7` | data: acquire and verify BRFSS 2022-2024 variables | Yes |
| (next) | ml + backend: Phases 2–3 | See `git log` |
