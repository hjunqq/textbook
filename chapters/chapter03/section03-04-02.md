# 前端开发环境配置

> 本小节是[第四节 开发环境配置与工具使用](section03-04.md)的一部分

前端开发是智慧水利平台建设的重要组成部分，负责构建用户与系统交互的界面，包括水情监测看板、GIS地图展示、数据可视化分析等关键功能。本小节将详细介绍智慧水利平台前端开发环境的配置方法，涵盖Node.js环境搭建、前端构建工具配置以及Vue.js开发环境等内容。

## 3.4.2.1 Node.js环境搭建

Node.js是现代前端开发的基础环境，用于运行JavaScript构建工具和开发服务器。在智慧水利平台开发中，正确配置Node.js环境是前端开发的第一步。

### Node.js版本选择

不同的前端项目可能需要不同版本的Node.js：

- **LTS版本**：长期支持版本，稳定性好，适合生产环境，推荐用于大多数智慧水利平台项目
- **Current版本**：最新特性版本，包含新功能，但可能不够稳定
- **特定版本**：某些项目可能指定使用特定版本，以确保兼容性

**版本选择建议**：
- 对于新项目，优先选择最新的LTS版本
- 对于现有项目，查看项目文档或package.json中的推荐版本

### Node.js安装方法

**Windows环境**：

1. 官方安装包安装：
   ```bash
   # 1. 从Node.js官网下载安装包
   # 2. 运行安装程序，按照提示完成安装
   # 3. 验证安装
   node -v
   npm -v
   ```

2. 使用nvm-windows管理多版本：
   ```bash
   # 1. 从GitHub下载nvm-windows
   # 2. 安装nvm
   # 3. 安装和使用特定版本的Node.js
   nvm install 16.15.0
   nvm use 16.15.0
   ```

**Linux环境**：

1. 使用包管理器安装：
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
   sudo apt-get install -y nodejs

   # CentOS/RHEL
   curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash -
   sudo yum install -y nodejs
   ```

2. 使用nvm管理多版本：
   ```bash
   # 1. 安装nvm
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
   # 2. 安装和使用特定版本的Node.js
   nvm install 16.15.0
   nvm use 16.15.0
   ```

**macOS环境**：

1. 使用Homebrew安装：
   ```bash
   brew install node
   ```

2. 使用nvm管理多版本：
   ```bash
   brew install nvm
   nvm install 16.15.0
   nvm use 16.15.0
   ```

### npm配置与优化

npm是Node.js的包管理器，合理配置npm可以提高开发效率：

1. **设置镜像源**：在国内环境下，使用淘宝npm镜像可以加速包下载：
   ```bash
   # 设置淘宝镜像
   npm config set registry https://registry.npmmirror.com
   ```

2. **全局依赖**：安装常用的全局开发工具：
   ```bash
   # 安装Vue CLI
   npm install -g @vue/cli
   # 安装Vite
   npm install -g create-vite
   # 安装常用工具
   npm install -g npm-check-updates rimraf serve
   ```

3. **npm缓存优化**：
   ```bash
   # 清理缓存
   npm cache clean --force
   # 设置缓存路径(可选)
   npm config set cache D:\npm-cache --global
   ```

4. **团队项目的.npmrc配置**：在项目根目录创建.npmrc文件，统一团队npm配置：
   ```
   registry=https://registry.npmmirror.com
   save-exact=true
   engine-strict=true
   ```

### 包管理器选择

除了npm，还有其他包管理器可供选择：

- **yarn**：Facebook开发的替代npm的包管理器，提供更好的性能和确定性
- **pnpm**：节省磁盘空间并提高安装速度的包管理器

**选择建议**：
- 对于新项目，可以考虑使用pnpm，它具有更好的性能和磁盘空间利用率
- 对于现有项目，建议遵循项目已使用的包管理器

**pnpm安装与配置**：
```bash
# 安装pnpm
npm install -g pnpm

