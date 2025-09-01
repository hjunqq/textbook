#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaTeX质量检查脚本 - 检查生成的LaTeX文件是否存在常见问题
"""

import re
from pathlib import Path

def check_latex_quality(tex_file_path):
    """检查LaTeX文件质量"""
    
    with open(tex_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 开始检查LaTeX文件质量...")
    
    issues = []
    
    # 1. 检查未定义的命令
    print("   检查未定义的命令...")
    fa_commands = re.findall(r'\\fa[A-Z][A-Za-z]*', content)
    if fa_commands:
        issues.append(f"发现未定义的FontAwesome命令: {set(fa_commands)}")
    
    # 2. 检查错误的引用
    print("   检查错误的反向引用...")
    bad_refs = re.findall(r'\\[0-9]+', content)
    if bad_refs:
        issues.append(f"发现错误的反向引用: {set(bad_refs)}")
    
    # 3. 检查表格格式
    print("   检查表格格式...")
    broken_tables = re.findall(r'\\begin\{longtable\}\[\]\{\s*[lcr]\s*\}\s*[lcr]\s*\}\s*[lcr]\s*\}\}', content)
    if broken_tables:
        issues.append(f"发现破碎的表格定义: {len(broken_tables)} 个")
    
    # 4. 检查图片引用
    print("   检查图片引用...")
    images_without_size = re.findall(r'\\includegraphics\{[^}]+\}(?!\[)', content)
    if images_without_size:
        print(f"   ⚠️ 发现 {len(images_without_size)} 个没有尺寸设置的图片")
    
    # 5. 检查空环境
    print("   检查空环境...")
    empty_tcolorbox = re.findall(r'\\begin\{tcolorbox\}[^\\]*\\end\{tcolorbox\}', content)
    empty_count = sum(1 for box in empty_tcolorbox if len(box.strip()) < 50)
    if empty_count > 0:
        issues.append(f"发现 {empty_count} 个可能的空tcolorbox")
    
    # 6. 统计基本信息
    print("   统计基本信息...")
    chapter_count = len(re.findall(r'\\chapter\{', content))
    section_count = len(re.findall(r'\\section\{', content))
    table_count = len(re.findall(r'\\begin\{longtable\}', content))
    image_count = len(re.findall(r'\\includegraphics', content))
    tcolorbox_count = len(re.findall(r'\\begin\{tcolorbox\}', content))
    
    print(f"\n📊 LaTeX文件统计:")
    print(f"   章节数量: {chapter_count}")
    print(f"   小节数量: {section_count}")
    print(f"   表格数量: {table_count}")
    print(f"   图片数量: {image_count}")
    print(f"   特殊块数量: {tcolorbox_count}")
    
    # 7. 报告问题
    if issues:
        print(f"\n❌ 发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        return False
    else:
        print(f"\n✅ LaTeX文件检查通过，未发现严重问题!")
        return True

def main():
    tex_file = Path("输出/教材.tex")
    
    if not tex_file.exists():
        print("❌ 未找到教材.tex文件")
        return
    
    print(f"📄 检查文件: {tex_file}")
    print(f"📏 文件大小: {tex_file.stat().st_size / 1024:.1f} KB")
    
    is_clean = check_latex_quality(tex_file)
    
    if is_clean:
        print(f"\n🎉 文件质量良好，可以进行LaTeX编译!")
    else:
        print(f"\n⚠️ 建议运行修复脚本解决发现的问题")

if __name__ == "__main__":
    main()