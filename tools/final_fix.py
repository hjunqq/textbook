#!/usr/bin/env python3
"""
最终修复版本：彻底解决章节结构问题
"""

import os
import re
from pathlib import Path

def rebuild_and_fix():
    """重建并修复"""
    print("🔧 最终修复方案...")
    
    Path('output').mkdir(exist_ok=True)
    
    chapters_dir = Path('../docs/chapters')
    all_content = []
    
    # 添加前言
    preface_file = Path('../docs/前言.md')
    if preface_file.exists():
        with open(preface_file, 'r', encoding='utf-8') as f:
            all_content.append(f.read())
    
    # 按顺序添加章节
    for i in range(1, 10):  # chapter01 到 chapter09
        chapter = f'chapter{i:02d}'
        chapter_dir = chapters_dir / chapter
        if not chapter_dir.exists():
            continue
            
        # 添加主章节文件
        main_file = chapter_dir / f"{chapter}.md"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_content.append(content)
        
        # 添加所有section文件
        for section_file in sorted(chapter_dir.glob("section*.md")):
            with open(section_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_content.append(content)
    
    # 合并内容
    raw_content = '\n\n'.join(all_content)
    
    # 清理内容 - 在处理章节结构之前
    print("清理问题内容...")
    
    # 移除数学公式
    raw_content = re.sub(r'\$[^$]*\$', '[数学公式]', raw_content)
    raw_content = re.sub(r'\$\$[^$]*\$\$', '[数学公式]', raw_content)
    
    # 移除LaTeX命令
    raw_content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '[LaTeX]', raw_content)
    raw_content = re.sub(r'\\[a-zA-Z]+', '[LaTeX]', raw_content)
    
    # 移除特殊字符
    raw_content = re.sub(r'[📱🔍📑💡🧮📊🌓📖🟢🔴🚨⚠️ℹ️🐛📝❌✅✓✗○□├─│└┌┐┘┴┬┤]', '', raw_content)
    
    # 移除Unicode转义
    raw_content = re.sub(r'\\u[0-9a-fA-F]{4}', '', raw_content)
    
    # 现在处理章节结构
    print("修复章节结构...")
    
    # 一步到位的方法：直接替换特定的章节标题
    chapter_fixes = [
        (r'^#+\s*前言\s*$', '# 前言'),
        (r'^#+\s*\*?\*?第一章[^#]*$', '# 第一章 智慧水利概述与平台架构基础'),
        (r'^#+\s*\*?\*?第二章[^#]*$', '# 第二章 软件工程基础与需求分析'),
        (r'^#+\s*\*?\*?第三章[^#]*$', '# 第三章 软件模块详细设计'),
        (r'^#+\s*\*?\*?第四章[^#]*$', '# 第四章 前端开发技术'),
        (r'^#+\s*\*?\*?第五章[^#]*$', '# 第五章 后端开发技术'),
        (r'^#+\s*\*?\*?第六章[^#]*$', '# 第六章 三维场景技术基础'),
        (r'^#+\s*\*?\*?第七章[^#]*$', '# 第七章 三维场景的观测数据展示'),
        (r'^#+\s*\*?\*?第八章[^#]*$', '# 第八章 典型应用'),
        (r'^#+\s*\*?\*?第九章[^#]*$', '# 第九章 结语'),
    ]
    
    for pattern, replacement in chapter_fixes:
        raw_content = re.sub(pattern, replacement, raw_content, flags=re.MULTILINE)
    
    # 将剩余的#降级为##
    lines = raw_content.split('\n')
    fixed_lines = []
    main_chapters = ['# 前言', '# 第一章', '# 第二章', '# 第三章', '# 第四章', '# 第五章', '# 第六章', '# 第七章', '# 第八章', '# 第九章']
    
    for line in lines:
        if line.startswith('#'):
            # 如果是主章节，保持不变
            is_main_chapter = any(line.startswith(main) for main in main_chapters)
            if is_main_chapter:
                fixed_lines.append(line)
            else:
                # 其他标题降级
                if line.startswith('# '):
                    fixed_lines.append('## ' + line[2:])
                else:
                    fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    final_content = '\n'.join(fixed_lines)
    
    # 保存并验证
    with open('output/final_fixed_textbook.md', 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    # 验证结果
    h1_titles = re.findall(r'^# (.+)$', final_content, re.MULTILINE)
    print(f"\n最终章节目录 ({len(h1_titles)} 个):")
    for i, title in enumerate(h1_titles, 1):
        print(f"  {i}. {title}")
    
    print(f"\n文档大小: {len(final_content):,} 字符")
    print(f"文件已保存: output/final_fixed_textbook.md")
    
    return len(h1_titles) == 10  # 前言 + 9章

if __name__ == "__main__":
    success = rebuild_and_fix()
    if success:
        print("\n🎉 成功！所有章节都正确包含！")
    else:
        print("\n⚠️ 章节数量不对，需要检查")