# 配置镜像
pnpm config set registry https://registry.npmmirror.com

# 使用pnpm安装依赖
pnpm install
```

## 3.4.2.2 前端构建工具配置

前端构建工具负责代码转换、打包、压缩和优化等任务，对于现代智慧水利平台前端开发至关重要。

### 常用构建工具概述

- **Webpack**：功能强大的模块打包器，生态完善，适用于复杂项目
- **Vite**：基于ESM的构建工具，开发服务器启动快，HMR性能优秀
- **Rollup**：专注于JavaScript库的打包，生成高效的输出文件
- **Parcel**：零配置的Web应用打包工具，适合快速原型开发

**选择建议**：
- 对于新的智慧水利平台项目，推荐使用Vite，可获得更好的开发体验
- 对于复杂的现有项目，Webpack仍是稳定可靠的选择

### Webpack配置

对于基于Webpack的智慧水利平台前端项目，以下是常用的配置：

1. **基本配置**：webpack.config.js示例：
   ```javascript
   const path = require('path');
   const HtmlWebpackPlugin = require('html-webpack-plugin');
   const MiniCssExtractPlugin = require('mini-css-extract-plugin');
   
   module.exports = {
     entry: './src/main.js',
     output: {
       path: path.resolve(__dirname, 'dist'),
       filename: 'js/[name].[contenthash].js',
       clean: true
     },
     module: {
       rules: [
         {
           test: /\.js$/,
           exclude: /node_modules/,
           use: {
             loader: 'babel-loader'
           }
         },
         {
           test: /\.css$/,
           use: [MiniCssExtractPlugin.loader, 'css-loader']
         },
         {
           test: /\.(png|svg|jpg|jpeg|gif)$/i,
           type: 'asset/resource',
           generator: {
             filename: 'images/[hash][ext][query]'
           }
         }
       ]
     },
     plugins: [
       new HtmlWebpackPlugin({
         template: './public/index.html'
       }),
       new MiniCssExtractPlugin({
         filename: 'css/[name].[contenthash].css'
       })
     ],
     resolve: {
       alias: {
         '@': path.resolve(__dirname, 'src')
       }
     }
   };
   ```

2. **开发环境配置**：webpack.dev.js示例：
   ```javascript
   const { merge } = require('webpack-merge');
   const common = require('./webpack.common.js');
   
   module.exports = merge(common, {
     mode: 'development',
     devtool: 'eval-source-map',
     devServer: {
       static: './dist',
       hot: true,
       port: 3000,
       proxy: {
         '/api': {
           target: 'http://localhost:8080',
           changeOrigin: true
         }
       }
     }
   });
   ```

3. **生产环境配置**：webpack.prod.js示例：
   ```javascript
   const { merge } = require('webpack-merge');
   const common = require('./webpack.common.js');
   const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
   const TerserPlugin = require('terser-webpack-plugin');
   
   module.exports = merge(common, {
     mode: 'production',
     optimization: {
       minimizer: [
         new CssMinimizerPlugin(),
         new TerserPlugin()
       ],
       splitChunks: {
         chunks: 'all',
         cacheGroups: {
           vendor: {
             test: /[\\/]node_modules[\\/]/,
             name: 'vendors',
             chunks: 'all'
           }
         }
       }
     }
   });
   ```

### Vite配置

Vite是新一代前端构建工具，特别适合智慧水利平台这类需要快速开发迭代的项目：

1. **项目创建**：
   ```bash
   # 使用npm
   npm create vite@latest my-water-platform -- --template vue
   
   # 使用yarn
   yarn create vite my-water-platform --template vue
   
   # 使用pnpm
   pnpm create vite my-water-platform --template vue
   ```

2. **基本配置**：vite.config.js示例：
   ```javascript
   import { defineConfig } from 'vite'
   import vue from '@vitejs/plugin-vue'
   import path from 'path'
   
   export default defineConfig({
     plugins: [vue()],
     resolve: {
       alias: {
         '@': path.resolve(__dirname, 'src'),
       },
     },
     server: {
       port: 3000,
       proxy: {
         '/api': {
           target: 'http://localhost:8080',
           changeOrigin: true,
           rewrite: (path) => path.replace(/^\/api/, '')
         }
       }
     },
     build: {
       outDir: 'dist',
       assetsDir: 'assets',
       sourcemap: false,
       rollupOptions: {
         output: {
           manualChunks: {
             'vendor': ['vue', 'vue-router', 'pinia'],
             'echarts': ['echarts']
           }
         }
       }
     }
   })
   ```

3. **常用插件配置**：
   ```javascript
   // vite.config.js
   import { defineConfig } from 'vite'
   import vue from '@vitejs/plugin-vue'
   import vueJsx from '@vitejs/plugin-vue-jsx'
   import legacy from '@vitejs/plugin-legacy'
   import Components from 'unplugin-vue-components/vite'
   import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'
   
   export default defineConfig({
     plugins: [
       vue(),
       vueJsx(),
       legacy({
         targets: ['defaults', 'not IE 11']
       }),
       Components({
         resolvers: [AntDesignVueResolver()]
       })
     ]
   })
   ```

### 其他构建流程优化

1. **ESLint配置**：代码质量检查工具：
   ```javascript
   // .eslintrc.js
   module.exports = {
     root: true,
     env: {
       node: true,
       browser: true,
     },
     extends: [
       'plugin:vue/vue3-recommended',
       'eslint:recommended'
     ],
     rules: {
       'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
       'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
     }
   }
   ```

2. **Prettier配置**：代码格式化工具：
   ```javascript
   // .prettierrc.js
   module.exports = {
     semi: true,
     singleQuote: true,
     printWidth: 80,
     tabWidth: 2,
     trailingComma: 'es5',
     arrowParens: 'always'
   }
   ```

3. **TypeScript配置**：类型检查配置：
   ```javascript
   // tsconfig.json
   {
     "compilerOptions": {
       "target": "esnext",
       "module": "esnext",
       "moduleResolution": "node",
       "strict": true,
       "jsx": "preserve",
       "sourceMap": true,
       "resolveJsonModule": true,
       "esModuleInterop": true,
       "baseUrl": ".",
       "paths": {
         "@/*": ["src/*"]
       },
       "lib": ["esnext", "dom"]
     },
     "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
     "exclude": ["node_modules"]
   }
   ```

## 3.4.2.3 Vue.js开发环境

Vue.js是智慧水利平台前端开发的常用框架，以下是Vue.js开发环境的配置方法。

### Vue CLI配置

Vue CLI是Vue.js的官方脚手架工具，适用于基于Vue.js的智慧水利平台项目：

1. **安装Vue CLI**：
   ```bash
   npm install -g @vue/cli
   ```

2. **创建项目**：
   ```bash
   vue create water-monitoring-platform
   ```

3. **项目配置选项**：
   - 选择Vue版本(推荐Vue 3)
   - 选择Babel、Router、Vuex、CSS预处理器、Linter等功能
   - 选择是否使用TypeScript
   - 选择CSS预处理器(SCSS/LESS/Stylus)
   - 选择Linter配置
   - 选择配置文件位置

4. **vue.config.js配置**：
   ```javascript
   const { defineConfig } = require('@vue/cli-service')
   
   module.exports = defineConfig({
     transpileDependencies: true,
     publicPath: process.env.NODE_ENV === 'production' ? '/water-platform/' : '/',
     productionSourceMap: false,
     devServer: {
       port: 3000,
       proxy: {
         '/api': {
           target: 'http://localhost:8080',
           changeOrigin: true,
           pathRewrite: {
             '^/api': ''
           }
         }
       }
     },
     configureWebpack: {
       optimization: {
         splitChunks: {
           chunks: 'all',
           cacheGroups: {
             vendors: {
               name: 'chunk-vendors',
               test: /[\\/]node_modules[\\/]/,
               priority: 10,
               chunks: 'initial'
             },
             echarts: {
               name: 'chunk-echarts',
               priority: 20,
               test: /[\\/]node_modules[\\/]echarts[\\/]/
             },
             commons: {
               name: 'chunk-commons',
               minChunks: 2,
               priority: 5,
               chunks: 'initial',
               reuseExistingChunk: true
             }
           }
         }
       }
     }
   })
   ```

### Vue 3 + Vite环境配置

对于新项目，Vue 3 + Vite组合是更好的选择：

1. **创建Vue 3 + Vite项目**：
   ```bash
   npm create vite@latest water-platform -- --template vue
   # 或使用pnpm
   pnpm create vite water-platform --template vue
   ```

2. **安装必要依赖**：
   ```bash
   cd water-platform
   npm install
   
   # 安装路由
   npm install vue-router@4
   
   # 安装状态管理
   npm install pinia
   
   # 安装UI组件库
   npm install ant-design-vue@3
   ```

3. **配置项目结构**：
   ```
   water-platform/
   ├── public/
   │   ├── favicon.ico
   │   └── static/
   ├── src/
   │   ├── assets/
   │   │   ├── icons/
   │   │   └── images/
   │   ├── components/
   │   │   ├── common/
   │   │   ├── charts/
   │   │   ├── map/
   │   │   └── monitor/
   │   ├── constants/
   │   │   └── index.js
   │   ├── hooks/
   │   │   ├── useSocket.js
   │   │   └── useStationData.js
   │   ├── layouts/
   │   │   ├── MainLayout.vue
   │   │   └── components/
   │   ├── router/
   │   │   └── index.js
   │   ├── stores/
   │   │   ├── index.js
   │   │   ├── modules/
   │   │   ├── user.js
   │   │   └── water-data.js
   │   ├── styles/
   │   │   ├── variables.scss
   │   │   └── global.scss
   │   ├── utils/
   │   │   ├── request.js
   │   │   ├── storage.js
   │   │   └── map-utils.js
   │   ├── views/
   │   │   ├── dashboard/
   │   │   ├── monitor/
   │   │   ├── analysis/
   │   │   └── map/
   │   ├── App.vue
   │   └── main.js
   ├── .eslintrc.js
   ├── .prettierrc.js
   ├── index.html
   ├── package.json
   ├── tsconfig.json
   └── vite.config.js
   ```

4. **路由配置(router/index.js)**：
   ```javascript
   import { createRouter, createWebHistory } from 'vue-router'
   
   const routes = [
     {
       path: '/',
       name: 'Home',
       component: () => import('../views/Home.vue')
     },
     {
       path: '/monitor',
       name: 'WaterMonitor',
       component: () => import('../views/WaterMonitor.vue')
     },
     {
       path: '/analysis',
       name: 'DataAnalysis',
       component: () => import('../views/DataAnalysis.vue')
     },
     {
       path: '/map',
       name: 'MapViewer',
       component: () => import('../views/MapViewer.vue')
     }
   ]
   
   const router = createRouter({
     history: createWebHistory('/'),
     routes
   })
   
   export default router
   ```

5. **状态管理配置(stores/index.js)**：
   ```javascript
   import { createPinia } from 'pinia'
   
   const pinia = createPinia()
   
   export default pinia
   ```

6. **主入口配置(main.js)**：
   ```javascript
   import { createApp } from 'vue'
   import App from './App.vue'
   import router from './router'
   import pinia from './stores'
   import Antd from 'ant-design-vue'
   import 'ant-design-vue/dist/antd.css'
   import './styles/main.css'
   
   const app = createApp(App)
   
   app.use(router)
   app.use(pinia)
   app.use(Antd)
   
   app.mount('#app')
   ```

### 智慧水利平台特殊组件配置

智慧水利平台前端通常需要一些特殊的组件支持：

1. **地图组件配置**：
   ```bash
   # 安装OpenLayers
   npm install ol
   
   # 安装Leaflet
   npm install leaflet
   
   # 安装三维地图库Cesium
   npm install cesium
   ```

   配置Cesium与Vite的集成：
   ```javascript
   // vite.config.js
   import { defineConfig } from 'vite'
   import vue from '@vitejs/plugin-vue'
   import cesium from 'vite-plugin-cesium'
   
   export default defineConfig({
     plugins: [
       vue(),
       cesium()
     ]
   })
   ```

2. **图表组件配置**：
   ```bash
   # 安装ECharts
   npm install echarts
   
   # 安装水情可视化专用库
   npm install @antv/g2
   ```

3. **WebSocket实时通信配置**：
   ```bash
   # 安装socket.io客户端
   npm install socket.io-client
   ```

   使用示例：
   ```javascript
   // src/utils/socket.js
   import { io } from 'socket.io-client'
   
   export const socket = io('ws://localhost:8080/water-data', {
     reconnectionDelayMax: 10000,
     path: '/ws'
   })
   
   // 连接水情实时数据
   socket.on('connect', () => {
     console.log('Socket connected')
     socket.emit('subscribe', { stationIds: ['ST001', 'ST002'] })
   })
   
   // 接收实时水位数据
   socket.on('waterLevel', (data) => {
     console.log('Received water level data:', data)
   })
   
   // 接收预警信息
   socket.on('alert', (alert) => {
     console.log('Received alert:', alert)
   })
   ```

## 3.4.2.4 智慧水利前端项目实例

以下是一个智慧水利监测平台前端项目的具体实例，展示配置和结构。

### 项目初始化与依赖

```bash
# 创建项目
pnpm create vite water-monitor-platform --template vue

