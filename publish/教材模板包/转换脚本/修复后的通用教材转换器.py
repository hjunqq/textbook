#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的通用教材转换脚本
主要修复问题：
1. LaTeX文档结构问题 - 避免在章节文件中包含preamble命令
2. 缺失命令定义 - 确保所有必要命令都在主文档中定义
3. Emoji字符支持 - 自动移除或替换emoji字符
4. 图片路径统一 - 统一管理图片路径到images目录
5. 包依赖管理 - 确保所有必要的LaTeX包都正确加载

版本: v3.0 (修复版)
更新: 2025年8月27日
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

class FixedTextbookConverter:
    """修复后的教材转换主类"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.supported_formats = ['latex', 'pdf', 'docx', 'html']
        self.check_dependencies()
        # emoji字符映射表
        self.emoji_map = {
            '🌐': '在线',
            '📖': '阅读',
            '📱': '移动端',
            '🔍': '搜索',
            '📑': '导航',
            '💡': '亮点',
            '🎨': '设计',
            '🚀': '快速',
            '📚': '使用',
            '🤝': '贡献',
            '📄': '许可',
            '📞': '联系',
            '🛠️': '技术',
            '🙏': '致谢',
            '🐛': '错误',
            '📝': '完善',
            '📁': '本地',
            '🌟': '',
            '📧': '邮箱',
            '💬': '讨论',
            '⚡': '快速',
            '✅': '完成',
            '❌': '错误',
            '⚠️': '注意'
        }
    
    def load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "input_format": "markdown",
            "output_format": "latex", 
            "template_dir": "LaTeX模板",
            "output_dir": "输出",
            "source_encoding": "utf-8",
            "latex_engine": "xelatex",
            "pandoc_options": [
                "--toc",
                "--number-sections",
                "--standalone"
            ],
            "chapters": [],
            "preprocessing": {
                "fix_encoding": True,
                "standardize_format": True,
                "optimize_images": True,
                "fix_code_blocks": True,
                "remove_emojis": True
            },
            "postprocessing": {
                "optimize_latex": True,
                "fix_chinese_fonts": True,
                "add_listings_config": True,
                "beautify_layout": True,
                "fix_document_structure": True
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"警告：读取配置文件失败，使用默认配置：{e}")
        
        return default_config
    
    def check_dependencies(self):
        """检查依赖工具"""
        self.available_tools = {}
        
        # 检查pandoc
        try:
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.available_tools['pandoc'] = True
            print("✓ Pandoc 可用")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.available_tools['pandoc'] = False
            print("✗ Pandoc 不可用")
        
        # 检查LaTeX
        for engine in ['xelatex', 'pdflatex', 'lualatex']:
            try:
                result = subprocess.run([engine, '--version'], 
                                      capture_output=True, text=True, check=True)
                self.available_tools[engine] = True
                print(f"✓ {engine} 可用")
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.available_tools[engine] = False
        
        if not any(self.available_tools.get(engine, False) for engine in ['xelatex', 'pdflatex', 'lualatex']):
            print("✗ 未找到可用的LaTeX引擎")
    
    def discover_chapters(self, source_dir: str) -> List[str]:
        """自动发现章节文件"""
        markdown_files = []
        
        # 首先添加根目录的主要文件
        main_files = ['index.md', '前言.md', 'README.md']
        for filename in main_files:
            filepath = os.path.join(source_dir, filename)
            if os.path.exists(filepath):
                markdown_files.append(filepath)
        
        # 查找docs目录
        docs_dir = os.path.join(source_dir, 'docs')
        if os.path.exists(docs_dir):
            # 添加docs目录下的主文件
            for filename in ['前言.md', 'index.md']:
                filepath = os.path.join(docs_dir, filename)
                if os.path.exists(filepath):
                    markdown_files.append(filepath)
            
            # 查找chapters目录
            chapters_dir = os.path.join(docs_dir, 'chapters')
            if os.path.exists(chapters_dir):
                chapter_dirs = sorted(glob.glob(os.path.join(chapters_dir, "chapter*")))
                for chapter_dir in chapter_dirs:
                    if os.path.isdir(chapter_dir):
                        # 先添加主章节文件
                        chapter_name = os.path.basename(chapter_dir)
                        main_chapter_file = os.path.join(chapter_dir, f"{chapter_name}.md")
                        if os.path.exists(main_chapter_file):
                            markdown_files.append(main_chapter_file)
                        
                        # 再添加section文件
                        section_files = sorted(glob.glob(os.path.join(chapter_dir, "section*.md")))
                        markdown_files.extend(section_files)
        else:
            # 直接在源目录查找chapters
            chapters_dir = os.path.join(source_dir, 'chapters')
            if os.path.exists(chapters_dir):
                chapter_dirs = sorted(glob.glob(os.path.join(chapters_dir, "chapter*")))
                for chapter_dir in chapter_dirs:
                    if os.path.isdir(chapter_dir):
                        chapter_name = os.path.basename(chapter_dir)
                        main_chapter_file = os.path.join(chapter_dir, f"{chapter_name}.md")
                        if os.path.exists(main_chapter_file):
                            markdown_files.append(main_chapter_file)
                        
                        section_files = sorted(glob.glob(os.path.join(chapter_dir, "section*.md")))
                        markdown_files.extend(section_files)
        
        # 去除重复文件
        markdown_files = list(dict.fromkeys(markdown_files))
        
        return markdown_files
    
    def preprocess_markdown(self, input_files: List[str], temp_dir: str) -> List[str]:
        """预处理Markdown文件"""
        print("开始预处理Markdown文件...")
        
        os.makedirs(temp_dir, exist_ok=True)
        processed_files = []
        
        for input_file in input_files:
            print(f"处理文件：{input_file}")
            
            with open(input_file, 'r', encoding=self.config['source_encoding']) as f:
                content = f.read()
            
            # 移除emoji字符
            if self.config['preprocessing']['remove_emojis']:
                content = self.remove_emojis(content)
            
            # 标准化格式
            if self.config['preprocessing']['standardize_format']:
                content = self.standardize_markdown_format(content)
            
            # 修复代码块
            if self.config['preprocessing']['fix_code_blocks']:
                content = self.fix_code_blocks(content)
            
            # 优化图片引用
            if self.config['preprocessing']['optimize_images']:
                content = self.optimize_image_references(content, input_file)
            
            # 保存处理后的文件
            processed_file = os.path.join(temp_dir, os.path.basename(input_file))
            with open(processed_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            processed_files.append(processed_file)
        
        print(f"✓ 预处理完成，处理了 {len(processed_files)} 个文件")
        return processed_files
    
    def remove_emojis(self, content: str) -> str:
        """移除或替换emoji字符"""
        # 替换已知的emoji
        for emoji, replacement in self.emoji_map.items():
            if replacement:
                content = content.replace(emoji + ' ', replacement)
                content = content.replace(emoji, replacement)
            else:
                content = content.replace(emoji + ' ', '')
                content = content.replace(emoji, '')
        
        # 移除其他未知的emoji (Unicode范围)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        content = emoji_pattern.sub('', content)
        
        return content
    
    def standardize_markdown_format(self, content: str) -> str:
        """标准化Markdown格式"""
        # 修复列表项格式
        content = re.sub(r'^(\s*)-\s+(.+)$', r'\1- \2', content, flags=re.MULTILINE)
        
        # 修复代码块格式
        content = re.sub(r'```(\w+)?\s*\n', r'```\1\n', content)
        
        # 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 修复表格格式中的问题
        content = re.sub(r'\|([^|\n]*)\|', lambda m: '|' + m.group(1).strip() + '|', content)
        
        return content
    
    def fix_code_blocks(self, content: str) -> str:
        """修复代码块格式"""
        # 为没有语言标识的代码块添加默认标识
        patterns = [
            (r'```\s*\n(.*?using.*?;)', r'```csharp\n\1'),
            (r'```\s*\n(.*?<.*?>)', r'```xml\n\1'),  
            (r'```\s*\n(.*?function.*?\()', r'```javascript\n\1'),
            (r'```\s*\n(.*?def .*?\()', r'```python\n\1'),
            (r'```\s*\n(.*?public class)', r'```java\n\1')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        return content
    
    def optimize_image_references(self, content: str, source_file: str) -> str:
        """优化图片引用，统一图片路径"""
        def normalize_image_path(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # 获取当前文件所在的目录信息
            source_dir = os.path.dirname(source_file)
            
            # 如果是绝对路径，转换为相对路径
            if os.path.isabs(image_path):
                image_path = os.path.basename(image_path)
            
            # 移除路径中的 "../" 等
            image_path = image_path.replace('../', '').replace('./', '')
            
            # 统一放到images目录下
            if not image_path.startswith('images/'):
                # 保留章节信息
                if 'chapter' in image_path:
                    # 如果路径中已包含chapter信息，保持结构
                    if not image_path.startswith('chapter'):
                        chapter_match = re.search(r'(chapter\d+)', source_file)
                        if chapter_match:
                            chapter_name = chapter_match.group(1)
                            image_path = f"images/{chapter_name}/{os.path.basename(image_path)}"
                        else:
                            image_path = f"images/{image_path}"
                    else:
                        image_path = f"images/{image_path}"
                else:
                    # 从源文件路径推断章节
                    chapter_match = re.search(r'(chapter\d+)', source_file)
                    if chapter_match:
                        chapter_name = chapter_match.group(1)
                        image_path = f"images/{chapter_name}/{os.path.basename(image_path)}"
                    else:
                        image_path = f"images/{os.path.basename(image_path)}"
            
            return f"![{alt_text}]({image_path})"
        
        # 应用路径标准化
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', normalize_image_path, content)
        
        return content
    
    def create_optimized_main_latex_file(self, output_file: str, chapter_files: List[str]) -> bool:
        """创建优化的主LaTeX文件，包含所有必要的命令定义"""
        
        main_content = r"""% ========================================
