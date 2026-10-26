# Phase 1 Report: Foundation and Dataset Decisions

| | |
|---|---|
| **Project** | Vytal: personalized health-risk assessment web application |
| **Phase** | 1 of 7 (Day 1) |
| **Tasks** | Task 1 (foundation and runnable skeleton), Task 2 (BRFSS data download and variable checks) |
| **Phase status** | **Complete** |
| **Report last updated** | 27 October 2026 |

---

## Summary in plain words

Phase 1 had two jobs: get a working software skeleton in place, and find out exactly what the survey data can and cannot support before any model is built.

**Task 1** produced a small but real application: a Python backend that answers at `/api/health`, a React website that connects to it (you confirmed "API connected" in your browser), automated tests, tracking documents and a GitHub repository.

**Task 2** downloaded the CDC BRFSS survey files for 2022, 2023 and 2024 (about 1.3 million interviews in total) and checked every question we were considering using. The main findings:

- **Both models can be trained on all three years pooled together.** The heart disease question and the COPD question are worded and coded identically in all three years, and so are all the risk-factor questions we chose.
- **Blood pressure and cholesterol cannot be used.** They were only asked in 2023. You had accepted this possibility when choosing to pool the years.
- **The downloaded files are complete and genuine.** CDC's website blocks automated downloads from this computer, so the files came from the Internet Archive's saved copy of CDC's own download links. To be sure they are the real thing, the script compared them with CDC's published numbers: the number of interviews in each file and the number of people giving each answer to every question we checked match CDC's official codebook exactly.
- About 1.09 million interviews are usable for the heart model and 1.13 million for the COPD model.

Between the two tasks, the project direction changed to "production-ready software" (Revision 1 of the master plan), and you chose to pool 2022–2024 for the heart model.

---

## 1. Phase objective

Every later step depends on two things: software that starts and communicates, and data whose meaning is understood. If either is wrong, the work built on top of it is wasted. Phase 1 settles both before any feature work.

| Task | Goal | Done? |
|---|---|---|
| Task 1 | Tools installed; backend and frontend that communicate; tests; tracking files; Git | Yes |
| Task 2 | Download BRFSS 2022–2024; verify the outcome and feature questions in each year; decide the final model inputs; document the data | Yes |

---

## 2. Work completed

### Task 1: Foundation

1. **Saved the approved plan** to `docs/implementation/MASTER_IMPLEMENTATION_PLAN.md`.
2. **Checked the tools:** Python 3.13.15, Node.js 26.12.1, npm 11.20.0, Git 2.56.0. Git's name and email were set for this project (`aryanbhowar`).
3. **Created a Python virtual environment** (`.venv`): a private copy of Python for this project so its packages don't affect anything else. Package versions are pinned, because a saved model usually only loads with the same scikit-learn version that created it.
4. **Built the backend skeleton:** FastAPI app with `GET /api/health`, which replies `{"status": "ok", "app": "Vytal", "version": "0.1.0"}`.
5. **Built the frontend skeleton:** React + TypeScript (Vite), a page that shows whether the backend is reachable, and a *proxy* so the browser can reach the backend without security errors.
6. **Proved the two halves talk:** requests to the backend directly and through the frontend proxy both returned success; you confirmed the page in your browser.
7. **Created tracking files** (status, changelog, decision log, viva notes, this report) and **set up Git and GitHub**.

### Direction update (between the tasks)

The goal changed from "educational prototype" to **production-ready software**: reliable, tested, secure, private and deployable, while still never claiming to be clinically validated. The plan gained a Revision 1 section listing the extra work (security protections, privacy rules, model file checks, fairness checks, model cards, a production build, automated tests on GitHub, real-browser tests). You also decided to **pool 2022–2024 for the heart model**, subject to the data checks below.

### Task 2: Getting and checking the data

