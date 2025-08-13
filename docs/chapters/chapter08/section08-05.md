# 第五节 系统集成与运维管理

## 引言

系统集成与运维管理是智慧水利平台稳定运行的重要保障。随着平台功能的不断完善和用户规模的持续增长，如何确保系统的高可用性、高性能和高安全性，成为运维管理面临的核心挑战。

本节将从系统架构优化、运维监控体系、自动化运维和故障处理等方面，全面介绍智慧水利平台的集成与运维管理实践。

## 8.5.1 系统架构优化

### 微服务架构设计

```javascript
// 微服务注册中心
class ServiceRegistry {
    constructor(config) {
        this.services = new Map();
        this.healthChecks = new Map();
        this.loadBalancers = new Map();
        
        this.config = config;
        this.initializeRegistry();
    }
    
    initializeRegistry() {
        // 注册核心服务
        this.registerService('data-collection', {
            instances: [
                { id: 'dc-001', host: '10.1.1.10', port: 8080, weight: 100 },
                { id: 'dc-002', host: '10.1.1.11', port: 8080, weight: 100 }
            ],
            healthCheck: {
                path: '/health',
                interval: 30000,
                timeout: 5000
            }
        });
        
        this.registerService('data-processing', {
            instances: [
                { id: 'dp-001', host: '10.1.2.10', port: 8081, weight: 100 },
                { id: 'dp-002', host: '10.1.2.11', port: 8081, weight: 100 },
                { id: 'dp-003', host: '10.1.2.12', port: 8081, weight: 100 }
            ],
            healthCheck: {
                path: '/health',
                interval: 15000,
                timeout: 3000
            }
        });
        
        this.registerService('visualization', {
            instances: [
                { id: 'viz-001', host: '10.1.3.10', port: 8082, weight: 100 },
                { id: 'viz-002', host: '10.1.3.11', port: 8082, weight: 100 }
            ],
            healthCheck: {
                path: '/health',
                interval: 30000,
                timeout: 5000
            }
        });
    }
    
    registerService(serviceName, config) {
        this.services.set(serviceName, {
            name: serviceName,
            instances: config.instances,
            healthCheck: config.healthCheck,
            status: 'active',
            registeredAt: new Date()
        });
        
        // 初始化负载均衡器
        this.loadBalancers.set(serviceName, new LoadBalancer(config.instances));
        
        // 启动健康检查
        this.startHealthCheck(serviceName, config.healthCheck);
    }
    
    async startHealthCheck(serviceName, healthConfig) {
        const service = this.services.get(serviceName);
        
        const healthCheck = setInterval(async () => {
            for (const instance of service.instances) {
                try {
                    const response = await fetch(
                        `http://${instance.host}:${instance.port}${healthConfig.path}`,
                        { timeout: healthConfig.timeout }
                    );
                    
                    instance.healthy = response.ok;
                    instance.lastCheck = new Date();
                    
                    if (!response.ok) {
                        console.warn(`服务实例 ${instance.id} 健康检查失败`);
                    }
                } catch (error) {
                    instance.healthy = false;
                    instance.lastCheck = new Date();
                    instance.lastError = error.message;
                    
                    console.error(`服务实例 ${instance.id} 无法访问: ${error.message}`);
                }
            }
        }, healthConfig.interval);
        
        this.healthChecks.set(serviceName, healthCheck);
    }
    
    getServiceInstance(serviceName) {
        const loadBalancer = this.loadBalancers.get(serviceName);
        return loadBalancer ? loadBalancer.getNextInstance() : null;
    }
    
    getServiceStatus() {
        const status = {};
        
        for (const [serviceName, service] of this.services) {
            const healthyInstances = service.instances.filter(i => i.healthy).length;
            const totalInstances = service.instances.length;
            
            status[serviceName] = {
                total: totalInstances,
                healthy: healthyInstances,
                ratio: totalInstances > 0 ? (healthyInstances / totalInstances) : 0,
                instances: service.instances.map(i => ({
                    id: i.id,
                    host: i.host,
                    port: i.port,
                    healthy: i.healthy,
                    lastCheck: i.lastCheck
                }))
            };
        }
        
        return status;
    }
}

