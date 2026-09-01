import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    // Each test gets clean mocks, so one test's stubbed fetch cannot quietly
    // decide the outcome of the next.
    restoreMocks: true,
  },
})
