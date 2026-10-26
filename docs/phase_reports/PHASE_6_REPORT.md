# Phase 6 Report: Stability, Production Build and Deployment Readiness

| | |
|---|---|
| **Project** | Vytal: personalized health-risk assessment web application |
| **Phase** | 6 of 7 (Day 6 in the plan; done on Day 2) |
| **Tasks** | Task 12 (stability, production build, deployment readiness) |
| **Phase status** | **Complete**, except the Dockerfile, which is written but **not verified** (Docker is not installed) |
| **Report last updated** | 27 October 2026 |

---

## Summary in plain words

Vytal can now run in **production mode**: one command starts a single server that delivers both the website and the API. All 11 browser tests pass against this production server, not just the development setup.

Also added:

- a **release script** that runs every check and builds the site, stopping at the first failure;
- **GitHub Actions CI**, which tests every push automatically. **The first run passed** on GitHub;
- a **dependency audit**: no known vulnerabilities in any Python or JavaScript package;
- a **deployment guide** covering configuration, health checks, a checklist, troubleshooting, rollback, and exactly what is still needed before public or clinical use;
- a **Dockerfile** for container hosting, clearly marked as not yet tested.

## 1. Phase objective

Make the working application repeatable to build, start, check and roll back, and be honest about what separates it from a public deployment.

## 2. Work completed

| Item | Detail |
|---|---|
| Production serving | The backend serves `frontend/dist` when `VYTAL_SERVE_FRONTEND=true`. Website routes such as `/results` return the app; unknown `/api/...` paths still return JSON 404s; files outside the build folder can't be reached |
| `scripts/start_production.ps1` | Checks the build exists, turns API docs off, starts one Uvicorn worker on 127.0.0.1 (no server-version header) |
| `scripts/build_release.ps1` | pytest → `npm ci` → lint → Vitest → build → Playwright (optional `-SkipBrowserTests`) |
| `scripts/start_dev.ps1` | Opens the backend and frontend dev servers in two windows |
| `.github/workflows/ci.yml` | Ubuntu, Python 3.13: all Python tests. Node 24: `npm ci`, lint, tests, build. Read-only permissions |
| `Dockerfile`, `.dockerignore` | Two stages (Node build, Python slim runtime), unprivileged user, readiness health check, only runtime files copied. **Never built** |
| `docs/deployment/DEPLOYMENT.md` | Full guide |
| Playwright config | `VYTAL_E2E_BASE_URL` points the browser tests at any running server, so production mode is tested too |
| Dependency audit | `pip-audit` 2.10.1 added to dev requirements |

## 3. Important files

`scripts/start_production.ps1`, `scripts/build_release.ps1`, `scripts/start_dev.ps1`, `.github/workflows/ci.yml`, `Dockerfile`, `.dockerignore`, `docs/deployment/DEPLOYMENT.md`, `tests/integration/test_production_frontend_serving.py`, `frontend/playwright.config.ts`.

## 4. Technical decisions and reasons

| Decision | Reason |
|---|---|
| One process for website and API (D-018) | Simplest deployment; same origin, so no CORS |
| One Uvicorn worker | Models are tiny and in memory; the rate limiter is per process, so several workers would weaken it |
| Bind to 127.0.0.1 by default | Not exposed to the network unless someone chooses to |
| CI without browser tests | Browser tests use the Windows Edge install; they run locally and in the release script |
| No hosting chosen, nothing deployed publicly | Needs your approval, HTTPS and a privacy review (guide section 7) |

## 5. Commands executed

```powershell
.venv\Scripts\python.exe -m pip_audit -r backend\requirements.txt -r ml\requirements.txt -r requirements-dev.txt
cd frontend; npm audit; npm audit --omit=dev
.venv\Scripts\python.exe -m pytest tests/integration/test_production_frontend_serving.py
powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1
$env:VYTAL_E2E_BASE_URL = "http://127.0.0.1:8000"; npx playwright test
git push   # then queried the GitHub Actions API for the run result
```

## 6. Actual tests and outcomes

| Check | Result |
|---|---|
| Production-serving tests (website routes, static files, API still JSON, path traversal blocked, docs off) | **6 passed** |
| Browser tests against the production server | **11 passed** |
| Full Python suite | **124 passed** |
| `pip-audit` | No known vulnerabilities |
| `npm audit` (all and production only) | 0 vulnerabilities |
| GitHub Actions CI on commit `d83c41c` | **completed, success** (run 40397494983) |
| Docker build | **Not run**: Docker not installed |

## 7. Current errors and limitations

| Item | Note |
|---|---|
| Dockerfile unverified | Must be built and run before use |
| Rate limiter in memory, per process | Public use also needs proxy-level limits |
| No HTTPS locally | Required before any public deployment |
| CI does not run browser tests | Run locally (`npm run test:e2e` or the release script) |

## 8. Dataset and model status

Unchanged.

## 9. Git commit and push status

`d83c41c` "deploy: add production mode scripts, Dockerfile, CI and deployment guide", pushed; CI passed.

## 10. Exact next steps

Phase 7: fresh-clone check, final documentation and status.

## 11. Decisions requiring your approval

None now. Any public deployment will need your approval (hosting provider, account, HTTPS setup).
