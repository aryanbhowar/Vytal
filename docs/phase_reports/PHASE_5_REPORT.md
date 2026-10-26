# Phase 5 Report: Results Dashboard, Methodology and End-to-End Verification

| | |
|---|---|
| **Project** | Vytal: personalized health-risk assessment web application |
| **Phase** | 5 of 7 (Day 5 in the plan; done on Day 2) |
| **Tasks** | Task 10 (results dashboard), Task 11 (methodology page and end-to-end checks) |
| **Phase status** | **Complete** |
| **Report last updated** | 27 October 2026 |

---

## Summary in plain words

**The whole application now works from start to finish in a real browser.** A person opens Vytal, answers the questions, and sees results calculated by the two trained models on the server. This was tested automatically in Microsoft Edge against the real backend and models, not against made-up data.

The results page shows, for each model:

- the **model estimate** ("Of survey respondents with answers like yours, about 30 in 100 had reported this condition") next to the **US survey average**;
- the **band** (Low, Moderate, Elevated, High) on a coloured scale with a marker showing the person's position, plus how often people in that band actually reported the condition in testing;
- **what moved the estimate**: a bar chart and a list of up to five answers that raised or lowered it, marked when they are something the person can change;
- what the estimate is and is not, and its limitations.

Below that: an urgent-symptoms notice, a "Reading these numbers" panel explaining the difference between a model estimate, the survey average, a band and clinical risk, general suggestions with WHO links, the person's answers (BMI marked as derived), and the disclaimer and data source. Buttons let people **revise answers, print, or start over** (which wipes everything).

If a model is missing, or height and weight weren't given, its card says so plainly and shows **no number**.

A **methodology page** explains the data, models, metrics, bands, limitations and privacy, with the evaluation figures loaded live from the server.

## 1. Phase objective

Present real model output clearly and honestly, explain the method, and prove the full workflow works in a browser.

## 2. Work completed

### Task 10: Results dashboard

| Component | Shows |
|---|---|
| `RiskResultCard` | Estimate, survey average and how they compare (e.g. "4.4× the average"), band chip, band scale, band validation, factors chart and list, limitations, model version; or an honest "Not enough information" / "Estimate unavailable" panel |
| `BandScale` | The four bands as proportions of respondents (50/25/15/10%) and a marker at the person's percentile; a text description for screen readers |
| `ContributionChart` | The real contributions from the API as a two-sided bar chart (rose = raised, teal = lowered); the list below gives the same information as text |
| `SuggestionCard` | Theme, title, guidance and WHO link (opens in a new tab) |
| `ProfileSummary` | Every answer; BMI labelled "derived" with its WHO category |

Wording rules followed: "had reported this condition", never "your risk"; "higher than about N% of survey respondents", never "100th percentile" (shown as "more than 99%"); factors are "associations the model learned, not causes".

### Task 11: Methodology page and end-to-end checks

- **`/methodology`** fetches `/api/models/status` and shows each model's training and test sizes, ROC-AUC, PR-AUC, calibration gap, Brier score, sensitivity, specificity and precision, with plain explanations, the band definitions, seven limitations and the privacy statement.
- **`scripts/run_demo_profiles.py`** sends four documented example profiles to the running backend and checks the replies:

| Profile (made up) | Heart | COPD | Check |
|---|---|---|---|
| 1. 34, female, active, never smoked | 0.4%, Low | 0.4%, Low | Pass |
| 2. 55, male, daily smoker, vapes, inactive, asthma now | 14.6%, Elevated | 67.5%, High | Pass |
| 3. 71, male, former smoker, diabetes, stroke, kidney disease | 73.5%, High | 20.4%, High | Pass |
| 4. 48, female, height and weight unknown | Not enough information | Not enough information | Pass |

These numbers are what the real models returned; they move in the expected directions (for example smoking and asthma dominate the COPD estimate; stroke and kidney disease dominate the heart estimate).

- **Browser tests** (`frontend/e2e/`, Playwright in Edge, real backend): full assessment shows exactly the API's numbers; missing measurements → two honest "Not enough information" cards; answers survive a reload and Start over clears storage; a blocked request shows a retryable error and no result; the first step works with the keyboard only; the methodology page shows the server's live ROC-AUC values; no sideways scrolling at four widths, including the results page.
- **Screenshots** at 1440 px and 375 px were reviewed. Two small layout fixes were made from them (link icons in suggestion cards; band labels on narrow screens), and a duplicated disclaimer at the bottom of the results was removed.

## 3. Important files

| File | What it does |
|---|---|
| `frontend/src/pages/ResultsPage.tsx` | Results dashboard |
| `frontend/src/components/results/*.tsx` | Result card, band scale, chart, suggestions, profile |
| `frontend/src/pages/MethodologyPage.tsx` | Methodology with live figures |
| `frontend/src/test/fixtures.ts` | **TEST FIXTURE** responses for component tests only |
| `frontend/src/pages/pages.test.tsx` | Page tests |
| `frontend/e2e/assessment-flow.spec.ts`, `responsive-layout.spec.ts`, `frontend/playwright.config.ts` | Browser tests |
| `scripts/run_demo_profiles.py` | Demo profiles against the live API |

## 4. Technical decisions and reasons

| Decision | Reason |
|---|---|
| Show estimate + survey average + band together (D-007) | Context makes the number meaningful; no single number stands alone |
| "about N in 100" wording | Natural frequencies are easier to understand than percentages |
| Show the band's tested outcome rate | Proves the band means something and shows how it was validated |
| No number at all when unavailable | Never a guessed or placeholder estimate |
| Playwright with installed Edge (D-019) | Real browser tests without downloading a browser |

## 5. Commands executed

```powershell
cd frontend; npm test; npm run lint; npm run build
npx playwright test
cd ..; .venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
.venv\Scripts\python.exe scripts\run_demo_profiles.py
.venv\Scripts\python.exe -m pytest
```

## 6. Actual tests and outcomes

| Suite | Result |
|---|---|
| pytest (backend, ML, data) | **118 passed** |
| Vitest (frontend units and pages) | **25 passed** |
| Playwright in Edge (real backend and models) | **11 passed** |
| Demo profiles script | **4/4 passed** |
| Lint and build | Pass |

Problems found by the tests and fixed: "Start over" sent people to the questionnaire instead of the home page (the cleared result triggered a redirect); two lint warnings; test selectors that matched several elements.

## 7. Current errors and limitations

| Item | Note |
|---|---|
| Only Edge tested | Chromium-based; Firefox/Safari untested |
| Print layout basic | Readable black-on-white, not designed in detail |
| Explanations for the heart model describe the score before calibration | Stated on the card |

## 8. Dataset and model status

Unchanged.

## 9. Git commit and push status

Recorded in `PROJECT_STATUS.md` after the push.

## 10. Exact next steps

Phase 6: production build (backend serves the website), Dockerfile, GitHub Actions CI, dependency audit, deployment guide. Phase 7: final documentation and a fresh-clone check.

## 11. Decisions requiring your approval

None.
