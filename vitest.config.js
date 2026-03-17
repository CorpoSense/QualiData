import { defineConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['tests/**/*.spec.js'],
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})