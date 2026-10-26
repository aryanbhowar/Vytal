# Vytal: project status

_Last updated: 2026-10-27 (Day 2 of 7). All 13 planned tasks complete; see "Known limitations" for what remains._

## Objective

A maintainable, deployment-ready personalized health-risk assessment web application. A questionnaire feeds a FastAPI backend that runs two trained scikit-learn models (reported coronary heart disease or heart attack; reported COPD, emphysema or chronic bronchitis), both trained on pooled CDC BRFSS 2022–2024 data, and shows results with explanations, suggestions and limitations. It runs without paid services and is **not** clinically validated or suitable for clinical decisions. Plan: [`docs/implementation/MASTER_IMPLEMENTATION_PLAN.md`](docs/implementation/MASTER_IMPLEMENTATION_PLAN.md) (Revision 1).

## Current phase

**All 7 phases complete.** Remaining work is optional (see "Next actions").

## Overall completion estimate: about 95%

Method: all 13 tasks (about 21 effort units) are done and tested. The missing 5% is the one deliverable that exists but is unverified (Dockerfile) and the untested browsers. This estimates planned work done, not clinical readiness, which is out of scope.

## Deliverables

| Status | Deliverable |
|---|---|
| Done (tested) | Verified BRFSS 2022–2024 data pipeline; heart and COPD models trained, calibrated, evaluated (incl. subgroups), hash-protected; prediction API with validation, honest failure states, security and privacy controls; 12 WHO-sourced suggestion rules; landing page, questionnaire, results dashboard, methodology page; production mode; CI; fresh-clone reproduction |
| Done | Data sources, evaluation reports, model cards, architecture, demo script, deployment guide, viva notes, decision log D-001–D-037, Phase 1–7 reports |
| Written, **not verified** | `Dockerfile` (Docker not installed) |
| Not done (out of scope without approval) | Public deployment |

## Known blockers

None.

## Component status

| Area | Status |
|---|---|
| Frontend | Landing, 5-step questionnaire, results, methodology, 404. Lint and build clean. Tested in Edge at 1440/1024/768/375 px. |
| Backend | `/api/health`, `/api/health/ready`, `/api/models/status`, `/api/assessment/predict`; production mode serves the website. |
| Datasets | Verified; processed tables reproducible (not in Git). |
| Heart model | v1.0.0. Test ROC-AUC 0.810, PR-AUC 0.299, Brier 0.0723, calibration gap 0.22 points (isotonic). |
| Respiratory model | v1.0.0. Test ROC-AUC 0.836, PR-AUC 0.363, Brier 0.0609, calibration gap 0.47 points (no recalibration needed). |
| Tests | pytest **124 passed**; Vitest **25 passed**; Playwright **11 passed** (dev and production servers); demo profiles 4/4; CI passed on GitHub. |
| Security audit | pip-audit and npm audit: no known vulnerabilities (2026-10-27). |
| Deployment | Local production mode verified, including from a fresh clone. Not deployed publicly. |

## Latest working commands (from project root)

```powershell
# Setup (first time)
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r ml\requirements.txt -r requirements-dev.txt
cd frontend; npm install; cd ..

# Develop
powershell -ExecutionPolicy Bypass -File scripts\start_dev.ps1          # http://localhost:5173

# Check and run in production mode
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1   # http://127.0.0.1:8000

# Tests
.venv\Scripts\python.exe -m pytest
cd frontend; npm test; npm run test:e2e
```

## Latest known-good commit

See the Git table (the tag `v0.2.0` marks the final verified release).

## Next three actions (optional)

1. Install Docker and verify the image.
2. Test in Firefox and Safari.
3. Rehearse the demo using `docs/DEMO_SCRIPT.md`.

## Decisions needing user input

None. A public deployment would need approval (host, account, HTTPS).

## Known limitations

- Not clinically validated; estimates are associations with *reported* conditions in US survey data, not diagnoses or future risk.
- No blood pressure or cholesterol (asked only in 2023); heavy drinking removed from the heart model (D-029).
- Heart explanations describe the score before calibration (stated in the UI).
- In-memory per-process rate limiter; public use needs HTTPS and proxy limits.
- Dockerfile unverified; only Microsoft Edge tested.

## Success criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Frontend runs locally | **Done** |
| 2 | Backend runs locally | **Done** |
| 3 | Frontend can communicate with backend | **Done** (browser tests) |
| 4 | Questionnaire validates inputs | **Done** (frontend and backend, tested) |
| 5 | BMI calculated correctly where possible | **Done** (same formula both sides, tested; never guessed) |
| 6 | Dataset provenance documented | **Done** |
| 7 | Heart model training reproducible | **Done** |
| 8 | Respiratory model training reproducible | **Done** |
| 9 | Model artifacts load successfully | **Done** (also from a fresh clone) |
| 10 | Both prediction paths use correct preprocessing | **Done** (API output equals direct model output) |
| 11 | Model evaluation documented honestly | **Done** |
| 12 | Prediction endpoints return validated structured results | **Done** |
| 13 | Dashboard uses actual model outputs | **Done** (browser test compares screen to API) |
| 14 | Unsupported predictions produce honest error states | **Done** (API and UI) |
| 15 | Factor explanations technically defensible | **Done** |
| 16 | Suggestions follow documented rules | **Done** |
| 17 | Design system consistent and responsive | **Done** (4 widths tested) |
| 18 | Important functionality has tests | **Done** (160 automated tests in total) |
| 19 | End-to-end workflow demonstrated | **Done** (Playwright, dev and production) |
| 20 | Project starts with documented commands | **Done** (fresh-clone verified) |
| 21 | Git history and status maintained | **Done** |
| 22 | Phase reports allow resuming work | **Done** (Phases 1–7) |
| 23 | Viva notes explain implementation | **Done** |
| 24 | Medical limitations visible and accurate | **Done** (landing, results, methodology, footer, docs) |
| 25 | Security controls tested | **Done** for the app; HTTPS/proxy needed for public use |
| 26 | Privacy controls tested | **Done** |
| 27 | Model artifacts integrity-checked before loading | **Done** |
| 28 | Model cards and data dictionary published | **Done** |
| 29 | Subgroup performance reported | **Done** |
| 30 | Production build runs from documented commands | **Done** |
| 31 | CI runs tests and build on GitHub | **Done** (first run passed) |
| 32 | Browser end-to-end tests pass against real models | **Done** |

## Git

| Commit | Message | Pushed |
|---|---|---|
| `e77e07f` | chore: initialize Vytal project structure | Yes |
| `a242a78`, `550b834` | Task 1 status records | Yes |
| `5369140` | docs: adopt Revision 1 production-readiness direction | Yes |
| `aede5e7` | data: acquire and verify BRFSS 2022-2024 variables | Yes |
| `5973c8d` | ml, backend: train and evaluate both models and implement prediction API | Yes |
| `a24e894` | frontend: build assessment, results and methodology UI with browser tests | Yes |
| `d83c41c` | deploy: add production mode scripts, Dockerfile, CI and deployment guide | Yes; CI passed |
| (final) | docs: complete handover documentation (tag `v0.2.0`) | See `git log` |
