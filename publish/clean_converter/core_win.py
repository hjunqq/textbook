#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows环境专用核心处理脚本
只负责文件预处理和合并，转换交给Windows的Pandoc
"""

import os
import sys
import shutil
from pathlib import Path

def setup_paths():
    """设置Windows路径"""
    script_dir = Path(__file__).parent
    
    # Windows环境下的路径
    project_root = script_dir.parent.parent
    docs_dir = project_root / 'docs'
    output_dir = script_dir / 'output'
    images_dir = output_dir / 'images'
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    return docs_dir, output_dir, images_dir

def discover_files(docs_dir):
    """发现文件（简化版）"""
    files = []
    
    # 前言
    preface = docs_dir / '前言.md'
    if preface.exists():
        files.append(('preface', preface))
    
    # 章节
    chapters_dir = docs_dir / 'chapters'
    if chapters_dir.exists():
        chapter_order = [f'chapter{i:02d}' for i in range(1, 10)]
        
        for chapter_key in chapter_order:
            chapter_dir = chapters_dir / chapter_key
            if chapter_dir.exists():
                # 章节主文件
                main_file = chapter_dir / f'{chapter_key}.md'
                if main_file.exists():
                    files.append(('chapter', main_file))
                
                # section文件
                for section_file in sorted(chapter_dir.glob('section*.md')):
                    files.append(('section', section_file))
    
    return files

def simple_preprocess(content, file_type, file_path, image_counter, output_images_dir):
    """简化的预处理"""
    
    # 基本的标题处理
    if file_type == 'chapter':
        # 提取章节号
        chapter_match = None
        for i in range(1, 10):
            if f'chapter{i:02d}' in str(file_path):
                chapter_match = i
                break
        
        if chapter_match:
            chapter_titles = {
                1: '第一章 智慧水利概述与平台架构基础',
                2: '第二章 软件工程基础与需求分析', 
                3: '第三章 版本控制与协作开发',
                4: '第四章 数据库设计与数据管理',
                5: '第五章 后端开发与API设计',
                6: '第六章 倾斜摄影三维建模技术',
                7: '第七章 前端开发与用户界面设计',
                8: '第八章 系统集成与部署',
                9: '第九章 系统测试与质量保证'
            }
            title = chapter_titles.get(chapter_match, f'第{chapter_match}章')
            
            import re
            content = re.sub(r'^#\s+.*', f'# {title}', content, count=1, flags=re.MULTILINE)
    
    elif file_type == 'section':
        # section文件的标题处理
        import re
        section_match = re.search(r'section(\d+)-(\d+)', str(file_path))
        if section_match:
            chapter_num = int(section_match.group(1))
            section_num = int(section_match.group(2))
            content = re.sub(r'^#\s+(.+)', f'## {chapter_num}.{section_num} \\1', 
                           content, count=1, flags=re.MULTILINE)
    
    # 简化的图片处理
    import re
    def process_image(match):
        nonlocal image_counter
        alt_text = match.group(1)
        original_path = match.group(2)
        
        # 查找原始图片
        possible_paths = [
            file_path.parent / original_path,
            file_path.parent / 'images' / Path(original_path).name,
            file_path.parent.parent / 'images' / Path(original_path).name,
        ]
        
        # 在整个docs目录中搜索
        docs_root = file_path
        while docs_root.name != 'docs' and docs_root.parent != docs_root:
            docs_root = docs_root.parent
        
        if docs_root.name == 'docs':
            for img_file in docs_root.rglob(Path(original_path).name):
                possible_paths.append(img_file)
        
        # 尝试复制图片
        for src_path in possible_paths:
            if src_path.exists():
                try:
                    ext = src_path.suffix.lower()
                    new_name = f'image_{image_counter:03d}{ext}'
                    dst_path = output_images_dir / new_name
                    
                    shutil.copy2(src_path, dst_path)
                    image_counter += 1
                    
                    print(f'  复制图片: {src_path.name} -> {new_name}')
                    return f'![{alt_text}](images/{new_name})'
                except Exception as e:
                    print(f'  复制图片失败: {e}')
                    break
        
        print(f'  警告: 图片未找到 {original_path}')
        return match.group(0)  # 保持原样
    
    content = re.sub(r'!\[(.*?)\]\((.*?)\)', process_image, content)
    
    return content, image_counter

def clean_latex_content(content):
    """清理可能导致LaTeX错误的内容"""
    import re
    
    # 移除或转义可能有问题的字符和模式
    
    # 1. 修复换行符问题
    content = content.replace('\\n', '\n')  # 将文字\n转换为真正的换行
    content = content.replace('\\r', '')    # 移除\r
    content = content.replace('\\t', ' ')   # 将\t转换为空格
    
    # 2. 转义LaTeX特殊字符
    latex_special_chars = {
        '#': '\\#',
        '$': '\\$', 
        '%': '\\%',
        '&': '\\&',
        '^': '\\textasciicircum{}',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '\\': '\\textbackslash{}'
    }
    
    # 但是要避免转义已经在代码块中的内容
    # 简单处理：先保护代码块
    code_blocks = []
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f'__CODE_BLOCK_{len(code_blocks)-1}__'
    
    # 保护代码块
    content = re.sub(r'```.*?```', save_code_block, content, flags=re.DOTALL)
    content = re.sub(r'`[^`]+`', save_code_block, content)
    
    # 转义特殊字符（除了在代码块中的）
    for char, escape in latex_special_chars.items():
        if char != '\\':  # 反斜杠需要特殊处理
            content = content.replace(char, escape)
    
    # 恢复代码块
    for i, block in enumerate(code_blocks):
        content = content.replace(f'__CODE_BLOCK_{i}__', block)
    
    # 3. 清理多余的空行
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # 4. 修复可能的日期格式问题
    content = re.sub(r'(\d{4})年(\d{1,2})月\s*\\n', r'\1年\2月', content)
    
    return content

def main():
    """主处理函数"""
    print('📝 Windows环境文件预处理')
    print('=' * 40)
    
    try:
        # 设置路径
        docs_dir, output_dir, images_dir = setup_paths()
        
        print(f'📁 源目录: {docs_dir}')
        print(f'📁 输出目录: {output_dir}')
        
        # 发现文件
        files = discover_files(docs_dir)
        print(f'📄 发现文件: {len(files)} 个')
        
        if not files:
            print('❌ 未找到源文件')
            return 1
        
        # 处理文件
        merged_parts = []
        image_counter = 1
        
        for file_type, file_path in files:
            print(f'  处理 {file_type}: {file_path.name}')
            
            try:
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 预处理
                processed_content, image_counter = simple_preprocess(
                    content, file_type, file_path, image_counter, images_dir
                )
                
                if processed_content.strip():
                    merged_parts.append(processed_content)
                    merged_parts.append('')  # 空行分隔
                    
            except Exception as e:
                print(f'  警告: 处理文件失败 {file_path}: {e}')
                continue
        
        # 保存合并文件
        merged_content = '\n'.join(merged_parts)  # 修复：应该是真正的换行符，不是\n字符串
        
        # 清理内容，移除可能导致LaTeX错误的字符
        merged_content = clean_latex_content(merged_content)
        
        merged_file = output_dir / 'textbook_merged.md'
        
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        print(f'✅ 合并文件已生成: {merged_file}')
        print(f'📊 文件大小: {len(merged_content)} 字符')
        print(f'🖼️  处理图片: {image_counter-1} 个')
        
        return 0
        
    except Exception as e:
        print(f'❌ 处理失败: {e}')
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)