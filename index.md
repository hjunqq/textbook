# 《智慧水利平台架构与开发》教材仓库

面向水利类专业本科三年级的教材及其配套工程。读者入口是在线站点首页 [`docs/index.md`](docs/index.md)；本页只说明仓库里东西放在哪里。

| 位置 | 内容 |
|---|---|
| `output/` | LaTeX 书稿（正文唯一来源）：`chapters/` 前言与第1—9章，`appendix/` 附录A—C，`case-params.tex` 案例参数宏；编译方法见 `output/BUILD.md` |
| `docs/` | 在线站点。`chapters/`、`appendix/` 由 `tools/tex2site` 从书稿生成，不手改；`index.md` 手工维护 |
| `companion/water-platform-demo/` | 配套工程与 S0—S6 阶段包；从 `STAGES.md`、`MAPPING.md` 读起 |
| `companion/datasets/` | 脚本生成的28测点示例数据集 |
| `tools/` | `check_textbook.py`（书稿检查）、`check_listings.py`（书中清单与配套文件一致性）、`tex2site/`（书稿转站点） |
| `AGENTS.md`、`DECISIONS.md` | 修订规则与方向性决策 |
| `revision/r11/` | 第十一轮教学性重编的计划与进度 |
| `archive/` 及根目录各轮“修改记录/审查报告” | 历史材料，不代表当前书稿状态 |

全书九章：智慧水利概述与平台架构基础；软件工程基础与需求分析；软件架构设计与模块划分；前端开发技术；后端开发技术；智慧水利三维场景构建；三维场景的观测数据展示；智慧水利平台典型应用；结语。

许可：`companion/` 为 MIT；正文与插图版权归编写组；第三方素材授权范围见 `docs/index.md`。
