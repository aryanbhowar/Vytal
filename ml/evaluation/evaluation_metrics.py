"""Evaluation metrics for binary risk models.

Accuracy is deliberately not the headline: with ~8-9% positives, a model that
always says "no" is ~91% accurate and useless. Ranking (ROC-AUC, PR-AUC),
probability quality (Brier, log loss, calibration) and threshold metrics
(precision, recall, specificity, F1) are reported instead.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    log_loss,
    precision_recall_curve,
    roc_auc_score,
)

from ml.training.model_training_config import CALIBRATION_BINS


def _logit(probability: np.ndarray) -> np.ndarray:
    clipped = np.clip(probability, 1e-6, 1 - 1e-6)
    return np.log(clipped / (1 - clipped))


def calibration_table(y_true: np.ndarray, probability: np.ndarray, bins: int = CALIBRATION_BINS) -> list[dict]:
    """Equal-size bins by predicted probability: mean prediction vs observed rate."""
    order = np.argsort(probability, kind="stable")
    rows = []
    for chunk in np.array_split(order, bins):
        rows.append({
            "count": int(chunk.size),
            "mean_predicted": float(probability[chunk].mean()),
            "observed_rate": float(y_true[chunk].mean()),
        })
    return rows


def expected_calibration_error(table: list[dict]) -> float:
    total = sum(row["count"] for row in table)
    return float(sum(row["count"] * abs(row["mean_predicted"] - row["observed_rate"]) for row in table) / total)


def calibration_slope_intercept(y_true: np.ndarray, probability: np.ndarray) -> tuple[float, float]:
    """Logistic recalibration: slope 1 and intercept 0 mean perfectly calibrated."""
    recalibration = LogisticRegression(C=1e6, max_iter=1000)
    recalibration.fit(_logit(probability).reshape(-1, 1), y_true)
    return float(recalibration.coef_[0, 0]), float(recalibration.intercept_[0])


def probability_metrics(y_true: np.ndarray, probability: np.ndarray, weight: np.ndarray | None = None) -> dict:
    table = calibration_table(y_true, probability)
    slope, intercept = calibration_slope_intercept(y_true, probability)
    metrics = {
        "rows": int(y_true.size),
        "positives": int(y_true.sum()),
        "prevalence": float(y_true.mean()),
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "pr_auc": float(average_precision_score(y_true, probability)),
        "brier_score": float(brier_score_loss(y_true, probability)),
        "log_loss": float(log_loss(y_true, probability)),
        "expected_calibration_error": expected_calibration_error(table),
        "calibration_slope": slope,
        "calibration_intercept": intercept,
        "mean_predicted": float(probability.mean()),
        "calibration_table": table,
    }
    if weight is not None:
        metrics["roc_auc_survey_weighted"] = float(roc_auc_score(y_true, probability, sample_weight=weight))
    return metrics


def prevalence_baseline(y_true: np.ndarray, training_prevalence: float) -> dict:
    """What you get by predicting the training prevalence for everyone."""
    constant = np.full(y_true.shape, training_prevalence)
    return {
        "roc_auc": 0.5,
        "pr_auc": float(y_true.mean()),
        "brier_score": float(brier_score_loss(y_true, constant)),
        "log_loss": float(log_loss(y_true, constant)),
    }


def best_f1_threshold(y_true: np.ndarray, probability: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, probability)
    f1 = 2 * precision * recall / np.clip(precision + recall, 1e-12, None)
    return float(thresholds[int(np.argmax(f1[:-1]))])


def threshold_metrics(y_true: np.ndarray, probability: np.ndarray, threshold: float) -> dict:
    predicted = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, predicted, labels=[0, 1]).ravel()
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": float(threshold),
        "confusion_matrix": {"true_negative": int(tn), "false_positive": int(fp),
                             "false_negative": int(fn), "true_positive": int(tp)},
        "precision": float(precision),
        "recall_sensitivity": float(recall),
        "specificity": float(specificity),
        "f1": float(f1),
        "accuracy": float((tp + tn) / y_true.size),
        "flagged_share": float(predicted.mean()),
    }
