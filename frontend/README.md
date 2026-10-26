# Vytal frontend

React 19 + TypeScript + Vite 8. In development it talks to the FastAPI backend through the Vite proxy (`/api` → `http://127.0.0.1:8000`); in production the backend serves the built files itself.

## Commands (inside `frontend/`)

| Command | Purpose |
|---|---|
| `npm install` | Install packages (first time) |
| `npm run dev` | Dev server at http://localhost:5173 (start the backend first) |
| `npm run build` | Type-check and build to `dist/` |
| `npm run lint` | Lint with oxlint |
| `npm test` | Unit and component tests (Vitest, jsdom) |
| `npm run test:e2e` | Browser tests in the installed Microsoft Edge against the real backend and models (starts both servers if needed) |

## Structure

| Folder | Contents |
|---|---|
| `src/pages/` | `LandingPage`, `assessment/AssessmentPage` + `AssessmentSteps`, `ResultsPage`, `MethodologyPage`, `NotFoundPage` |
| `src/components/layout/` | Navigation (with live service status), footer, logo |
| `src/components/common/` | `GlassCard`, `Button`/`ButtonLink`, notices (disclaimer, loading, error, warning) |
| `src/components/form/` | `NumberField`, `RadioCardGroup`, `StepProgress` |
| `src/components/results/` | `RiskResultCard`, `BandScale`, `ContributionChart` (Recharts), `SuggestionCard`, `ProfileSummary` |
| `src/context/AssessmentContext.tsx` | Answers, step and result; kept in `sessionStorage` (this tab only) |
| `src/config/assessmentQuestions.ts` | Question wording and options (canonical values) |
| `src/services/` | `apiClient.ts` (all HTTP, error mapping), `assessmentService.ts` |
| `src/utils/` | Validation, unit conversion, BMI, formatting |
| `src/styles/` | `tokens.css` (design tokens), `global.css`, `glass.css` (components), `layout.css` (pages) |
| `src/test/` | Test setup and **clearly labelled test fixtures** (never shown to users) |
| `e2e/` | Playwright tests; screenshots go to `e2e/.results/` (not committed) |

Every number on screen comes from the backend. Test fixtures are only used by unit tests.
