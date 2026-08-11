# tex2site — LaTeX 正文生成在线站点

**唯一事实来源是 `output/` 下的 LaTeX 书稿**;`docs/` 中的正文
(`前言.md`、`chapters/chapterXX/chapterXX.md`、`appendix/answers.md`、
`references.md` 及各章 `images/*.svg`)全部由本目录脚本生成,
**禁止手工编辑生成物**——改动书稿后重新生成即可。
`docs/index.md`、`docs/assets/`、`docs/javascripts/`、`docs/stylesheets/` 为手工维护文件,不在生成范围内。

## 生成步骤

```bash
# 0) 先完整编译书稿,使 output/main.aux 与正文一致(编号来源)
python tools/check_textbook.py --build

# 1) 转换正文并生成 TikZ 片段
python3 tools/tex2site/convert.py

# 2) 编译 TikZ -> SVG(需 xelatex、pdftocairo、Noto CJK 字体;WSL/Linux 下运行)
bash tools/tex2site/build-tikz.sh

# 3) 再跑一次转换,把 SVG 分发进 docs/,并本地严格校验
python3 tools/tex2site/convert.py
mkdocs build --strict -f mkdocs-ci.yml
```

## 约定

- 交叉引用编号取自 `output/main.aux`,因此第 0 步必须先编译书稿;
- 案例参数宏(`output/case-params.tex`)在转换时展开为数值;
- 第8章6幅51WIM授权截图仅限纸质版:线上自动替换为 `webfigs/` 中的重绘示意图,
  授权 jpg 不得进入 `docs/`;
- 参考文献按全书首次引用顺序编号,生成 `docs/references.md`;
- `mkdocs-ci.yml` 是 CI 严格构建配置(不含 PDF/打印插件),与 `mkdocs.yml` 同步维护。
