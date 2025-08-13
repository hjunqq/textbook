# 5.6.1 后端服务配置管理

## 配置管理概述

配置管理是维护系统参数、环境特定设置和服务连接信息的系统化方法。良好的配置管理可以使应用程序更加灵活、可移植和易于维护。

## 配置管理原则

1. **配置与代码分离**
   - 将可变配置从代码中抽离
   - 避免硬编码敏感信息
   - 方便不同环境下部署

2. **环境特定配置**
   - 开发环境(Development)
   - 测试环境(Testing)
   - 预生产环境(Staging)
   - 生产环境(Production)

3. **配置即代码**
   - 将配置文件纳入版本控制
   - 使用基础设施即代码(IaC)工具管理配置
   - 建立配置审计和变更跟踪

## 配置管理方法

1. **基于文件的配置**
   - properties文件
   - YAML文件
   - JSON文件
   - XML文件

   ```yaml
   # application.yml 示例
   spring:
     application:
       name: water-monitoring-service
     profiles:
       active: ${SPRING_PROFILES_ACTIVE:dev}
   
   server:
     port: ${SERVER_PORT:8080}
   
   # 智慧水利平台特定配置
   water:
     monitoring:
       data-refresh-interval: ${DATA_REFRESH_INTERVAL:300}
       warning-threshold: ${WARNING_THRESHOLD:0.8}
       alert-recipients: ${ALERT_RECIPIENTS:admin@waterplatform.com}
   ```

2. **环境变量配置**
   - 操作系统环境变量
   - 容器环境变量
   - 云平台环境变量

   ```bash
   # 环境变量设置示例
   export DATABASE_URL=jdbc:mysql://db-server:3306/waterdb
   export DATABASE_USERNAME=water_app
   export DATABASE_PASSWORD=secret
   export REDIS_HOST=redis-server
   export REDIS_PORT=6379
   ```

3. **集中式配置管理**
   - Spring Cloud Config
   - Apache ZooKeeper
   - HashiCorp Consul
   - Nacos

   ```java
   // Spring Cloud Config客户端示例
   @SpringBootApplication
   @EnableConfigServer
   public class ConfigServerApplication {
       public static void main(String[] args) {
           SpringApplication.run(ConfigServerApplication.class, args);
       }
   }
   ```

4. **敏感信息管理**
   - 环境变量注入
   - 密钥管理服务
   - 加密配置文件

   ```yaml
   # 加密配置示例
   datasource:
     url: jdbc:mysql://localhost:3306/waterdb
     username: water_app
     password: '{cipher}AQA6xqS4TuYE/GbF9h8/5SBl...'
   ```

## Spring Boot配置示例

```java
// 配置属性类
@Component
@ConfigurationProperties(prefix = "water.monitoring")
@Validated
public class MonitoringProperties {
    
    @NotNull
    private Integer dataRefreshInterval;
    
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double warningThreshold;
    
    @Email
    private String alertRecipients;
    
    // getter和setter方法
}

// 使用配置
@Service
public class MonitoringService {
    
    private final MonitoringProperties properties;
    
    @Autowired
    public MonitoringService(MonitoringProperties properties) {
        this.properties = properties;
    }
    
    @Scheduled(fixedRateString = "#{${water.monitoring.data-refresh-interval} * 1000}")
    public void refreshData() {
        // 实现数据刷新逻辑
    }
}
``` 