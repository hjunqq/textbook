# 5.3.2 RESTful API设计原则

## 资源设计

### 资源命名规范

- **使用名词而非动词**
  - 资源表示实体，应使用名词
  - 操作通过HTTP方法表达，而非URL

```
# 好的示例
/stations           # 水文站集合
/stations/st12345   # 特定水文站
/stations/st12345/water-levels  # 特定水文站的水位记录集合

# 不好的示例
/getStations        # 使用了动词
/station            # 单数形式不明确
/st                 # 缩写不直观
```

- **使用复数形式表示集合**
  - 集合资源用复数形式：`/reservoirs`
  - 单个资源保持一致性：`/reservoirs/{id}`

- **使用小写字母和连字符（短横线）**
  - URL对大小写敏感，统一使用小写
  - 多个单词间用连字符连接：`/water-levels`而非`/waterLevels`或`/water_levels`

- **避免使用文件扩展名**
  - 使用Accept头指定格式，而非URL扩展名
  - 不用：`/stations/st12345.json`
  - 应用：`/stations/st12345` + `Accept: application/json`

### 资源关系表示

- **子资源表示**
  - 通过URL路径表示资源间的从属关系
  - 例如：`/reservoirs/res001/monitoring-points`

- **引用资源**
  - 使用查询参数表示筛选或引用
  - 例如：`/water-levels?station_id=st12345`

- **资源间关系**
  - 可以创建专门的关系资源
  - 例如：`/stations/st12345/related-reservoirs`

### 复杂操作的处理

对于不符合CRUD的操作，可以采用以下策略：

- **将操作视为资源的属性**
  ```
  # 启动泄洪操作
  POST /reservoirs/res001/discharge-operations
  
  # 查询泄洪操作状态
  GET /reservoirs/res001/discharge-operations/op123
  ```

- **使用控制器资源模式**
  ```
  # 创建洪水模拟任务
  POST /flood-simulations
  
  # 查询模拟结果
  GET /flood-simulations/sim456
  ```

- **适当使用查询参数**
  ```
  # 搜索水位超过警戒值的站点
  GET /stations?status=warning
  
  # 获取特定时间范围的水位数据
  GET /water-levels?start_date=2023-06-01&end_date=2023-06-30
  ```

## HTTP方法的正确使用

### 基本HTTP方法

| 方法 | 语义 | 示例 |
|------|------|------|
| GET | 获取资源 | GET /stations/st12345 |
| POST | 创建资源 | POST /stations |
| PUT | 全量更新资源 | PUT /stations/st12345 |
| PATCH | 部分更新资源 | PATCH /stations/st12345 |
| DELETE | 删除资源 | DELETE /stations/st12345 |

### 安全性与幂等性

- **安全方法**：不会修改资源状态（GET、HEAD、OPTIONS）
- **幂等方法**：多次调用产生相同结果（GET、PUT、DELETE、HEAD、OPTIONS）

这些特性对于设计可靠的API至关重要，尤其是在网络不稳定的环境中：
- 安全方法可以被缓存，提高性能
- 幂等方法允许客户端重试请求而不造成意外后果

### 方法使用指南

- **GET**
  - 用于获取资源，不应有副作用
  - 可以被缓存
  - 例如：`GET /stations/st12345`获取特定水文站信息

- **POST**
  - 主要用于创建资源
  - 也可用于难以用其他方法表达的复杂操作
  - 不是幂等的，多次相同请求可能创建多个资源
  - 例如：`POST /alerts`创建新的预警信息

- **PUT**
  - 用于全量更新资源，客户端提供完整资源表示
  - 是幂等的，多次相同请求不会产生不同结果
  - 例如：`PUT /stations/st12345`更新整个站点信息

- **PATCH**
  - 用于部分更新资源，客户端只提供需要更改的部分
  - 通常不是幂等的（除非特别设计）
  - 例如：`PATCH /stations/st12345`只更新站点的某些属性

- **DELETE**
  - 用于删除资源
  - 是幂等的，多次删除同一资源效果相同
  - 例如：`DELETE /stations/st12345`删除特定站点

## 请求与响应设计

### 请求参数类型

1. **路径参数**
   - 用于标识特定资源
   - 例如：`/stations/{id}`中的`id`

2. **查询参数**
   - 用于过滤、排序、分页等操作
   - 例如：`/water-levels?start_date=2023-01-01&end_date=2023-01-31`

3. **请求体**
   - 用于POST、PUT、PATCH请求中传递数据
   - 通常使用JSON格式

### 查询参数最佳实践

1. **分页**
   ```
   GET /water-levels?page=2&page_size=100
   # 或
   GET /water-levels?offset=100&limit=100
   ```

2. **排序**
   ```
   GET /water-levels?sort=timestamp:desc
   # 或多字段排序
   GET /stations?sort=province:asc,name:asc
   ```

