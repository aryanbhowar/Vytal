import { NavLink } from 'react-router-dom'
import { useServiceStatus, type ServiceStatus } from '../../hooks/useServiceStatus'
import { VytalLogo } from './VytalLogo'

const STATUS_TEXT: Record<ServiceStatus, string> = {
  checking: 'Checking service…',
  ready: 'Models online',
  partial: 'One model offline',
  offline: 'Service offline',
}

const STATUS_DOT: Record<ServiceStatus, string> = {
  checking: '',
  ready: 'status-dot--ok',
  partial: 'status-dot--warning',
  offline: 'status-dot--error',
}

export function AppNavigation() {
  const status = useServiceStatus()
  return (
    <header className="app-header">
      <nav className="app-nav" aria-label="Main">
        <NavLink to="/" className="brand" aria-label="Vytal home">
          <VytalLogo />
          <span>Vytal</span>
        </NavLink>
        <ul className="app-nav__links">
          <li>
            <NavLink to="/assessment">Assessment</NavLink>
          </li>
          <li>
            <NavLink to="/methodology">How it works</NavLink>
          </li>
        </ul>
        <span className="service-status" role="status" title="Live status from the Vytal server">
          <span className={`status-dot ${STATUS_DOT[status]}`} aria-hidden="true" />
          <span className="service-status__text">{STATUS_TEXT[status]}</span>
        </span>
      </nav>
    </header>
  )
}
