import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AppRoutes } from '../App'
import { AssessmentProvider, STORAGE_KEY, type AssessmentState } from '../context/AssessmentContext'

/** Render the real routes at a given URL, optionally with saved session state. */
export function renderApp(path: string, savedState?: Partial<AssessmentState>) {
  if (savedState) window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(savedState))
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AssessmentProvider>
        <AppRoutes />
      </AssessmentProvider>
    </MemoryRouter>,
  )
}
