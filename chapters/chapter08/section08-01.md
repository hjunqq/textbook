# 第一节 水利工程安全监测平台开发

智慧水利工程安全监测平台是现代水利信息化建设的重要组成部分，它综合运用物联网、大数据、云计算、人工智能等前沿技术，实现对水利工程安全状态的实时监测、预警分析和智能管理。本节将以某大型水库安全监测平台为例，详细介绍智慧水利平台开发的完整流程，从需求分析到系统上线的全过程实践。

## 8.1.1 项目背景与需求分析

### 8.1.1.1 项目背景

某省重点水库作为区域防洪、供水、发电的重要枢纽工程，承担着下游100万人口的防洪安全和50万人口的生活用水保障任务。随着气候变化和极端天气事件频发，传统的人工巡检和定期检测已无法满足现代水库安全管理的需要。迫切需要建设一套智能化、数字化的安全监测平台，实现对大坝结构、水文情况、设备运行状态的7×24小时实时监控。

**工程概况**：
- 坝型：混凝土重力坝
- 坝高：128米
- 库容：15.8亿立方米
- 装机容量：300MW
- 监测点位：1200+个传感器节点
- 监测要素：位移、渗压、应力应变、水位、流量、水质等

### 8.1.1.2 业务需求分析

#### 功能性需求

**1. 实时监测需求**
- 自动采集大坝变形、渗流、应力等安全监测数据
- 实时监测库水位、入库流量、出库流量等水文数据
- 监测闸门、泵站、发电机组等设备运行状态
- 监测周边气象条件，包括降雨、风速、气温等

**2. 数据处理需求**
- 海量监测数据的清洗、存储和管理
- 异常数据的自动识别和校正
- 历史数据的趋势分析和规律挖掘
- 多源数据的融合处理和关联分析

**3. 预警分析需求**
- 基于监测数据的安全评价模型
- 多级预警机制（蓝色、黄色、橙色、红色）
- 预警信息的自动推送和应急响应
- 风险评估和安全态势感知

**4. 可视化展示需求**
- 大坝三维模型与监测数据的融合展示
- 实时数据的图表化展示和趋势分析
- 预警信息的直观化表达
- 移动端的便捷查看和操作

**5. 系统管理需求**
- 用户权限管理和角色分配
- 监测设备的远程配置和维护
- 系统日志和操作审计
- 数据备份和灾难恢复

#### 非功能性需求

**1. 性能需求**
- 系统并发用户数：100+
- 数据处理延迟：≤3秒
- 系统可用性：99.9%
- 数据存储：支持PB级数据存储

**2. 安全需求**
- 数据传输加密
- 用户身份认证
- 操作权限控制
- 安全审计日志

**3. 可扩展性需求**
- 支持新增监测点位和设备
- 支持新增监测参数和算法
- 支持与其他系统的集成
- 支持多水库的统一管理

### 8.1.1.3 技术需求分析

#### 架构需求
- 采用微服务架构，确保系统的可扩展性和可维护性
- 前后端分离设计，支持多端访问
- 云原生部署，支持容器化和自动扩缩容
- 采用分布式架构，确保系统的高可用性

#### 技术栈需求
- **前端**：Vue.js + Element UI + ECharts + Cesium
- **后端**：Spring Boot + Spring Cloud + MyBatis Plus
- **数据库**：MySQL + Redis + InfluxDB
- **消息队列**：RabbitMQ
- **大数据**：Spark + Flink
- **容器化**：Docker + Kubernetes

## 8.1.2 系统架构设计

### 8.1.2.1 总体架构

智慧水利工程安全监测平台采用"云-边-端"三层架构，实现从传感器设备到云端服务的全链路数据处理。

