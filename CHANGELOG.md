# Changelog

All meaningful changes, newest first. Dates are local (project day in brackets).

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
