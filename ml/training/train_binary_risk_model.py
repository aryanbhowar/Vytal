"""Train, select, calibrate, evaluate and save one Vytal risk model.

Data use, strictly separated:
  train      -> fit the model (and the comparison model)
  validation -> choose the BMI form, check calibration, fit calibration if needed,
                choose the threshold for reported metrics
  test       -> evaluated ONCE at the end; nothing is chosen from it

Usage (via the per-model entry points):
    .venv\\Scripts\\python.exe -m ml.training.heart_model_training
    .venv\\Scripts\\python.exe -m ml.training.respiratory_model_training
"""

import json
import platform
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler

from ml.evaluation import evaluation_metrics as em
from ml.evaluation.evaluation_report_writer import write_evaluation_documents
from ml.feature_definitions.feature_schema import (
    categorical_values,
    is_categorical,
    load_schema,
    model_definition,
    model_features,
)
from ml.inference.risk_model import LoadedRiskModel, metadata_path_for, sha256_of_file
from ml.preprocessing.build_model_dataset import TARGET_COLUMN, dataset_path, summary_path
from ml.training import model_training_config as cfg


def load_dataset(model_id: str) -> pd.DataFrame:
    features = model_features(model_id)
    dtypes = {f: "string" for f in features if is_categorical(f)}
    data = pd.read_csv(dataset_path(model_id), dtype=dtypes)
    for feature in dtypes:
        data[feature] = data[feature].astype(object)
    return data


def build_preprocessor(model_id: str, bmi_form: str) -> ColumnTransformer:
    features = model_features(model_id)
    categorical = [f for f in features if is_categorical(f)]
    bmi_transformer = (
        SplineTransformer(**cfg.BMI_SPLINE_PARAMS) if bmi_form == "spline" else StandardScaler()
    )
    return ColumnTransformer(
        [
            # Categories are fixed from the schema, so the encoder (and the API) can
            # never silently meet an unexpected value.
            ("categorical", OneHotEncoder(categories=[categorical_values(f) for f in categorical],
                                          handle_unknown="error", sparse_output=False), categorical),
            ("bmi", bmi_transformer, ["bmi"]),
        ],
        verbose_feature_names_out=False,
    )


def build_logistic_pipeline(model_id: str, bmi_form: str) -> Pipeline:
    return Pipeline([
        ("preprocess", build_preprocessor(model_id, bmi_form)),
        ("classifier", LogisticRegression(**cfg.LOGISTIC_REGRESSION_PARAMS)),
    ])


def encoded_column_owners(preprocess: ColumnTransformer, model_id: str) -> list[str]:
    """For each encoded column, the original feature it came from."""
    owners = []
    for name, transformer, columns in preprocess.transformers_:
        if name == "categorical":
            for feature, categories in zip(columns, transformer.categories_):
                owners.extend([feature] * len(categories))
        elif name == "bmi":
            owners.extend(["bmi"] * transformer.transform(pd.DataFrame({"bmi": [25.0]})).shape[1])
    return owners


def calibration_is_acceptable(metrics: dict) -> bool:
    low, high = cfg.CALIBRATION_SLOPE_RANGE
    return metrics["expected_calibration_error"] <= cfg.MAX_ACCEPTABLE_ECE and low <= metrics["calibration_slope"] <= high


def subgroup_metrics(frame: pd.DataFrame, probability: np.ndarray, threshold: float) -> dict:
    y = frame[TARGET_COLUMN].to_numpy()
    groups = {
        "sex": frame["sex"],
        "age": frame["age_group"].map({a: g for g, ages in cfg.AGE_SUBGROUPS.items() for a in ages}),
        "survey_year": frame["survey_year"].astype(str),
    }
    result = {}
    for dimension, labels in groups.items():
        result[dimension] = {}
        for label in sorted(labels.unique()):
            mask = (labels == label).to_numpy()
            pm = em.probability_metrics(y[mask], probability[mask])
            tm = em.threshold_metrics(y[mask], probability[mask], threshold)
            result[dimension][label] = {
                "rows": pm["rows"], "prevalence": pm["prevalence"], "mean_predicted": pm["mean_predicted"],
                "roc_auc": pm["roc_auc"], "pr_auc": pm["pr_auc"],
                "expected_calibration_error": pm["expected_calibration_error"],
                "recall_sensitivity": tm["recall_sensitivity"], "specificity": tm["specificity"],
                "precision": tm["precision"],
            }
    return result


def band_validation(model: LoadedRiskModel, frame: pd.DataFrame, probability: np.ndarray) -> dict:
    """How often test-set respondents in each band actually reported the condition."""
    bands = np.array([model.band(p) for p in probability])
    y = frame[TARGET_COLUMN].to_numpy()
    return {
        band: {
            "rows": int((bands == band).sum()),
            "share_of_respondents": float((bands == band).mean()),
            "observed_prevalence": float(y[bands == band].mean()) if (bands == band).any() else None,
            "mean_estimate": float(probability[bands == band].mean()) if (bands == band).any() else None,
        }
        for band in cfg.BAND_ORDER
    }


