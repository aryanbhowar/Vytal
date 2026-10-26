"""Download the BRFSS 2022-2024 SAS transport files into datasets/raw/.

For each year it tries, in order:
  1. A file you already placed in datasets/raw/ (e.g. downloaded in a browser).
  2. The official CDC URL.
  3. The Internet Archive snapshot of that same official URL (original bytes).

Downloads go to a ".part" file first and are only renamed once complete, so an
interrupted download never looks like a finished one. The zip is then tested.
Whether the contents are the complete official dataset is checked separately by
inspect_brfss_variables.py (record and variable counts against CDC's figures).

Usage (from the project root):
    .venv\\Scripts\\python.exe -m ml.preprocessing.download_brfss_data
    .venv\\Scripts\\python.exe -m ml.preprocessing.download_brfss_data --years 2023
"""

import argparse
import hashlib
import shutil
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from ml.preprocessing.brfss_sources import (
    BRFSS_YEARS,
    DOCUMENTATION_DIR,
    RAW_DATA_DIR,
    BrfssYear,
    archive_url_for,
)

BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
MINIMUM_PLAUSIBLE_ZIP_BYTES = 20_000_000  # official zips are about 64 MB
DOWNLOAD_TIMEOUT_SECONDS = 120
CHUNK_BYTES = 1024 * 1024
ATTEMPTS_PER_SOURCE = 4
RETRY_WAIT_SECONDS = 15


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK_BYTES), b""):
            digest.update(block)
    return digest.hexdigest()


def is_valid_zip(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < MINIMUM_PLAUSIBLE_ZIP_BYTES:
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None
    except zipfile.BadZipFile:
        return False


def download(url: str, destination: Path) -> None:
    partial = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": BROWSER_USER_AGENT})
    with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        with partial.open("wb") as output:
            shutil.copyfileobj(response, output, CHUNK_BYTES)
    partial.replace(destination)


def download_with_retries(url: str, destination: Path, label: str, year: int) -> None:
    """Retry transient failures (connection resets, timeouts). HTTP 403 is not retried."""
    for attempt in range(1, ATTEMPTS_PER_SOURCE + 1):
        try:
            download(url, destination)
            return
        except urllib.error.HTTPError:
            raise
        except Exception as error:
            if attempt == ATTEMPTS_PER_SOURCE:
                raise
            wait = RETRY_WAIT_SECONDS * attempt
            print(f"  {year}: {label} attempt {attempt} failed ({error}); retrying in {wait}s", flush=True)
            time.sleep(wait)


def acquire_year(source: BrfssYear) -> str:
    """Return a short description of where the valid zip came from."""
    if is_valid_zip(source.zip_path):
        return "already present"

    attempts = [("CDC", source.official_zip_url), ("Internet Archive", source.archive_zip_url)]
    for label, url in attempts:
        print(f"  {source.year}: trying {label} ...", flush=True)
        try:
            download_with_retries(url, source.zip_path, label, source.year)
        except Exception as error:  # HTTP 403, or retries exhausted
            print(f"  {source.year}: {label} failed ({error})", flush=True)
            continue
        if is_valid_zip(source.zip_path):
            return label
        print(f"  {source.year}: {label} returned something that is not a valid zip", flush=True)
        source.zip_path.unlink(missing_ok=True)
    raise RuntimeError(f"Could not obtain a valid {source.zip_name}")


def extract_xpt(source: BrfssYear) -> Path:
    with zipfile.ZipFile(source.zip_path) as archive:
        members = [name for name in archive.namelist() if name.strip().lower().endswith(".xpt")]
        if len(members) != 1:
            raise RuntimeError(f"{source.zip_name} should contain one .XPT file, found {members}")
        member = members[0]
        target = RAW_DATA_DIR / f"LLCP{source.year}.XPT"
        if target.exists() and target.stat().st_size == archive.getinfo(member).file_size:
            return target
        with archive.open(member) as packed, target.open("wb") as unpacked:
            shutil.copyfileobj(packed, unpacked, CHUNK_BYTES)
    return target


def print_manual_instructions(failed_years: list[int]) -> None:
    print("\nAutomatic download failed. Download these in your web browser:")
    for year in failed_years:
        source = BRFSS_YEARS[year]
        print(f"  {year}: {source.official_page_url}")
        print(f"        -> '{year} BRFSS Data (SAS Transport Format)' -> save as {source.zip_path}")
    print("Then run this script again; it will use the files you saved.")


def acquire_documentation(source: BrfssYear) -> None:
    """Download and unpack the year's codebook and SAS format files (small)."""
    DOCUMENTATION_DIR.mkdir(parents=True, exist_ok=True)
    for official_path in source.documentation_files:
        target = DOCUMENTATION_DIR / Path(official_path).name
        if not target.exists():
            try:
                download_with_retries(
                    f"https://www.cdc.gov/brfss/annual_data/{official_path}", target, "CDC", source.year
                )
            except Exception:
                download_with_retries(archive_url_for(official_path), target, "Internet Archive", source.year)
        if target.suffix.lower() == ".zip":
            with zipfile.ZipFile(target) as archive:
                archive.extractall(DOCUMENTATION_DIR / target.stem)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--years", type=int, nargs="+", default=sorted(BRFSS_YEARS))
    years = parser.parse_args().years

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    failed: list[int] = []
    for year in years:
        source = BRFSS_YEARS[year]
        try:
            origin = acquire_year(source)
            digest = sha256_of(source.zip_path)
            if digest != source.verified_zip_sha256:
                # Not fatal: CDC may publish a corrected release. The inspection
                # script then re-checks record and answer counts against the codebook.
                print(f"  {year}: WARNING sha256 {digest} differs from the verified file; re-run the inspection")
            xpt_path = extract_xpt(source)
            acquire_documentation(source)
        except Exception as error:
            print(f"  {year}: FAILED ({error})")
            failed.append(year)
            continue
        print(
            f"  {year}: OK from {origin}; zip {source.zip_path.stat().st_size:,} bytes, sha256 {digest}; "
            f"extracted {xpt_path.name} ({xpt_path.stat().st_size:,} bytes); codebook ready",
            flush=True,
        )
    if failed:
        print_manual_instructions(failed)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
