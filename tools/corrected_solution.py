#!/usr/bin/env python3
"""
修复版本：正确处理章节结构
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
            print(f"  ⚠️ {chapter} 目录不存在")
            continue
            
        print(f"  处理 {chapter}...")
        
        # 添加主章节文件
        main_file = chapter_dir / f"{chapter}.md"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_content.append(content)
                print(f"    ✅ 添加 {chapter}.md")
        else:
            print(f"    ⚠️ {chapter}.md 不存在")
        
        # 添加章节下的所有section文件
        section_files = sorted(chapter_dir.glob("section*.md"))
        for section_file in section_files:
            with open(section_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_content.append(content)
                print(f"    ✅ 添加 {section_file.name}")
    
    # 合并内容
    raw_content = '\n\n'.join(all_content)
    print(f"✅ 原始合并完成，总长度: {len(raw_content):,} 字符")
    
    return raw_content

def check_original_structure(content):
    """检查原始结构"""
    print("🔍 检查原始章节结构...")
    
    h1_titles = re.findall(r'^# (.+)$', content, re.MULTILINE)
    print(f"找到 {len(h1_titles)} 个一级标题:")
    for i, title in enumerate(h1_titles[:15], 1):  # 显示前15个
        print(f"  {i:2d}. {title}")
    if len(h1_titles) > 15:
        print(f"  ... 还有 {len(h1_titles) - 15} 个")
    
    return h1_titles

def fix_chapter_structure_correctly(content):
    """正确修复章节结构"""
    print("🔧 正确修复章节结构...")
    
    # 检查原始结构
    original_h1 = check_original_structure(content)
    
    # 保存原始的主章节标题
    main_chapter_titles = []
    for title in original_h1:
        if ('第' in title and '章' in title) or title == '前言':
            main_chapter_titles.append(title)
    
    print(f"识别出主章节: {main_chapter_titles}")
    
    # 第一步：将所有#降级为##
    content = re.sub(r'^#', '##', content, flags=re.MULTILINE)
    
    # 第二步：将真正的主章节恢复为#
    for title in main_chapter_titles:
        # 精确匹配并恢复
        escaped_title = re.escape(title)
        pattern = f'^## {escaped_title}$'
        content = re.sub(pattern, f'# {title}', content, flags=re.MULTILINE)
        print(f"  恢复主章节: {title}")
    
    return content

def basic_cleanup(content):
    """基础清理"""
    print("🧹 基础清理...")
    
    # 修复admonition语法
    content = re.sub(r'!!! (\w+)', r'**\1**', content)
    
    # 移除Unicode转义
    content = re.sub(r'\\u[0-9a-fA-F]{4}', '', content)
    
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
    content = re.sub(r'[├─│└┌┐┘┴┬┤├┤]', '', content)
    
    print(f"✅ 移除了 {math_count} 个数学公式, {latex_count} 个LaTeX命令, {emoji_count} 个特殊符号")
    return content

def generate_corrected_version():
    """生成修正版本"""
    print("\n" + "="*60)
    print("🚀 开始生成修正版本...")
    print("="*60)
    
    # 步骤1：确保目录存在
    ensure_output_dir()
    
    # 步骤2：从源文件重建
    content = rebuild_from_source()
    
    # 步骤3：正确修复章节结构
    content = fix_chapter_structure_correctly(content)
    
    # 步骤4：基础清理
    content = basic_cleanup(content)
    
    # 步骤5：移除问题内容
    content = remove_problematic_content(content)
    
    # 最终统计和验证
    h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
    h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
    h1_titles = re.findall(r'^# (.+)$', content, re.MULTILINE)
    
    print(f"\n📊 最终文档统计:")
    print(f"  文档大小: {len(content):,} 字符")
    print(f"  主章节 (#): {h1_count}")
    print(f"  小节 (##): {h2_count}")
    
    # 保存最终版本
    with open('output/corrected_textbook.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修正版本已保存: output/corrected_textbook.md")
    
    # 显示最终章节目录
    print(f"\n📋 最终章节目录:")
    for i, title in enumerate(h1_titles, 1):
        print(f"  {i}. {title}")
    
    # 验证是否包含所有预期章节
    expected_chapters = ['前言', '第一章', '第二章', '第三章', '第四章', '第五章', '第六章', '第七章', '第八章', '第九章']
    missing_chapters = []
    for expected in expected_chapters:
        found = any(expected in title for title in h1_titles)
        if not found:
            missing_chapters.append(expected)
    
    if missing_chapters:
        print(f"\n⚠️ 缺失的章节: {missing_chapters}")
        return False
    else:
        print(f"\n✅ 所有章节都存在！")
        return True

if __name__ == "__main__":
    try:
        success = generate_corrected_version()
        if success:
            print(f"\n🎉 修正完成！所有章节都正确包含！")
            print(f"现在可以生成PDF: pandoc output/corrected_textbook.md --pdf-engine=xelatex -V CJKmainfont=\"Microsoft YaHei\" --toc --toc-depth=2 -o output/完整教材.pdf")
        else:
            print(f"\n❌ 仍有章节缺失，需要检查源文件")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()