#!/usr/bin/env python3
"""
修复章节结构 - 这才是根本问题！
"""

import re
from pathlib import Path

def fix_chapter_structure():
    """修复混乱的章节结构"""
    print("📚 修复章节结构...")
    
    with open('output/clean_rebuild.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("原始文件分析...")
    
    # 找到所有一级标题
    h1_titles = re.findall(r'^# (.+)$', content, re.MULTILINE)
    print(f"发现 {len(h1_titles)} 个一级标题:")
    for i, title in enumerate(h1_titles[:10]):  # 显示前10个
        print(f"  {i+1}. {title}")
    if len(h1_titles) > 10:
        print(f"  ... 还有 {len(h1_titles) - 10} 个")
    
    # 修复章节结构
    print("\n开始修复...")
    
    # 1. 修复错误的一级标题 (# 4.1.1 -> ## 4.1.1)
    pattern1 = r'^# (\d+\.\d+.*?)$'
    matches1 = re.findall(pattern1, content, re.MULTILINE)
    content = re.sub(pattern1, r'## \1', content, flags=re.MULTILINE)
    print(f"修复小节标题为二级标题: {len(matches1)} 个")
    
    # 2. 修复其他错误格式
    pattern2 = r'^# (\d+\.\d+\.\d+.*?)$'
    matches2 = re.findall(pattern2, content, re.MULTILINE)  
    content = re.sub(pattern2, r'### \1', content, flags=re.MULTILINE)
    print(f"修复子小节标题为三级标题: {len(matches2)} 个")
    
    # 3. 确保主章节标题格式正确
    chapter_pattern = r'^# 第([一二三四五六七八九])章'
    chapter_matches = re.findall(chapter_pattern, content, re.MULTILINE)
    print(f"发现正确的主章节: {len(chapter_matches)} 个")
    
    # 4. 添加目录结构
    print("\n生成目录结构...")
    
    # 重新扫描修复后的标题
    h1_final = re.findall(r'^# (.+)$', content, re.MULTILINE)
    h2_final = re.findall(r'^## (.+)$', content, re.MULTILINE)
    
    print(f"修复后结构:")
    print(f"  一级标题: {len(h1_final)} 个")
    print(f"  二级标题: {len(h2_final)} 个")
    
    # 保存修复后的文件
    with open('output/structure_fixed.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n章节结构修复完成: output/structure_fixed.md")
    
    # 生成目录预览
    toc_content = "# 目录\n\n"
    for title in h1_final[:15]:  # 显示前15个主要标题
        toc_content += f"- {title}\n"
    
    with open('output/toc_preview.md', 'w', encoding='utf-8') as f:
        f.write(toc_content)
    
    print("目录预览已生成: output/toc_preview.md")

if __name__ == "__main__":
    fix_chapter_structure()