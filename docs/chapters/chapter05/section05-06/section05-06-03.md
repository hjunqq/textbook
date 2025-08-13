# 5.6.3 容器化技术

## Docker基础

Docker是一种开源的容器化平台，允许开发者将应用程序及其依赖打包到标准化的单元(容器)中，实现"一次构建，到处运行"的理念。

**核心概念**：
- **容器(Container)**：应用程序运行的独立实例
- **镜像(Image)**：容器的静态模板
- **Dockerfile**：构建镜像的脚本
- **仓库(Registry)**：存储和分发镜像的服务

## Dockerfile示例

```dockerfile
# 基础镜像
FROM openjdk:17-slim

# 元数据
LABEL maintainer="devteam@waterplatform.com"
LABEL description="Water Monitoring Service"

# 工作目录
WORKDIR /app

# 拷贝构建产物
COPY target/water-monitoring-service.jar app.jar

# 环境变量
ENV SPRING_PROFILES_ACTIVE=prod
ENV SERVER_PORT=8080

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# 启动命令
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Docker Compose

Docker Compose是一个用于定义和运行多容器Docker应用程序的工具。

**docker-compose.yml示例**：

```yaml
version: '3.8'

services:
  water-monitoring-service:
    build: .
    image: waterplatform/monitoring-service:latest
    container_name: water-monitoring-service
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DATABASE_URL=jdbc:mysql://mysql:3306/waterdb
      - DATABASE_USERNAME=water_app
      - DATABASE_PASSWORD=secret
    depends_on:
      - mysql
      - redis
    restart: unless-stopped
    networks:
      - water-net
    volumes:
      - ./logs:/app/logs
      
  mysql:
    image: mysql:8.0
    container_name: water-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=waterdb
      - MYSQL_USER=water_app
      - MYSQL_PASSWORD=secret
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
    networks:
      - water-net
      
  redis:
    image: redis:6.2-alpine
    container_name: water-redis
    ports:
      - "6379:6379"
    networks:
      - water-net
    volumes:
      - redis-data:/data

networks:
  water-net:
    driver: bridge

volumes:
  mysql-data:
  redis-data:
```

## 容器镜像管理

1. **镜像仓库**
   - Docker Hub
   - GitHub Container Registry
   - Harbor
   - 阿里云容器镜像服务

2. **镜像标签策略**
   - 语义化版本：major.minor.patch (1.2.3)
   - 提交哈希：git-abcdef1
   - 日期标签：20230615
   - 环境标签：dev, test, prod

3. **镜像安全扫描**
   - Trivy
   - Clair
   - Anchore Engine 