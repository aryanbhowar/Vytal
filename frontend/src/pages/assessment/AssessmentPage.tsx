import { ArrowLeft, ArrowRight, Send } from 'lucide-react'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../../components/common/Button'
import { GlassCard } from '../../components/common/GlassCard'
import { DisclaimerBanner, ErrorState, LoadingState } from '../../components/common/Notices'
import { StepProgress } from '../../components/form/StepProgress'
import { ASSESSMENT_STEPS } from '../../config/assessmentQuestions'
import { useAssessment } from '../../context/AssessmentContext'
import { ApiError } from '../../services/apiClient'
import { submitAssessment } from '../../services/assessmentService'
import { firstStepWithErrors, toAssessmentRequest, validateStep, type FormErrors } from '../../utils/formValidation'
import { AboutStep, BodyStep, HistoryStep, LifestyleStep, ReviewStep } from './AssessmentSteps'

const STEP_INTROS: Record<string, string> = {
  about: 'A couple of basics. Vytal does not ask for your name or any contact details.',
  body: 'Used to calculate your body mass index (BMI). You can switch units.',
  lifestyle: 'Habits that are linked with heart and lung health in the survey data.',
  history: 'Conditions a health professional has told you about.',
  review: 'Check your answers. You can edit any section before getting your results.',
}

export function AssessmentPage() {
  const { state, goToStep, setResult } = useAssessment()
  const navigate = useNavigate()
  const [errors, setErrors] = useState<FormErrors>({})
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<ApiError | null>(null)
  const headingRef = useRef<HTMLHeadingElement>(null)
  const stepIndex = Math.min(state.stepIndex, ASSESSMENT_STEPS.length - 1)
  const step = ASSESSMENT_STEPS[stepIndex]
  const isReview = step.id === 'review'

  // Move focus to the step heading on step change so keyboard and screen-reader users know where they are.
  useEffect(() => {
    headingRef.current?.focus()
  }, [stepIndex])

  function goTo(index: number) {
    setErrors({})
    setSubmitError(null)
    goToStep(index)
    window.scrollTo({ top: 0 })
  }

  async function submit() {
    const invalidStep = firstStepWithErrors(state.values)
    if (invalidStep) {
      const index = ASSESSMENT_STEPS.findIndex((s) => s.id === invalidStep)
      goTo(index)
      setErrors(validateStep(invalidStep, state.values))
      return
    }
    setSubmitting(true)
    setSubmitError(null)
    try {
      const result = await submitAssessment(toAssessmentRequest(state.values))
      setResult(result)
      navigate('/results')
    } catch (error) {
      setSubmitError(error instanceof ApiError ? error : new ApiError('Something unexpected went wrong. Please try again.', null))
    } finally {
      setSubmitting(false)
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (isReview) {
      void submit()
      return
    }
    const stepErrors = validateStep(step.id, state.values)
    setErrors(stepErrors)
    if (Object.keys(stepErrors).length === 0) goTo(stepIndex + 1)
  }

  const errorCount = Object.keys(errors).length

  return (
    <div className="page page--narrow assessment">
      <StepProgress current={stepIndex} />
      <GlassCard as="section" large blur className="assessment__card enter" labelledBy="step-heading">
        <form onSubmit={handleSubmit} noValidate className="stack-lg">
          <header className="stack-sm">
            <h1 id="step-heading" ref={headingRef} tabIndex={-1}>
              {step.title}
            </h1>
            <p className="muted">{STEP_INTROS[step.id]}</p>
          </header>

          {errorCount > 0 && (
            <p className="notice notice--danger" role="alert">
              {errorCount === 1 ? 'One answer needs attention.' : `${errorCount} answers need attention.`}
            </p>
          )}

          <div className="stack-lg">
            {step.id === 'about' && <AboutStep errors={errors} />}
            {step.id === 'body' && <BodyStep errors={errors} />}
            {step.id === 'lifestyle' && <LifestyleStep errors={errors} />}
            {step.id === 'history' && <HistoryStep errors={errors} />}
            {isReview && <ReviewStep />}
          </div>

          {submitting && <LoadingState label="Running the heart and lung models…" />}
          {submitError && (
            <ErrorState title="Your results could not be calculated" message={submitError.message} onRetry={() => void submit()}>
              {submitError.fieldErrors.length > 0 && (
                <ul>
                  {submitError.fieldErrors.map((e) => (
                    <li key={e.field}>
                      {e.field}: {e.message}
                    </li>
                  ))}
                </ul>
              )}
            </ErrorState>
          )}

          <div className="form-actions">
            {stepIndex > 0 ? (
              <Button variant="ghost" onClick={() => goTo(stepIndex - 1)} disabled={submitting}>
                <ArrowLeft size={16} aria-hidden="true" /> Back
              </Button>
            ) : (
              <span />
            )}
            <Button type="submit" large disabled={submitting}>
              {isReview ? (
                <>
                  See my results <Send size={16} aria-hidden="true" />
                </>
              ) : (
                <>
                  Continue <ArrowRight size={16} aria-hidden="true" />
                </>
              )}
            </Button>
          </div>
        </form>
      </GlassCard>
      {isReview && <DisclaimerBanner compact />}
    </div>
  )
}