**Step 1: Tried CDC directly.** Every automated request to cdc.gov, even for plain web pages, was refused with "HTTP 403 Access Denied" (CDC's content network blocks it). This is a block on automated access from this computer, not a problem with the files.

**Step 2: Used the Internet Archive's copy of CDC's own links.** The Internet Archive (web.archive.org) stores copies of public web pages and files. It holds copies of the exact CDC download links for all three years. The download script asks for the *original bytes* of those copies. 2023 failed once on a dropped connection, so the script was given automatic retries; it then succeeded.

| Year | Zip size | Unzipped `.XPT` file |
|---|---|---|
| 2022 | 84.6 MB | 1.16 GB |
| 2023 | 93.2 MB | 1.21 GB |
| 2024 | 83.0 MB | 1.09 GB |

**Step 3: Downloaded the official codebooks.** A *codebook* is CDC's dictionary for the survey: for every question it gives the exact wording, what each answer number means (for example 1 = yes, 2 = no, 7 = don't know, 9 = refused), and how many people gave each answer. These came the same way.

**Step 4: Proved the files are complete and genuine.** The inspection script:

- counted the interviews in each file: 445,132 (2022), 433,323 (2023), 457,670 (2024), **exactly** the numbers on CDC's pages;
- for every question we checked, counted how many people gave each answer and compared that with the codebook: **every count matched exactly** in all three years.

A file that had been altered or cut short would not match on hundreds of separate counts. Each verified file's SHA-256 fingerprint is now recorded, so a future download can be compared with it.

**Step 5: Checked every candidate question across the three years.** For 25 variables (the two outcomes, their parts, 18 possible features and 3 survey-design variables) the script checked:

- Is it in all three years?
- Is the question worded the same way?
- Do the answer codes mean the same thing?

Comparing wording needed care. The codebooks print the same text with different punctuation each year (curly versus straight apostrophes, different dashes) and the "Go to Section 08.01" skip instructions are renumbered every year. The comparison ignores those differences but still catches real changes in meaning. A unit test proves it catches one real change: in 2024 the e-cigarette question reworded answer 4.

**Step 6: Counted usable interviews and checked for bias from exclusions.** When someone answered "don't know" or refused a question the model needs, that interview can't be used (we never treat "don't know" as "no"). The script counted how many are left and whether the removed people differ:

| Model | Usable interviews (all 3 years) | Reported the condition | US adult estimate (weighted) |
|---|---|---|---|
| Heart (CHD or heart attack) | 1,093,195 | about 9% of usable interviews | 6.5–6.9% |
| Respiratory (COPD, emphysema, chronic bronchitis) | 1,127,855 | about 8% | 6.2–6.8% |

People removed for missing answers reported the condition slightly *less* often than people kept (difference under 1 percentage point), so the exclusions make little difference. The "weighted" figure is lower than the sample figure because the survey deliberately interviews more of some groups (such as older adults); CDC's weights correct for that.

**Step 7: Decided the final model inputs** (decisions D-022 to D-028, in plain words in section 4).

**Step 8: Wrote the data documentation**, `datasets/DATA_SOURCES.md` and `datasets/README.md`, and added tests.

---

## 3. Important files created or modified

### Task 1 (summary; details in the Task 1 commit)

