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