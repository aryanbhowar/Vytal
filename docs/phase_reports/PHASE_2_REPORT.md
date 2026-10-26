# Phase 2 Report: Data Preparation and Model Training

| | |
|---|---|
| **Project** | Vytal: personalized health-risk assessment web application |
| **Phase** | 2 of 7 (Day 2) |
| **Tasks** | Task 3 (preprocessing), Task 4 (heart model), Task 5 (COPD model) |
| **Phase status** | **Complete** |
| **Report last updated** | 27 October 2026 |

---

## Summary in plain words

Vytal now has **two real, trained and honestly evaluated machine-learning models**:

| Model | What it estimates | Trained on | How well it ranks people (ROC-AUC, test set) | Are its percentages trustworthy? |
|---|---|---|---|---|
| Heart | Chance of having *reported* coronary heart disease or a heart attack | 791,357 survey answers | **0.810** | Yes: estimates are on average within 0.22 percentage points of what actually happened |
| Lungs (COPD) | Chance of having *reported* COPD, emphysema or chronic bronchitis | 789,054 survey answers | **0.836** | Yes: within 0.47 points on average |

ROC-AUC of 0.81–0.84 means: pick one person who reported the condition and one who didn't; about 81–84 times out of 100 the model gives the first person the higher estimate (50 would be guessing). That is solid for a model using only nine or so simple questions, and **modest** compared with clinical tools that use blood tests and blood pressure.

To get there, the survey data was cleaned into two model-ready tables, each split into training, validation and test groups; the models were fitted, checked for calibration, and evaluated once on data they had never seen. Every number is in auto-generated reports and model cards.

One finding changed the plan: in the first heart model, **heavy drinkers got lower heart estimates**. That is a known trap in survey data (many people cut down after a heart diagnosis), not a real protective effect. Showing anyone "heavy drinking lowered your estimate" would be wrong and harmful, so heavy drinking was removed from the heart model (decision D-029). Accuracy barely changed.

---

## 1. Phase objective

Turn the verified survey data into trustworthy models: clean, reproducible inputs; a model per outcome; honest evaluation with more than accuracy; saved files the backend can load safely.

| Task | Goal | Done? |
|---|---|---|
| 3 | Reproducible preprocessing: recode answers, exclude unusable ones, split the data | Yes |
| 4 | Train, calibrate, evaluate and save the heart model; report and model card | Yes |
| 5 | The same for the COPD model, plus a check across years | Yes |

---

## 2. Work completed

### Task 3: Preparing the data

1. **One feature schema for everything.** `ml/feature_definitions/vytal_feature_schema.json` lists every input, its allowed answers in readable form (e.g. `smoking_status`: `current_daily`, `current_some_days`, `former`, `never`), which CDC code each answer comes from, and which model uses it. Training, the API and the saved models all follow this one file, and tests check they agree.
2. **Extraction.** Reading a 1.1 GB survey file takes about a minute, so the 15 needed columns were copied once into small files (about 5 MB per year).
3. **Recoding.** CDC numbers became readable values, e.g. `_SMOKER3 = 3` → `former`. Codes meaning "don't know", "refused" or "missing" became *empty*, never "no". BMI is stored by CDC with two hidden decimals (2534 = 25.34) and was divided by 100; values outside 12–70 (0.06% of values, almost certainly typing errors) were treated as unusable.
4. **Exclusions, step by step.** For each year, the script removed rows with an unusable outcome, then rows with an unusable answer for each input in turn, and recorded how many each step removed (in `datasets/processed/*_summary.json`). BMI was the biggest cause (about 9–11% of rows).
5. **Split.** Each dataset was divided 70% / 15% / 15% into **training** (the model learns from it), **validation** (used to make choices) and **test** (used once, at the end, to measure performance). The split is *stratified* (each part has the same share of positive cases and the same mix of years) and *seeded* (identical every run).

| Dataset | Rows | Reported the condition | US adult estimate (weighted) |
|---|---|---|---|
| Heart | 1,130,510 | 102,951 (9.11%) | 6.72% |
| COPD | 1,127,220 | 89,998 (7.98%) | 6.42% |

### Tasks 4 and 5: Training and evaluating the models

The same steps were used for both models (one shared training script):

1. **Fit logistic regression** on the training set. Logistic regression adds up a weight for each answer and turns the total into a probability. It was chosen because its explanations are exact (D-008).
2. **Choose how BMI is used** by comparing two versions on the *validation* set: BMI as a straight line, or as a smooth curve (a *spline*) so that both very low and very high BMI can raise the estimate. The curve was slightly better for both models (D-031).
3. **Check calibration on validation.** *Calibration* asks: when the model says 20%, do about 20% of those people actually report the condition? The rule (D-032): if the average gap is over 0.5 percentage points, correct it with *isotonic calibration* fitted on the validation set.
   - Heart: gap 0.83 points → corrected.
   - COPD: gap 0.47 points → no correction needed.
