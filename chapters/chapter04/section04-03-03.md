# Vue组件系统

组件系统是Vue.js的一个重要特性，它允许我们构建由小型、独立且可复用的组件组成的大型应用。在智慧水利平台中，组件化开发可以帮助我们更高效地构建和维护复杂的用户界面。

## 3.1 组件基础

Vue组件本质上是一个带有预定义选项的Vue实例，可以在应用中被反复使用。组件的注册方式有全局注册和局部注册两种。

### 3.1.1 组件注册

**全局注册**：全局注册的组件可以在任何Vue实例中使用。

```javascript
// 全局注册水位监测组件
Vue.component('water-level-gauge', {
  props: ['value', 'maxValue', 'minValue', 'warningValue'],
  template: `
    <div class="water-gauge">
      <div class="gauge-container">
        <div class="water-fill" :style="fillStyle"></div>
      </div>
      <div class="gauge-reading">{{ value }}m</div>
    </div>
  `,
  computed: {
    fillStyle() {
      const percentage = ((this.value - this.minValue) / (this.maxValue - this.minValue)) * 100;
      let color = '#1890ff'; // 默认蓝色
      
      if (this.value >= this.warningValue) {
        color = '#ff4d4f'; // 红色警戒
      } else if (this.value >= this.warningValue * 0.9) {
        color = '#faad14'; // 黄色提醒
      }
      
      return {
        height: `${percentage}%`,
        backgroundColor: color
      };
    }
  }
});
```

**局部注册**：局部注册的组件只能在当前注册它的Vue实例中使用。

```javascript
const StationCard = {
  props: ['station'],
  template: `
    <div class="station-card" :class="station.status">
      <h3>{{ station.name }}</h3>
      <div class="station-data">
        <p>水位: {{ station.waterLevel }}米</p>
        <p>流量: {{ station.flowRate }}立方米/秒</p>
      </div>
    </div>
  `
};

new Vue({
  el: '#app',
  components: {
    'station-card': StationCard
  },
  data: {
    stations: [
      /* 站点数据 */
    ]
  }
});
```

### 3.1.2 单文件组件

在实际开发中，Vue更常用的是`.vue`单文件组件，它将组件的模板、逻辑和样式封装在一个文件中。

```vue
<!-- WaterLevelGauge.vue -->
<template>
  <div class="water-gauge">
    <div class="gauge-container">
      <div class="water-fill" :style="{ height: waterPercentage + '%', backgroundColor: waterColor }"></div>
    </div>
    <div class="gauge-reading">{{ waterLevel }}m</div>
    <div class="gauge-labels">
      <span class="max-label">{{ maxLevel }}m</span>
      <span class="min-label">{{ minLevel }}m</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WaterLevelGauge',
  props: {
    waterLevel: {
      type: Number,
      required: true
    },
    maxLevel: {
      type: Number,
      default: 100
    },
    minLevel: {
      type: Number,
      default: 0
    },
    warningLevel: {
      type: Number,
      default: 90
    }
  },
  computed: {
    waterPercentage() {
      return ((this.waterLevel - this.minLevel) / (this.maxLevel - this.minLevel)) * 100;
    },
    waterColor() {
      if (this.waterLevel >= this.warningLevel) {
        return '#ff4d4f'; // 红色警戒
      } else if (this.waterLevel >= this.warningLevel * 0.9) {
        return '#faad14'; // 黄色提醒
      } else {
        return '#1890ff'; // 蓝色正常
      }
    }
  }
}
</script>

<style scoped>
.water-gauge {
  position: relative;
  width: 100px;
  height: 200px;
  margin: 0 auto;
}

.gauge-container {
  position: relative;
  width: 60px;
  height: 150px;
  border: 2px solid #333;
  border-radius: 8px;
  overflow: hidden;
  margin: 0 auto;
}

.water-fill {
  position: absolute;
  bottom: 0;
  width: 100%;
  transition: height 0.5s ease, background-color 0.5s ease;
}

.gauge-reading {
  text-align: center;
  font-weight: bold;
  margin-top: 5px;
}

.gauge-labels {
  display: flex;
  flex-direction: column;
  position: absolute;
  top: 0;
  right: -30px;
  height: 150px;
  justify-content: space-between;
}
</style>
```

