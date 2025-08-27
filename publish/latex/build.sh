#!/bin/bash

# ========================================
# LaTeX 编译脚本 - Linux/macOS版本
# 智慧水利平台架构与开发教材
# ========================================

set -e  # 出错时退出

echo "========================================="
echo "开始编译智慧水利平台架构与开发教材"
echo "========================================="

# 检查必要的工具
command -v xelatex >/dev/null 2>&1 || { echo "错误: 需要安装XeLaTeX" >&2; exit 1; }

# 设置目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 创建输出目录
mkdir -p output
mkdir -p build/logs

# 编译函数
compile_tex() {
    local filename=$1
    local max_runs=$2
    
    echo "编译 $filename..."
    
    for i in $(seq 1 $max_runs); do
        echo "第 $i 次编译..."
        if ! xelatex -interaction=nonstopmode -output-directory=output "$filename" > "build/logs/compile_$i.log" 2>&1; then
            echo "错误: 第 $i 次编译失败，查看日志: build/logs/compile_$i.log"
            return 1
        fi
    done
    
    echo "$filename 编译完成"
}

# 清理旧文件
echo "清理旧的编译文件..."
rm -f output/*.aux output/*.log output/*.toc output/*.out output/*.fdb_latexmk output/*.fls
rm -f output/*.lot output/*.lof output/*.synctex.gz

# 编译主文档 (需要多次编译以正确生成目录和交叉引用)
compile_tex "main.tex" 3

# 检查PDF是否生成成功
if [ -f "output/main.pdf" ]; then
    echo "========================================="
    echo "编译成功! PDF文件位于: output/main.pdf"
    echo "========================================="
    
    # 显示文件大小
    ls -lh output/main.pdf
    
    # 可选: 自动打开PDF (取消注释下行)
    # xdg-open output/main.pdf 2>/dev/null || open output/main.pdf 2>/dev/null || true
else
    echo "编译失败: 未能生成PDF文件"
    echo "请检查编译日志: build/logs/"
    exit 1
fi

echo "编译流程完成!"