#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF效果查看工具
用于快速打开生成的教材PDF并提供效果总结
"""

import os
import subprocess
import sys
from pathlib import Path

def open_pdf():
    """打开生成的PDF文件"""
    script_dir = Path(__file__).parent
    pdf_path = script_dir.parent.parent / "publish" / "latex_output" / "教材.pdf"
    
    if not pdf_path.exists():
        print("❌ PDF文件不存在，请先运行转换器生成PDF")
        return False
    
    print("📖 正在打开PDF文件...")
    try:
        if sys.platform.startswith('win'):
            os.startfile(str(pdf_path))
        elif sys.platform.startswith('darwin'):  # macOS
            subprocess.run(['open', str(pdf_path)])
        else:  # Linux
            subprocess.run(['xdg-open', str(pdf_path)])
        
        print(f"✅ PDF已打开: {pdf_path}")
        return True
    except Exception as e:
        print(f"❌ 无法打开PDF: {e}")
        return False

def show_improvements():
    """显示本次代码块改进的效果说明"""
    print("🎯 代码块样式改进效果:")
    print("=" * 50)
    print("📝 字体大小: small → scriptsize (更小)")
    print("🎨 背景颜色: 灰色10% → 灰色8% (更淡)")
    print("📏 边距优化: 增加了精确的边距控制")
    print("🔢 行号样式: 改为淡灰色，更美观")
    print("✨ 语法高亮: 蓝色关键字，红色字符串，灰色注释")
    print("📐 间距优化: 减少了上下间距，更紧凑")
    print("🖼️ 边框改进: 更细致的边框和内边距设置")
    print("=" * 50)
    print("💡 建议查看第4章开始的代码块，对比之前的效果")

def main():
    print("智慧水利教材 - PDF效果查看工具")
    print("=" * 40)
    
    # 显示改进说明
    show_improvements()
    print()
    
    # 打开PDF
    if open_pdf():
        print("\n🎉 PDF已成功打开！")
        print("💭 请重点查看代码块的显示效果:")
        print("   • 字号是否更合适")
        print("   • 行间距是否更紧凑")
        print("   • 语法高亮是否清晰")
        print("   • 整体布局是否美观")
    else:
        print("\n❌ 无法打开PDF文件")

if __name__ == "__main__":
    main()
