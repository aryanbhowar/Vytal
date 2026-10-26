# Phase reports: how they are written

There is one report per phase (`PHASE_1_REPORT.md` to `PHASE_7_REPORT.md`). Each report is updated as its tasks finish, so it always describes the real state of that phase.

## Who the reports are for

- **You (the student)**, to understand and explain each step in the viva.
- **An external reviewer** (for example ChatGPT, a supervisor or an examiner) who has not seen the work happen and may not be able to open the repository.
- **The next work session**, so it can continue without reconstructing anything.

## Writing style

- Plain, beginner-level language. Every technical term is explained the first time it appears.
- Detailed: say what was done, why, how it was checked, and what it means.
- Honest: only real, observed results. Anything not checked is marked as not checked.
- Tables for lists of files, decisions, tests and results; short paragraphs for explanations.

## Required structure

Each report starts with a header table (phase, tasks, status, date) and a **Summary in plain words**, then has these ten sections:

1. **Phase objective**: what the phase is for and why it comes at this point.
2. **Work completed**: step by step, per task.
3. **Important files created or modified**: what each file does.
4. **Technical decisions and reasons**: in simple terms, with decision-log IDs.
5. **Commands executed**: in order, with comments saying what each does.
6. **Actual tests and outcomes**: what was tested, how, the real result, and what a pass means.
7. **Current errors and limitations**: the effect of each and the plan for it.
8. **Dataset and model status**.
9. **Git commit and push status**.
10. **Exact next steps**, including anything the user will need to do.

Phases that involve data or models also explain the numbers (row counts, metrics) in plain language: what each number means and whether it is good or modest.

## Phase-to-task mapping

| Phase | Day | Tasks |
|---|---|---|
| 1 | 1 | 1 Foundation, 2 BRFSS download and variable checks |
| 2 | 2 | 3 Preprocessing, 4 Heart model, 5 Respiratory model |
| 3 | 3 | 6 Prediction API, 7 Suggestion rules |
| 4 | 4 | 8 Design system and landing page, 9 Questionnaire |
| 5 | 5 | 10 Results dashboard, 11 Methodology page and end-to-end check |
| 6 | 6 | 12 Stability and demo preparation |
| 7 | 7 | 13 Documentation and handover |
