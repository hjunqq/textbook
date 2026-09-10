# 仓库文件与教材章节对应表

## 工程版本线（与教材第4—8章开头的版本卡对应）

| 版本 | 完成于 | 能力 | 本仓库对应 |
|---|---|---|---|
| v0 | 起点 | 空骨架 | 仓库初始结构；第1章的 S0 演示记录见 S0-demo-record.md（由 teaching-api/record-demo.mjs 实录生成） |
| v1 | 第4章 | 登录+只读监测页 | frontend/ 全部；S1 阶段页 lesson44.html + lesson44-detail.html 不依赖后端；S2 阶段页 lesson45.html 只靠 teaching-api 运行 |
| v2 | 第5章 | JWT认证+观测API | S3 起点 backend/src/main/java/edu/example/lesson52/（单类、无库、无认证）；S3 终点 backend/ 全部 |
| v3 | 第6章 | 三维场景页 | lesson61.html 为起点（坝体长方体 + 28 测点绑定）；GLTF 模型与 GIS 集成为课程实现 |
| v4 | 第7章 | 曲线与三维联动 | S5 阶段页 lesson74.html（拾取→曲线→高亮双向联动），依赖 S3 与 S4 |
| v5 | 第8章核心篇 | 质量检查+预警+工单+部署 | S6：classify.js（定级）+ 教学接口的 ack/工单端点 + closeloop-check.mjs（闭环核对）；db/、ReadingConsumer、compose、smoke.sh 骨架 |

本仓库包含各阶段可运行的教学切片；完整业务界面、详情路由、GLTF/GIS集成等课程任务由读者在骨架上完成。已提供能力与学生待完成任务逐项见 STAGES.md。


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
| frontend/lesson74.html + src/lesson74/main.js | 7.2.4 / 7.4 | S5 阶段页：真实观测曲线与三维对象双向联动 |
| frontend/src/lesson74/scene-bus.js | 7.2.4 | 清单 lst:ch07-link-controller 注释里说的“应用层场景封装”，事件总线 + focusAsset，不依赖 three |
| frontend/src/lesson74/link.js | 7.2.4 | 与清单 lst:ch07-link-controller 逐字一致；chart 与 scene 均为注入 |
| frontend/src/lesson74/picker.js | 7.4 | 与清单 lst:ch07-point-picker 逐字一致（THREE 改为模块导入），另加 firstAsset 跳过坝体回指测点 |
| frontend/tests/lesson74.test.js | 7.2.4 / 7.4 | S5 验收：高亮切换、下标越界、解绑、拾取回指 |
| frontend/src/lesson74/series-controller.js + tests/series-controller.test.js | 4.5.4 / 7.2.4 | 切换立即解绑、取消与序号校验、空数据/失败/卸载回归 |
| frontend/src/lesson74/window-chart.js + tests/window-chart.test.js | 7.2.2 | 与清单 lst:ch07-append-data 一致；实测 ECharts 折线更新、300点窗口、缺测与双轴 |
| frontend/src/views/LoginView.vue | 4.5.7 / 4.7 | 登录与安全回跳 |
| frontend/src/router/index.js | 4.7.1 | 路由守卫 |
| frontend/src/stores/monitoring.js | 4.7.4 / 8.3 | Pinia 状态与查询参数 |
| frontend/src/components/MonitoringDashboard.vue | 7.2 / 8.3 | ECharts 曲线、缺测与可疑呈现 |
| frontend/tests/*.test.js | 4.8.1 | vitest 单元测试 |
| backend/.../JwtService.java | 5.6 | jjwt 0.11.x 签发与校验 |
| backend/.../JwtAuthenticationFilter.java | 5.6 | Bearer 解析入 SecurityContext |
| backend/.../SecurityConfig.java | 5.6 | 无状态过滤链、CORS、教学账号 |
| backend/.../AuthController.java | 5.6 | 登录端点（防账号枚举） |
| backend/edu/example/lesson52/ | 5.2 | S3 阶段起点：清单 lst:ch05-first-controller + lst:ch05-first-params 合并成的可运行类；独立根包，避免与完整工程的 /api/assets 映射冲突 |
| teaching-api/contract-check.mjs | 5.2.3 / 8.1 | 把表 tab:ch05-first-verify 与契约错误体写成可执行检查；--stage=teaching/lesson52/full 对三种数据来源跑同一套断言 |
| backend/.../ApiExceptionHandler.java | 5.5 / 8.1 | 契约错误体 {code, message, field?}；兜住控制器接不到的时间参数解析失败 |
| backend/.../AssetController.java | 5.2 / 8.3 | DTO 映射，不暴露实体；readings/latest 按契约区分 404（对象不存在）与 204（尚无观测） |
| backend/.../ReadingService.java | 5.4 / 8.3 | 事务边界、幂等预检 |
| backend/.../ReadingConsumer.java | 5.7 / 8.3 | 事务边界外捕获冲突 |
| backend/.../FileSecretsEnvironmentPostProcessor.java | 8.6 | Docker secrets 的 *_FILE 约定 |
| backend/src/test/... | 5.9 | JUnit 单元测试（无外部依赖） |
| db/001_init.sql | 8.3 | 超表 + (occurred_at,event_id) 复合唯一索引 |
| db/002_seed.sql | 8.3 | 种子观测（含缺测与可疑样例） |
| docker-compose.yml | 8.6 | 服务编排、healthcheck、secrets |
| frontend/src/lesson84/classify.js | 8.4 | 质量码门禁与四级定级；evaluable 与 level 两个维度，阈值 0.30/0.50/0.70/0.85 与 warnings.json 一致 |
| frontend/tests/lesson84.test.js | 8.4 | 前三个用例与清单 lst:ch08-classification-test 的 JUnit 断言一一对应 |
| teaching-api/closeloop-check.mjs | 8.4 / 8.6 | S6 闭环核对：观测→质量→预警→确认→工单→回写→归档，含三条受控状态约束 |
| smoke.sh | 8.6 | 端到端冒烟验证 |

## 面向读者的三份索引

| 文件 | 给谁看 | 内容 |
|---|---|---|
| STAGES.md | 学生 | S0–S6 每个阶段的入口、运行依赖、必须能演示的行为、注入故障与验收证据 |
| TEACHING.md | 教师 | 核心教学路线与 56 学时分配、O1–O7 验收证据、六处常见卡点、实验课收法、环境清单 |
| S0-demo-record.md | 第1章课堂 | 一次“查看某测点历史观测”的完整实录，含四种失败情形的状态码与错误码 |
