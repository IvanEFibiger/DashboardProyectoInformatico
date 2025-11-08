import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
      resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"), 
    },
  },
    proxy: {
      '/login': 'http://127.0.0.1:5500',
      '/usuarios': 'http://127.0.0.1:5500'
    }
  }
})