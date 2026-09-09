# 仓库文件与教材章节对应表

## 工程版本线（与教材第4—8章开头的版本卡对应）

| 版本 | 完成于 | 能力 | 本仓库对应 |
|---|---|---|---|
| v0 | 起点 | 空骨架 | 仓库初始结构 |
| v1 | 第4章 | 登录+只读监测页 | frontend/ 全部；4.5 节阶段页 lesson45.html 可只靠 teaching-api 运行 |
| v2 | 第5章 | JWT认证+观测API | backend/ 全部 |
| v3 | 第6章 | 三维场景页 | （课程实现，见第6章清单） |
| v4 | 第7章 | 曲线与三维联动 | frontend/src/utils/readings.js 起点 |
| v5 | 第8章核心篇 | 质量检查+预警+工单+部署 | db/、ReadingConsumer、compose、smoke.sh 骨架 |

本仓库即 v1+v2+v5 骨架的合体（最小可运行闭环）；v3、v4 与 v5 的完整实现由读者按教材清单增量完成。


| 仓库文件 | 对应章节 | 说明 |
|---|---|---|
| teaching-api/server.mjs | 4.5 / 8.1 | 零依赖教学接口：按 8.1 接口契约用固定数据集应答，`teach=` 故障注入 |
| frontend/lesson45.html + src/lesson45/*.js | 4.5 | S2 阶段页：detail.js（清单 4.5.2）、state.js（4.5.3）、controller.js（4.5.4 故障单元） |
| frontend/tests/lesson45.test.js | 4.5.4 / 4.5.8 | 竞态覆盖的自动化验证（先发请求被取消、最终页面属于后点击对象） |
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
