#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复LaTeX文件中的listings代码块问题 - 终极版本
"""

import os
import re

def fix_listings_in_file_ultimate(filepath):
    """彻底修复单个文件中的listings问题"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 方法1：将所有lstlisting环境改为verbatim环境
        def replace_lstlisting(match):
            style = match.group(1) if match.group(1) else ""
            code_content = match.group(2)
            # 简单替换为verbatim
            return f'\\begin{{verbatim}}{code_content}\\end{{verbatim}}'
        
        # 匹配lstlisting环境，包括带样式的
        pattern = r'\\begin\{lstlisting\}(?:\[style=([^\]]*)\])?(.*?)\\end\{lstlisting\}'
        content = re.sub(pattern, replace_lstlisting, content, flags=re.DOTALL)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 修复了文件: {filepath}")
            return True
        else:
            print(f"- 无需修复: {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ 修复失败: {filepath} - {e}")
        return False

def main():
    """主函数"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 需要修复的文件
    files_to_fix = [
        'main_content.tex',
        'chapters/chapter01.tex',
        'chapters/chapter02.tex', 
        'chapters/chapter03.tex',
        'chapters/chapter04.tex',
        'chapters/chapter05.tex',
        'chapters/chapter06.tex',
        'chapters/chapter07.tex',
        'chapters/chapter08.tex',
        'chapters/chapter09.tex'
    ]
    
    fixed_count = 0
    
    for filename in files_to_fix:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            if fix_listings_in_file_ultimate(filepath):
                fixed_count += 1
        else:
            print(f"- 文件不存在: {filepath}")
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件。")

if __name__ == '__main__':
    main()
