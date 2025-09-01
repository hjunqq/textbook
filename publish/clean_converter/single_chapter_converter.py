#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单章节转换器 - 基于成功经验的逐章处理版本
"""

import os
import sys
import subprocess
import shutil
import re
import json
from pathlib import Path
from typing import List, Dict, Optional

class SingleChapterConverter:
    """单章节转换器"""
    
    def __init__(self):
        # 获取项目路径
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent
        self.source_dir = self.project_root / "docs"
        self.output_dir = script_dir / "output"
        self.chapter_output_dir = self.output_dir / "chapters"
        self.images_dir = self.output_dir / "images"
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chapter_output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 章节顺序映射
        self.chapter_order = {
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
        
        # 重置图片计数器（每章单独计数）
        self.reset_image_counter()
        
    def reset_image_counter(self):
        """重置图片计数器"""
        self.image_counter = 1
        self.image_mapping = {}
    
    def get_chapter_files(self, chapter_id: str) -> List[str]:
        """获取指定章节的所有文件"""
        if chapter_id not in self.chapter_order:
            raise ValueError(f"未知章节: {chapter_id}")
        
        chapter_files = []
        chapter_dir = self.source_dir / "chapters" / chapter_id
        
        if not chapter_dir.exists():
            raise FileNotFoundError(f"章节目录不存在: {chapter_dir}")
        
        # 添加章节主文件
        main_file = chapter_dir / f"{chapter_id}.md"
        if main_file.exists():
            chapter_files.append(str(main_file))
        
        # 添加节文件（按序号排序）
        section_files = sorted(chapter_dir.glob("section*.md"))
        chapter_files.extend(str(f) for f in section_files)
        
        print(f"章节 {chapter_id} 包含 {len(chapter_files)} 个文件")
        return chapter_files
    
    def standardize_chapters(self, content: str, file_path: str) -> str:
        """标准化章节编号 - 恢复成功版本的正确逻辑"""
        file_name = Path(file_path).name
        
        # 处理章节主文件的标题
        if file_name.startswith('chapter') and file_name.endswith('.md'):
            chapter_num = re.search(r'chapter(\d+)', file_name)
            if chapter_num:
                chapter_key = f"chapter{chapter_num.group(1).zfill(2)}"
                if chapter_key in self.chapter_order:
                    title = self.chapter_order[chapter_key]
                    # 确保章节标题使用正确的格式（不带前导0）
                    clean_chapter_num = int(chapter_num.group(1))
                    clean_title = title.replace(f'第{chapter_num.group(1).zfill(2)}章', f'第{clean_chapter_num}章')
                    content = re.sub(r'^#\s+.*', f'# {clean_title}', content, count=1, flags=re.MULTILINE)
        
        # 处理节文件的标题 - 恢复成功版本的添加编号逻辑
        if file_name.startswith('section'):
            section_match = re.search(r'section(\d+)-(\d+)', file_name)
            if section_match:
                chapter_num = int(section_match.group(1))  # 去掉前导0
                section_num = int(section_match.group(2))  # 去掉前导0
                # 将二级标题转换为正确的节标题格式
                content = re.sub(r'^##\s+(.+)', f'## {chapter_num}.{section_num} \\1', content, count=1, flags=re.MULTILINE)
        
        # 过滤不必要的章节
        unnecessary_sections = [
            r'^##\s+本章小结.*$',
            r'^##\s+重点难点.*$', 
            r'^##\s+思考题与练习.*$',
            r'^##\s+本节小结.*$',
            r'^##\s+参考文献.*$'
        ]
        
        for pattern in unnecessary_sections:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def unify_image_paths(self, content: str, file_path: str, chapter_id: str) -> str:
        """统一图片路径 - 为每个章节创建独立的图片目录"""
        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # 处理相对路径
            if not os.path.isabs(image_path):
                source_dir = Path(file_path).parent
                full_image_path = source_dir / image_path
            else:
                full_image_path = Path(image_path)
            
            # 检查图片是否存在
            if not full_image_path.exists():
                # 尝试在其他可能的位置查找
                possible_paths = [
                    self.source_dir / "assets" / "images" / Path(image_path).name,
                    self.source_dir / Path(image_path),
                    source_dir / "images" / Path(image_path).name,
                    self.source_dir / "chapters" / "images" / Path(image_path).name,
                    self.source_dir / "chapters" / "images" / chapter_id / Path(image_path).name,
                    self.source_dir / "chapters" / chapter_id / "images" / Path(image_path).name
                ]
                
                for possible_path in possible_paths:
                    if possible_path.exists():
                        full_image_path = possible_path
                        break
            
            if full_image_path.exists():
                # 生成新的文件名 - 包含章节前缀
                file_ext = full_image_path.suffix
                new_filename = f"{chapter_id}_{self.image_counter:03d}{file_ext}"
                new_path = self.images_dir / new_filename
                
                # 复制图片
                try:
                    shutil.copy2(full_image_path, new_path)
                    self.image_mapping[str(full_image_path)] = new_filename
                    self.image_counter += 1
                    
                    return f"![{alt_text}](images/{new_filename})"
                except Exception as e:
                    print(f"警告：复制图片失败 {full_image_path} -> {new_path}: {e}")
                    return match.group(0)
            else:
                print(f"警告：找不到图片文件: {image_path}")
                return f"![{alt_text}](图片缺失: {Path(image_path).name})"
        
        # 处理Markdown图片语法
        content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_image, content)
        return content
    
    def detect_code_language(self, lines: List[str]) -> str:
        """检测代码语言"""
        combined = '\n'.join(lines).lower()
        
        if any(keyword in combined for keyword in ['function', 'const', 'let', 'var', '=>']):
            return 'javascript'
        elif any(keyword in combined for keyword in ['def ', 'import ', 'from ', 'class ']):
            return 'python'
        elif any(keyword in combined for keyword in ['public class', 'private ', 'import java']):
            return 'java'
        elif any(keyword in combined for keyword in ['using ', 'namespace', 'public static']):
            return 'csharp'
        elif any(keyword in combined for keyword in ['select ', 'from ', 'where ', 'insert ']):
            return 'sql'
        elif any(keyword in combined for keyword in ['<template>', '<script>', '<style>']):
            return 'vue'
        elif any(keyword in combined for keyword in ['<html>', '<div>', '<span>']):
            return 'html'
        elif any(keyword in combined for keyword in ['body {', 'class {', '&:', 'margin:']):
            return 'css'
        else:
            return 'text'
    
    def fix_code_blocks(self, content: str) -> str:
        """修复代码块格式"""
        lines = content.split('\n')
        in_code_block = False
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                if not in_code_block:
                    # 开始代码块
                    in_code_block = True
                    # 如果没有指定语言，尝试推断
                    if line.strip() == '```':
                        # 查看下几行来推断语言
                        next_lines = lines[i+1:i+5] if i+5 < len(lines) else lines[i+1:]
                        language = self.detect_code_language(next_lines)
                        fixed_lines.append(f'```{language}')
                    else:
                        fixed_lines.append(line)
                else:
                    # 结束代码块
                    in_code_block = False
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_markdown_tables(self, content: str) -> str:
        """修复Markdown表格格式问题"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 检测表格开始（包含 | 的行）
            if '|' in line and line.strip():
                # 检查是否是表格行
                if line.count('|') >= 2:
                    table_lines = []
                    
                    # 收集连续的表格行
                    while i < len(lines) and '|' in lines[i] and lines[i].strip():
                        table_lines.append(lines[i])
                        i += 1
                    
                    # 处理收集到的表格
                    if len(table_lines) >= 2:  # 至少要有标题行和分隔行
                        processed_table = self.process_table(table_lines)
                        fixed_lines.extend(processed_table)
                    else:
                        fixed_lines.extend(table_lines)
                    
                    continue
            
            fixed_lines.append(line)
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def process_table(self, table_lines: List[str]) -> List[str]:
        """处理单个表格，确保格式正确"""
        if len(table_lines) < 2:
            return table_lines
        
        processed_lines = []
        
        for i, line in enumerate(table_lines):
            # 清理行首行尾空格，确保以|开始和结束
            line = line.strip()
            if not line.startswith('|'):
                line = '|' + line
            if not line.endswith('|'):
                line = line + '|'
            
            # 如果是第二行，确保它是正确的分隔行格式
            if i == 1:
                # 分隔行应该是 |---|---|---| 的格式
                cells = line.split('|')[1:-1]  # 去掉首尾空元素
                separator_cells = []
                for cell in cells:
                    cell_content = cell.strip()
                    if ':' in cell_content:
                        # 保持对齐设置
                        separator_cells.append(cell_content)
                    else:
                        # 默认左对齐
                        separator_cells.append('---')
                line = '|' + '|'.join(separator_cells) + '|'
            
            processed_lines.append(line)
        
        # 在表格前后添加空行以确保正确渲染
        result = [''] + processed_lines + ['']
        return result
    
    def convert_special_blocks(self, content: str) -> str:
        
        # 处理带标题的note块
        content = re.sub(
            r'!!! note "([^"]+)"\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=blue!5, colframe=blue!40, title=\\faInfoCircle\\ \\1]\n\\2\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理不带标题的note块
        content = re.sub(
            r'!!! note\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=blue!5, colframe=blue!40, title=\\faInfoCircle\\ 注意]\n\\1\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理tip块
        content = re.sub(
            r'!!! tip "([^"]+)"\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=green!5, colframe=green!40, title=\\faLightbulb\\ \\1]\n\\2\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        content = re.sub(
            r'!!! tip\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=green!5, colframe=green!40, title=\\faLightbulb\\ 提示]\n\\1\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理warning块
        content = re.sub(
            r'!!! warning "([^"]+)"\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=orange!5, colframe=orange!60, title=\\faExclamationTriangle\\ \\1]\n\\2\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        content = re.sub(
            r'!!! warning\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=orange!5, colframe=orange!60, title=\\faExclamationTriangle\\ 警告]\n\\1\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理important块
        content = re.sub(
            r'!!! important "([^"]+)"\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=red!5, colframe=red!60, title=\\faExclamation\\ \\1]\n\\2\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        content = re.sub(
            r'!!! important\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=red!5, colframe=red!60, title=\\faExclamation\\ 重要]\n\\1\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 清理tcolorbox内容中的多余缩进
        content = re.sub(r'^    ', '', content, flags=re.MULTILINE)
        
        return content
    
    def preprocess_markdown(self, content: str, file_path: str, chapter_id: str) -> str:
        """预处理Markdown内容"""
        
        # 1. 修复编码问题
        if content.startswith('\ufeff'):
            content = content[1:]
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 2. 标准化章节编号
        content = self.standardize_chapters(content, file_path)
        
        # 3. 统一图片路径
        content = self.unify_image_paths(content, file_path, chapter_id)
        
        # 4. 修复代码块
        content = self.fix_code_blocks(content)
        
        # 5. 修复表格格式 - 新增的关键步骤
        content = self.fix_markdown_tables(content)
        
        # 6. 转换特殊块
        content = self.convert_special_blocks(content)
        
        return content
    
    def process_single_chapter(self, chapter_id: str) -> Dict:
        """处理单个章节"""
        print(f"\n处理章节: {chapter_id} - {self.chapter_order[chapter_id]}")
        print("=" * 60)
        
        # 重置图片计数器
        self.reset_image_counter()
        
        # 获取章节文件
        chapter_files = self.get_chapter_files(chapter_id)
        
        # 合并章节内容
        merged_content = []
        for file_path in chapter_files:
            print(f"  处理文件: {Path(file_path).name}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                processed_content = self.preprocess_markdown(content, file_path, chapter_id)
                merged_content.append(processed_content)
                
            except Exception as e:
                print(f"  错误：处理文件失败 {file_path}: {e}")
                continue
        
        # 保存合并后的Markdown
        chapter_md = self.chapter_output_dir / f"{chapter_id}.md"
        final_content = '\n\n'.join(merged_content)
        
        with open(chapter_md, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"  ✅ Markdown保存: {chapter_md}")
        print(f"  📊 内容长度: {len(final_content)} 字符")
        print(f"  🖼️  图片数量: {len(self.image_mapping)} 个")
        
        return {
            'chapter_id': chapter_id,
            'title': self.chapter_order[chapter_id],
            'markdown_file': str(chapter_md),
            'content_length': len(final_content),
            'image_count': len(self.image_mapping),
            'image_mapping': self.image_mapping.copy()
        }
    
    def convert_chapter_to_latex(self, chapter_id: str) -> str:
        """将章节转换为LaTeX"""
        chapter_md = self.chapter_output_dir / f"{chapter_id}.md"
        chapter_tex = self.chapter_output_dir / f"{chapter_id}.tex"
        
        if not chapter_md.exists():
            raise FileNotFoundError(f"章节Markdown文件不存在: {chapter_md}")
        
        # 创建简单的LaTeX模板
        template = self.create_chapter_template()
        template_path = self.chapter_output_dir / f"{chapter_id}_template.tex"
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        # 执行Pandoc转换
        pandoc_cmd = [
            'pandoc',
            str(chapter_md),
            '--template', str(template_path),
            '--to', 'latex',
            '--no-highlight',
            '--number-sections',
            '--variable', 'geometry:margin=2.5cm',
            '--variable', 'fontsize=12pt',
            '--variable', 'mainfont=SimSun',
            '--variable', 'CJKmainfont=SimSun',
            '-o', str(chapter_tex)
        ]
        
        try:
            result = subprocess.run(pandoc_cmd, capture_output=True, text=True, 
                                  check=True, cwd=self.output_dir)
            print(f"  ✅ LaTeX转换成功: {chapter_tex}")
            return str(chapter_tex)
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ LaTeX转换失败: {e}")
            print(f"  错误输出: {e.stderr}")
            raise
    
    def compile_chapter_pdf(self, chapter_id: str) -> str:
        """编译章节PDF"""
        chapter_tex = self.chapter_output_dir / f"{chapter_id}.tex"
        chapter_pdf = self.chapter_output_dir / f"{chapter_id}.pdf"
        
        if not chapter_tex.exists():
            raise FileNotFoundError(f"章节LaTeX文件不存在: {chapter_tex}")
        
        # 切换到章节输出目录
        original_dir = os.getcwd()
        os.chdir(self.chapter_output_dir)
        
        try:
            # 编译PDF
            for i in range(2):  # 编译两次处理交叉引用
                cmd = ['xelatex', '-interaction=nonstopmode', f"{chapter_id}.tex"]
                env = os.environ.copy()
                env['LC_ALL'] = 'C.UTF-8'
                
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      encoding='utf-8', errors='ignore', env=env)
                
                if result.returncode != 0:
                    print(f"  ⚠️  编译警告（第{i+1}次）")
                    if i == 1:  # 最后一次检查是否生成了PDF
                        if chapter_pdf.exists():
                            print(f"  ✅ PDF已生成（有警告）: {chapter_pdf}")
                            return str(chapter_pdf)
                        else:
                            print(f"  ❌ PDF编译失败")
                            if result.stderr:
                                print(f"  错误: {result.stderr[-500:]}")
                            raise subprocess.CalledProcessError(result.returncode, cmd)
                else:
                    print(f"  ✅ 编译成功（第{i+1}次）")
            
            if chapter_pdf.exists():
                size_kb = chapter_pdf.stat().st_size // 1024
                print(f"  ✅ PDF生成成功: {chapter_pdf} ({size_kb} KB)")
                return str(chapter_pdf)
            else:
                raise FileNotFoundError("PDF文件未生成")
                
        finally:
            os.chdir(original_dir)
    
    def create_chapter_template(self) -> str:
        """创建章节LaTeX模板"""
        template = r"""
\documentclass[12pt,a4paper]{article}

% 基础包
\usepackage[UTF8]{ctex}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{listings}
\usepackage{fontawesome5}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{hyperref}

% 修复Pandoc缺失的命令
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 页面设置
\geometry{
    top=2.5cm,
    bottom=2.5cm,
    left=2.8cm,
    right=2.2cm
}

% 代码高亮设置
\lstset{
    basicstyle=\ttfamily\footnotesize,
    backgroundcolor=\color{gray!8},
    frame=single,
    framesep=3pt,
    numbers=left,
    numberstyle=\tiny\color{gray!60},
    breaklines=true,
    showstringspaces=false,
    tabsize=2,
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{gray!70}\itshape,
    stringstyle=\color{red!80}
}

% 超链接设置
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=cyan
}

\begin{document}

% 正文内容
$body$

\end{document}
"""
        return template
    
    def list_available_chapters(self) -> None:
        """列出可用章节"""
        print("可用章节:")
        print("=" * 40)
        
        for i, (chapter_id, title) in enumerate(self.chapter_order.items(), 1):
            chapter_dir = self.source_dir / "chapters" / chapter_id
            status = "✅" if chapter_dir.exists() else "❌"
            print(f"{i:2d}. {chapter_id} - {title} {status}")
        
        print("=" * 40)

def main():
    """主函数"""
    converter = SingleChapterConverter()
    
    # 如果没有参数，显示帮助
    if len(sys.argv) < 2:
        print("单章节转换器 - 基于成功经验")
        print("=" * 50)
        converter.list_available_chapters()
        print("\n使用方法:")
        print("  python single_chapter_converter.py <chapter_id>")
        print("  python single_chapter_converter.py chapter01")
        print("\n或者:")
        print("  python single_chapter_converter.py all  # 处理所有章节")
        return
    
    chapter_arg = sys.argv[1].lower()
    
    if chapter_arg == 'all':
        # 处理所有章节
        results = []
        for chapter_id in converter.chapter_order.keys():
            try:
                result = converter.process_single_chapter(chapter_id)
                results.append(result)
            except Exception as e:
                print(f"章节 {chapter_id} 处理失败: {e}")
                continue
        
        print(f"\n处理完成！共处理 {len(results)} 个章节")
        
    else:
        # 处理单个章节
        if chapter_arg not in converter.chapter_order:
            print(f"错误：未知章节 {chapter_arg}")
            converter.list_available_chapters()
            return
        
        try:
            result = converter.process_single_chapter(chapter_arg)
            print(f"\n章节 {chapter_arg} 处理完成！")
            
        except Exception as e:
            print(f"章节 {chapter_arg} 处理失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()