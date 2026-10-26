"""Extract only the BRFSS columns Vytal needs into small interim Parquet files.

Reading a 1.1 GB SAS file takes about a minute; the extracted file is a few MB
and loads in under a second, so later steps never touch the raw files.

Output: datasets/interim/brfss_<year>_selected.parquet (raw codes, unchanged).

Usage:
    .venv\\Scripts\\python.exe -m ml.preprocessing.brfss_data_extraction
"""

import sys
from pathlib import Path

import pandas as pd
import pyreadstat

from ml.feature_definitions.brfss_candidate_variables import SURVEY_YEARS, candidate_by_name
from ml.feature_definitions.feature_schema import load_schema
from ml.preprocessing.brfss_sources import INTERIM_DATA_DIR, RAW_DATA_DIR

XPT_ENCODING = "latin1"
SURVEY_WEIGHT = "survey_weight"


def needed_canonical_names() -> list[str]:
    schema = load_schema()
    names = {SURVEY_WEIGHT}
    for model in schema["models"].values():
        names.add(model["target"])
        names.update(model["features"])
    return sorted(names)


def interim_path(year: int) -> Path:
    return INTERIM_DATA_DIR / f"brfss_{year}_selected.parquet"


def extract_year(year: int) -> pd.DataFrame:
    """Read the needed columns for one year and rename them to canonical names."""
    source_to_canonical = {candidate_by_name(name).source(year): name for name in needed_canonical_names()}
    frame, _ = pyreadstat.read_xport(
        str(RAW_DATA_DIR / f"LLCP{year}.XPT"), usecols=list(source_to_canonical), encoding=XPT_ENCODING
    )
    frame = frame.rename(columns=source_to_canonical)
    frame.insert(0, "survey_year", year)
    return frame


def load_interim(year: int) -> pd.DataFrame:
    return pd.read_parquet(interim_path(year))


def main() -> int:
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for year in SURVEY_YEARS:
        frame = extract_year(year)
        frame.to_parquet(interim_path(year), index=False)
        print(f"{year}: {len(frame):,} rows x {frame.shape[1]} columns -> {interim_path(year).name} "
              f"({interim_path(year).stat().st_size / 1e6:.1f} MB)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
