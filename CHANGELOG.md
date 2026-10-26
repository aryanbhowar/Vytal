# Changelog

All meaningful changes, newest first. Dates are local (project day in brackets).

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
