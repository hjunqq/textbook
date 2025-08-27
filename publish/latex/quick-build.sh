#!/bin/bash

# ========================================
# LaTeX 快速编译脚本
# 仅编译一次，用于快速预览
# ========================================

set -e

echo "快速编译模式..."

# 设置目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 创建输出目录
mkdir -p output

# 单次编译
echo "编译中..."
if xelatex -interaction=nonstopmode -output-directory=output main.tex; then
    echo "快速编译完成! PDF文件: output/main.pdf"
    ls -lh output/main.pdf
else
    echo "编译失败"
    exit 1
fi