// 负载均衡器
class LoadBalancer {
    constructor(instances) {
        this.instances = instances;
        this.algorithm = 'round_robin';
        this.currentIndex = 0;
    }
    
    getNextInstance() {
        const healthyInstances = this.instances.filter(i => i.healthy);
        
        if (healthyInstances.length === 0) {
            throw new Error('没有可用的服务实例');
        }
        
        switch (this.algorithm) {
            case 'round_robin':
                return this.roundRobin(healthyInstances);
            case 'weighted_round_robin':
                return this.weightedRoundRobin(healthyInstances);
            case 'least_connections':
                return this.leastConnections(healthyInstances);
            default:
                return healthyInstances[0];
        }
    }
    
    roundRobin(instances) {
        const instance = instances[this.currentIndex % instances.length];
        this.currentIndex++;
        return instance;
    }
    
    weightedRoundRobin(instances) {
        // 根据权重选择实例
        const totalWeight = instances.reduce((sum, i) => sum + i.weight, 0);
        const random = Math.random() * totalWeight;
        
        let currentWeight = 0;
        for (const instance of instances) {
            currentWeight += instance.weight;
            if (random <= currentWeight) {
                return instance;
            }
        }
        
        return instances[0];
    }
}
```

### 服务网格实现

```yaml
# 服务网格配置 (istio)
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: water-monitoring-platform
  namespace: smart-water
spec:
  http:
  - match:
    - uri:
        prefix: /api/data-collection
    route:
    - destination:
        host: data-collection-service
        subset: v1
      weight: 90
    - destination:
        host: data-collection-service
        subset: v2
      weight: 10
    fault:
      delay:
        percentage:
          value: 0.1
        fixedDelay: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
      
  - match:
    - uri:
        prefix: /api/processing
    route:
    - destination:
        host: data-processing-service
    circuitBreaker:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      
  - match:
    - uri:
        prefix: /api/visualization
    route:
    - destination:
        host: visualization-service
    timeout: 30s
    mirror:
      host: visualization-service-canary
      
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: data-collection-destination
  namespace: smart-water
spec:
  host: data-collection-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 10
    loadBalancer:
      simple: LEAST_CONN
    outlierDetection:
      consecutiveErrors: 3
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

## 8.5.2 运维监控体系

### 系统监控框架

