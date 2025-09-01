#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单章节测试预处理工具
"""

import sys
import shutil
from pathlib import Path

# 添加core模块路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from core.config import Config
from core.preprocessor import MarkdownPreprocessor

def process_single_chapter(chapter_id):
    """处理单个章节"""
    print(f"🔄 处理章节: {chapter_id}")
    print("=" * 30)
    
    config = Config()
    preprocessor = MarkdownPreprocessor()
    
    # 检查章节是否存在
    if chapter_id not in config.chapter_order:
        print(f"❌ 章节 {chapter_id} 不存在")
        available_chapters = list(config.chapter_order.keys())
        print(f"💡 可用章节: {', '.join(available_chapters)}")
        return False
    
    # 查找章节文件
    chapter_dir = config.docs_dir / 'chapters' / chapter_id
    chapter_file = chapter_dir / f'{chapter_id}.md'
    
    if not chapter_file.exists():
        print(f"❌ 章节文件不存在: {chapter_file}")
        return False
    
    print(f"📄 找到章节文件: {chapter_file}")
    
    # 创建单章节测试目录
    test_dir = config.output_dir / 'single_tests'
    test_dir.mkdir(exist_ok=True)
    
    # 创建图片目录
    test_images_dir = test_dir / 'images'
    test_images_dir.mkdir(exist_ok=True)
    
    try:
        # 预处理章节内容
        print(f"⚙️  预处理章节内容...")
        processed_content = preprocessor.process_file(chapter_file, 'chapter')
        
        # 保存处理后的文件
        output_file = test_dir / f'{chapter_id}.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        print(f"✅ 处理完成")
        print(f"📊 内容长度: {len(processed_content)} 字符")
        print(f"💾 输出文件: {output_file}")
        
        # 复制相关图片
        print(f"🖼️  复制章节图片...")
        copy_chapter_images(chapter_id, config, test_images_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False

def copy_chapter_images(chapter_id, config, target_dir):
    """复制章节相关的图片"""
    images_copied = 0
    
    # 可能的图片位置
    image_locations = [
        config.docs_dir / 'chapters' / 'images' / chapter_id,
        config.docs_dir / 'chapters' / chapter_id / 'images',
        config.docs_dir / 'assets' / 'images' / chapter_id,
        config.docs_dir / 'assets' / 'images',
        config.docs_dir / 'chapters' / 'images'
    ]
    
    for image_dir in image_locations:
        if image_dir.exists():
            print(f"  📁 检查图片目录: {image_dir}")
            
            for image_file in image_dir.rglob('*'):
                if image_file.is_file() and image_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']:
                    # 保持相对路径结构
                    relative_path = image_file.relative_to(image_dir)
                    target_file = target_dir / relative_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    if not target_file.exists():
                        shutil.copy2(image_file, target_file)
                        images_copied += 1
                        print(f"    ✅ 复制: {relative_path}")
    
    if images_copied > 0:
        print(f"🖼️  共复制 {images_copied} 个图片文件")
    else:
        print(f"ℹ️  未找到 {chapter_id} 相关图片")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("❌ 用法: python test_single_chapter.py <chapter_id>")
        print("💡 示例: python test_single_chapter.py chapter01")
        return False
    
    chapter_id = sys.argv[1]
    
    print(f"📖 单章节测试预处理工具")
    print(f"章节: {chapter_id}")
    print("=" * 40)
    
    success = process_single_chapter(chapter_id)
    
    if success:
        print(f"\n🎉 章节 {chapter_id} 预处理完成")
        print(f"💡 可以继续进行LaTeX转换")
        return True
    else:
        print(f"\n❌ 章节 {chapter_id} 预处理失败")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)