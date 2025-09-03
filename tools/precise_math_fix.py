#!/usr/bin/env python3
"""
精确修复数学公式 - 避免重复包装
"""

import re
from pathlib import Path

def fix_math_precisely(content):
    """精确修复数学公式，避免重复包装"""
    
    print("开始精确修复数学公式...")
    
    # 1. 先修复重复包装的问题
    # 找到 $$ \n $$公式内容$$ \n $$ 的模式并修复
    content = re.sub(r'\$\$\s*\n\s*\$\$([^$]+)\$\$\s*\n\s*\$\$', r'$$\1$$', content)
    
    # 2. 修复单个公式内的语法问题
    def fix_single_formula(match):
        formula = match.group(1)
        # 修复常见的语法问题
        formula = re.sub(r'\\sqrt\s+\{', r'\\sqrt{', formula)
        formula = re.sub(r'\\frac\s+\{', r'\\frac{', formula)
        # 确保下标用花括号
        formula = re.sub(r'([A-Za-z])_([A-Za-z0-9]+)', r'\1_{\2}', formula)
        return f'$${formula}$$'
    
    # 应用到块级公式
    content = re.sub(r'\$\$([^$]+)\$\$', fix_single_formula, content)
    
    # 3. 修复行内公式
    def fix_inline_formula(match):
        formula = match.group(1)
        formula = re.sub(r'\\sqrt\s+\{', r'\\sqrt{', formula)
        formula = re.sub(r'\\frac\s+\{', r'\\frac{', formula)
        formula = re.sub(r'([A-Za-z])_([A-Za-z0-9]+)', r'\1_{\2}', formula)
        return f'${formula}$'
    
    content = re.sub(r'\$([^$]+)\$', fix_inline_formula, content)
    
    # 4. 处理剩余的裸露数学命令（更谨慎的方法）
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # 检查是否是裸露的数学公式行（包含等号和LaTeX命令，但不在$中）
        if (re.search(r'^[^$]*[\\](frac|sqrt|partial|sum|int|Delta|times|cdot)', line) and 
            '=' in line and 
            not line.strip().startswith('```') and
            not line.strip().startswith('#') and
            '$' not in line):  # 确保不是已经包装的公式
            
            print(f"修复裸露公式行 {i+1}: {line[:50]}...")
            # 包装为块级公式
            fixed_line = f'$${line.strip()}$$'
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def check_math_syntax(content):
    """检查数学公式语法"""
    print("\n检查数学公式语法...")
    
    issues = []
    
    # 检查嵌套的$$
    nested_count = len(re.findall(r'\$\$[^$]*\$\$[^$]*\$\$[^$]*\$\$', content))
    if nested_count > 0:
        issues.append(f"发现 {nested_count} 处嵌套的$$符号")
    
    # 检查裸露的LaTeX命令
    lines = content.split('\n')
    bare_latex_lines = []
    for i, line in enumerate(lines, 1):
        if (re.search(r'[^$\\][\\](frac|sqrt|partial)', line) and '$' not in line):
            bare_latex_lines.append(i)
    
    if bare_latex_lines:
        issues.append(f"发现 {len(bare_latex_lines)} 行裸露LaTeX命令：{bare_latex_lines[:5]}")
    
    # 检查不匹配的$符号
    single_dollar_count = content.count('$') - content.count('$$') * 2
    if single_dollar_count % 2 != 0:
        issues.append("发现不匹配的$符号")
    
    if issues:
        print("⚠️ 发现问题：")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ 数学公式语法检查通过")
        return True

def create_precisely_fixed_version():
    """创建精确修复版本"""
    print("创建精确修复版本...")
    
    with open('output/properly_fixed_textbook.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 精确修复
    fixed_content = fix_math_precisely(content)
    
    # 语法检查
    is_valid = check_math_syntax(fixed_content)
    
    # 统计信息
    inline_math = len(re.findall(r'\$[^$]+\$', fixed_content))
    block_math = len(re.findall(r'\$\$[^$]+\$\$', fixed_content))
    
    print(f"\n修复统计：")
    print(f"行内公式: {inline_math} 个")
    print(f"块级公式: {block_math} 个")
    print(f"总公式: {inline_math + block_math} 个")
    
    with open('output/precisely_fixed_textbook.md', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("精确修复版本已创建: output/precisely_fixed_textbook.md")
    return is_valid

if __name__ == "__main__":
    create_precisely_fixed_version()