### 3.1.3 Props属性

Props是向子组件传递数据的一种方式。它们类似于自定义HTML属性。

**Prop验证**：可以为prop指定验证要求，增加组件的健壮性。

```javascript
export default {
  props: {
    // 基本类型检查
    stationId: String,
    
    // 必填项校验
    waterLevel: {
      type: Number,
      required: true
    },
    
    // 默认值
    refreshInterval: {
      type: Number,
      default: 60000 // 1分钟
    },
    
    // 自定义验证函数
    alarmThreshold: {
      type: Number,
      validator(value) {
        return value >= 0 && value <= 1000;
      }
    },
    
    // 数组/对象的默认值
    stationConfig: {
      type: Object,
      default() {
        return { 
          showDetails: true,
          displayUnit: 'metric'
        };
      }
    }
  }
}
```

### 3.1.4 智慧水利平台中的组件示例

在智慧水利平台中，可以将各种常见的UI元素和功能封装为组件：

1. **水位计组件**：显示水位数据和警戒状态
2. **流量图表组件**：展示水流量变化趋势
3. **降雨量组件**：显示降雨数据和预测
4. **站点卡片组件**：展示水文站点基本信息
5. **预警通知组件**：显示和管理预警信息

## 3.2 组件通信

在Vue应用中，组件之间的通信是构建复杂界面的关键。

### 3.2.1 父子组件通信

**父组件向子组件传递数据**：通过props向下传递数据

```vue
<!-- 父组件 -->
<template>
  <div class="monitoring-dashboard">
    <h2>{{ stationName }}实时监测</h2>
    <div class="dashboard-grid">
      <div class="gauge-item">
        <h3>水位监测</h3>
        <water-level-gauge 
          :water-level="currentData.waterLevel" 
          :warning-level="warningThresholds.waterLevel"
          :max-level="stationInfo.maxWaterLevel"
          :min-level="stationInfo.minWaterLevel"
        />
      </div>
      <!-- 其他监测项 -->
    </div>
  </div>
</template>

<script>
import WaterLevelGauge from './components/WaterLevelGauge.vue';

export default {
  components: {
    WaterLevelGauge
  },
  data() {
    return {
      stationName: '三峡水文站',
      currentData: {
        waterLevel: 165.4,
        flowRate: 28500,
        precipitation: 15.2
      },
      warningThresholds: {
        waterLevel: 175.0,
        flowRate: 35000,
        precipitation: 50.0
      },
      stationInfo: {
        maxWaterLevel: 185.0,
        minWaterLevel: 145.0
      }
    }
  }
}
</script>
```

**子组件向父组件传递事件**：通过自定义事件向上传递信息

```vue
<!-- 子组件 WaterLevelGauge.vue -->
<template>
  <div class="water-gauge" @click="emitWarning">
    <!-- 组件内容 -->
  </div>
</template>

<script>
export default {
  props: ['waterLevel', 'warningLevel'],
  methods: {
    emitWarning() {
      if (this.waterLevel > this.warningLevel) {
        this.$emit('warning', {
          type: 'waterLevel',
          value: this.waterLevel,
          threshold: this.warningLevel,
          time: new Date().toISOString()
        });
      }
    }
  },
  watch: {
    waterLevel(newValue, oldValue) {
      // 当水位首次超过警戒值时触发预警事件
      if (newValue > this.warningLevel && oldValue <= this.warningLevel) {
        this.$emit('warning', {
          type: 'waterLevel',
          value: newValue,
          threshold: this.warningLevel,
          time: new Date().toISOString()
        });
      }
      // 当水位首次低于警戒值时触发安全事件
      else if (newValue <= this.warningLevel && oldValue > this.warningLevel) {
        this.$emit('safe', {
          type: 'waterLevel',
          value: newValue,
          time: new Date().toISOString()
        });
      }
    }
  }
}
</script>
```

