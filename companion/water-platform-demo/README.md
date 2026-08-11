# 水利工程安全监测平台 · 最小可运行闭环

本仓库是《智慧水利平台架构与开发》的配套工程，提供一条**最小可运行闭环**：
登录认证 → 测点/观测查询 → Kafka 消息消费入库 → 一条命令启动 → 前后端冒烟测试。
它是练习的起点仓库；书中 200+ 代码清单是把它改造成完整平台的施工图（对应关系见 `MAPPING.md`）。

## 一条命令启动

```bash
cp secrets/db_password.txt.example secrets/db_password.txt
cp secrets/kafka_password.txt.example secrets/kafka_password.txt
docker compose up -d --build
./smoke.sh        # 启动—401拒绝—登录—取数—错误口令 五步验证
```

启动后访问 http://localhost:8080 ，使用教学账号登录：

| 账号 | 口令 | 角色 |
|---|---|---|
| duty01 | duty123 | 值班员（DUTY） |
| analyst01 | analyst123 | 专业分析员（ANALYST） |
| ops01 | ops123 | 运维员（OPS） |

数据库初始化脚本自动建表（`db/001_init.sql`）并写入种子观测（`db/002_seed.sql`），
页面开箱即有渗压曲线（含一段缺测断线与一条可疑值）。完整 28 测点数据集见
`../datasets/`，在本目录下执行一条命令即可导入（psql 客户端 `\copy`，CSV 相对路径按
当前目录解析，坐标与种子数据一致）：

```bash
psql "postgresql://qingyuan_app:<密码>@localhost:5432/qingyuan" -f db/load-s3-data.sql
```

## 正常链路与故障链路

正常链路：登录 → 选择测点 → 时间窗查询 → 曲线渲染（缺测断线、可疑标注）。
故障链路（均可当场复现）：
- 未登录访问 `/api/assets` → 401，前端跳转登录页并携带回跳地址；
- 错误口令 → 401，登录页就地提示，不发生页面跳转；
- 传入 `from >= to` 的时间窗 → 前端 `readingQuery` 直接拒绝，不发出请求；
- Kafka 收到重复 `eventId` 事件 → 由 `(occurred_at, event_id)` 复合唯一索引裁决，
  消费者在事务边界之外捕获冲突并确认消息（第8章 8.3 节的口径）。

## 各自运行测试

```bash
cd frontend && npm ci && npm test     # vitest：6 个断言（缺测断线/时间窗/令牌契约）
cd backend  && mvn -q test            # JUnit：JWT 签发/过期/篡改 + 事件契约反序列化
```

测试不依赖数据库与 Kafka，可在任何装有 Node 20+ 与 JDK 17 的机器上直接运行。

## 目录

```
frontend/   Vue 3.4 + Pinia + Vue Router + ECharts；登录页、监测页、请求封装
backend/    Spring Boot 3.2 + Security 6 + JPA + Kafka；JWT 过滤器、幂等消费
db/         001 建表（TimescaleDB 超表 + 复合唯一索引）、002 种子数据
secrets/    Docker secrets 模板（*.example，正式文件不入库）
smoke.sh    端到端冒烟脚本
```

## 安全说明

教学口令与 JWT 默认密钥仅用于课堂；部署到任何可被他人访问的环境前，
必须替换 `secrets/` 与 `JWT_SECRET`，并按第5章的密钥轮换与撤销策略管理。