```
                    ┌─────────────────────────────────────┐
                    │             云端服务层              │
                    │   ┌─────────────┐ ┌─────────────┐   │
                    │   │  数据服务   │ │  业务服务   │   │
                    │   └─────────────┘ └─────────────┘   │
                    │   ┌─────────────┐ ┌─────────────┐   │
                    │   │  AI算法服务 │ │  可视化服务 │   │
                    │   └─────────────┘ └─────────────┘   │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────────────────────────┐
                    │             边缘计算层              │
                    │   ┌─────────────┐ ┌─────────────┐   │
                    │   │  数据网关   │ │  边缘分析   │   │
                    │   └─────────────┘ └─────────────┘   │
                    │   ┌─────────────┐ ┌─────────────┐   │
                    │   │  协议转换   │ │  本地存储   │   │
                    │   └─────────────┘ └─────────────┘   │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────────────────────────┐
                    │             设备感知层              │
                    │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
                    │ │位移 │ │渗压 │ │应力 │ │水位 │ ...│
                    │ │传感器│ │传感器│ │传感器│ │传感器│   │
                    │ └─────┘ └─────┘ └─────┘ └─────┘   │
                    └─────────────────────────────────────┘
```

### 8.1.2.2 微服务架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                         │
│                   (Spring Cloud Gateway)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
   │用户服务  │      │设备服务   │    │数据服务   │
   │User     │      │Device     │    │Data       │
   │Service  │      │Service    │    │Service    │
   └─────────┘      └───────────┘    └───────────┘
        │                 │                 │
   ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
   │监测服务  │      │预警服务   │    │分析服务   │
   │Monitor  │      │Alert      │    │Analysis   │
   │Service  │      │Service    │    │Service    │
   └─────────┘      └───────────┘    └───────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                    ┌─────▼─────┐
                    │注册中心   │
                    │Eureka     │
                    └───────────┘
