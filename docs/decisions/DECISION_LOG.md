# Decision log

Decisions that affect later work. Each entry: what was decided, why, and its status. Newest decisions are appended at the end.

| ID | Date | Decision | Reason | Status |
|---|---|---|---|---|
| D-001 | 2026-10-26 | Use raw CDC BRFSS LLCP files as the data source for both models. | Both targets (`_MICHD`, `CHCCOPD3`) are in the same official files with published codebooks. One source means one preprocessing approach and one questionnaire. | Accepted |
| D-002 | 2026-10-26 | Reject the Zenodo "BRFSS 2020 Heart Disease (Cleaned)" dataset (record 15364962). | 2020 data; its documentation contradicts itself on the target (CHD-or-MI vs `CVDINFR4`) and BMI (`_BMI5CAT` vs continuous values); recodes cannot be verified; no COPD target. | Accepted |
| D-003 | 2026-10-26 | Heart model trained on BRFSS **2023 only**. | Keeps the high blood pressure and cholesterol questions, which are believed to be asked only in odd years. Chosen by the user (option 1b). **Must be verified from the 2023 file in Task 2.** | Accepted, pending verification |
| D-004 | 2026-10-26 | Respiratory model trained on BRFSS **2024 + 2023 + 2022**, harmonized per year. | User choice (1c). BRFSS is cross-sectional, so pooled years contain different respondents. Only variables with the same meaning in all three years are used. | Accepted |
| D-005 | 2026-10-26 | Model inputs are risk factors and health history only. Exclude self-rated general health, difficulty walking, and unhealthy-days counts. | Those variables partly reflect the disease itself (reverse causation) and are hard to defend in a viva. User choice (2a). | Accepted |
| D-006 | 2026-10-26 | Exclude race, income and education as features. | Fairness concerns, and not needed for a lifestyle-awareness tool. | Accepted |
| D-007 | 2026-10-26 | Results show category + model estimate + survey average. Probabilities are displayed only after a calibration check. | User choice (2a). An uncalibrated probability could mislead. | Accepted |
| D-008 | 2026-10-26 | Deploy Logistic Regression; evaluate HistGradientBoosting for comparison only. | Logistic Regression gives exact, explainable per-feature contributions. | Accepted |
| D-009 | 2026-10-26 | Train without class weighting; handle imbalance with a validation-chosen threshold for reported metrics. | `class_weight="balanced"` distorts predicted probabilities. | Accepted |
| D-010 | 2026-10-26 | Presentation bands from the user's percentile among training-set predictions: Low <50, Moderate 50–75, Elevated 75–90, High ≥90. | Defensible, documented mapping that does not pretend to be a clinical threshold. | Accepted |
| D-011 | 2026-10-26 | Explanations = log-odds contributions relative to the training mean, per feature. | Exact for a linear model and simple to explain. | Accepted |
| D-012 | 2026-10-26 | No database, accounts or stored health profiles; request bodies are not logged. | Not required for the demo; avoids holding health data. | Accepted |
| D-013 | 2026-10-26 | Commit small model artifacts; never commit raw, interim or processed survey data. | App runs straight after cloning; repository stays small. | Accepted |
| D-014 | 2026-10-26 | Single root `.venv` for backend and ML, called as `.venv\Scripts\python.exe`. | One environment to install; avoids PowerShell execution-policy problems with `Activate.ps1`. | Accepted |
| D-015 | 2026-10-26 | Pin Python packages to the versions installed on the development machine (e.g. scikit-learn 1.9.1). | Saved joblib models reliably load only with the scikit-learn version that created them. | Accepted |
| D-016 | 2026-10-26 | Use the Vite dev-server proxy for `/api` instead of relying on CORS. | The browser talks to one origin; simpler and fewer failure modes. CORS for the dev origin is still allowed as a fallback. | Accepted |

## Open decisions (resolve in Task 2)

- Final feature list for each model and exact variable names per year.
- Whether sparse categories (e.g. diabetes only during pregnancy) are merged.
- What to do if the 2023 file lacks blood pressure or cholesterol questions (ask the user).
