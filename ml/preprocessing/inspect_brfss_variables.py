"""Inspect the BRFSS 2022-2024 files and codebooks for every candidate variable.

Checks, for each year:
  * the file has the record and variable counts CDC publishes (it is complete);
  * each candidate variable exists in the codebook and in the data file;
  * the actual value counts in the file equal the codebook's published frequencies;
and, across years:
  * whether the question wording and answer codes are identical.

Only the candidate columns are read, so memory use stays low (about 100 MB).

Outputs:
  datasets/processed/brfss_variable_inspection_summary.json  (aggregate counts only)
  docs/datasets/brfss_variable_availability.md                (generated report)

Usage (from the project root):
    .venv\\Scripts\\python.exe -m ml.preprocessing.inspect_brfss_variables
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pyreadstat

from ml.feature_definitions.brfss_candidate_variables import (
    CANDIDATE_VARIABLES,
    INVALID_CODES,
    MODEL_TARGETS,
    POSITIVE_TARGET_CODE,
    PROPOSED_MODEL_FEATURES,
    SURVEY_YEARS,
    CandidateVariable,
    candidate_by_name,
)
from ml.preprocessing.brfss_codebook import CodebookVariable, load_codebook
from ml.preprocessing.brfss_sources import BRFSS_YEARS, PROCESSED_DATA_DIR, PROJECT_ROOT, RAW_DATA_DIR

SUMMARY_PATH = PROCESSED_DATA_DIR / "brfss_variable_inspection_summary.json"
REPORT_PATH = PROJECT_ROOT / "docs" / "datasets" / "brfss_variable_availability.md"


def xpt_path(year: int) -> Path:
    return RAW_DATA_DIR / f"LLCP{year}.XPT"


# Some variable labels contain non-UTF-8 bytes (e.g. 0xB4, an acute accent in
# Latin-1). SAS on Windows writes Latin-1, so decode labels that way.
XPT_ENCODING = "latin1"


def read_file_metadata(year: int) -> dict:
    _, meta = pyreadstat.read_xport(str(xpt_path(year)), metadataonly=True, encoding=XPT_ENCODING)
    return {"columns": list(meta.column_names), "file_label": meta.file_label}


def read_candidate_columns(year: int, columns: list[str]) -> pd.DataFrame:
    frame, _ = pyreadstat.read_xport(str(xpt_path(year)), usecols=columns, encoding=XPT_ENCODING)
    return frame


def observed_counts(series: pd.Series) -> dict[str, int]:
    """Value counts keyed like the codebook: integer codes as text, missing as BLANK."""
    counts: dict[str, int] = {}
    for value, count in series.value_counts(dropna=False).items():
        if pd.isna(value):
            key = "BLANK"
        elif float(value).is_integer():
            key = str(int(value))
        else:
            key = str(value)
        counts[key] = int(count)
    return counts


def compare_with_codebook(observed: dict[str, int], entry: CodebookVariable) -> list[str]:
    """Return mismatches between file counts and the codebook's published counts."""
    problems = []
    for value in entry.values:
        if value.frequency is None or " - " in value.code or "-" in value.code.strip("-"):
            continue  # ranges such as "1 - 30" are not single codes
        actual = observed.get(value.code, 0)
        if actual != value.frequency:
            problems.append(f"code {value.code}: codebook {value.frequency:,}, file {actual:,}")
    return problems


def continuous_summary(series: pd.Series) -> dict:
    present = series.dropna()
    return {
        "non_missing": int(present.size),
        "missing": int(series.isna().sum()),
        "min": float(present.min()) if present.size else None,
        "max": float(present.max()) if present.size else None,
        "median": float(present.median()) if present.size else None,
    }


_SKIP_INSTRUCTION = re.compile(r"(go to section|code=).*$", re.I)
_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")


def normalised(text: str) -> str:
    """Reduce a label or question to its meaning-bearing words for comparison.

    Removes skip instructions ("Go to Section 08.01 AGE", renumbered every year),
    derivation notes ("Code=1 if LANDSEX1=1 ..."), and punctuation, including the
    curly apostrophes and dashes that are encoded differently in each year's file.
    """
    text = _SKIP_INSTRUCTION.sub("", text.lower())
    return _NON_ALPHANUMERIC.sub("", text.encode("ascii", "ignore").decode())


