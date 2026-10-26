import { expect, test, type Page } from '@playwright/test'

// These tests use the real backend and trained models. The answers are a
// made-up example profile, not a real person.

async function answer(page: Page, group: string | RegExp, option: string) {
  await page.getByRole('group', { name: group }).getByText(option, { exact: true }).click()
}

async function completeQuestionnaire(page: Page, { withMeasurements = true } = {}) {
  await page.goto('/')
  await page.getByRole('link', { name: /start the assessment/i }).click()
  await page.getByRole('textbox', { name: 'Age' }).fill('62')
  await answer(page, 'Sex', 'Male')
  await page.getByRole('button', { name: /continue/i }).click()
  if (withMeasurements) {
    await page.getByRole('textbox', { name: 'Height', exact: true }).fill('175')
    await page.getByRole('textbox', { name: 'Weight', exact: true }).fill('92')
    await expect(page.getByText('30', { exact: true })).toBeVisible()
  } else {
    await page.getByRole('checkbox', { name: "I don't know my height or weight" }).check()
  }
  await page.getByRole('button', { name: /continue/i }).click()
  await answer(page, 'Do you smoke cigarettes?', 'Every day')
  await answer(page, 'Do you currently use e-cigarettes or vapes?', 'No')
  await answer(page, /physical activity or exercise/, 'No')
  await page.getByRole('button', { name: /continue/i }).click()
  await answer(page, /told you that you have diabetes/, 'Yes')
  await answer(page, /had a stroke/, 'No')
  await answer(page, /kidney disease/, 'No')
  await answer(page, 'Asthma', 'I have never been told I have asthma')
  await page.getByRole('button', { name: /continue/i }).click()
  await expect(page.getByRole('heading', { name: 'Review' })).toBeVisible()
}

test('full assessment returns real model results', async ({ page }) => {
  await completeQuestionnaire(page)
  const [response] = await Promise.all([
    page.waitForResponse((r) => r.url().endsWith('/api/assessment/predict')),
    page.getByRole('button', { name: /see my results/i }).click(),
  ])
  expect(response.status()).toBe(200)
  const body = await response.json()
  expect(body.results.map((r: { status: string }) => r.status)).toEqual(['ok', 'ok'])

  await expect(page).toHaveURL(/\/results$/)
  for (const result of body.results) {
    const card = page.getByRole('region', { name: result.title })
    // The page shows exactly the numbers the API returned.
    await expect(card.getByText(`${(result.estimated_probability * 100).toFixed(1)}%`)).toBeVisible()
    await expect(card.getByText('What moved your estimate')).toBeVisible()
  }
  await expect(page.getByText('Support to stop smoking')).toBeVisible()
  await expect(page.getByText(/Urgent symptoms need care now/)).toBeVisible()
})

test('missing height and weight gives an honest no-estimate state', async ({ page }) => {
  await completeQuestionnaire(page, { withMeasurements: false })
  await page.getByRole('button', { name: /see my results/i }).click()
  await expect(page.getByText('Not enough information')).toHaveCount(2)
})

test('answers survive a page reload and Start over clears them', async ({ page }) => {
  await completeQuestionnaire(page)
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Review' })).toBeVisible()
  await expect(page.getByText('62 years')).toBeVisible()
  await page.getByRole('button', { name: /see my results/i }).click()
  await page.getByRole('button', { name: /start over/i }).click()
  await expect(page).toHaveURL(/\/$/)
  expect(await page.evaluate(() => window.sessionStorage.length)).toBe(0)
})

test('server failure shows a retryable error, not a fake result', async ({ page }) => {
  await completeQuestionnaire(page)
  await page.route('**/api/assessment/predict', (route) => route.abort())
  await page.getByRole('button', { name: /see my results/i }).click()
  await expect(page.getByText('Your results could not be calculated')).toBeVisible()
  await expect(page.getByRole('button', { name: /try again/i })).toBeVisible()
  await expect(page).toHaveURL(/\/assessment$/)
})

test('keyboard-only: the first step can be completed without a mouse', async ({ page }) => {
  await page.goto('/assessment')
  await page.keyboard.press('Tab') // skip link
  await page.getByRole('textbox', { name: 'Age' }).focus()
  await page.keyboard.type('45')
  await page.keyboard.press('Tab') // into the radio group
  await page.keyboard.press('Space')
  await page.keyboard.press('Enter') // submit the step form
  await expect(page.getByRole('heading', { name: 'Height and weight' })).toBeVisible()
})

test('methodology page shows live evaluation figures from the server', async ({ page }) => {
  const status = await (await page.request.get('/api/models/status')).json()
  await page.goto('/methodology')
  for (const model of status.models) {
    await expect(page.getByText(model.evaluation.roc_auc.toFixed(3))).toBeVisible()
  }
})
