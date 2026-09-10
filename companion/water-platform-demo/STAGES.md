# S0–S6 阶段包与验收

从本目录（`companion/water-platform-demo`）执行命令。首次使用先在 `frontend/` 执行 `npm ci`。长时间运行的服务分别放在独立终端；以下命令不依赖 shell 后台语法。

| 阶段 | 学习位置 | 已提供入口 | 依赖与实际能力 |
|---|---|---|---|
| S0 | 第1章 | `S0-demo-record.md` | 固定演示记录；解释一次查询的六个环节 |
| S1 | 4.2–4.4 | `lesson44.html`、`lesson44-detail.html` | Node、浏览器；静态列表、详情、筛选与排序 |
| S2 核心 | 4.5 | `lesson45.html` | 教学接口；原生 JavaScript、四种状态与竞态处理 |
| S2 指导实践 | 4.6–4.7 | `index.html`、`src/router/`等骨架 | Vue、Pinia与登录守卫；按书中清单完成详情路由 |
| S3 起点 | 5.2 | `edu.example.lesson52.Lesson52Application` | Java 17、Maven；四个固定对象、部分固定观测，无登录和数据库 |
| S3 终点 | 5.4–5.6、8.3 | 完整 `backend/` 与 Compose | 持久化、认证及契约错误体齐备后承接 S2 联调 |
| S4 | 6.1 | `lesson61.html` | 教学接口、Three.js；坝体几何体与28个测点 |
| S5 | 7.2–7.4 | `lesson74.html` | 教学接口或 S3 完整后端、S4场景；曲线与测点联动 |
| S6 | 8.4 | `classify.js`、`closeloop-check.mjs` | 教学接口验证受控闭环；完整工程另做部署验收 |

## S0：解释请求

直接阅读固定演示记录；需要重新实录时，在终端一运行 `node teaching-api/server.mjs`，在终端二运行 `node teaching-api/record-demo.mjs`。实录是 HTTP 交互证据，学生还要结合1.2.1节解释浏览器渲染等环节。

验收：说明正常请求各环节的责任，并为一次失败指出状态码、日志或页面证据。不要求编程。

## S1：静态列表与详情

```powershell
cd frontend
npm run dev
```

打开终端显示的地址下的 `/lesson44.html`。验收：列表与详情可访问，能按名称或编码筛选、按数值排序；空列表有提示。8个位移测点的 `null` 观测排在末尾。

故障：把详情页编码改为 `DAM-A-XX-99`，应回显编码并提示未找到。保存输入、页面结果与 `lesson44.test.js` 测试输出。

## S2：先验证状态，再迁移到 Vue

终端一在本目录运行 `node teaching-api/server.mjs`；终端二在 `frontend/` 运行 `npm run dev`，打开 `/lesson45.html`。

该页的入口是 `src/lesson45/main.js`，自动使用教学账号登录，采用原生 DOM 操作。它负责验证加载、成功、空数据、失败和快速切换；它没有 Vue Router，也不承担登录回跳的验收。选择无观测的位移测点可观察空状态。

故障注入按8.1节约定，在 `src/lesson45/detail.js` 的最新观测请求 URL 后临时加入 `?teach=delay:3000` 或 `?teach=unauthorized`，试验后恢复。只改浏览器页面地址不会自动把参数传给接口。快速切换两个对象，最后状态必须属于后选对象；401在此核心页显示读取失败。`lesson45.test.js` 用可控响应验证竞态。

Vue指导实践以 `/login`、`/monitoring` 和 `src/router/index.js` 为已提供骨架。按4.6–4.7节实现 `/assets/:id` 详情路由并验证刷新、参数变化和登录回跳；提交修改后的代码与独立证据。现有路由表不包含这条详情路由，不能用 `lesson45.test.js` 代替该项验收。

## S3：分开验收起点和终点

先停教学接口，释放8080。在终端一运行起点：

```powershell
cd backend
mvn spring-boot:run -Dspring-boot.run.main-class=edu.example.lesson52.Lesson52Application
```

终端二回到本目录：

```powershell
node teaching-api/contract-check.mjs http://localhost:8080 --stage=lesson52
```

起点只提供四个固定对象、PZ-07最新值和空历史查询；没有登录端点。直接请求 `/api/assets` 观察四元素数组，核对204、400与404，先不用 S2 的自动登录页。时间参数中的 `+` 应编码为 `%2B`；类型转换失败的统一错误体在5.5节接入。

终点：完成 `README.md` 中的 secrets 和数据准备，停掉起点，在本目录的独立终端执行：

```powershell
docker compose up -d --build
node teaching-api/contract-check.mjs http://localhost:8080 --stage=full
```

终点通过契约核对后再连接 S2 页面，验证认证、对象列表、最新观测与空数据行为。教学接口与终点共用固定数据；起点是教学子集，数据条数和认证能力不能视为相同。

## S4：场景与对象绑定

运行教学接口和 Vite，打开 `/lesson61.html`。坝体可旋转缩放；控制台 `bound.group.children.length` 应等于接口返回的对象数（教学数据为28），`bound.find('DAM-A-PZ-07')` 应返回相应对象。按6.1.5节检查表核对高程、轴方向和单位。

按6.1.1节分别制造缺少光源、相机位置错误、停止渲染循环的黑屏情形；每次只改一个因素，恢复后验证。记录现象、原因、处理、结果。

## S5：曲线与场景联动

运行教学接口和 Vite，打开 `/lesson74.html`。点球应切换曲线；点曲线数据点应高亮对应球；点坝体或空白应提示未选中。此页可以直接使用教学接口，不必先启动 Java 和数据库。

依次验证：快速切换两个测点、选择无观测的位移测点、断网后重试。异步控制器必须同时约束曲线、单位与状态文字；切换开始即解绑旧联动。`lesson74.test.js` 验证映射与拾取，`series-controller.test.js` 用可控顺序覆盖旧响应、空结果、网络错误和卸载后迟到响应。

自动化通过后仍需在真实浏览器核对坐标、视图布局与交互，这些不由无 WebGL 的测试代替。

## S6：预警与工单闭环

先运行教学接口，在另一终端执行：

```powershell
node teaching-api/closeloop-check.mjs http://localhost:8080
```

在 `frontend/` 运行 `npm test`，其中 `lesson84.test.js` 核对质量门禁与蓝黄橙红分界。故障：高分但质量为 `suspect` 的记录必须未评估；未评估事件不能确认。记录确认、派单、完成与归档的受控转换。

完整工程的部署验收另按 `README.md` 启动 Compose，在 Git Bash/Linux 执行 `./smoke.sh`；教学内存闭环通过不代表持久化和容器恢复已经通过。

## 构建与交付

在 `frontend/` 执行 `npm run build`，生产包应包含 `index.html`、`lesson44.html`、`lesson44-detail.html`、`lesson45.html`、`lesson61.html`、`lesson74.html` 六个入口。静态服务器须配置 `/api` 代理；Vite开发代理不会自动进入生产服务器。阶段页使用现代浏览器的 ES2022 能力。

各阶段字段与错误体以教材8.1节为准；运行版本以随书发行包的 `package-lock.json`、`pom.xml`、Compose和 `MAPPING.md` 为准。每次实验提交一个可观察结果及一条“现象→原因→处理→验证”的失败记录。
