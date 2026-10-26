# Phase 1 Report: Foundation and Dataset Decisions

| | |
|---|---|
| **Project** | Vytal: Personalized Health Risk Assessment Model and Web Application |
| **Phase** | 1 of 7 (Day 1) |
| **Tasks in this phase** | Task 1 (foundation and runnable skeleton) and Task 2 (BRFSS data download and variable checks) |
| **Phase status** | **In progress.** Task 1 is finished. Task 2 has not started. |
| **Report last updated** | 26 October 2026 |

---

## Summary in plain words

At the start of this phase the project folder `c:\vytal_ty` was completely empty. By the end of Task 1 it contains a small but real working application:

- a **backend** (the Python program that will later run the machine-learning models) that answers a simple "are you alive?" question at `/api/health`;
- a **frontend** (the website the user sees) that asks the backend that question and shows whether the connection works;
- **automated tests** that prove the backend answers correctly;
- **tracking documents** (status, changelog, decision log, viva notes, this report) so anyone can see what has been done and why;
- a **Git repository** linked to GitHub, so every step of progress is saved.

Nothing to do with health predictions exists yet. That is deliberate: the first job is to prove the pieces can talk to each other before building features on top of them. Task 2 (next) will download the CDC survey data and check exactly which questions it contains, which decides what the models can use.

---

## 1. Phase objective

**Why this phase exists:** every later step depends on a working environment. If the backend and frontend can't start, or the data turns out to be missing key questions, everything after that is wasted effort. Phase 1 removes those risks first.

**Goals:**

| Task | Goal | Done? |
|---|---|---|
| Task 1 | Install the tools, create a backend and frontend that can communicate, set up tests, tracking files and Git | Yes |
| Task 2 | Download BRFSS 2022, 2023 and 2024 survey files, check which questions each year contains, and fix the final list of model inputs | Not yet |

---

## 2. Work completed

### Task 1: Foundation (complete)

**Step 1: Saved the approved plan.**
The full plan agreed in Plan Mode was saved to `docs/implementation/MASTER_IMPLEMENTATION_PLAN.md`. Every later task refers back to it, so the plan never has to be re-explained.

**Step 2: Checked the computer's tools.**

| Tool | What it is for | Version found | Minimum needed |
|---|---|---|---|
| Python | Runs the backend and machine learning | 3.13.15 | 3.10 |
| Node.js | Runs the frontend build tools | 26.12.1 | 18 |
| npm | Installs frontend packages | 11.20.0 | — |
| Git | Saves project history | 2.56.0 | — |

Git did not have a name and email set, which it needs to record who made each change. You supplied them (`aryanbhowar`, `aryanbhowar45.sphs@gmail.com`) and they are now set for this project.

**Step 3: Created a Python "virtual environment".**
A virtual environment (`.venv` folder) is a private copy of Python just for this project. Packages installed into it don't affect anything else on the computer, and anyone can recreate it from the list in `backend/requirements.txt`.

Packages installed, and why:

| Package | Version | Why it is needed |
|---|---|---|
| fastapi | 0.162.0 | The web framework for the backend: turns Python functions into web addresses |
| uvicorn | 0.54.0 | The server program that actually runs FastAPI |
| pydantic | 2.14.1 | Checks that incoming data has the right fields and types |
| scikit-learn | 1.9.1 | The machine-learning library (used from Task 4) |
| pandas | 3.1.0 | Works with tables of data (used from Task 2) |
| numpy | 2.5.4 | Fast number calculations, used by pandas and scikit-learn |
| joblib | 1.6.0 | Saves and loads trained models to and from files |
| pytest | 9.1.1 | Runs the automated tests |
| httpx | 0.28.1 | Lets the tests send requests to the backend |

The machine-learning packages were installed now, not later, so their versions are fixed from the start. This matters because a saved scikit-learn model can usually only be loaded by the same scikit-learn version that saved it.

**Step 4: Built the backend skeleton.**
The backend has one endpoint so far:

```
GET /api/health   →   {"status": "ok", "app": "Vytal", "version": "0.1.0"}
```

