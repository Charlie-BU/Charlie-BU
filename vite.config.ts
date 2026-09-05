import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const apiEnv = loadEnv(mode, process.cwd(), 'API_UPSTREAM_')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    server: {
      proxy: {
        '/api': {
          target: apiEnv.API_UPSTREAM_BASE_URL,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api(?=\/|$)/, '')
        }
      }
    }
  }
})
