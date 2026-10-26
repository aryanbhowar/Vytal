// TEST FIXTURES ONLY. These are hand-written example API responses used to test
// how the UI renders. They are NOT model output and are never shown to users.

import type { AssessmentResponse, ModelResult } from '../types/assessment'

export const TEST_FIXTURE_HEART_OK: ModelResult = {
  model_id: 'heart',
  title: 'Heart: coronary heart disease or heart attack',
  outcome_description: 'TEST FIXTURE outcome description (heart).',
  status: 'ok',
  message: null,
  estimated_probability: 0.25,
  survey_prevalence: 0.07,
  percentile: 91,
  category: 'high',
  category_explanation: 'Among the top tenth of survey respondents.',
  band_validation: { observed_rate: 0.3, share_of_respondents: 0.1 },
  contributing_factors: [
    { feature: 'smoking_status', label: 'Cigarette smoking', answer: 'Smoke every day', direction: 'raised', log_odds_contribution: 0.5, modifiable: true },
    { feature: 'physical_activity_past_30_days', label: 'Activity', answer: 'Yes', direction: 'lowered', log_odds_contribution: -0.1, modifiable: true },
  ],
  explanation_note: 'TEST FIXTURE note.',
  limitations: ['TEST FIXTURE limitation.'],
  model_version: '0.0.0-test',
}

export const TEST_FIXTURE_RESPIRATORY_UNAVAILABLE: ModelResult = {
  model_id: 'respiratory',
  title: 'Lungs: COPD, emphysema or chronic bronchitis',
  outcome_description: '',
  status: 'unavailable',
  message: 'This estimate is not available right now. TEST FIXTURE reason.',
  estimated_probability: null,
  survey_prevalence: null,
  percentile: null,
  category: null,
  category_explanation: null,
  band_validation: null,
  contributing_factors: [],
  explanation_note: null,
  limitations: [],
  model_version: null,
}

export const TEST_FIXTURE_RESPONSE: AssessmentResponse = {
  profile_summary: {
    age_years: 60,
    age_group: '60-64',
    height_cm: 175,
    weight_kg: 90,
    bmi: { value: 29.4, who_category: 'Overweight', source: 'derived from height and weight' },
    answers: [{ field: 'smoking_status', question: 'Cigarette smoking', value: 'current_daily', label: 'Smoke every day' }],
  },
  results: [TEST_FIXTURE_HEART_OK, TEST_FIXTURE_RESPIRATORY_UNAVAILABLE],
  suggestions: [
    { id: 'urgent_symptoms', theme: 'Safety', title: 'TEST FIXTURE urgent notice', body: 'Urgent body.', triggered_by: [], priority: 'urgent', source_name: 'WHO', source_url: 'https://www.who.int/' },
    { id: 'tobacco_cessation', theme: 'Tobacco', title: 'TEST FIXTURE stop smoking', body: 'Body.', triggered_by: ['smoking_status'], priority: 'high', source_name: 'WHO', source_url: 'https://www.who.int/' },
  ],
  disclaimer: 'TEST FIXTURE disclaimer.',
  data_attribution: 'TEST FIXTURE attribution.',
}
