#!/usr/bin/env python3
"""
智慧水利教材转换器 - Markdown预处理工具
修复常见的转换问题
"""

import re
import sys
import os
from pathlib import Path

def fix_admonitions(content):
    """修复MkDocs admonitions为LaTeX可识别格式"""
    # 处理 !!! info "标题" 格式
    content = re.sub(r'!!! (\w+) "([^"]*)"', r'\\begin{tcolorbox}[title=\2,colback=blue!5!white,colframe=blue!75!black]\n', content)
    content = re.sub(r'!!! (\w+)', r'\\begin{tcolorbox}[colback=blue!5!white,colframe=blue!75!black]\n', content)
    
    # 处理结束标记（通过空行或下一个标题来判断）
    lines = content.split('\n')
    new_lines = []
    in_admonition = False
    
    for i, line in enumerate(lines):
        if '\\begin{tcolorbox}' in line:
            in_admonition = True
            new_lines.append(line)
        elif in_admonition and (line.strip() == '' or line.startswith('#') or (i == len(lines) - 1)):
            new_lines.append('\\end{tcolorbox}\n')
            in_admonition = False
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def fix_code_blocks(content):
    """修复代码块格式"""
    # 确保代码块前后有空行
    content = re.sub(r'(\n```)', r'\n\n```', content)
    content = re.sub(r'(```\n)', r'```\n\n', content)
    
    # 处理行内代码
    content = re.sub(r'`([^`]+)`', r'\\texttt{\1}', content)
    
    return content

def fix_tables(content):
    """修复表格格式"""
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        if '|' in line and not line.strip().startswith('#'):
            # 这可能是表格行
            if i > 0 and '|' not in lines[i-1]:
                # 表格开始前加空行
                new_lines.append('')
            new_lines.append(line)
            # 检查是否是表格结束
            if i < len(lines) - 1 and '|' not in lines[i+1]:
                # 表格结束后加空行
                new_lines.append('')
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def fix_headers(content):
    """修复章节标题格式"""
    # 确保标题前后有适当的空行
    content = re.sub(r'\n(#{1,6} )', r'\n\n\1', content)
    content = re.sub(r'(#{1,6} [^\n]+)\n([^\n#])', r'\1\n\n\2', content)
    
    return content

def fix_lists(content):
    """修复列表格式"""
    # 确保列表前有空行
    content = re.sub(r'\n(\d+\. )', r'\n\n\1', content)
    content = re.sub(r'\n([-*] )', r'\n\n\1', content)
    
    return content

def preprocess_markdown(content):
    """预处理markdown内容"""
    content = fix_headers(content)
    content = fix_code_blocks(content)
    content = fix_tables(content)
    content = fix_lists(content)
    content = fix_admonitions(content)
    
    # 清理多余的空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

def main():
    if len(sys.argv) != 3:
        print("用法: python preprocess_markdown.py input_file output_file")
        return 1
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        processed_content = preprocess_markdown(content)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        print(f"处理完成: {input_file} -> {output_file}")
        return 0
        
    except Exception as e:
        print(f"处理失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())