def inspect_candidate(candidate: CandidateVariable, codebooks: dict, frames: dict) -> dict:
    per_year = {}
    for year in SURVEY_YEARS:
        source = candidate.source(year)
        entry = codebooks[year].get(source)
        in_file = source in frames[year].columns
        record = {"source_variable": source, "in_codebook": entry is not None, "in_file": in_file}
        if entry is not None:
            record["question"] = entry.question
            record["label"] = entry.label
            record["codes"] = entry.code_map()
        if in_file:
            series = frames[year][source]
            if candidate.continuous:
                record["summary"] = continuous_summary(series)
            else:
                record["observed_counts"] = observed_counts(series)
                if entry is not None:
                    record["codebook_mismatches"] = compare_with_codebook(record["observed_counts"], entry)
        per_year[year] = record

    available_years = [y for y in SURVEY_YEARS if per_year[y]["in_codebook"] and per_year[y]["in_file"]]
    questions = {normalised(per_year[y]["question"]) for y in available_years}
    code_maps = {
        json.dumps({k: normalised(v) for k, v in per_year[y]["codes"].items()}, sort_keys=True)
        for y in available_years
    }
    return {
        "canonical_name": candidate.canonical_name,
        "role": candidate.role,
        "description": candidate.description,
        "available_years": available_years,
        "in_all_years": len(available_years) == len(SURVEY_YEARS),
        "question_identical_across_years": len(questions) <= 1,
        "codes_identical_across_years": len(code_maps) <= 1,
        "codebook_counts_match_file": all(
            not per_year[y].get("codebook_mismatches") for y in available_years
        ),
        "by_year": per_year,
    }


def check_file_completeness(year: int, columns: list[str], row_count: int, codebook: dict) -> dict:
    """A file counts as complete when its record count equals CDC's published count.

    Variable counts are recorded but not used as a pass/fail test: CDC's data pages
    reuse template text (all three years say "ZIP – 64.3 MB", and 2024 says 345
    variables while its own codebook lists 297), so they are not reliable.
    """
    expected = BRFSS_YEARS[year]
    return {
        "records": row_count,
        "expected_records": expected.expected_records,
        "variables_in_file": len(columns),
        "variables_on_cdc_page": expected.expected_variables,
        "variables_in_codebook": len(codebook),
        "codebook_variables_missing_from_file": sorted(set(codebook) - set(columns)),
        "file_variables_not_in_codebook": sorted(set(columns) - set(codebook)),
        "complete": row_count == expected.expected_records,
    }


def code_series(frame: pd.DataFrame, candidate: CandidateVariable, year: int) -> pd.Series:
    """Return the column as codebook-style text codes ('1', '9', 'BLANK')."""
    series = frame[candidate.source(year)]
    if candidate.continuous:
        return series.map(lambda v: "BLANK" if pd.isna(v) else "value")
    return series.map(lambda v: "BLANK" if pd.isna(v) else str(int(v)))


def model_sample_counts(frames: dict) -> dict:
    """Per model and year: target counts, unusable-answer rates and complete cases."""
    results = {}
    for model, target_name in MODEL_TARGETS.items():
        target = candidate_by_name(target_name)
        per_year = {}
        for year in SURVEY_YEARS:
            frame = frames[year]
            target_codes = code_series(frame, target, year)
            target_valid = ~target_codes.isin(INVALID_CODES[target_name])
            positive = target_codes == POSITIVE_TARGET_CODE
            feature_invalid = {}
            prevalence_when_unusable = {}
            usable = target_valid.copy()
            for feature_name in PROPOSED_MODEL_FEATURES[model]:
                codes = code_series(frame, candidate_by_name(feature_name), year)
                invalid = codes.isin(INVALID_CODES[feature_name])
                feature_invalid[feature_name] = round(float(invalid[target_valid].mean()) * 100, 2)
                # Selection-bias check: do people with an unusable answer report the
                # condition at a different rate from people with a usable answer?
                dropped = invalid & target_valid
                prevalence_when_unusable[feature_name] = (
                    round(float(positive[dropped].mean()) * 100, 2) if dropped.any() else None
                )
                usable &= ~invalid
            excluded = target_valid & ~usable
            weights = frame["_LLCPWT"]
            per_year[year] = {
                "records": int(len(frame)),
                "target_positive": int(positive.sum()),
                "target_negative": int((target_valid & ~positive).sum()),
                "target_unusable": int((~target_valid).sum()),
                "unusable_answer_percent_by_feature": feature_invalid,
                "prevalence_percent_among_unusable_by_feature": prevalence_when_unusable,
                "complete_cases": int(usable.sum()),
                "complete_case_prevalence_percent": round(float(positive[usable].mean()) * 100, 2),
                "excluded_for_feature_answers": int(excluded.sum()),
                "prevalence_percent_among_excluded": round(float(positive[excluded].mean()) * 100, 2),
                "weighted_prevalence_percent_all_valid": round(
                    float(weights[positive].sum() / weights[target_valid].sum()) * 100, 2
                ),
            }
        complete = sum(per_year[y]["complete_cases"] for y in SURVEY_YEARS)
        positives = sum(
            round(per_year[y]["complete_cases"] * per_year[y]["complete_case_prevalence_percent"] / 100)
            for y in SURVEY_YEARS
        )
        results[model] = {
            "target": target_name,
            "features": PROPOSED_MODEL_FEATURES[model],
            "by_year": per_year,
            "pooled_complete_cases": complete,
            "pooled_complete_case_positives_approx": positives,
        }
    return results


