# MD→LaTeX 转换工具（便携精简版）

面向通用项目的 Markdown → LaTeX/PDF 转换工具，基于 Pandoc + XeLaTeX，并内置中文、代码、图片、告警框等处理。

## 环境依赖
- Python 3.8+
- Pandoc 2.x（命令 `pandoc` 可用）
- LaTeX 发行版（含 XeLaTeX，命令 `xelatex` 可用）
- 建议安装中文字体（或调整 `converter_config.py` 中字体）

## 目录约定
- `docs/前言.md`
- `docs/chapters/chapter01/chapter01.md`（主文件，可选 `section*.md` 小节）
- `docs/chapters/chapter02/...`
- 章节图片：
  - 通用：`docs/chapters/images/...`
  - 每章：`docs/chapters/chapter01/images/...`

输出目录：`output/`

## 快速使用
- 完整转换并编译 PDF（从仓库根目录运行）：
  - `python tools/md2latex.py --project-root . --clean`
- 仅转换为 `.tex`：
  - `python tools/md2latex.py --convert-only`
- 仅编译（使用现有 `output/main.tex`）：
  - `python tools/md2latex.py --build-only`
- 选择章节：
  - `python tools/md2latex.py --chapters 1,2`

说明：
- 可在仓库根或 `tools/` 内运行；`--project-root` 指向包含 `docs/` 的目录。
- 转换日志写入仓库根的 `conversion.log`。

## 主要文件
- `improved_main_converter.py`：核心流程（转换、模板、编译）
- `content_processors.py`：内容处理流水线（标题、数学、图片、代码、告警框等）
- `latex_templates.py`：LaTeX 主模板生成（中文、目录、代码风格等）
- `latex_validator.py`：转换后 LaTeX 语法修复
- `converter_config.py`：基本配置与路径管理
- `md2latex.py`：便捷 CLI 封装入口
- `requirements.txt`：外部依赖说明（仅工具依赖 Pandoc/XeLaTeX）

## 常见问题
- 未找到 Pandoc/XeLaTeX：请先安装并确保在 PATH 中。
- 中文字体缺失：安装相应字体或在模板/配置中切换为系统已有字体。
- 图片不显示：检查图片是否被复制到 `output/images/`，以及 Markdown 中的相对路径是否符合约定。

本工具已精简为可复用形态，可直接拷贝到其他项目的 `tools/` 下继续使用。