```

### 8.1.2.3 数据库设计

#### 核心数据表结构

**1. 监测点位表 (monitoring_points)**
```sql
CREATE TABLE monitoring_points (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    point_code VARCHAR(50) UNIQUE NOT NULL COMMENT '点位编码',
    point_name VARCHAR(100) NOT NULL COMMENT '点位名称',
    point_type VARCHAR(20) NOT NULL COMMENT '点位类型',
    position_x DECIMAL(10,6) COMMENT 'X坐标',
    position_y DECIMAL(10,6) COMMENT 'Y坐标',
    position_z DECIMAL(8,3) COMMENT 'Z坐标',
    sensor_type VARCHAR(50) COMMENT '传感器类型',
    install_date DATE COMMENT '安装日期',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常 0-停用',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**2. 监测数据表 (monitoring_data)**
```sql
CREATE TABLE monitoring_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    point_id BIGINT NOT NULL COMMENT '监测点位ID',
    measure_time TIMESTAMP NOT NULL COMMENT '测量时间',
    parameter_code VARCHAR(20) NOT NULL COMMENT '参数编码',
    parameter_value DECIMAL(12,4) COMMENT '参数值',
    parameter_unit VARCHAR(10) COMMENT '参数单位',
    data_quality TINYINT DEFAULT 1 COMMENT '数据质量：1-正常 2-可疑 3-错误',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_point_time (point_id, measure_time),
    INDEX idx_measure_time (measure_time)
);
```

**3. 预警规则表 (alert_rules)**
```sql
CREATE TABLE alert_rules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    point_type VARCHAR(20) NOT NULL COMMENT '适用点位类型',
    parameter_code VARCHAR(20) NOT NULL COMMENT '监测参数',
    alert_level TINYINT NOT NULL COMMENT '预警级别：1-蓝色 2-黄色 3-橙色 4-红色',
    threshold_value DECIMAL(12,4) COMMENT '阈值',
    threshold_type TINYINT COMMENT '阈值类型：1-上限 2-下限 3-变化率',
    status TINYINT DEFAULT 1 COMMENT '状态：1-启用 0-禁用',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 8.1.3 核心功能实现

### 8.1.3.1 数据采集服务实现

#### 数据采集微服务

```java
@RestController
@RequestMapping("/api/data-collection")
@Slf4j
public class DataCollectionController {
    
    @Autowired
    private DataCollectionService dataCollectionService;
    
    /**
     * 批量接收监测数据
     */
    @PostMapping("/batch")
    public Result<Void> batchReceiveData(@RequestBody List<MonitoringDataDTO> dataList) {
        try {
            dataCollectionService.batchProcessData(dataList);
            return Result.success();
        } catch (Exception e) {
            log.error("批量数据处理失败", e);
            return Result.error("数据处理失败：" + e.getMessage());
        }
    }
    
    /**
     * 实时数据接收
     */
    @PostMapping("/realtime")
    public Result<Void> receiveRealtimeData(@RequestBody MonitoringDataDTO data) {
        try {
            dataCollectionService.processRealtimeData(data);
            return Result.success();
        } catch (Exception e) {
            log.error("实时数据处理失败", e);
            return Result.error("数据处理失败：" + e.getMessage());
        }
    }
}

@Service
@Transactional
public class DataCollectionServiceImpl implements DataCollectionService {
    
    @Autowired
    private MonitoringDataMapper monitoringDataMapper;
    
    @Autowired
    private DataValidationService dataValidationService;
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    @Override
    public void batchProcessData(List<MonitoringDataDTO> dataList) {
        // 数据验证
        List<MonitoringData> validDataList = new ArrayList<>();
        for (MonitoringDataDTO dto : dataList) {
            if (dataValidationService.validate(dto)) {
                MonitoringData data = convertToEntity(dto);
                validDataList.add(data);
            }
        }
        
        // 批量插入数据库
        if (!validDataList.isEmpty()) {
            monitoringDataMapper.batchInsert(validDataList);
            
            // 发送消息到预警服务
            for (MonitoringData data : validDataList) {
                rabbitTemplate.convertAndSend("alert.exchange", 
                    "data.received", data);
            }
        }
    }
    
    @Override
    public void processRealtimeData(MonitoringDataDTO dto) {
        // 实时数据处理
        if (dataValidationService.validate(dto)) {
            MonitoringData data = convertToEntity(dto);
            
            // 存储到数据库
            monitoringDataMapper.insert(data);
            
            // 存储到Redis缓存（用于实时展示）
            redisTemplate.opsForValue().set(
                "realtime:data:" + data.getPointId(), 
                data, 300, TimeUnit.SECONDS);
            
            // 发送实时数据到WebSocket
            websocketService.broadcastData(data);
            
            // 触发预警检查
            rabbitTemplate.convertAndSend("alert.exchange", 
                "data.realtime", data);
        }
    }
}
```

### 8.1.3.2 预警分析服务实现

#### 预警分析引擎

```java
@Component
@RabbitListener(queues = "alert.queue")
@Slf4j
public class AlertAnalysisEngine {
    
    @Autowired
    private AlertRuleService alertRuleService;
    
    @Autowired
    private AlertRecordService alertRecordService;
    
    @Autowired
    private NotificationService notificationService;
    
    /**
     * 处理监测数据，进行预警分析
     */
    @RabbitHandler
    public void analyzeData(MonitoringData data) {
        try {
            // 获取适用的预警规则
            List<AlertRule> rules = alertRuleService.getRulesByPointType(
                data.getPointType(), data.getParameterCode());
            
            for (AlertRule rule : rules) {
                if (checkAlertCondition(data, rule)) {
                    // 生成预警记录
                    AlertRecord alert = createAlertRecord(data, rule);
                    alertRecordService.save(alert);
                    
                    // 发送通知
                    notificationService.sendAlert(alert);
                    
                    log.warn("触发预警 - 点位：{}，参数：{}，级别：{}", 
                        data.getPointCode(), data.getParameterCode(), 
                        rule.getAlertLevel());
                }
            }
        } catch (Exception e) {
            log.error("预警分析失败", e);
        }
    }
    
    /**
     * 检查预警条件
     */
    private boolean checkAlertCondition(MonitoringData data, AlertRule rule) {
        BigDecimal value = data.getParameterValue();
        BigDecimal threshold = rule.getThresholdValue();
        
        switch (rule.getThresholdType()) {
            case 1: // 上限
                return value.compareTo(threshold) > 0;
            case 2: // 下限
                return value.compareTo(threshold) < 0;
            case 3: // 变化率
                return checkChangeRate(data, threshold);
            default:
                return false;
        }
    }
    
    /**
     * 检查变化率
     */
    private boolean checkChangeRate(MonitoringData data, BigDecimal threshold) {
        // 获取上一次的测量值
        MonitoringData lastData = alertRuleService.getLastData(
            data.getPointId(), data.getParameterCode());
        
        if (lastData != null) {
            BigDecimal changeRate = data.getParameterValue()
                .subtract(lastData.getParameterValue())
                .divide(lastData.getParameterValue(), 4, RoundingMode.HALF_UP)
                .multiply(new BigDecimal("100"));
            
            return changeRate.abs().compareTo(threshold) > 0;
        }
        
        return false;
    }
}
```

### 8.1.3.3 三维可视化实现

#### 前端三维场景组件

```vue
<template>
  <div class="monitoring-3d-view">
    <div id="cesiumContainer" class="cesium-container"></div>
    
    <!-- 控制面板 -->
    <div class="control-panel">
      <el-card>
        <h3>监测点位控制</h3>
        <el-tree
          :data="monitoringPoints"
          :props="treeProps"
          show-checkbox
          @check="onPointCheck"
        />
      </el-card>
      
      <el-card>
        <h3>预警信息</h3>
        <div v-for="alert in alerts" :key="alert.id" 
             :class="['alert-item', 'level-' + alert.level]">
          <div class="alert-title">{{ alert.pointName }}</div>
          <div class="alert-content">{{ alert.message }}</div>
          <div class="alert-time">{{ alert.createTime }}</div>
        </div>
      </el-card>
    </div>
    
    <!-- 数据面板 -->
    <div class="data-panel" v-if="selectedPoint">
      <el-card>
        <h3>{{ selectedPoint.pointName }}</h3>
        <div class="data-charts">
          <div ref="trendChart" class="trend-chart"></div>
        </div>
        
        <el-table :data="selectedPoint.realtimeData" size="small">
          <el-table-column prop="parameterName" label="参数" width="120"/>
          <el-table-column prop="value" label="当前值" width="100"/>
          <el-table-column prop="unit" label="单位" width="80"/>
          <el-table-column prop="updateTime" label="更新时间"/>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script>
import * as Cesium from 'cesium'
import * as echarts from 'echarts'

export default {
  name: 'Monitoring3DView',
  data() {
    return {
      viewer: null,
      monitoringPoints: [],
      alerts: [],
      selectedPoint: null,
      trendChart: null,
      pointEntities: new Map(),
      treeProps: {
        children: 'children',
        label: 'name'
      }
    }
  },
  
  mounted() {
    this.initCesium()
    this.loadMonitoringPoints()
    this.initWebSocket()
    this.loadAlerts()
  },
  
  methods: {
    /**
     * 初始化Cesium三维场景
     */
    initCesium() {
      // 设置Cesium访问令牌
      Cesium.Ion.defaultAccessToken = 'your_cesium_access_token'
      
      // 创建Cesium Viewer
      this.viewer = new Cesium.Viewer('cesiumContainer', {
        terrainProvider: Cesium.createWorldTerrain(),
        skyBox: new Cesium.SkyBox({
          sources: {
            positiveX: '/assets/skybox/TychoSkymapII.t3_08192x04096_80_px.jpg',
            negativeX: '/assets/skybox/TychoSkymapII.t3_08192x04096_80_mx.jpg',
            positiveY: '/assets/skybox/TychoSkymapII.t3_08192x04096_80_py.jpg',
            negativeY: '/assets/skybox/TychoSkymapII.t3_08192x04096_80_my.jpg',
            positiveZ: '/assets/skybox/TychoSkymapII.t3_08192x04096_80_pz.jpg',
            negativeZ: '/assets/skybox/TychoSkymapII.t3_08192x04096_80_mz.jpg'
          }
        })
      })
      
      // 加载大坝三维模型
      this.loadDamModel()
      
      // 设置相机位置
      this.viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(116.3974, 39.9093, 1000),
        orientation: {
          heading: Cesium.Math.toRadians(0),
          pitch: Cesium.Math.toRadians(-30),
          roll: 0.0
        }
      })
    },
    
    /**
     * 加载大坝三维模型
     */
    async loadDamModel() {
      try {
        const damModel = await Cesium.Model.fromGltf({
          url: '/assets/models/dam_model.gltf',
          modelMatrix: Cesium.Transforms.eastNorthUpToFixedFrame(
            Cesium.Cartesian3.fromDegrees(116.3974, 39.9093, 0)
          )
        })
        
        this.viewer.scene.primitives.add(damModel)
      } catch (error) {
        console.error('加载大坝模型失败:', error)
      }
    },
    
    /**
     * 加载监测点位
     */
    async loadMonitoringPoints() {
      try {
        const response = await this.$api.get('/monitoring/points')
        this.monitoringPoints = response.data
        
        // 在三维场景中添加监测点位
        this.addPointsToScene()
      } catch (error) {
        this.$message.error('加载监测点位失败')
      }
    },
    
    /**
     * 在三维场景中添加监测点位
     */
    addPointsToScene() {
      this.monitoringPoints.forEach(point => {
        const entity = this.viewer.entities.add({
          id: point.id,
          position: Cesium.Cartesian3.fromDegrees(
            point.longitude, point.latitude, point.elevation
          ),
          point: {
            pixelSize: 10,
            color: this.getPointColor(point.status),
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2,
            heightReference: Cesium.HeightReference.RELATIVE_TO_GROUND
          },
          label: {
            text: point.pointName,
            font: '14pt monospace',
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            outlineWidth: 2,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            pixelOffset: new Cesium.Cartesian2(0, -30),
            heightReference: Cesium.HeightReference.RELATIVE_TO_GROUND
          }
        })
        
        this.pointEntities.set(point.id, entity)
      })
      
      // 添加点击事件
      this.viewer.cesiumWidget.screenSpaceEventHandler.setInputAction(
        this.onPointClick.bind(this),
        Cesium.ScreenSpaceEventType.LEFT_CLICK
      )
    },
    
    /**
     * 获取点位颜色（根据状态）
     */
    getPointColor(status) {
      switch (status) {
        case 'normal': return Cesium.Color.GREEN
        case 'warning': return Cesium.Color.YELLOW
        case 'alert': return Cesium.Color.RED
        case 'offline': return Cesium.Color.GRAY
        default: return Cesium.Color.WHITE
      }
    },
    
    /**
     * 点位点击事件
     */
    onPointClick(event) {
      const picked = this.viewer.scene.pick(event.position)
      if (picked && picked.id) {
        const pointId = picked.id.id
        this.selectPoint(pointId)
      }
    },
    
    /**
     * 选择监测点位
     */
    async selectPoint(pointId) {
      try {
        const response = await this.$api.get(`/monitoring/points/${pointId}/detail`)
        this.selectedPoint = response.data
        
        // 绘制趋势图
        this.drawTrendChart()
        
        // 高亮选中的点位
        this.highlightPoint(pointId)
      } catch (error) {
        this.$message.error('获取点位详情失败')
      }
    },
    
    /**
     * 绘制趋势图
     */
    drawTrendChart() {
      if (!this.selectedPoint.trendData) return
      
      this.$nextTick(() => {
        if (this.trendChart) {
          this.trendChart.dispose()
        }
        
        this.trendChart = echarts.init(this.$refs.trendChart)
        
        const option = {
          title: {
            text: '监测数据趋势',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: this.selectedPoint.trendData.parameters
          },
          xAxis: {
            type: 'time',
            data: this.selectedPoint.trendData.times
          },
          yAxis: {
            type: 'value'
          },
          series: this.selectedPoint.trendData.parameters.map(param => ({
            name: param.name,
            type: 'line',
            data: param.values
          }))
        }
        
        this.trendChart.setOption(option)
      })
    },
    
    /**
     * 初始化WebSocket连接
     */
    initWebSocket() {
      const ws = new WebSocket('ws://localhost:8080/ws/monitoring')
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'realtime_data') {
          this.updateRealtimeData(data.payload)
        } else if (data.type === 'alert') {
          this.handleAlert(data.payload)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket连接错误:', error)
        this.$message.error('实时数据连接失败')
      }
    },
    
    /**
     * 更新实时数据
     */
    updateRealtimeData(data) {
      // 更新点位颜色
      const entity = this.pointEntities.get(data.pointId)
      if (entity) {
        entity.point.color = this.getPointColor(data.status)
      }
      
      // 如果是当前选中的点位，更新详情面板
      if (this.selectedPoint && this.selectedPoint.id === data.pointId) {
        this.selectedPoint.realtimeData = data.parameters
      }
    },
    
    /**
     * 处理预警信息
     */
    handleAlert(alert) {
      // 添加到预警列表
      this.alerts.unshift(alert)
      
      // 更新点位状态
      const entity = this.pointEntities.get(alert.pointId)
      if (entity) {
        entity.point.color = this.getAlertColor(alert.level)
        
        // 添加闪烁效果
        this.addBlinkEffect(entity, alert.level)
      }
      
      // 显示通知
      this.$notify({
        title: `${alert.levelName}预警`,
        message: `${alert.pointName}: ${alert.message}`,
        type: 'warning',
        duration: 0
      })
    },
    
    /**
     * 获取预警颜色
     */
    getAlertColor(level) {
      switch (level) {
        case 1: return Cesium.Color.BLUE
        case 2: return Cesium.Color.YELLOW
        case 3: return Cesium.Color.ORANGE
        case 4: return Cesium.Color.RED
        default: return Cesium.Color.WHITE
      }
    },
    
    /**
     * 添加闪烁效果
     */
    addBlinkEffect(entity, level) {
      const originalColor = entity.point.color.getValue()
      const alertColor = this.getAlertColor(level)
      
      let isVisible = true
      const blinkInterval = setInterval(() => {
        entity.point.color = isVisible ? alertColor : originalColor
        isVisible = !isVisible
      }, 500)
      
      // 5秒后停止闪烁
      setTimeout(() => {
        clearInterval(blinkInterval)
        entity.point.color = alertColor
      }, 5000)
    }
  }
}
</script>

