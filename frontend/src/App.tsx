import { useEffect, useState } from 'react'
import { fetchApiHealth, type ApiHealth } from './services/apiClient'

// Task 1 skeleton: confirms the frontend can reach the backend.
// The landing page and design system replace this screen in Task 8.

type ConnectionState =
  | { kind: 'checking' }
  | { kind: 'connected'; health: ApiHealth }
  | { kind: 'failed'; message: string }

function App() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: 'checking' })

  useEffect(() => {
    fetchApiHealth()
      .then((health) => setConnection({ kind: 'connected', health }))
      .catch((error: Error) => setConnection({ kind: 'failed', message: error.message }))
  }, [])

  return (
    <main className="status-page">
      <h1>Vytal</h1>
      <p className="tagline">Personalized health-risk assessment</p>
      <p className={`status status-${connection.kind}`} role="status">
        {connection.kind === 'checking' && 'Checking API connection…'}
        {connection.kind === 'connected' &&
          `API connected (${connection.health.app} v${connection.health.version})`}
        {connection.kind === 'failed' && connection.message}
      </p>
    </main>
  )
}

export default App
