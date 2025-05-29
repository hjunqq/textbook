# 现代JavaScript特性

本节将介绍现代JavaScript（ES6及以后版本）的核心特性，以及这些特性如何在智慧水利平台开发中提高开发效率和代码质量。

## 4.2.4.1 ES6+核心特性

### let和const

与传统的`var`不同，`let`和`const`提供了块级作用域，减少了变量污染问题：

```javascript
// 使用let声明可变变量
let currentWaterLevel = 42.5;
currentWaterLevel = 43.2; // 可以重新赋值

// 使用const声明常量
const MAX_WATER_LEVEL = 50.0;
const MIN_WATER_LEVEL = 20.0;

// 块级作用域示例
if (currentWaterLevel > MAX_WATER_LEVEL) {
  const alertMessage = "水位超过警戒线";
  console.log(alertMessage);
}
// alertMessage在此处不可访问
```

### 箭头函数

箭头函数提供了更简洁的语法，同时保持词法this值：

```javascript
// 传统函数
function calculateAverageFlow(readings) {
  return readings.reduce(function(sum, reading) {
    return sum + reading.flow;
  }, 0) / readings.length;
}

// 箭头函数
const calculateAverageFlow = readings => 
  readings.reduce((sum, reading) => sum + reading.flow, 0) / readings.length;

// 在智慧水利应用中处理数据
const filterAbnormalReadings = readings => 
  readings.filter(reading => reading.value > THRESHOLD);

// 保持this上下文的示例
const waterMonitor = {
  readings: [],
  addReading(reading) {
    this.readings.push(reading);
  },
  getAverages() {
    // 箭头函数保持外部this指向waterMonitor
    return {
      flow: this.readings.reduce((sum, r) => sum + r.flow, 0) / this.readings.length,
      level: this.readings.reduce((sum, r) => sum + r.level, 0) / this.readings.length
    };
  }
};
```

### 模板字符串

模板字符串简化了字符串拼接，特别适合创建HTML元素和格式化报告：

```javascript
const stationName = "龙泉水库";
const waterLevel = 42.5;
const timestamp = new Date().toLocaleString();

// 传统字符串拼接
const oldReport = "监测站" + stationName + "于" + timestamp + "报告水位为" + waterLevel + "米";

// 模板字符串
const report = `监测站${stationName}于${timestamp}报告水位为${waterLevel}米`;

// 在HTML生成中的应用
function createStationCard(station) {
  return `
    <div class="station-card ${station.status}">
      <h3>${station.name}</h3>
      <div class="details">
        <p>水位: ${station.waterLevel}米</p>
        <p>流量: ${station.flowRate}m³/s</p>
        <p>状态: ${getStatusText(station.status)}</p>
      </div>
      <button data-id="${station.id}" class="details-btn">查看详情</button>
    </div>
  `;
}

document.getElementById('stations-container').innerHTML = stations.map(createStationCard).join('');
```

### 解构赋值

解构赋值让代码更简洁，特别是在处理API返回的复杂数据时：

```javascript
// 对象解构
const stationData = {
  id: 'ST001',
  name: '龙泉水库',
  readings: {
    waterLevel: 42.5,
    flow: 210,
    rainfall: 0,
    temperature: 22.5
  },
  location: {
    latitude: 39.856,
    longitude: 116.789
  }
};

// 提取需要的属性
const { name, readings, location } = stationData;
const { waterLevel, flow } = readings;
const { latitude, longitude } = location;

console.log(`${name}的水位为${waterLevel}米，流量为${flow}m³/s`);

// 在函数参数中使用解构
function displayStationInfo({ name, readings: { waterLevel, flow }, location }) {
  console.log(`${name} (坐标: ${location.latitude}, ${location.longitude})`);
  console.log(`水位: ${waterLevel}米，流量: ${flow}m³/s`);
}

// 数组解构
const timeSeriesData = [
  ['2023-01-01', 42.1, 205],
  ['2023-01-02', 42.3, 212],
  ['2023-01-03', 42.8, 230]
];

// 处理时间序列数据
timeSeriesData.forEach(([date, level, flow]) => {
  console.log(`${date}: 水位${level}米，流量${flow}m³/s`);
});
```

