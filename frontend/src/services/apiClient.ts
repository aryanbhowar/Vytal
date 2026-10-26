// The only place that talks to the Vytal backend. Components call the service
// functions instead of fetch, so URLs and error handling live in one file.

export interface ApiHealth {
  status: string
  app: string
  version: string
}

export interface ApiFieldError {
  field: string
  message: string
}

export class ApiError extends Error {
  readonly status: number | null
  readonly fieldErrors: ApiFieldError[]

  constructor(message: string, status: number | null, fieldErrors: ApiFieldError[] = []) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.fieldErrors = fieldErrors
  }

  get isNetworkError(): boolean {
    return this.status === null
  }
}

const UNREACHABLE = 'Vytal could not reach its server. Check that the backend is running, then try again.'

function messageForStatus(status: number, detail: string | undefined): string {
  if (status === 422) return detail ?? 'Some answers need attention.'
  if (status === 429) return detail ?? 'Too many assessments in a short time. Please wait a minute and try again.'
  if (status === 503) return detail ?? 'Assessments are temporarily unavailable. Please try again later.'
  if (status >= 500) return 'Something went wrong on the server. Please try again.'
  return detail ?? `The request failed (HTTP ${status}).`
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, {
      ...init,
      headers: { Accept: 'application/json', ...(init.body ? { 'Content-Type': 'application/json' } : {}) },
    })
  } catch {
    throw new ApiError(UNREACHABLE, null)
  }
  let body: unknown = null
  try {
    body = await response.json()
  } catch {
    body = null
  }
  if (!response.ok) {
    const parsed = (body ?? {}) as { detail?: unknown; errors?: ApiFieldError[] }
    const detail = typeof parsed.detail === 'string' ? parsed.detail : undefined
    throw new ApiError(messageForStatus(response.status, detail), response.status, parsed.errors ?? [])
  }
  if (body === null) throw new ApiError('The server sent an unreadable response.', response.status)
  return body as T
}

export function getJson<T>(path: string): Promise<T> {
  return request<T>(path)
}

export function postJson<T>(path: string, payload: unknown): Promise<T> {
  return request<T>(path, { method: 'POST', body: JSON.stringify(payload) })
}

export function fetchApiHealth(): Promise<ApiHealth> {
  return getJson<ApiHealth>('/api/health')
}
