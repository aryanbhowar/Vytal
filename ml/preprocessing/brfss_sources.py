"""Official facts about each BRFSS survey year used by Vytal.

The expected record and variable counts come from CDC's "BRFSS Survey Data and
Documentation" page for each year (read via Internet Archive snapshots because
cdc.gov blocks scripted requests from this machine). They are used to check that
a downloaded file is the complete, official dataset.
"""

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "datasets" / "raw"
INTERIM_DATA_DIR = PROJECT_ROOT / "datasets" / "interim"
PROCESSED_DATA_DIR = PROJECT_ROOT / "datasets" / "processed"


@dataclass(frozen=True)
class BrfssYear:
    year: int
    expected_records: int
    expected_variables: int  # as printed on CDC's page; known to be unreliable (see inspection)
    release_note: str
    archive_timestamp: str  # Internet Archive snapshot of the official zip URL
    # SHA-256 of the zip verified on 2026-10-26/27: record count equals CDC's figure and
    # every answer count for the inspected variables equals the official codebook.
    verified_zip_sha256: str
    documentation_files: tuple[str, ...]  # paths under https://www.cdc.gov/brfss/annual_data/

    @property
    def zip_name(self) -> str:
        return f"LLCP{self.year}XPT.zip"

    @property
    def official_zip_url(self) -> str:
        return f"https://www.cdc.gov/brfss/annual_data/{self.year}/files/{self.zip_name}"

    @property
    def official_page_url(self) -> str:
        return f"https://www.cdc.gov/brfss/annual_data/annual_{self.year}.html"

    @property
    def archive_zip_url(self) -> str:
        # "id_" asks the Internet Archive for the original bytes, unmodified.
        return f"https://web.archive.org/web/{self.archive_timestamp}id_/{self.official_zip_url}"

    @property
    def zip_path(self) -> Path:
        return RAW_DATA_DIR / self.zip_name


DOCUMENTATION_DIR = RAW_DATA_DIR / "documentation"

BRFSS_YEARS: dict[int, BrfssYear] = {
    2022: BrfssYear(
        2022, 445_132, 326, "November 2023 release", "20260726053926",
        "b6319c949b7289f8020fc903c3c2d38fe7e0b28ad703dcd81547f5cd0c0dcfeb",
        ("2022/zip/codebook22_llcp-v2-508.zip", "2022/files/FORMAT22.sas"),
    ),
    2023: BrfssYear(
        2023, 433_323, 345, "February 2025 release", "20260726054012",
        "d1ab80e4806a1d07bd3e40ec78c971ad9ff920f3ea5f6049780aeaa41ff31f43",
        ("2023/zip/codebook23_llcp-v2-508.zip", "2023/files/FORMAT23.zip"),
    ),
    2024: BrfssYear(
        2024, 457_670, 345, "August 2025 release", "20260726053305",
        "d33de91a584e866f657d29b1d5b51b5672467286ed22d021e36ee3c7b4d712a4",
        ("2024/zip/codebook24_llcp-v2-508.zip", "2024/files/FORMAT24.zip"),
    ),
}


def archive_url_for(official_path: str) -> str:
    """Closest 2026 Internet Archive snapshot of an official CDC BRFSS file."""
    return f"https://web.archive.org/web/2026id_/https://www.cdc.gov/brfss/annual_data/{official_path}"