# 安装核心依赖
cd water-monitor-platform
pnpm install vue-router@4 pinia axios

# 安装UI组件
pnpm install ant-design-vue@3 @ant-design/icons-vue

# 安装地图和图表组件
pnpm install ol echarts @antv/g2 datav-vue3

# 安装工具库
pnpm install dayjs lodash-es

# 安装开发依赖
pnpm install -D sass typescript @types/node vite-plugin-svg-icons
```

### 项目结构

```
water-monitor-platform/
├── public/
│   ├── static/
│   │   ├── geoserver/
│   │   └── data/
│   └── favicon.ico
├── src/
│   ├── api/
│   │   ├── index.js
│   │   ├── station.js
│   │   └── water-level.js
│   ├── assets/
│   │   ├── icons/
│   │   └── images/
│   ├── components/
│   │   ├── common/
│   │   ├── charts/
│   │   ├── map/
│   │   └── monitor/
│   ├── constants/
│   │   └── index.js
│   ├── hooks/
│   │   ├── useSocket.js
│   │   └── useStationData.js
│   ├── layouts/
│   │   ├── MainLayout.vue
│   │   └── components/
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── index.js
│   │   ├── modules/
│   │   ├── user.js
│   │   └── water-data.js
│   ├── styles/
│   │   ├── variables.scss
│   │   └── global.scss
│   ├── utils/
│   │   ├── request.js
│   │   ├── storage.js
│   │   └── map-utils.js
│   ├── views/
│   │   ├── dashboard/
│   │   ├── monitor/
│   │   ├── analysis/
│   │   └── map/
│   ├── App.vue
│   └── main.js
├── .env
├── .env.development
├── .env.production
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.js
```

### 环境变量配置

**.env.development**:
```
VITE_BASE_URL=http://localhost:8080
VITE_API_PREFIX=/api
VITE_GEOSERVER_URL=http://localhost:8600/geoserver
VITE_WS_URL=ws://localhost:8080/ws
```

**.env.production**:
```
VITE_BASE_URL=https://water.example.gov.cn
VITE_API_PREFIX=/api
VITE_GEOSERVER_URL=https://water.example.gov.cn/geoserver
VITE_WS_URL=wss://water.example.gov.cn/ws
```

### API请求配置

**src/utils/request.js**:
```javascript
import axios from 'axios'
import { message } from 'ant-design-vue'
import { useUserStore } from '../stores/user'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_PREFIX,
  timeout: 15000
})