% 智慧水利教材 - 主文件 (修复版)
% ========================================

\documentclass[12pt,a4paper]{book}

% ========================================
% 基础包引入
% ========================================

% 数学支持
\usepackage{amsmath,amssymb,amsthm}

% 图形和颜色
\usepackage{graphicx}
\usepackage{xcolor}

% 页面布局
\usepackage[
    top=2.5cm,
    bottom=2.5cm,
    left=2.8cm,
    right=2.2cm,
    bindingoffset=0.5cm,
    headheight=15pt,
    footskip=1.5cm
]{geometry}

% 中文支持
\usepackage[UTF8]{ctex}

% 字体和行距配置
\usepackage{setspace}
\onehalfspacing  % 1.5倍行距
\setCJKmainfont{SimSun}[BoldFont=SimHei, ItalicFont=KaiTi]
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}

% 超链接和目录
\usepackage{hyperref}
\usepackage{url}

% 列表和表格
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage{multirow}
\usepackage{wrapfig}
\usepackage{float}
\usepackage{colortbl}
\usepackage{pdflscape}
\usepackage{tabu}
\usepackage{threeparttable}
\usepackage{threeparttablex}
\usepackage[normalem]{ulem}
\usepackage{makecell}
\usepackage{calc}

% 代码高亮
\usepackage{fancyvrb}
\usepackage{listings}

