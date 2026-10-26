"""Turn a model's raw output into the result a person sees.

Kept separate from inference so the wording and rules can be reviewed on their own.
Categories are positions among survey respondents (D-010), not clinical risk levels.
"""

from app.schemas.assessment_schemas import BandValidation, ContributingFactor, ModelResult
from app.services.input_preprocessing_service import PreparedAssessment, answer_label
from app.services.model_registry import MODEL_TITLES
from ml.feature_definitions.feature_schema import feature_definition
from ml.inference.risk_model import LoadedRiskModel

MAX_FACTORS_SHOWN = 5
# Contributions smaller than this (in log-odds) change the estimate by well under
# 1% in relative terms and are not worth showing as "factors".
MIN_FACTOR_LOG_ODDS = 0.02

DISCLAIMER = (
    "Vytal is not a diagnosis and has not been clinically validated. Its estimates describe patterns in "
    "answers given by US adults to a CDC health survey and cannot tell you whether you have, or will develop, "
    "any condition. Talk to a qualified health professional about your health. If you have chest pain, "
    "severe breathlessness, or other urgent symptoms, seek emergency care now."
)
DATA_ATTRIBUTION = (
    "Source: CDC, Behavioral Risk Factor Surveillance System 2022–2024. Vytal's use of these data does not "
    "imply endorsement by CDC, HHS or the U.S. Government. The original data are available free of charge "
    "from cdc.gov."
)

BAND_TEXT = {
    "low": "Lower than about half of survey respondents.",
    "moderate": "Higher than about half of survey respondents, but lower than the top quarter.",
    "elevated": "Among the top quarter of survey respondents, but not the top tenth.",
    "high": "Among the top tenth of survey respondents.",
}

COMMON_LIMITATIONS = [
    "Based on what people told a telephone survey; it is an association with reported conditions, not a diagnosis or a prediction of the future.",
    "Represents US adults; it may not apply as well to other populations.",
    "Factors show what the model associates with the condition, not what causes it.",
]
MODEL_LIMITATIONS = {
    "heart": ["Blood pressure and cholesterol, two major heart risk factors, are not included because the survey did not ask them every year."],
    "respiratory": ["COPD, emphysema and chronic bronchitis are combined in one survey question; asthma is used as an input, not part of this outcome."],
}


def contributing_factors(model: LoadedRiskModel, prepared: PreparedAssessment) -> list[ContributingFactor]:
    row = prepared.feature_row(model.model_id)
    contributions = model.contributions(row).iloc[0]
    answers = prepared.answers()
    ranked = sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)
    factors = []
    for feature, value in ranked:
        if abs(value) < MIN_FACTOR_LOG_ODDS or len(factors) == MAX_FACTORS_SHOWN:
            continue
        definition = feature_definition(feature)
        factors.append(ContributingFactor(
            feature=feature,
            label=definition["question"],
            answer=answer_label(feature, answers[feature]),
            direction="raised" if value > 0 else "lowered",
            log_odds_contribution=round(float(value), 4),
            modifiable=bool(definition["modifiable"]),
        ))
    return factors


def interpret(model: LoadedRiskModel, prepared: PreparedAssessment) -> ModelResult:
    metadata = model.metadata
    row = prepared.feature_row(model.model_id)
    probability = float(model.probability(row)[0])
    percentile = float(model.percentile(probability)[0])
    band = model.band(probability)
    band_check = metadata["evaluation"]["test_band_validation"][band]
    calibrated = metadata["calibration_method"] != "none needed"
    return ModelResult(
        model_id=model.model_id,
        title=MODEL_TITLES[model.model_id],
        outcome_description=metadata["outcome_description"],
        status="ok",
        estimated_probability=round(probability, 4),
        survey_prevalence=round(float(metadata["training_data"]["weighted_us_adult_prevalence"]), 4),
        percentile=round(percentile, 1),
        category=band,
        category_explanation=BAND_TEXT[band],
        band_validation=BandValidation(
            observed_rate=round(float(band_check["observed_prevalence"]), 4),
            share_of_respondents=round(float(band_check["share_of_respondents"]), 4),
        ),
        contributing_factors=contributing_factors(model, prepared),
        explanation_note=(
            "Factors are compared with an average survey respondent. They explain the model's score before a "
            "final calibration step, which keeps the order of people the same but adjusts the scale."
            if calibrated else "Factors are compared with an average survey respondent."
        ),
        limitations=COMMON_LIMITATIONS + MODEL_LIMITATIONS[model.model_id],
        model_version=metadata["model_version"],
    )


def unavailable_result(model_id: str, reason: str) -> ModelResult:
    return ModelResult(model_id=model_id, title=MODEL_TITLES[model_id], outcome_description="",
                       status="unavailable", message=f"This estimate is not available right now. {reason}")


def insufficient_input_result(model: LoadedRiskModel) -> ModelResult:
    return ModelResult(
        model_id=model.model_id, title=MODEL_TITLES[model.model_id],
        outcome_description=model.metadata["outcome_description"], status="insufficient_input",
        message="This estimate needs your height and weight (to calculate BMI). Vytal does not guess missing values.",
        model_version=model.metadata["model_version"],
    )
