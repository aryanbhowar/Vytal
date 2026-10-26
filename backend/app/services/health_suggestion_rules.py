"""General health-awareness suggestions as transparent, testable rules.

Each rule says WHEN it applies (a condition on the person's answers and results),
WHAT it says, and WHERE the guidance comes from. Rules never mention medicines,
doses, specific diets or supplements, and never state that a person has a condition.
Wording paraphrases WHO public guidance; links point to the original pages.
"""

from collections.abc import Callable
from dataclasses import dataclass

from app.schemas.assessment_schemas import ModelResult

ELEVATED_BANDS = {"elevated", "high"}


@dataclass(frozen=True)
class SuggestionContext:
    answers: dict[str, object]
    bmi: float | None
    results: dict[str, ModelResult]

    def band(self, model_id: str) -> str | None:
        result = self.results.get(model_id)
        return result.category if result and result.status == "ok" else None


@dataclass(frozen=True)
class SuggestionRule:
    id: str
    theme: str
    title: str
    body: str
    priority: str  # "urgent", "high" or "normal"
    source_name: str
    source_url: str
    applies: Callable[[SuggestionContext], bool]
    triggered_by: Callable[[SuggestionContext], list[str]]


def _always(_: SuggestionContext) -> bool:
    return True


def _nothing(_: SuggestionContext) -> list[str]:
    return []


def _fields(*names: str) -> Callable[[SuggestionContext], list[str]]:
    return lambda _: list(names)


def _elevated_models(context: SuggestionContext) -> list[str]:
    return [f"{model_id} result" for model_id in ("heart", "respiratory") if context.band(model_id) in ELEVATED_BANDS]


