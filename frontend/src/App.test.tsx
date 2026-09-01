import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, it, vi } from 'vitest'
import App from './App'

/**
 * The journey, driven the way a person drives it: by the names of things on
 * screen rather than by test ids. If a query here stops finding a control, a
 * screen reader user has probably lost it too.
 *
 * Only the network is faked. Everything else is the real components.
 */

const ROUTES = {
  routes: [
    {
      id: 'repairs',
      label: 'Something needs repairing and it is not being fixed',
      legalTerm: 'Repairs, maintenance and disrepair',
    },
  ],
  notSureOption: { id: 'not_sure', label: 'I am not sure which of these fits' },
}

const QUESTION = {
  status: 'question',
  route: ROUTES.routes[0],
  inferred: false,
  question: {
    id: 'repairs_location',
    text: 'Where is the problem?',
    answers: [
      { id: 'inside_flat', label: 'Inside my own flat' },
      { id: 'shared_area', label: 'In a shared part of the building' },
    ],
  },
}

const OUTCOME = {
  status: 'outcome',
  route: ROUTES.routes[0],
  guidance: {
    title: 'Repairs to shared parts of a building',
    summary: 'A possible next step is to report the problem in writing.',
    leaseUrl: 'https://www.lease-advice.org/building-management/repairs/',
  },
}

const ok = (body: unknown) => ({ ok: true, status: 200, json: () => Promise.resolve(body) })

const serve = (...responses: unknown[]) => {
  const fetchMock = vi.fn()
  fetchMock.mockResolvedValueOnce(ok(ROUTES))
  for (const response of responses) fetchMock.mockResolvedValueOnce(ok(response))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

it('walks someone from a scenario to a next step', async () => {
  const user = userEvent.setup()
  serve(QUESTION, OUTCOME)
  render(<App />)

  await user.click(await screen.findByRole('radio', { name: /needs repairing/i }))
  await user.click(screen.getByRole('button', { name: 'Continue' }))

  await user.click(await screen.findByRole('radio', { name: /shared part/i }))
  await user.click(screen.getByRole('button', { name: 'Continue' }))

  expect(await screen.findByRole('heading', { name: /shared parts/i })).toBeDefined()
  expect(screen.getByRole('link', { name: /LEASE website/i })).toBeDefined()
  // The boundary the whole prototype rests on: the result itself carries the
  // disclaimer, not just the page header.
  expect(screen.getByText(/general information to help you find the right guidance/i)).toBeDefined()
})

it('refuses an empty form without troubling the server', async () => {
  const user = userEvent.setup()
  const fetchMock = serve()
  render(<App />)

  await screen.findByRole('radio', { name: /needs repairing/i })
  await user.click(screen.getByRole('button', { name: 'Continue' }))

  expect(await screen.findByText(/choose one of the options/i)).toBeDefined()
  // Only the initial routes call: the empty form never became a request.
  expect(fetchMock).toHaveBeenCalledTimes(1)
})

it('takes focus to the error so it is not missed', async () => {
  const user = userEvent.setup()
  serve()
  render(<App />)

  await screen.findByRole('radio', { name: /needs repairing/i })
  await user.click(screen.getByRole('button', { name: 'Continue' }))

  const error = await screen.findByText(/choose one of the options/i)
  await waitFor(() => expect(document.activeElement).toBe(error))
})

it('offers a way back when the service cannot be reached', async () => {
  const user = userEvent.setup()
  const fetchMock = vi.fn().mockResolvedValueOnce(ok(ROUTES))
  fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'))
  fetchMock.mockResolvedValueOnce(ok(QUESTION))
  vi.stubGlobal('fetch', fetchMock)
  render(<App />)

  await user.click(await screen.findByRole('radio', { name: /needs repairing/i }))
  await user.click(screen.getByRole('button', { name: 'Continue' }))

  const alert = await screen.findByRole('alert')
  expect(alert.textContent).toMatch(/could not reach/i)

  // Retrying resends what they already chose, so nothing is typed twice.
  await user.click(screen.getByRole('button', { name: 'Try again' }))
  expect(await screen.findByRole('heading', { name: /where is the problem/i })).toBeDefined()
})

it('lets someone say we guessed their problem wrongly', async () => {
  const user = userEvent.setup()
  const inferred = {
    ...QUESTION,
    inferred: true,
    question: {
      ...QUESTION.question,
      answers: [
        ...QUESTION.question.answers,
        { id: 'not_my_problem', label: 'This is not what my problem is about' },
      ],
    },
  }
  const fallback = {
    status: 'fallback',
    title: 'We could not match this to one of our topics',
    message: 'This prototype only covers a few common topics.',
    guidance: {
      title: 'Talking to an adviser',
      summary: 'LEASE gives free initial advice.',
      leaseUrl: 'https://www.lease-advice.org/',
    },
  }
  serve(inferred, fallback)
  render(<App />)

  await user.type(
    await screen.findByLabelText(/describe the problem/i),
    'my service charge bill has gone up',
  )
  await user.click(screen.getByRole('button', { name: 'Continue' }))

  // We say plainly that this is a guess rather than presenting it as fact.
  expect(await screen.findByText(/looks like it may be about/i)).toBeDefined()

  await user.click(screen.getByRole('radio', { name: /not what my problem is about/i }))
  await user.click(screen.getByRole('button', { name: 'Continue' }))

  expect(await screen.findByRole('heading', { name: /could not match/i })).toBeDefined()
})

it('clears everything when starting again', async () => {
  const user = userEvent.setup()
  serve(QUESTION, OUTCOME)
  render(<App />)

  await user.click(await screen.findByRole('radio', { name: /needs repairing/i }))
  await user.click(screen.getByRole('button', { name: 'Continue' }))
  await user.click(await screen.findByRole('radio', { name: /shared part/i }))
  await user.click(screen.getByRole('button', { name: 'Continue' }))
  await user.click(await screen.findByRole('button', { name: 'Start again' }))

  const description = await screen.findByLabelText(/describe the problem/i)
  expect((description as HTMLTextAreaElement).value).toBe('')
  expect(screen.getByRole('radio', { name: /needs repairing/i }).getAttribute('checked')).toBeNull()
})
