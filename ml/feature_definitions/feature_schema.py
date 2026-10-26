"""Load and query vytal_feature_schema.json (shared by training and the backend)."""

import json
from functools import lru_cache
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("vytal_feature_schema.json")


@lru_cache(maxsize=1)
def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def model_definition(model_id: str) -> dict:
    return load_schema()["models"][model_id]


def model_features(model_id: str) -> list[str]:
    return list(model_definition(model_id)["features"])


def feature_definition(feature: str) -> dict:
    return load_schema()["features"][feature]


def is_categorical(feature: str) -> bool:
    return feature_definition(feature)["type"] == "categorical"


def categorical_values(feature: str) -> list[str]:
    """Canonical values in codebook order (used as the encoder's fixed categories)."""
    return list(feature_definition(feature)["brfss_codes"].values())


def bmi_range() -> tuple[float, float]:
    limits = load_schema()["bmi_range"]
    return float(limits["min"]), float(limits["max"])
