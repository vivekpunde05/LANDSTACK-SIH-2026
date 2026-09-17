import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendTarget = globalThis.process?.env.VITE_BACKEND_TARGET || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': backendTarget,
      '/demo-assets': backendTarget,
      '/generated': backendTarget,
    },
  },
})
