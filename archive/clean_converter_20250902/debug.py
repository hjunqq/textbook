#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试版转换器 - 用于问题诊断
"""

import sys
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent / 'core'))

from core.config import config
from core.validator import validator
from core.converter import converter

def debug_conversion():
    """调试转换流程"""
    print("🐛 调试模式：转换流程诊断")
    print("=" * 60)
    
    # 1. 检查环境
    print("📋 环境检查:")
    print(f"  项目根目录: {config.project_root}")
    print(f"  文档目录: {config.docs_dir}")
    print(f"  输出目录: {config.output_dir}")
    print(f"  模板目录: {config.templates_dir}")
    
    # 2. 检查文件发现
    print(f"\n📁 文件发现测试:")
    try:
        chapters = converter._discover_chapters()
        print(f"  发现文件: {len(chapters)} 个")
        for i, (file_type, file_path) in enumerate(chapters[:5]):  # 只显示前5个
            print(f"  [{i+1}] {file_type}: {Path(file_path).name}")
        if len(chapters) > 5:
            print(f"  ... 还有 {len(chapters)-5} 个文件")
    except Exception as e:
        print(f"  ❌ 文件发现失败: {e}")
        return
    
    # 3. 测试预处理
    print(f"\n🔧 预处理测试:")
    try:
        # 取前3个文件测试
        test_files = chapters[:3]
        for file_type, file_path in test_files:
            print(f"  测试文件: {Path(file_path).name}")
            from core.preprocessor import preprocessor
            content = preprocessor.process_file(Path(file_path), file_type)
            print(f"    处理后长度: {len(content)} 字符")
            if not content.strip():
                print(f"    ⚠️  内容为空")
    except Exception as e:
        print(f"  ❌ 预处理失败: {e}")
    
    # 4. 检查输出目录
    print(f"\n📂 输出目录检查:")
    print(f"  输出目录存在: {config.output_dir.exists()}")
    images_dir = config.output_dir / "images"
    print(f"  图片目录存在: {images_dir.exists()}")
    if images_dir.exists():
        image_files = list(images_dir.glob("*"))
        print(f"  图片文件数量: {len(image_files)}")
        if image_files:
            print(f"  示例图片: {image_files[0].name}")
    
    # 5. 检查合并文件
    merged_file = config.get_output_path("textbook_merged.md")
    print(f"\n📄 合并文件检查:")
    print(f"  合并文件存在: {merged_file.exists()}")
    if merged_file.exists():
        with open(merged_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"  文件大小: {len(content)} 字符")
        lines = content.split('\n')
        print(f"  文件行数: {len(lines)}")
        
        # 检查图片引用
        import re
        image_refs = re.findall(r'!\[.*?\]\((.*?)\)', content)
        print(f"  图片引用数量: {len(image_refs)}")
        if image_refs:
            print(f"  示例引用: {image_refs[0]}")
    
    # 6. 测试简单Pandoc命令
    print(f"\n🔄 Pandoc命令测试:")
    if merged_file.exists():
        simple_cmd = [
            'pandoc',
            'textbook_merged.md',
            '-o', 'test_simple.html',
            '--from=markdown',
            '--to=html'
        ]
        
        print(f"  测试命令: {' '.join(simple_cmd)}")
        print(f"  工作目录: {config.output_dir}")
        
        import subprocess
        try:
            result = subprocess.run(simple_cmd, capture_output=True, text=True, 
                                  encoding='utf-8', cwd=config.output_dir, timeout=30)
            
            print(f"  返回码: {result.returncode}")
            if result.returncode == 0:
                test_html = config.output_dir / "test_simple.html"
                if test_html.exists():
                    size = test_html.stat().st_size
                    print(f"  ✅ HTML测试成功 ({size} bytes)")
                else:
                    print(f"  ⚠️  命令成功但文件不存在")
            else:
                print(f"  ❌ 命令失败")
                if result.stderr:
                    print(f"  错误: {result.stderr[:200]}...")
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  命令超时")
        except Exception as e:
            print(f"  ❌ 命令异常: {e}")
    
    print(f"\n🎯 调试总结:")
    print("  如果上述步骤都正常，问题可能在:")
    print("  1. LaTeX模板过于复杂")
    print("  2. XeLaTeX环境配置")
    print("  3. 特定内容导致的编译错误")
    print("  建议先尝试HTML输出验证内容正确性")

if __name__ == '__main__':
    debug_conversion()