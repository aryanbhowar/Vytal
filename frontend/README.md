# Vytal frontend

React 19 + TypeScript + Vite. Talks to the FastAPI backend through the Vite dev-server proxy (`/api` → `http://127.0.0.1:8000`).

## Commands (run inside `frontend/`)

| Command | Purpose |
|---|---|
| `npm install` | Install packages (first time only) |
| `npm run dev` | Start the dev server at http://localhost:5173 |
| `npm run build` | Type-check and build to `dist/` |
| `npm run lint` | Lint with oxlint |

Start the backend first (see the root `README.md`), otherwise the page shows "The Vytal API could not be reached".

## Structure

- `src/services/apiClient.ts`: the only place that calls the backend.
- `src/App.tsx`: Task 1 connection-check screen; replaced by routed pages in Task 8.