% 额外的包支持
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning}
\usepackage{fontspec}
\usepackage{multicol}
\usepackage{enumitem}
\usepackage{tcolorbox}
\usepackage{fontawesome5}

% 页眉页脚
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[LO]{\rightmark}
\fancyhead[RE]{\leftmark}
\renewcommand{\headrulewidth}{0.4pt}

% ========================================
% 颜色定义
% ========================================
\definecolor{primarycolor}{RGB}{41,128,185}
\definecolor{secondarycolor}{RGB}{52,73,94}
\definecolor{accentcolor}{RGB}{231,76,60}
\definecolor{successcolor}{RGB}{39,174,96}
\definecolor{warningcolor}{RGB}{241,196,15}
\definecolor{dangercolor}{RGB}{231,76,60}
\definecolor{lightgray}{RGB}{236,240,241}
\definecolor{darkgray}{RGB}{52,73,94}
\definecolor{codecolor}{RGB}{46,51,56}
\definecolor{linkcolor}{RGB}{41,128,185}

% ========================================
% 定理环境设置
% ========================================
\newtheorem{definition}{定义}[chapter]
\newtheorem{theorem}{定理}[chapter]
\newtheorem{lemma}[theorem]{引理}
\newtheorem{example}{例}[chapter]
\newtheorem{exercise}{练习}[chapter]

