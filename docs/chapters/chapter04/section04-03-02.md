# Vue.js基础

本部分介绍Vue.js的基础知识，包括Vue实例、模板语法、计算属性、侦听器以及条件渲染和列表渲染等核心概念，这些是开发智慧水利平台前端应用的基础。

## 2.1 Vue实例

Vue实例是Vue应用的起点，通过创建Vue实例，我们可以将数据和视图绑定在一起，实现响应式更新。

```javascript
// 创建一个Vue实例 - 智慧水利平台示例
const app = new Vue({
  el: '#water-monitoring-app',
  data: {
    stationName: '黄河水文站',
    waterLevel: 85.6,
    flowRate: 1200,
    precipitation: 25.5,
    timestamp: '2023-07-15 10:30:45',
    warningThreshold: {
      waterLevel: 90.0,
      flowRate: 1500,
      precipitation: 50.0
    },
    isWarning: false,
    stationStatus: 'normal', // normal, warning, danger
    historyDays: 7
  },
  computed: {
    waterStatus() {
      if (this.waterLevel > this.warningThreshold.waterLevel) {
        return '警戒';
      } else if (this.waterLevel > this.warningThreshold.waterLevel * 0.9) {
        return '注意';
      } else {
        return '正常';
      }
    },
    statusColor() {
      switch(this.stationStatus) {
        case 'danger': return '#ff4d4f';
        case 'warning': return '#faad14';
        default: return '#52c41a';
      }
    }
  },
  methods: {
    refreshData() {
      // 获取最新数据的方法
      console.log('正在刷新水文站数据...');
    },
    changeHistoryRange(days) {
      this.historyDays = days;
      this.fetchHistoricalData(days);
    },
    fetchHistoricalData(days) {
      // 获取历史数据
      console.log(`正在获取${days}天的历史数据...`);
    },
    sendAlert(message) {
      // 发送预警信息
      console.log(`预警信息: ${message}`);
    }
  },
  watch: {
    waterLevel(newValue, oldValue) {
      // 监听水位变化，自动发送预警
      if (newValue > this.warningThreshold.waterLevel) {
        this.stationStatus = 'danger';
        this.sendAlert(`${this.stationName}水位超过警戒值！当前: ${newValue}米`);
      } else if (newValue > this.warningThreshold.waterLevel * 0.9) {
        this.stationStatus = 'warning';
      } else {
        this.stationStatus = 'normal';
      }
    }
  }
})
```

Vue实例的主要属性和选项：

1. **el**: 指定Vue实例挂载的DOM元素，可以是CSS选择器或DOM对象
2. **data**: 存储数据的对象，数据会被Vue转换为响应式的
3. **computed**: 计算属性，基于依赖进行缓存，只有依赖变化时才重新计算
4. **methods**: 存储方法的对象，可以在模板中通过事件指令调用
5. **watch**: 侦听器，用于响应数据变化并执行异步操作或复杂逻辑
6. **created、mounted等**: 生命周期钩子，在实例生命周期的不同阶段调用

在智慧水利平台中，Vue实例通常用于管理水文站点的数据、状态和行为，例如监控水位变化、处理预警逻辑等。

## 2.2 模板语法

Vue.js使用基于HTML的模板语法，允许开发者声明式地将DOM绑定到Vue实例的数据。Vue会自动建立数据与DOM之间的关联，实现响应式更新。

### 2.2.1 文本插值

使用双大括号`{{ ... }}`在文本中插入数据：

```html
<span>水位: {{ waterLevel }}米</span>
```

### 2.2.2 指令

Vue提供了许多内置指令，以`v-`为前缀：

- **v-bind**: 绑定HTML属性
  ```html
  <div v-bind:class="stationStatus">水文站状态</div>
  <!-- 缩写形式 -->
  <div :class="stationStatus">水文站状态</div>
  ```

- **v-if/v-else/v-else-if**: 条件渲染
  ```html
  <div v-if="waterStatus === '警戒'">水位警戒！</div>
  <div v-else-if="waterStatus === '注意'">水位接近警戒线</div>
  <div v-else>水位正常</div>
  ```

- **v-for**: 列表渲染
  ```html
  <div v-for="station in stations" :key="station.id">
    {{ station.name }}: {{ station.waterLevel }}米
  </div>
  ```

- **v-on**: 绑定事件
  ```html
  <button v-on:click="refreshData">刷新数据</button>
  <!-- 缩写形式 -->
  <button @click="refreshData">刷新数据</button>
  ```

- **v-model**: 双向数据绑定，常用于表单元素
  ```html
  <input v-model="searchQuery" placeholder="搜索水文站...">
  ```

