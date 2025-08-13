# 5.3.5 水利API案例

## 引言

本节通过具体的水利API案例，展示RESTful API设计原则在智慧水利平台中的实际应用。我们将分析水文监测、水库调度和工程监测预警等典型水利业务场景的API设计，帮助读者理解如何将理论知识转化为实际的API实现。

## 5.3.5.1 水文监测API设计案例

### 水文站点信息管理API

水文站点是水利监测的基础设施，其信息管理API需要支持站点的增删改查操作。

#### API设计规范

```http
# 获取所有水文站点
GET /api/v1/hydro-stations
# 查询参数: page, size, region, type

# 获取指定站点信息
GET /api/v1/hydro-stations/{stationId}

# 创建新站点
POST /api/v1/hydro-stations
# 请求体: 站点基本信息JSON

# 更新站点信息
PUT /api/v1/hydro-stations/{stationId}
# 请求体: 更新的站点信息JSON

# 删除站点
DELETE /api/v1/hydro-stations/{stationId}
```

#### 数据模型设计

```json
{
  "stationId": "HS001",
  "name": "长江干流大通站",
  "location": {
    "latitude": 31.7667,
    "longitude": 117.6333,
    "altitude": 6.8
  },
  "type": "RIVER",
  "status": "ACTIVE",
  "operator": "安徽省水文局",
  "establishDate": "1950-01-01",
  "equipment": [
    {
      "type": "WATER_LEVEL",
      "model": "WL-2000",
      "accuracy": "±1cm"
    }
  ]
}
```

### 水文数据查询API

水文数据查询是智慧水利平台的核心功能，需要支持多维度、多时间段的数据检索。

#### API设计

```http
# 获取站点实时数据
GET /api/v1/hydro-data/realtime/{stationId}

# 获取历史数据
GET /api/v1/hydro-data/history
# 查询参数: 
# - stationIds: 站点ID列表(逗号分隔)
# - dataTypes: 数据类型(WATER_LEVEL,FLOW,RAINFALL)
# - startTime: 开始时间(ISO 8601格式)
# - endTime: 结束时间
# - interval: 数据间隔(1h,1d,1m)

# 获取统计数据
GET /api/v1/hydro-data/statistics
# 查询参数: stationId, dataType, period(DAILY,MONTHLY,YEARLY)
```

#### 响应数据格式

```json
{
  "success": true,
  "data": {
    "stationId": "HS001",
    "dataType": "WATER_LEVEL",
    "unit": "m",
    "records": [
      {
        "timestamp": "2024-01-01T08:00:00Z",
        "value": 12.35,
        "quality": "GOOD"
      }
    ]
  },
  "pagination": {
    "page": 1,
    "size": 100,
    "total": 1500
  }
}
```

## 5.3.5.2 水库调度API设计案例

### 水库基本信息API

水库调度系统需要管理水库的基本信息和运行参数。

#### API设计

```http
# 获取水库列表
GET /api/v1/reservoirs
# 查询参数: region, capacity_min, capacity_max

# 获取水库详细信息
GET /api/v1/reservoirs/{reservoirId}

# 获取水库运行状态
GET /api/v1/reservoirs/{reservoirId}/status

# 获取调度规则
GET /api/v1/reservoirs/{reservoirId}/dispatch-rules
```

#### 水库信息数据模型

```json
{
  "reservoirId": "RV001",
  "name": "三峡水库",
  "location": {
    "latitude": 30.8182,
    "longitude": 111.0031
  },
  "capacity": {
    "total": 39300000000,
    "useful": 22150000000,
    "dead": 17150000000
  },
  "waterLevels": {
    "normal": 175.0,
    "flood": 145.0,
    "dead": 155.0
  },
  "turbines": [
    {
      "unitId": "T01",
      "capacity": 700000,
      "status": "RUNNING"
    }
  ]
}
```

### 调度计划API

调度计划是水库运行的核心，需要支持计划的制定、审批和执行。

#### API设计