```python
import psutil
import time
from datetime import datetime
import json
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MetricPoint:
    timestamp: float
    value: float
    tags: Dict[str, str] = None

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, config):
        self.config = config
        self.metrics_buffer = []
        self.alert_rules = self.load_alert_rules()
        self.collectors = self.initialize_collectors()
        
    def initialize_collectors(self):
        """初始化监控数据收集器"""
        return {
            'system': SystemMetricsCollector(),
            'application': ApplicationMetricsCollector(),
            'business': BusinessMetricsCollector(),
            'network': NetworkMetricsCollector()
        }
    
    def collect_all_metrics(self):
        """收集所有监控指标"""
        all_metrics = {}
        
        for collector_name, collector in self.collectors.items():
            try:
                metrics = collector.collect()
                all_metrics[collector_name] = metrics
            except Exception as e:
                print(f"收集器 {collector_name} 失败: {e}")
                
        return all_metrics
    
    def process_metrics(self, metrics):
        """处理监控指标"""
        processed_metrics = []
        
        for category, category_metrics in metrics.items():
            for metric_name, metric_data in category_metrics.items():
                # 创建标准化的指标点
                point = MetricPoint(
                    timestamp=time.time(),
                    value=metric_data['value'],
                    tags={
                        'category': category,
                        'metric': metric_name,
                        'host': self.config.get('hostname', 'unknown'),
                        **metric_data.get('tags', {})
                    }
                )
                processed_metrics.append(point)
        
        return processed_metrics
    
    def check_alerts(self, metrics):
        """检查告警规则"""
        alerts = []
        
        for rule in self.alert_rules:
            try:
                if self.evaluate_alert_rule(rule, metrics):
                    alert = {
                        'rule_id': rule['id'],
                        'severity': rule['severity'],
                        'message': rule['message'],
                        'timestamp': datetime.now().isoformat(),
                        'metrics': self.extract_relevant_metrics(rule, metrics)
                    }
                    alerts.append(alert)
            except Exception as e:
                print(f"告警规则 {rule['id']} 评估失败: {e}")
        
        return alerts
    
    def evaluate_alert_rule(self, rule, metrics):
        """评估告警规则"""
        target_metrics = self.extract_relevant_metrics(rule, metrics)
        
        if not target_metrics:
            return False
        
        condition = rule['condition']
        threshold = rule['threshold']
        
        for metric in target_metrics:
            value = metric.value
            
            if condition == 'greater_than' and value > threshold:
                return True
            elif condition == 'less_than' and value < threshold:
                return True
            elif condition == 'equals' and value == threshold:
                return True
            elif condition == 'not_equals' and value != threshold:
                return True
        
        return False

class SystemMetricsCollector:
    """系统指标收集器"""
    
    def collect(self):
        """收集系统指标"""
        return {
            'cpu_usage': {
                'value': psutil.cpu_percent(interval=1),
                'unit': 'percent',
                'tags': {'type': 'system'}
            },
            'memory_usage': {
                'value': psutil.virtual_memory().percent,
                'unit': 'percent',
                'tags': {'type': 'system'}
            },
            'disk_usage': {
                'value': psutil.disk_usage('/').percent,
                'unit': 'percent',
                'tags': {'type': 'system', 'mount_point': '/'}
            },
            'load_average': {
                'value': psutil.getloadavg()[0],
                'unit': 'load',
                'tags': {'type': 'system', 'period': '1min'}
            },
            'network_io_bytes_sent': {
                'value': psutil.net_io_counters().bytes_sent,
                'unit': 'bytes',
                'tags': {'type': 'network', 'direction': 'sent'}
            },
            'network_io_bytes_recv': {
                'value': psutil.net_io_counters().bytes_recv,
                'unit': 'bytes',
                'tags': {'type': 'network', 'direction': 'received'}
            }
        }

class ApplicationMetricsCollector:
    """应用指标收集器"""
    
    def __init__(self):
        self.service_endpoints = {
            'data-collection': 'http://localhost:8080/metrics',
            'data-processing': 'http://localhost:8081/metrics',
            'visualization': 'http://localhost:8082/metrics'
        }
    
    def collect(self):
        """收集应用指标"""
        metrics = {}
        
        for service_name, endpoint in self.service_endpoints.items():
            try:
                service_metrics = self.collect_service_metrics(service_name, endpoint)
                metrics.update(service_metrics)
            except Exception as e:
                print(f"收集服务 {service_name} 指标失败: {e}")
                # 记录服务不可用
                metrics[f'{service_name}_available'] = {
                    'value': 0,
                    'unit': 'boolean',
                    'tags': {'service': service_name, 'status': 'unavailable'}
                }
        
        return metrics
    
    def collect_service_metrics(self, service_name, endpoint):
        """收集单个服务的指标"""
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        service_data = response.json()
        
        return {
            f'{service_name}_response_time': {
                'value': service_data.get('avg_response_time', 0),
                'unit': 'milliseconds',
                'tags': {'service': service_name}
            },
            f'{service_name}_request_rate': {
                'value': service_data.get('requests_per_second', 0),
                'unit': 'rps',
                'tags': {'service': service_name}
            },
            f'{service_name}_error_rate': {
                'value': service_data.get('error_rate', 0),
                'unit': 'percent',
                'tags': {'service': service_name}
            },
            f'{service_name}_active_connections': {
                'value': service_data.get('active_connections', 0),
                'unit': 'count',
                'tags': {'service': service_name}
            }
        }

class BusinessMetricsCollector:
    """业务指标收集器"""
    
    def __init__(self):
        self.database_connection = self.get_database_connection()
    
    def collect(self):
        """收集业务指标"""
        return {
            'active_monitoring_stations': {
                'value': self.count_active_stations(),
                'unit': 'count',
                'tags': {'type': 'business'}
            },
            'data_points_per_minute': {
                'value': self.count_recent_data_points(),
                'unit': 'count/min',
                'tags': {'type': 'business'}
            },
            'active_alerts': {
                'value': self.count_active_alerts(),
                'unit': 'count',
                'tags': {'type': 'business'}
            },
            'system_users_online': {
                'value': self.count_online_users(),
                'unit': 'count',
                'tags': {'type': 'business'}
            }
        }
    
    def count_active_stations(self):
        """统计活跃监测站数量"""
        query = """
        SELECT COUNT(DISTINCT station_id) 
        FROM monitoring_data 
        WHERE timestamp > NOW() - INTERVAL 1 HOUR
        """
        result = self.database_connection.execute(query).fetchone()
        return result[0] if result else 0
    
    def count_recent_data_points(self):
        """统计最近一分钟的数据点数量"""
        query = """
        SELECT COUNT(*) 
        FROM monitoring_data 
        WHERE timestamp > NOW() - INTERVAL 1 MINUTE
        """
        result = self.database_connection.execute(query).fetchone()
        return result[0] if result else 0
```

