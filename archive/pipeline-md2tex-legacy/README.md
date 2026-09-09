# 已停用：MD→LaTeX 转换流水线（第七轮之前）

**这里的东西不要运行。** 归档于 2026-09-09。

## 为什么停用

第七轮迁到 tex2site 之后，数据流向反过来了：

| | 之前（本目录这套） | 现在 |
|---|---|---|
| 事实来源 | `docs/` 下的 Markdown | **`output/` 下的 LaTeX 书稿** |
| 生成物 | `output/chapters/*.tex`、`output/main.tex` | `docs/`（站点） |
| 工具 | `improved_main_converter.py` | `tools/tex2site/convert.py` |

问题在于本目录的 `improved_main_converter.py`（以及 `improved_build.bat` / `improved_build.sh`）
仍按旧方向工作：**读 `docs/` 的 Markdown，覆盖写 `output/chapters/*.tex` 与 `output/main.tex`**。
而 `docs/` 现在是 tex2site 的生成物——现在跑它一次，就会用生成物反向覆盖掉书稿源文件，
把正文改回若干轮之前的状态。这是把它移出 `tools/` 的唯一原因：留在现役工具目录里迟早会被误跑。

## 当前正确的流程

见 `tools/tex2site/README.md`：

```bash
python tools/check_textbook.py --build     # 先编译书稿，交叉引用编号来自 main.aux
python tools/tex2site/convert.py           # tex → docs/
bash tools/tex2site/build-tikz.sh          # TikZ → SVG
python tools/tex2site/convert.py           # 分发 SVG
mkdocs build --strict -f mkdocs-ci.yml
```

门禁：`tools/check_textbook.py`（字数、引用、编译、软指标）与
`tools/check_listings.py`（书中清单与 companion 代码是否一致）。

## 目录内容

| 文件 | 原位置 | 作用 |
|---|---|---|
| `tools/improved_main_converter.py` | `tools/` | 主转换器，md → tex |
| `tools/content_processors.py` | `tools/` | 正文内容处理 |
| `tools/converter_config.py` | `tools/` | 路径与字体配置 |
| `tools/latex_templates.py` | `tools/` | LaTeX 模板片段 |
| `tools/latex_validator.py` | `tools/` | 转换后校验，仅被主转换器调用 |
| `tools/md2latex.py` | `tools/` | 命令行入口 |
| `tools/convert_preface_only.py` | `tools/` | 只转前言 |
| `tools/README.md` | `tools/` | 这套流水线的原始说明 |
| `improved_build.bat` / `.sh` | 仓库根 | 调用主转换器的构建脚本 |

配套的中间产物 `output/chapters/*.md`（10 个文件、2.1 MB）已于同日删除，
内容可从 git 历史取回；按小节拆分的 L2 手稿另见 `archive/docs-legacy/`。

`pandoc/` 目录及其中的 `build.bat` **未动**——AGENTS.md 第四节明确要求保留（合法 GBK 编码）。
