#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

def remove_reference_sections(filename):
    """从文件中删除所有参考文献段落"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 \paragraph*{参考文献} 及其后面的所有内容，直到下一个主要部分
    # 参考文献通常在 \section, \subsection 或下一个 \paragraph 之前结束
    pattern = r'\n\s*\\paragraph\*\{参考文献\}.*?(?=\n\s*\\(?:section|subsection|subsubsection|paragraph\*{(?!参考文献)|clearpage|endinput|end\{document\})|\Z)'
    
    original_content = content
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # 检查是否找到并删除了内容
    if content != original_content:
        removed_lines = original_content.count('\n') - content.count('\n')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, removed_lines
    return False, 0

# 处理各章节
files_to_process = [
    'chapters/chapter01.tex',
    'chapters/chapter06.tex',
    'chapters/chapter07.tex',
    'chapters/chapter08.tex'
]

for filepath in files_to_process:
    try:
        removed, lines = remove_reference_sections(filepath)
        if removed:
            print(f"✓ {filepath}: 删除了参考文献段落 ({lines} 行)")
        else:
            print(f"✗ {filepath}: 未找到参考文献段落")
    except Exception as e:
        print(f"✗ {filepath}: 处理错误 - {e}")