### 日志管理系统

```javascript
class LogManagementSystem {
    constructor(config) {
        this.config = config;
        this.logLevel = config.logLevel || 'INFO';
        this.logDestinations = config.destinations || [];
        this.logBuffer = [];
        this.maxBufferSize = config.maxBufferSize || 1000;
        
        this.initializeDestinations();
        this.setupPeriodicFlush();
    }
    
    initializeDestinations() {
        this.destinations = this.logDestinations.map(dest => {
            switch (dest.type) {
                case 'file':
                    return new FileLogDestination(dest.config);
                case 'elasticsearch':
                    return new ElasticsearchLogDestination(dest.config);
                case 'kafka':
                    return new KafkaLogDestination(dest.config);
                default:
                    return new ConsoleLogDestination();
            }
        });
    }
    
    log(level, message, metadata = {}) {
        if (!this.shouldLog(level)) {
            return;
        }
        
        const logEntry = {
            timestamp: new Date().toISOString(),
            level: level,
            message: message,
            metadata: {
                ...metadata,
                hostname: this.config.hostname,
                service: this.config.serviceName,
                version: this.config.version,
                pid: process.pid
            },
            traceId: this.getTraceId()
        };
        
        this.logBuffer.push(logEntry);
        
        // 如果是错误级别，立即刷新
        if (level === 'ERROR' || level === 'FATAL') {
            this.flush();
        }
        
        // 缓冲区满时刷新
        if (this.logBuffer.length >= this.maxBufferSize) {
            this.flush();
        }
    }
    
    shouldLog(level) {
        const levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'];
        const currentLevelIndex = levels.indexOf(this.logLevel);
        const messageLevelIndex = levels.indexOf(level);
        
        return messageLevelIndex >= currentLevelIndex;
    }
    
    flush() {
        if (this.logBuffer.length === 0) {
            return;
        }
        
        const logs = [...this.logBuffer];
        this.logBuffer = [];
        
        // 并行发送到所有目标
        this.destinations.forEach(destination => {
            destination.send(logs).catch(error => {
                console.error(`日志发送失败: ${error.message}`);
            });
        });
    }
    
    setupPeriodicFlush() {
        setInterval(() => {
            this.flush();
        }, 5000); // 每5秒刷新一次
    }
    
    // 便捷方法
    debug(message, metadata) { this.log('DEBUG', message, metadata); }
    info(message, metadata) { this.log('INFO', message, metadata); }
    warn(message, metadata) { this.log('WARN', message, metadata); }
    error(message, metadata) { this.log('ERROR', message, metadata); }
    fatal(message, metadata) { this.log('FATAL', message, metadata); }
}

class ElasticsearchLogDestination {
    constructor(config) {
        this.config = config;
        this.client = new ElasticsearchClient(config);
        this.indexPattern = config.indexPattern || 'logs-{yyyy.MM.dd}';
    }
    
    async send(logs) {
        const bulkBody = [];
        
        logs.forEach(log => {
            const index = this.generateIndexName(log.timestamp);
            
            bulkBody.push({
                index: { _index: index }
            });
            bulkBody.push(log);
        });
        
        try {
            await this.client.bulk({ body: bulkBody });
        } catch (error) {
            throw new Error(`Elasticsearch写入失败: ${error.message}`);
        }
    }
    
    generateIndexName(timestamp) {
        const date = new Date(timestamp);
        return this.indexPattern
            .replace('{yyyy}', date.getFullYear())
            .replace('{MM}', String(date.getMonth() + 1).padStart(2, '0'))
            .replace('{dd}', String(date.getDate()).padStart(2, '0'));
    }
}
```

