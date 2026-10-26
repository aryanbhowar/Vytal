# Demo script (about 10 minutes)

All numbers come from the live models; they are listed here only so you know what to expect. Profiles are made-up examples.

## Before the demo (5 minutes)

```powershell
cd c:\vytal_ty
powershell -ExecutionPolicy Bypass -File scripts\start_production.ps1
```

Open http://127.0.0.1:8000. Check the header says **Models online**. Optional: in a second terminal run `.venv\Scripts\python.exe scripts\run_demo_profiles.py` (expect "4/4 profiles passed").

If production mode is not built yet: `powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1 -SkipBrowserTests` first.

## 1. Landing page (1 minute)

- Point out: the live figures (training respondents, ROC-AUC, survey average) are fetched from the server, not typed in.
- "What Vytal can and cannot tell you" and the disclaimer.

## 2. Questionnaire (3 minutes): profile "62-year-old male smoker"

| Step | Enter |
|---|---|
| About you | Age 62, Male |
| Height and weight | 175 cm, 92 kg → BMI preview **30** (derived, Obesity) |
| Lifestyle | Smoke every day; e-cigarettes No; physical activity No |
| Health history | Diabetes Yes; stroke No; kidney disease No; asthma Never |

Show along the way: press Continue with an empty field (error beside it); switch to ft/lb and back; press Back (answers kept); Edit from Review.

## 3. Results (3 minutes)

Expected: **Heart 29.8%** vs survey average 6.7%, High; **Lungs 32.5%** vs 6.4%, High.

- Read the estimate sentence: "about 30 in 100 respondents with answers like yours had reported this condition".
- Band scale and "In testing … 31.9% of people in the High band had reported …" (the band is validated).
- "What moved your estimate": diabetes and smoking raised heart; smoking dominates lungs. Say: associations, not causes.
- "Reading these numbers": estimate vs survey average vs band vs clinical risk.
- Suggestions with WHO links; urgent-symptoms notice first.
- Revise answers → change smoking to Never → see estimates drop.

## 4. Honest failure (1 minute)

- Start over → new assessment → tick "I don't know my height or weight" → results show **Not enough information** for both models, no number.

## 5. Methodology (1 minute)

- Live metrics per model; why accuracy is not used; limitations (no blood pressure/cholesterol; heavy drinking removed and why).

## 6. Engineering evidence (if asked)

| Question | Show |
|---|---|
| Tests? | `pytest` (124), `npm test` (25), `npm run test:e2e` (11), CI badge/run on GitHub |
| Evaluation? | `docs/model_evaluation/heart_model_evaluation_report.md`, model cards |
| Data provenance? | `datasets/DATA_SOURCES.md` |
| Decisions? | `docs/decisions/DECISION_LOG.md` |
| Security? | `/api/assessment/predict` with an extra field → 422; `backend/app/core/security.py` |
