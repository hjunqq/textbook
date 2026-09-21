# 智慧水利平台架构与开发

面向水利类专业本科三年级的教材。读者学过一门编程语言（Python、Java、C 或 C# 均可），不要求学过 Web 前后端和软件工程。

## 这门课学什么

全书围绕一个虚构的“案例水库安全监测平台”展开：28个测点的观测数据怎样从接口到页面、到曲线、到三维场景，再到预警和处置。学完核心内容后，你应当能够：

1. 说清一个智慧水利平台由哪些部分组成，一次“查询渗压计 PZ-07 最新观测”的请求经过了哪些环节；
2. 在配套工程骨架上实现监测对象查询、观测曲线、三维测点关联和一条简单的预警规则；
3. 解释水利观测数据的单位、时间、质量码、坐标与高程在程序里怎样表示，为什么不能省；
4. 遇到“页面空白”“接口 404”“曲线断线”这类常见异常时，知道先看什么证据。

课程会让你接触 Vue、Spring Boot、Three.js、PostgreSQL 等多种技术，但目标是**读得懂、改得动、讲得清**，不是熟练掌握整套技术栈。消息队列、数字孪生调度、复杂性能调优等内容安排为选读。

## 全书结构

| 章 | 标题 | 你会做什么 |
|---|---|---|
| [前言](前言.md) | 读者起点、学时方案、核心与选读的划分 | 选一条学习路线 |
| [第1章](chapters/chapter01/chapter01.md) | 智慧水利概述与平台架构基础 | 读一次请求的全过程（S0 演示记录） |
| [第2章](chapters/chapter02/chapter02.md) | 软件工程基础与需求分析 | 把业务问题写成可检验的需求 |
| [第3章](chapters/chapter03/chapter03.md) | 软件架构设计与模块划分 | 划分模块，约定接口，走查一次请求 |
| [第4章](chapters/chapter04/chapter04.md) | 前端开发技术 | 静态列表与详情页（S1），带四种状态的请求页面（S2） |
| [第5章](chapters/chapter05/chapter05.md) | 后端开发技术 | 第一个 HTTP 接口，接入数据库，分层与认证（S3） |
| [第6章](chapters/chapter06/chapter06.md) | 智慧水利三维场景构建 | 坝体几何体与28个测点绑定（S4） |
| [第7章](chapters/chapter07/chapter07.md) | 三维场景的观测数据展示 | 观测曲线与三维测点联动（S5） |
| [第8章](chapters/chapter08/chapter08.md) | 智慧水利平台典型应用 | 质量检查、预警定级与工单处置（S6） |
| [第9章](chapters/chapter09/chapter09.md) | 结语 | 回顾与后续学习 |
| 附录 | [A 习题参考答案](appendix/answers.md) · [B 开发环境与语言衔接预备](appendix/prep.md) · [C 拓展专题](appendix/extended.md) | 没学过 Java/JavaScript 的读者先读附录B |

案例参数（坝高、特征水位、测点编码、预警等级）和接口契约以第8章8.1节的两张表为唯一来源，其他章节引用它们。

## 配套工程

仓库地址：<https://github.com/hjunqq/textbook>

```bash
git clone https://github.com/hjunqq/textbook.git
cd textbook/companion/water-platform-demo
```

- `STAGES.md`：S0—S6 各阶段的入口文件、运行命令、验收和故障练习；
- `MAPPING.md`：仓库文件与书中章节、清单的对应关系，以及工程版本 v0—v5 与阶段 S0—S6 的对应；
- `teaching-api/`：零依赖的教学接口，只需 Node.js 即可启动，前端各阶段不必先装 Java 和数据库；
- `companion/datasets/`：脚本生成的28测点示例数据集，不是真实工程数据。

阶段页提供的是可运行的教学切片；详情路由、GLTF 模型与 GIS 集成等任务由读者在骨架上完成，二者的界线见 `STAGES.md`。

## 关于本网站

网站正文由 `output/` 下的 LaTeX 书稿经 `tools/tex2site` 转换生成，与 PDF 书稿同源；请勿直接修改 `docs/chapters/` 和 `docs/appendix/`。本页（`docs/index.md`）为手工维护。本地预览：

```bash
uv sync
uv run mkdocs serve    # 浏览器打开 http://localhost:8000
```

发现错误或有改进建议，请在仓库提交 Issue。

## 版权与许可

- 配套代码与示例数据集（`companion/`）：MIT License；
- 教材正文与插图（`docs/`、`output/`）：版权归编写组所有，网站仅供在线学习浏览，转载、印刷或商业使用须事先取得书面授权；
- 第三方素材：纸质版第8章8.5节的51WIM产品截图经北京五一视界数字孪生科技股份有限公司书面授权，仅限纸质/PDF版刊出，不随本仓库分发，也不适用 MIT 协议；在线版对应插图为编写组重绘的教学示意图；
- 标注“AI生成教学渲染”的插图为生成图像，不是现场照片或测绘成果；
- 案例水库及其数据均为教学虚构，不代表任何真实工程。
