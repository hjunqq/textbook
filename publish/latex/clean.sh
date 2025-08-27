#!/bin/bash

# ========================================
# 清理LaTeX编译产生的临时文件
# ========================================

echo "清理LaTeX临时文件..."

# 设置目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 清理输出目录中的临时文件
if [ -d "output" ]; then
    echo "清理output目录..."
    rm -f output/*.aux
    rm -f output/*.log
    rm -f output/*.toc
    rm -f output/*.out
    rm -f output/*.fdb_latexmk
    rm -f output/*.fls
    rm -f output/*.lot
    rm -f output/*.lof
    rm -f output/*.synctex.gz
    rm -f output/*.nav
    rm -f output/*.snm
    rm -f output/*.vrb
    rm -f output/*.bbl
    rm -f output/*.blg
    rm -f output/*.idx
    rm -f output/*.ilg
    rm -f output/*.ind
fi

# 清理编译日志
if [ -d "build/logs" ]; then
    echo "清理编译日志..."
    rm -f build/logs/*.log
fi

# 清理根目录下可能的临时文件
rm -f *.aux *.log *.toc *.out *.fdb_latexmk *.fls *.lot *.lof *.synctex.gz

echo "清理完成!"