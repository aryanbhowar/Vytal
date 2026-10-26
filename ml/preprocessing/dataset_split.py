"""Reproducible stratified train / validation / test assignment.

Rows are stratified by target and survey year together, so each split keeps the
same share of positive cases and the same mix of years. The seed makes the
assignment identical every time the pipeline runs.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

RANDOM_SEED = 42
SPLIT_FRACTIONS = {"train": 0.70, "validation": 0.15, "test": 0.15}


def assign_splits(target: pd.Series, survey_year: pd.Series, seed: int = RANDOM_SEED) -> pd.Series:
    strata = target.astype(str) + "_" + survey_year.astype(str)
    positions = np.arange(len(target))

    held_out_fraction = SPLIT_FRACTIONS["validation"] + SPLIT_FRACTIONS["test"]
    train_idx, held_out_idx = train_test_split(
        positions, test_size=held_out_fraction, stratify=strata, random_state=seed
    )
    test_share_of_held_out = SPLIT_FRACTIONS["test"] / held_out_fraction
    validation_idx, test_idx = train_test_split(
        held_out_idx,
        test_size=test_share_of_held_out,
        stratify=strata.iloc[held_out_idx],
        random_state=seed,
    )

    labels = np.empty(len(target), dtype=object)
    labels[train_idx] = "train"
    labels[validation_idx] = "validation"
    labels[test_idx] = "test"
    return pd.Series(labels, index=target.index, name="split")
