#!/usr/bin/env python3
"""
完整的一键解决方案：从源文件到最终PDF
"""

import os
import re
from pathlib import Path

def ensure_output_dir():
    """确保输出目录存在"""
    Path('output').mkdir(exist_ok=True)
    print("✅ 输出目录已准备")

def rebuild_from_source():
    """从源文件完全重新构建"""
    print("📚 从源文件重新构建...")
    
    chapters_dir = Path('../docs/chapters')
    all_content = []
    
    # 添加前言
    preface_file = Path('../docs/前言.md')
    if preface_file.exists():
        print("  添加前言...")
        with open(preface_file, 'r', encoding='utf-8') as f:
            all_content.append(f.read())
    
    # 按顺序添加章节
    chapter_order = [
        'chapter01', 'chapter02', 'chapter03', 'chapter04', 'chapter05',
        'chapter06', 'chapter07', 'chapter08', 'chapter09'
    ]
    
    for chapter in chapter_order:
        chapter_dir = chapters_dir / chapter
        if not chapter_dir.exists():
            continue
            
        print(f"  处理 {chapter}...")
        
        # 添加主章节文件
        main_file = chapter_dir / f"{chapter}.md"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_content.append(content)
        
        # 添加章节下的所有section文件
        for section_file in sorted(chapter_dir.glob("section*.md")):
            with open(section_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_content.append(content)
    
    # 合并内容
    raw_content = '\n\n'.join(all_content)
    print(f"✅ 原始合并完成，总长度: {len(raw_content):,} 字符")
    
    return raw_content

def fix_chapter_structure(content):
    """修复章节结构"""
    print("🔧 修复章节结构...")
    
    # 第一步：将所有标题降级
    content = re.sub(r'^######', '######', content, flags=re.MULTILINE)  # 6级保持不变
    content = re.sub(r'^#####', '######', content, flags=re.MULTILINE)   # 5->6
    content = re.sub(r'^####', '#####', content, flags=re.MULTILINE)     # 4->5  
    content = re.sub(r'^###', '####', content, flags=re.MULTILINE)       # 3->4
    content = re.sub(r'^##', '###', content, flags=re.MULTILINE)         # 2->3
    content = re.sub(r'^#', '##', content, flags=re.MULTILINE)           # 1->2
    
    # 第二步：恢复真正的主章节为一级标题
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
    ]
    
    main_chapter_count = 0
    for pattern in main_chapters:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            content = re.sub(pattern, lambda m: m.group(0)[1:], content, flags=re.MULTILINE)  # 去掉一个#
            main_chapter_count += len(matches)
    
    print(f"✅ 恢复了 {main_chapter_count} 个主章节标题")
    return content

def basic_cleanup(content):
    """基础清理"""
    print("🧹 基础清理...")
    
    # 修复admonition语法
    content = re.sub(r'!!! (\w+)', r'**\1**', content)
    
    # 移除Unicode转义
    content = re.sub(r'\\u[0-9a-fA-F]{4}', '', content)
    
    # 修复图片路径
    content = re.sub(r'!\[([^\]]*)\]\(docs/chapters/', r'![\1](../docs/chapters/', content)
    content = re.sub(r'!\[([^\]]*)\]\(images/', r'![\1](../docs/chapters/images/', content)
    
    print("✅ 基础清理完成")
    return content

def remove_problematic_content(content):
    """移除所有可能有问题的内容"""
    print("🔨 移除问题内容...")
    
    # 移除所有数学公式
    math_count = len(re.findall(r'\$[^$]*\$', content))
    content = re.sub(r'\$[^$]*\$', '[数学公式]', content)
    content = re.sub(r'\$\$[^$]*\$\$', '[数学公式]', content)
    
    # 移除所有LaTeX命令
    latex_patterns = [
        r'\\sqrt\{[^}]*\}',
        r'\\frac\{[^}]*\}\{[^}]*\}', 
        r'\\[a-zA-Z]+\{[^}]*\}',
        r'\\[a-zA-Z]+',
    ]
    
    latex_count = 0
    for pattern in latex_patterns:
        matches = re.findall(pattern, content)
        latex_count += len(matches)
        content = re.sub(pattern, '[LaTeX]', content)
    
    # 移除emoji和特殊字符
    emoji_count = len(re.findall(r'[📱🔍📑💡🧮📊🌓📖🟢🔴🚨⚠️ℹ️🐛📝❌✅✓✗○□]', content))
    content = re.sub(r'[📱🔍📑💡🧮📊🌓📖🟢🔴🚨⚠️ℹ️🐛📝❌✅✓✗○□]', '', content)
    
    # 移除ASCII艺术字符
    content = re.sub(r'[├─│└┌┐┘┴┬┤├]', '', content)
    
    print(f"✅ 移除了 {math_count} 个数学公式, {latex_count} 个LaTeX命令, {emoji_count} 个特殊符号")
    return content

def generate_final_version():
    """生成最终版本"""
    print("\n" + "="*60)
    print("🚀 开始生成最终版本...")
    print("="*60)
    
    # 步骤1：确保目录存在
    ensure_output_dir()
    
    # 步骤2：从源文件重建
    content = rebuild_from_source()
    
    # 步骤3：修复章节结构
    content = fix_chapter_structure(content)
    
    # 步骤4：基础清理
    content = basic_cleanup(content)
    
    # 步骤5：移除问题内容
    content = remove_problematic_content(content)
    
    # 最终统计
    h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
    h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
    
    print(f"\n📊 最终文档统计:")
    print(f"  文档大小: {len(content):,} 字符")
    print(f"  主章节 (#): {h1_count}")
    print(f"  小节 (##): {h2_count}")
    
    # 保存最终版本
    with open('output/final_textbook.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 最终版本已保存: output/final_textbook.md")
    
    # 显示章节目录
    h1_titles = re.findall(r'^# (.+)$', content, re.MULTILINE)
    print(f"\n📋 章节目录:")
    for i, title in enumerate(h1_titles, 1):
        print(f"  {i}. {title}")
    
    return True

if __name__ == "__main__":
    try:
        success = generate_final_version()
        if success:
            print(f"\n🎉 完成！现在可以生成PDF了！")
            print(f"运行: pandoc output/final_textbook.md --pdf-engine=xelatex -V CJKmainfont=\"Microsoft YaHei\" --toc --toc-depth=2 -o output/教材最终版.pdf")
        else:
            print(f"\n❌ 生成失败")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()