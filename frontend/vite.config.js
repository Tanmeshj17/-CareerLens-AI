import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    // Minify with esbuild (default, fast)
    minify: 'esbuild',
    // Inline small assets directly into CSS/JS to save requests
    assetsInlineLimit: 4096,
    rollupOptions: {
      output: {
        // Aggressive code splitting — each lazy page is its own chunk
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react-dom') || id.includes('react-router-dom')) {
              return 'react-vendor'
            }
            if (id.includes('recharts') || id.includes('d3-')) {
              return 'charts'
            }
            return 'vendor'
          }
        }
      }
    },
    chunkSizeWarningLimit: 800,
  },
  // Cache busting — assets get content hashes in filenames
  server: {
    headers: {
      'Cache-Control': 'public, max-age=31536000, immutable',
    }
  }
})

