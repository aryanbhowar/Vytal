import { useCallback, useEffect, useState } from 'react'
import { ButtonLink } from '../components/common/Button'
import { GlassCard } from '../components/common/GlassCard'
import { DisclaimerBanner, ErrorState, LoadingState } from '../components/common/Notices'
import { ApiError } from '../services/apiClient'
import { fetchModelsStatus } from '../services/assessmentService'
import type { ModelStatus } from '../types/assessment'
import { formatPercent, shortFactorLabel } from '../utils/formatting'

function ModelMethodCard({ model }: { model: ModelStatus }) {
  if (!model.available || !model.evaluation) {
    return (
      <GlassCard as="article" className="method-card">
        <h3>{model.title}</h3>
        <p className="muted">Unavailable on this server: {model.unavailable_reason}</p>
      </GlassCard>
    )
  }
  const e = model.evaluation
  return (
    <GlassCard as="article" className="method-card" labelledBy={`method-${model.model_id}`}>
      <h3 id={`method-${model.model_id}`}>{model.title}</h3>
      <p>{model.outcome_description}</p>
      <dl className="metric-grid">
        <div>
          <dt>Training respondents</dt>
          <dd>{model.training_rows?.toLocaleString('en-US')}</dd>
        </div>
        <div>
          <dt>Test respondents (never seen in training)</dt>
          <dd>{e.test_rows.toLocaleString('en-US')}</dd>
        </div>
        <div>
          <dt>ROC-AUC</dt>
          <dd>{e.roc_auc.toFixed(3)}</dd>
        </div>
        <div>
          <dt>PR-AUC</dt>
          <dd>{e.pr_auc.toFixed(3)}</dd>
        </div>
        <div>
          <dt>Average calibration gap</dt>
          <dd>{(e.expected_calibration_error * 100).toFixed(2)} points</dd>
        </div>
        <div>
          <dt>Brier score</dt>
          <dd>{e.brier_score.toFixed(4)}</dd>
        </div>
        <div>
          <dt>Sensitivity / specificity*</dt>
          <dd>
            {formatPercent(e.sensitivity)} / {formatPercent(e.specificity)}
          </dd>
        </div>
        <div>
          <dt>Precision*</dt>
          <dd>{formatPercent(e.precision)}</dd>
        </div>
      </dl>
      <p className="muted small">
        *At a {formatPercent(e.reporting_threshold)} reporting threshold chosen on validation data. Vytal does not show users a yes/no result.
        Inputs: {model.features.map(shortFactorLabel).join(', ')}. Survey years {model.training_years.join(', ')}. Calibration:{' '}
        {model.calibration_method}. Version {model.model_version}.
      </p>
    </GlassCard>
  )
}

export function MethodologyPage() {
  const [models, setModels] = useState<ModelStatus[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchModels = useCallback(() => {
    fetchModelsStatus()
      .then((r) => setModels(r.models))
      .catch((e: unknown) => setError(e instanceof ApiError ? e.message : 'Model details could not be loaded.'))
  }, [])

  useEffect(() => {
    fetchModels()
  }, [fetchModels])

  function load() {
    setError(null)
    setModels(null)
    fetchModels()
  }

  return (
    <div className="page page--reading methodology">
      <header className="stack-sm enter">
        <p className="eyebrow">How it works</p>
        <h1>Methodology and limitations</h1>
        <p className="muted">How Vytal&apos;s two models were built, what they estimate and where they fall short.</p>
      </header>

      <section className="stack-md" aria-labelledby="data-heading">
        <h2 id="data-heading">The data</h2>
        <p>
          The models learned from the CDC <strong>Behavioral Risk Factor Surveillance System</strong> (BRFSS) for 2022, 2023 and
          2024: a yearly telephone survey of US adults. Each year interviews different people. Only questions asked the same way in
          all three years were used, and every downloaded file was checked against CDC&apos;s published counts.
        </p>
        <p>
          The outcomes are whether a respondent said a health professional had <em>ever</em> told them they had the condition. So
          the models learn which answers go with <strong>having reported</strong> the condition. They do not predict future illness.
        </p>
      </section>

      <section className="stack-md" aria-labelledby="models-heading">
        <h2 id="models-heading">The models (live figures from the server)</h2>
        <p>
          Each model is a logistic regression: every answer adds or subtracts from a score, which becomes an estimate. This makes
          the explanations exact. The data was split into training (70%), validation (15%, used for every choice) and test (15%,
          used once for the figures below).
        </p>
        {models === null && !error && <LoadingState label="Loading model details…" />}
        {error && <ErrorState title="Model details unavailable" message={error} onRetry={load} />}
        {models && (
          <div className="method-grid">
            {models.map((m) => (
              <ModelMethodCard key={m.model_id} model={m} />
            ))}
          </div>
        )}
        <dl className="term-grid">
          <div>
            <dt>ROC-AUC</dt>
            <dd>How often the model ranks a person who reported the condition above one who did not (0.5 = guessing, 1 = perfect).</dd>
          </div>
          <div>
            <dt>PR-AUC</dt>
            <dd>Precision across all thresholds. Compare it with the share who reported the condition (about 0.08–0.09).</dd>
          </div>
          <div>
            <dt>Calibration gap</dt>
            <dd>The average difference between an estimate and what actually happened for people with that estimate.</dd>
          </div>
          <div>
            <dt>Why not accuracy?</dt>
            <dd>Only about 9% reported each condition, so always saying &quot;no&quot; would be 91% accurate and useless.</dd>
          </div>
        </dl>
      </section>

      <section className="stack-md" aria-labelledby="bands-heading">
        <h2 id="bands-heading">Bands and explanations</h2>
        <p>
          Bands show where an estimate falls among the training-set survey respondents: <strong>Low</strong> below the 50th
          percentile, <strong>Moderate</strong> 50th–75th, <strong>Elevated</strong> 75th–90th, <strong>High</strong> top 10%. In
          held-out testing, the share of people who had reported the condition rose steadily from Low to High in both models. They
          are positions, not clinical risk categories.
        </p>
        <p>
          &quot;What moved your estimate&quot; compares each of your answers with an average respondent, using the model&apos;s
          own weights. These are associations in survey data, not causes.
        </p>
      </section>

      <section className="stack-md" aria-labelledby="limits-heading">
        <h2 id="limits-heading">Limitations</h2>
        <ul className="limit-list">
          <li>Self-reported answers; people with undiagnosed conditions count as &quot;no&quot;.</li>
          <li>Answers describe people now, sometimes after a diagnosis (for example, people may stop smoking after a heart attack).</li>
          <li>US adults reached by telephone; results may not transfer to other countries or groups.</li>
          <li>Blood pressure and cholesterol are not included because the survey only asked them in 2023.</li>
          <li>Heavy drinking was left out of the heart model because, in this survey, it showed a misleading reversed link.</li>
          <li>About 12–17% of respondents were left out for missing answers; this shifted the outcome rate by under 1 point.</li>
          <li>Vytal has not been clinically validated and is not a medical device.</li>
        </ul>
        <DisclaimerBanner />
      </section>

      <section className="stack-sm" aria-labelledby="privacy-heading">
        <h2 id="privacy-heading">Privacy</h2>
        <p>
          Vytal does not ask for your name, email or location. Your answers stay in this browser tab (cleared when you close it or
          press Start over) and are sent once to the Vytal server to calculate your results. The server does not store or log them.
        </p>
      </section>

      <p>
        <ButtonLink to="/assessment">Start the assessment</ButtonLink>
      </p>
    </div>
  )
}