def global_contribution_importance(model: LoadedRiskModel, frame: pd.DataFrame) -> dict:
    """Mean absolute per-person contribution on the test set (same method as user explanations)."""
    contributions = model.contributions(frame)
    return {f: float(v) for f, v in contributions.abs().mean().sort_values(ascending=False).items()}


def temporal_check(model_id: str, data: pd.DataFrame, bmi_form: str) -> dict:
    """Report-only: train on 2022-2023 training rows, test on 2024 test rows."""
    features = model_features(model_id)
    train = data[(data["split"] == "train") & (data["survey_year"] < 2024)]
    test = data[(data["split"] == "test") & (data["survey_year"] == 2024)]
    pipeline = build_logistic_pipeline(model_id, bmi_form).fit(train[features], train[TARGET_COLUMN])
    probability = pipeline.predict_proba(test[features])[:, 1]
    metrics = em.probability_metrics(test[TARGET_COLUMN].to_numpy(), probability)
    metrics.pop("calibration_table")
    return {"train_rows": len(train), "test_rows": len(test), **metrics}


def gradient_boosting_comparison(model_id: str, splits: dict) -> dict:
    features = model_features(model_id)
    pipeline = Pipeline([
        ("preprocess", build_preprocessor(model_id, "linear")),
        ("classifier", HistGradientBoostingClassifier(**cfg.GRADIENT_BOOSTING_PARAMS)),
    ])
    pipeline.fit(splits["train"][features], splits["train"][TARGET_COLUMN])
    result = {}
    for split in ("validation", "test"):
        probability = pipeline.predict_proba(splits[split][features])[:, 1]
        metrics = em.probability_metrics(splits[split][TARGET_COLUMN].to_numpy(), probability)
        metrics.pop("calibration_table")
        result[split] = metrics
    return result


def artifact_path(model_id: str) -> Path:
    major = cfg.MODEL_VERSION.split(".")[0]
    return cfg.MODELS_DIR / model_id / f"{model_id}_logreg_v{major}.joblib"


