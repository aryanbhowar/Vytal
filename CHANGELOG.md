# Changelog

All meaningful changes, newest first. Dates are local (project day in brackets).

## 2026-10-27 (Day 2): Phases 6 and 7, production readiness and handover (release v0.2.0)

### Added
- Production mode (backend serves `frontend/dist`), `scripts/start_production.ps1`, `scripts/build_release.ps1`, `scripts/start_dev.ps1`.
- GitHub Actions CI (Python tests; frontend lint, tests, build); first run passed.
- `Dockerfile` and `.dockerignore` (**not verified**: Docker not installed).
- `docs/deployment/DEPLOYMENT.md`, `docs/architecture/ARCHITECTURE.md`, `docs/DEMO_SCRIPT.md`, `docs/PROJECT_DOCUMENTATION.md`, Phase 6 and 7 reports, viva notes section 10 and quick answers.
- Production-serving tests (6); Playwright can target any server via `VYTAL_E2E_BASE_URL`.
- `pip-audit` in dev requirements; audits found no known vulnerabilities.

### Verified
- Fresh clone set up from the README: 114 passed / 10 skipped (no data), frontend 25 passed, production server gives identical results.

## 2026-10-27 (Day 2): Phases 4 and 5, user interface and end-to-end verification

### Added
- Design system (`frontend/src/styles/`: tokens, global, glass components, layout), reusable components, routing.
- Pages: landing (live model figures), five-step questionnaire (validation, unit switch, BMI preview, session persistence, review/edit), results dashboard (estimates, survey average, band scale with tested outcome rates, contribution chart, suggestions, profile, revise/print/start over), methodology (live metrics), 404.
- Frontend tests: Vitest (25) with labelled TEST FIXTURE responses; Playwright in installed Edge against the real backend (11), including responsive overflow checks and screenshots.
- `scripts/run_demo_profiles.py` (4 documented profiles, all checks pass).
- Decisions D-036, D-037; Phase 4 and 5 reports; viva notes section 9.

### Changed
- Removed the Task 1 connection page and `index.css`.
- `frontend/package.json` renamed to `vytal-frontend` 0.2.0; scripts `test` and `test:e2e`.
- `.gitignore` excludes Playwright output.

### Fixed
- "Start over" redirected to the questionnaire instead of the home page (found by a page test).
- Contrast figures in the design tokens corrected to computed WCAG values.

## 2026-10-27 (Day 2): Phases 2 and 3, models and prediction API

### Added
- Feature schema `ml/feature_definitions/vytal_feature_schema.json` (v1.1.0) and `feature_schema.py`.
- Preprocessing: `brfss_data_extraction.py`, `recode_functions.py`, `dataset_split.py`, `build_model_dataset.py` (step-by-step exclusion counts; summaries committed).
- Training and evaluation: `model_training_config.py`, `train_binary_risk_model.py`, entry points for both models, `evaluation_metrics.py`, `evaluation_report_writer.py`; shared inference `ml/inference/risk_model.py`.
- Models `models/heart/heart_logreg_v1.*` (test ROC-AUC 0.810, isotonic-calibrated) and `models/respiratory/respiratory_logreg_v1.*` (0.836), with SHA-256 integrity hashes.
- Generated evaluation reports, model cards and figures in `docs/model_evaluation/`.
- Backend: schemas, model registry, input preprocessing, interpretation, 12 WHO-sourced suggestion rules, assessment service, `/api/health/ready`, `/api/models/status`, `/api/assessment/predict`, security headers and CSP, body limit, rate limit, friendly errors.
- Tests: suite grows from 15 to 118.
- Docs: `ml/README.md`, `models/README.md`, `backend/README.md`, `.env.example` (all settings), Phase 2 and 3 reports, viva notes sections 6–8, decisions D-029–D-035.

