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

# 2) 编译 TikZ -> SVG(需 xelatex、pdftocairo、Noto CJK 字体)
bash tools/tex2site/build-tikz.sh

# 3) 再跑一次转换,把 SVG 分发进 docs/,并本地严格校验
python3 tools/tex2site/convert.py
mkdocs build --strict -f mkdocs-ci.yml
```

## Noto CJK 字体的安装(第 2 步的前提)

`preamble.tex` 按字族名请求 `Noto Sans CJK SC` 与 `Noto Sans Mono CJK SC`,
两者都必须能被 xelatex 按**字族名**找到,否则 93 个片段会全部编译失败。

- Linux / WSL:`apt install fonts-noto-cjk texlive-xetex poppler-utils` 即可。
- Windows + TeX Live:把静态 OTF 放进 texmf 字体树再刷新索引——
  这是**唯一可行且不需要管理员权限**的方式:

  ```bash
  # 取 https://github.com/notofonts/noto-cjk/releases 的
  # Sans2.004/08_NotoSansCJKsc.zip 与 13_NotoSansMonoCJKsc.zip,解出 Regular/Bold
  TL=/c/texlive/2026/texmf-dist/fonts/opentype/google/notocjk
  mkdir -p $TL && cp NotoSansCJKsc-{Regular,Bold}.otf NotoSansMonoCJKsc-{Regular,Bold}.otf $TL/
  mktexlsr
  ```

  以下三种办法在 Windows 上**都不管用**,不必再试:用户级字体安装
  (`%LOCALAPPDATA%\Microsoft\Windows\Fonts` + HKCU 注册表)、`OSFONTDIR` 环境变量、
  系统自带的 `NotoSansSC-VF.ttf`(可变字体,xdvipdfmx 生成 PDF 失败)。

- 只新增/改动了少量图时,不必重编 93 张:片段编号未位移的图,
  `docs/` 中的旧 SVG 仍然有效;手工只编需要的那几个片段,
  再跑第 3 步的 `convert.py` 分发即可(它只复制、不删除)。

## 约定

- 交叉引用编号取自 `output/main.aux`,因此第 0 步必须先编译书稿;
- 案例参数宏(`output/case-params.tex`)在转换时展开为数值;
- 第8章6幅51WIM授权截图仅限纸质版:线上自动替换为 `webfigs/` 中的重绘示意图,
  授权 jpg 不得进入 `docs/`;
- 参考文献按全书首次引用顺序编号,生成 `docs/references.md`;
- `mkdocs-ci.yml` 是 CI 严格构建配置(不含 PDF/打印插件),与 `mkdocs.yml` 同步维护。
