"""Apply the suggestion rules to one assessment."""

from app.schemas.assessment_schemas import ModelResult, Suggestion
from app.services.health_suggestion_rules import PRIORITY_ORDER, SUGGESTION_RULES, SuggestionContext
from app.services.input_preprocessing_service import PreparedAssessment


def build_suggestions(prepared: PreparedAssessment, results: list[ModelResult]) -> list[Suggestion]:
    context = SuggestionContext(prepared.answers(), prepared.bmi, {r.model_id: r for r in results})
    matched = [rule for rule in SUGGESTION_RULES if rule.applies(context)]
    matched.sort(key=lambda rule: PRIORITY_ORDER[rule.priority])  # stable: keeps rule order within a priority
    return [
        Suggestion(id=rule.id, theme=rule.theme, title=rule.title, body=rule.body,
                   triggered_by=rule.triggered_by(context), priority=rule.priority,
                   source_name=rule.source_name, source_url=rule.source_url)
        for rule in matched
    ]