## 8.5.3 自动化运维

### 容器化部署

```yaml
# Docker Compose配置
version: '3.8'

services:
  # 数据采集服务
  data-collection:
    image: smart-water/data-collection:latest
    container_name: data-collection
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=production
      - DATABASE_URL=jdbc:postgresql://postgres:5432/smart_water
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./config/data-collection.yml:/app/config/application.yml
      - ./logs:/app/logs
    networks:
      - smart-water-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
  
  # 数据处理服务
  data-processing:
    image: smart-water/data-processing:latest
    container_name: data-processing
    ports:
      - "8081:8081"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:5432/smart_water
      - KAFKA_BROKERS=kafka:9092
    depends_on:
      - postgres
      - kafka
    volumes:
      - ./config/data-processing.json:/app/config/production.json
      - ./logs:/app/logs
    networks:
      - smart-water-network
    restart: unless-stopped
    scale: 3
    
  # 可视化服务
  visualization:
    image: smart-water/visualization:latest
    container_name: visualization
    ports:
      - "8082:8082"
    environment:
      - VUE_APP_API_BASE_URL=http://api-gateway:8000
      - VUE_APP_CESIUM_TOKEN=${CESIUM_ACCESS_TOKEN}
    depends_on:
      - api-gateway
    volumes:
      - ./dist:/app/dist
      - ./nginx.conf:/etc/nginx/nginx.conf
    networks:
      - smart-water-network
    restart: unless-stopped
    
  # API网关
  api-gateway:
    image: nginx:alpine
    container_name: api-gateway
    ports:
      - "8000:80"
      - "8443:443"
    volumes:
      - ./nginx/gateway.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - data-collection
      - data-processing
      - visualization
    networks:
      - smart-water-network
    restart: unless-stopped
    
  # 数据库
  postgres:
    image: postgis/postgis:13-3.1
    container_name: postgres
    environment:
      - POSTGRES_DB=smart_water
      - POSTGRES_USER=smart_water_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - smart-water-network
    restart: unless-stopped
    
  # Redis缓存
  redis:
    image: redis:6-alpine
    container_name: redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - smart-water-network
    restart: unless-stopped
    
  # 监控系统
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - smart-water-network
    restart: unless-stopped
    
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - smart-water-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  smart-water-network:
    driver: bridge
```

### CI/CD流水线