SUGGESTION_RULES: list[SuggestionRule] = [
    SuggestionRule(
        id="urgent_symptoms",
        theme="Safety",
        title="Urgent symptoms need care now, whatever your result",
        body=("Chest pain or pressure, pain spreading to the arm, jaw or back, sudden weakness or numbness of the "
              "face, arm or leg, trouble speaking, or severe shortness of breath can be signs of an emergency. "
              "Contact your local emergency number immediately. A low estimate from Vytal is never a reason to wait."),
        priority="urgent",
        source_name="WHO: Cardiovascular diseases (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)",
        applies=_always,
        triggered_by=_nothing,
    ),
    SuggestionRule(
        id="tobacco_cessation",
        theme="Tobacco",
        title="Support to stop smoking",
        body=("Stopping smoking at any age brings health benefits for the heart and lungs. Combining support "
              "such as counselling or a quit service with a health professional's advice gives the best chance "
              "of success."),
        priority="high",
        source_name="WHO: Tobacco (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/tobacco",
        applies=lambda c: c.answers["smoking_status"] in {"current_daily", "current_some_days"},
        triggered_by=_fields("smoking_status"),
    ),
    SuggestionRule(
        id="ecigarette_use",
        theme="Tobacco",
        title="E-cigarettes are not harmless",
        body=("E-cigarette aerosols contain substances that can harm health, and their long-term effects are not "
              "fully known. If you use them, a health professional can help you plan to stop."),
        priority="normal",
        source_name="WHO: Tobacco and e-cigarettes (Q&A)",
        source_url="https://www.who.int/news-room/questions-and-answers/item/tobacco-e-cigarettes",
        applies=lambda c: c.answers["ecigarette_current_use"] == "yes",
        triggered_by=_fields("ecigarette_current_use"),
    ),
    SuggestionRule(
        id="physical_activity",
        theme="Physical activity",
        title="Build up regular physical activity",
        body=("WHO recommends that adults do at least 150–300 minutes of moderate activity (such as brisk "
              "walking) or 75–150 minutes of vigorous activity each week, plus muscle-strengthening on two or "
              "more days. Any amount is better than none; start small and build up. If you have a health "
              "condition, ask a health professional what is right for you."),
        priority="high",
        source_name="WHO: Physical activity (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/physical-activity",
        applies=lambda c: c.answers["physical_activity_past_30_days"] == "no",
        triggered_by=_fields("physical_activity_past_30_days"),
    ),
    SuggestionRule(
        id="weight_above_healthy_range",
        theme="Weight",
        title="Support for a healthy weight",
        body=("Your BMI is above the WHO healthy range (18.5–24.9). BMI is a rough measure and does not account "
              "for muscle or body shape. Regular activity and a balanced eating pattern help, and a health "
              "professional can offer personalised weight-management support."),
        priority="normal",
        source_name="WHO: Obesity and overweight (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight",
        applies=lambda c: c.bmi is not None and c.bmi >= 25,
        triggered_by=_fields("bmi"),
    ),
    SuggestionRule(
        id="weight_below_healthy_range",
        theme="Weight",
        title="Your BMI is below the healthy range",
        body=("A BMI under 18.5 can be linked to poor nutrition or an underlying health problem. It is worth "
              "discussing with a health professional, especially if your weight has dropped without trying."),
        priority="normal",
        source_name="WHO: Malnutrition (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/malnutrition",
        applies=lambda c: c.bmi is not None and c.bmi < 18.5,
        triggered_by=_fields("bmi"),
    ),
    SuggestionRule(
        id="diabetes_follow_up",
        theme="Ongoing care",
        title="Keep up regular diabetes check-ups",
        body=("People with diabetes or prediabetes benefit from regular check-ups with a health professional, "
              "including blood glucose, blood pressure and cholesterol checks. Physical activity, a healthy "
              "weight and not smoking also help."),
        priority="normal",
        source_name="WHO: Diabetes (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/diabetes",
        applies=lambda c: c.answers["diabetes_status"] in {"yes", "prediabetes"},
        triggered_by=_fields("diabetes_status"),
    ),
    SuggestionRule(
        id="cardiovascular_history_follow_up",
        theme="Ongoing care",
        title="Stay in touch with your care team",
        body=("After a stroke or with kidney disease, regular reviews with a health professional help manage "
              "your health and reduce the chance of further problems."),
        priority="normal",
        source_name="WHO: Stroke, cerebrovascular accident",
        source_url="https://www.who.int/news-room/fact-sheets/detail/stroke",
        applies=lambda c: c.answers["stroke_history"] == "yes" or c.answers["kidney_disease_history"] == "yes",
        triggered_by=lambda c: [f for f in ("stroke_history", "kidney_disease_history") if c.answers[f] == "yes"],
    ),
    SuggestionRule(
        id="asthma_care",
        theme="Ongoing care",
        title="Review your asthma care",
        body=("If you have asthma now, a written plan agreed with a health professional and regular reviews help "
              "keep it under control. Avoiding tobacco smoke also helps."),
        priority="normal",
        source_name="WHO: Asthma (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/asthma",
        applies=lambda c: c.answers["asthma_status"] == "current",
        triggered_by=_fields("asthma_status"),
    ),
    SuggestionRule(
        id="discuss_heart_result",
        theme="Check-up",
        title="Consider a heart health check",
        body=("Your heart estimate is higher than most survey respondents'. This is not a diagnosis, but it is "
              "a good reason to ask a health professional for a heart health check, which can include blood "
              "pressure and cholesterol."),
        priority="high",
        source_name="WHO: Cardiovascular diseases (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)",
        applies=lambda c: c.band("heart") in ELEVATED_BANDS,
        triggered_by=lambda c: ["heart result"],
    ),
    SuggestionRule(
        id="discuss_lung_result",
        theme="Check-up",
        title="Mention breathing symptoms to a professional",
        body=("Your lung estimate is higher than most survey respondents'. This is not a diagnosis. If you have "
              "a long-lasting cough, phlegm or breathlessness, ask a health professional about a lung check, "
              "which may include a simple breathing test (spirometry)."),
        priority="high",
        source_name="WHO: Chronic obstructive pulmonary disease (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/chronic-obstructive-pulmonary-disease-(copd)",
        applies=lambda c: c.band("respiratory") in ELEVATED_BANDS,
        triggered_by=lambda c: ["respiratory result"],
    ),
    SuggestionRule(
        id="know_your_numbers",
        theme="Check-up",
        title="Know your blood pressure and cholesterol",
        body=("Vytal cannot include blood pressure or cholesterol, but both matter for heart health and high "
              "blood pressure often has no symptoms. Having them checked regularly is a simple way to learn more "
              "than this estimate can tell you."),
        priority="normal",
        source_name="WHO: Hypertension (fact sheet)",
        source_url="https://www.who.int/news-room/fact-sheets/detail/hypertension",
        applies=_always,
        triggered_by=_nothing,
    ),
]

PRIORITY_ORDER = {"urgent": 0, "high": 1, "normal": 2}