An *endpoint* is a web address the server responds to. This one just confirms the server is running. Later tasks add `/api/models/status` and `/api/assessment/predict` in the same style.

**Step 5: Built the frontend skeleton.**
The frontend was created with Vite's official starter template (React 19 + TypeScript). The template's demo pictures and styles were deleted because Vytal doesn't use them. In their place:

- a page that calls `/api/health` and shows **"API connected"**, **"Checking API connection…"** or an error message;
- one file (`apiClient.ts`) that handles all communication with the backend;
- a *proxy* setting so the website can reach the backend without browser security errors (explained in section 4);
- a simple Vytal "V" logo for the browser tab.

**Step 6: Proved the two halves talk to each other.**
Both servers were started and requests were sent to them. Both requests returned success (HTTP 200), and the backend's own log showed it received them. Details are in section 6.

**Step 7: Created the tracking and support files.** These are listed in section 3.

**Step 8: Set up Git and GitHub.**
The folder became a Git repository on branch `main`, linked to `https://github.com/aryanbhowar/Vytal.git`. The link was tested and GitHub responded (the repository was empty, as expected). Before committing, the list of files was checked to make sure nothing private or huge was included. The commit and push results are in section 9.

### Task 2: Dataset download and checks (not started)

This begins next. See section 10.

---

## 3. Important files created

### Backend (the Python server)

| File | What it does |
|---|---|
| `backend/app/main.py` | Creates the FastAPI application, allows the frontend's address to call it, and plugs in the endpoints |
| `backend/app/core/config.py` | Stores settings (app name, version, allowed website addresses) in one place |
| `backend/app/api/health_routes.py` | Defines `GET /api/health` |
| `backend/requirements.txt` | Exact list of Python packages the backend needs |
| `backend/README.md` | How to run the backend and what each file does |

### Frontend (the website)

| File | What it does |
|---|---|
| `frontend/src/App.tsx` | The connection-status page (replaced by the real landing page in Task 8) |
| `frontend/src/services/apiClient.ts` | The only file that sends requests to the backend; turns failures into readable messages |
| `frontend/src/index.css` | Temporary dark styling (replaced by the full design system in Task 8) |
| `frontend/vite.config.ts` | Development server on port 5173; forwards `/api` requests to the backend |
| `frontend/index.html` | The HTML page shell, titled "Vytal" |
| `frontend/public/favicon.svg` | The browser-tab icon |
| `frontend/package.json` | Lists frontend packages and commands (`dev`, `build`, `lint`) |
| `frontend/README.md` | Frontend commands and structure |

### Tests and tools

| File | What it does |
|---|---|
| `tests/integration/test_health_api.py` | Two automated tests for the backend (section 6) |
| `pytest.ini` | Tells pytest where the code and tests are |
| `requirements-dev.txt` | Test-only packages (pytest, httpx) |
| `scripts/check_environment.ps1` | Checks the computer has the right tool versions |
| `tests/README.md` | How to run tests and what each test folder is for |

### Project settings

| File | What it does |
|---|---|
| `.gitignore` | Tells Git which files must **never** be uploaded: the virtual environment, `node_modules`, build output, `.env` secrets files and all survey data files |
| `.gitattributes` | Makes line endings consistent, so files look identical on every computer |
| `.env.example` | Documents the one optional setting (`VYTAL_ALLOWED_ORIGINS`). Vytal needs no passwords or API keys |

### Tracking and documentation

| File | What it does |
|---|---|
| `README.md` | Front page of the project: what it is, how to install, run and test it |
| `PROJECT_STATUS.md` | The single place showing current progress, blockers and next steps |
| `CHANGELOG.md` | A dated list of every meaningful change |
| `docs/decisions/DECISION_LOG.md` | Every important decision with its reason (16 so far) |
| `docs/VIVA_NOTES.md` | Beginner-friendly explanations for the viva |
| `docs/implementation/MASTER_IMPLEMENTATION_PLAN.md` | The approved plan for all 13 tasks |
| `docs/phase_reports/README.md` | The standard every phase report follows |
| `docs/phase_reports/PHASE_1_REPORT.md` | This report |

