# 《智慧水利平台架构与开发》教材仓库

面向水利类专业大三学生的教材书稿、在线版与配套代码。

## 目录

| 位置 | 内容 |
|---|---|
| `output/` | **书稿唯一来源**（LaTeX）：`main.tex`、`chapters/`、`appendix/`、`case-params.tex`、`references.bib` |
| `output/online/online.tex` | 线上拓展专题：从正文迁出的拓展层内容，只生成网站页面，不进入印刷版 |
| `docs/` | 在线版（MkDocs），由 `tools/tex2site/` 从 LaTeX 生成，**不要手改** |
| `companion/water-platform-demo/` | 配套工程：Vue 前端、Spring Boot 后端、教学接口、数据集与 docker compose |
| `tools/` | 门禁与检查脚本（`check_textbook.py`、`check_listings.py`、`audit_learning_path.py`）、tex2site |
| `课件_节级*/`、`题库导入*/`、`课堂在线/` | 课程平台使用的节级课件、题库与在线课堂材料 |
| `process/` | 历轮审查报告、修改方案、修改记录、需求与大纲等过程文件 |
| `archive/` | 早期手稿与已停用的流水线 |

## 常用命令

```bash
python tools/check_textbook.py            # 门禁（不得倒退）
python tools/check_textbook.py --build    # 含完整编译：xelatex → biber → xelatex×2
python tools/check_listings.py            # 书中清单与配套代码逐字核对
python tools/tex2site/convert.py          # 由 LaTeX 生成网站（先完整编译得到 main.aux）
```

网站生成的完整步骤见 `tools/tex2site/README.md`。在本仓库工作的自动化代理须先读 `AGENTS.md`；改变项目方向的决定记录在 `DECISIONS.md`。
