// TypeScript mirror of backend/app/schemas/assessment_schemas.py.
// Answer values are the canonical values from ml/feature_definitions/vytal_feature_schema.json.

export type Sex = 'male' | 'female'
export type SmokingStatus = 'current_daily' | 'current_some_days' | 'former' | 'never'
export type YesNo = 'yes' | 'no'
export type DiabetesStatus = 'yes' | 'gestational_only' | 'no' | 'prediabetes'
export type AsthmaStatus = 'current' | 'former' | 'never'
export type ModelId = 'heart' | 'respiratory'
export type ResultStatus = 'ok' | 'unavailable' | 'insufficient_input'
export type Band = 'low' | 'moderate' | 'elevated' | 'high'

export interface AssessmentRequest {
  age_years: number
  sex: Sex
  height_cm: number | null
  weight_kg: number | null
  smoking_status: SmokingStatus
  ecigarette_current_use: YesNo
  physical_activity_past_30_days: YesNo
  diabetes_status: DiabetesStatus
  stroke_history: YesNo
  kidney_disease_history: YesNo
  asthma_status: AsthmaStatus
}

export interface BmiSummary {
  value: number
  who_category: string
  source: string
}

export interface ProfileAnswer {
  field: string
  question: string
  value: string
  label: string
}

export interface ProfileSummary {
  age_years: number
  age_group: string
  height_cm: number | null
  weight_kg: number | null
  bmi: BmiSummary | null
  answers: ProfileAnswer[]
}

export interface ContributingFactor {
  feature: string
  label: string
  answer: string
  direction: 'raised' | 'lowered'
  log_odds_contribution: number
  modifiable: boolean
}

export interface BandValidation {
  observed_rate: number
  share_of_respondents: number
}

export interface ModelResult {
  model_id: ModelId
  title: string
  outcome_description: string
  status: ResultStatus
  message: string | null
  estimated_probability: number | null
  survey_prevalence: number | null
  percentile: number | null
  category: Band | null
  category_explanation: string | null
  band_validation: BandValidation | null
  contributing_factors: ContributingFactor[]
  explanation_note: string | null
  limitations: string[]
  model_version: string | null
}

export interface Suggestion {
  id: string
  theme: string
  title: string
  body: string
  triggered_by: string[]
  priority: 'urgent' | 'high' | 'normal'
  source_name: string
  source_url: string
}

export interface AssessmentResponse {
  profile_summary: ProfileSummary
  results: ModelResult[]
  suggestions: Suggestion[]
  disclaimer: string
  data_attribution: string
}

export interface ModelEvaluationSummary {
  test_rows: number
  roc_auc: number
  pr_auc: number
  brier_score: number
  expected_calibration_error: number
  sensitivity: number
  specificity: number
  precision: number
  reporting_threshold: number
}

export interface ModelStatus {
  model_id: ModelId
  title: string
  available: boolean
  unavailable_reason: string | null
  model_version: string | null
  outcome_description: string | null
  training_years: number[]
  training_rows: number | null
  features: string[]
  survey_prevalence: number | null
  calibration_method: string | null
  evaluation: ModelEvaluationSummary | null
}

export interface ModelsStatusResponse {
  models: ModelStatus[]
}

export interface ReadinessResponse {
  ready: boolean
  models: Record<ModelId, boolean>
}
