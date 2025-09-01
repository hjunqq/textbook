#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试文件合并问题
"""
import sys
from pathlib import Path
from latex_config import CHAPTER_MAPPING

def debug_merge():
    source_dir = Path(__file__).parent.parent.parent / 'docs'
    chapter_key = 'chapter01'
    
    print(f"源目录: {source_dir}")
    print(f"章节键: {chapter_key}")
    
    if chapter_key not in CHAPTER_MAPPING:
        print(f"章节键 {chapter_key} 不存在")
        return
    
    chapter_info = CHAPTER_MAPPING[chapter_key]
    print(f"章节信息: {chapter_info}")
    
    combined_content = ""
    
    if 'files' in chapter_info:
        print("这是多文件章节")
        for i, file_path in enumerate(chapter_info['files']):
            source_file = source_dir / file_path
            print(f"\n处理文件 {i+1}: {file_path}")
            print(f"完整路径: {source_file}")
            print(f"文件存在: {source_file.exists()}")
            
            if source_file.exists():
                file_content = source_file.read_text(encoding='utf-8')
                print(f"文件长度: {len(file_content)} 字符")
                print(f"文件前50字符: {repr(file_content[:50])}")
                
                if combined_content:
                    combined_content += "\n\n"
                combined_content += file_content
                print(f"累计长度: {len(combined_content)} 字符")
            else:
                print(f"文件不存在!")
    
    print(f"\n最终合并文件长度: {len(combined_content)} 字符")
    print(f"最终合并文件前100字符: {repr(combined_content[:100])}")
    
    # 保存到临时文件
    debug_file = Path(__file__).parent / "debug_merged.md"
    debug_file.write_text(combined_content, encoding='utf-8')
    print(f"\n调试文件保存至: {debug_file}")

if __name__ == '__main__':
    debug_merge()