**在父组件中接收子组件事件**：

```vue
<!-- 父组件 -->
<template>
  <div class="monitoring-dashboard">
    <water-level-gauge 
      :water-level="currentData.waterLevel" 
      :warning-level="warningThresholds.waterLevel"
      @warning="handleWarning"
      @safe="handleSafe"
    />
  </div>
</template>

<script>
export default {
  // ...
  methods: {
    handleWarning(data) {
      console.log(`接收到警告：${data.type}超过警戒值，当前值：${data.value}`);
      this.alertSystem.addAlert({
        message: `${this.stationName}水位超过警戒线！当前水位：${data.value}米`,
        level: 'danger',
        time: data.time
      });
    },
    handleSafe(data) {
      console.log(`接收到安全通知：${data.type}恢复正常，当前值：${data.value}`);
      this.alertSystem.addNotification({
        message: `${this.stationName}水位恢复正常，当前水位：${data.value}米`,
        level: 'info',
        time: data.time
      });
    }
  }
}
</script>
```

### 3.2.2 非父子组件通信

在智慧水利平台的复杂界面中，经常需要非父子组件之间的通信：

**事件总线（EventBus）**：用于任意组件间的通信

```javascript
// 创建事件总线
const EventBus = new Vue();

// 组件A：发送事件
export default {
  methods: {
    sendAlertToSystem() {
      EventBus.$emit('global-water-alert', {
        stationId: this.stationId,
        waterLevel: this.waterLevel,
        timestamp: Date.now()
      });
    }
  }
}

// 组件B：接收事件
export default {
  created() {
    EventBus.$on('global-water-alert', (data) => {
      this.processAlert(data);
    });
  },
  beforeDestroy() {
    // 清理事件监听
    EventBus.$off('global-water-alert');
  },
  methods: {
    processAlert(data) {
      // 处理接收到的预警数据
    }
  }
}
```

**Vuex状态管理**：适用于大型应用的状态管理（详见进阶特性部分）

**依赖注入（Provide/Inject）**：适用于深层嵌套组件

```javascript
// 祖先组件提供数据
export default {
  provide() {
    return {
      waterSystemConfig: this.systemConfig,
      updateInterval: this.updateInterval
    };
  },
  data() {
    return {
      systemConfig: {
        units: 'metric',
        displayMode: 'detailed',
        refreshEnabled: true
      },
      updateInterval: 30000
    };
  }
}

// 深层嵌套的后代组件注入数据
export default {
  inject: ['waterSystemConfig', 'updateInterval'],
  created() {
    console.log(this.waterSystemConfig, this.updateInterval);
    this.setupRefreshTimer(this.updateInterval);
  }
}
```

## 3.3 插槽

插槽（Slots）是Vue的一个强大特性，它允许父组件向子组件传递内容，使组件更加灵活和可复用。

### 3.3.1 默认插槽

最基本的插槽用法，子组件提供一个插槽位置，父组件可以向其传入任意内容。

```vue
<!-- 数据面板组件 DataPanel.vue -->
<template>
  <div class="data-panel">
    <div class="panel-header">
      <h3>{{ title }}</h3>
    </div>
    <div class="panel-body">
      <!-- 默认插槽 -->
      <slot></slot>
    </div>
    <div class="panel-footer">
      <p>最后更新: {{ lastUpdated }}</p>
    </div>
  </div>
</template>

<!-- 使用数据面板组件 -->
<data-panel title="水库数据" :last-updated="updateTime">
  <div class="reservoir-data">
    <p>当前水位: {{ waterLevel }}米</p>
    <p>蓄水量: {{ storageVolume }}亿立方米</p>
    <p>入库流量: {{ inflowRate }}立方米/秒</p>
  </div>
</data-panel>
```

### 3.3.2 具名插槽

当需要在组件中提供多个插槽位置时，可以使用具名插槽。