service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 假设API返回的数据结构为 { code: number, data: any, message: string }
    if (res.code !== 200) {
      message.error(res.message || '请求失败')
      
      // 处理401等特殊错误
      if (res.code === 401) {
        const userStore = useUserStore()
        userStore.logout()
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    } else {
      return res.data
    }
  },
  error => {
    console.error('Response error:', error)
    message.error(error.message || '网络请求失败')
    return Promise.reject(error)
  }
)

export default service
```

### 地图组件配置

**src/components/map/WaterResourceMap.vue**:
```vue
<template>
  <div class="map-container" ref="mapContainer"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Map, View } from 'ol'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'
import { fromLonLat } from 'ol/proj'
import WMSLayer from 'ol/layer/Tile'
import WMSSource from 'ol/source/TileWMS'

const mapContainer = ref(null)
let map = null

// 水库位置数据
const reservoirs = [
  { id: 1, name: '新丰江水库', lon: 114.5698, lat: 24.0987, level: 105.3 },
  { id: 2, name: '白盆珠水库', lon: 114.2589, lat: 24.1278, level: 92.7 },
  // 更多水库数据...
]

onMounted(() => {
  // 初始化地图
  map = new Map({
    target: mapContainer.value,
    layers: [
      // 底图
      new TileLayer({
        source: new OSM()
      }),
      // WMS水系图层
      new WMSLayer({
        source: new WMSSource({
          url: import.meta.env.VITE_GEOSERVER_URL + '/wms',
          params: {
            'LAYERS': 'water:river_network',
            'TILED': true
          },
          serverType: 'geoserver'
        })
      })
    ],
    view: new View({
      center: fromLonLat([114.3, 24.1]), // 中心点坐标
      zoom: 10
    })
  })
  
  // 添加水库标记
  addReservoirMarkers(reservoirs)
})