### 扩展运算符

扩展运算符(`...`)简化了数组和对象操作：

```javascript
// 合并数组
const upstreamStations = ['ST001', 'ST002', 'ST003'];
const downstreamStations = ['ST004', 'ST005'];
const allStations = [...upstreamStations, ...downstreamStations];

// 复制数组
const stationsCopy = [...allStations];

// 函数参数
function calculateTotalFlow(...flowReadings) {
  return flowReadings.reduce((sum, flow) => sum + flow, 0);
}
const totalFlow = calculateTotalFlow(120, 150, 80, 200);

// 对象扩展
const baseStationConfig = {
  refreshInterval: 60000,
  alertThreshold: 50.0,
  units: 'metric'
};

const customStation = {
  ...baseStationConfig,
  id: 'ST006',
  name: '青龙水库',
  alertThreshold: 45.0  // 覆盖默认值
};
```

### 默认参数

默认参数简化了函数调用：

```javascript
// 具有默认参数的函数
function fetchWaterData(stationId, period = '24h', resolution = '1h') {
  console.log(`获取站点${stationId}的${period}数据，分辨率为${resolution}`);
  // API调用逻辑
}

// 调用方式
fetchWaterData('ST001');                // 使用所有默认值
fetchWaterData('ST001', '7d');          // 覆盖第一个默认值
fetchWaterData('ST001', '7d', '30min'); // 覆盖所有默认值

// 在智慧水利平台中的复杂设置函数
function configureWaterLevelChart(
  containerId, 
  data, 
  {
    height = 400, 
    width = 800, 
    title = '水位变化图', 
    yAxisLabel = '水位(m)',
    thresholds = { warning: 45, danger: 48 }
  } = {}
) {
  // 图表配置逻辑
  console.log(`配置图表：${title}, 尺寸: ${width}x${height}px`);
  console.log(`警戒水位: ${thresholds.warning}m，危险水位: ${thresholds.danger}m`);
}

// 调用
configureWaterLevelChart('chart1', waterLevelData);
configureWaterLevelChart('chart2', waterLevelData, { 
  height: 300, 
  thresholds: { warning: 40, danger: 42 } 
});
```

### 类语法

ES6引入的类语法使面向对象编程更加直观：

```javascript
// 定义基础监测站类
class MonitoringStation {
  constructor(id, name, location) {
    this.id = id;
    this.name = name;
    this.location = location;
    this.readings = [];
    this.lastUpdated = null;
  }

  addReading(reading) {
    this.readings.push(reading);
    this.lastUpdated = new Date();

    // 保持最新的100条记录
    if (this.readings.length > 100) {
      this.readings.shift();
    }
  }

  getLatestReading() {
    if (this.readings.length === 0) return null;
    return this.readings[this.readings.length - 1];
  }

  // 静态方法
  static createFromApiResponse(data) {
    const station = new MonitoringStation(
      data.id, 
      data.name, 
      data.location
    );
    
    if (data.readings && Array.isArray(data.readings)) {
      data.readings.forEach(r => station.addReading(r));
    }
    
    return station;
  }
}

// 继承
class WaterLevelStation extends MonitoringStation {
  constructor(id, name, location, warningThreshold) {
    super(id, name, location);  // 调用父类构造函数
    this.warningThreshold = warningThreshold;
  }

  isAboveWarningLevel() {
    const latest = this.getLatestReading();
    return latest && latest.value > this.warningThreshold;
  }

  // 重写父类方法
  addReading(reading) {
    super.addReading(reading);
    
    // 额外逻辑：检查是否超过警戒值
    if (reading.value > this.warningThreshold) {
      console.log(`警告：${this.name}水位(${reading.value}m)超过警戒值(${this.warningThreshold}m)`);
    }
  }
}

// 使用示例
const station = new WaterLevelStation('WL001', '龙泉水库', { lat: 39.856, lng: 116.789 }, 45.0);
station.addReading({ time: '2023-06-15T10:00:00', value: 42.5 });
station.addReading({ time: '2023-06-15T11:00:00', value: 46.2 });
```

### Promise与异步编程

Promise简化了异步操作处理：

