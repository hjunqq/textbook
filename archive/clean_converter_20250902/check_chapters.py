#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节状态检查工具 - 快速查看每个章节的文件情况
"""

import sys
from pathlib import Path

# 添加core模块路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from core.config import Config

def check_chapter_status():
    """检查所有章节的状态"""
    print("📋 智慧水利教材章节状态检查")
    print("=" * 50)
    
    config = Config()
    
    print(f"📁 源文档目录: {config.docs_dir}")
    print(f"📁 输出目录: {config.output_dir}")
    print()
    
    all_good = True
    
    for chapter_id, title in config.chapter_order.items():
        print(f"📖 {chapter_id}: {title}")
        print("-" * 40)
        
        # 检查源文件
        chapter_dir = config.docs_dir / 'chapters' / chapter_id
        chapter_file = chapter_dir / f'{chapter_id}.md'
        
        if chapter_file.exists():
            size = chapter_file.stat().st_size
            print(f"  ✅ 源文件存在: {chapter_file.name} ({size} bytes)")
        else:
            print(f"  ❌ 源文件缺失: {chapter_file}")
            all_good = False
            continue
        
        # 检查图片目录
        image_locations = [
            config.docs_dir / 'chapters' / 'images' / chapter_id,
            config.docs_dir / 'chapters' / chapter_id / 'images',
            config.docs_dir / 'assets' / 'images' / chapter_id
        ]
        
        image_count = 0
        for img_dir in image_locations:
            if img_dir.exists():
                images = list(img_dir.rglob('*'))
                images = [f for f in images if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']]
                image_count += len(images)
        
        if image_count > 0:
            print(f"  🖼️  图片文件: {image_count} 个")
        else:
            print(f"  ℹ️  无图片文件")
        
        # 检查已处理的测试文件
        test_dir = config.output_dir / 'single_tests'
        if test_dir.exists():
            test_md = test_dir / f'{chapter_id}.md'
            test_tex = test_dir / f'{chapter_id}.tex'
            test_pdf = test_dir / f'{chapter_id}.pdf'
            
            if test_md.exists():
                print(f"  📄 已处理MD: {test_md.name}")
            if test_tex.exists():
                print(f"  📄 已生成LaTeX: {test_tex.name}")
            if test_pdf.exists():
                size_kb = test_pdf.stat().st_size // 1024
                print(f"  📄 已生成PDF: {test_pdf.name} ({size_kb} KB)")
        
        print()
    
    print("=" * 50)
    if all_good:
        print("✅ 所有章节源文件完整")
    else:
        print("⚠️  存在缺失的章节文件")
    
    print()
    print("💡 使用建议:")
    print("  1. 运行 test_single_chapter.bat 逐章测试")
    print("  2. 选择从第1章开始，逐步验证")
    print("  3. 发现问题及时修复，再测试下一章")
    print("  4. 全部章节测试通过后，运行完整转换")

if __name__ == '__main__':
    check_chapter_status()