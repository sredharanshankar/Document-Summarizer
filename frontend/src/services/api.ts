import { ApiError, NetworkError } from '../types/api'

// Empty by default: the Vite dev proxy forwards /api to the backend locally
// (see vite.config.ts). Set VITE_API_BASE_URL for a production build where
// the frontend and backend are on different origins.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

async function parseErrorResponse(response: Response): Promise<never> {
  let code = 'unknown_error'
  let message = 'Something went wrong. Please try again.'
  try {
    const body = await response.json()
    if (typeof body.error === 'string') code = body.error
    if (typeof body.message === 'string') message = body.message
  } catch {
    // Response wasn't JSON (e.g. a proxy/server error page) - fall back to
    // the generic message above rather than leaking raw HTML/text.
  }
  throw new ApiError(response.status, code, message)
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init)
  } catch {
    throw new NetworkError()
  }

  if (!response.ok) {
    return parseErrorResponse(response)
  }

  return (await response.json()) as T
}