---

## 4. Technical decisions and reasons

Each decision is also recorded in `docs/decisions/DECISION_LOG.md` with an ID.

**Decisions about data and models (made during planning, recorded now)**

| Decision | Reason in simple terms |
|---|---|
| Use the raw CDC BRFSS survey files for both models (D-001) | It is official US government data with published codebooks explaining every answer code. Both conditions (heart disease and COPD) are in the same files |
| Reject the "cleaned" Zenodo dataset (D-002) | It is 2020 data, its own description contradicts itself about what the target column means, its changes can't be checked, and it has no COPD column |
| Heart model uses 2023 data only (D-003) | The blood pressure and cholesterol questions are believed to be asked only in odd years. This is checked against the real file in Task 2 |
| Respiratory model uses 2022 + 2023 + 2024 (D-004) | More data, and each year surveys different people. Only questions asked the same way in all three years are used |
| Inputs are risk factors and history only (D-005) | Questions like "How is your general health?" partly measure the disease itself, which would make the model look better than it really is |
| No race, income or education inputs (D-006) | Fairness concerns, and they aren't needed for lifestyle awareness |
| Logistic Regression is the deployed model (D-008) | Its explanations are exact and can be explained step by step in the viva |

**Decisions about the software (made in Task 1)**

| Decision | Reason in simple terms |
|---|---|
| One shared `.venv` for backend and ML, run as `.venv\Scripts\python.exe` (D-014) | One install for everything. Calling Python directly avoids a Windows security setting that blocks the usual "activate" script |
| Fix exact package versions (D-015) | Saved models may not load with a different scikit-learn version |
| Use a Vite proxy (D-016) | Browsers block a page on one address (port 5173) from calling a server on another (port 8000) unless the server allows it ("CORS"). The proxy makes the browser think everything comes from one address, so this problem doesn't arise. CORS is still allowed as a backup |
| Keep the template's `oxlint` code checker | It came with the template and works; adding ESLint would add many extra packages for no benefit |
| No `.env` loader | There are no secrets to configure, so loading a settings file would be unnecessary code |
| Add `.gitattributes` | Git warned about Windows vs Linux line endings on every file. This setting stops that and keeps files consistent |
| Git name and email set for **this project only**, not globally | Keeps your settings for other projects unchanged |

---

## 5. Commands executed

Commands run during Task 1, in order, with what each one does.

```powershell
# Check tool versions and Git identity
python --version; node --version; npm --version; git --version
git config --global user.name; git config --global user.email     # both were empty

# Create the Python environment and install packages
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" pydantic scikit-learn pandas numpy joblib pytest httpx

# Run backend tests
.venv\Scripts\python.exe -m pytest

# Create and build the frontend
npm create vite@latest frontend --yes -- --template react-ts --no-interactive
cd frontend; npm install; npm run build; npm run lint

# Start both servers and test the connection
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
cd frontend; npm run dev
Invoke-WebRequest http://127.0.0.1:8000/api/health     # backend directly
Invoke-WebRequest http://localhost:5173/api/health     # through the frontend proxy

# Check the environment script works
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1

# Set up Git
git init
git branch -M main
git remote add origin https://github.com/aryanbhowar/Vytal.git
git ls-remote origin                                   # confirms GitHub is reachable
git config user.name "aryanbhowar"
git config user.email "aryanbhowar45.sphs@gmail.com"
git add -A; git status --short                         # check exactly what will be committed
git commit -m "chore: initialize Vytal project structure"
git push -u origin main
```

---

## 6. Actual tests and outcomes

Every result below was actually observed. Nothing is assumed.