```javascript
// 基于Promise的数据获取
function fetchStationData(stationId) {
  return fetch(`/api/stations/${stationId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('无法获取站点数据');
      }
      return response.json();
    });
}

// 使用Promise
fetchStationData('ST001')
  .then(data => {
    console.log('站点数据:', data);
    // 处理数据
    updateStationDisplay(data);
    
    // 链式调用
    return fetchStationData('ST002');
  })
  .then(data => {
    console.log('关联站点数据:', data);
    updateRelatedStationDisplay(data);
  })
  .catch(error => {
    console.error('获取数据失败:', error);
    showErrorMessage(error.message);
  });

// Promise组合
const stationIds = ['ST001', 'ST002', 'ST003'];

// 并行获取多个站点数据
Promise.all(stationIds.map(id => fetchStationData(id)))
  .then(results => {
    console.log(`成功获取${results.length}个站点的数据`);
    displayMultipleStations(results);
  })
  .catch(error => {
    console.error('获取站点数据时出错:', error);
  });

// 获取最先返回数据的站点
Promise.race(stationIds.map(id => fetchStationData(id)))
  .then(firstResult => {
    console.log('最先获取的站点数据:', firstResult);
    quickUpdateDisplay(firstResult);
  });
```

### async/await

`async/await`进一步简化了异步代码：

```javascript
// 使用async/await重写数据获取
async function getStationData(stationId) {
  try {
    const response = await fetch(`/api/stations/${stationId}`);
    if (!response.ok) {
      throw new Error('无法获取站点数据');
    }
    return await response.json();
  } catch (error) {
    console.error(`获取站点${stationId}数据失败:`, error);
    throw error; // 重新抛出错误以供调用者处理
  }
}

// 更复杂的异步操作示例
async function updateDashboard() {
  try {
    // 显示加载状态
    showLoadingIndicator();
    
    // 并行获取多个数据源
    const [stationData, weatherData, alertsData] = await Promise.all([
      getStationData('ST001'),
      getWeatherForecast('区域A'),
      getActiveAlerts()
    ]);
    
    // 处理获取的数据
    updateStationDisplay(stationData);
    updateWeatherSection(weatherData);
    
    // 条件处理
    if (alertsData.length > 0) {
      showAlertBanner(alertsData);
      
      // 序列化处理严重警报
      for (const alert of alertsData.filter(a => a.severity === 'high')) {
        await processHighPriorityAlert(alert);
      }
    }
    
    console.log('仪表盘更新完成');
  } catch (error) {
    console.error('更新仪表盘时出错:', error);
    showErrorMessage('无法更新仪表盘数据');
  } finally {
    hideLoadingIndicator();
  }
}

// 模拟处理高优先级警报
async function processHighPriorityAlert(alert) {
  console.log(`处理严重警报: ${alert.message}`);
  await notifyEmergencyContacts(alert);
  await logAlertToDatabase(alert);
}
```

### 模块化

ES6模块系统提供了更好的代码组织方式：

```javascript
// utils.js - 工具函数模块
export function formatWaterLevel(level) {
  return `${level.toFixed(2)}m`;
}

export function calculateChangeRate(previous, current, hours) {
  return (current - previous) / hours;
}

// 导出默认对象
export default {
  WATER_LEVEL_THRESHOLD: 45.0,
  FLOW_RATE_THRESHOLD: 200,
  REFRESH_INTERVAL: 60000
};

// station-service.js - 站点服务模块
import CONFIG from './utils.js';
import { formatWaterLevel } from './utils.js';

export async function fetchStationData(stationId) {
  // 获取站点数据的实现
}

export class StationManager {
  constructor() {
    this.stations = new Map();
    this.refreshInterval = CONFIG.REFRESH_INTERVAL;
  }
  
  // 方法实现
}

// main.js - 主应用模块
import CONFIG, { formatWaterLevel, calculateChangeRate } from './utils.js';
import { fetchStationData, StationManager } from './station-service.js';
import * as ChartUtils from './chart-utils.js';

