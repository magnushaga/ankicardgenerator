import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      '/api': 'http://localhost:5000'
    },
    allowedHosts: 'all'
  },
  resolve: {
    alias: {
      '@mui/icons-material': '@mui/icons-material/esm',
    },
  },
  optimizeDeps: {
    include: ['@mui/material', '@mui/icons-material'],
  },
})
