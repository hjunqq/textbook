import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';

// 与第4章"构建与性能优化"呼应:第三方依赖单独分包,
// 业务页面配合路由懒加载(见 router/index.js 的动态 import)按需加载。
export default defineConfig({
  plugins: [vue()],
  // 开发时把 /api 转发到教学接口或本地后端（两者同为 8080，可互换）
  server: { proxy: { '/api': { target: process.env.VITE_PROXY_TARGET || 'http://localhost:8080', changeOrigin: true } } },
  // 测试环境：lesson44/lesson45 的用例要操作 document，必须跑在 jsdom 下。
  // 不写这一段时 vitest 默认用 node 环境，那些用例会以 document is not defined 失败——
  // 纯函数用例（readings、auth、lesson84）在 jsdom 下同样正常。
  test: { environment: 'jsdom' },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) return 'vendor';
        },
      },
    },
  },
});
