#!/bin/bash
# 智慧水利教材转换器 - 改进版构建脚本 (Linux/macOS)

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 设置项目路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
CONVERTER_SCRIPT="$PROJECT_ROOT/tools/improved_main_converter.py"

echo "==============================================="
echo "   智慧水利教材转换器 - 改进版构建脚本"
echo "   Improved Textbook Converter Build Script"
echo "==============================================="
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装或不在 PATH 中${NC}"
    exit 1
fi

# 检查转换器脚本
if [ ! -f "$CONVERTER_SCRIPT" ]; then
    echo -e "${RED}❌ 转换器脚本不存在: $CONVERTER_SCRIPT${NC}"
    exit 1
fi

show_menu() {
    echo "请选择操作:"
    echo
    echo "[1] 完整转换流程 (MD → LaTeX → PDF)"
    echo "[2] 仅转换 Markdown 到 LaTeX"
    echo "[3] 仅构建 PDF (需要先转换)"
    echo "[4] 清理构建文件"
    echo "[5] 查看构建日志"
    echo "[0] 退出"
    echo
}

full_build() {
    echo
    echo -e "${BLUE}🚀 执行完整转换流程...${NC}"
    echo
    echo "步骤 1: 转换 Markdown 到 LaTeX"
    echo "步骤 2: 处理图片文件"
    echo "步骤 3: 构建 PDF 文档"
    echo
    python3 "$CONVERTER_SCRIPT" --project-root "$PROJECT_ROOT"
}

convert_only() {
    echo
    echo -e "${BLUE}🔄 仅转换 Markdown 到 LaTeX...${NC}"
    echo
    echo "正在转换章节文件..."
    echo "- 智能处理章节顺序 (sections 在章节最后)"
    echo "- 保持现有中文标题格式"
    echo "- 自动移除重复的\"本章小节\"部分"
    echo "- 统一处理图片路径"
    echo
    python3 "$CONVERTER_SCRIPT" --project-root "$PROJECT_ROOT" --convert-only
}

build_only() {
    echo
    echo -e "${BLUE}🔨 仅构建 PDF 文档...${NC}"
    echo
    echo "正在使用 XeLaTeX 构建 PDF..."
    echo
    python3 "$CONVERTER_SCRIPT" --project-root "$PROJECT_ROOT" --build-only
}

clean_build() {
    echo
    echo -e "${YELLOW}🧹 清理构建文件...${NC}"
    echo
    
LATEX_DIR="$PROJECT_ROOT/output"
    if [ -d "$LATEX_DIR" ]; then
        cd "$LATEX_DIR"
        echo "清理 LaTeX 临时文件..."
        rm -f *.aux *.log *.out *.toc *.fdb_latexmk *.fls *.synctex.gz
    fi
    
    echo "清理转换日志..."
    rm -f "$PROJECT_ROOT/conversion.log"
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

view_log() {
    echo
    echo -e "${BLUE}📄 查看构建日志...${NC}"
    echo
    
    LOG_FILE="$PROJECT_ROOT/conversion.log"
    if [ -f "$LOG_FILE" ]; then
        echo "最后 20 行日志内容:"
        echo "----------------------------------------"
        tail -n 20 "$LOG_FILE"
        echo "----------------------------------------"
        echo
        echo "完整日志文件位置: $LOG_FILE"
    else
        echo -e "${YELLOW}日志文件不存在: $LOG_FILE${NC}"
        echo "请先运行一次转换"
    fi
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (0-5): " choice
    
    case $choice in
        1)
            full_build
            ;;
        2)
            convert_only
            ;;
        3)
            build_only
            ;;
        4)
            clean_build
            ;;
        5)
            view_log
            ;;
        0)
            echo
            echo -e "${GREEN}👋 感谢使用智慧水利教材转换器！${NC}"
            echo
            PDF_FILE="$PROJECT_ROOT/output/main.pdf"
            if [ -f "$PDF_FILE" ]; then
                PDF_SIZE=$(stat -f%z "$PDF_FILE" 2>/dev/null || stat -c%s "$PDF_FILE" 2>/dev/null)
                echo -e "${GREEN}✅ 当前 PDF 文件: $PDF_FILE${NC}"
                if [ -n "$PDF_SIZE" ]; then
                    echo "   文件大小: $PDF_SIZE bytes"
                fi
            fi
            echo
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择${NC}"
            ;;
    esac
    
    echo
    echo "==============================================="
    echo
    read -p "按回车键继续，或输入 'q' 退出: " continue_choice
    if [[ $continue_choice == "q" || $continue_choice == "Q" ]]; then
        echo
        echo -e "${GREEN}👋 感谢使用智慧水利教材转换器！${NC}"
        break
    fi
done
