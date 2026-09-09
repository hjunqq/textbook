# S0 演示记录：一次“查看某测点历史观测”的完整过程

> 本文件由 `teaching-api/record-demo.mjs` 对运行中的教学接口实录生成，
> 不是手写的示例。对照第1章 1.2.1 节的六环节追踪图阅读。

> 生成时间：2026-09-09T07:55:14.126Z　数据来源：教学接口 http://localhost:8080

---

### 环节 1：页面动作 → 身份

**这一步在做什么**：值班员在登录页提交账号口令，页面把它变成一次 HTTP 请求。

```http
POST /api/auth/login
Content-Type: application/json

{"username":"duty01","password":"duty123"}
```

**响应**：`200 OK`，耗时 70 ms

```json
{"accessToken":"-dT9t9j7sJfewtEkgsz0PjJr6TrTsmuY","expiresInSeconds":1800,"authorities":["DUTY"]}
```

平台发回一个有效期 1800 秒的令牌，角色为 `DUTY`。此后每个业务请求都要带上它。

### 环节 2：HTTP 请求 → 对象列表

**这一步在做什么**：页面要先知道有哪些测点，才能让用户选一个。

```http
GET /api/assets
Authorization: Bearer <令牌已省略>
```

**响应**：`200 OK`，耗时 3 ms

```json
[{"assetId":"DAM-A-PZ-01","displayName":"案例渗压01","assetType":"渗压","unit":"kPa"},{"assetId":"DAM-A-PZ-02","displayName":"案例渗压02","assetType":"渗压","unit":"kPa"},{"assetId":"DAM-A-PZ-03","displayName":"案例渗压03","assetType":" …（已截断）
```

### 环节 3：服务处理 → 最新观测

**这一步在做什么**：选中案例渗压07 后，页面请求它的最新一条观测。

```http
GET /api/assets/DAM-A-PZ-07/readings/latest
Authorization: Bearer <令牌已省略>
```

**响应**：`200 OK`，耗时 2 ms

```json
{"assetId":"DAM-A-PZ-07","occurredAt":"2026-07-01T23:55:00+08:00","value":185.091,"unit":"kPa","quality":"valid","eventId":"evt-pz-0287-6","version":1}
```

### 环节 4：数据查询 → 一段历史

**这一步在做什么**：把时间窗交给平台，取回一段观测用来画曲线。时间必须带时区。

```http
GET /api/assets/DAM-A-PZ-07/readings?from=2026-07-01T00%3A00%3A00%2B08%3A00&to=2026-07-01T02%3A00%3A00%2B08%3A00
Authorization: Bearer <令牌已省略>
```

**响应**：`200 OK`，耗时 2 ms

```json
[{"assetId":"DAM-A-PZ-07","occurredAt":"2026-07-01T00:00:00+08:00","value":181.2,"unit":"kPa","quality":"valid","eventId":"evt-pz-0000-6","version":1},{"assetId":"DAM-A-PZ-07","occurredAt":"2026-07-01T00:05:00+08:00","va …（已截断）
```

### 环节 5：页面更新 → 预警状态

**这一步在做什么**：曲线之外，值班员还要看到这个测点当前有没有预警。

```http
GET /api/warnings?assetId=DAM-A-PZ-07
Authorization: Bearer <令牌已省略>
```

**响应**：`200 OK`，耗时 1 ms

```json
[{"warningId":"w-0002","assetId":"DAM-A-PZ-07","level":"YELLOW","evaluable":true,"score":0.58,"reason":"渗压趋势超过黄色阈值","status":"acknowledged"}]
```

---

## 出问题时去哪里找证据

把上面五个环节各破坏一次，观察平台的回答有什么不同。
这四种情况都能当场复现，也都是第4章要在页面上分别显示的状态。

### 环节 6a：证据一：不带令牌

**这一步在做什么**：模拟令牌过期。页面应当清除令牌并跳转登录页，登录后回到原页面。

```http
GET /api/assets
```

**响应**：`401 Unauthorized`，耗时 1 ms

```json
{"code":"UNAUTHORIZED","message":"未登录或令牌已失效"}
```

### 环节 6b：证据二：编码打错

**这一步在做什么**：模拟用户输错对象编码。404 与 204 必须分开——前者是“没有这个测点”，后者是“有但还没上报”。

```http
GET /api/assets/DAM-A-XX-99/readings/latest
Authorization: Bearer <令牌已省略>
```

**响应**：`404 Not Found`，耗时 2 ms

```json
{"code":"ASSET_NOT_FOUND","message":"对象 DAM-A-XX-99 不存在"}
```

### 环节 6c：证据三：有测点但没观测

**这一步在做什么**：位移测点在数据集中没有观测记录。页面应显示“暂无观测”，不是报错也不是空白。

```http
GET /api/assets/DAM-A-D-01/readings/latest
Authorization: Bearer <令牌已省略>
```

**响应**：`204 No Content`，耗时 1 ms

```json
（空响应体）
```

### 环节 6d：证据四：时间窗写反

**这一步在做什么**：from 晚于 to。错误体里的 field 指出是哪个字段错了，页面据此定位输入框。

```http
GET /api/assets/DAM-A-PZ-07/readings?from=2026-07-02T00%3A00%3A00%2B08%3A00&to=2026-07-01T00%3A00%3A00%2B08%3A00
Authorization: Bearer <令牌已省略>
```

**响应**：`400 Bad Request`，耗时 4 ms

```json
{"code":"INVALID_RANGE","message":"from 必须早于 to","field":"from"}
```

| 破坏方式 | 状态码 | 错误码 | 页面应有的表现 |
|---|---|---|---|
| 不带令牌 | 401 | UNAUTHORIZED | 清除令牌，跳登录页，登录后回跳 |
| 编码打错 | 404 | ASSET_NOT_FOUND | “对象不存在，请返回列表” |
| 有测点无观测 | 204 | — | “暂无观测”，不是报错 |
| 时间窗写反 | 400 | INVALID_RANGE（field=from） | 提示到具体字段，保留已输入的值 |

五个环节里的路径、字段名和错误码，都能在教材 8.1 节的接口契约表里查到。
如果实录结果与契约表对不上，说明某一端写歪了——这正是第5章契约核对脚本要拦住的事。
