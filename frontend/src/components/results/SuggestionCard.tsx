import { Activity, AlertOctagon, CigaretteOff, ClipboardCheck, ExternalLink, Scale, Stethoscope } from 'lucide-react'
import type { Suggestion } from '../../types/assessment'

const THEME_ICONS: Record<string, typeof Activity> = {
  Safety: AlertOctagon,
  Tobacco: CigaretteOff,
  'Physical activity': Activity,
  Weight: Scale,
  'Ongoing care': Stethoscope,
  'Check-up': ClipboardCheck,
}

export function SuggestionCard({ suggestion }: { suggestion: Suggestion }) {
  const Icon = THEME_ICONS[suggestion.theme] ?? ClipboardCheck
  return (
    <article className={`suggestion suggestion--${suggestion.priority}`}>
      <span className="suggestion__icon">
        <Icon size={20} aria-hidden="true" />
      </span>
      <div className="stack-sm">
        <p className="suggestion__theme">{suggestion.theme}</p>
        <h3>{suggestion.title}</h3>
        <p>{suggestion.body}</p>
        <a href={suggestion.source_url} target="_blank" rel="noopener noreferrer" className="suggestion__source">
          {suggestion.source_name} <ExternalLink size={14} aria-hidden="true" />
          <span className="visually-hidden">(opens in a new tab)</span>
        </a>
      </div>
    </article>
  )
}
