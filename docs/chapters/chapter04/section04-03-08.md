# 使用Vite创建Vue 3.0项目

Vite是一个由Vue.js团队开发的新一代前端构建工具，它提供了更快的开发服务器启动和更快的模块热更新。本节将介绍如何使用Vite创建Vue 3.0项目，并提供智慧水利平台开发中的最佳实践。

## 创建Vue 3项目的基本步骤

### 1. 使用Vite脚手架创建项目

```bash
# 使用npm
npm create vite@latest smart-water-resources-vue3 -- --template vue

# 或使用yarn
yarn create vite smart-water-resources-vue3 --template vue

# 或使用pnpm
pnpm create vite smart-water-resources-vue3 -- --template vue
```

### 2. 安装依赖并启动项目

```bash
cd smart-water-resources-vue3
npm install
npm run dev
```

### 3. 项目目录结构

创建的基本项目结构如下：

```
smart-water-resources-vue3/
├── public/              # 静态资源目录
│   └── favicon.ico      # 网站图标
├── src/                 # 源代码目录
│   ├── assets/          # 资源文件
│   │   └── logo.png     # Vue logo
│   ├── components/      # 组件目录
│   │   └── HelloWorld.vue  # 示例组件
│   ├── App.vue          # 根组件
│   ├── main.js          # 入口文件
│   └── style.css        # 全局样式
├── index.html           # HTML模板
├── package.json         # 项目配置文件
├── vite.config.js       # Vite配置文件
└── README.md            # 项目说明文档
```

## 扩展基础项目

智慧水利平台通常需要一些额外的功能，下面介绍如何扩展基础项目。

### 1. 添加Vue Router

```bash
npm install vue-router@4
```

在`src`目录下创建`router`文件夹和`router/index.js`文件：

```javascript
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/monitoring',
    name: 'WaterMonitoring',
    // 使用懒加载减少首屏加载时间
    component: () => import('../views/WaterMonitoring.vue')
  },
  {
    path: '/reservoirs',
    name: 'ReservoirManagement',
    component: () => import('../views/ReservoirManagement.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

在`main.js`中引入路由：

```javascript
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

createApp(App)
  .use(router)
  .mount('#app')
```

### 2. 添加Pinia状态管理

```bash
npm install pinia
```

在`src`目录下创建`stores`文件夹和`stores/waterData.js`文件：

```javascript
// src/stores/waterData.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useWaterDataStore = defineStore('waterData', () => {
  // 状态
  const waterLevels = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  
  // 计算属性
  const highRiskStations = computed(() => {
    return waterLevels.value.filter(station => station.level > station.warningLevel)
  })
  
  // 动作
  async function fetchWaterLevels() {
    isLoading.value = true
    error.value = null
    try {
      const response = await axios.get('/api/water-levels')
      waterLevels.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('获取水位数据失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    waterLevels,
    isLoading,
    error,
    highRiskStations,
    fetchWaterLevels
  }
})
```

在`main.js`中引入Pinia：

```javascript
// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

### 3. 添加Element Plus UI组件库

```bash
npm install element-plus
```

在`main.js`中引入Element Plus：

```javascript
// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

## 项目配置优化

对于智慧水利平台，我们需要进一步优化Vite配置。

### 1. 增强vite.config.js

```javascript
// vite.config.js
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  
  return {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8080',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    },
    plugins: [
      vue(),
      // 自动导入Element Plus组件
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
    build: {
      // 生产环境构建配置
      rollupOptions: {
        output: {
          manualChunks: {
            vue: ['vue', 'vue-router', 'pinia'],
            elementplus: ['element-plus'],
          }
        }
      },
      // 关闭生产环境sourceMap
      sourcemap: mode !== 'production'
    }
  }
})
```

### 2. 环境变量配置

创建以下环境配置文件：

```
# .env
VITE_APP_TITLE=智慧水利平台

# .env.development
VITE_API_URL=http://localhost:8080
VITE_APP_ENV=development

# .env.production
VITE_API_URL=https://api.water-resources-platform.com
VITE_APP_ENV=production
```

## 智慧水利平台Vue 3组件示例

### 水位监测组件

```vue
<!-- src/components/WaterLevelMonitor.vue -->
<template>
  <div class="water-level-monitor">
    <el-card class="monitor-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h3>{{ station.name }} 水位监测</h3>
          <el-tag :type="alertLevelType">{{ alertLevelText }}</el-tag>
        </div>
      </template>
      
      <div class="current-level">
        <div class="level-value">{{ waterLevel }}m</div>
        <div class="level-indicator">
          <div 
            class="water-bar" 
            :style="{ height: waterLevelPercentage + '%', backgroundColor: waterLevelColor }"
          ></div>
        </div>
      </div>
      
      <div class="info-rows">
        <div class="info-row">
          <span class="label">警戒水位:</span>
          <span class="value">{{ station.warningLevel }}m</span>
        </div>
        <div class="info-row">
          <span class="label">更新时间:</span>
          <span class="value">{{ formattedUpdateTime }}</span>
        </div>
      </div>
      
      <el-button type="primary" @click="refreshData" :loading="loading">
        刷新数据
      </el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 组件属性
