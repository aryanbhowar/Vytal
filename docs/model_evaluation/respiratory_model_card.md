# Model card: Vytal respiratory model v1.0.0

_Generated from `respiratory_logreg_v1.joblib` metadata on 2026-10-27. Full results: [respiratory_model_evaluation_report.md](respiratory_model_evaluation_report.md)._

## Model details

- **Type:** Logistic regression (scikit-learn), unweighted; BMI as spline; calibration: none needed.
- **Artifact:** `models/respiratory/respiratory_logreg_v1.joblib`, SHA-256 `0de0b6360c2ea42f9ebe3c8268debd6152bad4299ff9582a872a09972e3518b6` (checked before loading).
- **Software:** scikit-learn 1.9.1, Python 3.13.15. Loading with other versions is not supported.

## Intended use

- Health-awareness information inside Vytal: an estimate of how often people with similar survey answers reported the condition, shown with its limitations and general, non-prescriptive suggestions.

## Out-of-scope uses

- Diagnosis, screening decisions, treatment, triage or insurance/employment decisions.
- Predicting future onset of disease.
- Populations outside US adults, or people under 18.
- Reassuring anyone with symptoms: chest pain or severe breathlessness need urgent care regardless of any estimate.

## Training data

- CDC BRFSS 2022, 2023, 2024 (pooled, complete cases); 789,054 training rows.
- Outcome: Ever reported being told by a health professional that they had COPD, emphysema or chronic bronchitis (BRFSS CHCCOPD3).
- Inputs: Age, Sex, Body mass index (from height and weight), Cigarette smoking, Current e-cigarette or vape use, Any physical activity or exercise outside work in the past 30 days, Ever told by a health professional that you have diabetes, Asthma.
- See `datasets/DATA_SOURCES.md` for provenance, exclusions and terms of use.

## Performance (held-out test set)

- ROC-AUC 0.836; PR-AUC 0.363 (outcome rate 8.0%); Brier 0.0609; expected calibration error 0.47%.
- At the reporting threshold: sensitivity 49.7%, specificity 91.2%, precision 32.9%.
- Subgroup results by sex, age group and survey year are in the evaluation report.

## Interpretation

- **Model estimate:** the model's estimated share of similar respondents who reported the condition; validation showed it is well calibrated, so no recalibration was applied.
- **Survey prevalence:** the weighted share of all US adult respondents who reported it (6.4%).
- **Band:** position of the estimate among survey respondents (percentile cut-offs 50/75/90). Not a clinical category.
- **Clinical risk:** not estimated by Vytal. It requires clinical assessment, measurements (e.g. blood pressure, cholesterol) and validated tools.

## Ethical considerations and limitations

- Self-reported, cross-sectional data; associations, not causes. Race, income and education are deliberately not inputs.
- Not clinically validated, not a medical device.
