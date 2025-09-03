#!/usr/bin/env python3
"""
智能章节合并工具 - 包含所有小节内容并修复格式
"""

import os
import re
from pathlib import Path

def fix_admonitions(content):
    """修复MkDocs admonitions语法"""
    # 处理 !!! info "标题" 格式
    content = re.sub(r'!!! (\w+) "([^"]*)"', r'> **\2**\n>\n', content)
    content = re.sub(r'!!! (\w+)\s*\n', r'> **\1**\n>\n', content)
    
    # 处理admonition内容（缩进的行）
    lines = content.split('\n')
    new_lines = []
    in_admonition = False
    
    for i, line in enumerate(lines):
        if line.startswith('> **') and ('**' in line[4:]):
            in_admonition = True
            new_lines.append(line)
        elif in_admonition and line.strip() == '':
            # 空行结束admonition
            in_admonition = False
            new_lines.append(line)
        elif in_admonition and line.startswith('    '):
            # 缩进内容转换为引用
            new_lines.append(f'> {line[4:]}')
        elif in_admonition and not line.startswith('#'):
            # 其他内容也转为引用
            new_lines.append(f'> {line}')
        else:
            if in_admonition and (line.startswith('#') or i == len(lines) - 1):
                in_admonition = False
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def fix_image_paths(content):
    """修复图片路径"""
    # 修复图片路径：../images/ -> docs/chapters/images/
    content = re.sub(r'\!\[(.*?)\]\(\.\./images/', r'![\1](docs/chapters/images/', content)
    
    # 修复第6章特殊图片路径：images/ch6_ -> docs/chapters/chapter06/images/ch6_
    content = re.sub(r'\!\[(.*?)\]\(images/(ch6_[^)]+)\)', r'![\1](docs/chapters/chapter06/images/\2)', content)
    
    return content

def fix_math_formulas(content):
    """修复数学公式格式"""
    # 修复数学公式中的下标
    content = re.sub(r'([A-Za-z])_([A-Za-z0-9]+)', r'\1_{\2}', content)
    
    # 查找并修复包含数学符号的行
    lines = content.split('\n')
    new_lines = []
    i = 0
    in_code_block = False
    
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # 检查是否进入或退出代码块
        if line_stripped.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            i += 1
            continue
            
        # 如果在代码块内，不处理数学公式
        if in_code_block:
            new_lines.append(line)
            i += 1
            continue
        
        # 跳过已经在数学环境中的内容
        if line_stripped.startswith('$') or line_stripped.endswith('$'):
            new_lines.append(line)
            i += 1
            continue
            
        # 检查是否是数学公式行 - 更宽松的检测
        is_math_formula = (
            '=' in line_stripped and 
            ('{' in line_stripped and '}' in line_stripped) and  # 包含下标格式
            not line_stripped.startswith('#') and 
            not line_stripped.startswith('|') and
            # 排除JavaScript/编程语言的代码行
            not 'const ' in line_stripped and
            not 'let ' in line_stripped and
            not 'var ' in line_stripped and
            not 'function' in line_stripped and
            not 'new ' in line_stripped and
            not 'import' in line_stripped and
            not '.env' in line_stripped and
            not 'WebSocket' in line_stripped and
            not 'http' in line_stripped.lower() and
            not 'url' in line_stripped.lower() and
            # 这行看起来像数学公式
            ('cdots' in line_stripped or 'sqrt' in line_stripped or 
             re.search(r'[A-Za-z]_\{[A-Za-z0-9]+\}', line_stripped))
        )
            
        if is_math_formula:
            # 检查下一行是否是公式编号
            formula = line_stripped
            if (i + 1 < len(lines) and 
                lines[i + 1].strip().startswith('(') and 
                lines[i + 1].strip().endswith(')')):
                equation_number = lines[i + 1].strip()
                new_lines.append(f'$${formula}$$ \\quad {equation_number}')
                i += 2  # 跳过编号行
            else:
                new_lines.append(f'$${formula}$$')
                i += 1
        else:
            new_lines.append(line)
            i += 1
    
    content = '\n'.join(new_lines)
    
    # 清理多余的空公式行和错误的公式包装
    content = re.sub(r'\$\$\s*\$\$', '', content)
    content = re.sub(r'\n\$\$\s*\n', '\n', content)
    content = re.sub(r'\$\$在式.*?\$\$', '在式', content)  # 修复"$$在式...$$"问题
    
    return content