```http
# 创建调度计划
POST /api/v1/dispatch-plans
# 请求体: 调度计划JSON

# 获取调度计划
GET /api/v1/dispatch-plans/{planId}

# 审批调度计划
POST /api/v1/dispatch-plans/{planId}/approve
# 请求体: 审批意见

# 执行调度指令
POST /api/v1/dispatch-plans/{planId}/execute
```

#### 调度计划数据模型

```json
{
  "planId": "DP20240101001",
  "reservoirId": "RV001",
  "planType": "FLOOD_CONTROL",
  "planPeriod": {
    "startTime": "2024-01-01T00:00:00Z",
    "endTime": "2024-01-31T23:59:59Z"
  },
  "schedules": [
    {
      "time": "2024-01-01T08:00:00Z",
      "targetLevel": 174.5,
      "discharge": 15000,
      "generation": 500000
    }
  ],
  "status": "PENDING_APPROVAL",
  "creator": "张工程师",
  "createTime": "2024-01-01T06:00:00Z"
}
```

## 5.3.5.3 工程监测预警API设计案例

### 监测数据采集API

工程安全监测需要实时采集各类传感器数据，并进行异常检测。

#### API设计

```http
# 设备数据上报
POST /api/v1/monitoring/data
# 请求体: 监测数据JSON数组

# 获取设备列表
GET /api/v1/monitoring/devices
# 查询参数: projectId, deviceType, status

# 获取实时监测数据
GET /api/v1/monitoring/realtime/{projectId}

# 获取历史监测数据
GET /api/v1/monitoring/history
# 查询参数: projectId, deviceIds, startTime, endTime
```

#### 监测数据模型

```json
{
  "deviceId": "SENSOR001",
  "projectId": "DAM001",
  "deviceType": "DISPLACEMENT",
  "location": {
    "section": "0+100",
    "elevation": 185.5,
    "coordinates": {
      "x": 1000.5,
      "y": 2000.3,
      "z": 185.5
    }
  },
  "data": [
    {
      "timestamp": "2024-01-01T08:00:00Z",
      "value": 2.35,
      "unit": "mm",
      "quality": "NORMAL"
    }
  ]
}
```

### 预警管理API

预警系统需要支持预警规则配置、预警生成和预警处理。

#### API设计

```http
# 配置预警规则
POST /api/v1/alerts/rules
# 请求体: 预警规则JSON

# 获取当前预警
GET /api/v1/alerts/current
# 查询参数: level, status, projectId

# 预警确认处理
POST /api/v1/alerts/{alertId}/acknowledge
# 请求体: 处理意见

# 预警关闭
POST /api/v1/alerts/{alertId}/close
```

#### 预警数据模型

```json
{
  "alertId": "ALT20240101001",
  "projectId": "DAM001",
  "deviceId": "SENSOR001",
  "alertType": "THRESHOLD_EXCEEDED",
  "level": "WARNING",
  "title": "坝体位移异常",
  "description": "0+100断面位移超过预警阈值",
  "triggerValue": 5.2,
  "threshold": 5.0,
  "triggerTime": "2024-01-01T08:30:00Z",
  "status": "ACTIVE",
  "assignee": "值班工程师",
  "actions": [
    {
      "action": "INCREASE_MONITORING",
      "description": "增加监测频率"
    }
  ]
}
```

## 5.3.5.4 API安全与认证案例

### JWT认证实现

智慧水利平台API需要实现安全的用户认证和授权机制。

#### 认证API设计

```http
# 用户登录
POST /api/v1/auth/login
# 请求体: 用户名密码

# 刷新Token
POST /api/v1/auth/refresh
# 请求头: Refresh-Token

# 用户注销
POST /api/v1/auth/logout
```

