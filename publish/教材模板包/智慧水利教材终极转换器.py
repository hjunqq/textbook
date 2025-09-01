#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材终极转换脚本
专门针对智慧水利平台架构与开发教材的完整转换解决方案
解决章节编号、图片路径、格式转换等问题

版本: v1.0 Final
作者: AI Assistant
日期: 2025年8月31日
"""

import os
import sys
import subprocess
import glob
import shutil
import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class SmartWaterTextbookConverter:
    """智慧水利教材专用转换器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
 # 代码高亮设置
\lstdefinelanguage{JavaScript}{
  keywords={break, case, catch, continue, debugger, default, delete, do, else, finally, for, function, if, in, instanceof, new, return, switch, this, throw, try, typeof, var, void, while, with, let, const, class, extends, export, import},
  morecomment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]',
  morestring=[b]",
  sensitive=true
}

\lstdefinelanguage{CSS}{
  keywords={color, background-color, font-size, font-family, margin, padding, border, width, height, display, position},
  morecomment=[s]{/*}{*/},
  morestring=[b]",
  morestring=[b]',
  sensitive=true
}

\lstdefinelanguage{YAML}{
  keywords={true, false, null, True, False, Null},
  comment=[l]{\#},
  morestring=[b]",
  morestring=[b]',
  sensitive=true
}

\lstdefinelanguage{HTML}{
  keywords={html, head, body, div, span, p, a, img, ul, ol, li, table, tr, td, th},
  morecomment=[s]{<!--}{-->},
  morestring=[b]",
  morestring=[b]',
  sensitive=false
}

\lstset{脚本所在目录并找到项目根目录
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent  # 向上两级到项目根目录
        self.source_dir = self.project_root / "docs"
        self.output_dir = self.project_root / "publish" / "latex_output"
        self.images_dir = self.output_dir / "images"
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 章节顺序映射
        self.chapter_order = {
            'chapter01': {'title': '第一章 智慧水利概述与平台架构基础', 'sections': []},
            'chapter02': {'title': '第二章 软件工程基础与需求分析', 'sections': []},
            'chapter03': {'title': '第三章 软件模块详细设计', 'sections': []},
            'chapter04': {'title': '第四章 系统开发技术基础', 'sections': []},
            'chapter05': {'title': '第五章 数据库设计与实现', 'sections': []},
            'chapter06': {'title': '第六章 前端开发技术', 'sections': []},
            'chapter07': {'title': '第七章 系统集成与测试', 'sections': []},
            'chapter08': {'title': '第八章 系统优化与维护', 'sections': []},
            'chapter09': {'title': '第九章 项目实战与案例分析', 'sections': []}
        }
        
        # 图片处理
        self.image_counter = 1
        self.image_mapping = {}
        
        # LaTeX特殊字符转义
        self.latex_escape_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '\\': r'\textbackslash{}'
        }
        
        # Emoji到LaTeX的映射
        self.emoji_mapping = {
            '📚': r'\faBook',
            '🎯': r'\faTarget',
            '💡': r'\faLightbulb',
            '🔧': r'\faWrench',
            '⚙️': r'\faCog',
            '🔍': r'\faSearch',
            '📝': r'\faEdit',
            '✅': r'\faCheck',
            '❌': r'\faTimes',
            '⚠️': r'\faExclamationTriangle'
        }
        
        print("智慧水利教材转换器初始化完成")
        
    def load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "title": "智慧水利平台架构与开发",
            "author": "教材编写组",
            "latex_engine": "xelatex",
            "template": "智慧水利Pandoc模板.tex",
            "output_formats": ["pdf", "tex"],
            "preprocessing": {
                "fix_encoding": True,
                "standardize_chapters": True,
                "unify_image_paths": True,
                "fix_code_blocks": True,
                "remove_emojis": False,
                "convert_special_blocks": True
            },
            "image_settings": {
                "max_width": "0.8\\textwidth",
                "default_caption": True,
                "numbering": True
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"警告：配置文件读取失败，使用默认配置：{e}")
                
        return default_config
    
    def discover_chapters(self) -> List[str]:
        """发现并排序章节文件"""
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
            
        # 添加附录
        appendix_dir = self.project_root / "appendix"
        if appendix_dir.exists():
            appendix_files = sorted(appendix_dir.glob("*.md"))
            chapter_files.extend(str(f) for f in appendix_files)
            
        print(f"发现 {len(chapter_files)} 个章节文件")
        return chapter_files
    
    def preprocess_markdown(self, content: str, file_path: str) -> str:
        """预处理Markdown内容"""
        
        # 1. 修复编码问题
        if self.config["preprocessing"]["fix_encoding"]:
            content = self.fix_encoding(content)
            
        # 2. 标准化章节编号
        if self.config["preprocessing"]["standardize_chapters"]:
            content = self.standardize_chapters(content, file_path)
            
        # 3. 统一图片路径
        if self.config["preprocessing"]["unify_image_paths"]:
            content = self.unify_image_paths(content, file_path)
            
        # 4. 修复代码块
        if self.config["preprocessing"]["fix_code_blocks"]:
            content = self.fix_code_blocks(content)
            
        # 5. 处理Emoji
        if self.config["preprocessing"]["remove_emojis"]:
            content = self.convert_emojis(content)
            
        # 6. 转换特殊块
        if self.config["preprocessing"]["convert_special_blocks"]:
            content = self.convert_special_blocks(content)
            
        return content
    
    def fix_encoding(self, content: str) -> str:
        """修复编码问题"""
        # 移除BOM
        if content.startswith('\ufeff'):
            content = content[1:]
            
        # 标准化换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 简单的编码检测和修复
        try:
            # 尝试重新编码以确保正确性
            content.encode('utf-8')
        except UnicodeEncodeError:
            # 如果编码有问题，尝试修复常见的编码错误
            content = content.encode('utf-8', errors='ignore').decode('utf-8')
            
        return content
    
    def standardize_chapters(self, content: str, file_path: str) -> str:
        """标准化章节编号"""
        file_name = Path(file_path).name
        
        # 处理章节主文件的标题
        if file_name.startswith('chapter') and file_name.endswith('.md'):
            chapter_num = re.search(r'chapter(\d+)', file_name)
            if chapter_num:
                chapter_key = f"chapter{chapter_num.group(1).zfill(2)}"
                if chapter_key in self.chapter_order:
                    title = self.chapter_order[chapter_key]['title']
                    # 确保章节标题使用正确的格式（不带前导0）
                    clean_chapter_num = int(chapter_num.group(1))
                    clean_title = title.replace(f'第{chapter_num.group(1).zfill(2)}章', f'第{clean_chapter_num}章')
                    content = re.sub(r'^#\s+.*', f'# {clean_title}', content, count=1, flags=re.MULTILINE)
                    
        # 处理节文件的标题
        if file_name.startswith('section'):
            section_match = re.search(r'section(\d+)-(\d+)', file_name)
            if section_match:
                chapter_num = int(section_match.group(1))  # 去掉前导0
                section_num = int(section_match.group(2))  # 去掉前导0
                # 将二级标题转换为正确的节标题格式
                content = re.sub(r'^##\s+(.+)', f'## {chapter_num}.{section_num} \\1', content, count=1, flags=re.MULTILINE)
        
        # 过滤掉不必要的目录内容
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
        """统一图片路径并复制图片"""
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
                    self.source_dir / Path(image_path),  # docs目录下的相对路径
                    source_dir / "images" / Path(image_path).name,  # 章节目录下的images
                    self.project_root / "参考" / "extracted_images_ch6" / Path(image_path).name,
                    self.project_root / "参考" / "images" / Path(image_path).name,
                    # 支持chapter06特殊的images目录
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
                    
                    # 返回新的Markdown图片语法
                    if self.config["image_settings"]["numbering"]:
                        return f"![{alt_text}](images/{new_filename})"
                    else:
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
    
    def fix_code_blocks(self, content: str) -> str:
        """修复代码块格式"""
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
                        next_lines = lines[lines.index(line)+1:lines.index(line)+5]
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
    
    def convert_emojis(self, content: str) -> str:
        """转换Emoji为LaTeX命令"""
        for emoji, latex_cmd in self.emoji_mapping.items():
            content = content.replace(emoji, latex_cmd)
        return content
    
    def convert_special_blocks(self, content: str) -> str:
        """转换特殊块语法"""
        
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
        
        # 处理带标题的tip块
        content = re.sub(
            r'!!! tip "([^"]+)"\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=green!5, colframe=green!40, title=\\faLightbulb\\ \\1]\n\\2\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理不带标题的tip块
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
        
        # 处理不带标题的warning块
        content = re.sub(
            r'!!! warning\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=orange!5, colframe=orange!60, title=\\faExclamationTriangle\\ 警告]\n\\1\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理info块
        content = re.sub(
            r'!!! info "([^"]+)"\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=cyan!5, colframe=cyan!40, title=\\faInfoCircle\\ \\1]\n\\2\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理不带标题的info块
        content = re.sub(
            r'!!! info\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=cyan!5, colframe=cyan!40, title=\\faInfoCircle\\ 信息]\n\\1\\end{tcolorbox}\n',
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
        
        # 处理不带标题的important块
        content = re.sub(
            r'!!! important\s*\n((?:    .*\n)*)',
            r'\\begin{tcolorbox}[colback=red!5, colframe=red!60, title=\\faExclamation\\ 重要]\n\\1\\end{tcolorbox}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 清理tcolorbox内容中的多余缩进 - 简化版本
        content = re.sub(r'^    ', '', content, flags=re.MULTILINE)
        
        return content
    
    def filter_unnecessary_content(self, content: str) -> str:
        """过滤不必要的内容，避免出现在目录中"""
        
        # 删除整个不必要的章节
        patterns_to_remove = [
            r'##\s+本章小结.*?(?=\n##|\n#|\Z)',
            r'##\s+重点难点.*?(?=\n##|\n#|\Z)',
            r'##\s+思考题与练习.*?(?=\n##|\n#|\Z)',
            r'##\s+本节小结.*?(?=\n##|\n#|\Z)',
            r'##\s+参考文献.*?(?=\n##|\n#|\Z)',
            r'##\s+配套资源.*?(?=\n##|\n#|\Z)',
            r'##\s+许可证.*?(?=\n##|\n#|\Z)',
            r'##\s+联系方式.*?(?=\n##|\n#|\Z)',
            r'##\s+技术支持.*?(?=\n##|\n#|\Z)',
            r'##\s+软件.*?(?=\n##|\n#|\Z)',
            r'##\s+版权声明.*?(?=\n##|\n#|\Z)',
            r'##\s+编写背景.*?(?=\n##|\n#|\Z)',
            r'##\s+编写目标.*?(?=\n##|\n#|\Z)',
            r'##\s+适用对象.*?(?=\n##|\n#|\Z)',
            r'##\s+主要特色.*?(?=\n##|\n#|\Z)',
            r'##\s+内容结构.*?(?=\n##|\n#|\Z)',
            r'##\s+使用建议.*?(?=\n##|\n#|\Z)',
            r'##\s+贡献指南.*?(?=\n##|\n#|\Z)',
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
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
                # 过滤不需要的章节内容
                processed_content = self.filter_unnecessary_content(processed_content)
                merged_content.append(processed_content)
                merged_content.append('\n\n\\newpage\n\n')  # 添加分页
                
            except Exception as e:
                print(f"错误：处理文件失败 {file_path}: {e}")
                continue
        
        return '\n'.join(merged_content)
    
    def create_latex_template(self) -> str:
        """创建LaTeX模板"""
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
\setcounter{tocdepth}{2}  % 只显示到小节级别

% 自定义目录格式
\titlecontents{chapter}[0em]
    {\addvspace{1.5em}\large\bfseries}
    {\contentspush{\thecontentslabel\quad}}
    {}
    {\titlerule*[.6em]{.}\contentspage}

\titlecontents{section}[2em]
    {}
    {\contentspush{\thecontentslabel\quad}}
    {}
    {\titlerule*[.6em]{.}\contentspage}

\begin{document}

% 封面
\title{智慧水利平台架构与开发}
\author{教材编写组}
\date{\today}
\maketitle

% 目录
\tableofcontents
\cleardoublepage  % 确保目录后开始新的右页

% 正文内容
$body$

\end{document}
"""
        return template
    
    def convert_to_latex(self, merged_content: str) -> str:
        """使用Pandoc转换为LaTeX"""
        # 创建临时Markdown文件
        temp_md = self.output_dir / "temp_merged.md"
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        # 创建模板文件
        template_path = self.output_dir / "template.tex"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(self.create_latex_template())
        
        # 执行Pandoc转换 - 只转换为LaTeX，禁用语法高亮
        output_tex = self.output_dir / "教材.tex"
        
        pandoc_cmd = [
            'pandoc',
            str(temp_md),
            '--template', str(template_path),
            '--to', 'latex',  # 明确指定输出为LaTeX
            '--no-highlight',  # 禁用Pandoc的语法高亮
            '--toc',
            '--number-sections',
            '--variable', 'geometry:margin=2.5cm',
            '--variable', 'fontsize=12pt',
            '--variable', 'mainfont=SimSun',
            '--variable', 'CJKmainfont=SimSun',
            '-o', str(output_tex)
        ]
        
        try:
            result = subprocess.run(pandoc_cmd, capture_output=True, text=True, check=True)
            print("Pandoc转换成功")
            
            # 后处理LaTeX文件
            with open(output_tex, 'r', encoding='utf-8') as f:
                latex_content = f.read()
                
            latex_content = self.postprocess_latex(latex_content)
            
            with open(output_tex, 'w', encoding='utf-8') as f:
                f.write(latex_content)
                
            return str(output_tex)
            
        except subprocess.CalledProcessError as e:
            print(f"Pandoc转换失败: {e}")
            print(f"错误输出: {e.stderr}")
            raise
        finally:
            # 清理临时文件
            if temp_md.exists():
                temp_md.unlink()
    
    def postprocess_latex(self, content: str) -> str:
        """后处理LaTeX内容"""
        
        # 修复图片引用
        content = re.sub(
            r'\\includegraphics\{images/([^}]+)\}',
            r'\\includegraphics[width=0.8\\textwidth]{images/\\1}',
            content
        )
        
        # 将Pandoc生成的verbatim代码块转换为listings环境
        def replace_code_block(match):
            code_content = match.group(1)
            # 检测代码语言（简单的启发式方法）
            language = self.detect_latex_code_language(code_content)
            
            # 转义LaTeX特殊字符
            code_content = self.escape_listings_content(code_content)
            
            return f'\\begin{{lstlisting}}[language={language}]\n{code_content}\n\\end{{lstlisting}}'
        
        # 替换verbatim环境为listings
        content = re.sub(
            r'\\begin\{verbatim\}(.*?)\\end\{verbatim\}',
            replace_code_block,
            content,
            flags=re.DOTALL
        )
        
        # 处理可能的Shaded环境（Pandoc生成的代码块环境）
        content = re.sub(
            r'\\begin\{Shaded\}.*?\\begin\{Highlighting\}\[\](.*?)\\end\{Highlighting\}.*?\\end\{Shaded\}',
            lambda m: self.clean_highlighted_code(m.group(1)),
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def detect_latex_code_language(self, code_block: str) -> str:
        """从代码块内容检测编程语言"""
        # 常见的语言关键字模式
        language_patterns = {
            'Python': [r'\bdef\b', r'\bimport\b', r'\bfrom\b', r'\bclass\b', r'#.*$', r'\.py\b'],
            'Java': [r'\bpublic\b', r'\bprivate\b', r'\bclass\b', r'\bstatic\b', r'//.*$', r'\.java\b'],
            'JavaScript': [r'\bfunction\b', r'\bvar\b', r'\blet\b', r'\bconst\b', r'//.*$', r'\.js\b', r'=>', r'\bconsole\.log\b'],
            'C++': [r'#include', r'\busing\s+namespace\b', r'\bstd::', r'//.*$', r'\.cpp\b', r'\.h\b'],
            'C': [r'#include', r'\bmain\s*\(', r'printf\s*\(', r'//.*$', r'\.c\b'],
            'HTML': [r'<[^>]+>', r'<!DOCTYPE', r'<html', r'<body', r'<div'],
            'CSS': [r'[.#][a-zA-Z][a-zA-Z0-9_-]*\s*{', r'[a-zA-Z-]+\s*:', r'/\*.*?\*/'],
            'SQL': [r'\bSELECT\b', r'\bFROM\b', r'\bWHERE\b', r'\bINSERT\b', r'\bUPDATE\b'],
            'JSON': [r'^\s*[\{\[]', r':\s*["\[\{]', r'^\s*"[^"]+"\s*:'],
            'XML': [r'<\?xml', r'<[^>]+>[^<]*</[^>]+>'],
            'Bash': [r'#!/bin/bash', r'\$[A-Za-z_][A-Za-z0-9_]*', r'echo\s+', r'grep\s+'],
            'YAML': [r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:', r'^\s*-\s+', r'---\s*$']
        }
        
        # 统计每种语言的匹配度
        scores = {}
        for lang, patterns in language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, code_block, re.MULTILINE | re.IGNORECASE))
                score += matches
            scores[lang] = score
        
        # 返回得分最高的语言，如果没有明确的模式则返回Python
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'Python'
    
    def escape_listings_content(self, content: str) -> str:
        """转义listings环境中的特殊字符"""
        # listings环境中需要转义的字符
        content = content.replace('\\', '\\textbackslash{}')
        content = content.replace('^', '\\textasciicircum{}')
        content = content.replace('~', '\\textasciitilde{}')
        content = content.replace('%', '\\%')
        content = content.replace('&', '\\&')
        content = content.replace('$', '\\$')
        content = content.replace('#', '\\#')
        content = content.replace('_', '\\_')
        content = content.replace('{', '\\{')
        content = content.replace('}', '\\}')
        return content
    
    def clean_highlighted_code(self, code_content: str) -> str:
        """清理复杂的高亮代码，转换为简单的listings格式"""
        # 移除所有高亮命令
        patterns_to_remove = [
            r'\\KeywordTok\{([^}]*)\}',  # 关键字
            r'\\StringTok\{([^}]*)\}',   # 字符串
            r'\\CommentTok\{([^}]*)\}',  # 注释
            r'\\NormalTok\{([^}]*)\}',   # 普通文本
            r'\\OperatorTok\{([^}]*)\}', # 操作符
            r'\\DecValTok\{([^}]*)\}',   # 数字
            r'\\BaseNTok\{([^}]*)\}',    # 基础数字
            r'\\FloatTok\{([^}]*)\}',    # 浮点数
            r'\\CharTok\{([^}]*)\}',     # 字符
            r'\\SpecialCharTok\{([^}]*)\}', # 特殊字符
            r'\\VerbatimStringTok\{([^}]*)\}', # 原样字符串
            r'\\SpecialStringTok\{([^}]*)\}',  # 特殊字符串
            r'\\ImportTok\{([^}]*)\}',   # 导入
            r'\\DataTypeTok\{([^}]*)\}', # 数据类型
            r'\\BuiltInTok\{([^}]*)\}',  # 内置函数
            r'\\ExtensionTok\{([^}]*)\}', # 扩展
            r'\\PreprocessorTok\{([^}]*)\}', # 预处理器
            r'\\AttributeTok\{([^}]*)\}', # 属性
            r'\\RegionMarkerTok\{([^}]*)\}', # 区域标记
            r'\\InformationTok\{([^}]*)\}',  # 信息
            r'\\WarningTok\{([^}]*)\}',  # 警告
            r'\\AlertTok\{([^}]*)\}',    # 警报
            r'\\ErrorTok\{([^}]*)\}',    # 错误
            r'\\FunctionTok\{([^}]*)\}', # 函数
            r'\\VariableTok\{([^}]*)\}', # 变量
            r'\\ControlFlowTok\{([^}]*)\}' # 控制流
        ]
        
        cleaned_content = code_content
        for pattern in patterns_to_remove:
            cleaned_content = re.sub(pattern, r'\1', cleaned_content)
        
        # 检测语言
        language = self.detect_latex_code_language(cleaned_content)
        
        # 清理多余的空行和空格
        lines = cleaned_content.split('\n')
        lines = [line.rstrip() for line in lines]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        cleaned_content = '\n'.join(lines)
        
        # 构建简单的listings环境
        listings_code = f"""\\begin{{lstlisting}}[language={language}]
{cleaned_content}
\\end{{lstlisting}}"""
        
        return listings_code

    def compile_pdf(self, tex_file: str) -> str:
        """编译PDF"""
        tex_path = Path(tex_file)
        output_dir = tex_path.parent
        
        # 切换到输出目录
        original_dir = os.getcwd()
        os.chdir(output_dir)
        
        try:
            # 多次编译以处理交叉引用
            for i in range(3):
                cmd = [self.config['latex_engine'], '-interaction=nonstopmode', tex_path.name]
                # 设置环境变量确保UTF-8编码
                env = os.environ.copy()
                env['LC_ALL'] = 'C.UTF-8'
                
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      encoding='utf-8', errors='ignore', env=env)
                
                if result.returncode != 0:
                    print(f"LaTeX编译失败（第{i+1}次）:")
                    if result.stdout:
                        print("标准输出:", result.stdout[-1000:])  # 只显示最后1000字符
                    if result.stderr:
                        print("错误输出:", result.stderr[-1000:])
                    
                    if i == 2:  # 最后一次尝试
                        # 检查PDF是否生成了（有时即使报错也能生成PDF）
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
    
    def generate_statistics(self, chapter_files: List[str]) -> Dict:
        """生成转换统计信息"""
        stats = {
            'total_files': len(chapter_files),
            'total_chapters': 0,
            'total_sections': 0,
            'total_images': len(self.image_mapping),
            'total_code_blocks': 0,
            'image_mapping': self.image_mapping
        }
        
        for file_path in chapter_files:
            filename = Path(file_path).name
            if filename.startswith('chapter'):
                stats['total_chapters'] += 1
            elif filename.startswith('section'):
                stats['total_sections'] += 1
                
        return stats
    
    def run_conversion(self) -> None:
        """执行完整转换流程"""
        print("=" * 60)
        print("智慧水利教材转换器 v1.0")
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
            if 'pdf' in self.config['output_formats']:
                print("\n4. 编译PDF...")
                pdf_file = self.compile_pdf(tex_file)
            
            # 5. 生成统计信息
            print("\n5. 生成统计信息...")
            stats = self.generate_statistics(chapter_files)
            
            print("\n" + "=" * 60)
            print("转换完成！")
            print("=" * 60)
            print(f"输出目录: {self.output_dir}")
            print(f"处理文件: {stats['total_files']} 个")
            print(f"章节数量: {stats['total_chapters']} 个")
            print(f"节数量: {stats['total_sections']} 个")
            print(f"图片数量: {stats['total_images']} 个")
            
            # 保存统计信息
            stats_file = self.output_dir / "conversion_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"\n错误：转换失败: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智慧水利教材转换器')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--output', '-o', type=str, help='输出目录')
    
    args = parser.parse_args()
    
    # 创建转换器实例
    converter = SmartWaterTextbookConverter(args.config)
    
    # 如果指定了输出目录，更新配置
    if args.output:
        converter.output_dir = Path(args.output)
        converter.images_dir = converter.output_dir / "images"
        converter.output_dir.mkdir(parents=True, exist_ok=True)
        converter.images_dir.mkdir(parents=True, exist_ok=True)
    
    # 执行转换
    converter.run_conversion()


if __name__ == '__main__':
    main()
