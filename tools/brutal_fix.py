#!/usr/bin/env python3
"""
暴力解决方案：移除所有数学公式，生成可用的PDF
"""

import re

def brutal_fix():
    """暴力移除所有可能有问题的内容"""
    print("🔨 暴力解决：移除所有问题内容")
    
    with open('output/clean_rebuild.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 移除所有数学公式，用文字描述替代
    content = re.sub(r'\$[^$]*\$', '[数学公式]', content)
    content = re.sub(r'\$\$[^$]*\$\$', '[数学公式]', content)
    
    # 2. 移除所有裸露的LaTeX命令
    latex_patterns = [
        r'\\sqrt\{[^}]*\}',
        r'\\frac\{[^}]*\}\{[^}]*\}', 
        r'\\[a-zA-Z]+\{[^}]*\}',
        r'\\[a-zA-Z]+',
    ]
    
    for pattern in latex_patterns:
        content = re.sub(pattern, '[LaTeX]', content)
    
    # 3. 简化所有图片为文字描述
    content = re.sub(r'!\[[^\]]*\]\([^)]*\)', '[图片]', content)
    
    # 4. 移除特殊字符
    content = re.sub(r'[^\x00-\x7F\u4e00-\u9fff]', '', content)
    
    print("所有问题内容已移除")
    
    with open('output/brutal_fix.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("暴力修复版本: output/brutal_fix.md")

if __name__ == "__main__":
    brutal_fix()