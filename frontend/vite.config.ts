import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// The backend runs on port 8000. Proxying /api through the Vite dev server means
// the browser only ever talks to one origin, so no CORS setup is needed in development.
const BACKEND_URL = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': BACKEND_URL,
    },
  },
  build: {
    // Recharts is large; keep it in its own file so the landing page loads faster.
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/recharts') || id.includes('node_modules/d3-')) return 'charts'
          return undefined
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    css: false,
  },
})