const props = defineProps({
  station: {
    type: Object,
    required: true
  }
})

// 响应式状态
const waterLevel = ref(0)
const lastUpdateTime = ref(null)
const loading = ref(false)

// 计算属性
const waterLevelPercentage = computed(() => {
  const percentage = (waterLevel.value / props.station.maxLevel) * 100
  return Math.min(percentage, 100)
})

const waterLevelColor = computed(() => {
  if (waterLevel.value >= props.station.warningLevel) {
    return '#F56C6C' // 红色 - 危险
  } else if (waterLevel.value >= props.station.warningLevel * 0.9) {
    return '#E6A23C' // 橙色 - 警告
  }
  return '#67C23A' // 绿色 - 安全
})

const alertLevelType = computed(() => {
  if (waterLevel.value >= props.station.warningLevel) {
    return 'danger'
  } else if (waterLevel.value >= props.station.warningLevel * 0.9) {
    return 'warning'
  }
  return 'success'
})

const alertLevelText = computed(() => {
  if (waterLevel.value >= props.station.warningLevel) {
    return '超警戒水位'
  } else if (waterLevel.value >= props.station.warningLevel * 0.9) {
    return '接近警戒水位'
  }
  return '水位正常'
})

const formattedUpdateTime = computed(() => {
  if (!lastUpdateTime.value) return '暂无数据'
  return new Date(lastUpdateTime.value).toLocaleString()
})

// 方法
async function fetchData() {
  loading.value = true
  try {
    // 这里应该替换为实际的API调用
    // const response = await fetch(`/api/stations/${props.station.id}/water-level`)
    // const data = await response.json()
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    const data = {
      waterLevel: Math.random() * (props.station.maxLevel - props.station.minLevel) + props.station.minLevel,
      timestamp: new Date().toISOString()
    }
    
    waterLevel.value = data.waterLevel
    lastUpdateTime.value = data.timestamp
    
    // 检查是否超过警戒水位
    if (waterLevel.value >= props.station.warningLevel) {
      ElMessage.warning(`警告: ${props.station.name}水位已超过警戒线!`)
    }
  } catch (error) {
    console.error('获取水位数据失败:', error)
    ElMessage.error('获取水位数据失败')
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  await fetchData()
}

// 生命周期钩子
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.water-level-monitor {
  width: 300px;
}

.monitor-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
}

.current-level {
  display: flex;
  align-items: center;
  margin: 20px 0;
}

.level-value {
  font-size: 24px;
  font-weight: bold;
  width: 50%;
  text-align: center;
}

.level-indicator {
  width: 50%;
  height: 100px;
  background-color: #EBEEF5;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.water-bar {
  position: absolute;
  bottom: 0;
  width: 100%;
  transition: height 0.5s, background-color 0.5s;
}

.info-rows {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.label {
  color: #909399;
}

.value {
  font-weight: 500;
}
</style>
```

## 迁移Vue 2项目到Vue 3

如果你有现有的Vue 2智慧水利平台项目需要迁移到Vue 3，可以参考以下步骤：

1. **使用官方迁移构建**：Vue 3提供了兼容Vue 2 API的迁移构建版本
2. **更新依赖**：将Vue相关包更新到Vue 3版本
3. **API变更**：逐步将选项式API迁移到组合式API
4. **更新路由和状态管理**：从Vue Router 3迁移到Vue Router 4，从Vuex迁移到Pinia
5. **更新UI组件库**：如从Element UI迁移到Element Plus

详细的迁移指南可以参考Vue官方文档：https://v3-migration.vuejs.org/

## 结语

使用Vite创建Vue 3项目为智慧水利平台开发带来了更高效的开发体验。Composition API的逻辑组织方式、更好的TypeScript支持以及更快的构建工具链，都能帮助开发团队构建更易维护、性能更好的水利信息系统。 

## 思考题与练习

### 基础题

1. 请简述本节的核心概念，并说明其在智慧水利平台开发中的重要性。
2. 总结本节介绍的主要技术方法，并分析各方法的适用场景。
3. 结合智慧水利的实际需求，解释本节内容如何应用于实际项目中。

### 提高题

4. 分析本节涉及的技术难点，并提出可能的解决方案。
5. 比较本节介绍的不同方法的优缺点，并给出选择建议。
6. 设计一个简单的案例，说明如何将本节理论应用于智慧水利系统设计。

### 讨论题

7. 讨论本节内容与其他相关技术的集成方案，分析可能遇到的挑战。
8. 展望本节涉及技术的发展趋势，分析其对智慧水利未来发展的影响。

## 本节小结

本节内容为智慧水利平台的设计和开发提供了重要的理论基础和技术指导。通过学习本节内容，学生应能够理解相关概念的内涵和应用价值，掌握基本的分析方法和设计原则，为后续章节的学习和实际项目的开展奠定坚实基础。
