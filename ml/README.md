# Vytal ML pipeline

Offline code: run by hand to prepare data and train models. The web app never retrains anything; it loads the saved artifacts in `models/`.

| Folder | Purpose | Key files |
|---|---|---|
| `feature_definitions/` | The single source of truth for model inputs | `vytal_feature_schema.json` (features, answer values, BRFSS codes, which model uses what), `feature_schema.py`, `brfss_candidate_variables.py` (source variable names per year, unusable codes) |
| `preprocessing/` | Get, check and prepare the data | `download_brfss_data.py`, `inspect_brfss_variables.py`, `brfss_data_extraction.py`, `recode_functions.py`, `build_model_dataset.py`, `dataset_split.py` |
| `training/` | Fit, calibrate, evaluate, save | `model_training_config.py` (all settings), `train_binary_risk_model.py`, `heart_model_training.py`, `respiratory_model_training.py` |
| `evaluation/` | Metrics and generated documents | `evaluation_metrics.py`, `evaluation_report_writer.py` |
| `inference/` | Load a model and compute estimates and explanations | `risk_model.py` (shared with the backend, so served numbers equal evaluated numbers) |

Commands: see `datasets/README.md`. Data flow:

```
BRFSS XPT (raw) -> extraction (interim parquet) -> recode + exclude + split (processed CSV)
  -> train on train split -> choose BMI form + calibration + threshold on validation
  -> evaluate once on test -> models/*.joblib + metadata + docs/model_evaluation/*
```