4. **Choose a threshold on validation** (the point that maximises F1, explained below). Vytal never shows users a yes/no result; the threshold exists only so that sensitivity, specificity and precision can be reported.
5. **Evaluate once on the test set**, including a breakdown by sex, age group and survey year.
6. **Extra checks (reported only):** train on 2022–2023 and test on 2024 (does it work on a later year?), and compare with a more complex model (gradient boosting).
7. **Save** the model file, its SHA-256 fingerprint and all results in a metadata file; generate the evaluation report, model card and three charts.

---

## 3. Results explained

### The main numbers (test set: 169,577 heart / 169,083 COPD people never seen in training)

| Metric | Heart | COPD | Baseline | What it means |
|---|---|---|---|---|
| ROC-AUC | 0.810 | 0.836 | 0.5 | How well the model *ranks* people (1.0 = perfect) |
| ROC-AUC, survey-weighted | 0.831 | 0.836 | 0.5 | The same, with people weighted to represent US adults |
| PR-AUC | 0.299 | 0.363 | 0.091 / 0.080 | Precision across all thresholds; the baseline equals the outcome rate. About 3.3–4.5× better than chance |
| Brier score | 0.0723 | 0.0609 | 0.0828 / 0.0735 | Average squared error of the percentages (lower is better) |
| Calibration error | 0.22 points | 0.47 points | — | Average gap between estimate and reality |
| Sensitivity at threshold | 54.4% | 49.7% | — | Share of people who reported the condition that the model flagged |
| Specificity at threshold | 85.5% | 91.2% | — | Share of people who did not, correctly not flagged |
| Precision at threshold | 27.3% | 32.9% | — | Share of flagged people who had reported the condition |

**Why accuracy is not the headline.** Only about 9% of people reported heart disease, so a "model" that always says "no" is 91% accurate and completely useless. That is why ROC-AUC, PR-AUC, calibration, sensitivity and specificity are reported instead.

**Why precision looks low.** When a condition is rare, even a good model flags many people who don't have it. 27–33% precision is three to four times the base rate. It is another reason Vytal shows bands and estimates, not "you have it / you don't".

### What users will see: bands

A person's estimate is compared with all training-set respondents: **Low** (below the 50th percentile), **Moderate** (50th–75th), **Elevated** (75th–90th), **High** (top 10%). The test set shows the bands mean something real:

| Band | Heart: share of people / actually reported | COPD: share / actually reported |
|---|---|---|
| Low | 46.9% / 1.7% | 49.8% / 1.5% |
| Moderate | 25.8% / 7.9% | 25.1% / 5.7% |
| Elevated | 16.4% / 17.0% | 15.1% / 15.1% |
| High | 10.9% / 31.9% | 10.0% / 35.3% |

These are positions among survey respondents, **not clinical risk categories**.

### Fairness check (bias)

| Group | Heart ROC-AUC | COPD ROC-AUC |
|---|---|---|
| Women / men | 0.791 / 0.812 | 0.836 / 0.834 |
| Age 18–44 / 45–64 / 65+ | 0.720 / 0.755 / 0.707 | 0.770 / 0.840 / 0.794 |
| 2022 / 2023 / 2024 | 0.809 / 0.815 / 0.806 | 0.835 / 0.836 / 0.836 |

Calibration error stays under 1 point in every group (details in the reports). Within an age group, ROC-AUC is lower because age (the strongest signal) no longer separates people. Results are stable across the three years.

### Which answers matter most

| Heart | COPD |
|---|---|
| Age, sex, smoking, diabetes, BMI, exercise, stroke, kidney disease | Age, smoking, asthma, exercise, BMI, diabetes, sex, e-cigarettes |

(Ordered by average size of effect on the test set. These are associations within the model, not causes.)

### Robustness

| Check | Heart ROC-AUC | COPD ROC-AUC |
|---|---|---|
| Deployed model | 0.810 | 0.836 |
| Trained on 2022–2023, tested on 2024 | 0.806 | 0.836 |
| Gradient boosting (more complex, not deployed) | 0.813 | 0.839 |

The model works as well on a later year, and the more complex model gains only 0.003–0.004, so choosing the explainable model costs almost nothing.

---

## 4. Important files created or modified

| File | What it does |
|---|---|
| `ml/feature_definitions/vytal_feature_schema.json`, `feature_schema.py` | The shared definition of every input and its answers (version 1.1.0) |
| `ml/preprocessing/brfss_data_extraction.py` | Copies the needed columns from the raw files |
| `ml/preprocessing/recode_functions.py` | CDC codes → readable values; unusable → empty |
| `ml/preprocessing/dataset_split.py` | Seeded, stratified 70/15/15 split |
| `ml/preprocessing/build_model_dataset.py` | Builds each model's dataset with step-by-step exclusion counts |
| `ml/training/model_training_config.py` | Every setting and threshold in one place |
| `ml/training/train_binary_risk_model.py` | Fit, choose, calibrate, evaluate, save |
| `ml/training/heart_model_training.py`, `respiratory_model_training.py` | One-line entry points |
| `ml/evaluation/evaluation_metrics.py` | All metrics, including calibration |
| `ml/evaluation/evaluation_report_writer.py` | Generates reports, model cards and charts from the metadata |
| `ml/inference/risk_model.py` | Loads a model (fingerprint check first), computes estimates, percentiles, bands and explanations; shared with the backend |
| `models/heart/*`, `models/respiratory/*` | The saved models (5 KB and 2 KB) and their metadata |
| `docs/model_evaluation/*_model_evaluation_report.md`, `*_model_card.md`, `figures/*.png` | Generated results |
| `datasets/processed/*_summary.json` | Counts at every preprocessing step (no individual data) |
| `tests/unit/test_recode_functions.py`, `tests/data/test_processed_datasets.py`, `tests/unit/test_risk_model_artifacts.py` | Tests (section 6) |
| `ml/README.md`, `models/README.md`, `datasets/README.md`, `datasets/DATA_SOURCES.md` | Documentation |