### 2.2.3 智慧水利平台中的模板应用示例

```html
<!-- 智慧水利平台水文站监测卡片 -->
<div class="water-station-card" :class="stationStatus">
  <div class="card-header">
    <h2>{{ stationName }}</h2>
    <span class="status-indicator" :style="{backgroundColor: statusColor}"></span>
  </div>
  
  <div class="station-data">
    <div class="data-row">
      <span class="label">水位:</span>
      <span class="value" :class="{'warning-text': waterLevel > warningThreshold.waterLevel * 0.9, 'danger-text': waterLevel > warningThreshold.waterLevel}">
        {{ waterLevel }}米
      </span>
    </div>
    <div class="data-row">
      <span class="label">流量:</span>
      <span class="value" :class="{'warning-text': flowRate > warningThreshold.flowRate * 0.9, 'danger-text': flowRate > warningThreshold.flowRate}">
        {{ flowRate }}立方米/秒
      </span>
    </div>
    <div class="data-row">
      <span class="label">降水量:</span>
      <span class="value" :class="{'warning-text': precipitation > warningThreshold.precipitation * 0.9, 'danger-text': precipitation > warningThreshold.precipitation}">
        {{ precipitation }}毫米
      </span>
    </div>
    <div class="data-row">
      <span class="label">状态:</span>
      <span class="value status">{{ waterStatus }}</span>
    </div>
    <div class="data-row">
      <span class="label">更新时间:</span>
      <span class="value">{{ timestamp }}</span>
    </div>
  </div>
  
  <div class="card-actions">
    <button @click="refreshData" class="refresh-btn">刷新数据</button>
    <div class="history-selector">
      <span>历史数据:</span>
      <select v-model="historyDays" @change="fetchHistoricalData(historyDays)">
        <option :value="1">24小时</option>
        <option :value="7">7天</option>
        <option :value="30">30天</option>
      </select>
    </div>
  </div>
</div>
```

## 2.3 计算属性与监听器

计算属性和监听器是Vue.js中处理复杂逻辑的两种重要机制。

### 2.3.1 计算属性

计算属性用于处理复杂的数据计算逻辑，它会基于依赖进行缓存，只有依赖变化时才重新计算。这使得计算属性比方法更高效。

```javascript
computed: {
  // 计算当前水位状态
  waterStatus() {
    if (this.waterLevel > this.warningThreshold.waterLevel) {
      return '警戒';
    } else if (this.waterLevel > this.warningThreshold.waterLevel * 0.9) {
      return '注意';
    } else {
      return '正常';
    }
  },
  
  // 计算水位趋势（上升/下降/稳定）
  waterLevelTrend() {
    if (this.historicalData.length < 2) return '无趋势数据';
    
    const latest = this.historicalData[this.historicalData.length - 1].waterLevel;
    const previous = this.historicalData[this.historicalData.length - 2].waterLevel;
    
    const diff = latest - previous;
    if (Math.abs(diff) < 0.1) return '稳定';
    return diff > 0 ? '上升' : '下降';
  },
  
  // 计算当日累计降水量
  todayTotalPrecipitation() {
    const today = new Date().toLocaleDateString();
    return this.precipitationRecords
      .filter(record => new Date(record.time).toLocaleDateString() === today)
      .reduce((sum, record) => sum + record.value, 0);
  },
  
  // 计算水库蓄水百分比
  reservoirPercentage() {
    return (this.currentStorage / this.maxStorage * 100).toFixed(1) + '%';
  }
}
```

### 2.3.2 监听器

监听器用于响应数据变化并执行副作用操作（如异步请求、DOM操作等）。

```javascript
watch: {
  // 监听水位变化，自动发送预警
  waterLevel(newValue, oldValue) {
    if (newValue > this.warningThreshold.waterLevel && !this.isWarning) {
      this.isWarning = true;
      this.sendAlert(`水位超过警戒线！当前水位：${newValue}米`);
      this.logWaterLevelChange(newValue, oldValue, '警戒');
    } else if (newValue > this.warningThreshold.waterLevel * 0.9 && !this.isWarning) {
      this.stationStatus = 'warning';
      this.sendAlert(`水位接近警戒线！当前水位：${newValue}米`);
      this.logWaterLevelChange(newValue, oldValue, '注意');
    } else if (newValue <= this.warningThreshold.waterLevel && this.isWarning) {
      this.isWarning = false;
      this.stationStatus = 'normal';
      this.clearAlert();
      this.logWaterLevelChange(newValue, oldValue, '恢复正常');
    }
  },
  
  // 监听雨量变化，预测可能的水位变化
  'precipitation': {
    handler(newValue, oldValue) {
      if (newValue > this.warningThreshold.precipitation) {
        this.predictWaterLevelChange(newValue);
        this.sendAlert(`降水量超过警戒值！可能引起水位上涨，请注意防范。`);
      }
    },
    immediate: true // 立即以当前值触发回调
  },
  
  // 深度监听配置对象的变化
  'warningThreshold': {
    handler(newValue) {
      console.log('预警阈值已更新:', newValue);
      this.saveThresholdSettings();
      this.reevaluateCurrentStatus();
    },
    deep: true // 深度监听对象内部属性变化
  }
}
```

