#!/usr/bin/env python3
"""
彻底修复文档结构 - 只保留真正的章节标题为一级标题
"""

import re

def radical_structure_fix():
    """彻底修复文档结构"""
    print("🔧 彻底修复文档结构...")
    
    with open('output/clean_rebuild.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("第一步：将所有#降级为##...")
    # 先将所有标题降级
    content = re.sub(r'^######', '######', content, flags=re.MULTILINE)  # 6级保持不变
    content = re.sub(r'^#####', '######', content, flags=re.MULTILINE)   # 5->6
    content = re.sub(r'^####', '#####', content, flags=re.MULTILINE)     # 4->5  
    content = re.sub(r'^###', '####', content, flags=re.MULTILINE)       # 3->4
    content = re.sub(r'^##', '###', content, flags=re.MULTILINE)         # 2->3
    content = re.sub(r'^#', '##', content, flags=re.MULTILINE)           # 1->2
    
    print("第二步：恢复真正的主章节为一级标题...")
    
    # 只有这些应该是一级标题
    main_chapters = [
        r'^## 前言$',
        r'^## 第一章.*?$',
        r'^## 第二章.*?$', 
        r'^## 第三章.*?$',
        r'^## 第四章.*?$',
        r'^## 第五章.*?$',
        r'^## 第六章.*?$',
        r'^## 第七章.*?$',
        r'^## 第八章.*?$',
        r'^## 第九章.*?$',
        r'^## 第十章.*?$',
        r'^## 附录.*?$',
        r'^## 参考文献.*?$',
    ]
    
    main_chapter_count = 0
    for pattern in main_chapters:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            content = re.sub(pattern, lambda m: m.group(0)[1:], content, flags=re.MULTILINE)  # 去掉一个#
            main_chapter_count += len(matches)
            for match in matches:
                print(f"  恢复主章节: {match[2:]}")  # 去掉##显示
    
    print(f"恢复了 {main_chapter_count} 个主章节标题")
    
    # 最终统计
    h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
    h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
    h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
    
    print(f"\n最终结构统计:")
    print(f"  一级标题 (#): {h1_count}")
    print(f"  二级标题 (##): {h2_count}")  
    print(f"  三级标题 (###): {h3_count}")
    
    # 生成正确的目录
    h1_titles = re.findall(r'^# (.+)$', content, re.MULTILINE)
    print(f"\n正确的章节目录:")
    for i, title in enumerate(h1_titles, 1):
        print(f"  {i}. {title}")
    
    # 保存最终版本
    with open('output/final_structure.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n最终结构文件已保存: output/final_structure.md")
    
    # 移除数学公式，创建可发布版本
    print("\n创建无数学公式的发布版本...")
    clean_content = re.sub(r'\$[^$]*\$', '[数学公式]', content)
    clean_content = re.sub(r'\$\$[^$]*\$\$', '[数学公式]', clean_content)
    clean_content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '[LaTeX]', clean_content)
    clean_content = re.sub(r'\\[a-zA-Z]+', '[LaTeX]', clean_content)
    
    with open('output/ready_to_publish.md', 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print("发布版本已保存: output/ready_to_publish.md")

if __name__ == "__main__":
    radical_structure_fix()