import { AlertCircle } from 'lucide-react'
import { useId } from 'react'
import type { ChoiceOption } from '../../config/assessmentQuestions'

interface RadioCardGroupProps {
  name: string
  legend: string
  help?: string
  options: readonly ChoiceOption<string>[]
  value: string | null
  onChange: (value: string) => void
  error?: string
}

export function RadioCardGroup({ name, legend, help, options, value, onChange, error }: RadioCardGroupProps) {
  const id = useId()
  const describedBy = [help && `${id}-help`, error && `${id}-error`].filter(Boolean).join(' ') || undefined
  return (
    <fieldset className={`choice-group${error ? ' choice-group--invalid' : ''}`} aria-describedby={describedBy}>
      <legend>{legend}</legend>
      {help && (
        <p className="field__hint" id={`${id}-help`}>
          {help}
        </p>
      )}
      <div className="choice-group__options">
        {options.map((option) => (
          <label className="choice-card" key={option.value}>
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
            />
            <span className="choice-card__dot" aria-hidden="true" />
            <span>{option.label}</span>
          </label>
        ))}
      </div>
      {error && (
        <p className="field__error" id={`${id}-error`}>
          <AlertCircle size={16} aria-hidden="true" /> {error}
        </p>
      )}
    </fieldset>
  )
}
