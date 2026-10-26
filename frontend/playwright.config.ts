import { defineConfig } from '@playwright/test'

// End-to-end tests drive the Microsoft Edge already installed on Windows
// (channel "msedge"), so no browser download is needed (D-019).
// By default they start the REAL backend and the Vite dev server. To test a
// production server instead, start it and set VYTAL_E2E_BASE_URL, e.g.
//   $env:VYTAL_E2E_BASE_URL = "http://127.0.0.1:8000"; npm run test:e2e
const externalBaseUrl = process.env.VYTAL_E2E_BASE_URL

export default defineConfig({
  testDir: './e2e',
  outputDir: './e2e/.results',
  timeout: 60_000,
  // The dev server compiles pages on first visit, which can take several seconds on a laptop.
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: externalBaseUrl ?? 'http://127.0.0.1:5173',
    channel: 'msedge',
    trace: 'retain-on-failure',
  },
  webServer: externalBaseUrl
    ? undefined
    : [
        {
          command: '..\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --app-dir ../backend --host 127.0.0.1 --port 8000',
          url: 'http://127.0.0.1:8000/api/health/ready',
          reuseExistingServer: true,
          timeout: 60_000,
        },
        {
          command: 'npm run dev -- --host 127.0.0.1',
          url: 'http://127.0.0.1:5173',
          reuseExistingServer: true,
          timeout: 60_000,
        },
      ],
})
