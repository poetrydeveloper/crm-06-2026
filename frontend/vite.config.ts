// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',      // Открывает порт для внутренней сети Docker-оркестрации
    port: 5173,           // Стандартный порт разработки Vite
    watch: {
      usePolling: true,   // Заставляет Vite жестко сканировать файлы, решая проблему кэша Windows/Docker
      interval: 100       // Частота проверки изменений (раз в 100 миллисекунд)
    }
  }
})
