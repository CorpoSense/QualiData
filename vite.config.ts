import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  server: {
    port: process.env['PORT'] ? parseInt(process.env['PORT'], 10) : 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  appType: 'spa',
  build: {
    outDir: 'dist/',
    assetsDir: 'assets',
    target: 'esnext',
    minify: 'esbuild'
  },
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
})
