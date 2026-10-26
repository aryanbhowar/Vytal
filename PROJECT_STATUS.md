# Vytal: project status

_Last updated: 2026-10-26 (Day 1), after Task 1 and the Revision 1 direction update._

## Objective

A maintainable, deployment-ready personalized health-risk assessment web application. A questionnaire feeds a FastAPI backend that runs two trained scikit-learn models (reported coronary heart disease or heart attack; reported COPD, emphysema or chronic bronchitis, both from CDC BRFSS survey data) and shows results with explanations, suggestions and limitations. It runs without paid services and is **not** clinically validated or suitable for clinical decisions. Full plan: [`docs/implementation/MASTER_IMPLEMENTATION_PLAN.md`](docs/implementation/MASTER_IMPLEMENTATION_PLAN.md) (Revision 1).

## Current phase

**Phase 1 (Day 1): Foundation and dataset decisions.** Task 1 is done. Task 2 (BRFSS download and variable verification) is next and **paused at the user's request** until the full direction update has been received.

## Overall completion estimate: about 5%

Method: the 13 tasks weighted by expected effort. Revision 1 added production-readiness work (mostly to Tasks 6, 11, 12), raising the total from 19 to about 21 units. Task 1 is about 1 unit ≈ 5%. This estimates planned work done, not features working.

## Deliverables

| Status | Deliverable |
|---|---|
| Done (tested, re-verified after Revision 1) | Python environment with pinned packages; `GET /api/health`; frontend connects to backend via Vite proxy (user confirmed in browser); environment check script; Git repo with remote and identity |
| Done | Master plan (Revision 1), decision log (D-001 to D-022), README, changelog, viva notes (Task 1 sections), phase report standard, Phase 1 report (Task 1 part) |
| Not started | Tasks 2–13, including the Revision 1 additions: security headers and limits, privacy controls, model artifact hashing, subgroup evaluation, model cards, data dictionary, production build, Dockerfile, CI, Playwright tests, dependency audit, deployment guide |

## Known blockers

None technical. Waiting on the user for: the rest of the direction update message (it ended mid-sentence in section 7), and D-022 (heart model training years).

## Component status

| Area | Status |
|---|---|
| Frontend | Vite 8 + React 19 + TypeScript skeleton; connection-status page (to be replaced by the full application in Tasks 8–11). `npm run build` and lint pass. |
| Backend | FastAPI app with `GET /api/health` only. 2 tests pass. |
| Datasets | Not downloaded. Zenodo cleaned dataset rejected (D-002). BRFSS variable availability not yet verified. |
| Heart model | Not started. Training years open (D-022). |
| Respiratory model | Not started. |
| Tests | pytest: 2 passed (re-run 2026-10-26 after Revision 1). Frontend: build and lint pass; Vitest (Task 8) and Playwright (Tasks 11–12) not yet set up. |
| Deployment | Not started (Task 12). No public deployment without explicit approval. |

## Latest working commands (from project root)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
cd frontend; npm run dev      # http://localhost:5173
cd frontend; npm run build
```

## Latest known-good commit

See the Git table below.

## Next three actions

1. Receive the remainder of the direction update and the D-022 answer; fold both into the plan.
2. Task 2: add `ml/requirements.txt` and the BRFSS download script; download 2022, 2023, 2024 (scripted, or manual fallback).
3. Task 2: inspect candidate heart and respiratory variables in all three years; settle feature lists; write `datasets/DATA_SOURCES.md`.

## Decisions needing user input

- **D-022:** heart model on 2023 only with blood pressure and cholesterol (current decision), or pooled 2022–2024 with only shared inputs?
- The rest of the direction update (from section 7 onward).

## Success criteria

Criteria 1–24 come from the original brief; 25–32 were added by Revision 1.

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
| 17 | Design system consistent and responsive | Not started |
| 18 | Important functionality has tests | Partial: health endpoint only |
| 19 | End-to-end workflow demonstrated | Not started |
| 20 | Project starts with documented commands | Done for skeleton (README) |
| 21 | Git history and status maintained | Partial: commits pushed (see Git table) |
| 22 | Phase reports allow resuming work | Partial: Phase 1 report covers Task 1 |
| 23 | Viva notes explain implementation | Partial: Task 1 sections written |
| 24 | Medical limitations visible and accurate | Partial: README statement only |
| 25 | Security controls (strict schemas, size limit, headers, generic errors) tested | Not started |
| 26 | Privacy controls (no identifiers, no storage, no body logging, no-store) tested | Not started |
| 27 | Model artifacts integrity-checked before loading | Not started |
| 28 | Model cards and data dictionary published | Not started |
| 29 | Subgroup performance reported | Not started |
| 30 | Production build runs from documented commands | Not started |
| 31 | CI runs tests and build on GitHub | Not started |
| 32 | Browser end-to-end tests pass against real models | Not started |

## Git

| Commit | Message | Pushed |
|---|---|---|
| `e77e07f` | chore: initialize Vytal project structure | Yes, verified with `git ls-remote` |
| `a242a78` | docs: record Task 1 commit and push status | Yes |
| `550b834` | docs: record browser confirmation of API connection | Yes (last known-good before Revision 1) |
| Revision 1 commit | docs: adopt Revision 1 production-readiness direction | See `git log` (a file cannot contain its own commit ID) |
