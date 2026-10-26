import '@fontsource-variable/inter'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import { AssessmentProvider } from './context/AssessmentContext.tsx'
import './styles/tokens.css'
import './styles/global.css'
import './styles/glass.css'
import './styles/layout.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AssessmentProvider>
        <App />
      </AssessmentProvider>
    </BrowserRouter>
  </StrictMode>,
)
