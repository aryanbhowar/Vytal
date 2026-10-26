// Frontend validation gives fast, friendly feedback. The backend repeats every
// check, so these rules are a convenience, not the security boundary.

import { ASSESSMENT_STEPS, type ChoiceField, type StepId } from '../config/assessmentQuestions'
import type { AssessmentRequest } from '../types/assessment'
import { calculateBmi, isBmiInModelRange, MODEL_BMI_RANGE } from './bmiCalculation'
import { feetInchesToCm, parseNumber, poundsToKg } from './unitConversion'

// Must match the backend request schema limits.
export const LIMITS = {
  age: { min: 18, max: 120 },
  heightCm: { min: 100, max: 250 },
  weightKg: { min: 25, max: 350 },
} as const

export type UnitSystem = 'metric' | 'imperial'

export interface AssessmentFormValues {
  ageYears: string
  unitSystem: UnitSystem
  heightCm: string
  weightKg: string
  heightFeet: string
  heightInches: string
  weightPounds: string
  measurementsUnknown: boolean
  answers: Record<ChoiceField, string | null>
}

export type FormErrors = Partial<Record<string, string>>

export const EMPTY_FORM: AssessmentFormValues = {
  ageYears: '',
  unitSystem: 'metric',
  heightCm: '',
  weightKg: '',
  heightFeet: '',
  heightInches: '',
  weightPounds: '',
  measurementsUnknown: false,
  answers: {
    sex: null,
    smoking_status: null,
    ecigarette_current_use: null,
    physical_activity_past_30_days: null,
    diabetes_status: null,
    stroke_history: null,
    kidney_disease_history: null,
    asthma_status: null,
  },
}

const STEP_CHOICE_FIELDS: Record<StepId, ChoiceField[]> = {
  about: ['sex'],
  body: [],
  lifestyle: ['smoking_status', 'ecigarette_current_use', 'physical_activity_past_30_days'],
  history: ['diabetes_status', 'stroke_history', 'kidney_disease_history', 'asthma_status'],
  review: [],
}

/** Height and weight in metric units, or null where not entered. */
export function measurementsInMetric(values: AssessmentFormValues): { heightCm: number | null; weightKg: number | null } {
  if (values.measurementsUnknown) return { heightCm: null, weightKg: null }
  if (values.unitSystem === 'metric') {
    return { heightCm: parseNumber(values.heightCm), weightKg: parseNumber(values.weightKg) }
  }
  const feet = parseNumber(values.heightFeet)
  const inches = parseNumber(values.heightInches) ?? 0
  const pounds = parseNumber(values.weightPounds)
  return {
    heightCm: feet === null ? null : feetInchesToCm(feet, inches),
    weightKg: pounds === null ? null : poundsToKg(pounds),
  }
}

function validateAge(values: AssessmentFormValues, errors: FormErrors): void {
  const age = parseNumber(values.ageYears)
  if (age === null) errors.ageYears = 'Enter your age in years.'
  else if (!Number.isInteger(age)) errors.ageYears = 'Enter your age as a whole number.'
  else if (age < LIMITS.age.min) errors.ageYears = 'Vytal is for adults aged 18 and over.'
  else if (age > LIMITS.age.max) errors.ageYears = `Enter an age of ${LIMITS.age.max} or less.`
}

function validateMeasurements(values: AssessmentFormValues, errors: FormErrors): void {
  if (values.measurementsUnknown) return
  const heightKey = values.unitSystem === 'metric' ? 'heightCm' : 'heightFeet'
  const weightKey = values.unitSystem === 'metric' ? 'weightKg' : 'weightPounds'
  const { heightCm, weightKg } = measurementsInMetric(values)

  if (values.unitSystem === 'imperial') {
    const inches = parseNumber(values.heightInches)
    if (values.heightInches.trim() !== '' && (inches === null || inches < 0 || inches >= 12)) {
      errors.heightInches = 'Inches must be between 0 and 11.'
    }
  }
  if (heightCm === null) errors[heightKey] = 'Enter your height, or tick "I don\'t know my height or weight".'
  else if (heightCm < LIMITS.heightCm.min || heightCm > LIMITS.heightCm.max)
    errors[heightKey] = 'Height must be between 100 and 250 cm (3 ft 4 in and 8 ft 2 in).'

  if (weightKg === null) errors[weightKey] = 'Enter your weight, or tick "I don\'t know my height or weight".'
  else if (weightKg < LIMITS.weightKg.min || weightKg > LIMITS.weightKg.max)
    errors[weightKey] = 'Weight must be between 25 and 350 kg (55 and 771 lb).'

  if (heightCm !== null && weightKg !== null && !errors[heightKey] && !errors[weightKey]) {
    const bmi = calculateBmi(heightCm, weightKg)
    if (!isBmiInModelRange(bmi)) {
      errors[weightKey] =
        `These give a BMI of ${bmi}, outside ${MODEL_BMI_RANGE.min}–${MODEL_BMI_RANGE.max}. Please check both values and units.`
    }
  }
}

export function validateStep(step: StepId, values: AssessmentFormValues): FormErrors {
  const errors: FormErrors = {}
  if (step === 'about') validateAge(values, errors)
  if (step === 'body') validateMeasurements(values, errors)
  for (const field of STEP_CHOICE_FIELDS[step]) {
    if (values.answers[field] === null) errors[field] = 'Please choose an answer.'
  }
  return errors
}

export function validateAll(values: AssessmentFormValues): FormErrors {
  return ASSESSMENT_STEPS.reduce<FormErrors>((all, step) => ({ ...all, ...validateStep(step.id, values) }), {})
}

/** First step that has an error, so the review page can send the user back to it. */
export function firstStepWithErrors(values: AssessmentFormValues): StepId | null {
  return ASSESSMENT_STEPS.find((step) => Object.keys(validateStep(step.id, values)).length > 0)?.id ?? null
}

export function toAssessmentRequest(values: AssessmentFormValues): AssessmentRequest {
  const { heightCm, weightKg } = measurementsInMetric(values)
  const round1 = (n: number | null) => (n === null ? null : Math.round(n * 10) / 10)
  const a = values.answers
  return {
    age_years: Number(values.ageYears),
    sex: a.sex as AssessmentRequest['sex'],
    height_cm: round1(heightCm),
    weight_kg: round1(weightKg),
    smoking_status: a.smoking_status as AssessmentRequest['smoking_status'],
    ecigarette_current_use: a.ecigarette_current_use as AssessmentRequest['ecigarette_current_use'],
    physical_activity_past_30_days: a.physical_activity_past_30_days as AssessmentRequest['physical_activity_past_30_days'],
    diabetes_status: a.diabetes_status as AssessmentRequest['diabetes_status'],
    stroke_history: a.stroke_history as AssessmentRequest['stroke_history'],
    kidney_disease_history: a.kidney_disease_history as AssessmentRequest['kidney_disease_history'],
    asthma_status: a.asthma_status as AssessmentRequest['asthma_status'],
  }
}
