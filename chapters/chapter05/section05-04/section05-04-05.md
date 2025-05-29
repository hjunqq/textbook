# 5.4.5 智慧水利平台实战案例

## 案例描述

为某流域建设一个水文监测与预警系统，实现以下功能：
1. 水文站点管理
2. 实时水位数据采集与存储
3. 历史数据查询与分析
4. 超警戒水位自动预警
5. 数据可视化API接口

## 系统架构

```
智慧水利监测系统
├── 前端应用层：Vue.js + ECharts
├── 后端服务层：Spring Boot REST API
├── 业务逻辑层：水文数据处理、预警算法
├── 数据访问层：Spring Data JPA
├── 数据存储层：MySQL + Redis
└── 外部集成：气象数据API、短信服务
```

## 核心代码示例

**定时任务采集水位数据**：
```java
@Service
@EnableScheduling
public class DataCollectionService {
    
    @Autowired
    private WaterLevelService waterLevelService;
    
    @Autowired
    private DeviceApiClient deviceApiClient;
    
    @Autowired
    private AlertService alertService;
    
    @Autowired
    private StationService stationService;
    
    @Scheduled(fixedRateString = "${water.monitor.data-refresh-interval}000")
    public void collectWaterLevelData() {
        log.info("开始采集水位数据...");
        
        List<StationDTO> activeStations = stationService.findActiveStations();
        
        for (StationDTO station : activeStations) {
            try {
                // 从设备API获取最新水位数据
                WaterLevelDTO latestData = deviceApiClient.getLatestWaterLevel(station.getDeviceId());
                
                // 记录水位数据
                WaterLevelDTO savedData = waterLevelService.recordWaterLevel(latestData);
                
                // 检查是否超过警戒水位并发送预警
                if (savedData.getWarningLevel()) {
                    alertService.sendWaterLevelAlert(station, savedData);
                }
                
                log.debug("站点{}水位数据采集成功: {}米", station.getName(), latestData.getWaterLevel());
            } catch (Exception e) {
                log.error("站点{}水位数据采集失败: {}", station.getName(), e.getMessage());
            }
        }
        
        log.info("水位数据采集完成");
    }
}
```

**预警服务**：
```java
@Service
public class AlertServiceImpl implements AlertService {
    
    @Autowired
    private AlertRepository alertRepository;
    
    @Autowired
    private SmsService smsService;
    
    @Autowired
    private EmailService emailService;
    
    @Autowired
    private StationService stationService;
    
    @Value("${alert.cooldown-minutes}")
    private int alertCooldownMinutes;
    
    @Override
    public void sendWaterLevelAlert(StationDTO station, WaterLevelDTO waterLevel) {
        // 检查冷却期，避免短时间内重复发送预警
        if (isInCooldownPeriod(station.getId())) {
            log.info("站点{}处于预警冷却期内，本次预警不发送", station.getName());
            return;
        }
        
        // 创建预警记录
        Alert alert = new Alert();
        alert.setStationId(station.getId());
        alert.setAlertType(AlertType.WATER_LEVEL_WARNING);
        alert.setWaterLevel(waterLevel.getWaterLevel());
        alert.setThreshold(station.getWarningLevel());
        alert.setAlertTime(LocalDateTime.now());
        alert.setStatus(AlertStatus.ACTIVE);
        
        alertRepository.save(alert);
        
        // 发送短信预警
        String message = String.format(
                "【水利预警】%s站点水位已达到%.2f米，超过警戒水位%.2f米，请及时处理。",
                station.getName(),
                waterLevel.getWaterLevel(),
                station.getWarningLevel()
        );
        
        List<String> contactNumbers = stationService.getStationContactNumbers(station.getId());
        smsService.sendBatchSms(contactNumbers, message);
        
        // 发送邮件预警
        List<String> contactEmails = stationService.getStationContactEmails(station.getId());
        emailService.sendAlertEmail(
                contactEmails,
                "水位超警戒预警 - " + station.getName(),
                buildAlertEmailContent(station, waterLevel)
        );
        
        log.info("站点{}水位预警已发送，当前水位: {}米，警戒水位: {}米",
                station.getName(), waterLevel.getWaterLevel(), station.getWarningLevel());
    }
    
    private boolean isInCooldownPeriod(String stationId) {
        LocalDateTime cooldownThreshold = LocalDateTime.now().minusMinutes(alertCooldownMinutes);
        return alertRepository.existsByStationIdAndAlertTimeAfterAndAlertType(
                stationId, cooldownThreshold, AlertType.WATER_LEVEL_WARNING);
    }
    
    private String buildAlertEmailContent(StationDTO station, WaterLevelDTO waterLevel) {
        // 构建邮件内容，包括站点信息、水位数据、趋势图链接等
        // ...
        return "";
    }
}
```

**水位趋势分析API**：
```java
@RestController
@RequestMapping("/api/analytics")
public class WaterLevelAnalyticsController {
    
    @Autowired
    private WaterLevelAnalyticsService analyticsService;
    
    @GetMapping("/water-level/trend")
    public ResponseEntity<WaterLevelTrendDTO> getWaterLevelTrend(
            @RequestParam String stationId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTime,
            @RequestParam(defaultValue = "HOUR") TimeGranularity granularity) {
        
        WaterLevelTrendDTO trend = analyticsService.analyzeWaterLevelTrend(
                stationId, startTime, endTime, granularity);
        
        return ResponseEntity.ok(trend);
    }
    
    @GetMapping("/water-level/forecast")
    public ResponseEntity<WaterLevelForecastDTO> getWaterLevelForecast(
            @RequestParam String stationId,
            @RequestParam(defaultValue = "24") Integer hours) {
        
        WaterLevelForecastDTO forecast = analyticsService.forecastWaterLevel(stationId, hours);
        
        return ResponseEntity.ok(forecast);
    }
    
    @GetMapping("/water-level/correlation")
    public ResponseEntity<StationCorrelationDTO> getStationCorrelation(
            @RequestParam String stationId,
            @RequestParam(defaultValue = "5") Integer topCount) {
        
        StationCorrelationDTO correlation = analyticsService.findCorrelatedStations(stationId, topCount);
        
        return ResponseEntity.ok(correlation);
    }
}
```

## 项目实现要点

1. **数据采集与存储**
   - 使用定时任务定期从传感器获取数据
   - 采用分层设计分离业务逻辑和数据访问
   - 使用Redis缓存热点数据提高查询性能

2. **预警机制**
   - 基于规则的实时预警
   - 多渠道通知（短信、邮件、系统内消息）
   - 预警冷却期避免频繁重复预警

3. **数据分析**
   - 水位趋势分析
   - 简单预测模型
   - 站点间关联性分析

4. **系统监控**
   - 使用Spring Boot Actuator监控应用状态
   - 自定义健康指标监控传感器连接状态
   - 操作审计日志记录关键操作 