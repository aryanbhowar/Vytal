import type { Band } from '../../types/assessment'
import { BAND_LABELS, BAND_PERCENTILE_EDGES, ordinal } from '../../utils/formatting'

const BANDS: Band[] = ['low', 'moderate', 'elevated', 'high']

/** Horizontal scale of survey-respondent percentiles with the four bands and the person's position. */
export function BandScale({ percentile, band }: { percentile: number; band: Band }) {
  const widths = BANDS.map((b, i) => (i + 1 < BANDS.length ? BAND_PERCENTILE_EDGES[BANDS[i + 1]] : 100) - BAND_PERCENTILE_EDGES[b])
  return (
    <figure className="band-scale">
      <div className="band-scale__track">
        {BANDS.map((b, i) => (
          <span key={b} className={`band-scale__segment band-scale__segment--${b}${b === band ? ' is-active' : ''}`} style={{ flexBasis: `${widths[i]}%` }} />
        ))}
        <span className="band-scale__marker" style={{ left: `${Math.min(Math.max(percentile, 1), 99)}%` }} aria-hidden="true" />
      </div>
      <div className="band-scale__labels" aria-hidden="true">
        {BANDS.map((b, i) => (
          <span key={b} style={{ flexBasis: `${widths[i]}%` }} className={b === band ? 'is-active' : undefined}>
            {BAND_LABELS[b]}
          </span>
        ))}
      </div>
      <figcaption className="visually-hidden">
        Your estimate is at the {ordinal(percentile)} percentile of survey respondents, in the {BAND_LABELS[band]} band.
        Bands: Low below the 50th percentile, Moderate 50th to 75th, Elevated 75th to 90th, High 90th and above.
      </figcaption>
    </figure>
  )
}
