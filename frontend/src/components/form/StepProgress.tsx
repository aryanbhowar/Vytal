import { Check } from 'lucide-react'
import { ASSESSMENT_STEPS } from '../../config/assessmentQuestions'

export function StepProgress({ current }: { current: number }) {
  return (
    <nav aria-label="Assessment progress" className="step-progress">
      <p className="step-progress__summary">
        Step {current + 1} of {ASSESSMENT_STEPS.length}: <strong>{ASSESSMENT_STEPS[current].title}</strong>
      </p>
      <ol className="step-progress__list">
        {ASSESSMENT_STEPS.map((step, index) => {
          const state = index < current ? 'done' : index === current ? 'current' : 'upcoming'
          return (
            <li key={step.id} className={`step-progress__item step-progress__item--${state}`} aria-current={state === 'current' ? 'step' : undefined}>
              <span className="step-progress__marker" aria-hidden="true">
                {state === 'done' ? <Check size={14} /> : index + 1}
              </span>
              <span className="step-progress__label">{step.title}</span>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