def yes_no(flag: bool) -> str:
    return "yes" if flag else "**NO**"


def write_report(files: dict, results: list[dict], samples: dict) -> None:
    lines = [
        "# BRFSS 2022–2024 variable availability (generated)",
        "",
        f"_Generated by `ml/preprocessing/inspect_brfss_variables.py` on {date.today().isoformat()}. "
        "Do not edit by hand; re-run the script. The interpretation of these results is in "
        "`datasets/DATA_SOURCES.md` and the decision log._",
        "",
        "## File completeness",
        "",
        "A file is treated as complete when its record count equals CDC's published count. "
        "Variable counts are shown for transparency only (see `check_file_completeness`).",
        "",
        "| Year | Records in file | CDC published records | Complete | Variables in file | In codebook | On CDC page | Codebook variables missing from file | File variables not in codebook |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for year, info in files.items():
        lines.append(
            f"| {year} | {info['records']:,} | {info['expected_records']:,} | {yes_no(info['complete'])} "
            f"| {info['variables_in_file']} | {info['variables_in_codebook']} | {info['variables_on_cdc_page']} "
            f"| {', '.join(info['codebook_variables_missing_from_file']) or 'none'} "
            f"| {', '.join(info['file_variables_not_in_codebook']) or 'none'} |"
        )
    lines += ["", "## Sample counts for the proposed pooled models", ""]
    for model, info in samples.items():
        lines += [
            f"### {model} (target `{info['target']}`)",
            "",
            f"Proposed features: {', '.join('`' + f + '`' for f in info['features'])}.",
            "",
            "| Year | Positive | Negative | Target unusable | Complete cases | Prevalence in complete cases | Weighted prevalence (all valid targets) |",
            "|---|---|---|---|---|---|---|",
        ]
        for year in SURVEY_YEARS:
            r = info["by_year"][year]
            lines.append(
                f"| {year} | {r['target_positive']:,} | {r['target_negative']:,} | {r['target_unusable']:,} "
                f"| {r['complete_cases']:,} | {r['complete_case_prevalence_percent']}% "
                f"| {r['weighted_prevalence_percent_all_valid']}% |"
            )
        lines += [
            "",
            f"Pooled complete cases: {info['pooled_complete_cases']:,} "
            f"(about {info['pooled_complete_case_positives_approx']:,} positive).",
            "",
            "Rows excluded because of an unusable feature answer, and how often they reported the condition "
            "(compare with the complete-case prevalence above):",
            "",
            "| Year | Excluded rows | Prevalence among excluded |",
            "|---|---|---|",
        ]
        for year in SURVEY_YEARS:
            r = info["by_year"][year]
            lines.append(f"| {year} | {r['excluded_for_feature_answers']:,} | {r['prevalence_percent_among_excluded']}% |")
        lines += [
            "",
            "Unusable answers (don't know, refused, missing) as % of rows with a valid target, and the "
            "condition's prevalence among those rows:",
            "",
            "| Feature | " + " | ".join(f"{y} unusable | {y} prevalence" for y in SURVEY_YEARS) + " |",
            "|---|" + "---|---|" * len(SURVEY_YEARS),
        ]
        for feature in info["features"]:
            cells = []
            for y in SURVEY_YEARS:
                r = info["by_year"][y]
                prevalence = r["prevalence_percent_among_unusable_by_feature"][feature]
                cells.append(f"{r['unusable_answer_percent_by_feature'][feature]}%")
                cells.append("—" if prevalence is None else f"{prevalence}%")
            lines.append(f"| `{feature}` | " + " | ".join(cells) + " |")
        lines.append("")
    lines += [
        "",
        "## Summary per candidate variable",
        "",
        "\"Counts match\" means the number of respondents giving each answer in the downloaded file equals "
        "the number printed in CDC's codebook for that year.",
        "",
        "| Variable | Role | Source names (2022 / 2023 / 2024) | In all 3 years | Same question | Same answer codes | Counts match codebook |",
        "|---|---|---|---|---|---|---|",
    ]
    for result in results:
        names = " / ".join(
            result["by_year"][y]["source_variable"] + ("" if result["by_year"][y]["in_file"] else " (absent)")
            for y in SURVEY_YEARS
        )
        lines.append(
            f"| `{result['canonical_name']}` | {result['role']} | {names} | {yes_no(result['in_all_years'])} "
            f"| {yes_no(result['question_identical_across_years'])} | {yes_no(result['codes_identical_across_years'])} "
            f"| {yes_no(result['codebook_counts_match_file'])} |"
        )
    lines += ["", "## Details per variable", ""]
    for result in results:
        lines += [f"### `{result['canonical_name']}`: {result['description']}", ""]
        for year in SURVEY_YEARS:
            record = result["by_year"][year]
            if not record["in_codebook"]:
                lines.append(f"- **{year}** (`{record['source_variable']}`): not in codebook or file.")
                continue
            lines.append(f"- **{year}** (`{record['source_variable']}`): {record['question'] or record['label']}")
            if "summary" in record:
                s = record["summary"]
                lines.append(
                    f"  - non-missing {s['non_missing']:,}, missing {s['missing']:,}, "
                    f"min {s['min']}, median {s['median']}, max {s['max']}"
                )
            else:
                counts = record.get("observed_counts", {})
                for code, label in record["codes"].items():
                    lines.append(f"  - `{code}` {label}: {counts.get(code, '—') if ' - ' not in code else 'range'}")
                for problem in record.get("codebook_mismatches", []):
                    lines.append(f"  - mismatch: {problem}")
        lines.append("")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    missing = [year for year in SURVEY_YEARS if not xpt_path(year).exists()]
    if missing:
        print(f"Missing data files for {missing}. Run ml.preprocessing.download_brfss_data first.")
        return 1

    codebooks = {year: load_codebook(year) for year in SURVEY_YEARS}
    frames, files = {}, {}
    for year in SURVEY_YEARS:
        all_columns = read_file_metadata(year)["columns"]
        wanted = sorted({c.source(year) for c in CANDIDATE_VARIABLES} & set(all_columns))
        print(f"{year}: reading {len(wanted)} candidate columns ...", flush=True)
        frames[year] = read_candidate_columns(year, wanted)
        files[year] = check_file_completeness(year, all_columns, len(frames[year]), codebooks[year])

    results = [inspect_candidate(candidate, codebooks, frames) for candidate in CANDIDATE_VARIABLES]
    samples = model_sample_counts(frames)

    print("\nFile completeness (record count vs CDC):")
    for year, info in files.items():
        print(f"  {year}: {info['records']:,} records (CDC {info['expected_records']:,}) -> "
              f"{'complete' if info['complete'] else 'MISMATCH'}; {info['variables_in_file']} variables "
              f"(codebook {info['variables_in_codebook']})")
    for model, info in samples.items():
        print(f"\n{model}: pooled complete cases {info['pooled_complete_cases']:,}")
        for year in SURVEY_YEARS:
            r = info["by_year"][year]
            print(f"  {year}: complete {r['complete_cases']:,}, prevalence {r['complete_case_prevalence_percent']}% "
                  f"(weighted {r['weighted_prevalence_percent_all_valid']}%); excluded {r['excluded_for_feature_answers']:,} "
                  f"with prevalence {r['prevalence_percent_among_excluded']}%")
            print(f"      prevalence among unusable answers: {r['prevalence_percent_among_unusable_by_feature']}")
    print(f"\n{'variable':32} {'all years':9} {'question':9} {'codes':6} {'counts':6}")
    for r in results:
        print(f"{r['canonical_name']:32} {str(r['in_all_years']):9} "
              f"{str(r['question_identical_across_years']):9} {str(r['codes_identical_across_years']):6} "
              f"{str(r['codebook_counts_match_file']):6}")

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(
        json.dumps(
            {"generated": date.today().isoformat(), "files": files, "model_samples": samples, "variables": results},
            indent=2,
        ),
        encoding="utf-8",
    )
    write_report(files, results, samples)
    print(f"\nWrote {SUMMARY_PATH.relative_to(PROJECT_ROOT)} and {REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
