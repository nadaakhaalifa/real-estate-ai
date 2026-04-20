import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Configure Vite to use React and Tailwind.
export default defineConfig({
  plugins: [react(), tailwindcss()],
})