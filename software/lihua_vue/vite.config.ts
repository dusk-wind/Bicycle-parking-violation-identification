import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 获取请求前缀
  const env = loadEnv(mode, process.cwd());
  const baseApi = env.VITE_APP_BASE_API
  return {
    plugins: [
      vue(),
      vueJsx(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      port: 90,
      host: true,
      open: true,
      proxy: {
        [baseApi]: {
          target: 'http://localhost:8080',
          changeOrigin: true,
          rewrite: (p:string) => p.replace(baseApi, '')
        },
        // 摄像头API代理到开发板5050端口
        '/camera-api': {
          target: 'http://192.168.76.178:5050',  // 请修改为你的开发板实际IP
          changeOrigin: true,
          rewrite: (p:string) => p.replace('/camera-api', ''),
          logLevel: 'debug'  // 添加调试日志
        }
      }
    },
    css: {
      preprocessorOptions: {
        less: {
          javascriptEnabled: true
        }
      }
    },
    build: {
      outDir: 'dist', // 输出目录
      target: 'esnext', // js格式
      terserOptions: {
        compress: {
          drop_console: true, // 生产环境去掉 console
          drop_debugger: true, // 生产环境去掉 debugger
          dead_code: true // 删除无法访问的代码
        },
      },
      chunkSizeWarningLimit: 2000 // 代码块超过2000 bytes时vite发出警告
    }
  }
})
