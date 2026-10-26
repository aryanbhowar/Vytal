"""Build the model-ready dataset for one outcome (heart or respiratory).

Steps, with the number of rows removed at each one recorded in the summary:
  1. Load the extracted 2022, 2023 and 2024 files.
  2. Recode the target; drop rows with an unusable target answer.
  3. Recode each feature in turn; drop rows with an unusable answer.
  4. Add a pooled survey weight (each year's weight / number of years, CDC guidance).
  5. Assign a stratified 70/15/15 train/validation/test split (seeded).

Outputs:
  datasets/processed/<model>_<outcome>_brfss2022_2024.csv   (not committed)
  datasets/processed/<model>_<outcome>_brfss2022_2024_summary.json (counts only, committed)

Usage:
    .venv\\Scripts\\python.exe -m ml.preprocessing.build_model_dataset --model heart
    .venv\\Scripts\\python.exe -m ml.preprocessing.build_model_dataset --model respiratory
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from ml.feature_definitions.brfss_candidate_variables import SURVEY_YEARS
from ml.feature_definitions.feature_schema import model_definition, model_features
from ml.preprocessing.brfss_data_extraction import SURVEY_WEIGHT, load_interim
from ml.preprocessing.brfss_sources import PROCESSED_DATA_DIR
from ml.preprocessing.dataset_split import assign_splits
from ml.preprocessing.recode_functions import recode_feature, recode_target

DATASET_NAMES = {"heart": "heart_mi_chd_brfss2022_2024", "respiratory": "respiratory_copd_brfss2022_2024"}
TARGET_COLUMN = "target"


def dataset_path(model_id: str) -> Path:
    return PROCESSED_DATA_DIR / f"{DATASET_NAMES[model_id]}.csv"


def summary_path(model_id: str) -> Path:
    return PROCESSED_DATA_DIR / f"{DATASET_NAMES[model_id]}_summary.json"


def weighted_prevalence_percent(target: pd.Series, weight: pd.Series) -> float:
    return round(float((weight * target).sum() / weight.sum()) * 100, 3)


def clean_year(raw: pd.DataFrame, model_id: str) -> tuple[pd.DataFrame, list[dict], float]:
    """Recode one year's rows; return the clean rows, the drop log and the all-valid weighted prevalence."""
    target_name = model_definition(model_id)["target"]
    features = model_features(model_id)
    steps = [{"step": "records in file", "remaining": len(raw), "removed": 0}]

    frame = pd.DataFrame({"survey_year": raw["survey_year"], SURVEY_WEIGHT: raw[SURVEY_WEIGHT]})
    frame[TARGET_COLUMN] = recode_target(raw[target_name], model_id)
    before = len(frame)
    frame = frame[frame[TARGET_COLUMN].notna()].copy()
    steps.append({"step": "unusable target answer", "remaining": len(frame), "removed": before - len(frame)})
    # The population estimate uses every respondent with a valid target (CDC weights
    # are designed for that), before feature-based exclusions.
    valid_target_prevalence = weighted_prevalence_percent(frame[TARGET_COLUMN].astype(float), frame[SURVEY_WEIGHT])

    for feature in features:
        frame[feature] = recode_feature(raw.loc[frame.index, feature], feature)
        before = len(frame)
        frame = frame[frame[feature].notna()]
        steps.append({"step": f"unusable {feature}", "remaining": len(frame), "removed": before - len(frame)})
    return frame, steps, valid_target_prevalence


def build(model_id: str) -> dict:
    features = model_features(model_id)
    yearly_frames, yearly_summaries = [], {}
    for year in SURVEY_YEARS:
        frame, steps, prevalence_all_valid = clean_year(load_interim(year), model_id)
        yearly_frames.append(frame)
        yearly_summaries[year] = {
            "drop_steps": steps,
            "final_rows": len(frame),
            "positives": int(frame[TARGET_COLUMN].sum()),
            "unweighted_prevalence_percent": round(float(frame[TARGET_COLUMN].mean()) * 100, 3),
            "weighted_prevalence_percent_valid_target": prevalence_all_valid,
        }

    data = pd.concat(yearly_frames, ignore_index=True)
    data["pooled_weight"] = data[SURVEY_WEIGHT] / len(SURVEY_YEARS)
    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype("int8")
    data["split"] = assign_splits(data[TARGET_COLUMN], data["survey_year"])
    data = data[["survey_year", "split", TARGET_COLUMN, *features, "pooled_weight"]]

    # Pooled population estimate over all valid-target respondents, years weighted equally.
    pooled_valid_prevalence = round(
        sum(yearly_summaries[y]["weighted_prevalence_percent_valid_target"] for y in SURVEY_YEARS)
        / len(SURVEY_YEARS), 3,
    )
    split_counts = {
        split: {
            "rows": int((data["split"] == split).sum()),
            "positives": int(data.loc[data["split"] == split, TARGET_COLUMN].sum()),
            "unweighted_prevalence_percent": round(
                float(data.loc[data["split"] == split, TARGET_COLUMN].mean()) * 100, 3
            ),
        }
        for split in ("train", "validation", "test")
    }
    category_counts = {
        feature: {str(k): int(v) for k, v in data[feature].value_counts().sort_index().items()}
        for feature in features if feature != "bmi"
    }
    summary = {
        "generated": date.today().isoformat(),
        "model_id": model_id,
        "outcome_description": model_definition(model_id)["outcome_description"],
        "survey_years": list(SURVEY_YEARS),
        "features": features,
        "total_rows": len(data),
        "total_positives": int(data[TARGET_COLUMN].sum()),
        "unweighted_prevalence_percent": round(float(data[TARGET_COLUMN].mean()) * 100, 3),
        "weighted_prevalence_percent_complete_cases": weighted_prevalence_percent(
            data[TARGET_COLUMN].astype(float), data["pooled_weight"]
        ),
        "weighted_prevalence_percent_valid_target_pooled": pooled_valid_prevalence,
        "bmi": {k: round(float(v), 2) for k, v in data["bmi"].describe().items()},
        "category_counts": category_counts,
        "splits": split_counts,
        "by_year": yearly_summaries,
    }

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    data.to_csv(dataset_path(model_id), index=False)
    summary_path(model_id).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def print_summary(summary: dict) -> None:
    print(f"\n{summary['model_id']}: {summary['outcome_description']}")
    for year, info in summary["by_year"].items():
        print(f"  {year}:")
        for step in info["drop_steps"]:
            print(f"    {step['step']:42} removed {step['removed']:>8,}  remaining {step['remaining']:>8,}")
        print(f"    prevalence {info['unweighted_prevalence_percent']}% unweighted, "
              f"{info['weighted_prevalence_percent_valid_target']}% weighted (all valid targets)")
    print(f"  pooled: {summary['total_rows']:,} rows, {summary['total_positives']:,} positive "
          f"({summary['unweighted_prevalence_percent']}% unweighted; "
          f"{summary['weighted_prevalence_percent_valid_target_pooled']}% weighted US adult estimate)")
    for split, info in summary["splits"].items():
        print(f"  {split:10} {info['rows']:>9,} rows, {info['positives']:>7,} positive ({info['unweighted_prevalence_percent']}%)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a model-ready Vytal dataset")
    parser.add_argument("--model", choices=sorted(DATASET_NAMES), nargs="+", default=sorted(DATASET_NAMES))
    for model_id in parser.parse_args().model:
        print_summary(build(model_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
