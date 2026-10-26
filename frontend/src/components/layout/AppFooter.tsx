import { Link } from 'react-router-dom'

export function AppFooter() {
  return (
    <footer className="app-footer">
      <div className="app-footer__inner">
        <p>
          Vytal is not a medical device, has not been clinically validated and does not replace a health professional.
          Your answers are not stored: they stay in this browser tab and are sent once to calculate your results.
        </p>
        <p>
          Data source: CDC, Behavioral Risk Factor Surveillance System 2022–2024. Use of these data does not imply
          endorsement by CDC, HHS or the U.S. Government. <Link to="/methodology">Methodology and limitations</Link>
        </p>
      </div>
    </footer>
  )
}
