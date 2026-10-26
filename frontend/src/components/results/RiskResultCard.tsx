import { ArrowDown, ArrowUp, HeartPulse, Info, Wind } from 'lucide-react'
import type { ModelResult } from '../../types/assessment'
import { BAND_LABELS, describePercentile, formatPercent, inHundred } from '../../utils/formatting'
import { GlassCard } from '../common/GlassCard'
import { WarningNotice } from '../common/Notices'
import { BandScale } from './BandScale'
import { shortFactorLabel } from '../../utils/formatting'
import { ContributionChart } from './ContributionChart'

const OUTCOME_NOUN: Record<ModelResult['model_id'], string> = {
  heart: 'coronary heart disease or a heart attack',
  respiratory: 'COPD, emphysema or chronic bronchitis',
}

function ModelIcon({ modelId }: { modelId: ModelResult['model_id'] }) {
  return modelId === 'heart' ? <HeartPulse size={22} aria-hidden="true" /> : <Wind size={22} aria-hidden="true" />
}

export function RiskResultCard({ result }: { result: ModelResult }) {
  const headingId = `result-${result.model_id}`
  if (result.status !== 'ok' || result.estimated_probability === null || result.category === null || result.percentile === null) {
    return (
      <GlassCard as="section" className="result-card result-card--empty" labelledBy={headingId}>
        <header className="result-card__header">
          <span className="result-card__icon">
            <ModelIcon modelId={result.model_id} />
          </span>
          <h2 id={headingId}>{result.title}</h2>
        </header>
        <WarningNotice>
          <strong>{result.status === 'insufficient_input' ? 'Not enough information' : 'Estimate unavailable'}</strong>
          <p>{result.message}</p>
        </WarningNotice>
        <p className="muted">No estimate is shown rather than a guessed one.</p>
      </GlassCard>
    )
  }

  const probability = result.estimated_probability
  const prevalence = result.survey_prevalence ?? 0
  const ratio = prevalence > 0 ? probability / prevalence : null
  return (
    <GlassCard as="section" className={`result-card result-card--${result.category}`} labelledBy={headingId} blur>
      <header className="result-card__header">
        <span className="result-card__icon">
          <ModelIcon modelId={result.model_id} />
        </span>
        <h2 id={headingId}>{result.title}</h2>
        <span className={`band-chip band-chip--${result.category}`}>{BAND_LABELS[result.category]}</span>
      </header>

      <div className="result-card__figures">
        <div className="figure figure--primary">
          <span className="figure__label">Model estimate</span>
          <span className="figure__value">{formatPercent(probability)}</span>
          <span className="figure__note">Of survey respondents with answers like yours, {inHundred(probability)} had reported this condition.</span>
        </div>
        <div className="figure">
          <span className="figure__label">US survey average</span>
          <span className="figure__value figure__value--secondary">{formatPercent(prevalence)}</span>
          <span className="figure__note">
            {ratio !== null && ratio >= 1.15
              ? `Your estimate is ${ratio.toFixed(1)}× the average.`
              : ratio !== null && ratio <= 0.85
                ? 'Your estimate is below the average.'
                : 'Your estimate is close to the average.'}
          </span>
        </div>
      </div>

      <div className="stack-sm">
        <p className="result-card__band-text">
          <strong>{BAND_LABELS[result.category]}:</strong> your estimate is {describePercentile(result.percentile)}.
        </p>
        <BandScale percentile={result.percentile} band={result.category} />
        {result.band_validation && (
          <p className="muted small">
            In testing on survey respondents the model had not seen, {formatPercent(result.band_validation.observed_rate)} of
            people in the {BAND_LABELS[result.category]} band had reported {OUTCOME_NOUN[result.model_id]}.
          </p>
        )}
      </div>

      {result.contributing_factors.length > 0 && (
        <div className="result-card__factors">
          <h3>What moved your estimate</h3>
          <p className="muted small">Compared with an average survey respondent. These are associations the model learned, not causes.</p>
          <ContributionChart factors={result.contributing_factors} title={`Factors for ${result.title}`} />
          <ul className="factor-list">
            {result.contributing_factors.map((factor) => (
              <li key={factor.feature} className={`factor factor--${factor.direction}`}>
                {factor.direction === 'raised' ? <ArrowUp size={16} aria-hidden="true" /> : <ArrowDown size={16} aria-hidden="true" />}
                <span>
                  <strong>{shortFactorLabel(factor.feature)}</strong>: {factor.answer}{' '}
                  <span className="muted">
                    ({factor.direction} the estimate{factor.modifiable ? '; something you can change' : ''})
                  </span>
                </span>
              </li>
            ))}
          </ul>
          {result.explanation_note && <p className="muted small">{result.explanation_note}</p>}
        </div>
      )}

      <details className="result-card__details">
        <summary>
          <Info size={16} aria-hidden="true" /> What this estimate is and is not
        </summary>
        <div className="stack-sm">
          <p>{result.outcome_description}</p>
          <ul>
            {result.limitations.map((limitation) => (
              <li key={limitation}>{limitation}</li>
            ))}
          </ul>
          <p className="muted small">Model version {result.model_version}.</p>
        </div>
      </details>
    </GlassCard>
  )
}
