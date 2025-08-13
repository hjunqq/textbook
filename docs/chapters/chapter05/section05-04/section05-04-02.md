# 5.4.2 Spring Boot核心特性

## 自动配置

Spring Boot自动配置机制基于条件注解，会根据类路径上的依赖和配置自动配置Spring应用。

**原理**：通过@EnableAutoConfiguration注解和spring.factories机制实现

**示例**：
```java
// 无需手动配置数据源，Spring Boot自动配置
@SpringBootApplication
public class WaterMonitoringApplication {
    public static void main(String[] args) {
        SpringApplication.run(WaterMonitoringApplication.class, args);
    }
}
```

## Starter依赖

Starter是一组依赖描述，旨在简化依赖管理和快速引入特定功能。

**常用Starter**：
- spring-boot-starter-web：Web应用开发
- spring-boot-starter-data-jpa：数据库访问
- spring-boot-starter-security：安全框架
- spring-boot-starter-actuator：监控和管理

**智慧水利平台常用依赖配置**：
```xml
<dependencies>
    <!-- Web应用支持 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- 数据库访问 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    
    <!-- MySQL驱动 -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <scope>runtime</scope>
    </dependency>
    
    <!-- 安全框架 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    
    <!-- 系统监控 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
</dependencies>
```

## 外部化配置

Spring Boot提供多种方式配置应用，支持优先级覆盖机制。

**配置源优先级(从高到低)**：
1. 命令行参数
2. Java系统属性
3. 操作系统环境变量
4. application.properties/application.yml

**配置示例(application.yml)**：
```yaml
server:
  port: 8080
  servlet:
    context-path: /water-api

spring:
  application:
    name: water-monitoring-service
  datasource:
    url: jdbc:mysql://localhost:3306/water_monitoring
    username: water_app
    password: ${DB_PASSWORD}  # 从环境变量读取
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false

# 水利业务配置
water:
  monitor:
    data-refresh-interval: 300  # 秒
    warning-check-interval: 60  # 秒
    threshold:
      water-level-rise-rate: 0.5  # 米/小时
```

## 内嵌Web服务器

Spring Boot内置多种Web服务器，无需单独配置和部署。

**支持的服务器**：
- Tomcat (默认)
- Jetty
- Undertow
- Netty (WebFlux)

**服务器配置**：
```yaml
server:
  port: 8080
  tomcat:
    max-threads: 200
    max-connections: 8192
    connection-timeout: 20000  # 毫秒
```

## 生产就绪特性

Spring Boot提供多种功能简化应用监控和运维。

**主要特性**：
1. **健康检查**：/actuator/health端点
2. **指标收集**：/actuator/metrics端点
3. **环境信息**：/actuator/env端点
4. **日志配置**：/actuator/loggers端点

**Actuator配置**：
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,loggers
  endpoint:
    health:
      show-details: when-authorized
``` 