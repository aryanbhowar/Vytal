# Deploying Vytal

This guide covers running Vytal in production mode on one machine, the (unverified) container image, configuration, checks, troubleshooting and rollback. **Vytal is not deployed publicly.** Any public deployment needs the project owner's explicit approval and the extra steps in section 7.

## 1. What "production mode" means

One Python process (Uvicorn running FastAPI) serves both the built website (`frontend/dist`) and the API on the same port. There is no database and no external service; the two model files are loaded into memory at startup.

```
Browser ──HTTPS (reverse proxy, public only)──> Uvicorn :8000
                                                 ├─ /            website (frontend/dist)
                                                 ├─ /api/...     API
                                                 └─ models/      loaded once, hash-checked
```

## 2. Requirements

| Item | Version used and tested |
|---|---|
| Windows 11 (Linux expected to work; untested) | — |
| Python | 3.13.15 |
| Node.js (build only) | 26.12.1; Node 24 LTS used in CI and the Dockerfile |
| RAM | About 300 MB for the server (models are a few KB) |

## 3. Local production run (verified)

From the project root:

```powershell
# First time only
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r ml\requirements.txt -r requirements-dev.txt

# Build and check everything (tests, lint, build; -SkipBrowserTests if Edge is unavailable)
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1

# Start
powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1
```

Open http://127.0.0.1:8000. On 2026-10-27 this mode passed all 11 browser tests (Playwright in Edge with `VYTAL_E2E_BASE_URL=http://127.0.0.1:8000`).

The server only needs `backend/`, `ml/feature_definitions/`, `ml/inference/`, `models/` and `frontend/dist/` at runtime. The survey data is **not** needed to run the app.

## 4. Configuration (environment variables)

| Variable | Default | Production value | Purpose |
|---|---|---|---|
| `VYTAL_SERVE_FRONTEND` | `false` | `true` (set by the start script) | Serve `frontend/dist` |
| `VYTAL_FRONTEND_DIST` | `frontend/dist` | — | Location of the built site |
| `VYTAL_MODELS_DIR` | `models` | — | Location of `heart/` and `respiratory/` |
| `VYTAL_ENABLE_API_DOCS` | `true` | `false` (set by the start script) | Interactive docs at `/docs` |
| `VYTAL_ALLOWED_ORIGINS` | Vite dev origins | Leave unset (same origin) | CORS |
| `VYTAL_MAX_REQUEST_BYTES` | `16384` | — | Largest request body |
| `VYTAL_PREDICT_RATE_LIMIT_PER_MINUTE` | `30` | Tune to expected use | Per-IP assessment limit (0 = off) |

No secrets are needed. Never put credentials in the repository; there are none to configure.

## 5. Health checks

| Endpoint | Healthy | Use |
|---|---|---|
| `GET /api/health` | 200 `{"status":"ok"}` | Process is alive (liveness) |
| `GET /api/health/ready` | 200 `{"ready":true,...}`; 503 if a model failed to load | Send traffic only when ready (readiness) |
| `GET /api/models/status` | Lists each model, version and test metrics | Confirm which model version is live |

## 6. Container image (NOT verified)

`Dockerfile` builds the frontend with Node 24, then runs Python 3.13 slim as an unprivileged user with a readiness health check. **Docker was not installed on the development machine, so the image has never been built or run.** Before using it:

```bash
docker build -t vytal:0.2.0 .
docker run --rm -p 8000:8000 vytal:0.2.0
curl http://localhost:8000/api/health/ready
```

## 7. Before any public deployment (requires owner approval)

Running locally is not the same as being production-secure. Before exposing Vytal to the internet:

1. **HTTPS** via a reverse proxy (e.g. Caddy or nginx) or the host's managed TLS. Never serve health answers over plain HTTP.
2. **Proxy-level rate limiting and request limits.** The built-in limiter is per process, in memory and resets on restart. Run Uvicorn with `--proxy-headers --forwarded-allow-ips <proxy IP>` so limits apply to real client IPs.
3. **Add `Strict-Transport-Security`** at the proxy once HTTPS works.
4. **Logging:** keep access logs free of request bodies (the app never logs them); decide a retention period for access logs, which contain IP addresses.
5. **Privacy notice and terms** reviewed for the jurisdiction (the in-app statements describe behaviour but are not legal documents).
6. **Hosting choice:** no host has been selected. Any free tier must be checked for current terms, data location and whether it permits health-related apps; creating an account and publishing require approval.
7. **Monitoring:** poll `/api/health/ready`; alert on 5xx responses.

## 8. Deployment checklist

- [ ] `scripts\build_release.ps1` passes (pytest, lint, Vitest, build, Playwright)
- [ ] CI is green for the commit being deployed
- [ ] `pip-audit` and `npm audit` show no known vulnerabilities (last run 2026-10-27: none)
- [ ] `/api/models/status` shows the expected model versions
- [ ] `/api/health/ready` returns 200
- [ ] `VYTAL_ENABLE_API_DOCS=false`
- [ ] Public only: HTTPS, proxy limits, HSTS, approval recorded

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Header says "Service offline" | Backend not running, or wrong port | Start the backend; check port 8000 is free |
| `/api/health/ready` 503 | A model failed to load | Read the server log: "not found", "failed its integrity check" or "different feature schema" |
| "failed its integrity check" | Model file changed after training, or Git line-ending conversion | Restore from Git (`git checkout -- models/`); `.gitattributes` marks `.joblib` as binary |
| Model loads fail after upgrading packages | scikit-learn version differs from training | Reinstall pinned versions from `backend/requirements.txt`, or retrain |
| `frontend\dist is missing` | Frontend not built | `scripts\build_release.ps1` or `cd frontend; npm run build` |
| 429 errors | Rate limit reached | Wait a minute or raise `VYTAL_PREDICT_RATE_LIMIT_PER_MINUTE` |
| PowerShell refuses to run scripts | Execution policy | Use `powershell -ExecutionPolicy Bypass -File <script>` as shown |

## 10. Rollback

Every release is a Git commit (tagged releases from `v0.2.0`). Models are versioned files in the repository, so code and models roll back together:

```powershell
git fetch --tags
git checkout v0.2.0                 # or a known-good commit hash from PROJECT_STATUS.md
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1 -SkipBrowserTests
powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1
```

Confirm with `/api/models/status` that the expected model version is live.

## 11. What still stands between Vytal and public or clinical use

| Area | Status |
|---|---|
| Public web deployment | Needs HTTPS, proxy limits, hosting decision, legal privacy review and owner approval |
| Clinical use | **Not possible on current evidence.** Would require prospective validation in the intended population, clinical oversight, a regulatory assessment (it may be a medical device in some jurisdictions) and outcome definitions beyond self-report |
| Model limitations | No blood pressure or cholesterol; US survey population; association with reported conditions, not future risk |
| Browser coverage | Tested in Microsoft Edge only |
