#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器 - 预处理模块
统一处理Markdown文件的格式标准化
"""

import re
import os
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from .config import config

class MarkdownPreprocessor:
    """Markdown预处理器"""
    
    def __init__(self):
        self.image_counter = 1
        self.processed_images = {}
        
    def process_file(self, file_path: Path, file_type: str = 'section') -> str:
        """处理单个Markdown文件"""
        print(f"处理文件: {file_path}")
        
        # 读取文件内容
        content = self._read_file_safe(file_path)
        if not content:
            return ""
        
        # 预处理流程
        content = self._remove_yaml_frontmatter(content)
        content = self._standardize_headings(content, file_path, file_type)
        content = self._fix_code_blocks(content)
        content = self._process_images(content, file_path)
        content = self._convert_admonitions(content)
        content = self._clean_content(content)
        
        return content
    
    def _read_file_safe(self, file_path: Path) -> str:
        """安全读取文件，处理编码问题"""
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"成功读取文件 ({encoding}): {file_path}")
                return content
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        print(f"警告：无法读取文件 {file_path}")
        return ""
    
    def _remove_yaml_frontmatter(self, content: str) -> str:
        """移除YAML前言"""
        content = content.replace('\r\n', '\n')
        if content.startswith('---'):
            pattern = r'^---\s*\n.*?\n---\s*\n'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        return content
    
    def _standardize_headings(self, content: str, file_path: Path, file_type: str) -> str:
        """标准化标题格式"""
        name = file_path.name
        
        if file_type == 'preface':
            # 前言文件处理
            content = re.sub(r'^#\s+(.+)', r'# \1', content, count=1, flags=re.MULTILINE)
        
        elif file_type == 'chapter' and 'chapter' in name:
            # 章节文件处理
            chapter_match = re.search(r'chapter(\d+)', name)
            if chapter_match:
                chapter_num = chapter_match.group(1).zfill(2)
                chapter_key = f'chapter{chapter_num}'
                title = config.get_chapter_title(chapter_key)
                content = re.sub(r'^#\s+.*', f'# {title}', content, count=1, flags=re.MULTILINE)
        
        elif file_type == 'section' and 'section' in name:
            # 节文件处理
            section_match = re.search(r'section(\d+)-(\d+)', name)
            if section_match:
                chapter_num = int(section_match.group(1))
                section_num = int(section_match.group(2))
                content = re.sub(r'^#\s+(.+)', f'## {chapter_num}.{section_num} \\1', content, count=1, flags=re.MULTILINE)
                # 调整其他标题级别
                content = re.sub(r'^##\s+(?!{}\\.{})(.+)'.format(chapter_num, section_num), r'### \\1', content, flags=re.MULTILINE)
        
        return content
    
    def _fix_code_blocks(self, content: str) -> str:
        """修复代码块格式"""
        # 检测并添加语言标识
        def detect_language(code_content: str) -> str:
            """智能检测代码语言"""
            code_lower = code_content.lower()
            
            # 检测模式
            if any(keyword in code_lower for keyword in ['function', 'const ', 'let ', 'var ', '=>']):
                return 'javascript'
            elif any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', 'print(']):
                return 'python'
            elif any(keyword in code_lower for keyword in ['public class', 'private ', 'package ', 'import java']):
                return 'java'
            elif any(keyword in code_lower for keyword in ['using system', 'namespace', 'public class']):
                return 'csharp'
            elif any(keyword in code_lower for keyword in ['select ', 'from ', 'where ', 'insert ', 'update']):
                return 'sql'
            elif any(keyword in code_lower for keyword in ['<', '>', '</', 'html', 'div']):
                return 'xml'
            elif any(keyword in code_lower for keyword in ['.class', '#', 'color:', 'font-']):
                return 'css'
            else:
                return 'text'
        
        # 修复空的代码块
        def fix_code_block(match):
            language = match.group(1)
            code_content = match.group(2)
            
            if not language or language.strip() == '':
                language = detect_language(code_content)
            
            return f'```{language}\n{code_content}\n```'
        
        # 处理代码块
        content = re.sub(r'```(\w*)\n(.*?)\n```', fix_code_block, content, flags=re.DOTALL)
        
        return content
    
    def _process_images(self, content: str, source_file: Path) -> str:
        """统一处理图片路径"""
        def process_image_match(match):
            alt_text = match.group(1)
            original_path = match.group(2)
            
            # 查找并复制图片
            image_path = self._find_and_copy_image(original_path, source_file)
            
            if image_path:
                return f'![{alt_text}]({image_path})'
            else:
                print(f"警告：找不到图片 {original_path}")
                return match.group(0)  # 保持原样
        
        # 处理图片引用
        content = re.sub(r'!\[(.*?)\]\((.*?)\)', process_image_match, content)
        
        return content
    
    def _find_and_copy_image(self, image_path: str, source_file: Path) -> Optional[str]:
        """查找并复制图片文件"""
        # 可能的图片搜索路径
        search_paths = [
            source_file.parent / image_path,
            source_file.parent / "images" / Path(image_path).name,
            config.docs_dir / "assets" / "images" / Path(image_path).name,
            config.docs_dir / "chapters" / "images" / Path(image_path).name,
            config.project_root / "docs" / "chapters" / "images" / Path(image_path).name
        ]
        
        # 递归搜索
        for search_dir in [config.docs_dir, config.project_root]:
            for img_file in search_dir.rglob(Path(image_path).name):
                if img_file.suffix.lower() in config.image_extensions:
                    search_paths.append(img_file)
        
        # 查找存在的图片文件
        for search_path in search_paths:
            if search_path.exists():
                return self._copy_image_to_output(search_path)
        
        return None
    
    def _copy_image_to_output(self, source_image: Path) -> str:
        """复制图片到输出目录并返回相对路径"""
        if str(source_image) in self.processed_images:
            return self.processed_images[str(source_image)]
        
        # 生成新的文件名
        extension = source_image.suffix.lower()
        new_name = f"image_{self.image_counter:03d}{extension}"
        self.image_counter += 1
        
        # 复制文件
        output_path = config.output_dir / "images" / new_name
        try:
            shutil.copy2(source_image, output_path)
            relative_path = f"images/{new_name}"
            self.processed_images[str(source_image)] = relative_path
            print(f"复制图片: {source_image} -> {relative_path}")
            return relative_path
        except Exception as e:
            print(f"复制图片失败 {source_image}: {e}")
            return None
    
    def _convert_admonitions(self, content: str) -> str:
        """转换警告框语法"""
        admonition_mapping = {
            'warning': 'warningbox',
            'info': 'infobox',
            'tip': 'tipbox',
            'note': 'notebox',
            'important': 'importantbox'
        }
        
        def convert_admonition(match):
            adm_type = match.group(1).lower()
            title = match.group(2) or adm_type.capitalize()
            content = match.group(3).strip()
            
            latex_env = admonition_mapping.get(adm_type, 'infobox')
            
            return f"""
\\begin{{{latex_env}}}[{title}]
{content}
\\end{{{latex_env}}}
"""
        
        # 转换 !!! 语法
        pattern = r'!!!\s+(\w+)(?:\s+"([^"]*)")?\n((?:(?!^\s*$).*\n?)*)'
        content = re.sub(pattern, convert_admonition, content, flags=re.MULTILINE)
        
        return content
    
    def _clean_content(self, content: str) -> str:
        """清理内容格式"""
        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 清理行尾空白
        content = re.sub(r' +$', '', content, flags=re.MULTILINE)
        
        # 确保文件结尾有换行符
        if content and not content.endswith('\n'):
            content += '\n'
        
        return content

# 导出预处理器实例
preprocessor = MarkdownPreprocessor()