def train_and_save(model_id: str) -> dict:
    features = model_features(model_id)
    data = load_dataset(model_id)
    splits = {name: data[data["split"] == name].reset_index(drop=True) for name in ("train", "validation", "test")}
    y = {name: frame[TARGET_COLUMN].to_numpy() for name, frame in splits.items()}
    print(f"[{model_id}] rows: " + ", ".join(f"{k} {len(v):,}" for k, v in splits.items()), flush=True)

    # 1. Fit both BMI forms on train; choose on validation log loss.
    candidates = {}
    for bmi_form in ("linear", "spline"):
        pipeline = build_logistic_pipeline(model_id, bmi_form).fit(splits["train"][features], y["train"])
        validation_probability = pipeline.predict_proba(splits["validation"][features])[:, 1]
        candidates[bmi_form] = {"pipeline": pipeline, "validation_log_loss": float(log_loss(y["validation"], validation_probability))}
        print(f"[{model_id}] BMI {bmi_form}: validation log loss {candidates[bmi_form]['validation_log_loss']:.5f}", flush=True)
    bmi_form = min(candidates, key=lambda form: candidates[form]["validation_log_loss"])
    pipeline = candidates[bmi_form]["pipeline"]

    # 2. Calibration check on validation; isotonic recalibration only if needed.
    raw_validation = pipeline.predict_proba(splits["validation"][features])[:, 1]
    validation_raw_metrics = em.probability_metrics(y["validation"], raw_validation)
    calibrator = None
    if not calibration_is_acceptable(validation_raw_metrics):
        calibrator = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip").fit(raw_validation, y["validation"])
    calibration_method = "isotonic (fitted on validation)" if calibrator else "none needed"
    print(f"[{model_id}] calibration on validation: ECE {validation_raw_metrics['expected_calibration_error']:.4f}, "
          f"slope {validation_raw_metrics['calibration_slope']:.3f} -> {calibration_method}", flush=True)

    # 3. Save the artifact, then reload through the same code the backend uses.
    path = artifact_path(model_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "calibrator": calibrator}, path, compress=3)
    preprocess = pipeline.named_steps["preprocess"]
    classifier = pipeline.named_steps["classifier"]
    encoded_train = preprocess.transform(splits["train"][features])
    encoded_means = encoded_train.mean(axis=0)
    data_summary = json.loads(summary_path(model_id).read_text(encoding="utf-8"))

    metadata = {
        "model_id": model_id,
        "model_version": cfg.MODEL_VERSION,
        "created": date.today().isoformat(),
        "artifact_file": path.name,
        "artifact_sha256": sha256_of_file(path),
        "algorithm": "Logistic regression (scikit-learn), unweighted",
        "bmi_form": bmi_form,
        "bmi_form_validation_log_loss": {k: v["validation_log_loss"] for k, v in candidates.items()},
        "calibration_method": calibration_method,
        "outcome_description": model_definition(model_id)["outcome_description"],
        "training_data": {
            "source": "CDC BRFSS 2022, 2023, 2024 (pooled, complete cases)",
            "survey_years": data_summary["survey_years"],
            "dataset_file": dataset_path(model_id).name,
            "rows": {k: len(v) for k, v in splits.items()},
            "training_prevalence": float(y["train"].mean()),
            "weighted_us_adult_prevalence": data_summary["weighted_prevalence_percent_valid_target_pooled"] / 100,
        },
        "feature_schema_version": load_schema()["schema_version"],
        "features": features,
        "feature_categories": {f: categorical_values(f) for f in features if is_categorical(f)},
        "dependencies": {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                         "numpy": np.__version__, "pandas": pd.__version__, "joblib": joblib.__version__},
        "explanation": {
            "method": "Per-feature log-odds contribution relative to the training-set average (exact for logistic regression)",
            "encoded_column_names": [str(n) for n in preprocess.get_feature_names_out()],
            "encoded_column_feature": encoded_column_owners(preprocess, model_id),
            "encoded_training_means": encoded_means.tolist(),
            "coefficients": classifier.coef_[0].tolist(),
            "intercept": float(classifier.intercept_[0]),
            "average_respondent_log_odds": float(classifier.intercept_[0] + encoded_means @ classifier.coef_[0]),
            "explains": "the logistic regression score before calibration" if calibrator else "the displayed estimate",
        },
    }
    # Score distribution and bands need the final probability on training data.
    interim = LoadedRiskModel(model_id, {**metadata, "training_score_quantiles": [0, 1]}, pipeline, calibrator)
    train_probability = interim.probability(splits["train"])
    quantiles = np.quantile(train_probability, np.linspace(0, 1, cfg.SCORE_QUANTILE_POINTS))
    metadata["training_score_quantiles"] = quantiles.tolist()
    metadata["bands"] = {
        "basis": "percentile of the respondent's estimate among training-set respondents",
        "cutoff_percentiles": cfg.BAND_CUTOFF_PERCENTILES,
        "probability_cutoffs": {name: float(np.quantile(train_probability, pct / 100))
                                for name, pct in cfg.BAND_CUTOFF_PERCENTILES.items()},
        "not_clinical": True,
    }
    model = LoadedRiskModel(model_id, metadata, pipeline, calibrator)

    # 4. Threshold for reported metrics, chosen on validation.
    validation_probability = model.probability(splits["validation"])
    threshold = em.best_f1_threshold(y["validation"], validation_probability)

    # 5. Single evaluation on the test set.
    test_probability = model.probability(splits["test"])
    weights = splits["test"]["pooled_weight"].to_numpy()
    metadata["evaluation"] = {
        "threshold_rule": "maximum F1 on the validation set",
        "validation": {**em.probability_metrics(y["validation"], validation_probability),
                       **em.threshold_metrics(y["validation"], validation_probability, threshold)},
        "validation_before_calibration": validation_raw_metrics,
        "test": {**em.probability_metrics(y["test"], test_probability, weights),
                 **em.threshold_metrics(y["test"], test_probability, threshold)},
        "test_prevalence_baseline": em.prevalence_baseline(y["test"], float(y["train"].mean())),
        "test_subgroups": subgroup_metrics(splits["test"], test_probability, threshold),
        "test_band_validation": band_validation(model, splits["test"], test_probability),
        "test_global_importance": global_contribution_importance(model, splits["test"]),
        "temporal_check_train_2022_2023_test_2024": temporal_check(model_id, data, bmi_form),
        "comparison_hist_gradient_boosting": gradient_boosting_comparison(model_id, splits),
    }
    metadata_path_for(path).write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_evaluation_documents(metadata, y["test"], test_probability)
    test = metadata["evaluation"]["test"]
    print(f"[{model_id}] TEST: ROC-AUC {test['roc_auc']:.4f}, PR-AUC {test['pr_auc']:.4f}, Brier {test['brier_score']:.5f}, "
          f"ECE {test['expected_calibration_error']:.4f}, recall {test['recall_sensitivity']:.3f}, "
          f"precision {test['precision']:.3f}, specificity {test['specificity']:.3f}", flush=True)
    print(f"[{model_id}] saved {path.relative_to(cfg.MODELS_DIR.parent)} ({path.stat().st_size / 1024:.0f} KB)", flush=True)
    return metadata
