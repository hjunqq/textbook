#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复LaTeX文件中的emoji问题
"""

import os
import re

def fix_emojis_in_file(filepath):
    """修复单个文件中的emoji"""
    # Emoji到LaTeX图标的映射
    emoji_map = {
        '🌐': r'',  # 移除，或用 \faGlobe 替换
        '📖': r'',  # 移除
        '📱': r'',  # 移除  
        '📑': r'',  # 移除
        '🎨': r'',  # 移除
        '🚀': r'',  # 移除
        '📚': r'',  # 移除
        '🤝': r'',  # 移除
        '🐛': r'',  # 移除
        '📞': r'',  # 移除
        '📧': r'',  # 移除
        '💬': r'',  # 移除
        '🛠': r'',  # 移除
        '️': r'',   # 移除修饰符
        '📄': r'',  # 移除
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换已知的emoji
        for emoji, replacement in emoji_map.items():
            content = content.replace(emoji, replacement)
        
        # 清理可能的多余空格
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r' +', ' ', content)
        
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
            if fix_emojis_in_file(filepath):
                fixed_count += 1
        else:
            print(f"- 文件不存在: {filepath}")
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件。")

if __name__ == '__main__':
    main()
