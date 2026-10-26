"""Load a saved Vytal model and turn feature rows into estimates and explanations.

Used by BOTH the training/evaluation code and the backend, so the numbers a user
sees are computed exactly as they were evaluated.

A saved artifact (models/<model>/<model>_logreg_v<version>.joblib) is a plain dict
of scikit-learn objects:
    {"pipeline": Pipeline(preprocess -> LogisticRegression),
     "calibrator": IsotonicRegression or None}
Its metadata JSON (same name + "_metadata.json") records the SHA-256 of the
.joblib file. joblib files are Python pickles, which can execute code when
loaded, so the hash is checked BEFORE loading (D-020).
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


class ModelIntegrityError(RuntimeError):
    """The artifact on disk does not match the hash recorded in its metadata."""


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass
class LoadedRiskModel:
    model_id: str
    metadata: dict
    pipeline: object
    calibrator: object | None

    @property
    def features(self) -> list[str]:
        return list(self.metadata["features"])

    def _frame(self, rows: pd.DataFrame) -> pd.DataFrame:
        return rows[self.features]

    def raw_probability(self, rows: pd.DataFrame) -> np.ndarray:
        """Logistic regression output before any calibration."""
        return self.pipeline.predict_proba(self._frame(rows))[:, 1]

    def probability(self, rows: pd.DataFrame) -> np.ndarray:
        raw = self.raw_probability(rows)
        if self.calibrator is None:
            return raw
        return np.clip(self.calibrator.predict(raw), 0.0, 1.0)

    def percentile(self, probability: np.ndarray) -> np.ndarray:
        """Approximate share (0-100) of training respondents with a lower estimate.

        Uses the stored training quantiles. Tied values (common after isotonic
        calibration) get the middle of their range, so ties are not pushed up or down.
        """
        quantiles = np.asarray(self.metadata["training_score_quantiles"])
        values = np.atleast_1d(probability)
        left = np.searchsorted(quantiles, values, side="left")
        right = np.searchsorted(quantiles, values, side="right")
        return np.clip((left + right) / 2 / (quantiles.size - 1) * 100, 0.0, 100.0)

    def band(self, probability: float) -> str:
        cutoffs = self.metadata["bands"]["probability_cutoffs"]
        band = "low"
        for name in ("moderate", "elevated", "high"):
            if probability >= cutoffs[name]:
                band = name
        return band

    def contributions(self, rows: pd.DataFrame) -> pd.DataFrame:
        """Per-feature contribution to the log-odds score, relative to the average respondent.

        contribution(feature) = sum over its encoded columns of coef * (x - training mean).
        For one row: intercept + sum(coef * training mean) + sum(contributions) equals the
        model's log-odds exactly (before calibration).
        """
        preprocess = self.pipeline.named_steps["preprocess"]
        classifier = self.pipeline.named_steps["classifier"]
        encoded = preprocess.transform(self._frame(rows))
        means = np.asarray(self.metadata["explanation"]["encoded_training_means"])
        per_column = (encoded - means) * classifier.coef_[0]
        groups = self.metadata["explanation"]["encoded_column_feature"]
        result = pd.DataFrame(index=rows.index)
        for feature in self.features:
            columns = [i for i, owner in enumerate(groups) if owner == feature]
            result[feature] = per_column[:, columns].sum(axis=1)
        return result

    def average_respondent_log_odds(self) -> float:
        return float(self.metadata["explanation"]["average_respondent_log_odds"])


def metadata_path_for(artifact_path: Path) -> Path:
    return artifact_path.with_name(artifact_path.stem + "_metadata.json")


def load_risk_model(artifact_path: Path) -> LoadedRiskModel:
    """Verify the artifact hash, then load it. Raises FileNotFoundError or ModelIntegrityError."""
    metadata = json.loads(metadata_path_for(artifact_path).read_text(encoding="utf-8"))
    actual = sha256_of_file(artifact_path)
    if actual != metadata["artifact_sha256"]:
        raise ModelIntegrityError(f"{artifact_path.name}: hash does not match its metadata")
    bundle = joblib.load(artifact_path)
    return LoadedRiskModel(metadata["model_id"], metadata, bundle["pipeline"], bundle["calibrator"])