def fix_encoding_issues(content):
    """修复编码和特殊字符问题"""
    # 移除Unicode转义序列
    content = re.sub(r'\\u[0-9a-fA-F]{4}', '', content)
    
    # 移除Claude工具产生的JSON片段
    content = re.sub(r'<parameter name="todos">.*?</parameter>', '', content, flags=re.DOTALL)
    content = re.sub(r'\[{.*?"status".*?}\]', '', content, flags=re.DOTALL)
    
    # 清理其他可能的特殊字符
    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', content)
    
    return content

def fix_formatting(content):
    """修复其他格式问题"""
    # 修复编码问题
    content = fix_encoding_issues(content)
    
    # 修复数学公式
    content = fix_math_formulas(content)
    
    # 修复图片路径
    content = fix_image_paths(content)
    
    # 修复代码块格式
    content = re.sub(r'```(\w+)\n', r'```\1\n', content)
    
    # 确保标题前后有空行
    content = re.sub(r'(\n)(#{1,6} )', r'\1\n\2', content)
    content = re.sub(r'(#{1,6} [^\n]+)(\n)([^#\n])', r'\1\2\n\3', content)
    
    return content

def process_chapter_files(chapter_dir):
    """处理单个章节的所有文件"""
    chapter_path = Path(chapter_dir)
    if not chapter_path.exists():
        return ""
    
    content_parts = []
    
    # 先添加主章节文件
    main_chapter = chapter_path / f"{chapter_path.name}.md"
    if main_chapter.exists():
        with open(main_chapter, 'r', encoding='utf-8') as f:
            chapter_content = f.read()
            chapter_content = fix_admonitions(chapter_content)
            chapter_content = fix_formatting(chapter_content)
            content_parts.append(chapter_content)
    
    # 添加所有小节文件
    section_files = sorted(chapter_path.glob("section*.md"))
    for section_file in section_files:
        with open(section_file, 'r', encoding='utf-8') as f:
            section_content = f.read()
            section_content = fix_admonitions(section_content)
            section_content = fix_formatting(section_content)
            content_parts.append(section_content)
    
    return '\n\n'.join(content_parts)

def main():
    """合并所有章节和小节"""
    print("开始合并所有章节和小节...")
    
    # 创建输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    merged_content = []
    
    # 添加封面
    merged_content.append("# 智慧水利平台架构与开发\n")
    
    # 添加前言
    preface_file = Path("../docs/前言.md")
    if preface_file.exists():
        with open(preface_file, 'r', encoding='utf-8') as f:
            preface_content = f.read()
            preface_content = fix_admonitions(preface_content)
            preface_content = fix_formatting(preface_content)
            merged_content.append(preface_content)
    
    # 处理所有章节
    chapter_dirs = sorted(Path("../docs/chapters").glob("chapter*"))
    for chapter_dir in chapter_dirs:
        print(f"处理 {chapter_dir.name}...")
        chapter_content = process_chapter_files(chapter_dir)
        if chapter_content.strip():
            merged_content.append(chapter_content)
    
    # 写入合并文件
    final_content = '\n\n\\newpage\n\n'.join(merged_content)
    
    output_file = output_dir / "complete_textbook.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"合并完成！输出文件：{output_file}")
    print(f"总计 {len(merged_content)} 个部分")

if __name__ == "__main__":
    main()