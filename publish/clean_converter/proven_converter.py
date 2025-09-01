#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于成功经验的智慧水利教材转换器
吸收原终极转换器的核心解决方案
"""

import os
import sys
import subprocess
import shutil
import re
import json
from pathlib import Path
from typing import List, Dict, Optional

class WaterTextbookConverter:
    """基于成功经验的转换器"""
    
    def __init__(self):
        # 获取项目路径
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent  # 向上两级到项目根目录
        self.source_dir = self.project_root / "docs"
        self.output_dir = script_dir / "output"
        self.images_dir = self.output_dir / "images"
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 章节顺序 - 与成功版本完全一致
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
        
        # 图片处理
        self.image_counter = 1
        self.image_mapping = {}
        
        print("智慧水利教材转换器初始化完成")
    
    def discover_chapters(self) -> List[str]:
        """发现并排序章节文件 - 完全沿用成功版本的逻辑"""
        chapters_dir = self.source_dir / "chapters"
        if not chapters_dir.exists():
            raise FileNotFoundError(f"章节目录不存在: {chapters_dir}")
            
        chapter_files = []
        
        # 添加前言
        preface_file = self.source_dir / "前言.md"
        if preface_file.exists():
            chapter_files.append(str(preface_file))
            
        # 按顺序添加章节
        for chapter_key in self.chapter_order.keys():
            chapter_dir = chapters_dir / chapter_key
            if not chapter_dir.exists():
                continue
                
            # 添加章节主文件
            main_file = chapter_dir / f"{chapter_key}.md"
            if main_file.exists():
                chapter_files.append(str(main_file))
                
            # 添加节文件
            section_files = sorted(chapter_dir.glob("section*.md"))
            chapter_files.extend(str(f) for f in section_files)
            
        print(f"发现 {len(chapter_files)} 个章节文件")
        return chapter_files
    
    def standardize_chapters(self, content: str, file_path: str) -> str:
        """标准化章节编号 - 沿用成功版本的核心逻辑"""
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
                    
        # 处理节文件的标题 - 移除原有编号，让Pandoc自动编号
        if file_name.startswith('section'):
            section_match = re.search(r'section(\d+)-(\d+)', file_name)
            if section_match:
                # 移除原有的数字编号，只保留标题文本
                content = re.sub(r'^##\s+\d+\.\d+\s+(.+)', r'## \1', content, count=1, flags=re.MULTILINE)
                content = re.sub(r'^###\s+\d+\.\d+\.\d+\s+(.+)', r'### \1', content, flags=re.MULTILINE)
                content = re.sub(r'^####\s+\d+\.\d+\.\d+\.\d+\s+(.+)', r'#### \1', content, flags=re.MULTILINE)
        
        # 在所有文件中移除手工编号，避免与Pandoc自动编号重复
        content = re.sub(r'^##\s+\d+\.\d+\s+(.+)', r'## \1', content, flags=re.MULTILINE)  # 二级标题
        content = re.sub(r'^###\s+\d+\.\d+\.\d+\s+(.+)', r'### \1', content, flags=re.MULTILINE)  # 三级标题
        content = re.sub(r'^####\s+\d+\.\d+\.\d+\.\d+\s+(.+)', r'#### \1', content, flags=re.MULTILINE)  # 四级标题
        
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
    
    def unify_image_paths(self, content: str, file_path: str) -> str:
        """统一图片路径 - 完全沿用成功版本的策略"""
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
                # 尝试在其他可能的位置查找 - 完全沿用成功版本的搜索策略
                possible_paths = [
                    self.source_dir / "assets" / "images" / Path(image_path).name,
                    self.source_dir / Path(image_path),
                    source_dir / "images" / Path(image_path).name,
                    self.source_dir / "chapters" / "images" / Path(image_path).name,
                    self.source_dir / "chapters" / "chapter06" / "images" / Path(image_path).name
                ]
                
                for possible_path in possible_paths:
                    if possible_path.exists():
                        full_image_path = possible_path
                        break
            
            if full_image_path.exists():
                # 生成新的文件名
                file_ext = full_image_path.suffix
                new_filename = f"image_{self.image_counter:03d}{file_ext}"
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
        """检测代码语言 - 沿用成功版本的逻辑"""
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
        """修复代码块格式 - 沿用成功版本的逻辑"""
        lines = content.split('\n')
        in_code_block = False
        fixed_lines = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if not in_code_block:
                    # 开始代码块
                    in_code_block = True
                    # 如果没有指定语言，尝试推断
                    if line.strip() == '```':
                        # 查看下几行来推断语言
                        current_idx = lines.index(line)
                        next_lines = lines[current_idx+1:current_idx+5]
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
    
    def convert_special_blocks(self, content: str) -> str:
        """转换!!! 特殊块语法 - 完全沿用成功版本的处理"""
        
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
    
    def preprocess_markdown(self, content: str, file_path: str) -> str:
        """预处理Markdown内容 - 按照成功版本的顺序"""
        
        # 1. 修复编码问题
        if content.startswith('\ufeff'):
            content = content[1:]
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 2. 标准化章节编号
        content = self.standardize_chapters(content, file_path)
        
        # 3. 统一图片路径
        content = self.unify_image_paths(content, file_path)
        
        # 4. 修复代码块
        content = self.fix_code_blocks(content)
        
        # 5. 转换特殊块
        content = self.convert_special_blocks(content)
        
        return content
    
    def merge_chapters(self, chapter_files: List[str]) -> str:
        """合并所有章节文件"""
        merged_content = []
        
        for file_path in chapter_files:
            print(f"处理文件: {Path(file_path).name}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                processed_content = self.preprocess_markdown(content, file_path)
                merged_content.append(processed_content)
                merged_content.append('\n\n\\newpage\n\n')  # 添加分页
                
            except Exception as e:
                print(f"错误：处理文件失败 {file_path}: {e}")
                continue
        
        return '\n'.join(merged_content)
    
    def create_latex_template(self) -> str:
        """创建LaTeX模板 - 沿用成功版本的模板"""
        template = r"""
