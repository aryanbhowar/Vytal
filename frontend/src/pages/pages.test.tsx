import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { STORAGE_KEY } from '../context/AssessmentContext'
import { TEST_FIXTURE_RESPONSE } from '../test/fixtures'
import { renderApp } from '../test/renderWithProviders'

function mockFetch(handler: (url: string, init?: RequestInit) => Response | Promise<Response>) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation((input, init) => Promise.resolve(handler(String(input), init)))
}

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })

async function fillToReview(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText('Age'), '50')
  await user.click(screen.getByLabelText('Female'))
  await user.click(screen.getByRole('button', { name: /continue/i }))
  await user.type(screen.getByLabelText('Height'), '165')
  await user.type(screen.getByLabelText('Weight'), '68')
  await user.click(screen.getByRole('button', { name: /continue/i }))
  for (const [group, answer] of [
    ['Do you smoke cigarettes?', 'Never'],
    ['Do you currently use e-cigarettes or vapes?', 'No'],
    [/physical activity or exercise/, 'Yes'],
  ] as const) {
    await user.click(within(screen.getByRole('group', { name: group })).getByLabelText(answer))
  }
  await user.click(screen.getByRole('button', { name: /continue/i }))
  for (const [group, answer] of [
    [/told you that you have diabetes/, 'No'],
    [/had a stroke/, 'No'],
    [/kidney disease/, 'No'],
    ['Asthma', 'I have never been told I have asthma'],
  ] as const) {
    await user.click(within(screen.getByRole('group', { name: group })).getByLabelText(answer))
  }
  await user.click(screen.getByRole('button', { name: /continue/i }))
}

describe('Landing page', () => {
  it('shows the disclaimer and links the main action to the assessment', async () => {
    mockFetch(() => json({ models: [] }))
    renderApp('/')
    expect(screen.getByText('Not a diagnosis.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /start the assessment/i })).toHaveAttribute('href', '/assessment')
    await waitFor(() => expect(screen.getByText(/could not be loaded/i)).toBeInTheDocument())
  })
})

describe('Assessment questionnaire', () => {
  it('blocks progress and explains missing answers beside the field', async () => {
    const user = userEvent.setup()
    renderApp('/assessment')
    await user.click(screen.getByRole('button', { name: /continue/i }))
    expect(screen.getByText('Enter your age in years.')).toBeInTheDocument()
    expect(screen.getByText('Please choose an answer.')).toBeInTheDocument()
    expect(screen.getByLabelText('Age')).toHaveAttribute('aria-invalid', 'true')
  })

  it('keeps answers when moving back and forward, and saves them for the tab', async () => {
    const user = userEvent.setup()
    renderApp('/assessment')
    await user.type(screen.getByLabelText('Age'), '50')
    await user.click(screen.getByLabelText('Female'))
    await user.click(screen.getByRole('button', { name: /continue/i }))
    expect(screen.getByRole('heading', { name: 'Height and weight' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /back/i }))
    expect(screen.getByLabelText('Age')).toHaveValue('50')
    expect(screen.getByLabelText('Female')).toBeChecked()
    expect(JSON.parse(window.sessionStorage.getItem(STORAGE_KEY) ?? '{}').values.ageYears).toBe('50')
  })

  it('shows a derived BMI preview', async () => {
    const user = userEvent.setup()
    renderApp('/assessment', { stepIndex: 1 })
    await user.type(screen.getByLabelText('Height'), '180')
    await user.type(screen.getByLabelText('Weight'), '81')
    expect(screen.getByText('25')).toBeInTheDocument()
    expect(screen.getByText(/Overweight/)).toBeInTheDocument()
  })

  it('sends the answers to the API and shows a retryable error when the server is unreachable', async () => {
    const user = userEvent.setup()
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('network down'))
    renderApp('/assessment')
    await fillToReview(user)
    expect(screen.getByRole('heading', { name: 'Review' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /see my results/i }))
    expect(await screen.findByText('Your results could not be calculated')).toBeInTheDocument()
    expect(screen.getByText(/could not reach its server/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()

    const [url, init] = fetchSpy.mock.calls[0]
    expect(url).toBe('/api/assessment/predict')
    expect(JSON.parse(String(init?.body))).toEqual({
      age_years: 50, sex: 'female', height_cm: 165, weight_kg: 68, smoking_status: 'never', ecigarette_current_use: 'no',
      physical_activity_past_30_days: 'yes', diabetes_status: 'no', stroke_history: 'no', kidney_disease_history: 'no',
      asthma_status: 'never',
    })
  })

  it('shows the server validation message on a 422', async () => {
    const user = userEvent.setup()
    mockFetch(() => json({ detail: 'Some answers need attention.', errors: [{ field: 'age_years', message: 'Must be at least 18.' }] }, 422))
    renderApp('/assessment')
    await fillToReview(user)
    await user.click(screen.getByRole('button', { name: /see my results/i }))
    expect(await screen.findByText('age_years: Must be at least 18.')).toBeInTheDocument()
  })
})

describe('Results page (TEST FIXTURE data)', () => {
  it('redirects to the assessment when there is no result', () => {
    renderApp('/results')
    expect(screen.getByRole('heading', { name: 'About you' })).toBeInTheDocument()
  })

  it('renders available, unavailable and suggestion states from a response', () => {
    mockFetch(() => json({ models: [] }))
    renderApp('/results', { result: TEST_FIXTURE_RESPONSE, stepIndex: 4 })
    const heart = screen.getByRole('region', { name: /Heart: coronary heart disease/ })
    expect(within(heart).getByText('25.0%')).toBeInTheDocument()
    expect(within(heart).getByText('7.0%')).toBeInTheDocument()
    expect(within(heart).getAllByText('High').length).toBeGreaterThan(0)
    expect(within(heart).getByText(/Smoking/)).toBeInTheDocument()

    const lungs = screen.getByRole('region', { name: /Lungs/ })
    expect(within(lungs).getByText('Estimate unavailable')).toBeInTheDocument()
    expect(within(lungs).queryByText('%')).not.toBeInTheDocument()

    expect(screen.getByText('TEST FIXTURE urgent notice')).toBeInTheDocument()
    expect(screen.getByText('TEST FIXTURE stop smoking')).toBeInTheDocument()
    expect(screen.getByText(/derived from height and weight/)).toBeInTheDocument()
  })

  it('renders the insufficient-input state honestly', () => {
    const insufficient = {
      ...TEST_FIXTURE_RESPONSE,
      results: TEST_FIXTURE_RESPONSE.results.map((r) => ({
        ...r, status: 'insufficient_input' as const, estimated_probability: null, category: null, percentile: null,
        message: 'This estimate needs your height and weight (to calculate BMI). Vytal does not guess missing values.',
      })),
    }
    renderApp('/results', { result: insufficient })
    expect(screen.getAllByText('Not enough information')).toHaveLength(2)
  })

  it('Start over clears saved answers and results', async () => {
    const user = userEvent.setup()
    mockFetch(() => json({ models: [] }))
    renderApp('/results', { result: TEST_FIXTURE_RESPONSE, stepIndex: 4 })
    await user.click(screen.getByRole('button', { name: /start over/i }))
    expect(window.sessionStorage.getItem(STORAGE_KEY)).toBeNull()
    expect(screen.getByRole('heading', { level: 1, name: /Understand how your answers compare/ })).toBeInTheDocument()
  })
})
