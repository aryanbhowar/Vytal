import { Pencil, Printer, RotateCcw } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { Button, ButtonLink } from '../components/common/Button'
import { GlassCard } from '../components/common/GlassCard'
import { ProfileSummary } from '../components/results/ProfileSummary'
import { RiskResultCard } from '../components/results/RiskResultCard'
import { SuggestionCard } from '../components/results/SuggestionCard'
import { ASSESSMENT_STEPS } from '../config/assessmentQuestions'
import { useAssessment } from '../context/AssessmentContext'
import { BAND_LABELS } from '../utils/formatting'

export function ResultsPage() {
  const { state, reset, goToStep } = useAssessment()
  const navigate = useNavigate()
  const headingRef = useRef<HTMLHeadingElement>(null)
  // Set while "Start over" is leaving the page, so clearing the result does not
  // trigger the "no result yet" redirect to the questionnaire.
  const [leaving, setLeaving] = useState(false)

  useEffect(() => {
    headingRef.current?.focus()
  }, [])

  if (!state.result) {
    return leaving ? null : <Navigate to="/assessment" replace />
  }
  const { results, suggestions, profile_summary: profile, disclaimer, data_attribution: attribution } = state.result
  const available = results.filter((r) => r.status === 'ok')
  const urgent = suggestions.filter((s) => s.priority === 'urgent')
  const others = suggestions.filter((s) => s.priority !== 'urgent')

  function startOver() {
    setLeaving(true)
    navigate('/')
    reset()
  }

  function reviseAnswers() {
    goToStep(ASSESSMENT_STEPS.length - 1)
    navigate('/assessment')
  }

  return (
    <div className="page results">
      <header className="results__header enter">
        <p className="eyebrow">Your results</p>
        <h1 ref={headingRef} tabIndex={-1}>
          Heart and lung estimates
        </h1>
        <p className="muted results__summary">
          {available.length === 0
            ? 'No estimate could be calculated from these answers. See the details below.'
            : available.map((r) => `${r.model_id === 'heart' ? 'Heart' : 'Lungs'}: ${BAND_LABELS[r.category ?? 'low']}`).join(' · ') +
              '. Bands compare your estimate with US survey respondents; they are not diagnoses.'}
        </p>
        <div className="results__actions">
          <Button variant="secondary" onClick={reviseAnswers}>
            <Pencil size={16} aria-hidden="true" /> Revise answers
          </Button>
          <Button variant="secondary" onClick={() => window.print()}>
            <Printer size={16} aria-hidden="true" /> Print
          </Button>
          <Button variant="ghost" onClick={startOver}>
            <RotateCcw size={16} aria-hidden="true" /> Start over
          </Button>
        </div>
      </header>

      {urgent.map((s) => (
        <div className="notice notice--danger" role="note" key={s.id}>
          <div className="stack-sm">
            <strong>{s.title}</strong>
            <p>{s.body}</p>
          </div>
        </div>
      ))}

      <div className="results__grid">
        {results.map((result) => (
          <RiskResultCard key={result.model_id} result={result} />
        ))}
      </div>

      <GlassCard as="section" className="understanding" labelledBy="understanding-heading" subtle>
        <h2 id="understanding-heading">Reading these numbers</h2>
        <dl className="term-grid">
          <div>
            <dt>Model estimate</dt>
            <dd>The model&apos;s estimate of how often survey respondents with answers like yours had been told they have the condition. It was checked against real outcomes in held-out survey data.</dd>
          </div>
          <div>
            <dt>US survey average</dt>
            <dd>The share of all US adult respondents (weighted to represent the population) who reported the condition.</dd>
          </div>
          <div>
            <dt>Band</dt>
            <dd>Where your estimate falls among survey respondents: Low (below the 50th percentile), Moderate (50th–75th), Elevated (75th–90th), High (top 10%). Not a clinical category.</dd>
          </div>
          <div>
            <dt>Your clinical risk</dt>
            <dd>Not something Vytal can estimate. It needs a health professional, measurements such as blood pressure and cholesterol, and validated clinical tools.</dd>
          </div>
        </dl>
      </GlassCard>

      {others.length > 0 && (
        <section aria-labelledby="suggestions-heading" className="stack-md">
          <div>
            <h2 id="suggestions-heading" className="section-title">
              General suggestions
            </h2>
            <p className="muted">Based on your answers. General public-health guidance, not medical advice or treatment.</p>
          </div>
          <div className="suggestion-grid">
            {others.map((s) => (
              <SuggestionCard key={s.id} suggestion={s} />
            ))}
          </div>
        </section>
      )}

      <ProfileSummary profile={profile} />

      <section className="stack-sm" aria-label="Disclaimer and data source">
        <div className="notice notice--info" role="note">
          <p>{disclaimer}</p>
        </div>
        <p className="muted small">{attribution}</p>
        <p>
          <ButtonLink to="/methodology" variant="ghost">
            How the models were built and tested
          </ButtonLink>
        </p>
      </section>
    </div>
  )
}
