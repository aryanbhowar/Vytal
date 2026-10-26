// Questionnaire wording and options. Option values must equal the backend's
// canonical values (a backend test checks the API against the feature schema;
// a frontend test checks these options against the same values).

import type { AsthmaStatus, DiabetesStatus, Sex, SmokingStatus, YesNo } from '../types/assessment'

export interface ChoiceOption<T extends string> {
  value: T
  label: string
  hint?: string
}

export interface ChoiceQuestion<T extends string> {
  field: ChoiceField
  question: string
  help?: string
  options: ChoiceOption<T>[]
}

export type ChoiceField =
  | 'sex'
  | 'smoking_status'
  | 'ecigarette_current_use'
  | 'physical_activity_past_30_days'
  | 'diabetes_status'
  | 'stroke_history'
  | 'kidney_disease_history'
  | 'asthma_status'

const YES_NO: ChoiceOption<YesNo>[] = [
  { value: 'yes', label: 'Yes' },
  { value: 'no', label: 'No' },
]

export const SEX_QUESTION: ChoiceQuestion<Sex> = {
  field: 'sex',
  question: 'Sex',
  help: 'The survey the models learned from recorded sex as male or female.',
  options: [
    { value: 'female', label: 'Female' },
    { value: 'male', label: 'Male' },
  ],
}

export const LIFESTYLE_QUESTIONS = [
  {
    field: 'smoking_status',
    question: 'Do you smoke cigarettes?',
    help: '"Never" means fewer than 100 cigarettes in your whole life.',
    options: [
      { value: 'current_daily', label: 'Every day' },
      { value: 'current_some_days', label: 'Some days' },
      { value: 'former', label: 'I used to, but not now' },
      { value: 'never', label: 'Never' },
    ],
  } satisfies ChoiceQuestion<SmokingStatus>,
  {
    field: 'ecigarette_current_use',
    question: 'Do you currently use e-cigarettes or vapes?',
    help: 'Every day or some days counts as yes.',
    options: YES_NO,
  } satisfies ChoiceQuestion<YesNo>,
  {
    field: 'physical_activity_past_30_days',
    question: 'In the past 30 days, did you do any physical activity or exercise outside your regular job?',
    help: 'For example running, walking for exercise, gardening, cycling or sport.',
    options: YES_NO,
  } satisfies ChoiceQuestion<YesNo>,
] as const

export const HEALTH_HISTORY_QUESTIONS = [
  {
    field: 'diabetes_status',
    question: 'Has a doctor or other health professional ever told you that you have diabetes?',
    options: [
      { value: 'yes', label: 'Yes' },
      { value: 'gestational_only', label: 'Only during pregnancy' },
      { value: 'prediabetes', label: 'Prediabetes or borderline' },
      { value: 'no', label: 'No' },
    ],
  } satisfies ChoiceQuestion<DiabetesStatus>,
  {
    field: 'stroke_history',
    question: 'Have you ever been told you had a stroke?',
    options: YES_NO,
  } satisfies ChoiceQuestion<YesNo>,
  {
    field: 'kidney_disease_history',
    question: 'Have you ever been told you have kidney disease?',
    help: 'Not including kidney stones, bladder infection or incontinence.',
    options: YES_NO,
  } satisfies ChoiceQuestion<YesNo>,
  {
    field: 'asthma_status',
    question: 'Asthma',
    options: [
      { value: 'current', label: 'I have asthma now' },
      { value: 'former', label: 'I had asthma in the past, not now' },
      { value: 'never', label: 'I have never been told I have asthma' },
    ],
  } satisfies ChoiceQuestion<AsthmaStatus>,
] as const

export const ALL_CHOICE_QUESTIONS: readonly ChoiceQuestion<string>[] = [
  SEX_QUESTION,
  ...LIFESTYLE_QUESTIONS,
  ...HEALTH_HISTORY_QUESTIONS,
]

export const ASSESSMENT_STEPS = [
  { id: 'about', title: 'About you' },
  { id: 'body', title: 'Height and weight' },
  { id: 'lifestyle', title: 'Lifestyle' },
  { id: 'history', title: 'Health history' },
  { id: 'review', title: 'Review' },
] as const

export type StepId = (typeof ASSESSMENT_STEPS)[number]['id']

export function optionLabel(field: ChoiceField, value: string | null): string {
  const question = ALL_CHOICE_QUESTIONS.find((q) => q.field === field)
  return question?.options.find((o) => o.value === value)?.label ?? 'Not answered'
}