<style scoped>
.monitoring-3d-view {
  position: relative;
  width: 100%;
  height: 100vh;
}

.cesium-container {
  width: 100%;
  height: 100%;
}

.control-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 300px;
  max-height: 60vh;
  overflow-y: auto;
  z-index: 1000;
}

.control-panel .el-card {
  margin-bottom: 10px;
}

.data-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 400px;
  max-height: 80vh;
  overflow-y: auto;
  z-index: 1000;
}

.trend-chart {
  width: 100%;
  height: 300px;
}

.alert-item {
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  background-color: #f5f5f5;
}

.alert-item.level-1 { border-left: 4px solid #409eff; }
.alert-item.level-2 { border-left: 4px solid #e6a23c; }
.alert-item.level-3 { border-left: 4px solid #f56c6c; }
.alert-item.level-4 { border-left: 4px solid #ff0000; }

.alert-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.alert-content {
  font-size: 14px;
  color: #666;
}

.alert-time {
  font-size: 12px;
  color: #999;
  text-align: right;
  margin-top: 5px;
}
</style>
```

## 8.1.4 系统部署与运维

### 8.1.4.1 容器化部署

#### Docker配置文件

```dockerfile
# 后端服务Dockerfile
FROM openjdk:11-jre-slim

LABEL maintainer="water-platform@example.com"

WORKDIR /app

COPY target/water-monitoring-*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

#### Docker Compose配置

```yaml
version: '3.8'

services:
  # MySQL数据库
  mysql:
    image: mysql:8.0
    container_name: water-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: water_monitoring
      MYSQL_USER: water_user
      MYSQL_PASSWORD: water_pass
    volumes:
      - mysql_data:/var/lib/mysql
      - ./sql:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
    networks:
      - water-network

  # Redis缓存
  redis:
    image: redis:6.2-alpine
    container_name: water-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - water-network

  # RabbitMQ消息队列
  rabbitmq:
    image: rabbitmq:3.9-management
    container_name: water-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin123
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - water-network

  # 后端服务
  water-backend:
    build: .
    container_name: water-backend
    environment:
      SPRING_PROFILES_ACTIVE: docker
      MYSQL_HOST: mysql
      REDIS_HOST: redis
      RABBITMQ_HOST: rabbitmq
    ports:
      - "8080:8080"
    depends_on:
      - mysql
      - redis
      - rabbitmq
    networks:
      - water-network

  # 前端服务
  water-frontend:
    image: nginx:alpine
    container_name: water-frontend
    volumes:
      - ./dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - water-backend
    networks:
      - water-network

volumes:
  mysql_data:
  redis_data:
  rabbitmq_data:

networks:
  water-network:
    driver: bridge
```

### 8.1.4.2 监控告警

#### 系统监控配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'water-monitoring'
    static_configs:
      - targets: ['water-backend:8080']
    metrics_path: '/actuator/prometheus'

  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql:3306']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

#### 告警规则配置

```yaml
# alert_rules.yml
groups:
  - name: water_monitoring_alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务 {{ $labels.instance }} 已停止"
          description: "{{ $labels.job }} 服务已停止超过1分钟"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "主机 {{ $labels.instance }} 内存使用率已达 {{ $value }}%"

      - alert: HighCPUUsage
        expr: 100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "CPU使用率过高"
          description: "主机 {{ $labels.instance }} CPU使用率已达 {{ $value }}%"

      - alert: DatabaseConnectionPoolHigh
        expr: hikaricp_connections_active / hikaricp_connections_max * 100 > 80
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "数据库连接池使用率过高"
          description: "数据库连接池使用率已达 {{ $value }}%"
```

## 8.1.5 项目总结与思考

### 8.1.5.1 技术成果

通过本项目的开发实践，我们成功构建了一套完整的智慧水利工程安全监测平台，主要技术成果包括：

1. **分布式架构设计**：采用微服务架构，实现了系统的高可用性和可扩展性
2. **实时数据处理**：建立了从数据采集到存储、分析、预警的完整数据流水线
3. **三维可视化**：集成Cesium三维引擎，实现了工程空间信息的立体展示
4. **智能预警**：构建了多级预警体系和智能分析算法
5. **移动端适配**：支持PC端和移动端的跨平台访问

### 8.1.5.2 关键技术要点

1. **微服务架构的应用**
   - 服务拆分策略和领域边界划分
   - 服务间通信和数据一致性处理
   - 分布式配置管理和服务发现

2. **实时数据处理技术**
   - 消息队列的异步处理机制
   - 流式数据处理和批处理结合
   - 数据质量控制和异常处理

3. **三维可视化技术**
   - WebGL在浏览器中的应用
   - 大规模三维场景的性能优化
   - 多源空间数据的融合展示

4. **前后端分离开发**
   - RESTful API设计规范
   - 前端组件化开发模式
   - 响应式设计和用户体验优化

### 8.1.5.3 工程价值

1. **技术价值**
   - 探索了智慧水利平台的技术实现路径
   - 验证了现代Web技术在水利行业的应用可行性
   - 建立了可复制的技术架构模式

2. **应用价值**
   - 提升了水利工程安全监测的自动化水平
   - 增强了应急响应和决策支持能力
   - 降低了运维成本和人工巡检风险

3. **示范价值**
   - 为其他水利工程提供了数字化改造参考
   - 推动了传统水利向智慧水利的转型
   - 培养了复合型技术人才

### 8.1.5.4 技术发展趋势

1. **人工智能深度融合**
   - 机器学习在异常检测中的应用
   - 深度学习在图像识别和模式分析中的应用
   - 数字孪生技术的进一步发展

2. **边缘计算的普及**
   - 边缘设备的智能化升级
   - 云边协同的计算架构
   - 5G网络在水利物联网中的应用

3. **标准化和规范化**
   - 水利信息化标准的完善
   - 数据格式和接口的统一
   - 安全规范和合规要求的提升

通过本节的学习和实践，学生不仅掌握了智慧水利平台开发的核心技术，更重要的是培养了系统性思维和工程实践能力，为今后从事智慧水利建设工作奠定了坚实基础。