| Area | Files |
|---|---|
| Backend | `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/api/health_routes.py`, `backend/requirements.txt` |
| Frontend | `frontend/src/App.tsx`, `frontend/src/services/apiClient.ts`, `frontend/vite.config.ts`, `frontend/index.html` |
| Tests and tools | `tests/integration/test_health_api.py`, `pytest.ini`, `requirements-dev.txt`, `scripts/check_environment.ps1` |
| Settings | `.gitignore`, `.gitattributes`, `.env.example` |
| Tracking | `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, `docs/decisions/DECISION_LOG.md`, `docs/VIVA_NOTES.md`, `docs/phase_reports/` |

### Task 2

| File | What it does |
|---|---|
| `ml/requirements.txt` | Data packages: `pyreadstat` (reads SAS files), `pyarrow` (fast table storage, used from Task 3), `matplotlib` (charts for evaluation) |
| `ml/preprocessing/brfss_sources.py` | Facts about each survey year: CDC's published record counts, download addresses, verified file fingerprints, codebook locations |
| `ml/preprocessing/download_brfss_data.py` | Downloads the data and codebooks (CDC first, then the Internet Archive copy), retries dropped connections, checks the zip, unzips, prints manual instructions if everything fails |
| `ml/preprocessing/brfss_codebook.py` | Reads CDC's HTML codebooks into Python: question text, answer codes, counts and derivation notes |
| `ml/feature_definitions/brfss_candidate_variables.py` | The list of variables considered, their name in each year, which answer codes are unusable, and the chosen features for each model |
| `ml/preprocessing/inspect_brfss_variables.py` | The checker: completeness, cross-year consistency, counts against the codebook, usable sample sizes, exclusion bias; writes the report and summary |
| `docs/datasets/brfss_variable_availability.md` | Generated report with every table and count |
| `datasets/processed/brfss_variable_inspection_summary.json` | The same results as data (totals only, no individual answers); committed so tests can use it |
| `datasets/DATA_SOURCES.md` | Where the data comes from, terms of use, exact outcome definitions, features, exclusions, limitations |
| `datasets/README.md` | Folder layout and the commands to recreate the data |
| `tests/unit/test_brfss_codebook_parsing.py` | Tests the codebook reader and the wording comparison using a small made-up codebook |
| `tests/data/test_brfss_variable_inspection.py` | Tests that the real data still supports the decisions (targets identical in all years, features compatible, blood pressure only in 2023, enough positive cases) |

---

## 4. Technical decisions and reasons

| ID | Decision | Reason in simple terms |
|---|---|---|
| D-017 | Vytal is production-oriented software, never described as clinically validated | Your direction update. Software quality can be built; clinical approval needs trials and regulators |
| D-018 to D-021 | Production build serves the website from the backend; real-browser tests use the installed Edge; model files are fingerprint-checked before loading; show the weighted US prevalence | Production-readiness additions (details in the decision log) |
| D-022 | Pool 2022–2024 for the heart model (replaces D-003, "2023 only") | Your choice. The checks found no reason to stop: the heart outcome is defined identically in all three years |
| D-023 | Heart inputs: age group, sex, BMI, smoking, exercise, heavy drinking, diabetes, stroke, kidney disease | Every one is asked the same way in all three years, is a risk factor or history, and is easy to ask in a form |
| D-024 | COPD inputs: age group, sex, BMI, smoking, e-cigarettes, exercise, diabetes, asthma status | Same checks. Asthma is an *input* only; it is never mixed into the COPD outcome |
| D-025 | No blood pressure or cholesterol | Only asked in 2023, so they can't be used across the three years |
| D-026 | Use the Internet Archive copy of CDC's files, only after checking it against CDC's numbers | CDC blocks automated downloads here; the checks show the files are identical to CDC's |
| D-027 | Use CDC's calculated e-cigarette and heavy-drinking variables | CDC renamed them in 2024 but kept the same definition; the calculated version is unaffected by a 2024 wording change |
| D-028 | Remove interviews with "don't know"/refused answers; keep all four diabetes answers | Never guess that "don't know" means "no". The removed group barely differs. Every diabetes group is big enough |

Other choices: SAS files are read with the Latin-1 text encoding and codebooks with Windows-1252, because that is how SAS on Windows writes them (the default UTF-8 crashed on an accented character). CDC's printed *variable* counts were not used as a completeness test because they are clearly copied template text (2024's page says 345 variables, but its own codebook lists 297; all three pages give the same zip size).

---

## 5. Commands executed

Task 1 commands are unchanged from the earlier version of this report (environment check, `python -m venv .venv`, package installs, `pytest`, `npm create vite`, `npm install/build/lint`, starting both servers, Git setup).

Task 2:

```powershell
# Test whether CDC allows scripted downloads (all returned 403 Access Denied)
Invoke-WebRequest -Method Head https://www.cdc.gov/brfss/annual_data/2023/files/LLCP2023XPT.zip
curl.exe -r 0-1023 -A "<browser user agent>" https://www.cdc.gov/brfss/annual_data/2023/files/LLCP2023XPT.zip

