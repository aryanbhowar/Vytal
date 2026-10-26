import { ButtonLink } from '../components/common/Button'

export function NotFoundPage() {
  return (
    <div className="page page--narrow stack-md">
      <h1>Page not found</h1>
      <p className="muted">That page does not exist.</p>
      <p>
        <ButtonLink to="/">Go to the home page</ButtonLink>
      </p>
    </div>
  )
}
