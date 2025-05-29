# 5.4.3 Spring Boot项目构建

## 创建Spring Boot项目

**方式1：Spring Initializr**
- 访问https://start.spring.io/
- 选择项目类型、语言、Spring Boot版本
- 添加依赖
- 生成并下载项目

**方式2：IDE集成**
- IntelliJ IDEA: File > New > Project > Spring Initializr
- Eclipse/STS: File > New > Spring Starter Project

**方式3：命令行**
```bash
spring init --dependencies=web,data-jpa,security,mysql water-monitoring
```

## 项目结构

典型的Spring Boot项目结构：

```
water-monitoring/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── waterplatform/
│   │   │           ├── WaterMonitoringApplication.java
│   │   │           ├── config/
│   │   │           ├── controller/
│   │   │           ├── service/
│   │   │           ├── repository/
│   │   │           ├── entity/
│   │   │           ├── dto/
│   │   │           ├── exception/
│   │   │           └── util/
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       ├── application-prod.yml
│   │       ├── static/
│   │       └── templates/
│   └── test/
│       └── java/
│           └── com/
│               └── waterplatform/
│                   └── ...
├── pom.xml
└── README.md
```

## 核心配置

**主应用类**：
```java
package com.waterplatform;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling  // 启用定时任务，用于定期获取水文数据
public class WaterMonitoringApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(WaterMonitoringApplication.class, args);
    }
}
```

**多环境配置**：
```yaml
# application.yml (公共配置)
spring:
  profiles:
    active: dev  # 默认激活开发环境配置

# application-dev.yml (开发环境)
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/water_monitoring_dev
    
logging:
  level:
    com.waterplatform: DEBUG

# application-prod.yml (生产环境)
spring:
  datasource:
    url: jdbc:mysql://prod-db-server:3306/water_monitoring
    
logging:
  level:
    com.waterplatform: INFO
```

## 依赖注入与Bean管理

Spring Boot使用注解进行依赖注入和Bean管理。

**常用注解**：
- @Component：通用组件
- @Service：业务逻辑层
- @Repository：数据访问层
- @Controller/@RestController：控制器
- @Configuration：配置类
- @Bean：在配置类中声明Bean
- @Autowired：注入依赖

**示例**：
```java
// 配置类
@Configuration
public class AppConfig {
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

// 服务类
@Service
public class WaterLevelServiceImpl implements WaterLevelService {
    
    @Autowired
    private WaterLevelRepository repository;
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Override
    public List<WaterLevelData> getLatestData(String stationId) {
        // 业务逻辑实现
    }
}
``` 