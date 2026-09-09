# 教学接口（第4章 S1/S2 阶段使用）

零依赖的 Node 18+ 模拟后端，按教材 8.1 节接口契约提供 `/api/auth/login`、`/api/assets`、
`/api/assets/{id}/readings`、`/api/assets/{id}/readings/latest`、`/api/warnings`，数据来自 `companion/datasets`。

```bash
node teaching-api/server.mjs          # 默认 8080，与真实后端同端口，前端 Vite 代理无需改动
```

教学账号：duty01/duty123、analyst01/analyst123、ops01/ops123（与骨架后端 SecurityConfig 一致）。

故障注入（查询参数 `teach=`，真实后端会忽略）：`delay:3000`、`empty`、`invalid`、`unauthorized`、`error`。
例如 `GET /api/assets/DAM-A-PZ-07/readings/latest?teach=delay:3000`。

第5章完成自己的后端后，停掉本服务、启动 Spring Boot 即可，前端代码不需要任何修改——这就是"契约不变，数据来源可换"。
