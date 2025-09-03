#!/usr/bin/env python3
"""
简化版合并工具 - 只做必要的修复
"""

import os
import re
from pathlib import Path

def minimal_fixes(content):
    """只做最基本的修复"""
    # 1. 修复图片路径
    content = re.sub(r'\!\[(.*?)\]\(\.\./images/', r'![\1](docs/chapters/images/', content)
    content = re.sub(r'\!\[(.*?)\]\(images/(ch6_[^)]+)\)', r'![\1](docs/chapters/chapter06/images/\2)', content)
    
    # 2. 修复admonitions为简单的引用
    content = re.sub(r'!!! (\w+) "([^"]*)"', r'> **\2**', content)
    content = re.sub(r'!!! (\w+)\s*\n', r'> **\1**\n', content)
    
    # 3. 清理Unicode转义
    content = re.sub(r'\\u[0-9a-fA-F]{4}', '', content)
    content = re.sub(r'<parameter name="todos">.*?</parameter>', '', content, flags=re.DOTALL)
    
    # 4. 不处理数学公式！让pandoc自己处理
    
    return content

def simple_merge():
    """简单合并所有文件"""
    print("开始简单合并...")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    merged_parts = []
    
    # 封面
    merged_parts.append("# 智慧水利平台架构与开发\n")
    
    # 前言
    preface_file = Path("../docs/前言.md")
    if preface_file.exists():
        with open(preface_file, 'r', encoding='utf-8') as f:
            content = minimal_fixes(f.read())
            merged_parts.append(content)
    
    # 处理所有章节
    chapter_dirs = sorted(Path("../docs/chapters").glob("chapter*"))
    for chapter_dir in chapter_dirs:
        print(f"处理 {chapter_dir.name}...")
        
        # 主章节文件
        main_file = chapter_dir / f"{chapter_dir.name}.md"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = minimal_fixes(f.read())
                merged_parts.append(content)
        
        # 小节文件
        section_files = sorted(chapter_dir.glob("section*.md"))
        for section_file in section_files:
            with open(section_file, 'r', encoding='utf-8') as f:
                content = minimal_fixes(f.read())
                merged_parts.append(content)
    
    # 写入合并文件
    final_content = '\n\n\\pagebreak\n\n'.join(merged_parts)
    
    output_file = output_dir / "simple_textbook.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"简单合并完成！输出：{output_file}")

if __name__ == "__main__":
    simple_merge()