onUnmounted(() => {
  if (map) {
    map.setTarget(null)
    map = null
  }
})

// 添加水库标记方法
function addReservoirMarkers(reservoirs) {
  // 实现添加水库标记的逻辑
  // ...
}
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>
```

### 水位实时监测组件

**src/views/monitor/WaterLevelMonitor.vue**:
```vue
<template>
  <div class="monitor-container">
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card title="监测站点列表">
          <a-list :data-source="stations" :loading="loading">
            <template #renderItem="{ item }">
              <a-list-item @click="selectStation(item)" :class="{ active: currentStation?.id === item.id }">
                <a-list-item-meta :title="item.name" :description="item.location">
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: getStatusColor(item.status) }">
                      {{ item.status === 'normal' ? '正常' : '异常' }}
                    </a-avatar>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
      
      <a-col :span="18">
        <a-card v-if="currentStation">
          <template #title>
            <div>{{ currentStation.name }} 水位实时监测
              <a-tag :color="getStatusColor(currentStation.status)">
                {{ currentStation.status === 'normal' ? '正常' : '异常' }}
              </a-tag>
            </div>
          </template>
          
          <a-row :gutter="16">
            <a-col :span="8">
              <a-statistic 
                title="当前水位" 
                :value="waterLevel.current" 
                :precision="2"
                suffix="m" 
                :value-style="{ color: waterLevel.warningLevel ? '#cf1322' : '#3f8600' }"
              />
              <a-progress 
                :percent="getWaterLevelPercent()" 
                :status="waterLevel.warningLevel ? 'exception' : 'normal'"
              />
            </a-col>
            
            <a-col :span="8">
              <a-statistic title="警戒水位" :value="waterLevel.warning" :precision="2" suffix="m" />
              <a-statistic title="24小时变化" :value="waterLevel.change24h" :precision="2" suffix="m" />
            </a-col>
            
            <a-col :span="8">
              <a-statistic title="更新时间" :value="waterLevel.updateTime" />
            </a-col>
          </a-row>
          
          <water-level-chart :station-id="currentStation.id" style="margin-top: 24px" />
        </a-card>
        
        <a-empty v-else description="请选择监测站点" />
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { getStationList } from '@/api/station'
import { getCurrentWaterLevel } from '@/api/water-level'
import WaterLevelChart from '@/components/charts/WaterLevelChart.vue'
import { useSocket } from '@/hooks/useSocket'

