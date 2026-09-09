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

## contract-check.mjs：三种数据来源跑同一套断言

教学接口、S3 起点（`edu.example.lesson52`）和接了数据库的完整后端，
必须对同一组请求给出同样形状的响应——状态码、字段名、错误体三者一致，
第4章的页面才能不改一行代码换数据源。这一点由 `contract-check.mjs` 逐条核对，
断言来自教材表 tab:ch05-first-verify 与 8.1 节契约表的通用约定。

```bash
# 教学接口（默认）
node teaching-api/server.mjs &
node teaching-api/contract-check.mjs http://localhost:8080 --stage=teaching

# S3 起点：先停掉教学接口，否则 8080 端口冲突
cd backend && mvn spring-boot:run -Dspring-boot.run.main-class=edu.example.lesson52.Lesson52Application
node teaching-api/contract-check.mjs http://localhost:8080 --stage=lesson52

# 完整后端（需数据库，见根目录 docker-compose.yml）
node teaching-api/contract-check.mjs http://localhost:8080 --stage=full
```

三个阶段的数据深度不同（固定数据集 28 个对象 / 5.2 节写死的 4 个 / 数据库种子），
所以脚本按阶段裁剪对数据的期望，但**契约形状的断言三者完全相同**。
退出码非 0 表示有断言失败，逐条打印在前面。

## closeloop-check.mjs：第8章闭环

把“观测 → 质量检查 → 预警 → 值班员确认 → 工单 → 处置回写并归档”写成可执行断言，
并验证 8.4 节状态流转图上的三条受控约束：未评估的事件不能确认、没确认不能派单、
已完成的工单不能重复完成。

```bash
node teaching-api/server.mjs &
node teaching-api/closeloop-check.mjs http://localhost:8080
```

教学接口为此新增了 `POST /api/warnings/{id}/ack`、`POST /api/work-orders`
与 `POST /api/work-orders/{id}/complete`（内存态，重启即清空），
按 8.1 契约应答，不需要数据库。第8章的清单在真实后端实现完成后，
同一个脚本应当同样全绿。
