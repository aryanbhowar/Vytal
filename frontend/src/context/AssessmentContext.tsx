// Holds the questionnaire answers, current step and latest result for the whole app.
//
// Privacy: state is kept in sessionStorage, which belongs to this browser tab only
// and is cleared when the tab closes. Nothing is sent anywhere except the single
// assessment request, and "Start over" wipes it immediately.

import { createContext, useContext, useEffect, useMemo, useReducer, type ReactNode } from 'react'
import type { ChoiceField } from '../config/assessmentQuestions'
import type { AssessmentResponse } from '../types/assessment'
import { EMPTY_FORM, type AssessmentFormValues, type UnitSystem } from '../utils/formValidation'

export const STORAGE_KEY = 'vytal.assessment.v1'

type TextField = 'ageYears' | 'heightCm' | 'weightKg' | 'heightFeet' | 'heightInches' | 'weightPounds'

export interface AssessmentState {
  values: AssessmentFormValues
  stepIndex: number
  result: AssessmentResponse | null
}

type Action =
  | { type: 'setText'; field: TextField; value: string }
  | { type: 'setAnswer'; field: ChoiceField; value: string }
  | { type: 'setUnitSystem'; value: UnitSystem }
  | { type: 'setMeasurementsUnknown'; value: boolean }
  | { type: 'goToStep'; index: number }
  | { type: 'setResult'; result: AssessmentResponse }
  | { type: 'reset' }

const INITIAL_STATE: AssessmentState = { values: EMPTY_FORM, stepIndex: 0, result: null }

function reducer(state: AssessmentState, action: Action): AssessmentState {
  switch (action.type) {
    case 'setText':
      return { ...state, values: { ...state.values, [action.field]: action.value } }
    case 'setAnswer':
      return { ...state, values: { ...state.values, answers: { ...state.values.answers, [action.field]: action.value } } }
    case 'setUnitSystem':
      return { ...state, values: { ...state.values, unitSystem: action.value } }
    case 'setMeasurementsUnknown':
      return { ...state, values: { ...state.values, measurementsUnknown: action.value } }
    case 'goToStep':
      return { ...state, stepIndex: action.index }
    case 'setResult':
      return { ...state, result: action.result }
    case 'reset':
      return INITIAL_STATE
  }
}

function loadState(): AssessmentState {
  try {
    const stored = window.sessionStorage.getItem(STORAGE_KEY)
    if (!stored) return INITIAL_STATE
    const parsed = JSON.parse(stored) as AssessmentState
    return {
      ...INITIAL_STATE,
      ...parsed,
      values: { ...EMPTY_FORM, ...parsed.values, answers: { ...EMPTY_FORM.answers, ...parsed.values?.answers } },
    }
  } catch {
    return INITIAL_STATE
  }
}

interface AssessmentContextValue {
  state: AssessmentState
  setText: (field: TextField, value: string) => void
  setAnswer: (field: ChoiceField, value: string) => void
  setUnitSystem: (value: UnitSystem) => void
  setMeasurementsUnknown: (value: boolean) => void
  goToStep: (index: number) => void
  setResult: (result: AssessmentResponse) => void
  reset: () => void
}

const AssessmentContext = createContext<AssessmentContextValue | null>(null)

export function AssessmentProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, undefined, loadState)

  useEffect(() => {
    try {
      if (state === INITIAL_STATE) window.sessionStorage.removeItem(STORAGE_KEY)
      else window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch {
      // Storage can be unavailable (private mode, full); the app still works without it.
    }
  }, [state])

  const value = useMemo<AssessmentContextValue>(
    () => ({
      state,
      setText: (field, text) => dispatch({ type: 'setText', field, value: text }),
      setAnswer: (field, answer) => dispatch({ type: 'setAnswer', field, value: answer }),
      setUnitSystem: (system) => dispatch({ type: 'setUnitSystem', value: system }),
      setMeasurementsUnknown: (unknown) => dispatch({ type: 'setMeasurementsUnknown', value: unknown }),
      goToStep: (index) => dispatch({ type: 'goToStep', index }),
      setResult: (result) => dispatch({ type: 'setResult', result }),
      reset: () => dispatch({ type: 'reset' }),
    }),
    [state],
  )
  return <AssessmentContext.Provider value={value}>{children}</AssessmentContext.Provider>
}

// The hook lives next to its provider on purpose (one file per piece of state).
// eslint-disable-next-line react/only-export-components
export function useAssessment(): AssessmentContextValue {
  const context = useContext(AssessmentContext)
  if (!context) throw new Error('useAssessment must be used inside AssessmentProvider')
  return context
}
