import { Route, Routes, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { AppFooter } from './components/layout/AppFooter'
import { AppNavigation } from './components/layout/AppNavigation'
import { AssessmentPage } from './pages/assessment/AssessmentPage'
import { LandingPage } from './pages/LandingPage'
import { MethodologyPage } from './pages/MethodologyPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ResultsPage } from './pages/ResultsPage'

const TITLES: Record<string, string> = {
  '/': 'Vytal: personalized health-risk assessment',
  '/assessment': 'Assessment · Vytal',
  '/results': 'Your results · Vytal',
  '/methodology': 'How it works · Vytal',
}

function DocumentTitle() {
  const { pathname } = useLocation()
  useEffect(() => {
    document.title = TITLES[pathname] ?? 'Vytal'
  }, [pathname])
  return null
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/assessment" element={<AssessmentPage />} />
      <Route path="/results" element={<ResultsPage />} />
      <Route path="/methodology" element={<MethodologyPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default function App() {
  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <DocumentTitle />
      <AppNavigation />
      <main id="main" className="app-main">
        <AppRoutes />
      </main>
      <AppFooter />
    </>
  )
}
