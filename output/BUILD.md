# LaTeX 编译指南

## 编译环境要求

- **TeX 发行版**：TeX Live 2024+ 或 MiKTeX（需包含 ctex 宏集）
- **编译引擎**：XeLaTeX
- **操作系统**：Windows / macOS / Linux 均可

### 必需的 TeX 宏包

以下宏包需要安装（TeX Live Full 版本已全部包含）：

```
ctex, fontspec, geometry, setspace, microtype,
longtable, booktabs, array, graphicx, ulem,
amsmath, amsfonts, amssymb, float, subcaption,
algorithm, algpseudocode, xcolor, listings,
tcolorbox, titlesec, tocloft, enumitem, caption,
fancyhdr, xurl, hyperref, etoolbox, calc
```

### 字体要求

文档使用以下字体（按优先级自动回退）：

| 类型 | 首选 | 备选1 | 备选2 |
|------|------|-------|-------|
| 西文正文 | TeX Gyre Pagella | — | — |
| 西文无衬线 | TeX Gyre Heros | — | — |
| 西文等宽 | Inconsolata | TeX Gyre Cursor | — |
| 中文正文 | Source Han Serif SC | Noto Serif CJK SC | Microsoft YaHei |

在 Windows 上安装了 Office 的系统通常有 Microsoft YaHei；如需更好的排版效果，建议安装思源宋体（Source Han Serif SC）。

## 编译步骤

```bash
cd output/

# 方法一：直接编译（推荐）
xelatex main.tex
biber main
xelatex main.tex
xelatex main.tex

# 方法二：使用 latexmk 自动处理
latexmk -xelatex -usebiber main.tex
```

当前文档使用 `biblatex + biber` 管理参考文献，因此正式编译链必须是 `XeLaTeX -> Biber -> XeLaTeX -> XeLaTeX`。最后两遍 XeLaTeX 用于稳定目录、交叉引用和参考文献页码。使用 `latexmk` 时也需要显式启用 `biber`。

## 参考文献排查

- 若文末“参考文献”为空，先检查 `main.log` 中是否出现 `Please (re)run Biber`。
- 再检查各章 `\cite{}` 的 key 是否存在于 `references.bib`。
- 若只改了正文引用或 `.bib` 文件，也应重新执行完整四步编译链。

## 目录结构

```
output/
├── main.tex              # 主文件（入口）
├── chapters/
│   ├── preface.tex       # 前言
│   ├── chapter01.tex     # 第一章：智慧水利概述
│   ├── chapter02.tex     # 第二章：软件工程基础
│   ├── chapter03.tex     # 第三章：现代开发方法
│   ├── chapter04.tex     # 第四章：前端开发技术
│   ├── chapter05.tex     # 第五章：后端开发技术
│   ├── chapter06.tex     # 第六章：三维场景构建
│   ├── chapter07.tex     # 第七章：监测数据展示
│   ├── chapter08.tex     # 第八章：典型应用
│   └── chapter09.tex     # 第九章：结语
└── images/               # 图片资源
    ├── chapter02/
    └── chapter06/
```

## 常见问题

### Q: 编译报错 "Font xxx not found"
A: 安装对应字体，或修改 `main.tex` 中的字体配置。文档已内置字体回退链，大多数系统可直接编译。

### Q: 图片找不到
A: `main.tex` 中已配置 `\graphicspath`，确保 `images/` 目录在 `output/` 下。如果图片在其他位置，可在 `\graphicspath` 中添加路径。

### Q: 中文显示为方框
A: 确认系统安装了中文字体（至少 Microsoft YaHei），并使用 XeLaTeX 而非 pdfLaTeX 编译。

## 静态验证

项目根目录提供了 `validate_latex.py` 验证脚本，可在不编译的情况下检查常见结构错误：

```bash
python3 validate_latex.py
```

检查项包括：花括号匹配、环境嵌套、图片引用、代码块完整性、章节结构等。