async function initializeApp() {
  const stationManager = new StationManager();
  const data = await fetchStationData('ST001');
  
  document.getElementById('current-level').textContent = 
    formatWaterLevel(data.waterLevel);
    
  const changeRate = calculateChangeRate(
    data.previousWaterLevel, 
    data.waterLevel, 
    data.hoursSinceLastReading
  );
  
  ChartUtils.createWaterLevelChart('chart-container', data.history);
}

// 初始化应用
initializeApp();
```

## 4.2.4.2 ES6+在智慧水利平台中的应用

### 数据处理与转换

使用现代JavaScript特性可以更高效地处理水利监测数据：

```javascript
// 处理监测站点数据
function processMonitoringData(stationsData) {
  // 使用解构和箭头函数
  return stationsData.map(({ id, name, readings }) => ({
    id,
    name,
    averageLevel: readings.reduce((sum, { level }) => sum + level, 0) / readings.length,
    maxLevel: Math.max(...readings.map(({ level }) => level)),
    lastReading: readings[readings.length - 1],
    hasWarning: readings.some(({ level }) => level > THRESHOLD)
  }));
}

// 过滤和分组
function analyzeWatershedData(stations) {
  // 按流域分组
  const byWatershed = stations.reduce((groups, station) => {
    const { watershed } = station;
    if (!groups[watershed]) {
      groups[watershed] = [];
    }
    groups[watershed].push(station);
    return groups;
  }, {});
  
  // 计算每个流域的汇总数据
  return Object.entries(byWatershed).map(([name, stations]) => {
    // 使用解构和箭头函数简化计算
    const avgWaterLevel = stations.reduce((sum, { waterLevel }) => sum + waterLevel, 0) / stations.length;
    const totalFlow = stations.reduce((sum, { flowRate }) => sum + flowRate, 0);
    
    return {
      watershed: name,
      stationCount: stations.length,
      averageWaterLevel: avgWaterLevel,
      totalFlow,
      stations: stations.map(({ id, name }) => ({ id, name }))
    };
  });
}
```

### 异步数据获取与显示

智慧水利平台需要处理多个数据源的异步请求：

```javascript
// 水利监测数据仪表盘
class WaterResourceDashboard {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.stations = [];
    this.lastUpdated = null;
  }
  
  // 使用async/await加载数据
  async initialize() {
    try {
      // 显示加载状态
      this.showLoading();
      
      // 并行获取配置和初始数据
      const [config, stationsData] = await Promise.all([
        this.fetchConfig(),
        this.fetchStations()
      ]);
      
      // 设置刷新间隔
      this.refreshInterval = config.refreshInterval || 60000;
      this.stations = stationsData;
      
      // 渲染仪表盘
      this.render();
      
      // 设置定时刷新
      this.startRefreshTimer();
      
      console.log('仪表盘初始化完成');
    } catch (error) {
      console.error('初始化仪表盘失败:', error);
      this.showError('无法加载仪表盘数据');
    }
  }
  
  // 获取配置
  async fetchConfig() {
    const response = await fetch('/api/dashboard/config');
    return response.json();
  }
  
  // 获取站点数据
  async fetchStations() {
    const response = await fetch('/api/stations');
    return response.json();
  }
  
  // 获取单个站点详细数据
  async fetchStationDetails(stationId) {
    const response = await fetch(`/api/stations/${stationId}/details`);
    if (!response.ok) {
      throw new Error(`无法获取站点${stationId}的详细信息`);
    }
    return response.json();
  }
  
  // 渲染仪表盘
  render() {
    if (this.stations.length === 0) {
      this.container.innerHTML = '<p>没有可用的监测站点数据</p>';
      return;
    }
    
    // 使用解构和模板字符串生成HTML
    this.container.innerHTML = `
      <div class="dashboard-header">
        <h2>水利监测仪表盘</h2>
        <p>最后更新: ${new Date().toLocaleString()}</p>
      </div>
      <div class="stations-grid">
        ${this.stations.map(station => this.renderStationCard(station)).join('')}
      </div>
    `;
    
    // 为每个站点卡片添加点击事件
    this.container.querySelectorAll('.station-card').forEach(card => {
      card.addEventListener('click', async (event) => {
        const stationId = card.dataset.id;
        await this.showStationDetails(stationId);
      });
    });
  }
  
  // 渲染单个站点卡片
  renderStationCard({ id, name, waterLevel, flowRate, status }) {
    return `
      <div class="station-card ${status}" data-id="${id}">
        <h3>${name}</h3>
        <div class="readings">
          <div class="reading">
            <span class="label">水位:</span>
            <span class="value">${waterLevel.toFixed(2)}m</span>
          </div>
          <div class="reading">
            <span class="label">流量:</span>
            <span class="value">${flowRate.toFixed(2)}m³/s</span>
          </div>
        </div>
        <div class="status-indicator ${status}">
          ${this.getStatusText(status)}
        </div>
      </div>
    `;
  }
  
  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      normal: '正常',
      warning: '警告',
      danger: '危险'
    };
    return statusMap[status] || '未知';
  }
  
  // 显示站点详情
  async showStationDetails(stationId) {
    try {
      const detailsContainer = document.getElementById('station-details-container');
      detailsContainer.innerHTML = '<p>加载中...</p>';
      
      // 显示模态框
      document.getElementById('station-details-modal').style.display = 'block';
      
      // 获取详细数据
      const details = await this.fetchStationDetails(stationId);
      
      // 使用解构获取需要的属性
      const { name, location, waterLevel, flowRate, rainfall, history } = details;
      
      // 渲染详情视图
      detailsContainer.innerHTML = `
        <h2>${name}详细信息</h2>
        <div class="details-content">
          <div class="location-info">
            <p>位置: ${location.description}</p>
            <p>坐标: ${location.latitude}, ${location.longitude}</p>
          </div>
          
          <div class="current-readings">
            <h3>当前读数</h3>
            <p>水位: ${waterLevel.toFixed(2)}m</p>
            <p>流量: ${flowRate.toFixed(2)}m³/s</p>
            <p>降雨量: ${rainfall !== null ? `${rainfall.toFixed(1)}mm` : '无数据'}</p>
          </div>
          
          <div class="history-chart-container">
            <h3>历史数据</h3>
            <canvas id="history-chart"></canvas>
          </div>
        </div>
      `;
      
      // 创建历史数据图表
      this.createHistoryChart(history);
      
    } catch (error) {
      console.error('获取站点详情失败:', error);
      document.getElementById('station-details-container').innerHTML = 
        `<p class="error-message">无法加载站点详情: ${error.message}</p>`;
    }
  }
  
  // 创建历史数据图表
  createHistoryChart(history) {
    // 图表创建逻辑...
  }
  
  // 开始定时刷新
  startRefreshTimer() {
    setInterval(async () => {
      try {
        const stationsData = await this.fetchStations();
        this.stations = stationsData;
        this.render();
        this.lastUpdated = new Date();
      } catch (error) {
        console.error('刷新数据失败:', error);
      }
    }, this.refreshInterval);
  }
  
  // 显示加载中状态
  showLoading() {
    this.container.innerHTML = '<div class="loading-spinner">加载中...</div>';
  }
  
  // 显示错误信息
  showError(message) {
    this.container.innerHTML = `<div class="error-message">${message}</div>`;
  }
}

