"""One test per suggestion rule: it fires when it should and stays silent otherwise.

Results here are SYNTHETIC ModelResult objects, not real model output.
"""

import re

import pytest

from app.schemas.assessment_schemas import ModelResult
from app.services.health_suggestion_rules import SUGGESTION_RULES, SuggestionContext

BASE_ANSWERS = {
    "sex": "female", "smoking_status": "never", "ecigarette_current_use": "no",
    "physical_activity_past_30_days": "yes", "diabetes_status": "no", "stroke_history": "no",
    "kidney_disease_history": "no", "asthma_status": "never", "age_group": "40-44", "bmi": 22.0,
}
RULES = {rule.id: rule for rule in SUGGESTION_RULES}


def result(model_id: str, band: str | None, status: str = "ok") -> ModelResult:
    return ModelResult(model_id=model_id, title="t", outcome_description="d", status=status, category=band)


def context(answers=None, bmi=22.0, heart="low", respiratory="low") -> SuggestionContext:
    merged = dict(BASE_ANSWERS, **(answers or {}))
    return SuggestionContext(merged, bmi, {"heart": result("heart", heart), "respiratory": result("respiratory", respiratory)})


def fired(ctx: SuggestionContext) -> set[str]:
    return {rule.id for rule in SUGGESTION_RULES if rule.applies(ctx)}


def test_baseline_profile_gets_only_the_always_on_notices():
    assert fired(context()) == {"urgent_symptoms", "know_your_numbers"}


@pytest.mark.parametrize("rule_id,ctx", [
    ("tobacco_cessation", context({"smoking_status": "current_daily"})),
    ("tobacco_cessation", context({"smoking_status": "current_some_days"})),
    ("ecigarette_use", context({"ecigarette_current_use": "yes"})),
    ("physical_activity", context({"physical_activity_past_30_days": "no"})),
    ("weight_above_healthy_range", context(bmi=27.0)),
    ("weight_below_healthy_range", context(bmi=17.9)),
    ("diabetes_follow_up", context({"diabetes_status": "yes"})),
    ("diabetes_follow_up", context({"diabetes_status": "prediabetes"})),
    ("cardiovascular_history_follow_up", context({"stroke_history": "yes"})),
    ("cardiovascular_history_follow_up", context({"kidney_disease_history": "yes"})),
    ("asthma_care", context({"asthma_status": "current"})),
    ("discuss_heart_result", context(heart="elevated")),
    ("discuss_heart_result", context(heart="high")),
    ("discuss_lung_result", context(respiratory="high")),
])
def test_rule_fires_when_condition_met(rule_id, ctx):
    assert rule_id in fired(ctx)


@pytest.mark.parametrize("rule_id,ctx", [
    ("tobacco_cessation", context({"smoking_status": "former"})),
    ("weight_above_healthy_range", context(bmi=24.9)),
    ("weight_above_healthy_range", context(bmi=None)),
    ("weight_below_healthy_range", context(bmi=18.5)),
    ("diabetes_follow_up", context({"diabetes_status": "gestational_only"})),
    ("asthma_care", context({"asthma_status": "former"})),
    ("discuss_heart_result", context(heart="moderate")),
    ("discuss_lung_result", context(respiratory="moderate")),
])
def test_rule_silent_when_condition_not_met(rule_id, ctx):
    assert rule_id not in fired(ctx)


def test_unavailable_model_never_triggers_result_based_advice():
    ctx = SuggestionContext(dict(BASE_ANSWERS), 22.0, {"heart": result("heart", "high", status="unavailable")})
    assert "discuss_heart_result" not in fired(ctx)


def test_no_rule_mentions_medicines_doses_diets_or_supplements():
    forbidden = re.compile(r"\b(medication|medicine|drug|dose|dosage|mg|tablet|pill|statin|aspirin|inhaler|"
                           r"supplement|vitamin|diet plan|keto|fasting|prescri\w*)\b", re.I)
    for rule in SUGGESTION_RULES:
        assert not forbidden.search(rule.title + " " + rule.body), rule.id


def test_every_rule_cites_a_who_source():
    for rule in SUGGESTION_RULES:
        assert rule.source_url.startswith("https://www.who.int/"), rule.id
        assert rule.priority in {"urgent", "high", "normal"}
