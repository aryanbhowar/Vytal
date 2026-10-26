import { AlertCircle } from 'lucide-react'
import { useId } from 'react'

interface NumberFieldProps {
  label: string
  value: string
  onChange: (value: string) => void
  unit?: string
  hint?: string
  error?: string
  inputMode?: 'numeric' | 'decimal'
  autoFocus?: boolean
  name: string
}

export function NumberField({ label, value, onChange, unit, hint, error, inputMode = 'decimal', autoFocus, name }: NumberFieldProps) {
  const id = useId()
  const hintId = `${id}-hint`
  const errorId = `${id}-error`
  const describedBy = [hint && hintId, error && errorId].filter(Boolean).join(' ') || undefined
  return (
    <div className={`field${error ? ' field--invalid' : ''}`}>
      <label className="field__label" htmlFor={id}>
        {label}
      </label>
      {hint && (
        <p className="field__hint" id={hintId}>
          {hint}
        </p>
      )}
      <div className="field__control">
        <input
          id={id}
          name={name}
          type="text"
          inputMode={inputMode}
          autoComplete="off"
          value={value}
          autoFocus={autoFocus}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          onChange={(event) => onChange(event.target.value)}
        />
        {unit && (
          <span className="field__unit" aria-hidden="true">
            {unit}
          </span>
        )}
      </div>
      {error && (
        <p className="field__error" id={errorId}>
          <AlertCircle size={16} aria-hidden="true" /> {error}
        </p>
      )}
    </div>
  )
}