// 初始化仪表盘
const dashboard = new WaterResourceDashboard('water-resources-dashboard');
dashboard.initialize();
```

### 模块化组织代码

模块化使智慧水利平台的代码更易维护：

```javascript
// config.js - 全局配置
export const API_BASE_URL = '/api';
export const REFRESH_INTERVALS = {
  DASHBOARD: 60000,  // 1分钟
  ALERTS: 30000,     // 30秒
  CHARTS: 300000     // 5分钟
};

export const THRESHOLDS = {
  WATER_LEVEL: {
    WARNING: 45.0,
    DANGER: 48.0
  },
  RAINFALL: {
    WARNING: 50,  // mm/h
    DANGER: 100   // mm/h
  }
};

// api-service.js - API服务
import { API_BASE_URL } from './config.js';

export async function fetchWithTimeout(url, options = {}, timeout = 10000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`API错误: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('请求超时');
    }
    throw error;
  }
}

export async function getStations() {
  return fetchWithTimeout(`${API_BASE_URL}/stations`);
}

export async function getStationDetails(stationId) {
  return fetchWithTimeout(`${API_BASE_URL}/stations/${stationId}`);
}

export async function getWatershedOverview(watershedId) {
  return fetchWithTimeout(`${API_BASE_URL}/watersheds/${watershedId}`);
}

// data-processor.js - 数据处理
import { THRESHOLDS } from './config.js';

export function calculateStationStatus(waterLevel) {
  if (waterLevel >= THRESHOLDS.WATER_LEVEL.DANGER) {
    return 'danger';
  } else if (waterLevel >= THRESHOLDS.WATER_LEVEL.WARNING) {
    return 'warning';
  }
  return 'normal';
}

export function processStationsData(stations) {
  return stations.map(station => ({
    ...station,
    status: calculateStationStatus(station.waterLevel)
  }));
}

export function groupStationsByWatershed(stations) {
  return stations.reduce((groups, station) => {
    const { watershed } = station;
    if (!groups[watershed]) {
      groups[watershed] = [];
    }
    groups[watershed].push(station);
    return groups;
  }, {});
}

// chart-utils.js - 图表工具
export function createWaterLevelChart(containerId, historyData, options = {}) {
  // 图表创建逻辑
}

export function createRainfallChart(containerId, historyData, options = {}) {
  // 图表创建逻辑
}

export function updateChartData(chart, newData) {
  // 更新图表数据
}

// main.js - 主模块
import { REFRESH_INTERVALS } from './config.js';
import { getStations, getStationDetails } from './api-service.js';
import { processStationsData, groupStationsByWatershed } from './data-processor.js';
import { createWaterLevelChart, createRainfallChart } from './chart-utils.js';

async function initializeDashboard() {
  try {
    // 获取并处理站点数据
    const stations = await getStations();
    const processedStations = processStationsData(stations);
    
    // 显示站点列表
    renderStationsList(processedStations);
    
    // 按流域分组并显示概览
    const stationsByWatershed = groupStationsByWatershed(processedStations);
    renderWatershedOverviews(stationsByWatershed);
    
    // 设置定时刷新
    setInterval(refreshDashboard, REFRESH_INTERVALS.DASHBOARD);
    
  } catch (error) {
    console.error('初始化仪表盘失败:', error);
    showErrorMessage('无法加载仪表盘数据');
  }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', initializeDashboard);
```

## 4.2.4.3 跨浏览器兼容性与Polyfill

面对不同浏览器的支持情况，我们可以使用Polyfill确保代码在各种环境中运行：

```javascript
// 检查浏览器对Promise的支持
if (typeof Promise === 'undefined') {
  console.warn('浏览器不支持Promise，加载polyfill');
  // 这里会加载Promise polyfill
}

// 可以使用条件检测来提供替代方案
function fetchStationData(stationId) {
  // 检查是否支持fetch API
  if (typeof fetch !== 'undefined') {
    return fetch(`/api/stations/${stationId}`)
      .then(response => response.json());
  } else {
    // 降级为XMLHttpRequest
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('GET', `/api/stations/${stationId}`);
      xhr.onload = function() {
        if (xhr.status === 200) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error(`无法获取数据: ${xhr.status}`));
        }
      };
      xhr.onerror = function() {
        reject(new Error('网络错误'));
      };
      xhr.send();
    });
  }
}

// 对于现代项目，通常使用Babel和core-js等工具自动添加polyfill
```

## 4.2.4.4 小结

现代JavaScript的特性大大提高了开发智慧水利平台的效率和代码质量：

1. **语法改进**：`let/const`、箭头函数、模板字符串、解构赋值等使代码更简洁清晰
2. **类与模块**：提供更好的代码组织和封装方式
3. **异步编程**：Promise和async/await简化异步操作处理
4. **扩展运算符**：简化数组和对象操作

在智慧水利平台开发中，这些特性可以帮助：
- 更高效地处理和转换水文数据
- 简化与后端API的交互
- 改进用户界面的响应性能
- 提高代码的可维护性和可读性

下一节，我们将探讨JavaScript在智慧水利平台中的具体应用场景，包括数据可视化、地图集成、表单处理和实时通信等方面。 