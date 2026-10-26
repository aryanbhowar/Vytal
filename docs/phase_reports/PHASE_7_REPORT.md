# Phase 7 Report: Documentation, Handover and Fresh-Clone Verification

| | |
|---|---|
| **Project** | Vytal: personalized health-risk assessment web application |
| **Phase** | 7 of 7 (Day 7 in the plan; done on Day 2) |
| **Tasks** | Task 13 (documentation and handover) |
| **Phase status** | **Complete** |
| **Report last updated** | 27 October 2026 |

---

## Summary in plain words

The project can be **rebuilt from GitHub by following the README alone**, and this was tested. The repository was cloned into an empty folder, set up with only the README's commands, and then:

- the Python tests passed (114 passed; 10 skipped because the survey data isn't downloaded, which is expected);
- the frontend tests passed (25) and the site built;
- the production server started, reported both models ready, and gave **the same results** as the development copy (heart 29.78%, COPD 32.46% for the sample profile).

The documentation is complete: architecture diagrams, a 10-minute demo script, a deployment guide, model cards, evaluation reports, data sources, viva notes with quick answers, one report per phase, and a final status that marks every success criterion honestly.

## 1. Phase objective

Make sure the project's state can be recovered from the repository alone, and that you can explain and demonstrate it.

## 2. Work completed

| Item | Detail |
|---|---|
| Fresh-clone check | `git clone` into `%TEMP%`, `python -m venv`, `pip install` (README commands), `pytest`, `npm ci`, `npm test`, `npm run build`, `scripts/start_production.ps1 -Port 8010`, readiness and a live assessment. Temporary folder deleted afterwards |
| `docs/architecture/ARCHITECTURE.md` | System diagram, request sequence diagram, key design points |
| `docs/DEMO_SCRIPT.md` | Step-by-step demo with the expected live values and backup checks |
| `docs/PROJECT_DOCUMENTATION.md` | Index of all documentation |
| `docs/VIVA_NOTES.md` | Sections 1–10 plus a quick-answer table |
| `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md` | Final state |
| Release tag | `v0.2.0` on the final commit (used by the rollback instructions) |

## 3. Important files

See `docs/PROJECT_DOCUMENTATION.md` for the full map.

## 4. Technical decisions and reasons

| Decision | Reason |
|---|---|
| Verify in a fresh clone, not the working folder | Proves nothing depends on local files that aren't in Git |
| Tag the release | Gives a named point to roll back to |

## 5. Commands executed

```powershell
git clone https://github.com/aryanbhowar/Vytal.git $env:TEMP\vytal_fresh_clone
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r ml\requirements.txt -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest
cd frontend; npm ci; npm test; npm run build; cd ..
powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1 -Port 8010
curl.exe http://127.0.0.1:8010/api/health/ready
Invoke-RestMethod -Method Post http://127.0.0.1:8010/api/assessment/predict -Body <sample>
```

## 6. Actual tests and outcomes

| Check (fresh clone) | Result |
|---|---|
| Python install from the README | Succeeded |
| pytest | **114 passed, 10 skipped** (dataset checks need the uncommitted survey data) |
| `npm ci` | 0 vulnerabilities |
| Vitest | **25 passed** |
| Build | Succeeded |
| Production server readiness | `{"ready":true,"models":{"heart":true,"respiratory":true}}` |
| Home page | HTTP 200 |
| Sample assessment | heart 0.2978 (High), COPD 0.3246 (High): identical to the development copy |

## 7. Current errors and limitations

See `PROJECT_STATUS.md` "Known limitations". Main ones: Dockerfile unverified; only Edge tested; no public deployment; models lack blood pressure and cholesterol; not clinically validated.

## 8. Dataset and model status

Final: heart model v1.0.0 (test ROC-AUC 0.810), COPD model v1.0.0 (0.836). Survey data not in Git; recreated by `datasets/README.md` steps 1–6.

## 9. Git commit and push status

Final documentation commit and tag `v0.2.0`: recorded in `PROJECT_STATUS.md` after the push.

## 10. Exact next steps (optional improvements)

1. Install Docker and verify the image (`docs/deployment/DEPLOYMENT.md` section 6).
2. Test in Firefox and Safari.
3. If public deployment is wanted: choose a host and approve it, then follow section 7 of the deployment guide.
4. Rehearse the demo with `docs/DEMO_SCRIPT.md`.

## 11. Decisions requiring your approval

None for the current scope. Public deployment would need your approval.