### Changed
- Heavy drinking removed from the heart model (D-029: reverse-causation artefact). Schema 1.0.0 → 1.1.0.
- `tests/integration/test_health_api.py` now runs the app's startup (model loading) through shared fixtures.
- Backend version 0.1.0 → 0.2.0.

## 2026-10-27 (Day 2): Task 2, BRFSS acquisition and verification (Phase 1 complete)

### Added
- `ml/` package: `brfss_sources.py`, `download_brfss_data.py` (CDC, then Internet Archive copy of the official URL; retries; zip check; SHA-256), `brfss_codebook.py` (HTML codebook reader), `brfss_candidate_variables.py`, `inspect_brfss_variables.py`.
- `ml/requirements.txt` (pyreadstat 1.3.7, pyarrow 26.0.0, matplotlib 3.11.2).
- BRFSS 2022, 2023, 2024 data and codebooks downloaded to `datasets/raw/` (ignored by Git) and verified: record counts and all inspected answer counts equal CDC's figures.
- `docs/datasets/brfss_variable_availability.md` (generated) and `datasets/processed/brfss_variable_inspection_summary.json` (aggregate counts).
- `datasets/DATA_SOURCES.md`, `datasets/README.md`.
- Tests: `tests/unit/test_brfss_codebook_parsing.py`, `tests/data/test_brfss_variable_inspection.py` (suite now 15 passing).
- Decisions D-023 to D-028; D-022 verified; D-003 superseded.

### Changed
- Master plan R1.4/R1.5: user sections 7–13 and the pooled heart-model decision folded in.
- Phase report standard gains section 11 "Decisions requiring your approval"; Phase 1 report completed.

## 2026-10-26 (Day 1): Revision 1, direction update

### Changed
- Master plan Revision 1: Vytal is now a maintainable, deployment-ready application (D-017), with engineering autonomy rules and production-readiness additions to Tasks 2, 4–6, 9–13 (security, privacy, artifact hashing, subgroup metrics, weighted prevalence, model cards, production build, Dockerfile, CI, Playwright tests, dependency audit).
- New decisions D-017 to D-021; D-022 (heart model training years) opened for user confirmation.
- `PROJECT_STATUS.md`: new objective, success criteria 25–32, Task 2 paused at user request.
- User-facing wording no longer says "educational prototype"; it still says the app is not a diagnosis and not clinically validated (README, API description, frontend tagline, page meta description, viva notes).

### Verified
- Re-ran `pytest` (2 passed), `npm run build` and `npm run lint` (both passed) on the current files.

## 2026-10-26 (Day 1): Task 1, foundation

### Added
- Approved master plan saved to `docs/implementation/MASTER_IMPLEMENTATION_PLAN.md`.
- Python virtual environment (`.venv`, Python 3.13.15) with pinned backend and test packages (`backend/requirements.txt`, `requirements-dev.txt`).
- FastAPI app (`backend/app/main.py`) with `GET /api/health`, central settings (`backend/app/core/config.py`) and CORS for the Vite dev origin.
- Integration tests `tests/integration/test_health_api.py` and `pytest.ini`.
- React 19 + TypeScript + Vite 8 frontend with a `/api` proxy to the backend, an API client (`src/services/apiClient.ts`) and a connection-status page.
- `scripts/check_environment.ps1`.
- `.gitignore` (excludes venv, node_modules, secrets, raw/interim data, processed CSVs), `.gitattributes` (LF line endings) and `.env.example`.
- Tracking files: `README.md`, `PROJECT_STATUS.md`, this changelog, `docs/decisions/DECISION_LOG.md`, `docs/VIVA_NOTES.md`, `docs/phase_reports/PHASE_1_REPORT.md`.

- `docs/phase_reports/README.md`: the standard for detailed, plain-language phase reports (user requirement); Phase 1 report rewritten to follow it.
- Git identity set for this repository (`aryanbhowar`).

### Removed
- Vite template demo assets (`hero.png`, `react.svg`, `vite.svg`, `icons.svg`, `App.css`).
