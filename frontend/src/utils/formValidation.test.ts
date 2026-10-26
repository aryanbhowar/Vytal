import { describe, expect, it } from 'vitest'
import { ALL_CHOICE_QUESTIONS } from '../config/assessmentQuestions'
import { calculateBmi, whoBmiCategory } from './bmiCalculation'
import { EMPTY_FORM, toAssessmentRequest, validateAll, validateStep, type AssessmentFormValues } from './formValidation'
import { cmToFeetInches, feetInchesToCm, parseNumber, poundsToKg } from './unitConversion'

const COMPLETE: AssessmentFormValues = {
  ...EMPTY_FORM,
  ageYears: '45',
  heightCm: '170',
  weightKg: '70',
  answers: {
    sex: 'female',
    smoking_status: 'never',
    ecigarette_current_use: 'no',
    physical_activity_past_30_days: 'yes',
    diabetes_status: 'no',
    stroke_history: 'no',
    kidney_disease_history: 'no',
    asthma_status: 'never',
  },
}

describe('unit conversion', () => {
  it('converts feet, inches and pounds exactly', () => {
    expect(feetInchesToCm(5, 10)).toBeCloseTo(177.8, 5)
    expect(poundsToKg(150)).toBeCloseTo(68.0389, 3)
    expect(cmToFeetInches(182.88)).toEqual({ feet: 6, inches: 0 })
  })

  it('parses numbers and rejects text', () => {
    expect(parseNumber(' 72,5 ')).toBe(72.5)
    expect(parseNumber('')).toBeNull()
    expect(parseNumber('abc')).toBeNull()
  })
})

describe('BMI', () => {
  it('matches the backend formula and WHO categories', () => {
    expect(calculateBmi(180, 81)).toBe(25)
    expect(whoBmiCategory(18.4)).toBe('Underweight')
    expect(whoBmiCategory(24.9)).toBe('Healthy weight')
    expect(whoBmiCategory(29.9)).toBe('Overweight')
    expect(whoBmiCategory(30)).toBe('Obesity')
  })
})

describe('validation', () => {
  it('accepts a complete form', () => {
    expect(validateAll(COMPLETE)).toEqual({})
  })

  it.each([
    ['', 'Enter your age in years.'],
    ['17', 'Vytal is for adults aged 18 and over.'],
    ['121', 'Enter an age of 120 or less.'],
    ['40.5', 'Enter your age as a whole number.'],
  ])('rejects age %s', (age, message) => {
    expect(validateStep('about', { ...COMPLETE, ageYears: age }).ageYears).toBe(message)
  })

  it('requires every choice question', () => {
    const errors = validateAll({ ...COMPLETE, answers: { ...COMPLETE.answers, smoking_status: null, asthma_status: null } })
    expect(errors.smoking_status).toBe('Please choose an answer.')
    expect(errors.asthma_status).toBe('Please choose an answer.')
  })

  it('checks height and weight ranges and implausible BMI', () => {
    expect(validateStep('body', { ...COMPLETE, heightCm: '90' }).heightCm).toMatch(/between 100 and 250/)
    expect(validateStep('body', { ...COMPLETE, weightKg: '400' }).weightKg).toMatch(/between 25 and 350/)
    expect(validateStep('body', { ...COMPLETE, heightCm: '100', weightKg: '300' }).weightKg).toMatch(/BMI of 300/)
  })

  it('allows unknown measurements and sends null instead of a guess', () => {
    const values = { ...COMPLETE, heightCm: '', weightKg: '', measurementsUnknown: true }
    expect(validateStep('body', values)).toEqual({})
    const request = toAssessmentRequest(values)
    expect(request.height_cm).toBeNull()
    expect(request.weight_kg).toBeNull()
  })

  it('converts imperial input to metric for the API', () => {
    const request = toAssessmentRequest({ ...COMPLETE, unitSystem: 'imperial', heightFeet: '5', heightInches: '7', weightPounds: '154' })
    expect(request.height_cm).toBe(170.2)
    expect(request.weight_kg).toBe(69.9)
  })

  it('rejects inches of 12 or more', () => {
    const errors = validateStep('body', { ...COMPLETE, unitSystem: 'imperial', heightFeet: '5', heightInches: '12', weightPounds: '150' })
    expect(errors.heightInches).toBe('Inches must be between 0 and 11.')
  })
})

describe('question options', () => {
  it('use exactly the canonical answer values accepted by the backend', () => {
    // From ml/feature_definitions/vytal_feature_schema.json
    const canonical: Record<string, string[]> = {
      sex: ['male', 'female'],
      smoking_status: ['current_daily', 'current_some_days', 'former', 'never'],
      ecigarette_current_use: ['no', 'yes'],
      physical_activity_past_30_days: ['yes', 'no'],
      diabetes_status: ['yes', 'gestational_only', 'no', 'prediabetes'],
      stroke_history: ['yes', 'no'],
      kidney_disease_history: ['yes', 'no'],
      asthma_status: ['current', 'former', 'never'],
    }
    for (const question of ALL_CHOICE_QUESTIONS) {
      expect(question.options.map((o) => o.value).sort()).toEqual([...canonical[question.field]].sort())
    }
  })
})

describe('percentile wording', () => {
  it('never claims the 100th percentile', async () => {
    const { describePercentile } = await import('./formatting')
    expect(describePercentile(99.7)).toBe('higher than more than 99% of survey respondents')
    expect(describePercentile(0.4)).toBe('lower than more than 99% of survey respondents')
    expect(describePercentile(52.3)).toBe('higher than about 52% of survey respondents (52nd percentile)')
  })
})
