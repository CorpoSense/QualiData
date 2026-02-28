import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  server: {
    port: process.env['PORT'] ? parseInt(process.env['PORT'], 10) : 3000,
    // Proxy API requests to FastAPI backend
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist/',
  },
  plugins: [
    vue({
      compilerOptions: {
        isCustomElement: (tag) => tag.startsWith('b-') || tag.includes('modal') || tag.includes('dropdown')
      }
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
})
