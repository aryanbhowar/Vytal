import type { Band } from '../types/assessment'

export function formatPercent(fraction: number, digits = 1): string {
  return `${(fraction * 100).toFixed(digits)}%`
}

/** "about 30 in 100" style wording for estimates, which many people find clearer than percentages. */
export function inHundred(fraction: number): string {
  const count = fraction * 100
  if (count < 1) return 'fewer than 1 in 100'
  return `about ${Math.round(count)} in 100`
}

export function ordinal(value: number): string {
  const n = Math.round(value)
  const lastTwo = n % 100
  if (lastTwo >= 11 && lastTwo <= 13) return `${n}th`
  return `${n}${({ 1: 'st', 2: 'nd', 3: 'rd' } as Record<number, string>)[n % 10] ?? 'th'}`
}

export const BAND_LABELS: Record<Band, string> = {
  low: 'Low',
  moderate: 'Moderate',
  elevated: 'Elevated',
  high: 'High',
}

// Lower edges of each band, in percentile of survey respondents (D-010).
export const BAND_PERCENTILE_EDGES: Record<Band, number> = { low: 0, moderate: 50, elevated: 75, high: 90 }

const SHORT_FACTOR_LABELS: Record<string, string> = {
  age_group: 'Age',
  sex: 'Sex',
  bmi: 'BMI',
  smoking_status: 'Smoking',
  ecigarette_current_use: 'E-cigarettes',
  physical_activity_past_30_days: 'Physical activity',
  diabetes_status: 'Diabetes',
  stroke_history: 'Stroke',
  kidney_disease_history: 'Kidney disease',
  asthma_status: 'Asthma',
}

export function shortFactorLabel(feature: string): string {
  return SHORT_FACTOR_LABELS[feature] ?? feature
}

/** Plain-language position among survey respondents, avoiding "100th percentile" at the extremes. */
export function describePercentile(percentile: number): string {
  if (percentile >= 99) return 'higher than more than 99% of survey respondents'
  if (percentile < 1) return 'lower than more than 99% of survey respondents'
  return `higher than about ${Math.round(percentile)}% of survey respondents (${ordinal(percentile)} percentile)`
}
