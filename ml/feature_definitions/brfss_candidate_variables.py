"""BRFSS variables considered for Vytal, with their source name in each survey year.

This list is what Task 2 inspects. Being on this list does NOT mean a variable is
used by a model; the final feature lists are decided from the inspection evidence
and recorded in docs/decisions/DECISION_LOG.md.
"""

from dataclasses import dataclass

from ml.feature_definitions.feature_schema import model_definition, model_features

SURVEY_YEARS = (2022, 2023, 2024)


@dataclass(frozen=True)
class CandidateVariable:
    canonical_name: str
    role: str  # "target", "target_component", "feature", "measurement", "survey_design"
    description: str
    source_by_year: dict[int, str]
    continuous: bool = False

    def source(self, year: int) -> str:
        return self.source_by_year[year]


def _same_name(name: str) -> dict[int, str]:
    return {year: name for year in SURVEY_YEARS}


CANDIDATE_VARIABLES: list[CandidateVariable] = [
    # Targets
    CandidateVariable("heart_target", "target", "Ever reported CHD or heart attack (calculated)", _same_name("_MICHD")),
    CandidateVariable("heart_attack_ever", "target_component", "Ever told had a heart attack", _same_name("CVDINFR4")),
    CandidateVariable("coronary_heart_disease_ever", "target_component", "Ever told had angina or CHD", _same_name("CVDCRHD4")),
    CandidateVariable("copd_target", "target", "Ever told had COPD, emphysema or chronic bronchitis", _same_name("CHCCOPD3")),
    # Demographics and measurements
    CandidateVariable("age_group", "feature", "Five-year age group (calculated)", _same_name("_AGEG5YR")),
    CandidateVariable("sex", "feature", "Sex of respondent", _same_name("SEXVAR")),
    CandidateVariable("bmi", "feature", "Body mass index x 100 (calculated)", _same_name("_BMI5"), continuous=True),
    CandidateVariable("height_m", "measurement", "Height in metres x 100 (calculated)", _same_name("HTM4"), continuous=True),
    CandidateVariable("weight_kg", "measurement", "Weight in kg x 100 (calculated)", _same_name("WTKG3"), continuous=True),
    # Lifestyle
    CandidateVariable("smoking_status", "feature", "Four-level smoker status (calculated)", _same_name("_SMOKER3")),
    CandidateVariable(
        "ecigarette_current_use", "feature", "Current e-cigarette user (calculated)",
        {2022: "_CURECI2", 2023: "_CURECI2", 2024: "_CURECI3"},
    ),
    CandidateVariable(
        "ecigarette_use_now", "feature", "Now use e-cigarettes (question)",
        {2022: "ECIGNOW2", 2023: "ECIGNOW2", 2024: "ECIGNOW3"},
    ),
    CandidateVariable("physical_activity_past_30_days", "feature", "Any exercise in past 30 days", _same_name("EXERANY2")),
    CandidateVariable(
        "heavy_alcohol_use", "feature", "Heavy drinker (calculated)",
        {2022: "_RFDRHV8", 2023: "_RFDRHV8", 2024: "_RFDRHV9"},
    ),
    # Health history
    CandidateVariable("diabetes_status", "feature", "Ever told had diabetes", _same_name("DIABETE4")),
    CandidateVariable("stroke_history", "feature", "Ever told had a stroke", _same_name("CVDSTRK3")),
    CandidateVariable("kidney_disease_history", "feature", "Ever told had kidney disease", _same_name("CHCKDNY2")),
    CandidateVariable("asthma_ever", "feature", "Ever told had asthma", _same_name("ASTHMA3")),
    CandidateVariable("asthma_status", "feature", "Asthma status: current/former/never (calculated)", _same_name("_ASTHMS1")),
    CandidateVariable("high_blood_pressure", "feature", "Ever told blood pressure high", _same_name("BPHIGH6")),
    CandidateVariable("cholesterol_checked", "feature", "Time since cholesterol checked", _same_name("CHOLCHK3")),
    CandidateVariable("high_cholesterol", "feature", "Ever told cholesterol high", _same_name("TOLDHI3")),
    # Survey design (never model features)
    CandidateVariable("survey_weight", "survey_design", "Final combined landline/cell weight", _same_name("_LLCPWT"), continuous=True),
    CandidateVariable("sampling_stratum", "survey_design", "Sample design stratum", _same_name("_STSTR"), continuous=True),
    CandidateVariable("primary_sampling_unit", "survey_design", "Primary sampling unit", _same_name("_PSU"), continuous=True),
]


# Codes that mean "no usable answer" for each variable (don't know, refused,
# not asked, missing). From the official codebooks; identical in all three years.
# These rows are excluded, never recoded to "no".
INVALID_CODES: dict[str, set[str]] = {
    "heart_target": {"BLANK"},
    "copd_target": {"7", "9", "BLANK"},
    "age_group": {"14"},
    "sex": set(),
    "bmi": {"BLANK"},
    "smoking_status": {"9"},
    "ecigarette_current_use": {"9"},
    "physical_activity_past_30_days": {"7", "9", "BLANK"},
    "heavy_alcohol_use": {"9"},
    "diabetes_status": {"7", "9", "BLANK"},
    "stroke_history": {"7", "9", "BLANK"},
    "kidney_disease_history": {"7", "9", "BLANK"},
    "asthma_status": {"9"},
}

# Final feature sets (D-023, D-024) live in vytal_feature_schema.json.
PROPOSED_MODEL_FEATURES: dict[str, list[str]] = {
    model: model_features(model) for model in ("heart", "respiratory")
}
MODEL_TARGETS = {model: model_definition(model)["target"] for model in ("heart", "respiratory")}
POSITIVE_TARGET_CODE = "1"


def candidate_by_name(canonical_name: str) -> CandidateVariable:
    for candidate in CANDIDATE_VARIABLES:
        if candidate.canonical_name == canonical_name:
            return candidate
    raise KeyError(canonical_name)
