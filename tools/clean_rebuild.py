#!/usr/bin/env python3
"""
全新重启方案：从源文件重新构建，系统化处理数学公式
"""

import os
import re
from pathlib import Path

def clean_rebuild_from_source():
    """从源文件完全重新构建"""
    print("🔄 全新重启：从源文件重新构建")
    
    # 第一步：重新合并所有章节（不做任何数学处理）
    print("第一步：重新合并源文件...")
    
    chapters_dir = Path('../docs/chapters')
    all_content = []
    
    # 添加前言
    preface_file = Path('../docs/前言.md')
    if preface_file.exists():
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
            print(f"    添加 {section_file.name}")
            with open(section_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_content.append(content)
    
    # 合并内容
    raw_content = '\n\n'.join(all_content)
    print(f"原始合并完成，总长度: {len(raw_content):,} 字符")
    
    return raw_content

def minimal_safe_fixes(content):
    """只做最安全的最小修复"""
    print("第二步：只做最安全的修复...")
    
    # 统计原始状态
    original_single = content.count('$') 
    original_double = content.count('$$')
    print(f"原始状态 - 单$: {original_single}, 双$$: {original_double}")
    
    # 修复1：只修复明显的admonition语法
    content = re.sub(r'!!! (\w+)', r'**\1**', content)
    
    # 修复2：只修复明显错误的图片路径（保守）
    content = re.sub(r'!\[([^\]]*)\]\(docs/chapters/', r'![\1](', content)
    
    # 修复3：移除Unicode转义（这个肯定有问题）
    content = re.sub(r'\\u[0-9a-fA-F]{4}', '', content)
    
    # 统计修复后状态
    after_single = content.count('$')
    after_double = content.count('$$') 
    print(f"基础修复后 - 单$: {after_single}, 双$$: {after_double}")
    
    return content

def save_clean_version(content):
    """保存干净版本"""
    with open('output/clean_rebuild.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("干净版本已保存: output/clean_rebuild.md")

def test_clean_version():
    """测试干净版本"""
    print("第三步：测试干净版本（不修改任何数学公式）...")
    
    # 创建测试脚本
    test_script = '''@echo off
chcp 65001
echo 测试完全干净的版本（不修改数学公式）
pandoc output\\clean_rebuild.md --defaults simple-config.yaml -o "output\\测试_干净版本.pdf" 2>clean_test_error.txt

if %errorlevel% equ 0 (
    echo ✅ 干净版本成功！
    for %%f in ("output\\测试_干净版本.pdf") do echo PDF大小: %%~zf 字节
) else (
    echo ❌ 干净版本也失败
    type clean_test_error.txt
    echo.
    echo 这说明问题不在数学公式，而在其他地方：
    echo - 文件编码问题
    echo - 特殊字符问题  
    echo - 图片路径问题
    echo - Pandoc配置问题
)
pause'''
    
    with open('test_clean_rebuild.bat', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("测试脚本已创建: test_clean_rebuild.bat")

if __name__ == "__main__":
    # 确保输出目录存在
    Path('output').mkdir(exist_ok=True)
    
    # 完全重新开始
    clean_content = clean_rebuild_from_source()
    
    # 最小安全修复
    safe_content = minimal_safe_fixes(clean_content)
    
    # 保存干净版本
    save_clean_version(safe_content)
    
    # 创建测试脚本
    test_clean_version()
    
    print("\n" + "="*50)
    print("🔄 全新重启完成！")
    print("请运行: test_clean_rebuild.bat")
    print("这将测试完全干净的版本，不修改任何数学公式")
    print("如果成功 -> 问题确实在数学公式")
    print("如果失败 -> 问题在其他地方，我们就知道真正的原因了")
    print("="*50)