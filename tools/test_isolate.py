#!/usr/bin/env python3
"""
第一性原理测试：逐步隔离问题
"""

import re
from pathlib import Path

def create_no_math_version():
    """创建无数学公式版本"""
    print("创建无数学公式版本...")
    
    # 读取原始合并文件
    with open('output/math_fixed_textbook.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除所有数学公式，用文字说明替代
    content = re.sub(r'\$[^$]*\$', '[数学公式]', content)
    content = re.sub(r'\$\$[^$]*\$\$', '[数学公式块]', content)
    
    # 保存无数学版本
    with open('output/no_math_textbook.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("无数学公式版本已创建")

def create_ultra_clean_version():
    """创建超级清理版本"""
    print("创建超级清理版本...")
    
    with open('output/math_fixed_textbook.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 彻底重新格式化数学公式
    def clean_math_content(match):
        math_content = match.group(1)
        # 移除多余的大括号和斜体标记
        math_content = re.sub(r'\*([^*]+)\*', r'\1', math_content)
        math_content = re.sub(r'\{+([^{}]+)\}+', r'{\1}', math_content)
        return f'${math_content}$'
    
    # 先替换为临时标记
    content = re.sub(r'\$([^$]+)\$', r'MATHSTART\1MATHEND', content)
    # 再清理并恢复
    content = re.sub(r'MATHSTART([^M]+?)MATHEND', clean_math_content, content)
    
    with open('output/ultra_clean_textbook.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("超级清理版本已创建")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "no_math":
            create_no_math_version()
        elif sys.argv[1] == "ultra_clean":
            create_ultra_clean_version()
    else:
        print("请指定参数: no_math 或 ultra_clean")