\documentclass[12pt,a4paper,openright]{book}

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
\usepackage{fancyhdr}
\usepackage{titletoc}

% 修复Pandoc缺失的命令
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 页面设置
\geometry{
    top=2.5cm,
    bottom=2.5cm,
    left=2.8cm,
    right=2.2cm,
    bindingoffset=0.5cm
}

% 修复页眉高度警告
\setlength{\headheight}{14.5pt}

% 代码高亮设置
\lstdefinelanguage{JavaScript}{
  keywords={break, case, catch, continue, debugger, default, delete, do, else, finally, for, function, if, in, instanceof, new, return, switch, this, throw, try, typeof, var, void, while, with, let, const, class, extends, export, import},
  morecomment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]',
  morestring=[b]",
  sensitive=true
}

\lstset{
    basicstyle=\ttfamily\scriptsize,
    backgroundcolor=\color{gray!8},
    frame=single,
    framesep=3pt,
    framexleftmargin=3pt,
    framexrightmargin=3pt,
    numbers=left,
    numberstyle=\tiny\color{gray!60},
    stepnumber=1,
    numbersep=5pt,
    breaklines=true,
    showstringspaces=false,
    tabsize=2,
    captionpos=b,
    belowcaptionskip=5pt,
    aboveskip=8pt,
    belowskip=8pt,
    xleftmargin=8pt,
    xrightmargin=8pt,
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{gray!70}\itshape,
    stringstyle=\color{red!80},
    identifierstyle=\color{black},
    emphstyle=\color{blue}\underbar
}

% 页眉页脚
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[CE]{智慧水利平台架构与开发}
\fancyhead[CO]{\leftmark}

% 超链接设置
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=cyan,
    pdftitle={智慧水利平台架构与开发},
    pdfauthor={教材编写组}
}

% 目录设置
\setcounter{tocdepth}{2}

\begin{document}

% 封面
\title{智慧水利平台架构与开发}
\author{教材编写组}
\date{\today}
\maketitle

% 目录
\tableofcontents
\cleardoublepage

