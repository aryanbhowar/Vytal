"""Convert BRFSS answer codes into Vytal's canonical values.

Every function returns NaN for codes that are not a usable answer (don't know,
refused, not asked, missing). Callers then exclude those rows; nothing here
ever turns an unusable answer into "no".
"""

import numpy as np
import pandas as pd

from ml.feature_definitions.feature_schema import bmi_range, feature_definition, model_definition


def _as_code_text(series: pd.Series) -> pd.Series:
    """Numeric BRFSS codes (stored as floats in the SAS file) -> '1', '2', ... ; NaN stays NaN."""
    return series.map(lambda value: np.nan if pd.isna(value) else str(int(value)))


def recode_categorical(series: pd.Series, feature: str) -> pd.Series:
    """Map codes listed in the schema to canonical values; every other code becomes NaN."""
    mapping = feature_definition(feature)["brfss_codes"]
    return _as_code_text(series).map(mapping)


def recode_bmi(series: pd.Series) -> pd.Series:
    """BRFSS `_BMI5` has two implied decimals (2534 means 25.34).

    Values outside the plausible range in the schema become NaN: they are almost
    always height or weight entry errors.
    """
    divisor = feature_definition("bmi")["brfss_scale_divisor"]
    bmi = series / divisor
    low, high = bmi_range()
    return bmi.where((bmi >= low) & (bmi <= high))


def recode_feature(series: pd.Series, feature: str) -> pd.Series:
    if feature_definition(feature)["type"] == "numeric":
        return recode_bmi(series)
    return recode_categorical(series, feature)


def recode_target(series: pd.Series, model_id: str) -> pd.Series:
    """1 = reported the condition, 0 = did not, NaN = unusable. Returned as nullable Int8."""
    mapping = model_definition(model_id)["target_brfss_codes"]
    return _as_code_text(series).map(mapping).astype("Int8")