```yaml
# GitLab CI/CD配置
stages:
  - validate
  - test
  - build
  - security-scan
  - deploy-staging
  - integration-test
  - deploy-production
  - post-deploy

variables:
  DOCKER_REGISTRY: registry.smart-water.com
  KUBECONFIG: /tmp/.kube/config

# 代码质量检查
code-quality:
  stage: validate
  image: sonarqube/sonar-scanner-cli:latest
  script:
    - sonar-scanner -Dsonar.projectKey=smart-water-platform
  only:
    - merge_requests
    - develop
    - master

# 单元测试
unit-tests:
  stage: test
  image: node:16
  services:
    - postgres:13
    - redis:6
  script:
    - npm ci
    - npm run test:unit
    - npm run test:coverage
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    expire_in: 1 week

# 构建Docker镜像
build-images:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY
  script:
    - docker build -t $DOCKER_REGISTRY/data-collection:$CI_COMMIT_SHA ./services/data-collection
    - docker build -t $DOCKER_REGISTRY/data-processing:$CI_COMMIT_SHA ./services/data-processing
    - docker build -t $DOCKER_REGISTRY/visualization:$CI_COMMIT_SHA ./services/visualization
    - docker push $DOCKER_REGISTRY/data-collection:$CI_COMMIT_SHA
    - docker push $DOCKER_REGISTRY/data-processing:$CI_COMMIT_SHA
    - docker push $DOCKER_REGISTRY/visualization:$CI_COMMIT_SHA
  only:
    - develop
    - master

# 安全扫描
security-scan:
  stage: security-scan
  image: owasp/zap2docker-stable
  script:
    - zap-baseline.py -t http://staging.smart-water.com
  artifacts:
    reports:
      junit: zap-report.xml
  only:
    - develop
    - master

# 部署到预发布环境
deploy-staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging.smart-water.com
  script:
    - kubectl config use-context staging
    - helm upgrade --install smart-water-staging ./helm-chart 
        --set image.tag=$CI_COMMIT_SHA
        --set environment=staging
        --namespace smart-water-staging
    - kubectl rollout status deployment/smart-water-staging -n smart-water-staging
  only:
    - develop

# 生产环境部署
deploy-production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://smart-water.com
  script:
    - kubectl config use-context production
    - helm upgrade --install smart-water-production ./helm-chart 
        --set image.tag=$CI_COMMIT_SHA
        --set environment=production
        --namespace smart-water-production
    - kubectl rollout status deployment/smart-water-production -n smart-water-production
  when: manual
  only:
    - master

# 部署后检查
post-deploy-check:
  stage: post-deploy
  image: alpine/curl
  script:
    - curl -f https://smart-water.com/health || exit 1
    - curl -f https://smart-water.com/api/health || exit 1
  only:
    - master
```

## 8.5.4 故障处理与恢复

### 故障自动检测与恢复