## 2.4 条件渲染与列表渲染

条件渲染和列表渲染是Vue.js中常用的两种DOM操作方式，适用于智慧水利平台中的多种场景。

### 2.4.1 条件渲染

Vue提供了`v-if`、`v-else-if`、`v-else`和`v-show`指令进行条件渲染。

- `v-if`/`v-else-if`/`v-else`: 根据条件真假，完全渲染或移除元素
- `v-show`: 根据条件真假，切换元素的CSS `display`属性

```html
<!-- 根据水位状态显示不同警告 -->
<div class="alert-panel">
  <div v-if="waterStatus === '警戒'" class="alert danger">
    <i class="icon-warning"></i>水位已超过警戒线，请密切关注！
  </div>
  <div v-else-if="waterStatus === '注意'" class="alert warning">
    <i class="icon-attention"></i>水位接近警戒线，请注意观察
  </div>
  <div v-else class="alert info">
    <i class="icon-info"></i>水位正常，运行安全
  </div>
</div>

<!-- 使用v-show的例子：频繁切换的元素 -->
<div v-show="showDetailInfo" class="station-details">
  <h3>{{ stationName }} - 详细信息</h3>
  <table class="details-table">
    <!-- 详细数据表格 -->
  </table>
</div>
```

**适用场景**：
- `v-if`: 适用于条件很少改变的场景（如权限控制）
- `v-show`: 适用于需要频繁切换的场景（如面板展开/折叠）

### 2.4.2 列表渲染

使用`v-for`指令基于数组渲染列表，通常与`:key`属性一起使用，以帮助Vue高效更新DOM。

```html
<!-- 监测站点列表 -->
<div class="station-list">
  <div v-for="station in stations" :key="station.id" class="station-item" :class="station.status">
    <h3>{{ station.name }}</h3>
    <div class="station-meta">
      <span class="station-id">ID: {{ station.id }}</span>
      <span class="station-type">类型: {{ station.type }}</span>
    </div>
    <div class="station-data">
      <p>水位: {{ station.waterLevel }}米</p>
      <p>流量: {{ station.flowRate }}立方米/秒</p>
      <p>状态: {{ getStatusText(station.status) }}</p>
      <p>更新时间: {{ formatTime(station.updateTime) }}</p>
    </div>
    <div class="station-actions">
      <button @click="viewDetails(station.id)">查看详情</button>
      <button @click="viewHistory(station.id)">历史数据</button>
    </div>
  </div>
</div>

<!-- 使用v-for遍历对象属性 -->
<div class="threshold-settings">
  <h3>预警阈值设置</h3>
  <div v-for="(value, key) in warningThreshold" :key="key" class="threshold-item">
    <label>{{ getThresholdLabel(key) }}:</label>
    <input type="number" v-model.number="warningThreshold[key]" @change="saveThresholdSettings">
    <span class="unit">{{ getThresholdUnit(key) }}</span>
  </div>
</div>

<!-- 嵌套的v-for -->
<div class="region-stations">
  <div v-for="region in regions" :key="region.id" class="region">
    <h2>{{ region.name }}</h2>
    <div class="region-stations-list">
      <div v-for="station in region.stations" :key="station.id" class="station-card">
        <!-- 站点信息 -->
      </div>
    </div>
  </div>
</div>
```

### 2.4.3 在智慧水利平台中的应用

条件渲染和列表渲染在智慧水利平台中有广泛应用：

1. **显示不同级别的预警信息**：根据水位、流量等数据的不同状态，显示不同级别的预警信息
2. **展示监测站点列表**：将后端获取的站点数据以列表或网格形式展示
3. **分区域显示站点信息**：按照行政区划或流域划分展示不同区域的水文站点
4. **根据用户权限显示不同功能**：基于用户角色显示或隐藏特定的操作按钮和管理选项
5. **数据仪表盘组件的动态加载**：根据用户配置，动态渲染不同的数据展示组件


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
