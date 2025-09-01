#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节状态查看器 - 快速查看各章节的处理状态
"""

from pathlib import Path
import os

def check_chapter_status():
    """检查章节状态"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    source_dir = project_root / "docs" / "chapters"
    output_dir = script_dir / "output" / "chapters"
    images_dir = script_dir / "output" / "images"
    
    chapter_titles = {
        'chapter01': '第一章 智慧水利概述与平台架构基础',
        'chapter02': '第二章 软件工程基础与需求分析',
        'chapter03': '第三章 版本控制系统Git',
        'chapter04': '第四章 前端开发技术栈',
        'chapter05': '第五章 后端开发框架',
        'chapter06': '第六章 数据处理与算法实现',
        'chapter07': '第七章 系统集成与部署',
        'chapter08': '第八章 性能优化与监控',
        'chapter09': '第九章 项目管理与团队协作'
    }
    
    print("智慧水利教材章节状态检查")
    print("=" * 60)
    print(f"源目录: {source_dir}")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    
    for chapter_id, title in chapter_titles.items():
        print(f"\n📖 {chapter_id}: {title}")
        print("-" * 50)
        
        # 检查源文件
        source_chapter_dir = source_dir / chapter_id
        if source_chapter_dir.exists():
            main_file = source_chapter_dir / f"{chapter_id}.md"
            section_files = list(source_chapter_dir.glob("section*.md"))
            
            print(f"  📁 源目录: ✅ 存在")
            print(f"  📄 主文件: {'✅' if main_file.exists() else '❌'} {main_file.name}")
            print(f"  📄 节文件: {len(section_files)} 个")
            
            # 检查图片
            image_dirs = [
                source_chapter_dir / "images",
                source_dir.parent / "assets" / "images" / chapter_id,
                source_dir.parent / "chapters" / "images" / chapter_id
            ]
            
            total_images = 0
            for img_dir in image_dirs:
                if img_dir.exists():
                    images = list(img_dir.rglob("*.png")) + list(img_dir.rglob("*.jpg")) + \
                            list(img_dir.rglob("*.jpeg")) + list(img_dir.rglob("*.svg"))
                    total_images += len(images)
            
            print(f"  🖼️  源图片: {total_images} 个")
        else:
            print(f"  📁 源目录: ❌ 不存在")
            continue
        
        # 检查输出文件
        if output_dir.exists():
            output_md = output_dir / f"{chapter_id}.md"
            output_tex = output_dir / f"{chapter_id}.tex"
            output_pdf = output_dir / f"{chapter_id}.pdf"
            
            if output_md.exists():
                size_kb = output_md.stat().st_size // 1024
                print(f"  📄 处理后MD: ✅ {size_kb} KB")
            else:
                print(f"  📄 处理后MD: ❌ 未生成")
            
            if output_tex.exists():
                size_kb = output_tex.stat().st_size // 1024
                print(f"  📄 LaTeX文件: ✅ {size_kb} KB")
            else:
                print(f"  📄 LaTeX文件: ❌ 未生成")
            
            if output_pdf.exists():
                size_kb = output_pdf.stat().st_size // 1024
                print(f"  📄 PDF文件: ✅ {size_kb} KB")
            else:
                print(f"  📄 PDF文件: ❌ 未生成")
        else:
            print(f"  📁 输出目录: ❌ 不存在")
    
    # 检查图片目录
    if images_dir.exists():
        all_images = list(images_dir.glob("*"))
        print(f"\n🖼️  统一图片目录: {len(all_images)} 个文件")
        
        # 按章节分组统计
        chapter_image_counts = {}
        for img in all_images:
            if img.is_file():
                chapter_prefix = img.name.split('_')[0]
                if chapter_prefix.startswith('chapter'):
                    chapter_image_counts[chapter_prefix] = chapter_image_counts.get(chapter_prefix, 0) + 1
        
        for chapter_id, count in sorted(chapter_image_counts.items()):
            print(f"    {chapter_id}: {count} 个")
    else:
        print(f"\n🖼️  统一图片目录: ❌ 不存在")
    
    print("\n" + "=" * 60)
    print("💡 使用建议:")
    print("  1. 运行 convert_chapter.bat chapter01 开始处理第1章")
    print("  2. 逐章检查和修改，确保质量")
    print("  3. 处理完所有章节后可以合并成完整教材")
    print("=" * 60)

if __name__ == '__main__':
    check_chapter_status()