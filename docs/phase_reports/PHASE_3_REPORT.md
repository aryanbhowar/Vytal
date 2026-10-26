# Phase 3 Report: Prediction API and Health Suggestions

| | |
|---|---|
| **Project** | Vytal: personalized health-risk assessment web application |
| **Phase** | 3 of 7 (Day 3) |
| **Tasks** | Task 6 (backend prediction pipeline), Task 7 (health suggestion rules) |
| **Phase status** | **Complete** |
| **Report last updated** | 27 October 2026 |

---

## Summary in plain words

The backend can now do a **real assessment**. You send it someone's answers; it checks them, works out age group and BMI, runs both trained models, and sends back:

- each model's estimate, the US survey average, the person's percentile and band (Low/Moderate/Elevated/High);
- up to five answers that raised or lowered each estimate the most;
- limitations, a disclaimer and a CDC attribution;
- general health suggestions, each linked to a WHO source.

Example from the live server (a made-up 62-year-old male daily smoker, BMI 30, no exercise, diabetes):

| Model | Estimate | US survey average | Percentile | Band | Biggest factors |
|---|---|---|---|---|---|
| Heart | 29.8% | 6.7% | 95th | High | diabetes ↑, smoking ↑, age ↑, sex ↑, no exercise ↑ |
| COPD | 32.5% | 6.4% | 95th | High | smoking ↑, age ↑, no exercise ↑, diabetes ↑, never had asthma ↓ |

The API is also built defensively: it refuses wrong or unexpected answers with clear messages, never guesses missing height or weight, says honestly when a model is missing or has been tampered with, never shows internal error details, never writes health answers to its logs, limits how often one computer can call it, and tells browsers not to store results.

---

## 1. Phase objective

Connect the trained models to a web API that is correct (served numbers equal evaluated numbers), honest (no invented results), and safe (validation, privacy, security).

| Task | Goal | Done? |
|---|---|---|
| 6 | Request/response schemas, preprocessing, model loading, prediction, interpretation, explanations, errors, security | Yes |
| 7 | Transparent, sourced suggestion rules in the response | Yes |

## 2. Work completed

### How one assessment flows through the backend

```
POST /api/assessment/predict  (JSON answers)
  1. Size limit and rate limit checks            core/security.py
  2. Pydantic validation (types, ranges, allowed  schemas/assessment_schemas.py
     answers, no extra fields)
  3. Age → age group; height + weight → BMI       services/input_preprocessing_service.py
  4. For each model: unavailable? no BMI? else    services/assessment_service.py
     run it
  5. Estimate, percentile, band, factors          services/result_interpretation_service.py
  6. Suggestion rules                              services/health_suggestion_rules.py
  7. JSON response with no-store headers
```

### Task 6 details

- **Inputs collected (11):** age in years, sex, height (cm, optional), weight (kg, optional), smoking, current e-cigarette use, any exercise in the past 30 days, diabetes, stroke ever, kidney disease ever, asthma status. No name, email, date of birth, location or other identifying detail.
- **Models load once at startup** (`model_registry.py`). Before loading each file, its SHA-256 fingerprint is compared with the metadata. A missing file, a fingerprint mismatch, a load error, or a model trained with a different schema version marks that model **unavailable** with a plain public reason.
- **The backend reuses the ML code** (`ml/inference/risk_model.py`) so the estimate a user sees is computed exactly like the evaluated one. A test confirms the API's number equals the model's own output for the same answers.
- **Missing height or weight** → that model returns `insufficient_input` ("Vytal does not guess missing values"). **Implausible BMI** (outside 12–70) → a 422 error asking the user to check units.
- **New endpoints:** `/api/health/ready` (200 only if both models loaded, otherwise 503 listing which one isn't) and `/api/models/status` (each model's version, training data and real test-set metrics, for the methodology page).

### Task 7 details

Twelve rules in `health_suggestion_rules.py`, each with a condition, text, priority and a WHO link (all 11 links checked live: HTTP 200):

