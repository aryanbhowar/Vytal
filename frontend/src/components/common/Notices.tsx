import { AlertTriangle, Info, RefreshCw, ShieldAlert } from 'lucide-react'
import type { ReactNode } from 'react'
import { Button } from './Button'

export function DisclaimerBanner({ compact = false }: { compact?: boolean }) {
  return (
    <div className="notice notice--info" role="note">
      <Info size={18} aria-hidden="true" />
      <p>
        <strong>Not a diagnosis.</strong> Vytal has not been clinically validated. Its estimates describe patterns in a US
        health survey{compact ? '.' : ' and cannot tell you whether you have, or will develop, a condition.'} If you have
        chest pain, severe breathlessness or other urgent symptoms, seek emergency care now.
      </p>
    </div>
  )
}

export function LoadingState({ label }: { label: string }) {
  return (
    <div className="state-panel" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <p>{label}</p>
    </div>
  )
}

interface ErrorStateProps {
  title: string
  message: string
  onRetry?: () => void
  children?: ReactNode
}

export function ErrorState({ title, message, onRetry, children }: ErrorStateProps) {
  return (
    <div className="notice notice--danger state-error" role="alert">
      <ShieldAlert size={20} aria-hidden="true" />
      <div className="stack-sm">
        <strong>{title}</strong>
        <p>{message}</p>
        {children}
        {onRetry && (
          <div>
            <Button variant="secondary" onClick={onRetry}>
              <RefreshCw size={16} aria-hidden="true" /> Try again
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

export function WarningNotice({ children }: { children: ReactNode }) {
  return (
    <div className="notice notice--warning" role="note">
      <AlertTriangle size={18} aria-hidden="true" />
      <div>{children}</div>
    </div>
  )
}
