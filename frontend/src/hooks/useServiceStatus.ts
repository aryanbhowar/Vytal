import { useEffect, useState } from 'react'
import type { ReadinessResponse } from '../types/assessment'

export type ServiceStatus = 'checking' | 'ready' | 'partial' | 'offline'

/** Real readiness from GET /api/health/ready (a 503 still reports which models loaded). */
export function useServiceStatus(): ServiceStatus {
  const [status, setStatus] = useState<ServiceStatus>('checking')
  useEffect(() => {
    let active = true
    fetch('/api/health/ready', { headers: { Accept: 'application/json' } })
      .then(async (response) => {
        const body = (await response.json()) as ReadinessResponse
        if (!active) return
        const loaded = Object.values(body.models ?? {}).filter(Boolean).length
        setStatus(body.ready ? 'ready' : loaded > 0 ? 'partial' : 'offline')
      })
      .catch(() => {
        if (active) setStatus('offline')
      })
    return () => {
      active = false
    }
  }, [])
  return status
}