% 正文内容
$body$

\end{document}
"""
        return template
    
    def convert_to_latex(self, merged_content: str) -> str:
        """转换为LaTeX - 沿用成功版本的Pandoc命令"""
        # 创建临时Markdown文件
        temp_md = self.output_dir / "textbook_merged.md"
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        # 创建模板文件
        template_path = self.output_dir / "template.tex"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(self.create_latex_template())
        
        # 执行Pandoc转换
        output_tex = self.output_dir / "textbook.tex"
        
        pandoc_cmd = [
            'pandoc',
            str(temp_md),
            '--template', str(template_path),
            '--to', 'latex',
            '--no-highlight',
            '--toc',
            '--number-sections',
            '--variable', 'geometry:margin=2.5cm',
            '--variable', 'fontsize=12pt',
            '--variable', 'mainfont=SimSun',
            '--variable', 'CJKmainfont=SimSun',
            '-o', str(output_tex)
        ]
        
        try:
            result = subprocess.run(pandoc_cmd, capture_output=True, text=True, 
                                  check=True, cwd=self.output_dir)
            print("Pandoc转换成功")
            return str(output_tex)
            
        except subprocess.CalledProcessError as e:
            print(f"Pandoc转换失败: {e}")
            print(f"错误输出: {e.stderr}")
            raise
    
    def compile_pdf(self, tex_file: str) -> str:
        """编译PDF - 沿用成功版本的编译策略"""
        tex_path = Path(tex_file)
        
        # 切换到输出目录
        original_dir = os.getcwd()
        os.chdir(self.output_dir)
        
        try:
            # 多次编译以处理交叉引用
            for i in range(3):
                cmd = ['xelatex', '-interaction=nonstopmode', tex_path.name]
                env = os.environ.copy()
                env['LC_ALL'] = 'C.UTF-8'
                
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      encoding='utf-8', errors='ignore', env=env)
                
                if result.returncode != 0:
                    print(f"LaTeX编译失败（第{i+1}次）:")
                    if result.stdout:
                        print("标准输出:", result.stdout[-1000:])
                    if result.stderr:
                        print("错误输出:", result.stderr[-1000:])
                    
                    if i == 2:  # 最后一次尝试
                        pdf_file = tex_path.with_suffix('.pdf')
                        if pdf_file.exists():
                            print(f"虽然有警告，但PDF已生成: {pdf_file}")
                            return str(pdf_file)
                        else:
                            raise subprocess.CalledProcessError(result.returncode, cmd)
                else:
                    print(f"LaTeX编译成功（第{i+1}次）")
                    
            pdf_file = tex_path.with_suffix('.pdf')
            if pdf_file.exists():
                print(f"PDF生成成功: {pdf_file}")
                return str(pdf_file)
            else:
                raise FileNotFoundError("PDF文件未生成")
                
        finally:
            os.chdir(original_dir)
    
    def run_conversion(self) -> None:
        """执行完整转换流程"""
        print("=" * 60)
        print("基于成功经验的智慧水利教材转换器")
        print("=" * 60)
        
        try:
            # 1. 发现章节文件
            print("\n1. 发现章节文件...")
            chapter_files = self.discover_chapters()
            
            # 2. 合并和预处理
            print("\n2. 合并和预处理...")
            merged_content = self.merge_chapters(chapter_files)
            
            # 3. 转换为LaTeX
            print("\n3. 转换为LaTeX...")
            tex_file = self.convert_to_latex(merged_content)
            
            # 4. 编译PDF
            print("\n4. 编译PDF...")
            pdf_file = self.compile_pdf(tex_file)
            
            print("\n" + "=" * 60)
            print("转换完成！")
            print("=" * 60)
            print(f"输出目录: {self.output_dir}")
            print(f"LaTeX文件: {tex_file}")
            print(f"PDF文件: {pdf_file}")
            print(f"图片数量: {len(self.image_mapping)} 个")
            
        except Exception as e:
            print(f"\n错误：转换失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    converter = WaterTextbookConverter()
    converter.run_conversion()