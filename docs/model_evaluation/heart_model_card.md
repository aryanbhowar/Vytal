# Model card: Vytal heart model v1.0.0

_Generated from `heart_logreg_v1.joblib` metadata on 2026-10-27. Full results: [heart_model_evaluation_report.md](heart_model_evaluation_report.md)._

## Model details

- **Type:** Logistic regression (scikit-learn), unweighted; BMI as spline; calibration: isotonic (fitted on validation).
- **Artifact:** `models/heart/heart_logreg_v1.joblib`, SHA-256 `ea09470db43de6bd7fe961b7b5e0664c2cab8cbcf6615ddb5840326c39c09be7` (checked before loading).
- **Software:** scikit-learn 1.9.1, Python 3.13.15. Loading with other versions is not supported.

## Intended use

- Health-awareness information inside Vytal: an estimate of how often people with similar survey answers reported the condition, shown with its limitations and general, non-prescriptive suggestions.

## Out-of-scope uses

- Diagnosis, screening decisions, treatment, triage or insurance/employment decisions.
- Predicting future onset of disease.
- Populations outside US adults, or people under 18.
- Reassuring anyone with symptoms: chest pain or severe breathlessness need urgent care regardless of any estimate.

## Training data

- CDC BRFSS 2022, 2023, 2024 (pooled, complete cases); 791,357 training rows.
- Outcome: Ever reported being told by a health professional that they had a heart attack (myocardial infarction) or coronary heart disease (BRFSS _MICHD).
- Inputs: Age, Sex, Body mass index (from height and weight), Cigarette smoking, Any physical activity or exercise outside work in the past 30 days, Ever told by a health professional that you have diabetes, Ever told you had a stroke, Ever told you had kidney disease (not stones, bladder infection or incontinence).
- See `datasets/DATA_SOURCES.md` for provenance, exclusions and terms of use.

## Performance (held-out test set)

- ROC-AUC 0.810; PR-AUC 0.298 (outcome rate 9.1%); Brier 0.0723; expected calibration error 0.22%.
- At the reporting threshold: sensitivity 54.4%, specificity 85.5%, precision 27.3%.
- Subgroup results by sex, age group and survey year are in the evaluation report.

## Interpretation

- **Model estimate:** the model's estimated share of similar respondents who reported the condition (calibrated).
- **Survey prevalence:** the weighted share of all US adult respondents who reported it (6.7%).
- **Band:** position of the estimate among survey respondents (percentile cut-offs 50/75/90). Not a clinical category.
- **Clinical risk:** not estimated by Vytal. It requires clinical assessment, measurements (e.g. blood pressure, cholesterol) and validated tools.

## Ethical considerations and limitations

- Self-reported, cross-sectional data; associations, not causes. Race, income and education are deliberately not inputs.
- Not clinically validated, not a medical device.
