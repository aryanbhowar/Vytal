# Vytal viva notes

Plain-language explanations of how Vytal works, written as each part is built. Each section answers: what it does, why it is needed, its inputs and outputs, how it connects to the rest, and how to explain it in the viva.

---

## 1. The big picture (Task 1)

**What Vytal is:** a website where someone answers health and lifestyle questions and gets two estimates: one about heart disease and one about COPD. The estimates come from machine-learning models trained on a large US health survey (BRFSS). It is built like real production software: validated inputs, tests, security and privacy controls, and a repeatable way to deploy it.

**Production-ready vs clinically validated:** these are different things. "Production-ready" is about the software: it runs reliably, is tested, secure and maintainable. "Clinically validated" would mean doctors and regulators have tested it on real patients and approved it for medical use. Vytal aims for the first. It has not had the second, and no amount of code or documentation can provide it.

**What Vytal is not:** a diagnosis. The survey asks people whether a doctor has *ever told them* they have a condition. So the models learn "people with these answers more often reported this condition". They do not predict whether you will get the disease in future.

**The three parts:**

| Part | Technology | Job |
|---|---|---|
| Frontend | React + TypeScript, built with Vite | The pages the user sees and clicks |
| Backend | Python + FastAPI | Checks the answers, runs the models, returns results |
| ML pipeline | Python + pandas + scikit-learn | Run once, offline: cleans survey data and trains the models |

**How to explain it:** "The browser sends the user's answers as JSON to the backend. The backend checks them, converts them into the exact format the model was trained on, runs the saved model, and sends back the result. The model itself was trained earlier by a separate script, so the website never retrains anything."

---

## 2. Backend foundation (Task 1)

**What it does:** `backend/app/main.py` creates the FastAPI application. Right now it has one endpoint, `GET /api/health`, which replies `{"status": "ok", "app": "Vytal", "version": "0.1.0"}`.

**Why it is needed:** the health endpoint is the simplest proof that the server is running. The frontend calls it to show "API connected", and the tests call it to check the app starts.

**Inputs/outputs:** no input; returns a small JSON object.

**Connections:**
- `app/core/config.py` holds settings (name, version, allowed browser origins) in one place, so they are not repeated across files.
- `app/api/health_routes.py` defines the endpoint as a *router*. Later routers (models status, predictions) are added the same way, keeping each file small.
- CORS middleware allows the frontend's address to call the API. In development the Vite proxy (below) makes this mostly unnecessary.

**Key terms:**
- *Endpoint:* a URL the server responds to, like `/api/health`.
- *FastAPI:* a Python web framework that turns functions into endpoints and uses Pydantic to check the shape of data.
- *Pydantic model:* a Python class describing the fields and types of some JSON. `HealthResponse` says the reply has three text fields.

---

## 3. Frontend foundation (Task 1)

**What it does:** a React page that calls `/api/health` when it loads and shows either "API connected", a "checking" message, or an error.

**Why it is needed:** it proves the two halves can talk before any real features are built.

**Connections:**
- `src/services/apiClient.ts` is the only file that calls the backend. Pages call its functions instead of using `fetch` everywhere. If the server is down, it turns the failure into a readable message.
- `vite.config.ts` sets a *proxy*: when the browser asks the frontend server (port 5173) for `/api/...`, Vite forwards the request to the backend (port 8000). The browser sees one address, which avoids cross-origin (CORS) problems.

**How to explain it:** "The page has three possible states: checking, connected, failed. React stores the current state and redraws the page when it changes."

---

## 4. Tests and tooling (Task 1)

- `tests/integration/test_health_api.py` uses FastAPI's `TestClient`, which calls the app in memory without starting a real server. It checks the health reply and that unknown URLs return 404 without leaking error details.
- `pytest.ini` tells pytest where the code lives.
- `npm run build` type-checks the TypeScript and builds the frontend; if it succeeds, the code has no type errors.
- `scripts/check_environment.ps1` checks Python, Node, npm, Git versions and the Git identity.

---

## 5. The data: BRFSS 2022–2024 (Task 2)

**What BRFSS is:** the Behavioral Risk Factor Surveillance System, a yearly CDC telephone survey of about 430,000–460,000 US adults about their health and habits. It is the largest continuous health survey in the world.

**Why it was chosen:** it is official, free, public-domain US government data with a codebook explaining every answer; both of Vytal's outcomes (heart disease and COPD) are in the same files; and the sample is huge.

**What the outcomes really mean (be precise in the viva):**
- Heart: `_MICHD` = the person said a health professional had *ever* told them they had a heart attack or coronary heart disease.
- COPD: `CHCCOPD3` = *ever* told they had COPD, emphysema or chronic bronchitis.
So the models learn "people who answer like you more often *reported* this condition". That is an association, not a prediction of the future and not a diagnosis.

**Why pooling three years is allowed:** each year interviews different people, so there are no repeated people. The questions used were checked to be worded and coded the same way every year. If they weren't, combining them would mix different meanings.

**How the files were checked:** CDC blocks automated downloads from this PC, so the files came from the Internet Archive's copy of CDC's own links. The script proved they are genuine by matching CDC's published numbers: the number of interviews per year, and the number of people giving each answer to every checked question. A damaged or altered file could not match hundreds of counts.

**Why blood pressure and cholesterol are missing:** CDC only asked them in 2023 (odd years). A model pooled across 2022–2024 can only use questions asked every year.

**Missing answers:** "don't know" or "refused" is never treated as "no". Those interviews are left out (about 15–19%). The people left out reported the conditions at almost the same rate as everyone else (under 1 percentage point different), so this hardly changes the data.

**Weighted vs unweighted:** the survey deliberately interviews more of some groups. In the sample about 9% reported heart disease; after CDC's weights correct for who was interviewed, the US adult figure is about 6.5–6.9%. The app shows the weighted figure as the "survey average".

**Key files:** `ml/preprocessing/download_brfss_data.py` (get the data), `inspect_brfss_variables.py` (check it), `ml/feature_definitions/brfss_candidate_variables.py` (which questions and which answer codes are unusable), `datasets/DATA_SOURCES.md` (the full story).

---

## Sections to be added

- Cleaning and recoding (Task 3)
- Training, metrics and calibration (Tasks 4–5)
- Prediction API, categories and factor explanations (Task 6)
- Suggestion rules (Task 7)
- Frontend design system, questionnaire and dashboard (Tasks 8–11)
