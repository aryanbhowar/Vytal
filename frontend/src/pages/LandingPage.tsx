import { ArrowRight, ClipboardList, Cpu, HeartPulse, LineChart, Lock, Wind } from 'lucide-react'
import { useEffect, useState } from 'react'
import { ButtonLink } from '../components/common/Button'
import { GlassCard } from '../components/common/GlassCard'
import { DisclaimerBanner } from '../components/common/Notices'
import { useAssessment } from '../context/AssessmentContext'
import { fetchModelsStatus } from '../services/assessmentService'
import type { ModelStatus } from '../types/assessment'
import { formatPercent } from '../utils/formatting'

const STEPS = [
  { icon: ClipboardList, title: 'Answer 11 questions', text: 'Age, sex, height and weight, a few lifestyle questions and your health history. About two minutes. No name or email.' },
  { icon: Cpu, title: 'Two models run', text: 'Separate models for heart and lung conditions, trained on about 1.1 million US health-survey answers, run on the Vytal server.' },
  { icon: LineChart, title: 'See what it means', text: 'Your estimates next to the survey average, which answers moved them, and general suggestions with sources.' },
]

function ModelFacts({ status }: { status: ModelStatus }) {
  if (!status.available || !status.evaluation) {
    return <p className="muted small">Currently unavailable on this server.</p>
  }
  return (
    <dl className="fact-row">
      <div>
        <dt>Survey respondents in training</dt>
        <dd>{status.training_rows?.toLocaleString('en-US')}</dd>
      </div>
      <div>
        <dt>Ranking accuracy (ROC-AUC, held-out test)</dt>
        <dd>{status.evaluation.roc_auc.toFixed(2)}</dd>
      </div>
      <div>
        <dt>US survey average</dt>
        <dd>{status.survey_prevalence !== null ? formatPercent(status.survey_prevalence) : '—'}</dd>
      </div>
    </dl>
  )
}

export function LandingPage() {
  const { state } = useAssessment()
  const [models, setModels] = useState<ModelStatus[] | null>(null)

  useEffect(() => {
    fetchModelsStatus()
      .then((response) => setModels(response.models))
      .catch(() => setModels([]))
  }, [])

  const hasProgress = state.result !== null || state.stepIndex > 0
  const byId = Object.fromEntries((models ?? []).map((m) => [m.model_id, m]))

  return (
    <div className="page landing">
      <section className="hero enter" aria-labelledby="hero-title">
        <p className="eyebrow">Personalized health-risk assessment</p>
        <h1 id="hero-title">
          Understand how your answers compare,
          <span className="hero__accent"> for your heart and lungs.</span>
        </h1>
        <p className="hero__lead">
          Vytal compares your answers with over a million responses to a large US health survey and shows how often people
          like you had been diagnosed with heart disease or COPD, and which of your answers mattered most.
        </p>
        <div className="hero__actions">
          <ButtonLink to="/assessment" large>
            {hasProgress ? 'Continue assessment' : 'Start the assessment'} <ArrowRight size={18} aria-hidden="true" />
          </ButtonLink>
          <ButtonLink to="/methodology" variant="secondary" large>
            How it works
          </ButtonLink>
        </div>
        <p className="hero__privacy">
          <Lock size={14} aria-hidden="true" /> No account. Your answers are not stored.
        </p>
      </section>

      <section className="landing__steps" aria-labelledby="steps-title">
        <h2 id="steps-title" className="section-title">
          How Vytal works
        </h2>
        <ol className="step-cards">
          {STEPS.map(({ icon: Icon, title, text }, index) => (
            <li key={title}>
              <GlassCard subtle className="step-card">
                <span className="step-card__number">{index + 1}</span>
                <Icon size={22} aria-hidden="true" className="step-card__icon" />
                <h3>{title}</h3>
                <p>{text}</p>
              </GlassCard>
            </li>
          ))}
        </ol>
      </section>

      <section className="landing__models" aria-labelledby="models-title">
        <h2 id="models-title" className="section-title">
          Two separate estimates
        </h2>
        <div className="model-cards">
          <GlassCard as="article" className="model-card" labelledBy="heart-model">
            <HeartPulse size={26} aria-hidden="true" className="model-card__icon" />
            <h3 id="heart-model">Heart</h3>
            <p>How often people with answers like yours reported coronary heart disease or a heart attack.</p>
            {models === null ? <p className="muted small">Loading live model details…</p> : byId.heart && <ModelFacts status={byId.heart} />}
          </GlassCard>
          <GlassCard as="article" className="model-card" labelledBy="lung-model">
            <Wind size={26} aria-hidden="true" className="model-card__icon" />
            <h3 id="lung-model">Lungs</h3>
            <p>How often people with answers like yours reported COPD, emphysema or chronic bronchitis.</p>
            {models === null ? <p className="muted small">Loading live model details…</p> : byId.respiratory && <ModelFacts status={byId.respiratory} />}
          </GlassCard>
        </div>
        {models !== null && models.length === 0 && (
          <p className="muted small">Live model details could not be loaded. Is the Vytal server running?</p>
        )}
      </section>

      <section className="landing__scope" aria-labelledby="scope-title">
        <GlassCard subtle large>
          <h2 id="scope-title">What Vytal can and cannot tell you</h2>
          <div className="scope-grid">
            <div>
              <h3>It can</h3>
              <ul>
                <li>Show how your answers compare with US survey respondents.</li>
                <li>Point to the answers most linked with each condition in the data.</li>
                <li>Suggest general, evidence-based next steps.</li>
              </ul>
            </div>
            <div>
              <h3>It cannot</h3>
              <ul>
                <li>Diagnose a condition or predict your future health.</li>
                <li>Use blood pressure, cholesterol or test results.</li>
                <li>Replace a health professional.</li>
              </ul>
            </div>
          </div>
          <DisclaimerBanner />
        </GlassCard>
      </section>
    </div>
  )
}