| What was tested | How | Result |
|---|---|---|
| Health endpoint replies correctly | Automated test `test_health_endpoint_reports_ok` | **Passed** |
| Unknown addresses return "not found" without leaking internal error details | Automated test `test_unknown_route_returns_404_without_internal_details` | **Passed** |
| Whole Python test suite | `pytest` | **2 passed**, run twice |
| Frontend compiles with no type errors | `npm run build` | **Passed** (output 220.5 kB, 69.1 kB compressed) |
| Frontend code style check | `npm run lint` | **Passed**, no problems found |
| Backend answers directly | Request to `127.0.0.1:8000/api/health` | **HTTP 200**, `{"status":"ok","app":"Vytal","version":"0.1.0"}` |
| Frontend proxy forwards to backend | Request to `localhost:5173/api/health` | **HTTP 200**, same reply; backend log shows it arrived |
| Environment check script | `check_environment.ps1` | All tools OK |
| "API connected" visible in a browser | User opened http://localhost:5173 with both servers running and shared a screenshot | **Confirmed by the user** on 2026-10-26: the page shows "Vytal", the tagline and a teal "API connected (Vytal v0.1.0)" badge |

**What a pass means:** the backend starts, answers correctly, doesn't leak errors, and the frontend can reach it. It does **not** yet mean anything about predictions, which don't exist yet.

---

## 7. Current errors and limitations

| Item | Effect | Plan |
|---|---|---|
| Test warning: "Using `httpx` with `starlette.testclient` is deprecated" | None. Tests still pass. It warns that a future library version will want a different package | Watch for it; change only if it becomes an error |
| Frontend package is named `frontend` (template default) | Cosmetic only | Rename when the frontend is built properly in Task 8 |
| One shell command was interrupted during the work | No effect; it was re-run successfully | None |

---

## 8. Dataset and model status

| Item | Status |
|---|---|
| BRFSS 2022, 2023, 2024 files | Not downloaded yet (Task 2) |
| Which questions each year contains | Not yet checked. In particular, whether 2023 has the blood pressure and cholesterol questions is **unconfirmed** |
| Zenodo "cleaned" heart dataset | Rejected (reasons in section 4) |
| Heart model | Not started |
| Respiratory model | Not started |

During planning, the CDC website blocked automatic page reading (HTTP 403 "Forbidden"). If it also blocks automatic downloads in Task 2, you may need to download three zip files in your browser. Exact links and steps will be given then.

---

## 9. Git commit and push status

| Item | Status |
|---|---|
| Repository | Created, branch `main` |
| Remote | `origin` → `https://github.com/aryanbhowar/Vytal.git` (reachable) |
| Files checked before commit | 39 project files. Confirmed **not** included: `.venv`, `node_modules`, `dist`, `.env`, any data files |
| Commit | `e77e07f` "chore: initialize Vytal project structure" (39 files) |
| Push | **Succeeded.** GitHub's `main` branch points at `e77e07f` (checked with `git ls-remote origin main`). Signing in to GitHub was completed in the browser |
| Follow-up commit | Records this hash in the tracking files (`docs: record Task 1 commit and push status`) |

---

## 10. Exact next steps

**Task 2: BRFSS download and variable checks**

1. Add `ml/requirements.txt` with the data-reading packages (`pyreadstat`, `pyarrow`, `matplotlib`) and install them.
2. Write `ml/preprocessing/download_brfss_data.py` to download the 2022, 2023 and 2024 survey zip files into `datasets/raw/`, check their size and unzip them. If CDC blocks it, print step-by-step manual download instructions.
3. Write `ml/preprocessing/inspect_brfss_variables.py` to read only the list of columns and the answer counts for the candidate questions, without loading the whole 1 GB file into memory.
4. Produce `docs/datasets/brfss_variable_availability.md`: a table showing which question exists in which year, and what each answer code means.
5. **If 2023 lacks blood pressure or cholesterol, stop and ask you** what to do.
6. Fix the final list of inputs for each model in the decision log.
7. Write `datasets/DATA_SOURCES.md` and `datasets/README.md`.
8. Add a test that checks both target columns exist in the years that need them.
9. Finish this report (Task 2 sections), update status files, commit and push.

**What you may need to do in Task 2:** possibly download three files in your browser, and possibly make one decision about the heart model's data.