```vue
<!-- 可重用的数据面板组件 -->
<template>
  <div class="data-panel">
    <div class="panel-header">
      <!-- 具名插槽：header -->
      <slot name="header">
        <h3>{{ title }}</h3>
      </slot>
    </div>
    <div class="panel-body">
      <!-- 默认插槽 -->
      <slot></slot>
    </div>
    <div class="panel-footer">
      <!-- 具名插槽：footer -->
      <slot name="footer">
        <p class="update-time">最后更新: {{ lastUpdated }}</p>
      </slot>
    </div>
  </div>
</template>

<!-- 使用数据面板组件 -->
<data-panel title="水库水情">
  <!-- 使用v-slot指令指定插槽名称 -->
  <template v-slot:header>
    <div class="custom-header">
      <h3>{{ reservoir.name }} - 水情监测</h3>
      <div class="status-indicator" :class="statusClass"></div>
    </div>
  </template>
  
  <!-- 默认插槽内容 -->
  <div class="reservoir-data">
    <p>当前水位: {{ reservoir.waterLevel }}米</p>
    <p>蓄水量: {{ reservoir.storage }}亿立方米</p>
    <p>入库流量: {{ reservoir.inflowRate }}立方米/秒</p>
    <p>出库流量: {{ reservoir.outflowRate }}立方米/秒</p>
  </div>
  
  <!-- 缩写形式 #footer -->
  <template #footer>
    <div class="custom-footer">
      <p>更新时间: {{ formatTime(reservoir.updateTime) }}</p>
      <button @click="refreshData">刷新</button>
    </div>
  </template>
</data-panel>
```

### 3.3.3 作用域插槽

作用域插槽允许子组件向父组件传递数据，使插槽内容能够访问子组件中的数据。

```vue
<!-- 水文站列表组件 StationList.vue -->
<template>
  <div class="station-list">
    <h3>{{ title }}</h3>
    <ul class="list-container">
      <li v-for="station in stations" :key="station.id">
        <!-- 作用域插槽：将station数据传递给父组件 -->
        <slot name="station-item" :station="station" :status="getStationStatus(station)">
          <!-- 默认显示内容 -->
          <span>{{ station.name }}: {{ station.waterLevel }}米</span>
        </slot>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: '水文站列表'
    },
    stations: {
      type: Array,
      required: true
    }
  },
  methods: {
    getStationStatus(station) {
      // 根据水位判断站点状态
      if (station.waterLevel > station.warningLevel) {
        return 'danger';
      } else if (station.waterLevel > station.warningLevel * 0.9) {
        return 'warning';
      }
      return 'normal';
    }
  }
}
</script>

<!-- 使用水文站列表组件 -->
<station-list :stations="riverStations" title="黄河流域水文站">
  <!-- 接收作用域插槽传递的数据 -->
  <template #station-item="{ station, status }">
    <div class="custom-station-item" :class="status">
      <div class="station-name">{{ station.name }}</div>
      <div class="station-data">
        <div class="water-level">水位: {{ station.waterLevel }}米</div>
        <div class="flow-rate">流量: {{ station.flowRate }}立方米/秒</div>
      </div>
      <div class="station-status">
        状态: <span :class="`status-${status}`">{{ getStatusText(status) }}</span>
      </div>
      <div class="station-actions">
        <button @click="viewDetails(station.id)">查看详情</button>
      </div>
    </div>
  </template>
</station-list>
```

### 3.3.4 在智慧水利平台中的应用

插槽在智慧水利平台开发中有广泛的应用场景：

1. **数据展示面板**：创建统一风格的数据面板，但允许不同内容的灵活展示
2. **预警通知组件**：统一预警组件的样式和行为，但根据不同类型的预警显示不同内容
3. **图表包装器**：封装图表组件的通用逻辑（如加载状态、错误处理），但允许不同的图表实现
4. **表格组件**：提供通用的表格功能，但允许自定义每一行的展示方式
5. **布局组件**：创建页面布局框架，但允许各个区域内容的自定义
