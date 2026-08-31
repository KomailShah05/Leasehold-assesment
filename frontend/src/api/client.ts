const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

/**
 * Every failure the UI can encounter, in one shape. Components should never
 * see a raw fetch rejection or an HTTP status code.
 */
export type ApiError = {
  kind: 'network' | 'server' | 'invalid'
  message: string
}

export type ApiResult<T> = { ok: true; data: T } | { ok: false; error: ApiError }

async function get<T>(path: string): Promise<ApiResult<T>> {
  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { Accept: 'application/json' },
    })
  } catch {
    return {
      ok: false,
      error: { kind: 'network', message: 'We could not reach the service. Please try again.' },
    }
  }

  if (!response.ok) {
    return {
      ok: false,
      error: { kind: 'server', message: 'Something went wrong at our end. Please try again.' },
    }
  }

  try {
    return { ok: true, data: (await response.json()) as T }
  } catch {
    return {
      ok: false,
      error: { kind: 'invalid', message: 'We received an unexpected response. Please try again.' },
    }
  }
}

export type Health = { status: string }

export function fetchHealth(): Promise<ApiResult<Health>> {
  return get<Health>('/api/health/')
}
