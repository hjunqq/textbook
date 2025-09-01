#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材终极转换器修复版
专门解决章节编号、特殊块转换、LaTeX编译等问题
"""

import os
import re
import shutil
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class SmartWaterTextbookConverterFixed:
    """智慧水利教材转换器 - 修复版"""
    
    def __init__(self, config_file: Optional[str] = None):
        # 获取脚本所在目录
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent
        self.source_dir = self.project_root / "docs"
        self.output_dir = script_dir / "输出" 
        self.images_dir = self.output_dir / "images"
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 章节顺序映射
        self.chapter_order = {
            'chapter01': {'title': '第一章 智慧水利概述与平台架构基础'},
            'chapter02': {'title': '第二章 软件工程基础与需求分析'},
            'chapter03': {'title': '第三章 版本控制系统'},
            'chapter04': {'title': '第四章 系统开发技术基础'},
            'chapter05': {'title': '第五章 后端开发技术'},
            'chapter06': {'title': '第六章 前端开发技术'},
            'chapter07': {'title': '第七章 智慧水利三维场景构建'},
            'chapter08': {'title': '第八章 系统优化与维护'},
            'chapter09': {'title': '第九章 典型应用'}
        }
        
        print("智慧水利教材转换器初始化完成")
    
    def discover_chapters(self) -> List[str]:
        """发现并排序章节文件"""
        chapters_dir = self.source_dir / "chapters"
        if not chapters_dir.exists():
            raise FileNotFoundError(f"章节目录不存在: {chapters_dir}")
            
        chapter_files = []
        
        # 添加前言 - 特殊处理，标记为前言
        preface_file = self.source_dir / "前言.md"
        if preface_file.exists():
            chapter_files.append(("preface", str(preface_file)))
            
        # 按顺序添加章节
        for chapter_key in self.chapter_order.keys():
            chapter_dir = chapters_dir / chapter_key
            if not chapter_dir.exists():
                continue
                
            # 添加章节主文件
            main_file = chapter_dir / f"{chapter_key}.md"
            if main_file.exists():
                chapter_files.append(("chapter", str(main_file)))
                
            # 添加节文件
            section_files = sorted(chapter_dir.glob("section*.md"))
            for section_file in section_files:
                chapter_files.append(("section", str(section_file)))
            
        # 添加附录
        appendix_dir = self.project_root / "appendix"
        if appendix_dir.exists():
            appendix_files = sorted(appendix_dir.glob("*.md"))
            for appendix_file in appendix_files:
                chapter_files.append(("appendix", str(appendix_file)))
            
        print(f"发现 {len(chapter_files)} 个文件")
        return chapter_files
    
    def preprocess_markdown(self, content: str, file_path: str, file_type: str) -> str:
        """预处理Markdown内容"""
        # 标准化章节编号
        content = self.standardize_chapters(content, file_path, file_type)
        # 转换特殊块
        content = self.convert_special_blocks(content)
        # 统一图片路径
        content = self.unify_image_paths(content, file_path)
        return content
    
    def standardize_chapters(self, content: str, file_path: str, file_type: str) -> str:
        """标准化章节编号"""
        file_name = Path(file_path).name
        
        # 处理前言 - 移除章节编号
        if file_type == "preface":
            # 将一级标题转换为无编号的标题（使用\chapter*）
            content = re.sub(r'^#\s+(.+)', r'# \1', content, count=1, flags=re.MULTILINE)
            
        # 处理章节主文件的标题
        elif file_type == "chapter" and file_name.startswith('chapter') and file_name.endswith('.md'):
            chapter_num = re.search(r'chapter(\d+)', file_name)
            if chapter_num:
                chapter_key = f"chapter{chapter_num.group(1).zfill(2)}"
                if chapter_key in self.chapter_order:
                    title = self.chapter_order[chapter_key]['title']
                    content = re.sub(r'^#\s+.*', f'# {title}', content, count=1, flags=re.MULTILINE)
                    
        # 处理节文件的标题 - 转换为section级别
        elif file_type == "section" and file_name.startswith('section'):
            section_match = re.search(r'section(\d+)-(\d+)', file_name)
            if section_match:
                chapter_num = int(section_match.group(1))
                section_num = int(section_match.group(2))
                # 将一级标题转换为二级标题（section级别）
                content = re.sub(r'^#\s+(.+)', f'## {chapter_num}.{section_num} \\1', content, count=1, flags=re.MULTILINE)
                # 将二级标题转换为三级标题
                content = re.sub(r'^##\s+(?!{}\\.{})(.+)'.format(chapter_num, section_num), r'### \\1', content, flags=re.MULTILINE)
        
        # 过滤掉不必要的目录内容
        unnecessary_sections = [
            r'^##\s+本章小结.*$',
            r'^##\s+重点难点.*$', 
            r'^##\s+思考题与练习.*$',
            r'^##\s+本节小结.*$',
            r'^##\s+参考文献.*$',
            r'^##\s+配套资源.*$',
            r'^##\s+许可证.*$',
            r'^##\s+联系方式.*$',
            r'^##\s+技术支持.*$',
            r'^##\s+软件.*$',
            r'^##\s+版权声明.*$',
            r'^##\s+编写背景.*$',
            r'^##\s+编写目标.*$',
            r'^##\s+适用对象.*$',
            r'^##\s+主要特色.*$',
            r'^##\s+内容结构.*$',
            r'^##\s+使用建议.*$',
            r'^##\s+贡献指南.*$'
        ]
        
        for pattern in unnecessary_sections:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
                
        return content
    
    def convert_special_blocks(self, content: str) -> str:
        """转换特殊块语法"""
        
        # 处理带标题的note块
        content = re.sub(
            r'!!! note "([^"]+)"\s*\n((?:    .*\n?)*)',
            lambda m: f'\\begin{{tcolorbox}}[colback=blue!5, colframe=blue!40, title=\\textbf{{注意：{m.group(1)}}}]\n{m.group(2) or ""}\n\\end{{tcolorbox}}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理不带标题的note块
        content = re.sub(
            r'!!! note\s*\n((?:    .*\n?)*)',
            lambda m: f'\\begin{{tcolorbox}}[colback=blue!5, colframe=blue!40, title=\\textbf{{注意}}]\n{m.group(1) or ""}\n\\end{{tcolorbox}}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理info块
        content = re.sub(
            r'!!! info(?:\s+"([^"]+)")?\s*\n((?:    .*\n?)*)',
            lambda m: f'\\begin{{tcolorbox}}[colback=cyan!5, colframe=cyan!40, title=\\textbf{{信息{f"：{m.group(1)}" if m.group(1) else ""}}}]\n{m.group(2) or ""}\n\\end{{tcolorbox}}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理tip块
        content = re.sub(
            r'!!! tip(?:\s+"([^"]+)")?\s*\n((?:    .*\n?)*)',
            lambda m: f'\\begin{{tcolorbox}}[colback=green!5, colframe=green!40, title=\\textbf{{提示{f"：{m.group(1)}" if m.group(1) else ""}}}]\n{m.group(2) or ""}\n\\end{{tcolorbox}}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理warning块
        content = re.sub(
            r'!!! warning(?:\s+"([^"]+)")?\s*\n((?:    .*\n?)*)',
            lambda m: f'\\begin{{tcolorbox}}[colback=orange!5, colframe=orange!60, title=\\textbf{{警告{f"：{m.group(1)}" if m.group(1) else ""}}}]\n{m.group(2) or ""}\n\\end{{tcolorbox}}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 处理important块
        content = re.sub(
            r'!!! important(?:\s+"([^"]+)")?\s*\n((?:    .*\n?)*)',
            lambda m: f'\\begin{{tcolorbox}}[colback=red!5, colframe=red!60, title=\\textbf{{重要{f"：{m.group(1)}" if m.group(1) else ""}}}]\n{m.group(2) or ""}\n\\end{{tcolorbox}}\n',
            content,
            flags=re.MULTILINE
        )
        
        # 清理缩进
        content = re.sub(r'^    ', '', content, flags=re.MULTILINE)
        
        return content
    
    def copy_images(self):
        """复制图片文件到输出目录"""
        # 查找多个可能的源图片目录
        possible_source_dirs = [
            self.source_dir / "chapters" / "images",
            self.source_dir / "assets" / "images", 
            self.source_dir / "images",
            self.project_root / "images"
        ]
        
        target_images_dir = self.output_dir / "images"
        target_images_dir.mkdir(exist_ok=True)
        
        copied_count = 0
        print("🖼️  开始复制图片文件...")
        
        for source_images_dir in possible_source_dirs:
            if not source_images_dir.exists():
                continue
                
            print(f"   检查目录: {source_images_dir}")
            
            # 复制所有图片文件
            for image_file in source_images_dir.rglob("*"):
                if image_file.is_file() and image_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp']:
                    try:
                        # 计算相对路径
                        relative_path = image_file.relative_to(source_images_dir)
                        target_path = target_images_dir / relative_path
                        
                        # 避免重复复制
                        if target_path.exists():
                            continue
                            
                        # 创建目标目录
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 复制文件
                        shutil.copy2(image_file, target_path)
                        copied_count += 1
                        print(f"   复制: {relative_path}")
                        
                    except Exception as e:
                        print(f"   ❌ 复制失败 {image_file}: {e}")
        
        if copied_count == 0:
            print("⚠️  未找到图片文件，将创建占位符图片")
            self.create_placeholder_images()
        else:
            print(f"✅ 图片复制完成，共复制 {copied_count} 个文件")
    
    def create_placeholder_images(self):
        """创建占位符图片"""
        images_dir = self.output_dir / "images"
        images_dir.mkdir(exist_ok=True, parents=True)
        
        # 创建常见的占位符图片名称
        placeholder_names = [
            "placeholder.png",
            "image_001.png",
            "image_002.png", 
            "image_003.png",
            "chapter01_function_framework.svg",
            "waterfall_model.svg",
            "evolutionary_model.png"
        ]
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            for name in placeholder_names:
                placeholder_path = images_dir / name
                if not placeholder_path.exists():
                    # 创建一个简单的占位符图像
                    img = Image.new('RGB', (400, 300), color='lightgray')
                    draw = ImageDraw.Draw(img)
                    try:
                        # 尝试使用默认字体
                        font = ImageFont.load_default()
                        draw.text((50, 140), f"Placeholder\n{name}", fill='black', font=font)
                    except:
                        draw.text((50, 140), f"Placeholder\n{name}", fill='black')
                    
                    if name.endswith('.svg'):
                        # SVG文件创建为简单的XML
                        svg_content = f'''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="lightgray"/>
  <text x="50%" y="50%" text-anchor="middle" fill="black">{name}</text>
</svg>'''
                        with open(placeholder_path, 'w', encoding='utf-8') as f:
                            f.write(svg_content)
                    else:
                        img.save(placeholder_path)
                    print(f"   创建占位符: {name}")
        except ImportError:
            # 如果没有PIL，创建简单的文本文件作为占位符
            for name in placeholder_names:
                placeholder_path = images_dir / name
                if not placeholder_path.exists():
                    placeholder_path.write_text(f"Placeholder for {name}", encoding='utf-8')
                    print(f"   创建文本占位符: {name}")
    
    def unify_image_paths(self, content: str, file_path: str) -> str:
        """统一图片路径"""
        # 处理不同的图片引用格式
        patterns = [
            # 处理 ../images/xxx 格式
            (r'!\[([^\]]*)\]\(\.\./images/([^)]+)\)', r'![\1](images/\2)'),
            # 处理 ./images/xxx 格式
            (r'!\[([^\]]*)\]\(\./(images/[^)]+)\)', r'![\1](\2)'),
            # 处理相对路径 images/xxx 格式
            (r'!\[([^\]]*)\]\(images/([^)]+)\)', r'![\1](images/\2)'),
            # 处理绝对路径
            (r'!\[([^\]]*)\]\([^/]*/(images/[^)]+)\)', r'![\1](\2)'),
            # 处理 docs/chapters/images/ 格式
            (r'!\[([^\]]*)\]\(docs/chapters/images/([^)]+)\)', r'![\1](images/\2)'),
            # 处理 docs/assets/images/ 格式
            (r'!\[([^\]]*)\]\(docs/assets/images/([^)]+)\)', r'![\1](images/\2)'),
            # 处理 chapters/images/ 格式
            (r'!\[([^\]]*)\]\(chapters/images/([^)]+)\)', r'![\1](images/\2)'),
            # 确保所有图片路径都以 images/ 开头 (但避免重复添加)
            (r'!\[([^\]]*)\]\((?!images/)([^/\s][^)]*\.(png|jpg|jpeg|gif|svg|bmp|webp))\)', r'![\1](images/\2)')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
        return content
    
    def filter_unnecessary_content(self, content: str) -> str:
        """过滤不必要的内容"""
        # 删除整个不必要的章节
        patterns_to_remove = [
            r'##\s+本章小结.*?(?=\n##|\n#|\Z)',
            r'##\s+重点难点.*?(?=\n##|\n#|\Z)',
            r'##\s+思考题与练习.*?(?=\n##|\n#|\Z)',
            r'##\s+本节小结.*?(?=\n##|\n#|\Z)',
            r'##\s+参考文献.*?(?=\n##|\n#|\Z)'
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def merge_chapters(self, chapter_files: List[tuple]) -> str:
        """合并所有章节文件"""
        merged_content = []
        
        for file_type, file_path in chapter_files:
            print(f"处理文件: {Path(file_path).name} (类型: {file_type})")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                processed_content = self.preprocess_markdown(content, file_path, file_type)
                processed_content = self.filter_unnecessary_content(processed_content)
                
                # 对于前言，添加特殊标记
                if file_type == "preface":
                    processed_content = "\\frontmatter\n" + processed_content + "\n\\mainmatter\n"
                
                merged_content.append(processed_content)
                
                # 只在章节之间添加分页，不在节之间添加
                if file_type in ["chapter", "preface"]:
                    merged_content.append('\n\n\\newpage\n\n')
                
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
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{titletoc}
\usepackage{array}
\usepackage{amsmath}
\usepackage{amssymb}

% 修复Pandoc缺失的命令
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 修复表格命令
\providecommand{\real}[1]{#1}
\providecommand{\arraybackslash}{\let\\\tabularnewline}

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

% 语言定义
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

% 代码高亮设置
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
\cleardoublepage

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
        
        # 执行Pandoc转换
        output_tex = self.output_dir / "教材.tex"
        
        try:
            pandoc_cmd = [
                'pandoc',
                str(temp_md),
                '--template', str(template_path),
                '--to', 'latex',
                '--no-highlight',
                '--toc',
                '--top-level-division=chapter',
                '--output', str(output_tex)
            ]
            
            result = subprocess.run(pandoc_cmd, check=True, capture_output=True, text=True)
            print("Pandoc转换成功")
            
            # 转换后立即修复LaTeX文件
            print("🔧 修复LaTeX文件...")
            self.fix_latex_file(str(output_tex))
            
            return str(output_tex)
            
        except subprocess.CalledProcessError as e:
            print(f"Pandoc转换失败: {e}")
            print(f"错误输出: {e.stderr}")
            raise
        finally:
            # 清理临时文件
            if temp_md.exists():
                temp_md.unlink()

    def fix_latex_file(self, tex_file: str):
        """修复LaTeX文件的各种问题"""
        with open(tex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("   修复前言章节编号...")
        # 1. 修复前言章节 - 移除编号
        content = re.sub(r'\\chapter\{前言\}', r'\\chapter*{前言}', content)
        
        print("   修复章节标题格式...")
        # 2. 修复章节标题格式 - 补全缺失的部分和级别错误
        chapter_fixes = [
            # 修复完整的章节标题
            (r'\\chapter\{第一章\s*([^}]*)\}', r'\\chapter{第一章 智慧水利概述与平台架构基础}'),
            (r'\\chapter\{第二章\s*([^}]*)\}', r'\\chapter{第二章 软件工程基础与需求分析}'), 
            (r'\\chapter\{第三章\s*([^}]*)\}', r'\\chapter{第三章 版本控制系统}'),
            (r'\\chapter\{第四章\s*([^}]*)\}', r'\\chapter{第四章 系统开发技术基础}'),
            (r'\\chapter\{第五章\s*([^}]*)\}', r'\\chapter{第五章 后端开发技术}'),
            (r'\\chapter\{第六章\s*([^}]*)\}', r'\\chapter{第六章 前端开发技术}'),
            (r'\\chapter\{第七章\s*([^}]*)\}', r'\\chapter{第七章 智慧水利三维场景构建}'),
            (r'\\chapter\{第八章\s*([^}]*)\}', r'\\chapter{第八章 系统优化与维护}'),
            (r'\\chapter\{第九章\s*([^}]*)\}', r'\\chapter{第九章 典型应用}'),
            
            # 修复错误级别的标题 - 将section级别的章节提升为chapter级别
            (r'\\section\{(第[一二三四五六七八九]章[^}]*)\}', r'\\chapter{\\1}'),
            (r'\\subsection\{(第[一二三四五六七八九]章[^}]*)\}', r'\\chapter{\\1}'),
            
            # 修复缺失编号的章节
            (r'\\chapter\{绪论\}', r'\\chapter{第一章 智慧水利概述与平台架构基础}'),
            (r'\\chapter\{软件工程基础\}', r'\\chapter{第二章 软件工程基础与需求分析}'),
            (r'\\chapter\{版本控制系统\}', r'\\chapter{第三章 版本控制系统}'),
        ]
        
        for pattern, replacement in chapter_fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        print("   修复图像路径...")
        # 3. 修复图像路径问题 - 修复映射和格式
        # 将编号格式化为3位数字
        def fix_image_path(match):
            num = match.group(1)
            formatted_num = f"{int(num):03d}"  # 格式化为3位数字
            return f'\\includegraphics[width=0.8\\textwidth]{{images/image_{formatted_num}.png}}'
        
        content = re.sub(r'\\includegraphics\{images//(\d+)\}', fix_image_path, content)
        content = re.sub(r'\\includegraphics\{images/(\d+)\}', fix_image_path, content)
        # 处理特殊的问题图像
        content = re.sub(r'\\includegraphics\{images//2\}', r'\\includegraphics[width=0.8\\textwidth]{images/image_002.png}', content)
        
        print("   修复表格格式...")
        # 4. 修复表格格式问题 - 全面处理minipage和表格错误
        
        # 修复表格环境中的错误格式
        # 移除表格中的错误参数模式 ()* 数字
        content = re.sub(
            r'\(\s*\)\s*\*\s*[0-9.]+\s*',
            '',
            content,
            flags=re.MULTILINE
        )
        
        # 修复复杂的表格列定义 - 将复杂的列定义简化为基本格式
        content = re.sub(
            r'\\begin\{longtable\}\[\]\{@\{\}\s*>\{[^}]*\}p\{[^}]*\}\s*>\{[^}]*\}p\{[^}]*\}\s*>\{[^}]*\}p\{[^}]*\}@\{\}\}',
            r'\\begin{longtable}{|l|l|l|}',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 修复更复杂的表格列定义
        content = re.sub(
            r'\\begin\{longtable\}\[\]\{@\{\}[^}]*@\{\}\}',
            r'\\begin{longtable}{|l|l|l|}',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 修复包含columnwidth计算的列定义
        content = re.sub(
            r'>\{[^}]*\}p\{[^}]*\\columnwidth[^}]*\}',
            'l',
            content,
            flags=re.MULTILINE
        )
        
        # 修复arraybackslash和复杂列定义
        content = re.sub(
            r'>\{[^}]*arraybackslash[^}]*\}[plcr]\{[^}]*\}',
            'l',
            content,
            flags=re.MULTILINE
        )
        
        # 修复破碎的表格列定义 - 处理多行的列定义
        content = re.sub(
            r'\\begin\{longtable\}\[\]\{\s*l\}\s*l\}\s*l\}\}',
            r'\\begin{longtable}{|l|l|l|}',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 修复任何形式的破碎列定义
        content = re.sub(
            r'\\begin\{longtable\}\[\]\{[^}]*\}[^}]*\}[^}]*\}\}',
            r'\\begin{longtable}{|l|l|l|}',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 修复minipage中的错误参数
        content = re.sub(
            r'\\begin\{minipage\}\[b\]\{\\linewidth\}\\raggedright\s*\(\s*\)\s*\*\s*[0-9.]+',
            r'\\begin{minipage}[b]{\\linewidth}\\raggedright',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 修复表格行中的格式问题 - 删除错误的参数
        content = re.sub(
            r'\\begin\{minipage\}\[b\]\{\\linewidth\}\\raggedright\s*\(\s*\)\s*\*\s*[0-9.]+([^\\]*?)\\end\{minipage\}',
            r'\\begin{minipage}[b]{\\linewidth}\\raggedright \1\\end{minipage}',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 清理表格中的其他错误格式
        content = re.sub(r'\(\s*\)\s*\*\s*[0-9.]+\s*\[\]\|', '', content)
        
        # 修复longtabu表格环境的问题
        content = re.sub(
            r'\\begin\{longtabu\}([^{]*)\{([^}]*)\}',
            r'\\begin{longtable}{\2}',
            content
        )
        content = re.sub(r'\\end\{longtabu\}', r'\\end{longtable}', content)
        
        # 修复表格列定义中的错误
        content = re.sub(
            r'\{\s*\|\s*p\{[^}]*\}\s*\|\s*\}',
            r'{|l|l|l|}',  # 使用简单的列定义
            content
        )
        
        # 修复表格单元格中的格式问题
        content = re.sub(
            r'\\begin\{minipage\}\[b\]\{[^}]+\}\\raggedright\s*([^\\]*?)\\end\{minipage\}',
            r'\1',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 添加表格头部格式修复
        content = re.sub(r'\\toprule\\noalign\{\}', r'\\hline', content)
        content = re.sub(r'\\midrule\\noalign\{\}', r'\\hline', content)
        content = re.sub(r'\\bottomrule\\noalign\{\}', r'\\hline', content)
        content = re.sub(r'\\endhead', r'\\hline', content)
        content = re.sub(r'\\endlastfoot', r'', content)
        
        # 修复表格@{}语法问题
        content = re.sub(r'@\{\}', '', content)
        
        print("   修复特殊块...")
        # 5. 修复!!! info块等特殊格式
        content = re.sub(
            r'\\begin\{quote\}\s*!\s*!\s*!\s*info\s*"([^"]*)"(.*?)\\end\{quote\}',
            r'\\begin{tcolorbox}[colback=blue!5!white,colframe=blue!75!black,title=\\textbf{信息：\\1}]\\2\\end{tcolorbox}',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 写回修复后的内容
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ LaTeX文件修复完成")
    
    def compile_pdf(self, tex_file: str) -> str:
        """编译PDF - 适配Windows和Linux环境"""
        tex_path = Path(tex_file)
        output_dir = tex_path.parent
        
        # 切换到输出目录
        original_dir = os.getcwd()
        os.chdir(output_dir)
        
        try:
            print("🚀 开始PDF编译...")
            
            # 创建一个占位符图像文件，避免缺失图像导致编译失败
            placeholder_path = output_dir / "images" / "placeholder.png"
            if not placeholder_path.exists():
                print("   创建占位符图像...")
                placeholder_path.parent.mkdir(parents=True, exist_ok=True)
                # 创建一个简单的白色1x1像素PNG
                try:
                    from PIL import Image
                    img = Image.new('RGB', (100, 50), color='white')
                    img.save(placeholder_path)
                except ImportError:
                    # 如果没有PIL，创建一个空文件
                    placeholder_path.touch()
            
            # 检查LaTeX环境
            latex_commands = ['xelatex', 'pdflatex', 'lualatex']
            working_latex = None
            
            for cmd in latex_commands:
                try:
                    result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        working_latex = cmd
                        print(f"   找到LaTeX编译器: {cmd}")
                        break
                except FileNotFoundError:
                    continue
            
            if not working_latex:
                print("❌ 未找到LaTeX编译器 (xelatex/pdflatex/lualatex)")
                print("   生成的LaTeX文件路径:", tex_path)
                print("   请在Windows环境中使用TeX Live或MiKTeX编译该文件")
                return str(tex_path)  # 返回tex文件路径
            
            # 使用找到的LaTeX编译器进行编译
            compilation_successful = False
            for i in range(2):  # 减少编译次数
                print(f"📝 第{i+1}次编译...")
                
                cmd = [working_latex, '-interaction=nonstopmode', '-halt-on-error', tex_path.name]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ 第{i+1}次编译成功")
                    compilation_successful = True
                else:
                    print(f"⚠️  第{i+1}次编译有警告 (返回码: {result.returncode})")
                    if result.stderr:
                        print(f"   错误信息: {result.stderr[:200]}...")
            
            # 检查PDF是否生成
            pdf_path = output_dir / "教材.pdf"
            if pdf_path.exists():
                file_size = pdf_path.stat().st_size / (1024*1024)
                if file_size > 0.1:  # 至少0.1MB才认为是有效的PDF
                    print(f"🎉 PDF文件生成成功!")
                    print(f"📊 文件路径: {pdf_path}")
                    print(f"📏 文件大小: {file_size:.1f} MB")
                    return str(pdf_path)
                else:
                    print(f"⚠️ PDF文件过小 ({file_size:.1f} MB)，可能编译不完整")
            
            # 如果PDF不存在，返回LaTeX文件路径
            print(f"📄 LaTeX文件已生成: {tex_path}")
            print("   请在Windows环境中手动编译或安装LaTeX环境")
            return str(tex_path)
                
        finally:
            os.chdir(original_dir)
    
    def run_conversion(self):
        """运行完整的转换过程"""
        print("=" * 60)
        print("智慧水利教材转换器 v2.0 - 全面修复版")
        print("=" * 60)
        
        try:
            # 1. 发现章节文件
            print("\n1. 发现章节文件...")
            chapter_files = self.discover_chapters()
            
            # 2. 复制图片文件
            print("\n2. 复制图片文件...")
            self.copy_images()
            
            # 3. 合并和预处理
            print("\n3. 合并和预处理...")
            merged_content = self.merge_chapters(chapter_files)
            
            # 4. 转换为LaTeX
            print("\n4. 转换为LaTeX...")
            tex_file = self.convert_to_latex(merged_content)
            
            # 5. 编译PDF
            print("\n5. 编译PDF...")
            pdf_file = self.compile_pdf(tex_file)
            
            # 6. 生成统计信息
            print("\n6. 生成统计信息...")
            
            print("\n" + "=" * 60)
            print("转换完成！")
            print("=" * 60)
            print(f"输出目录: {self.output_dir}")
            print(f"处理文件: {len(chapter_files)} 个")
            print(f"章节数量: {len(self.chapter_order)} 个")
            
        except Exception as e:
            print(f"转换失败: {e}")
            raise

def main():
    converter = SmartWaterTextbookConverterFixed()
    converter.run_conversion()

if __name__ == "__main__":
    main()
