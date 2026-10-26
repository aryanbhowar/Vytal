// The content of each questionnaire step. State lives in AssessmentContext.

import { Pencil } from 'lucide-react'
import { NumberField } from '../../components/form/NumberField'
import { RadioCardGroup } from '../../components/form/RadioCardGroup'
import {
  ASSESSMENT_STEPS,
  HEALTH_HISTORY_QUESTIONS,
  LIFESTYLE_QUESTIONS,
  SEX_QUESTION,
  optionLabel,
  type ChoiceField,
  type ChoiceQuestion,
} from '../../config/assessmentQuestions'
import { useAssessment } from '../../context/AssessmentContext'
import { calculateBmi, isBmiInModelRange, whoBmiCategory } from '../../utils/bmiCalculation'
import { measurementsInMetric, type FormErrors } from '../../utils/formValidation'

interface StepProps {
  errors: FormErrors
}

function ChoiceQuestions({ questions, errors }: { questions: readonly ChoiceQuestion<string>[]; errors: FormErrors }) {
  const { state, setAnswer } = useAssessment()
  return (
    <>
      {questions.map((q) => (
        <RadioCardGroup
          key={q.field}
          name={q.field}
          legend={q.question}
          help={q.help}
          options={q.options}
          value={state.values.answers[q.field]}
          onChange={(value) => setAnswer(q.field, value)}
          error={errors[q.field]}
        />
      ))}
    </>
  )
}

export function AboutStep({ errors }: StepProps) {
  const { state, setText } = useAssessment()
  return (
    <>
      <NumberField
        name="age"
        label="Age"
        unit="years"
        inputMode="numeric"
        hint="Vytal is for adults aged 18 and over."
        value={state.values.ageYears}
        onChange={(value) => setText('ageYears', value)}
        error={errors.ageYears}
      />
      <ChoiceQuestions questions={[SEX_QUESTION]} errors={errors} />
    </>
  )
}

function BmiPreview() {
  const { state } = useAssessment()
  const { heightCm, weightKg } = measurementsInMetric(state.values)
  if (state.values.measurementsUnknown) {
    return (
      <p className="bmi-preview bmi-preview--empty">
        Without height and weight, BMI cannot be calculated and the models cannot give an estimate. Vytal will not guess these values.
      </p>
    )
  }
  if (heightCm === null || weightKg === null || heightCm < 100 || weightKg < 25) {
    return <p className="bmi-preview bmi-preview--empty">Your BMI will appear here once both values are entered.</p>
  }
  const bmi = calculateBmi(heightCm, weightKg)
  return (
    <p className="bmi-preview" aria-live="polite">
      <span className="chip">derived</span> BMI <strong>{bmi}</strong>
      {isBmiInModelRange(bmi) ? <span className="muted"> · {whoBmiCategory(bmi)} (WHO adult categories)</span> : <span> · please check your values</span>}
    </p>
  )
}

export function BodyStep({ errors }: StepProps) {
  const { state, setText, setUnitSystem, setMeasurementsUnknown } = useAssessment()
  const { values } = state
  return (
    <>
      <div className="unit-toggle">
        <span id="unit-label" className="field__label">
          Units
        </span>
        <div className="segmented" role="group" aria-labelledby="unit-label">
          <button type="button" aria-pressed={values.unitSystem === 'metric'} onClick={() => setUnitSystem('metric')}>
            cm / kg
          </button>
          <button type="button" aria-pressed={values.unitSystem === 'imperial'} onClick={() => setUnitSystem('imperial')}>
            ft, in / lb
          </button>
        </div>
      </div>

      {!values.measurementsUnknown && (
        <div className="measurement-grid">
          {values.unitSystem === 'metric' ? (
            <>
              <NumberField name="height_cm" label="Height" unit="cm" value={values.heightCm} onChange={(v) => setText('heightCm', v)} error={errors.heightCm} />
              <NumberField name="weight_kg" label="Weight" unit="kg" value={values.weightKg} onChange={(v) => setText('weightKg', v)} error={errors.weightKg} />
            </>
          ) : (
            <>
              <div className="inline-fields">
                <NumberField name="height_ft" label="Height (feet)" unit="ft" inputMode="numeric" value={values.heightFeet} onChange={(v) => setText('heightFeet', v)} error={errors.heightFeet} />
                <NumberField name="height_in" label="and inches" unit="in" value={values.heightInches} onChange={(v) => setText('heightInches', v)} error={errors.heightInches} />
              </div>
              <NumberField name="weight_lb" label="Weight" unit="lb" value={values.weightPounds} onChange={(v) => setText('weightPounds', v)} error={errors.weightPounds} />
            </>
          )}
        </div>
      )}

      <label className="checkbox">
        <input type="checkbox" checked={values.measurementsUnknown} onChange={(event) => setMeasurementsUnknown(event.target.checked)} />
        I don&apos;t know my height or weight
      </label>
      <BmiPreview />
    </>
  )
}

