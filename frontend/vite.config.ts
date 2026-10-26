import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

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
})
