#!/usr/bin/env python3
"""
彻底清理所有LaTeX命令
"""

import re
from pathlib import Path

def completely_remove_latex_commands(content):
    """彻底移除所有LaTeX命令"""
    
    print("开始彻底清理LaTeX命令...")
    
    # 1. 移除所有$包围的数学公式
    content = re.sub(r'\$[^$]*\$', '[数学公式]', content)
    content = re.sub(r'\$\$[^$]*\$\$', '[数学公式块]', content)
    
    # 2. 移除所有裸露的LaTeX数学命令
    latex_commands = [
        r'\\frac\{[^}]*\}\{[^}]*\}',  # \frac{}{} 
        r'\\sqrt\{[^}]*\}',           # \sqrt{}
        r'\\partial',                 # \partial
        r'\\sum\\limits_[^}]*\{[^}]*\}',  # \sum\limits_{}^{}
        r'\\int\\limits_[^}]*\{[^}]*\}',  # \int\limits_{}^{}
        r'\\left\([^)]*\)',           # \left() \right()
        r'\\right\([^)]*\)',          
        r'\\left\{[^}]*\}',           # \left{} \right{}
        r'\\right\{[^}]*\}',
        r'\\cdots',                   # \cdots
        r'\\pi',                      # \pi
        r'\\exp',                     # \exp
        r'\\ln',                      # \ln
        r'\\delta',                   # \delta
        r'\\alpha',                   # \alpha
        r'\\sigma',                   # \sigma
        r'\\Omega',                   # \Omega
    ]
    
    for cmd in latex_commands:
        content = re.sub(cmd, '[LaTeX命令]', content, flags=re.IGNORECASE)
    
    # 3. 移除剩余的反斜杠转义字符
    content = re.sub(r'\\[a-zA-Z]+', '[LaTeX]', content)
    
    # 4. 移除多余的大括号
    content = re.sub(r'\{+[^}]*\}+', '[表达式]', content)
    
    print("LaTeX命令清理完成")
    return content

def create_completely_clean_version():
    """创建完全无LaTeX版本"""
    print("创建完全无LaTeX版本...")
    
    with open('output/math_fixed_textbook.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 彻底清理
    clean_content = completely_remove_latex_commands(content)
    
    with open('output/latex_free_textbook.md', 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print("完全无LaTeX版本已创建: output/latex_free_textbook.md")

if __name__ == "__main__":
    create_completely_clean_version()