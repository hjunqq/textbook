#!/bin/bash
# 编译 convert.py 产出的 TikZ 片段为 SVG(需 xelatex + pdftocairo + Noto CJK 字体)。
# 用法: 先 python3 convert.py,再 bash build-tikz.sh,最后再跑一次 python3 convert.py 分发SVG。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="${TEX2SITE_REPO:-$HERE/../..}"
BUILD="${TEX2SITE_BUILD:-$REPO/temp/tex2site-build}"
cd "$BUILD/tikz" || { echo "先运行 convert.py 生成片段"; exit 1; }
cp "$HERE/preamble.tex" .
cp "$REPO/output/tikz-diagrams.tex" .
fail=0
for f in chapter*_fig_*.tex; do
  case "$f" in build_*) continue;; esac
  base="${f%.tex}"
  [ -f "$base.svg" ] && continue
  cat preamble.tex "$f" > "build_$f"
  echo '\end{document}' >> "build_$f"
  if timeout 90 xelatex -interaction=nonstopmode -jobname="$base" "build_$f" >/dev/null 2>&1 \
     && [ -f "$base.pdf" ] && pdftocairo -svg "$base.pdf" "$base.svg"; then
    echo "OK   $base"
  else
    echo "FAIL $base"; fail=$((fail+1))
  fi
done
exit $fail
