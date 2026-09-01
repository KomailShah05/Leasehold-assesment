import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchRoutes, submitTriage } from './client'

/**
 * The client turns every kind of failure into one shape, so the UI has a single
 * error path. These tests describe what a person ends up being told, which is
 * the part that matters: the wording is what they read.
 */

const respondWith = (status: number, body: unknown) =>
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(body),
    }),
  )

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('successful calls', () => {
  it('returns the parsed body', async () => {
    respondWith(200, { status: 'fallback', title: 'x', message: 'y', guidance: null })

    const result = await submitTriage({ scenario: 'not_sure' })

    expect(result.ok).toBe(true)
    if (result.ok) expect(result.data.status).toBe('fallback')
  })

  it('sends a GET with no body when fetching routes', async () => {
    respondWith(200, { routes: [], notSureOption: { id: 'not_sure', label: 'x' } })

    await fetchRoutes()

    const [, init] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
    expect(init.method).toBe('GET')
    expect(init.body).toBeUndefined()
  })
})

describe('failures', () => {
  it('passes on the server’s wording for input it rejected', async () => {
    // A 400 is about what the person entered, so the server's message is safe
    // to show them and more specific than anything we could write here.
    respondWith(400, { status: 'error', message: 'Please choose one of the options shown.' })

    const result = await submitTriage({ scenario: 'repairs', answerId: 'banana' })

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.kind).toBe('invalid')
      expect(result.error.message).toBe('Please choose one of the options shown.')
    }
  })

  it('uses our own wording for a server fault', async () => {
    // Whatever went wrong at our end is not the person's problem to understand.
    respondWith(500, { detail: 'ValueError at /api/triage/' })

    const result = await submitTriage({ scenario: 'repairs' })

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.kind).toBe('server')
      expect(result.error.message).not.toContain('ValueError')
    }
  })

  it('reports a dropped connection in plain English', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    const result = await submitTriage({ scenario: 'repairs' })

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.kind).toBe('network')
      expect(result.error.message).toMatch(/could not reach/i)
    }
  })

  it('says so when the service is too slow rather than waiting forever', async () => {
    const timeout = new DOMException('The operation timed out.', 'TimeoutError')
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(timeout))

    const result = await submitTriage({ scenario: 'repairs' })

    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.message).toMatch(/longer than expected/i)
  })

  it('gives up on a response it cannot read', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.reject(new SyntaxError('Unexpected token')),
      }),
    )

    const result = await submitTriage({ scenario: 'repairs' })

    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.kind).toBe('server')
  })

  it('sets a timeout on every request', async () => {
    respondWith(200, { routes: [], notSureOption: { id: 'not_sure', label: 'x' } })

    await fetchRoutes()

    const [, init] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
    expect(init.signal).toBeInstanceOf(AbortSignal)
  })
})
