# Phase 4 Report: Design System, Landing Page and Questionnaire

| | |
|---|---|
| **Project** | Vytal: personalized health-risk assessment web application |
| **Phase** | 4 of 7 (Day 4 in the plan; done on Day 2) |
| **Tasks** | Task 8 (design system and landing page), Task 9 (questionnaire with submission) |
| **Phase status** | **Complete** |
| **Report last updated** | 27 October 2026 |

---

## Summary in plain words

The placeholder "API connected" page is gone. Vytal now has a proper website:

- a **landing page** that explains what Vytal does and does not do, shows **live figures from the server** (how many survey answers each model learned from, its tested ranking accuracy, the US survey average), and leads into the assessment;
- a **five-step questionnaire** (About you → Height and weight → Lifestyle → Health history → Review) with clear questions, help text, error messages next to the right field, a live BMI preview, a switch between cm/kg and ft-in/lb, and an "I don't know my height or weight" option;
- answers that are **kept while you move between steps and even if you reload the page**, but only in that browser tab;
- a **submit step** that sends the answers to the real API, shows a loading message, and shows a clear error with a "Try again" button if anything fails;
- a consistent **dark navy and teal glass design** used everywhere.

Screenshots of every page at four screen widths were taken automatically in Microsoft Edge and checked.

## 1. Phase objective

Give people a trustworthy, accessible way to enter their information, built on one reusable design system, and connect it to the real API.

## 2. Work completed

### Task 8: Design system and landing page

- **Design tokens** (`src/styles/tokens.css`): every colour, space, corner radius, shadow, font size and animation time is defined once. Navy/charcoal backgrounds, teal and cyan accents, violet only as a minor extra. Band colours are teal, blue, amber and rose, deliberately not alarm red, because bands are relative positions, not diagnoses.
- **Readability:** computed contrast against the page background / a typical card: main text 17.2:1 / 15.5:1, secondary text 11.0:1 / 9.9:1, muted text 6.8:1 / 6.1:1, teal accent 10.6:1; dark text on the teal button 9.2:1 (the accessibility standard, WCAG AA, asks for at least 4.5:1). Glass cards are kept fairly solid so text stays readable, and blur is used only on a few cards and the header (laptop graphics chips struggle with lots of blur). Where a browser does not support blur, cards fall back to a solid colour.
- **Motion:** small fade-up entrance effects and hover feedback; all animation is turned off if the computer's "reduce motion" setting is on.
- **Accessibility:** a "Skip to content" link, visible focus rings, real labels on every input, radio buttons grouped with their question, error messages connected to their field, focus moved to the heading on each new step, and a live service status in the header.
- **Reusable components:** `GlassCard`, `Button`/`ButtonLink`, `DisclaimerBanner`, `LoadingState`, `ErrorState`, `WarningNotice`, navigation and footer.
- **Landing page:** headline, plain explanation, "Start the assessment" button, three-step "How Vytal works", one card per model with **real figures fetched from `/api/models/status`** (nothing invented), a "What Vytal can and cannot tell you" section and the disclaimer. The font (Inter) is bundled with the app, so nothing is loaded from the internet.

### Task 9: Questionnaire

| Step | Questions |
|---|---|
| About you | Age (18–120), sex |
| Height and weight | Units switch; height and weight; "I don't know" option; live BMI preview marked "derived" |
| Lifestyle | Smoking (4 options), e-cigarettes now, any exercise in the past 30 days |
| Health history | Diabetes (4 options), stroke, kidney disease, asthma (now / in the past / never) |
| Review | Every answer, with "Edit" buttons that jump back to the right step |

- **Validation** (`utils/formValidation.ts`) uses the same limits as the backend: age 18–120, height 100–250 cm, weight 25–350 kg, BMI 12–70. Messages say what to do ("Enter your age as a whole number."). The backend repeats every check, so the browser checks are for convenience, not security.
- **Imperial units** are converted exactly (1 in = 2.54 cm, 1 lb = 0.45359237 kg) before sending.
- **State** (`context/AssessmentContext.tsx`) is kept in `sessionStorage`: it survives a reload but disappears when the tab is closed or "Start over" is pressed. Nothing is stored on the server.
- **Submission** goes through `services/apiClient.ts`, the only file that talks to the server. Network failure, validation errors (with the field list), rate limiting and server errors each get a clear message.
- If the review step finds a missing answer (for example after editing), the user is sent back to the first step that needs attention.

## 3. Important files

| File | What it does |
|---|---|
| `frontend/src/styles/tokens.css`, `global.css`, `glass.css`, `layout.css` | The design system |
| `frontend/src/components/common/*`, `layout/*`, `form/*` | Reusable building blocks |
| `frontend/src/pages/LandingPage.tsx` | Landing page with live model figures |
| `frontend/src/pages/assessment/AssessmentPage.tsx`, `AssessmentSteps.tsx` | The questionnaire |
| `frontend/src/config/assessmentQuestions.ts` | Question wording and options |
| `frontend/src/context/AssessmentContext.tsx` | Shared state in `sessionStorage` |
| `frontend/src/utils/formValidation.ts`, `unitConversion.ts`, `bmiCalculation.ts`, `formatting.ts` | Validation, conversion, BMI, wording |
| `frontend/src/services/apiClient.ts`, `assessmentService.ts` | Talking to the backend |
| `frontend/src/types/assessment.ts` | TypeScript copy of the API's request and response shapes |
| `frontend/src/hooks/useServiceStatus.ts` | Live "Models online" indicator |
| `frontend/vite.config.ts` | Dev proxy, chart code split into its own file, test settings |

## 4. Technical decisions and reasons

| Decision | Reason |
|---|---|
| `sessionStorage`, not `localStorage` or a server database | Answers survive a reload but are gone when the tab closes; nothing to secure on a server (D-036) |
| Validate in the browser and again on the server | Fast feedback for users; the server remains the real gatekeeper |
| Self-hosted Inter font | Works offline and sends no request to a font service (privacy) |
| Charts split into a separate file | The landing page loads less code |
| No yes/no result anywhere | Bands and estimates only, matching the evaluation's honesty rules |

## 5. Commands executed

```powershell
cd frontend
npm install react-router-dom lucide-react recharts @fontsource-variable/inter
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @playwright/test
npm run build; npm run lint; npm test
npx playwright test
```

## 6. Actual tests and outcomes

| Test | Result |
|---|---|
| `npm run build` (type-check + build) | Pass |
| `npm run lint` | Pass, no warnings (two warnings found during the work were fixed) |
| Vitest: validation, unit conversion, BMI, option values equal backend values, percentile wording | Pass |
| Vitest: landing page disclaimer and start link; missing answers shown beside the field; answers kept when going back; BMI preview; exact JSON sent to the API; unreachable server → retryable error; 422 → field messages | Pass |
| Playwright (Edge): keyboard-only first step; no sideways scrolling at 1440, 1024, 768 and 375 px on every page; screenshots reviewed | Pass |
| **Totals at end of Phase 5** | Vitest **25 passed**; Playwright **11 passed**; pytest **118 passed** |

## 7. Current errors and limitations

| Item | Note |
|---|---|
| Browser support checked in Edge only | Chrome uses the same engine; Firefox and Safari not tested |
| No automated colour-contrast scanner | Contrast was computed for the token colours with the WCAG formula, not scanned page by page |
| Only English | Not required by the brief |

## 8. Dataset and model status

Unchanged.

## 9. Git commit and push status

Committed with Phase 5 (see `PROJECT_STATUS.md`).

## 10. Exact next steps

Phase 5 (done in the same session): results dashboard and methodology page.

## 11. Decisions requiring your approval

None.