# Ask the Internet Archive whether it holds the official files (it does, for all three years)
curl.exe "https://archive.org/wayback/available?url=www.cdc.gov/brfss/annual_data/2023/files/LLCP2023XPT.zip"

# Install the data packages
.venv\Scripts\python.exe -m pip install pyreadstat pyarrow matplotlib

# Download data and codebooks (2023 retried after a dropped connection)
.venv\Scripts\python.exe -m ml.preprocessing.download_brfss_data
.venv\Scripts\python.exe -m ml.preprocessing.download_brfss_data --years 2023

# Inspect and verify every candidate variable; writes the report and summary
.venv\Scripts\python.exe -m ml.preprocessing.inspect_brfss_variables

# Run all tests
.venv\Scripts\python.exe -m pytest
```

---

## 6. Actual tests and outcomes

| Check | Result |
|---|---|
| Interviews per file equal CDC's published count | **Pass**, all 3 years, exact |
| Answer counts equal the official codebook for all 25 inspected variables | **Pass**, all 3 years, exact |
| Heart outcome `_MICHD` identical across years (wording, codes, derivation) | **Pass** |
| COPD outcome `CHCCOPD3` identical across years | **Pass** |
| All 9 heart and 8 COPD features identical across years | **Pass** |
| Blood pressure and cholesterol available in all years | **Fail as expected**: 2023 only, so they are excluded |
| `pytest` (whole suite) | **15 passed**: 2 health API, 4 codebook reader unit tests, 9 data tests |
| Re-running the downloader with files present | Recognises them, re-checks fingerprints, exit code 0 |
| Frontend build and lint | Pass (last run during the direction update; frontend unchanged since) |

**What a pass means:** the data is complete, genuine and consistent across the three years for every input we will use. It says nothing yet about how well a model will perform; that is Phase 2.

---

## 7. Current errors and limitations

| Item | Effect | Plan |
|---|---|---|
| cdc.gov blocks automated downloads from this computer | Data comes from the Internet Archive copy | Verified against CDC's figures; browser download from CDC also works with the script |
| No blood pressure or cholesterol | Heart model misses two strong risk factors | Stated in the app and model card |
| Survey answers are self-reported, "ever told" | Models learn associations with *reported* conditions, not future risk or diagnosis | Stated everywhere results appear |
| 15–19% of interviews removed for unusable answers | Prevalence shifts by under 1 point | Documented in `DATA_SOURCES.md` |
| US adults only; telephone survey; some states missing in 2023/2024 | Results may not apply elsewhere | Documented |
| Test warning about Starlette and `httpx` | None; tests pass | Watch |

---

## 8. Dataset and model status

| Item | Status |
|---|---|
| BRFSS 2022, 2023, 2024 data and codebooks | Downloaded and verified (in `datasets/raw/`, not in Git) |
| Variable inspection report | `docs/datasets/brfss_variable_availability.md` |
| Final model inputs | Decided (D-023, D-024) |
| Processed training tables | Not yet (Task 3) |
| Heart model, COPD model | Not yet (Tasks 4 and 5) |

---

## 9. Git commit and push status

| Commit | Content | Pushed |
|---|---|---|
| `e77e07f` | Task 1 foundation | Yes |
| `a242a78`, `550b834` | Task 1 status records, browser confirmation | Yes |
| `5369140` | Revision 1 direction update | Yes |
| Task 2 commit | Data acquisition, inspection, documentation | Recorded in `PROJECT_STATUS.md` after the push (a file cannot contain its own commit ID) |

Checked before committing: no data files, `.venv`, `node_modules`, build output or `.env` included. The committed summary JSON contains only totals.

---

## 10. Exact next steps (Phase 2)

1. **Task 3:** extract the chosen columns into compact files, convert CDC's answer codes to readable names (for example `smoking_status = former`), remove unusable rows, split each dataset into training (70%), validation (15%) and test (15%) groups, and write summary counts.
2. **Task 4:** train and evaluate the heart model; write its evaluation report and model card.
3. **Task 5:** the same for the COPD model.

You don't need to do anything for these.

## 11. Decisions requiring your approval

None.