// 站点列表状态
const stations = ref([])
const loading = ref(false)
const currentStation = ref(null)

// 水位数据状态
const waterLevel = reactive({
  current: 0,
  warning: 0,
  change24h: 0,
  updateTime: '',
  warningLevel: false
})

// 加载站点列表
async function loadStations() {
  loading.value = true
  try {
    const data = await getStationList()
    stations.value = data
    if (data.length > 0) {
      selectStation(data[0])
    }
  } catch (error) {
    console.error('Failed to load stations:', error)
  } finally {
    loading.value = false
  }
}

// 选择站点
async function selectStation(station) {
  currentStation.value = station
  
  try {
    const data = await getCurrentWaterLevel(station.id)
    waterLevel.current = data.current
    waterLevel.warning = data.warning
    waterLevel.change24h = data.change24h
    waterLevel.updateTime = data.updateTime
    waterLevel.warningLevel = data.current >= data.warning
  } catch (error) {
    console.error('Failed to load water level:', error)
  }
  
  // 订阅实时水位数据
  socket.emit('subscribeStation', { stationId: station.id })
}

// WebSocket实时数据处理
const { socket } = useSocket()

// 监听水位更新
socket.on('waterLevelUpdate', (data) => {
  if (currentStation.value && data.stationId === currentStation.value.id) {
    waterLevel.current = data.level
    waterLevel.updateTime = data.time
    waterLevel.warningLevel = data.level >= waterLevel.warning
  }
})

