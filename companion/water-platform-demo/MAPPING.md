# 仓库文件与教材章节对应表

## 工程版本线（与教材第4—8章开头的版本卡对应）

| 版本 | 完成于 | 能力 | 本仓库对应 |
|---|---|---|---|
| v0 | 起点 | 空骨架 | 仓库初始结构 |
| v1 | 第4章 | 登录+只读监测页 | frontend/ 全部；S1 阶段页 lesson44.html + lesson44-detail.html 不依赖后端；S2 阶段页 lesson45.html 只靠 teaching-api 运行 |
| v2 | 第5章 | JWT认证+观测API | backend/ 全部 |
| v3 | 第6章 | 三维场景页 | lesson61.html 为起点（坝体长方体 + 28 测点绑定）；GLTF 模型与 GIS 集成为课程实现 |
| v4 | 第7章 | 曲线与三维联动 | frontend/src/utils/readings.js 起点 |
| v5 | 第8章核心篇 | 质量检查+预警+工单+部署 | db/、ReadingConsumer、compose、smoke.sh 骨架 |

本仓库即 v1+v2+v5 骨架的合体（最小可运行闭环）；v3、v4 与 v5 的完整实现由读者按教材清单增量完成。


| 仓库文件 | 对应章节 | 说明 |
|---|---|---|
| frontend/lesson44.html + lesson44-detail.html | 4.2 / 4.8.1 | S1 阶段页：列表与详情，只需浏览器与 `npm run dev`，无框架无后端；骨架取自清单 lst:ch04-html-shell |
| frontend/lesson44.css | 4.3 | border-box、CSS 变量主题、Grid 卡片与移动优先断点；对应清单 lst:ch04-css-responsive |
| frontend/src/lesson44/assets.js | 4.8.1 | S1 固定数据：28 个测点的最新观测，取自 companion/datasets，字段名遵循 8.1 接口契约 |
| frontend/src/lesson44/query.js | 4.4 | 筛选、排序、编码校验的纯函数；null 值排末尾，不当作 0 |
| frontend/src/lesson44/render.js | 4.4.4 | DocumentFragment + textContent 安全写入，空结果写“暂无测点”；对应清单 lst:ch04-a44-dom |
| frontend/src/lesson44/list.js | 4.4.6 | 事件委托与表单校验装配；对应清单 lst:ch04-a44-events、lst:ch04-a44-dom-script |
| frontend/src/lesson44/detail.js | 4.4 / 4.7.1 | 从 ?assetId= 取参数，未找到时回显编码；4.7 节换成 Vue Router 深链接 |
| frontend/tests/lesson44.test.js | 4.8.1 | S1 验收用例：筛选、排序、空态、非法输入与故障 DAM-A-XX-99 |
| teaching-api/server.mjs | 4.5 / 8.1 | 零依赖教学接口：按 8.1 接口契约用固定数据集应答，`teach=` 故障注入 |
| frontend/lesson45.html + src/lesson45/*.js | 4.5 | S2 阶段页：detail.js（清单 4.5.2）、state.js（4.5.3）、controller.js（4.5.4 故障单元） |
| frontend/tests/lesson45.test.js | 4.5.4 / 4.5.8 | 竞态覆盖的自动化验证（先发请求被取消、最终页面属于后点击对象） |
| frontend/lesson61.html + src/lesson61/*.js | 6.1.1 / 6.1.5 | S4 阶段起点：first-scene.js（清单 6.1 首个场景）、bind-assets.js（对象绑定），坐标取 public/datasets/stations.json |
| frontend/src/utils/auth.js | 4.5 | TOKEN_KEY 单一契约 |
| frontend/src/utils/request.js | 4.5 | 令牌注入、401 分流（认证端点豁免） |
| frontend/src/utils/readings.js | 7.2 | 缺测断线、时间窗校验（纯函数，可测试） |
| frontend/src/views/LoginView.vue | 4.5.7 / 4.7 | 登录与安全回跳 |
| frontend/src/router/index.js | 4.7.1 | 路由守卫 |
| frontend/src/stores/monitoring.js | 4.7.4 / 8.3 | Pinia 状态与查询参数 |
| frontend/src/components/MonitoringDashboard.vue | 7.2 / 8.3 | ECharts 曲线、缺测与可疑呈现 |
| frontend/tests/*.test.js | 4.8.1 | vitest 单元测试 |
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
