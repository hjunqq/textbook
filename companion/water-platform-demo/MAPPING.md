# 仓库文件与教材章节对应表

| 仓库文件 | 对应章节 | 说明 |
|---|---|---|
| frontend/src/utils/auth.js | 4.5 | TOKEN_KEY 单一契约 |
| frontend/src/utils/request.js | 4.5 | 令牌注入、401 分流（认证端点豁免） |
| frontend/src/utils/readings.js | 7.2 | 缺测断线、时间窗校验（纯函数，可测试） |
| frontend/src/views/LoginView.vue | 4.7 | 登录与安全回跳 |
| frontend/src/router/index.js | 4.7 | 路由守卫 |
| frontend/src/stores/monitoring.js | 4.7 / 8.3 | Pinia 状态与查询参数 |
| frontend/src/components/MonitoringDashboard.vue | 7.2 / 8.3 | ECharts 曲线、缺测与可疑呈现 |
| frontend/tests/*.test.js | 4.8 | vitest 单元测试 |
| backend/.../JwtService.java | 5.5 | jjwt 0.11.x 签发与校验 |
| backend/.../JwtAuthenticationFilter.java | 5.5 | Bearer 解析入 SecurityContext |
| backend/.../SecurityConfig.java | 5.5 | 无状态过滤链、CORS、教学账号 |
| backend/.../AuthController.java | 5.5 | 登录端点（防账号枚举） |
| backend/.../AssetController.java | 5.3 / 8.3 | DTO 映射，不暴露实体 |
| backend/.../ReadingService.java | 5.4 / 8.3 | 事务边界、幂等预检 |
| backend/.../ReadingConsumer.java | 5.6 / 8.3 | 事务边界外捕获冲突 |
| backend/.../FileSecretsEnvironmentPostProcessor.java | 8.6 | Docker secrets 的 *_FILE 约定 |
| backend/src/test/... | 5.8 | JUnit 单元测试（无外部依赖） |
| db/001_init.sql | 8.3 | 超表 + (occurred_at,event_id) 复合唯一索引 |
| db/002_seed.sql | 8.3 | 种子观测（含缺测与可疑样例） |
| docker-compose.yml | 8.6 | 服务编排、healthcheck、secrets |
| smoke.sh | 8.6 | 端到端冒烟验证 |