3. **过滤**
   ```
   # 基本过滤
   GET /stations?status=active
   
   # 高级过滤
   GET /water-levels?level_gt=5.0&level_lt=10.0
   ```

4. **字段选择**
   ```
   # 只返回特定字段
   GET /stations?fields=id,name,location
   ```

5. **搜索**
   ```
   # 全文搜索
   GET /stations?search=长江
   ```

### HTTP状态码使用

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 OK | 成功 | GET请求成功 |
| 201 Created | 已创建 | POST请求创建资源成功 |
| 204 No Content | 无内容 | DELETE请求成功 |
| 400 Bad Request | 请求错误 | 请求参数有误 |
| 401 Unauthorized | 未授权 | 缺少认证信息 |
| 403 Forbidden | 禁止访问 | 无权限访问资源 |
| 404 Not Found | 未找到 | 资源不存在 |
| 409 Conflict | 冲突 | 资源状态冲突 |
| 429 Too Many Requests | 请求过多 | 超出请求频率限制 |
| 500 Internal Server Error | 服务器错误 | 服务器内部异常 |

### 响应数据结构

1. **成功响应**
   ```json
   // 单个资源
   {
     "data": {
       "id": "st12345",
       "name": "金沙江水文站",
       "location": {
         "longitude": 104.0668,
         "latitude": 30.5728
       },
       "latest_water_level": 5.24,
       "warning_level": 8.0
     },
     "links": {
       "self": "/api/v1/stations/st12345",
       "water_levels": "/api/v1/stations/st12345/water-levels",
       "related_reservoirs": "/api/v1/stations/st12345/related-reservoirs"
     }
   }
   ```

2. **错误响应**
   ```json
   {
     "error": {
       "code": "INVALID_PARAMETER",
       "message": "查询参数无效",
       "details": "start_date必须是有效的ISO日期格式",
       "timestamp": "2023-06-15T08:30:45Z",
       "request_id": "req-123456"
     }
   }
   ```

3. **集合资源响应**
   ```json
   {
     "data": [
       {
         "id": "st12345",
         "name": "金沙江水文站",
         "latest_water_level": 5.24
       },
       // ... 更多记录
     ],
     "meta": {
       "total_count": 157,
       "filtered_count": 25
     },
     "links": {
       "self": "/api/v1/stations?page=1&page_size=10",
       "next": "/api/v1/stations?page=2&page_size=10",
       "prev": null,
       "first": "/api/v1/stations?page=1&page_size=10",
       "last": "/api/v1/stations?page=16&page_size=10"
     }
   }
   ```

### 分页响应

```json
{
  "data": [ /* 资源数组 */ ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 157,
    "total_pages": 16
  },
  "links": {
    "self": "/api/v1/stations?page=1&page_size=10",
    "next": "/api/v1/stations?page=2&page_size=10",
    "last": "/api/v1/stations?page=16&page_size=10"
  }
}
```

## 内容协商

### 媒体类型

- 使用`Accept`和`Content-Type`头部进行内容协商
- 常用媒体类型：
  - `application/json`
  - `application/xml`
  - `application/csv`

- 自定义媒体类型可以提供更精确的语义：
  - `application/vnd.waterplatform.station.v1+json`
  - `application/vnd.waterplatform.water-level.v1+json`

### 语言与编码

- 使用`Accept-Language`进行语言协商
  ```
  Accept-Language: zh-CN, zh;q=0.9, en;q=0.8
  ```

- 使用`Accept-Encoding`协商压缩格式
  ```
  Accept-Encoding: gzip, deflate, br
  ```

## 设计提示

### URL设计清单

- 使用名词而非动词表示资源
- 使用复数形式表示集合
- 使用小写字母和连字符(-)
- 层次结构表示资源关系
- 避免在URL中包含API版本（最好放在标头或域名中）
- 保持URL相对简短和有意义

### 请求/响应设计清单

- 使用JSON作为主要数据格式
- 为JSON响应提供规范的结构
- 提供有用的错误消息
- 使用正确的HTTP状态码
- 实现HATEOAS，在响应中包含相关资源链接
- 支持内容协商（格式、语言、编码）

### 命名约定

- 资源名称：使用复数形式的名词，如`stations`
- 属性名称：使用驼峰命名法，如`waterLevel`，或下划线，如`water_level`
- 查询参数：使用下划线分隔单词，如`start_date`
- 统一命名风格，确保一致性

## 习题与思考

1. 设计一个用于智慧水利平台的水文监测数据API，要求符合RESTful设计原则，包括资源设计、HTTP方法使用和响应结构。
2. 分析在水利信息系统中，哪些操作适合用PUT方法，哪些适合用PATCH方法，并解释原因。
3. 针对一个水库调度系统，如何设计符合HATEOAS原则的API响应？请给出具体的JSON示例。 