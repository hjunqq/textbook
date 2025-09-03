#!/usr/bin/env python3
"""
正确的数学公式修复器
现在我们知道问题所在，可以正确地修复数学公式
"""

import re
from pathlib import Path

def fix_math_properly(content):
    """正确地修复数学公式"""
    
    # 找到所有现有的数学公式（$包围的）
    math_formulas = re.findall(r'\$([^$]+)\$', content)
    print(f"找到 {len(math_formulas)} 个数学公式")
    
    # 修复每个数学公式内的常见问题
    def fix_single_math(match):
        formula = match.group(1)
        # 修复空格问题
        formula = re.sub(r'\\sqrt\s+\{', r'\\sqrt{', formula)
        formula = re.sub(r'\\frac\s+\{', r'\\frac{', formula)
        # 确保下标用花括号
        formula = re.sub(r'([A-Za-z])_([A-Za-z0-9]+)', r'\1_{\2}', formula)
        return f'${formula}$'
    
    # 应用修复
    content = re.sub(r'\$([^$]+)\$', fix_single_math, content)
    
    # 查找裸露的LaTeX命令并包装
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 如果包含裸露的LaTeX命令，包装为数学公式
        if (re.search(r'[^$]\\(frac|sqrt|partial|sum|int)', line) and 
            not line.strip().startswith('```') and
            '=' in line):
            # 这行包含裸露的数学命令
            print(f"修复裸露命令行: {line[:50]}...")
            # 简单包装整行为数学公式
            fixed_line = f'$${line.strip()}$$'
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def create_math_fixed_version():
    """创建数学修复版本"""
    print("创建正确的数学公式修复版本...")
    
    with open('output/math_fixed_textbook.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 应用正确的数学修复
    fixed_content = fix_math_properly(content)
    
    with open('output/properly_fixed_textbook.md', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("正确修复版本已创建: output/properly_fixed_textbook.md")

if __name__ == "__main__":
    create_math_fixed_version()