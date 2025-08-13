# 5.6.4 服务编排与管理

## Kubernetes基础

Kubernetes(K8s)是一个开源的容器编排平台，用于自动化容器部署、扩展和管理。

**核心概念**：
- **Pod**：最小部署单元，包含一个或多个容器
- **Deployment**：管理Pod副本的控制器
- **Service**：定义Pod访问方式
- **ConfigMap/Secret**：配置管理
- **Namespace**：资源隔离单元
- **Ingress**：HTTP流量路由

## Kubernetes资源定义示例

**Deployment**：

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: water-monitoring-service
  namespace: water-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: water-monitoring-service
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: water-monitoring-service
    spec:
      containers:
      - name: water-monitoring-service
        image: waterplatform/monitoring-service:1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
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
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: water-db-config
              key: url
        - name: DATABASE_USERNAME
          valueFrom:
            secretKeyRef:
              name: water-db-credentials
              key: username
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: water-db-credentials
              key: password
        volumeMounts:
        - name: log-volume
          mountPath: /app/logs
      volumes:
      - name: log-volume
        persistentVolumeClaim:
          claimName: water-logs-pvc
```

**Service**：

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: water-monitoring-service
  namespace: water-platform
spec:
  selector:
    app: water-monitoring-service
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

**ConfigMap**：

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: water-app-config
  namespace: water-platform
data:
  application.properties: |
    server.port=8080
    management.endpoints.web.exposure.include=health,info,metrics
    water.monitoring.data-refresh-interval=300
    water.monitoring.warning-threshold=0.8
    logging.level.com.waterplatform=INFO
```

**Secret**：

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: water-db-credentials
  namespace: water-platform
type: Opaque
data:
  username: d2F0ZXJfYXBw  # Base64编码的 "water_app"
  password: c2VjcmV0      # Base64编码的 "secret"
```

**Ingress**：

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: water-platform-ingress
  namespace: water-platform
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: api.waterplatform.com
    http:
      paths:
      - path: /monitoring
        pathType: Prefix
        backend:
          service:
            name: water-monitoring-service
            port:
              number: 80
  tls:
  - hosts:
    - api.waterplatform.com
    secretName: waterplatform-tls
```

## Helm Charts

Helm是Kubernetes的包管理工具，通过Charts实现复杂应用的定义、安装和升级。

**Chart结构**：
```
water-monitoring-chart/
├── Chart.yaml           # Chart元数据
├── values.yaml          # 默认配置值
├── templates/           # 资源模板
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── ingress.yaml
├── charts/              # 依赖的子Chart
└── .helmignore          # 忽略文件
```

**values.yaml示例**：
```yaml
# 应用配置
application:
  name: water-monitoring-service
  replicas: 3
  version: 1.0.0
  
# 资源配置
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
    
# 网络配置
service:
  type: ClusterIP
  port: 80
  targetPort: 8080
  
ingress:
  enabled: true
  host: api.waterplatform.com
  path: /monitoring
  tls: true
  
# 数据库配置
database:
  url: jdbc:mysql://mysql:3306/waterdb
  username: water_app
  # password在安装时通过--set指定
  
# 监控配置
monitoring:
  dataRefreshInterval: 300
  warningThreshold: 0.8
``` 