## 5. Technical decisions and reasons

| ID | Decision | Reason |
|---|---|---|
| D-029 | Remove heavy drinking from the heart model | It produced a backwards, misleading association (see summary) |
| D-030 | One shared preprocessing script and trainer | The two models differ only in settings; duplicate code would drift |
| D-031 | BMI as a smooth curve | Better on validation for both models |
| D-032 | Calibrate only if needed (heart yes, COPD no) | Percentages are shown, so they must match reality |
| D-009 | No class weighting | Weighting would push percentages away from reality |
| D-010 | Bands from percentiles 50/75/90 | Defensible, documented, validated on test data; not clinical |
| D-011 | Explanations as exact log-odds contributions | For logistic regression, the contributions add up exactly to the score (tested) |

The feature schema was versioned 1.0.0 → 1.1.0 when heavy drinking was removed; the backend refuses to load a model trained with a different schema version.

## 6. Commands executed

```powershell
.venv\Scripts\python.exe -m ml.preprocessing.brfss_data_extraction
.venv\Scripts\python.exe -m ml.preprocessing.build_model_dataset              # both models
.venv\Scripts\python.exe -m ml.training.heart_model_training                    # first version (with heavy drinking)
.venv\Scripts\python.exe -m ml.training.respiratory_model_training
# after D-029:
.venv\Scripts\python.exe -m ml.preprocessing.build_model_dataset --model heart
.venv\Scripts\python.exe -m ml.training.heart_model_training
.venv\Scripts\python.exe -m ml.preprocessing.build_model_dataset --model respiratory   # same data, new schema version
.venv\Scripts\python.exe -m ml.training.respiratory_model_training
.venv\Scripts\python.exe -m pytest
```

## 7. Actual tests and outcomes

| Test group | What it checks | Result |
|---|---|---|
| Recoding (unit) | Codes map correctly; "don't know"/refused never become "no"; e-cigarette coding not reversed; BMI decimals and range; target coding | Pass |
| Every codebook answer accounted for | Each CDC answer code in all three years is either mapped or explicitly unusable | Pass |
| Split (unit) | Reproducible; 70/15/15; same positive rate in each part | Pass |
| Processed data | Expected columns only; no outcome columns leaked in; target is 0/1; no missing values; answers match the schema; BMI in range; summary counts add up | Pass (both datasets) |
| Model artifacts | Loads; fingerprint verified; encoder categories equal the schema; output shape (n, 2) and valid probabilities; unknown answers rejected; contributions rebuild the score exactly; bands ordered; metrics from held-out rows; tampered file refused | Pass (both models) |
| Whole suite at end of phase | | **Passed** (118 tests at the end of Phase 3, which includes these) |

## 8. Current errors and limitations

| Item | Effect |
|---|---|
| No blood pressure or cholesterol | Heart model misses two strong factors (stated to users) |
| Self-reported "ever told" outcomes, cross-sectional | Associations with reported conditions; answers like smoking may have changed after diagnosis |
| Metrics ignore survey strata and clusters | Uncertainty is somewhat understated |
| Lower ranking within age groups (0.71–0.84) | Most of the separation comes from age |
| Heart explanations describe the score before calibration | Stated in the response; calibration keeps the order of people the same |
| Inspection report sample counts predate D-029 | Heart counts there are about 37,000 lower; the dataset summary has the final numbers |

## 9. Dataset and model status

| Item | Status |
|---|---|
| Processed datasets | Built (not in Git; recreate with the commands above) |
| Heart model v1.0.0 | Trained, calibrated, evaluated, saved |
| COPD model v1.0.0 | Trained, evaluated (no calibration needed), saved |
| Reports and model cards | `docs/model_evaluation/` |

## 10. Git commit and push status

Committed together with Phase 3 (see `PROJECT_STATUS.md` for hashes and push status).

## 11. Exact next steps

Phase 3 (done in the same session): prediction API and suggestion rules. Then Phase 4: the user interface.

## 12. Decisions requiring your approval

None. D-029 (removing heavy drinking) was decided under the autonomy rules because keeping it would have shown users misleading explanations; it is recorded with evidence and can be revisited.
