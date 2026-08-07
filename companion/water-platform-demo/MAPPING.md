# 教材—工程核对表

| 教材内容 | 工程位置 |
|---|---|
| 第4章 `request.js`、Vue 3 SFC、Router、Pinia | `frontend/src/utils/request.js`, `frontend/src/components/MonitoringDashboard.vue`, `frontend/src/router/index.js`, `frontend/src/stores/monitoring.js` |
| 第5章 Jakarta 实体、Repository、事务服务 | `backend/src/main/java/edu/example/qingyuan/AssetEntity.java`, `ReadingEntity.java`, `ReadingRepository.java`, `ReadingService.java` |
| 第5章 SecurityFilterChain 与 JWT 过滤器 | `SecurityConfig.java`, `JwtAuthenticationFilter.java` |
| 第5章 Kafka 生产/消费边界 | `ReadingConsumer.java`；生产者由事务发件箱服务接入同一 topic |
| 第8章 A8-1 DDL 与质量码约束 | `db/001_init.sql`；初始化数据入口 `db/load-s3-data.sql` |
| 第8章 A8-3 API、Vue 页面和场景桥接 | `frontend/src`；页面使用 S3 的 `asset_id/event_id/quality` 字段 |
| 第8章 A8-4 Compose 与健康检查 | `docker-compose.yml`、`frontend/Dockerfile`、`backend/Dockerfile` |

SQL 清单的字段名、Java DTO/实体和 Vue API 均以 `db/001_init.sql` 为准；新增字段必须先更新迁移、数据集和教材字典。工程只保留可独立运行的核心切片，教材中的查询练习在同一 schema 上执行。
