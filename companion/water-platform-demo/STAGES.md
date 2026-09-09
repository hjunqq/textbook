# S0–S6 阶段包总表

本文件回答一个问题：**学完某一段，学生手上应该有什么能跑起来的东西，怎么验收。**

阶段划分与教材一致（前言的学习路线、第4章表“第4章两个阶段的验收检查单”）。
每一行的“可见成果”是学生能演示的东西，“注入故障”是必须亲手复现一次的失败，
“证据”是验收时要交的东西——不是截图好看，而是能说明系统在异常时做了什么。

| 阶段 | 学习位置 | 入口 | 运行依赖 | 可见成果 |
|---|---|---|---|---|
| S0 | 第1章 | `S0-demo-record.md` | 无（教师投影固定记录） | 看懂平台一次操作的六个环节 |
| S1 | 第4章 4.2–4.4 | `lesson44.html` / `lesson44-detail.html` | 浏览器 + `npm run dev` | 静态测点列表与详情、筛选、排序 |
| S2 | 第4章 4.5–4.7 | `lesson45.html` | S1 + 教学接口 | Vue 页面、四种页面状态、竞态修复 |
| S3 | 第5章 | `edu.example.lesson52` → 完整 `backend/` | JDK 17 + Maven（终点还需 PostgreSQL） | 自己写的接口替换教学接口，页面不改 |
| S4 | 第6章 | `lesson61.html` | S2 + Three.js | 坝体场景 + 28 个测点绑定 |
| S5 | 第7章 | `lesson74.html` | S3 + S4 | 观测曲线与三维对象双向联动 |
| S6 | 第8章 | `classify.js` + `closeloop-check.mjs` | 教学接口（终点需完整工程） | 质量门禁、四级预警、工单闭环 |

## 每个阶段怎么跑，怎么验收

### S0 演示记录（第1章）

```bash
node teaching-api/server.mjs &
node teaching-api/record-demo.mjs > S0-demo-record.md
```

记录是实录生成的，不是手写示例。**验收**：学生能指着记录说出，
页面显示不出数据时，六个环节里各应该去哪里找证据；不要求写代码。

### S1 静态监测页（第4章 4.2–4.4）

```bash
cd frontend && npm run dev     # 打开 /lesson44.html
```

**必须能演示**：列表与详情两个页面；按名称或编码筛选；按最新观测值排序；
非法输入有提示；筛选结果为空时显示“暂无测点”。
**注入故障**：把详情页地址里的编码改成 `DAM-A-XX-99`——格式合法但台账里没有。
**证据**：页面截图；开发者工具“元素”面板里的 `aria-*` 属性；`npm test` 中 lesson44 用例通过。

值得注意的一点：8 个位移测点没有观测，`value` 为 `null`。
按值升序排序时它们必须留在末尾——把 `null` 当成 0，它们会挤到最前面，看起来像读数最低的一批。

### S2 数据请求与页面状态（第4章 4.5–4.7）

```bash
node teaching-api/server.mjs &
cd frontend && npm run dev     # 打开 /lesson45.html
```

**必须能演示**：登录后读取对象列表与最新观测；加载、空数据、错误、正常四种状态都能看到；
快速切换两个对象时不出现旧数据；路由可直接打开详情深链接。
**注入故障**：`teach=delay:3000` 与 `teach=unauthorized`。
**证据**：“网络”面板里被取消的请求；401 后回登录页并能回跳；`lesson45.test.js` 通过。

### S3 自己的接口（第5章）

```bash
# 起点：一个类、无数据库、无认证。先停掉教学接口，否则 8080 端口冲突
cd backend
mvn spring-boot:run -Dspring-boot.run.main-class=edu.example.lesson52.Lesson52Application
node ../teaching-api/contract-check.mjs http://localhost:8080 --stage=lesson52

# 终点：完整工程（需数据库）
docker compose up -d --build
node teaching-api/contract-check.mjs http://localhost:8080 --stage=full
```

**必须能演示**：第4章的页面一行不改，换成自己的后端仍然工作。
**注入故障**：把 `from` 里的 `+` 原样放进地址栏——解析失败发生在进入控制器之前，
控制器里的异常处理器接不到，必须由 `@RestControllerAdvice` 兜住。
**证据**：`contract-check.mjs` 三种来源全绿。这是整套阶段包里最重要的一条验收：
它证明契约不是文档里的约定，而是可执行的。

### S4 三维场景（第6章）

```bash
node teaching-api/server.mjs &
cd frontend && npm run dev     # 打开 /lesson61.html
```

**必须能演示**：坝体长方体可拖动缩放；28 个测点绑在正确位置；
控制台 `bound.find('DAM-A-PZ-07')` 能取到对象。
**注入故障**：黑屏的三种原因（没有光、相机在物体内部、忘了渲染循环）各制造一次。
**证据**：`bound.group.children.length` 等于接口返回的对象数；
所有球的 y 落在坝基与坝顶之间。

### S5 曲线与三维联动（第7章）

```bash
node teaching-api/server.mjs &
cd frontend && npm run dev     # 打开 /lesson74.html
```

**必须能演示**：点场景里的球，曲线切到该测点；点曲线上的数据点，对应的球变橙。
**注入故障**：点坝体或空白处——必须提示“未选中测点”，不能高亮一个错误的球。
**证据**：`lesson74.test.js` 通过，其中覆盖下标越界、曲线里没有该对象、
换对象前先解绑三条边界。

### S6 质量、预警与闭环（第8章）

```bash
node teaching-api/server.mjs &
node teaching-api/closeloop-check.mjs http://localhost:8080
cd frontend && npm test         # lesson84 用例：质量门禁与四级定级
```

**必须能演示**：一条 PZ-07 的观测经质量检查触发预警，值班员确认、派单、
处置回写、预警归档。
**注入故障**：拿一条 `suspect` 的高分记录去定级——必须是“未评估”，
不能因为分数高就升级；拿一条未评估的事件去确认——必须被拒绝。
**证据**：`closeloop-check.mjs` 全绿；`docker compose up` 后 `./smoke.sh` 通过。

## 一条贯穿线

七个阶段用的是同一份数据和同一份契约：

- **数据**：`companion/datasets/` 的 28 个测点与三份观测 CSV。S1 把它写成字面量，
  S2–S6 由教学接口或真实后端应答，数值一致（DAM-A-WL-01 = 166.84 m，
  DAM-A-PZ-07 = 185.09 kPa）。
- **契约**：教材 8.1 节的接口契约表。字段名 `assetId` / `displayName` / `value` /
  `unit` / `quality` / `occurredAt`，错误体 `{code, message, field?}`，从 S1 到 S6 不变。

所以换数据源不需要改业务代码——这句话在 S3 那一步会被 `contract-check.mjs` 当场验证。
