#!/usr/bin/env python3
"""
数学公式语法修复器
"""

import re
from pathlib import Path

def fix_latex_math_syntax(content):
    """修复LaTeX数学公式语法错误"""
    
    # 修复 \sqrt { 的空格问题
    content = re.sub(r'\\sqrt\s+\{', r'\\sqrt{', content)
    
    # 修复 \frac { 的空格问题  
    content = re.sub(r'\\frac\s+\{', r'\\frac{', content)
    
    # 修复 \sum\limits { 的空格问题
    content = re.sub(r'\\sum\\limits\s+\{', r'\\sum\\limits{', content)
    
    # 修复其他常见的LaTeX命令空格问题
    content = re.sub(r'\\(left|right)\s+\{', r'\\\1{', content)
    content = re.sub(r'\\(left|right)\s+\\([()])', r'\\\1\\\2', content)
    
    return content

def basic_fixes(content):
    """基本修复"""
    # 图片路径
    content = re.sub(r'\!\[(.*?)\]\(\.\./images/', r'![\1](docs/chapters/images/', content)
    content = re.sub(r'\!\[(.*?)\]\(images/(ch6_[^)]+)\)', r'![\1](docs/chapters/chapter06/images/\2)', content)
    
    # admonitions
    content = re.sub(r'!!! (\w+) "([^"]*)"', r'> **\2**', content)
    content = re.sub(r'!!! (\w+)\s*\n', r'> **\1**\n', content)
    
    # 清理Unicode
    content = re.sub(r'\\u[0-9a-fA-F]{4}', '', content)
    content = re.sub(r'<parameter name="todos">.*?</parameter>', '', content, flags=re.DOTALL)
    
    # 修复数学公式语法！
    content = fix_latex_math_syntax(content)
    
    return content

def math_syntax_merge():
    """专门修复数学公式语法的合并"""
    print("开始修复数学公式语法并合并...")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    merged_parts = []
    
    # 封面
    merged_parts.append("# 智慧水利平台架构与开发\n")
    
    # 前言
    preface_file = Path("../docs/前言.md")
    if preface_file.exists():
        with open(preface_file, 'r', encoding='utf-8') as f:
            content = basic_fixes(f.read())
            merged_parts.append(content)
    
    # 处理所有章节
    chapter_dirs = sorted(Path("../docs/chapters").glob("chapter*"))
    for chapter_dir in chapter_dirs:
        print(f"处理 {chapter_dir.name}...")
        
        # 主章节文件
        main_file = chapter_dir / f"{chapter_dir.name}.md"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = basic_fixes(f.read())
                merged_parts.append(content)
        
        # 小节文件
        section_files = sorted(chapter_dir.glob("section*.md"))
        for section_file in section_files:
            with open(section_file, 'r', encoding='utf-8') as f:
                content = basic_fixes(f.read())
                merged_parts.append(content)
    
    # 写入合并文件
    final_content = '\n\n\\pagebreak\n\n'.join(merged_parts)
    
    output_file = output_dir / "math_fixed_textbook.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"数学公式语法修复完成！输出：{output_file}")

if __name__ == "__main__":
    math_syntax_merge()