```python
class AutoRecoverySystem:
    """自动故障恢复系统"""
    
    def __init__(self, config):
        self.config = config
        self.recovery_strategies = self.load_recovery_strategies()
        self.circuit_breakers = {}
        self.retry_policies = {}
        
    def load_recovery_strategies(self):
        """加载恢复策略"""
        return {
            'service_unavailable': {
                'detection': {
                    'method': 'health_check_failure',
                    'threshold': 3,
                    'window': 60  # 秒
                },
                'recovery': [
                    'restart_service',
                    'scale_out_replicas',
                    'fallback_to_backup'
                ]
            },
            'high_cpu_usage': {
                'detection': {
                    'method': 'metric_threshold',
                    'metric': 'cpu_usage',
                    'threshold': 80,
                    'duration': 300
                },
                'recovery': [
                    'scale_out_replicas',
                    'optimize_resource_allocation',
                    'enable_performance_mode'
                ]
            },
            'memory_leak': {
                'detection': {
                    'method': 'memory_growth_trend',
                    'growth_rate': 10,  # MB/minute
                    'duration': 600
                },
                'recovery': [
                    'restart_service_gracefully',
                    'collect_heap_dump',
                    'notify_development_team'
                ]
            },
            'database_connection_pool_exhausted': {
                'detection': {
                    'method': 'connection_pool_metric',
                    'threshold': 95,  # percent
                    'duration': 60
                },
                'recovery': [
                    'increase_connection_pool_size',
                    'kill_long_running_queries',
                    'restart_database_connections'
                ]
            }
        }
    
    async def monitor_and_recover(self):
        """监控并执行自动恢复"""
        while True:
            try:
                # 收集系统指标
                metrics = await self.collect_system_metrics()
                
                # 检测故障
                detected_issues = self.detect_issues(metrics)
                
                # 执行恢复策略
                for issue in detected_issues:
                    await self.execute_recovery(issue)
                
                await asyncio.sleep(30)  # 30秒检查一次
                
            except Exception as e:
                print(f"自动恢复系统错误: {e}")
                await asyncio.sleep(60)
    
    def detect_issues(self, metrics):
        """检测系统问题"""
        issues = []
        
        for strategy_name, strategy in self.recovery_strategies.items():
            if self.evaluate_detection_rule(strategy['detection'], metrics):
                issues.append({
                    'type': strategy_name,
                    'strategy': strategy,
                    'detected_at': datetime.now(),
                    'metrics': metrics
                })
        
        return issues
    
    async def execute_recovery(self, issue):
        """执行恢复策略"""
        strategy = issue['strategy']
        
        print(f"检测到问题: {issue['type']}, 开始执行恢复策略")
        
        for recovery_action in strategy['recovery']:
            try:
                success = await self.execute_recovery_action(recovery_action, issue)
                
                if success:
                    print(f"恢复行动成功: {recovery_action}")
                    # 验证问题是否已解决
                    if await self.verify_recovery(issue):
                        print(f"问题已解决: {issue['type']}")
                        break
                else:
                    print(f"恢复行动失败: {recovery_action}")
                    
            except Exception as e:
                print(f"执行恢复行动时出错 {recovery_action}: {e}")
    
    async def execute_recovery_action(self, action, issue):
        """执行具体的恢复行动"""
        
        action_handlers = {
            'restart_service': self.restart_service,
            'scale_out_replicas': self.scale_out_replicas,
            'fallback_to_backup': self.fallback_to_backup,
            'optimize_resource_allocation': self.optimize_resource_allocation,
            'increase_connection_pool_size': self.increase_connection_pool_size,
            'kill_long_running_queries': self.kill_long_running_queries
        }
        
        handler = action_handlers.get(action)
        if handler:
            return await handler(issue)
        else:
            print(f"未知的恢复行动: {action}")
            return False
    
    async def restart_service(self, issue):
        """重启服务"""
        try:
            # 获取受影响的服务
            service_name = self.identify_affected_service(issue)
            
            # 优雅停止服务
            await self.graceful_shutdown(service_name)
            
            # 等待服务完全停止
            await asyncio.sleep(10)
            
            # 启动服务
            await self.start_service(service_name)
            
            # 等待服务就绪
            return await self.wait_for_service_ready(service_name, timeout=120)
            
        except Exception as e:
            print(f"重启服务失败: {e}")
            return False
    
    async def scale_out_replicas(self, issue):
        """扩容副本"""
        try:
            service_name = self.identify_affected_service(issue)
            current_replicas = await self.get_current_replica_count(service_name)
            
            # 增加副本数量
            new_replica_count = min(current_replicas + 2, self.config.max_replicas)
            
            await self.set_replica_count(service_name, new_replica_count)
            
            # 等待新副本就绪
            return await self.wait_for_replicas_ready(service_name, new_replica_count)
            
        except Exception as e:
            print(f"扩容失败: {e}")
            return False
```

## 小结

系统集成与运维管理是智慧水利平台稳定运行的重要保障。通过微服务架构设计、全面的监控体系、自动化运维和智能故障恢复机制，可以构建高可用、高性能、高安全性的水利信息化平台。

**关键要点总结**：

1. **架构优化**：采用微服务架构和服务网格，提高系统的可扩展性和容错能力

2. **监控体系**：建立全方位的监控体系，实时掌握系统运行状态

3. **自动化运维**：通过容器化部署和CI/CD流水线，提高运维效率和可靠性

4. **故障恢复**：实现智能故障检测和自动恢复，最大限度减少系统中断时间

至此，第8章"智慧水利平台典型应用"的内容已经完成，涵盖了平台的完整应用实践和运维管理体系。



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
