"""Send four documented demo profiles to a RUNNING Vytal backend and check the answers.

These profiles are made-up examples for demonstrations and checks, not real people.
The numbers printed are whatever the real models return; nothing is hard-coded.

Usage (backend running on port 8000):
    .venv\\Scripts\\python.exe scripts\\run_demo_profiles.py
    .venv\\Scripts\\python.exe scripts\\run_demo_profiles.py --base-url http://127.0.0.1:8000
Exit code 0 if every check passes, 1 otherwise.
"""

import argparse
import json
import math
import sys
import urllib.error
import urllib.request

DEMO_PROFILES = {
    "1. Few risk factors (34, female, active, never smoked)": {
        "age_years": 34, "sex": "female", "height_cm": 165, "weight_kg": 60, "smoking_status": "never",
        "ecigarette_current_use": "no", "physical_activity_past_30_days": "yes", "diabetes_status": "no",
        "stroke_history": "no", "kidney_disease_history": "no", "asthma_status": "never",
    },
    "2. Daily smoker (55, male, inactive, current asthma)": {
        "age_years": 55, "sex": "male", "height_cm": 178, "weight_kg": 88, "smoking_status": "current_daily",
        "ecigarette_current_use": "yes", "physical_activity_past_30_days": "no", "diabetes_status": "no",
        "stroke_history": "no", "kidney_disease_history": "no", "asthma_status": "current",
    },
    "3. Heart-history-heavy (71, male, diabetes, stroke, kidney disease)": {
        "age_years": 71, "sex": "male", "height_cm": 172, "weight_kg": 95, "smoking_status": "former",
        "ecigarette_current_use": "no", "physical_activity_past_30_days": "no", "diabetes_status": "yes",
        "stroke_history": "yes", "kidney_disease_history": "yes", "asthma_status": "never",
    },
    "4. Missing height and weight (48, female)": {
        "age_years": 48, "sex": "female", "height_cm": None, "weight_kg": None, "smoking_status": "former",
        "ecigarette_current_use": "no", "physical_activity_past_30_days": "yes", "diabetes_status": "prediabetes",
        "stroke_history": "no", "kidney_disease_history": "no", "asthma_status": "former",
    },
}
EXPECTED_STATUS = {"4. Missing height and weight (48, female)": "insufficient_input"}


def post(base_url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{base_url}/api/assessment/predict", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def check(name: str, body: dict) -> list[str]:
    problems = []
    expected = EXPECTED_STATUS.get(name, "ok")
    for result in body["results"]:
        if result["status"] != expected:
            problems.append(f"{result['model_id']}: status {result['status']}, expected {expected}")
        if expected == "ok":
            p = result["estimated_probability"]
            if p is None or not math.isfinite(p) or not 0 < p < 1:
                problems.append(f"{result['model_id']}: invalid estimate {p}")
            if result["category"] not in {"low", "moderate", "elevated", "high"}:
                problems.append(f"{result['model_id']}: invalid band {result['category']}")
        elif result["estimated_probability"] is not None:
            problems.append(f"{result['model_id']}: an estimate was returned without BMI")
    if not body["suggestions"] or body["suggestions"][0]["id"] != "urgent_symptoms":
        problems.append("urgent-symptoms notice missing or not first")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Vytal demo profiles")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    base_url = parser.parse_args().base_url.rstrip("/")
    failures = 0
    for name, profile in DEMO_PROFILES.items():
        try:
            body = post(base_url, profile)
        except (urllib.error.URLError, OSError) as error:
            print(f"Could not reach {base_url}: {error}. Start the backend first.")
            return 1
        print(f"\n{name}")
        for r in body["results"]:
            if r["status"] == "ok":
                factors = ", ".join(f"{f['feature']} {'+' if f['direction'] == 'raised' else '-'}" for f in r["contributing_factors"])
                print(f"  {r['model_id']:12} {r['estimated_probability'] * 100:5.1f}%  (survey average "
                      f"{r['survey_prevalence'] * 100:.1f}%, percentile {r['percentile']:.0f}, {r['category']})  factors: {factors}")
            else:
                print(f"  {r['model_id']:12} {r['status']}: {r['message']}")
        print("  suggestions: " + ", ".join(s["id"] for s in body["suggestions"]))
        problems = check(name, body)
        for problem in problems:
            print(f"  CHECK FAILED: {problem}")
        failures += bool(problems)
    print(f"\n{len(DEMO_PROFILES) - failures}/{len(DEMO_PROFILES)} profiles passed their checks.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
