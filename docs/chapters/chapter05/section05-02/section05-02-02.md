# 5.2.2 Java基础与应用

## Java核心特性

1. **面向对象**：封装、继承、多态
2. **跨平台**：一次编写，到处运行
3. **类型安全**：强类型系统
4. **自动内存管理**：垃圾回收机制
5. **多线程**：内置线程支持
6. **丰富的标准库**：集合框架、IO/NIO、并发工具等
7. **注解机制**：简化配置，支持AOP编程

## Java开发环境配置

1. **JDK安装与配置**
   - 下载JDK（推荐版本JDK 8/11/17）
   - 设置JAVA_HOME环境变量
   - 配置PATH变量

2. **开发工具**
   - IntelliJ IDEA
   - Eclipse
   - Maven/Gradle构建工具

3. **项目构建与依赖管理**
   ```xml
   <!-- Maven pom.xml示例 -->
   <dependency>
     <groupId>org.springframework.boot</groupId>
     <artifactId>spring-boot-starter-web</artifactId>
     <version>2.7.0</version>
   </dependency>
   ```

## Java核心框架

1. **Spring Framework**
   - 依赖注入和控制反转
   - 面向切面编程
   - 事务管理

2. **Spring Boot**
   - 自动配置
   - 内嵌服务器
   - 简化部署

3. **Spring Cloud**
   - 服务注册与发现
   - 配置中心
   - 微服务通信

4. **MyBatis/Hibernate**
   - ORM框架
   - 数据库操作简化

## Java基础语法

### 类和对象

```java
// 定义水文站点类
public class HydrologicalStation {
    // 成员变量
    private String stationId;
    private String stationName;
    private double longitude;
    private double latitude;
    private double warningLevel;
    
    // 构造函数
    public HydrologicalStation(String stationId, String stationName, 
                              double longitude, double latitude) {
        this.stationId = stationId;
        this.stationName = stationName;
        this.longitude = longitude;
        this.latitude = latitude;
    }
    
    // getter和setter方法
    public String getStationId() {
        return stationId;
    }
    
    public void setWarningLevel(double warningLevel) {
        this.warningLevel = warningLevel;
    }
    
    // 业务方法
    public boolean isOverWarningLevel(double currentLevel) {
        return currentLevel >= warningLevel;
    }
}
```

### 继承和多态

```java
// 基类：监测点
public abstract class MonitoringPoint {
    protected String pointId;
    protected String location;
    
    public abstract void collectData();
}

// 子类：水位监测点
public class WaterLevelPoint extends MonitoringPoint {
    private double warningLevel;
    
    @Override
    public void collectData() {
        // 实现水位数据采集逻辑
        System.out.println("Collecting water level data...");
    }
}

// 子类：水质监测点
public class WaterQualityPoint extends MonitoringPoint {
    private List<String> parameters;
    
    @Override
    public void collectData() {
        // 实现水质数据采集逻辑
        System.out.println("Collecting water quality data...");
    }
}
```

### 接口和抽象类

```java
// 数据处理接口
public interface DataProcessor {
    void processData(List<Double> data);
    Map<String, Object> getProcessResult();
}

// 具体实现：水位数据处理器
public class WaterLevelProcessor implements DataProcessor {
    private double averageLevel;
    private double maxLevel;
    
    @Override
    public void processData(List<Double> data) {
        // 计算平均水位和最高水位
        this.averageLevel = data.stream().mapToDouble(d -> d).average().orElse(0);
        this.maxLevel = data.stream().mapToDouble(d -> d).max().orElse(0);
    }
    
    @Override
    public Map<String, Object> getProcessResult() {
        Map<String, Object> result = new HashMap<>();
        result.put("averageLevel", averageLevel);
        result.put("maxLevel", maxLevel);
        return result;
    }
}
```

## Java在智慧水利中的典型应用

### 水文信息管理系统

```java
@RestController
@RequestMapping("/api/hydrodata")
public class HydrologicalDataController {
    
    @Autowired
    private HydrologicalDataService dataService;
    
    @GetMapping("/stations")
    public ResponseEntity<List<Station>> getAllStations() {
        return ResponseEntity.ok(dataService.findAllStations());
    }
    
    @GetMapping("/waterLevel/{stationId}")
    public ResponseEntity<List<WaterLevelRecord>> getWaterLevelData(
            @PathVariable String stationId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTime) {
        
        return ResponseEntity.ok(dataService.getWaterLevelData(stationId, startTime, endTime));
    }
}
```

### 水库调度系统

```java
@Service
@Transactional
public class ReservoirSchedulingServiceImpl implements ReservoirSchedulingService {
    
    @Autowired
    private ReservoirRepository reservoirRepo;
    
    @Autowired
    private SchedulingRuleEngine ruleEngine;
    
    @Override
    public SchedulingPlan generateSchedulingPlan(String reservoirId, 
                                             LocalDateTime planStartTime,
                                             LocalDateTime planEndTime,
                                             SchedulingGoal goal) {
        
        Reservoir reservoir = reservoirRepo.findById(reservoirId)
            .orElseThrow(() -> new ResourceNotFoundException("水库不存在"));
        
        // 获取相关数据
        WaterLevelData currentWaterLevel = getLatestWaterLevel(reservoirId);
        WeatherForecast forecast = getWeatherForecast(reservoirId, planStartTime, planEndTime);
        
        // 调用规则引擎生成调度计划
        return ruleEngine.generatePlan(reservoir, currentWaterLevel, forecast, goal);
    }
}
```

## 习题与思考

1. 设计一个基于Java的水文监测系统数据模型，包括监测站点、监测数据、预警规则等核心类。
2. Spring Boot框架如何简化智慧水利平台的开发？请列举其在水利项目中的具体应用案例。
3. 分析Java多线程特性在水利数据采集与处理中的应用场景，并提供示例代码。 