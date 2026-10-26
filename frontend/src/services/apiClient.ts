// Central place for talking to the Vytal backend. Components call these
// functions instead of using fetch directly, so URLs and error handling live in one file.

export interface ApiHealth {
  status: string
  app: string
  version: string
}

export class ApiError extends Error {
  readonly status: number | null

  constructor(message: string, status: number | null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function getJson<T>(path: string): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, { headers: { Accept: 'application/json' } })
  } catch {
    throw new ApiError('The Vytal API could not be reached. Is the backend running?', null)
  }
  if (!response.ok) {
    throw new ApiError(`The Vytal API returned an error (HTTP ${response.status}).`, response.status)
  }
  return (await response.json()) as T
}

export function fetchApiHealth(): Promise<ApiHealth> {
  return getJson<ApiHealth>('/api/health')
}
