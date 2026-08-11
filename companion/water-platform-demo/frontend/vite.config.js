import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';

// 与第4章"构建与性能优化"呼应:第三方依赖单独分包,
// 业务页面配合路由懒加载(见 router/index.js 的动态 import)按需加载。
export default defineConfig({
  plugins: [vue()],
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
