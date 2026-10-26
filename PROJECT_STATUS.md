# Vytal: project status

_Last updated: 2026-10-27 (Day 2), end of Phase 1 (Tasks 1–2)._

## Objective

A maintainable, deployment-ready personalized health-risk assessment web application. A questionnaire feeds a FastAPI backend that runs two trained scikit-learn models (reported coronary heart disease or heart attack; reported COPD, emphysema or chronic bronchitis), both trained on pooled CDC BRFSS 2022–2024 data, and shows results with explanations, suggestions and limitations. It runs without paid services and is **not** clinically validated or suitable for clinical decisions. Plan: [`docs/implementation/MASTER_IMPLEMENTATION_PLAN.md`](docs/implementation/MASTER_IMPLEMENTATION_PLAN.md) (Revision 1).

## Current phase

**Phase 1 complete.** Next: **Phase 2** (Task 3 preprocessing, Task 4 heart model, Task 5 COPD model).

## Overall completion estimate: about 10%

Method: 13 tasks weighted by effort, about 21 units in total (Revision 1). Tasks 1 and 2 ≈ 2 units. Estimates planned work done, not features working.

## Deliverables

| Status | Deliverable |
|---|---|
| Done (tested) | Environment; `GET /api/health`; frontend↔backend connection (user confirmed in browser); BRFSS 2022–2024 data and codebooks downloaded and verified; variable inspection with 15 passing tests |
| Done | Master plan Rev. 1; decision log D-001–D-028; `datasets/DATA_SOURCES.md`, `datasets/README.md`; generated availability report; Phase 1 report |
| Not started | Tasks 3–13 (preprocessing, both models, prediction API, suggestions, UI, production work) |

## Known blockers

None.

## Component status

| Area | Status |
|---|---|
| Frontend | Skeleton connection page only. Build and lint pass. |
| Backend | `GET /api/health` only. |
| Datasets | 2022–2024 verified: record counts and all inspected answer counts equal CDC's figures. Obtained via Internet Archive copies of the official URLs because cdc.gov returns 403 here (D-026). |
| Heart model | Inputs decided (D-023). Not trained. |
| Respiratory model | Inputs decided (D-024). Not trained. |
| Tests | pytest 15 passed (2 API, 4 unit, 9 data). Frontend tests not yet set up. |
| Deployment | Not started. |

## Latest working commands (from project root)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r ml\requirements.txt -r requirements-dev.txt
.venv\Scripts\python.exe -m ml.preprocessing.download_brfss_data
.venv\Scripts\python.exe -m ml.preprocessing.inspect_brfss_variables
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
cd frontend; npm run dev
```

## Latest known-good commit

See the Git table.

## Next three actions

1. Task 3: feature schema, recoding and train/validation/test split for both outcomes.
2. Task 4: train and evaluate the heart model; model card.
3. Task 5: train and evaluate the COPD model; model card.

## Decisions needing user input

None.

## Success criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Frontend runs locally | Done (skeleton) |
| 2 | Backend runs locally | Done (skeleton) |
| 3 | Frontend can communicate with backend | Done; user confirmed in browser |
| 4 | Questionnaire validates inputs | Not started |
| 5 | BMI calculated correctly where possible | Not started |
| 6 | Dataset provenance documented | **Done**: `datasets/DATA_SOURCES.md` |
| 7 | Heart model training reproducible | Not started |
| 8 | Respiratory model training reproducible | Not started |
| 9 | Model artifacts load successfully | Not started |
| 10 | Both prediction paths use correct preprocessing | Not started |
| 11 | Model evaluation documented honestly | Not started |
| 12 | Prediction endpoints return validated structured results | Not started |
| 13 | Dashboard uses actual model outputs | Not started |
| 14 | Unsupported predictions produce honest error states | Not started |
| 15 | Factor explanations technically defensible | Not started (method: D-011) |
| 16 | Suggestions follow documented rules | Not started |
| 17 | Design system consistent and responsive | Not started |
| 18 | Important functionality has tests | Partial: health API, codebook reader, data checks |
| 19 | End-to-end workflow demonstrated | Not started |
| 20 | Project starts with documented commands | Done for current scope |
| 21 | Git history and status maintained | Partial (ongoing) |
| 22 | Phase reports allow resuming work | Phase 1 done |
| 23 | Viva notes explain implementation | Partial: Tasks 1–2 |
| 24 | Medical limitations visible and accurate | Partial: README, DATA_SOURCES |
| 25 | Security controls tested | Not started |
| 26 | Privacy controls tested | Not started |
| 27 | Model artifacts integrity-checked before loading | Not started |
| 28 | Model cards and data dictionary published | Partial: data sources and availability report |
| 29 | Subgroup performance reported | Not started |
| 30 | Production build runs from documented commands | Not started |
| 31 | CI runs tests and build on GitHub | Not started |
| 32 | Browser end-to-end tests pass against real models | Not started |

## Git

| Commit | Message | Pushed |
|---|---|---|
| `e77e07f` | chore: initialize Vytal project structure | Yes |
| `a242a78` | docs: record Task 1 commit and push status | Yes |
| `550b834` | docs: record browser confirmation of API connection | Yes |
| `5369140` | docs: adopt Revision 1 production-readiness direction | Yes |
| (next) | data: acquire and verify BRFSS 2022-2024 variables | See `git log` |