export function LifestyleStep({ errors }: StepProps) {
  return <ChoiceQuestions questions={LIFESTYLE_QUESTIONS} errors={errors} />
}

export function HistoryStep({ errors }: StepProps) {
  return (
    <>
      <p className="muted">Only answer &quot;yes&quot; if a doctor or other health professional told you.</p>
      <ChoiceQuestions questions={HEALTH_HISTORY_QUESTIONS} errors={errors} />
    </>
  )
}

const REVIEW_SECTIONS: { step: number; fields: ChoiceField[] }[] = [
  { step: 2, fields: LIFESTYLE_QUESTIONS.map((q) => q.field) },
  { step: 3, fields: HEALTH_HISTORY_QUESTIONS.map((q) => q.field) },
]

export function ReviewStep() {
  const { state, goToStep } = useAssessment()
  const { values } = state
  const { heightCm, weightKg } = measurementsInMetric(values)
  const bmi = heightCm !== null && weightKg !== null ? calculateBmi(heightCm, weightKg) : null
  const questionText = (field: ChoiceField) =>
    [SEX_QUESTION, ...LIFESTYLE_QUESTIONS, ...HEALTH_HISTORY_QUESTIONS].find((q) => q.field === field)?.question ?? field

  const editButton = (step: number) => (
    <button type="button" className="button button--ghost review__edit" onClick={() => goToStep(step)}>
      <Pencil size={14} aria-hidden="true" /> Edit <span className="visually-hidden">{ASSESSMENT_STEPS[step].title}</span>
    </button>
  )

  return (
    <div className="review">
      <section className="review__section">
        <header>
          <h3>About you</h3>
          {editButton(0)}
        </header>
        <dl>
          <div>
            <dt>Age</dt>
            <dd>{values.ageYears} years</dd>
          </div>
          <div>
            <dt>Sex</dt>
            <dd>{optionLabel('sex', values.answers.sex)}</dd>
          </div>
        </dl>
      </section>
      <section className="review__section">
        <header>
          <h3>Height and weight</h3>
          {editButton(1)}
        </header>
        <dl>
          {values.measurementsUnknown ? (
            <div>
              <dt>Height and weight</dt>
              <dd>Not known (no estimate can be calculated)</dd>
            </div>
          ) : (
            <>
              <div>
                <dt>Height</dt>
                <dd>{heightCm !== null ? `${heightCm.toFixed(1)} cm` : '—'}</dd>
              </div>
              <div>
                <dt>Weight</dt>
                <dd>{weightKg !== null ? `${weightKg.toFixed(1)} kg` : '—'}</dd>
              </div>
              <div>
                <dt>BMI (derived)</dt>
                <dd>{bmi ?? '—'}</dd>
              </div>
            </>
          )}
        </dl>
      </section>
      {REVIEW_SECTIONS.map(({ step, fields }) => (
        <section className="review__section" key={step}>
          <header>
            <h3>{ASSESSMENT_STEPS[step].title}</h3>
            {editButton(step)}
          </header>
          <dl>
            {fields.map((field) => (
              <div key={field}>
                <dt>{questionText(field)}</dt>
                <dd>{optionLabel(field, values.answers[field])}</dd>
              </div>
            ))}
          </dl>
        </section>
      ))}
    </div>
  )
}
