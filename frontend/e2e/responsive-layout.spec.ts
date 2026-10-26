import { expect, test } from '@playwright/test'

// Checks that no page scrolls sideways (a common sign of clipped or overflowing
// content) at common screen widths, and saves screenshots for visual review.
const WIDTHS = [1440, 1024, 768, 375]
const PAGES = ['/', '/assessment', '/methodology']

for (const width of WIDTHS) {
  test(`no horizontal overflow at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 })
    for (const path of PAGES) {
      await page.goto(path)
      await page.waitForLoadState('networkidle')
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      expect(overflow, `${path} overflows by ${overflow}px`).toBeLessThanOrEqual(0)
      await page.screenshot({ path: `e2e/.results/screens/${width}${path === '/' ? '-home' : path.replace('/', '-')}.png`, fullPage: true })
    }
  })
}

test('results page layout at desktop and mobile widths', async ({ page }) => {
  await page.goto('/assessment')
  const request = {
    age_years: 62, sex: 'male', height_cm: 175, weight_kg: 92, smoking_status: 'current_daily', ecigarette_current_use: 'no',
    physical_activity_past_30_days: 'no', diabetes_status: 'yes', stroke_history: 'no', kidney_disease_history: 'no', asthma_status: 'never',
  }
  const result = await (await page.request.post('/api/assessment/predict', { data: request })).json()
  await page.evaluate((saved) => window.sessionStorage.setItem('vytal.assessment.v1', JSON.stringify(saved)), { result, stepIndex: 4 })
  for (const width of [1440, 375]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/results')
    await page.waitForLoadState('networkidle')
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
    expect(overflow).toBeLessThanOrEqual(0)
    await page.screenshot({ path: `e2e/.results/screens/${width}-results.png`, fullPage: true })
  }
})
