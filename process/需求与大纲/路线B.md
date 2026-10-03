路线 B（高保真 / 推荐）：Pandoc 预处理 → 生成 LaTeX → PDF

适用：需要拿到干净的 .tex，用 XeLaTeX（中文）与学术级排版；解决 Pandoc 报错（admonition、tabs、细节折叠等）。

思路：

先把 MkDocs/Material 特有语法（如 !!! note 等 admonition）“规整化”为 Pandoc 更稳吃的结构；

用 Pandoc 的 defaults + 过滤器 + XeLaTeX 字体 统一出书。

你仓库新增这些文件（建议建一个 pandoc/ 目录）
1) pandoc/defaults-pdf.yaml
from: markdown+tex_math_dollars+pipe_tables+table_captions+footnotes+smart+fenced_divs+link_attributes+raw_tex+implicit_figures
to: pdf
pdf-engine: xelatex
output-file: book.pdf
filters:
  - pandoc-crossref
  - pandoc/filters/admonitions.py
citeproc: true
resource-path: [., docs]
metadata:
  title: "智慧水利平台架构与开发"
  lang: zh-CN
  toc: true
  toc-depth: 3
  link-citations: true
  geometry: [a4paper, margin=25mm]
  header-includes: |
    \usepackage{xeCJK}
    \setCJKmainfont{Source Han Serif SC}
    \usepackage{booktabs,longtable,tcolorbox,caption,hyperref}
variables:
  documentclass: scrbook
  fontsize: 12pt
  mainfont: TeX Gyre Termes
  monofont: Fira Code
  colorlinks: true
  linkcolor: blue


交叉引用用 pandoc-crossref，图表公式的 @fig:... 等自动编号最省心。
pandoc.org
GitHub

2) pandoc/filters/admonitions.py（把 !!! note 等换成 LaTeX tcolorbox）
# -*- coding: utf-8 -*-
import panflute as pf

MAP = {
    'note': ('Note', 'blue!5'),
    'tip': ('Tip', 'green!5'),
    'warning': ('Warning', 'yellow!10'),
    'danger': ('Danger', 'red!5'),
}

def action(elem, doc):
    # 识别经预处理转成 fenced_divs 的块：::: admonition note
    if isinstance(elem, pf.Div) and 'admonition' in elem.classes:
        kind = next((c for c in elem.classes if c in MAP), 'note')
        title, color = MAP.get(kind, ('Note', 'blue!5'))
        before = pf.RawBlock(
            rf'\begin{{tcolorbox}}[colback={color},title={{{title}}}]',
            format='latex'
        )
        after = pf.RawBlock(r'\end{tcolorbox}', format='latex')
        return [before] + list(elem.content) + [after]

def main(doc=None):
    return pf.run_filter(action, doc=doc)

if __name__ == "__main__":
    main()


过滤器基于 panflute（写 Pandoc 过滤器的轻量方式）。
Sergio Correia
Panflute

3) pandoc/tools/nav_to_list.py（把 mkdocs.yml 的 nav 展开成文件清单）
#!/usr/bin/env python3
import sys, yaml, os

def iter_nav(nav):
    if isinstance(nav, list):
        for item in nav:
            yield from iter_nav(item)
    elif isinstance(nav, dict):
        for _, v in nav.items():
            if isinstance(v, str) and v.lower().endswith(('.md','.markdown','.mdx')):
                yield v
            else:
                yield from iter_nav(v)