// 辅助方法
function getStatusColor(status) {
  return status === 'normal' ? '#52c41a' : '#f5222d'
}

function getWaterLevelPercent() {
  return Math.min(100, (waterLevel.current / waterLevel.warning) * 100)
}

onMounted(() => {
  loadStations()
})

onUnmounted(() => {
  if (currentStation.value) {
    socket.emit('unsubscribeStation', { stationId: currentStation.value.id })
  }
})
</script>

<style lang="scss" scoped>
.monitor-container {
  padding: 24px;
}

.active {
  background-color: #e6f7ff;
}
</style>
```

## 思考与练习

### 思考题

1. 在智慧水利平台开发中，为什么需要选择合适的包管理器？npm、yarn和pnpm各有哪些优缺点？

2. 智慧水利平台前端应用通常需要展示大量实时水情数据，这对前端构建工具有哪些特殊要求？如何优化构建配置以提高性能？

3. 智慧水利平台通常需要集成GIS地图功能，在Vue.js项目中集成OpenLayers或Cesium有哪些常见方式和注意事项？

4. 对于大型智慧水利平台前端项目，如何组织和管理项目的目录结构和模块划分？请设计一个合理的项目结构。

### 实践练习

1. 使用Vue 3和Vite构建一个简单的水位监测看板，展示多个水库的水位数据，包括实时数据和历史趋势图表。

2. 在Vue项目中集成OpenLayers地图，实现水系和水库的可视化展示，包括点击交互和弹窗信息展示功能。

3. 使用WebSocket技术实现一个水情实时监测组件，能够接收服务器推送的实时水位数据，并在界面上动态更新。 