#### JWT Token结构

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "userId": "user123",
    "username": "张工程师",
    "roles": ["ENGINEER", "OPERATOR"],
    "permissions": [
      "READ_HYDRO_DATA",
      "WRITE_DISPATCH_PLAN",
      "MANAGE_ALERTS"
    ],
    "exp": 1640995200,
    "iat": 1640908800
  }
}
```

### API权限控制

不同的API端点需要不同的权限级别。

#### 权限矩阵示例

| API端点 | 所需权限 | 角色要求 |
|---------|----------|----------|
| GET /api/v1/hydro-data/* | READ_HYDRO_DATA | VIEWER以上 |
| POST /api/v1/dispatch-plans | WRITE_DISPATCH_PLAN | ENGINEER以上 |
| POST /api/v1/alerts/*/acknowledge | MANAGE_ALERTS | OPERATOR以上 |
| DELETE /api/v1/hydro-stations/* | ADMIN_STATIONS | ADMIN |

## 5.3.5.5 API文档与测试

### Swagger/OpenAPI规范

使用OpenAPI 3.0规范来描述水利API。

#### API文档示例

```yaml
openapi: 3.0.0
info:
  title: 智慧水利平台API
  version: 1.0.0
  description: 智慧水利平台RESTful API接口文档

paths:
  /api/v1/hydro-stations:
    get:
      summary: 获取水文站点列表
      tags:
        - 水文监测
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: size
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: 成功返回站点列表
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StationListResponse'
```

### API测试策略

#### 单元测试

```javascript
// Jest测试示例
describe('水文站点API测试', () => {
  test('获取站点列表应返回正确格式', async () => {
    const response = await request(app)
      .get('/api/v1/hydro-stations')
      .expect(200);
    
    expect(response.body).toHaveProperty('success', true);
    expect(response.body).toHaveProperty('data');
    expect(Array.isArray(response.body.data)).toBe(true);
  });
});
```

#### 集成测试

```javascript
describe('水库调度API集成测试', () => {
  test('调度计划完整流程测试', async () => {
    // 1. 创建调度计划
    const createResponse = await request(app)
      .post('/api/v1/dispatch-plans')
      .send(mockPlan)
      .expect(201);
    
    const planId = createResponse.body.data.planId;
    
    // 2. 审批调度计划
    await request(app)
      .post(`/api/v1/dispatch-plans/${planId}/approve`)
      .send({ approved: true })
      .expect(200);
    
    // 3. 执行调度计划
    await request(app)
      .post(`/api/v1/dispatch-plans/${planId}/execute`)
      .expect(200);
  });
});
```

## 5.3.5.6 性能优化与监控

### API性能优化

#### 缓存策略

```javascript
// Redis缓存示例
const cacheKey = `hydro-data:${stationId}:${date}`;
let data = await redis.get(cacheKey);

if (!data) {
  data = await hydroDataService.getHistoryData(stationId, date);
  await redis.setex(cacheKey, 3600, JSON.stringify(data));
}
```

#### 分页与限流

```javascript
// 分页参数验证
const page = Math.max(1, parseInt(req.query.page) || 1);
const size = Math.min(100, Math.max(1, parseInt(req.query.size) || 20));

// 限流中间件
const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 100, // 最多100请求
  message: '请求过于频繁，请稍后再试'
});
```

### API监控

#### 性能指标收集

```javascript
// Prometheus指标
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status']
});

// 中间件记录指标
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path, res.statusCode)
      .observe(duration);
  });
  next();
});
```

## 小结

本节通过水文监测、水库调度和工程监测预警等典型案例，全面展示了RESTful API在智慧水利平台中的设计和实现。关键要点包括：

1. **API设计规范**：遵循RESTful原则，使用合适的HTTP方法和状态码
2. **数据模型设计**：建立清晰的数据结构，支持业务需求
3. **安全认证**：实现JWT认证和基于角色的权限控制
4. **文档化**：使用OpenAPI规范生成完整的API文档
5. **测试策略**：建立完善的单元测试和集成测试
6. **性能优化**：通过缓存、分页、限流等手段提升API性能
7. **监控告警**：收集关键指标，及时发现和解决问题

这些实践案例为智慧水利平台API的设计和开发提供了具体的指导，有助于构建高质量、高可用的水利信息化系统。