% ========================================
% 自定义命令定义 (重要：必须在此定义所有用到的命令)
% ========================================

% 列表环境命令（来自Pandoc，必须定义）
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 文本样式命令
\newcommand{\highlight}[1]{\colorbox{yellow!30}{\textbf{#1}}}
\newcommand{\important}[1]{\textcolor{accentcolor}{\textbf{#1}}}
\newcommand{\note}[1]{\textcolor{secondarycolor}{\textit{#1}}}
\newcommand{\code}[1]{\texttt{\colorbox{lightgray}{#1}}}
\newcommand{\file}[1]{\texttt{\textbf{#1}}}
\newcommand{\variable}[1]{\texttt{\textit{#1}}}

% 快捷符号
\providecommand{\checkmark}{\textcolor{accentcolor}{\faCheck}}
\newcommand{\crossmark}{\textcolor{dangercolor}{\faTimes}}
\newcommand{\infomark}{\textcolor{primarycolor}{\faInfoCircle}}
\newcommand{\warningmark}{\textcolor{warningcolor}{\faExclamationTriangle}}

% ========================================
% 特殊环境定义
% ========================================

% 学习目标框
\newcommand{\learningobjectives}[1]{
    \begin{tcolorbox}[
        colback=primarycolor!10,
        colframe=primarycolor,
        title=\faTarget\ 学习目标,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% 关键概念框
\newcommand{\keypoints}[1]{
    \begin{tcolorbox}[
        colback=successcolor!10,
        colframe=successcolor,
        title=\faKey\ 关键概念,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% 实践练习框
\newcommand{\practiceexercise}[1]{
    \begin{tcolorbox}[
        colback=accentcolor!10,
        colframe=accentcolor,
        title=\faCog\ 实践练习,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% 注意事项
\newcommand{\attention}[1]{
    \begin{tcolorbox}[
        colback=warningcolor!10,
        colframe=warningcolor,
        title=\faExclamationTriangle\ 注意,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% 章节摘要框
\newcommand{\chaptersummary}[1]{
    \begin{tcolorbox}[
        colback=secondarycolor!10,
        colframe=secondarycolor,
        title=\faClipboardList\ 章节摘要,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% ========================================
% 超链接设置
% ========================================
\hypersetup{
    colorlinks=true,
    linkcolor=linkcolor,
    filecolor=linkcolor,
    citecolor=linkcolor,
    urlcolor=linkcolor,
    pdfcreator={LaTeX via pandoc}
}

% ========================================
% 代码高亮配置
% ========================================
\lstset{
    basicstyle=\ttfamily\footnotesize,
    backgroundcolor=\color{lightgray!20},
    frame=single,
    breaklines=true,
    numbers=left,
    numberstyle=\tiny\color{darkgray},
    showstringspaces=false,
    commentstyle=\color{darkgray},
    keywordstyle=\color{primarycolor}\bfseries,
    stringstyle=\color{accentcolor}
}

% ========================================
% 文档开始
% ========================================
\begin{document}

% 目录
\tableofcontents
\newpage

"""
        
        # 添加章节包含命令
        for chapter_file in chapter_files:
            main_content += f'\\input{{{chapter_file}}}\n'
        
        # 结束文档
        main_content += '\n\\end{document}\n'
        
        # 写入主文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        return True
    
    def convert_to_latex(self, input_files: List[str], output_file: str) -> bool:
        """转换为LaTeX格式（修复版）"""
        print(f"开始转换为LaTeX（修复版）：{output_file}")
        
        if not self.available_tools['pandoc']:
            print("错误：Pandoc不可用，无法转换")
            return False
        
        # 按章节组织文件
        organized_files = self.organize_files_by_chapter(input_files)
        
        # 创建输出目录结构
        output_dir = os.path.dirname(output_file)
        latex_chapters_dir = os.path.join(output_dir, 'chapters')
        os.makedirs(latex_chapters_dir, exist_ok=True)
        
        # 转换每个章节
        chapter_tex_files = []
        
        # 处理前言和主要文件
        if 'main_files' in organized_files:
            main_tex_file = os.path.join(output_dir, 'main_content.tex')
            if self.convert_files_to_latex_content_only(organized_files['main_files'], main_tex_file):
                chapter_tex_files.append('main_content.tex')
        
        # 处理各章节
        for chapter_name, files in organized_files.items():
            if chapter_name == 'main_files':
                continue
                
            chapter_tex_file = os.path.join(latex_chapters_dir, f'{chapter_name}.tex')
            if self.convert_files_to_latex_content_only(files, chapter_tex_file):
                chapter_tex_files.append(f'chapters/{chapter_name}.tex')
        
        # 创建优化的主LaTeX文件
        success = self.create_optimized_main_latex_file(output_file, chapter_tex_files)
        
        if success:
            print("✓ LaTeX修复版转换成功")
        
        return success
    
    def convert_files_to_latex_content_only(self, files: List[str], output_file: str) -> bool:
        """转换文件为纯LaTeX内容（不包含文档结构）"""
        # 构建pandoc命令 - 只生成内容，不生成完整文档
        cmd = ['pandoc'] + files + ['-o', output_file]
        cmd.extend([
            '--from=markdown',
            '--to=latex',
            '--no-highlight'  # 避免代码高亮冲突
            # 不使用 --standalone，这样就不会生成完整的LaTeX文档结构
        ])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ 转换文件成功: {os.path.basename(output_file)}")
            
            # 清理生成的内容，确保不包含任何文档结构元素
            self.cleanup_latex_content_thoroughly(output_file)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 转换文件失败：{files[0]} - {e}")
            print(f"错误输出：{e.stderr}")
            return False
    
    def cleanup_latex_content_thoroughly(self, latex_file: str):
        """彻底清理LaTeX文件，确保只包含内容"""
        with open(latex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除所有可能的文档结构元素
        unwanted_patterns = [
            r'\\documentclass.*?\n',
            r'\\usepackage.*?\n',
            r'\\begin\{document\}.*?\n',
            r'\\end\{document\}.*?\n',
            r'\\title\{.*?\}',
            r'\\author\{.*?\}',
            r'\\date\{.*?\}',
            r'\\maketitle',
            r'\\PassOptionsToPackage.*?\n',
            r'\\providecommand.*?\n',
            r'\\newcommand.*?\n',
            r'\\definecolor.*?\n',
            r'\\setcounter.*?\n',
            r'\\setlength.*?\n',
            r'% Options for packages.*?\n'
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        # 清理多余的空行和注释行
        content = re.sub(r'^\s*%.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = content.strip()
        
        # 如果内容为空，添加注释
        if not content.strip():
            content = "% 此章节暂无内容\n"
        
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def organize_files_by_chapter(self, input_files: List[str]) -> dict:
        """按章节组织文件（改进版）"""
        organized = {}
        main_files = []
        
        for file_path in input_files:
            filename = os.path.basename(file_path)
            
            # 主要文件
            if filename in ['index.md', '前言.md', 'README.md']:
                main_files.append(file_path)
            # 章节主文件
            elif filename.startswith('chapter') and filename.endswith('.md'):
                chapter_num = re.search(r'chapter(\d+)', filename)
                if chapter_num:
                    chapter_key = f'chapter{chapter_num.group(1).zfill(2)}'
                    if chapter_key not in organized:
                        organized[chapter_key] = []
                    organized[chapter_key].append(file_path)
            # 章节小节文件
            elif filename.startswith('section') and filename.endswith('.md'):
                section_match = re.search(r'section(\d+)', filename)
                if section_match:
                    chapter_num = section_match.group(1)
                    chapter_key = f'chapter{chapter_num.zfill(2)}'
                    if chapter_key not in organized:
                        organized[chapter_key] = []
                    organized[chapter_key].append(file_path)
                else:
                    main_files.append(file_path)
            else:
                main_files.append(file_path)
        
        if main_files:
            organized['main_files'] = main_files
        
        # 对每个章节的文件进行排序
        for key, files in organized.items():
            organized[key] = sorted(files)
        
        print(f"文件组织结果：")
        for key, files in organized.items():
            print(f"  {key}: {len(files)} 个文件")
            for file in files:
                print(f"    - {os.path.basename(file)}")
        
        return organized
    
    def postprocess_latex(self, latex_file: str) -> bool:
        """后处理LaTeX文件（修复版）"""
        print("开始后处理LaTeX文件...")
        
        # 复制和统一管理图片文件
        self.unified_image_management(latex_file)
        
        # 处理主LaTeX文件
        with open(latex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复图片路径
        content = self.fix_image_paths_unified(content)
        
        # 修复文档结构问题
        if self.config['postprocessing']['fix_document_structure']:
            content = self.fix_document_structure(content)
        
        # 保存处理后的主文件
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 处理所有章节文件
        output_dir = os.path.dirname(latex_file)
        self.postprocess_all_chapter_files(output_dir)
        
        print("✓ LaTeX后处理完成")
        return True
    
    def unified_image_management(self, latex_file: str):
        """统一图片管理 - 将所有图片复制到统一的images目录"""
        output_dir = os.path.dirname(latex_file)
        unified_images_dir = os.path.join(output_dir, 'images')
        
        # 创建统一的images目录
        os.makedirs(unified_images_dir, exist_ok=True)
        
        # 查找源目录中的所有图片
        source_image_dirs = [
            os.path.join(self.source_dir, 'docs', 'chapters', 'images'),
            os.path.join(self.source_dir, 'docs', 'assets', 'images'),
            os.path.join(self.source_dir, 'chapters', 'images'),
            os.path.join(self.source_dir, 'images'),
            os.path.join(self.source_dir, 'assets', 'images')
        ]
        
        copied_count = 0
        for source_images_dir in source_image_dirs:
            if os.path.exists(source_images_dir):
                for root, dirs, files in os.walk(source_images_dir):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf')):
                            source_path = os.path.join(root, file)
                            
                            # 保持相对目录结构
                            rel_path = os.path.relpath(source_path, source_images_dir)
                            target_path = os.path.join(unified_images_dir, rel_path)
                            
                            # 创建目标目录
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            # 复制文件（如果不存在或更新）
                            if not os.path.exists(target_path) or \
                               os.path.getmtime(source_path) > os.path.getmtime(target_path):
                                shutil.copy2(source_path, target_path)
                                copied_count += 1
        
        print(f"✓ 统一图片管理完成，复制了 {copied_count} 个图片文件到: {unified_images_dir}")
    
    def fix_image_paths_unified(self, content: str) -> str:
        """修复图片路径为统一路径"""
        # 统一所有图片路径为 images/...
        patterns = [
            (r'\\includegraphics\{[^}]*?/images/([^}]+)\}', r'\\includegraphics{images/\1}'),
            (r'\\includegraphics\{images/\.\./images/([^}]+)\}', r'\\includegraphics{images/\1}'),
            (r'\\includegraphics\{chapters/images/([^}]+)\}', r'\\includegraphics{images/\1}'),
            (r'\\includegraphics\{docs/chapters/images/([^}]+)\}', r'\\includegraphics{images/\1}'),
            (r'\\includegraphics\{[^}]*?docs/assets/images/([^}]+)\}', r'\\includegraphics{images/\1}')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_document_structure(self, content: str) -> str:
        """修复文档结构问题"""
        # 确保没有重复的包引入
        seen_packages = set()
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.startswith('\\usepackage'):
                package_match = re.search(r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}', line)
                if package_match:
                    package_name = package_match.group(1)
                    if package_name not in seen_packages:
                        seen_packages.add(package_name)
                        fixed_lines.append(line)
                    # 跳过重复的包
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def postprocess_all_chapter_files(self, output_dir: str):
        """后处理所有章节文件"""
        # 处理chapters目录下的文件
        chapters_dir = os.path.join(output_dir, 'chapters')
        if os.path.exists(chapters_dir):
            for chapter_file in os.listdir(chapters_dir):
                if chapter_file.endswith('.tex'):
                    chapter_path = os.path.join(chapters_dir, chapter_file)
                    self.postprocess_chapter_file_unified(chapter_path)
        
        # 处理主内容文件
        main_content_file = os.path.join(output_dir, 'main_content.tex')
        if os.path.exists(main_content_file):
            self.postprocess_chapter_file_unified(main_content_file)
    
    def postprocess_chapter_file_unified(self, chapter_file: str):
        """后处理单个章节文件（统一版）"""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复图片路径
        content = self.fix_image_paths_unified(content)
        
        # 修复表格问题
        content = self.fix_table_issues(content)
        
        # 修复其他LaTeX语法问题
        content = self.fix_latex_syntax_issues(content)
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def fix_table_issues(self, content: str) -> str:
        """修复表格相关问题"""
        # 修复longtable中的 \\real 问题
        content = re.sub(r'\\real\{([0-9.]+)\}', r'\1', content)
        
        # 修复表格列定义问题
        content = re.sub(
            r'>\\{raggedright\\arraybackslash\\}p\\{\\(\\columnwidth - 4\\tabcolsep\\) \\* ([0-9.]+)\\}',
            r'>{\raggedright\\arraybackslash}p{(\\columnwidth - 4\\tabcolsep) * \1}',
            content
        )
        
        return content
    
    def fix_latex_syntax_issues(self, content: str) -> str:
        """修复其他LaTeX语法问题"""
        # 修复可能的转义问题
        content = re.sub(r'\\textbackslash\\{', r'\\{', content)
        content = re.sub(r'\\}', r'}', content)
        
        # 修复中文标点问题
        content = re.sub(r'，', '，', content)
        content = re.sub(r'。', '。', content)
        
        return content
    
    def compile_pdf(self, latex_file: str) -> bool:
        """编译PDF（修复版）"""
        print(f"开始编译PDF：{latex_file}")
        
        # 寻找可用的LaTeX引擎
        available_engine = None
        for engine in ['xelatex', 'lualatex', 'pdflatex']:
            if self.available_tools.get(engine, False):
                available_engine = engine
                break
        
        if not available_engine:
            print("错误：未找到可用的LaTeX引擎")
            return False
        
        print(f"使用 {available_engine} 编译...")
        
        # 切换到LaTeX文件目录
        original_dir = os.getcwd()
        latex_dir = os.path.dirname(os.path.abspath(latex_file))
        latex_name = os.path.basename(latex_file)
        
        try:
            os.chdir(latex_dir)
            
            # 编译多次以确保交叉引用正确
            for i in range(3):
                print(f"第 {i+1} 次编译...")
                result = subprocess.run([
                    available_engine,
                    '-interaction=nonstopmode',
                    '-output-directory=.',
                    latex_name
                ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                # 检查是否成功
                pdf_file = latex_name.replace('.tex', '.pdf')
                if os.path.exists(pdf_file):
                    if i == 2:  # 最后一次编译
                        print("✓ PDF编译成功")
                        return True
                    continue
                
                # 如果编译失败，显示关键错误信息
                if result.returncode != 0:
                    print(f"编译失败，显示关键错误：")
                    log_file = latex_name.replace('.tex', '.log')
                    if os.path.exists(log_file):
                        self.show_compilation_errors(log_file)
                    return False
            
            return False
            
        finally:
            os.chdir(original_dir)
    
    def show_compilation_errors(self, log_file: str):
        """显示编译错误信息"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            
            # 提取关键错误信息
            error_patterns = [
                r'! (.+)',
                r'(.+Error.+)',
                r'(.+not found.+)',
                r'(.+Undefined.+)',
                r'(.+Missing.+)'
            ]
            
            lines = log_content.split('\n')
            for line_num, line in enumerate(lines):
                for pattern in error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        print(f"  行 {line_num+1}: {line.strip()}")
                        # 显示下一行的上下文
                        if line_num + 1 < len(lines):
                            print(f"         {lines[line_num+1].strip()}")
                        break
        except Exception as e:
            print(f"无法读取日志文件: {e}")
    
    def convert(self, source_dir: str, output_format: str = None) -> bool:
        """主转换函数（修复版）"""
        if output_format:
            self.config['output_format'] = output_format
        
        # 保存源目录路径供其他方法使用
        self.source_dir = os.path.abspath(source_dir)
        
        print(f"开始教材转换流程 (修复版)...")
        print(f"源目录：{source_dir}")
        print(f"输出格式：{self.config['output_format']}")
        
        # 创建输出目录
        output_dir = self.config['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        # 发现章节文件
        if not self.config['chapters']:
            self.config['chapters'] = self.discover_chapters(source_dir)
        
        if not self.config['chapters']:
            print("错误：未找到任何章节文件")
            return False
        
        print(f"发现 {len(self.config['chapters'])} 个章节文件")
        
        # 预处理
        temp_dir = os.path.join(output_dir, 'temp')
        processed_files = self.preprocess_markdown(self.config['chapters'], temp_dir)
        
        # 根据输出格式进行转换
        success = False
        
        if self.config['output_format'] in ['latex', 'pdf']:
            latex_file = os.path.join(output_dir, '教材.tex')
            success = self.convert_to_latex(processed_files, latex_file)
            
            if success:
                success = self.postprocess_latex(latex_file)
                
                if success and self.config['output_format'] == 'pdf':
                    success = self.compile_pdf(latex_file)
        
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        if success:
            print(f"\n✓ 转换完成！输出文件在：{output_dir}")
            print("主要修复:")
            print("  ✓ 修复了LaTeX文档结构问题")
            print("  ✓ 统一了图片路径管理")
            print("  ✓ 移除了emoji字符")
            print("  ✓ 修复了缺失命令定义")
            print("  ✓ 优化了包依赖管理")
        else:
            print(f"\n✗ 转换失败")
        
        return success


def main():
    parser = argparse.ArgumentParser(description='修复后的通用教材转换工具')
    parser.add_argument('source_dir', help='源文件目录')
    parser.add_argument('-f', '--format', choices=['latex', 'pdf', 'docx'], 
                       default='pdf', help='输出格式')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-o', '--output', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建转换器
    converter = FixedTextbookConverter(args.config)
    
    # 设置输出目录
    if args.output:
        converter.config['output_dir'] = args.output
    
    # 执行转换
    success = converter.convert(args.source_dir, args.format)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()