def main():
    mk = 'mkdocs.yml'
    docs_dir = 'docs'
    if not os.path.exists(mk):
        print('mkdocs.yml not found', file=sys.stderr); sys.exit(1)
    data = yaml.safe_load(open(mk,'r',encoding='utf-8'))
    docs_dir = data.get('docs_dir', docs_dir)
    nav = data.get('nav', [])
    files = list(iter_nav(nav))
    # 兼容未显式 nav 的项目：按目录遍历
    if not files:
        for root, _, fnames in os.walk(docs_dir):
            for f in sorted(fnames):
                if f.lower().endswith(('.md','.markdown','.mdx')):
                    files.append(os.path.relpath(os.path.join(root,f), start='.'))
    with open('pandoc/files.txt','w',encoding='utf-8') as f:
        for p in files:
            # mkdocs 的路径相对 docs_dir；Pandoc 直接读相对路径即可
            f.write(f"{p}\n")

if __name__ == '__main__':
    main()

4) pandoc/tools/preprocess_admonition.py（把 !!! note → ::: admonition note）

Pandoc 不原生支持 !!! note；先用一个极小的预处理把它们改成 fenced div（Pandoc 支持），过滤器就能识别了。

#!/usr/bin/env python3
# 仅处理最常见的 "!!! kind" 语法；更复杂的标题可自行扩展
import re, sys

def convert(text):
    # 匹配开头的 !!! kind
    pat = re.compile(r'(?m)^\s*!!!\s+(\w+)\s*(?:\"([^\"]+)\")?\s*$')
    lines = text.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        m = pat.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        kind, title = m.group(1).lower(), m.group(2)
        out.append(f"::: admonition {kind}")
        if title: out.append(f"**{title}**")
        i += 1
        # 收集缩进内容（直到遇到空行+非缩进或文件结尾）
        while i < n and (lines[i].startswith('    ') or lines[i].strip()=='' ):
            out.append(lines[i][4:] if lines[i].startswith('    ') else '')
            i += 1
        out.append(":::")
    return "\n".join(out)

if __name__ == '__main__':
    txt = sys.stdin.read()
    sys.stdout.write(convert(txt))

5) pandoc/build.sh（一把梭脚本）
#!/usr/bin/env bash
set -euo pipefail

# 1. 生成文件顺序
python3 pandoc/tools/nav_to_list.py

# 2. 预处理 MkDocs Admonition 语法
mkdir -p pandoc/tmp
rm -rf pandoc/tmp/*
while read -r f; do
  mkdir -p "pandoc/tmp/$(dirname "$f")"
  python3 pandoc/tools/preprocess_admonition.py < "$f" > "pandoc/tmp/$f"
done < pandoc/files.txt

# 3. 调 Pandoc（保留 .tex 便于后期微调）
pandoc $(cat pandoc/files.txt | sed 's#^#pandoc/tmp/#') \
  --defaults pandoc/defaults-pdf.yaml \
  -o pandoc/book.pdf
pandoc $(cat pandoc/files.txt | sed 's#^#pandoc/tmp/#') \
  --defaults pandoc/defaults-pdf.yaml \
  -o pandoc/book.tex
echo "Done: pandoc/book.pdf  &  pandoc/book.tex"

6) 依赖
pip install panflute pyyaml
# 建议使用容器自带 LaTeX：
#   docker run -v "$PWD":/data --rm pandoc/latex:latest sh -lc \
#   "apk add --no-cache font-noto-cjk && cd /data && ./pandoc/build.sh"


pandoc/latex 镜像内置 LaTeX 与 Pandoc；你只需安装 panflute/pyyaml 即可。交叉引用由 pandoc-crossref 负责（如需单独安装或更换版本，见其文档）。
GitHub
Lierdakil

7) CI（可选，.github/workflows/pandoc.yml）
name: Pandoc PDF/LaTeX
on: [workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker://pandoc/latex:latest
        with: {}
      - name: Install deps & build
        run: |
          apt-get update && apt-get install -y fonts-noto-cjk python3-pip
          pip3 install panflute pyyaml
          bash pandoc/build.sh
      - uses: actions/upload-artifact@v4
        with:
          name: pandoc-out
          path: pandoc/book.pdf
      - uses: actions/upload-artifact@v4
        with:
          name: latex-source
          path: pandoc/book.tex