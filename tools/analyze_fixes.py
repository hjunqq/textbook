#!/usr/bin/env python3
"""
分析数学公式修复效果
"""

import re
from pathlib import Path

def analyze_math_fixes():
    """分析修复效果"""
    print("分析数学公式修复效果...")
    
    # 读取修复后的文件
    with open('output/properly_fixed_textbook.md', 'r', encoding='utf-8') as f:
        fixed_content = f.read()
    
    # 统计修复情况
    print("\n=== 修复统计 ===")
    
    # 计算各类数学元素
    inline_math = len(re.findall(r'\$[^$]+\$', fixed_content))
    block_math = len(re.findall(r'\$\$[^$]+\$\$', fixed_content))
    
    print(f"行内数学公式 ($...$): {inline_math} 个")
    print(f"块级数学公式 ($$...$$): {block_math} 个")
    print(f"总数学公式: {inline_math + block_math} 个")
    
    # 检查是否还有裸露的LaTeX命令
    bare_commands = []
    bare_patterns = [
        r'[^$]\\frac[^$]',  # 裸露的\frac
        r'[^$]\\sqrt[^$]',  # 裸露的\sqrt  
        r'[^$]\\partial[^$]', # 裸露的\partial
        r'[^$]\\sum[^$]',   # 裸露的\sum
        r'[^$]\\int[^$]',   # 裸露的\int
    ]
    
    print("\n=== 检查剩余问题 ===")
    for i, pattern in enumerate(bare_patterns):
        matches = re.findall(pattern, fixed_content)
        cmd_name = ['frac', 'sqrt', 'partial', 'sum', 'int'][i]
        if matches:
            print(f"⚠️ 仍有裸露的\\{cmd_name}命令: {len(matches)} 个")
            bare_commands.extend(matches)
        else:
            print(f"✅ \\{cmd_name}命令已正确包装")
    
    # 检查文档结构
    print("\n=== 文档结构检查 ===")
    chapters = re.findall(r'^# ([^#\n]+)', fixed_content, re.MULTILINE)
    sections = re.findall(r'^## ([^#\n]+)', fixed_content, re.MULTILINE)
    
    print(f"主要章节: {len(chapters)} 个")
    print(f"二级标题: {len(sections)} 个")
    
    if chapters:
        print("章节列表:")
        for i, chapter in enumerate(chapters[:5], 1):  # 显示前5个
            print(f"  {i}. {chapter.strip()}")
        if len(chapters) > 5:
            print(f"  ... 还有 {len(chapters) - 5} 个章节")
    
    # 文件大小统计
    file_size = len(fixed_content.encode('utf-8'))
    print(f"\n文件大小: {file_size:,} 字节 ({file_size/1024/1024:.1f} MB)")
    
    # 创建修复报告
    report = f"""# 数学公式修复报告

## 修复统计
- 行内数学公式: {inline_math} 个
- 块级数学公式: {block_math} 个
- 总数学公式: {inline_math + block_math} 个

## 文档结构
- 主要章节: {len(chapters)} 个
- 二级标题: {len(sections)} 个
- 文件大小: {file_size:,} 字节

## 问题检查
"""
    
    if bare_commands:
        report += f"- ⚠️ 仍有 {len(bare_commands)} 个裸露LaTeX命令需要修复\n"
    else:
        report += "- ✅ 所有LaTeX命令已正确包装\n"
    
    with open('output/fix_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n修复报告已保存: output/fix_report.md")

if __name__ == "__main__":
    analyze_math_fixes()