| Rule | Shown when |
|---|---|
| Urgent symptoms need care now | Always, first |
| Support to stop smoking | Smokes every day or some days |
| E-cigarettes are not harmless | Uses e-cigarettes now |
| Build up regular physical activity (WHO 150–300 min/week) | No exercise in the past 30 days |
| Support for a healthy weight | BMI 25 or more |
| BMI below healthy range | BMI under 18.5 |
| Keep up diabetes check-ups | Diabetes or prediabetes |
| Stay in touch with your care team | Stroke or kidney disease |
| Review your asthma care | Asthma now |
| Consider a heart health check | Heart band Elevated or High |
| Mention breathing symptoms to a professional | COPD band Elevated or High |
| Know your blood pressure and cholesterol | Always (says what the model can't include) |

The rules never mention medicines, doses, diets or supplements (a test scans every text) and never tell someone they have a condition.

## 3. Important files created or modified

| File | What it does |
|---|---|
| `backend/app/main.py` | App factory: middleware, error handlers, routers, startup model loading, optional frontend serving for production |
| `backend/app/core/config.py` | All settings from environment variables (documented in `.env.example`) |
| `backend/app/core/security.py` | Security headers + CSP, no-store, body size limit, rate limiter |
| `backend/app/core/errors.py` | Plain-language validation errors; generic 500 |
| `backend/app/schemas/assessment_schemas.py` | Exact request and response shapes |
| `backend/app/api/health_routes.py` | Health, readiness, model status |
| `backend/app/api/assessment_routes.py` | The predict endpoint |
| `backend/app/services/*.py` | Registry, preprocessing, interpretation, suggestion rules and service, orchestration |
| `tests/conftest.py` and the test files below | Shared test setup and tests |
| `backend/README.md`, `.env.example` | Documentation |

## 4. Technical decisions and reasons

| ID | Decision | Reason |
|---|---|---|
| D-033 | Show at most 5 factors, ignoring tiny ones (< 0.02 log-odds) | Readable; negligible effects add noise |
| D-034 | WHO sources; two always-on notices | Reputable international guidance; tell users what the model can't do |
| D-035 | Security and privacy controls listed in the decision log | Review items from your section 8 |
| — | Backend imports the ML package for schema and inference | One implementation, so served = evaluated |
| — | Rate limiter is in memory, per IP | Enough for one server; public deployment also needs proxy limits (Task 12) |

## 5. Commands executed

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
Invoke-WebRequest http://127.0.0.1:8000/api/health/ready
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/assessment/predict -Body <sample JSON>
curl.exe -s -o NUL -w "%{http_code}" <each WHO source URL>
```

## 6. Actual tests and outcomes

**Full suite: 118 passed** (`pytest`, 32 s).

| Area | Tests include | Result |
|---|---|---|
| Valid assessment | Both models `ok`; finite estimates in (0, 1); percentile 0–100; band valid; factors and limitations present; BMI 30.0 derived; disclaimer; urgent notice first | Pass |
| Consistency | API estimate equals direct model output; same input → identical response; riskier answers → higher estimates | Pass |
| Invalid input | Age 17 / 121, height 50, weight 400, unknown smoking value, unknown sex, text age → 422 naming the field; missing answer → "This answer is required."; extra field `name` → "not accepted"; BMI out of range → 422 | Pass |
| Honest failure | Missing height → `insufficient_input`, no estimate; one model missing → that model `unavailable`, other works; no models → 503; tampered model → `unavailable` ("integrity"); readiness 503 lists the missing model; no file paths in responses | Pass |
| Security | Headers (nosniff, DENY, no-referrer, CSP); `Cache-Control: no-store`; 20 KB body → 413; broken JSON → friendly 422; rate limit → 429 on the third call when the limit is 2; forced crash → generic 500 with no internal text; distinctive answer values do not appear in logs; docs can be turned off | Pass |
| Unit | Age groups at every boundary; BMI and WHO categories; API answer options equal the schema; rate limiter window | Pass |
| Suggestions | Each rule fires when it should and stays silent otherwise; baseline profile gets only the two always-on notices; unavailable model never triggers result advice; no medicine/diet/supplement words; every rule has a WHO link | Pass |
| Live server | Readiness `{"ready": true}`; sample assessment returned the results shown in the summary | Pass |

## 7. Current errors and limitations

| Item | Note |
|---|---|
| Rate limiter resets on restart and counts per IP | A reverse proxy limit is needed for public deployment |
| No HTTPS locally | Required before any public deployment (Task 12 documents it) |
| Starlette/httpx deprecation warning in tests | Harmless |
| Frontend still shows the Task 1 connection page | Phase 4 |

## 8. Dataset and model status

Unchanged from Phase 2; both models load and serve.

## 9. Git commit and push status

Recorded in `PROJECT_STATUS.md` after the push.

## 10. Exact next steps

Phase 4: design system and landing page (Task 8), then the questionnaire wired to this API (Task 9).

## 11. Decisions requiring your approval

None.
