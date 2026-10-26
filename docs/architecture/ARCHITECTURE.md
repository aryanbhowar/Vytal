# Vytal architecture

## System overview

```mermaid
flowchart LR
  subgraph Browser["Browser (React + TypeScript)"]
    L[Landing] --> Q[Questionnaire<br/>5 steps, sessionStorage]
    Q -->|POST /api/assessment/predict| API
    API -->|JSON result| R[Results dashboard]
    M[Methodology] -->|GET /api/models/status| API
  end
  subgraph Server["Server (FastAPI, one process)"]
    API[Security middleware<br/>size limit, rate limit, headers] --> V[Pydantic validation]
    V --> P[Input preprocessing<br/>age group, BMI]
    P --> REG[Model registry<br/>hash-checked at startup]
    REG --> H[Heart model]
    REG --> C[COPD model]
    H & C --> I[Interpretation<br/>estimate, percentile, band, factors]
    I --> S[Suggestion rules<br/>WHO sources]
  end
  subgraph Offline["Offline ML pipeline (run by hand)"]
    RAW[BRFSS 2022–2024] --> CHK[Verify vs CDC codebooks] --> PRE[Recode, exclude, split] --> TR[Train, calibrate, evaluate] --> ART[models/*.joblib + metadata]
  end
  ART -.loaded at startup.-> REG
  SCHEMA[(Feature schema JSON)] -.-> PRE
  SCHEMA -.-> V
  SCHEMA -.-> REG
```

## Request sequence

```mermaid
sequenceDiagram
  participant U as User
  participant F as Frontend
  participant B as Backend
  participant ML as Models (in memory)
  U->>F: Answers 11 questions
  F->>F: Validate (same limits as backend)
  F->>B: POST /api/assessment/predict (JSON)
  B->>B: Size + rate limit, schema validation
  B->>B: Age → age group, height/weight → BMI
  alt height or weight missing
    B-->>F: status "insufficient_input" (no estimate)
  else model unavailable
    B-->>F: status "unavailable" (no estimate)
  else
    B->>ML: feature row (canonical values)
    ML-->>B: probability, contributions
    B->>B: percentile, band, factors, suggestions
    B-->>F: results + disclaimer (Cache-Control: no-store)
  end
  F->>U: Results dashboard
```

## Key design points

| Point | How |
|---|---|
| One definition of inputs | `ml/feature_definitions/vytal_feature_schema.json` is used by preprocessing, training, the API schema tests and model loading |
| Served numbers equal evaluated numbers | The backend imports `ml/inference/risk_model.py`, the same code used to evaluate the models |
| Honest failure | Missing BMI, missing or tampered model → explicit status, never a number |
| Privacy | No identifiers collected; nothing stored or logged server-side; browser keeps answers in `sessionStorage` only |
| Production | One process serves website and API (`scripts/start_production.ps1`) |

## Folders

See the root `README.md` and each folder's `README.md` (`backend/`, `frontend/`, `ml/`, `models/`, `datasets/`, `tests/`).
