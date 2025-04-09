# 5.6.5 智慧水利平台部署案例

## 案例一：省级水文监测平台部署

**系统架构**：
- 前端：Angular应用
- 后端：Spring Boot微服务集群
- 数据库：PostgreSQL(主数据)、TimescaleDB(时序数据)
- 缓存：Redis集群
- 消息队列：Kafka
- 监控：Prometheus + Grafana

**部署架构**：
- Kubernetes集群(3主节点，5工作节点)
- Ingress控制器管理外部流量
- 服务网格(Istio)管理服务通信
- 持久化存储使用分布式存储系统
- 多可用区部署确保高可用性

**部署流程**：
1. 环境准备
   - 创建Kubernetes命名空间
   - 配置网络策略和角色权限
   - 部署持久化存储

2. 数据层部署
   - 部署PostgreSQL集群(主从结构)
   - 部署TimescaleDB集群
   - 部署Redis集群

3. 中间件部署
   - 部署Kafka集群
   - 配置消息主题和分区

4. 应用层部署
   - 部署后端微服务
   - 部署API网关
   - 部署前端应用

5. 监控与日志
   - 部署Prometheus和Grafana
   - 配置EFK(Elasticsearch, Fluentd, Kibana)日志系统
   - 设置告警规则

**关键配置**：

```yaml
# 水文服务Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hydrology-service
  namespace: water-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hydrology-service
  template:
    metadata:
      labels:
        app: hydrology-service
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - hydrology-service
              topologyKey: kubernetes.io/hostname
      containers:
      - name: hydrology-service
        image: waterplatform/hydrology-service:1.2.0
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        - name: POSTGRES_HOST
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: postgres-host
        - name: POSTGRES_PORT
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: postgres-port
        # ... 更多环境变量
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

**监控配置**：

```yaml
# Prometheus监控配置
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hydrology-service-monitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: hydrology-service
  endpoints:
  - port: http
    path: /actuator/prometheus
    interval: 15s
  namespaceSelector:
    matchNames:
    - water-platform
```

**部署自动化**：

```yaml
# GitLab CI/CD配置
stages:
  - build
  - test
  - deploy-dev
  - deploy-staging
  - deploy-prod

variables:
  IMAGE_NAME: waterplatform/hydrology-service
  KUBE_CONTEXT: water-platform-cluster

build:
  stage: build
  script:
    - ./mvnw clean package
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA

test:
  stage: test
  script:
    - ./mvnw test
    - ./mvnw sonar:sonar

deploy-dev:
  stage: deploy-dev
  script:
    - kubectl config use-context $KUBE_CONTEXT
    - helm upgrade --install hydrology-service ./helm/hydrology-service 
      --namespace water-platform-dev 
      --set image.tag=$CI_COMMIT_SHA 
      --set environment=dev
  environment:
    name: development
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

deploy-staging:
  stage: deploy-staging
  script:
    - kubectl config use-context $KUBE_CONTEXT
    - helm upgrade --install hydrology-service ./helm/hydrology-service 
      --namespace water-platform-staging 
      --set image.tag=$CI_COMMIT_SHA 
      --set environment=staging
  environment:
    name: staging
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
  when: manual

deploy-prod:
  stage: deploy-prod
  script:
    - kubectl config use-context $KUBE_CONTEXT
    - helm upgrade --install hydrology-service ./helm/hydrology-service 
      --namespace water-platform-prod 
      --set image.tag=$CI_COMMIT_SHA 
      --set environment=prod
  environment:
    name: production
  rules:
    - if: $CI_COMMIT_TAG
  when: manual
```

## 案例二：智慧水利平台分布式部署

**系统特点**：
- 多地市分布式部署
- 数据就近处理
- 中心节点汇总
- 容灾备份
- 弹性扩展

**部署架构**：
- 中心节点：省级数据中心部署
- 边缘节点：各地市部署边缘计算节点
- 容器化部署所有服务
- 部署服务网格构建跨区域服务通信

**核心技术**：
- Kubernetes多集群管理
- 混合云部署策略
- 边缘计算技术
- 数据同步与复制机制

**部署重点**：
1. 区域负载均衡
2. 跨区域服务发现
3. 数据分片与同步
4. 灾备机制
5. 统一监控与运维 