#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用教材转换脚本
支持多种转换路径和配置选项
版本: v2.0
适用: 教材制作工作流程
更新: 2025年8月7日
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


class TextbookConverter:
    """教材转换主类"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.supported_formats = ['latex', 'pdf', 'docx', 'html']
        self.check_dependencies()
    
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
                "fix_code_blocks": True
            },
            "postprocessing": {
                "optimize_latex": True,
                "fix_chinese_fonts": True,
                "add_listings_config": True,
                "beautify_layout": True
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
        try:
            result = subprocess.run(['xelatex', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.available_tools['xelatex'] = True
            print("✓ XeLaTeX 可用")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.available_tools['xelatex'] = False
            print("✗ XeLaTeX 不可用")
    
    def discover_chapters(self, source_dir: str) -> List[str]:
        """自动发现章节文件"""
        markdown_files = []
        
        # 首先添加根目录的主要文件（按特定顺序）
        main_files = ['index.md', '前言.md']
        for filename in main_files:
            filepath = os.path.join(source_dir, filename)
            if os.path.exists(filepath):
                markdown_files.append(filepath)
        
        # 查找chapters目录下的章节
        chapters_dir = os.path.join(source_dir, 'chapters')
        if os.path.exists(chapters_dir):
            # 查找chapter开头的目录
            chapter_dirs = glob.glob(os.path.join(chapters_dir, "chapter*"))
            chapter_dirs.sort()  # 按数字顺序排序
            
            for chapter_dir in chapter_dirs:
                if os.path.isdir(chapter_dir):
                    # 先添加主章节文件
                    chapter_name = os.path.basename(chapter_dir)
                    main_chapter_file = os.path.join(chapter_dir, f"{chapter_name}.md")
                    if os.path.exists(main_chapter_file):
                        markdown_files.append(main_chapter_file)
                    
                    # 再添加章节内的section文件
                    section_files = glob.glob(os.path.join(chapter_dir, "section*.md"))
                    section_files.sort()  # 按文件名排序
                    markdown_files.extend(section_files)
        
        # 兼容旧的章节目录格式（第*章*）
        chapter_dirs_old = glob.glob(os.path.join(source_dir, "第*章*"))
        chapter_dirs_old.sort()
        
        for chapter_dir in chapter_dirs_old:
            if os.path.isdir(chapter_dir):
                # 查找章节内的markdown文件
                md_files = glob.glob(os.path.join(chapter_dir, "*.md"))
                md_files.sort()
                markdown_files.extend(md_files)
        
        # 查找根目录的其他markdown文件
        root_md_files = glob.glob(os.path.join(source_dir, "*.md"))
        
        # 过滤掉已经添加的文件和README等文件
        existing_files = set(markdown_files)
        filtered_files = [f for f in root_md_files 
                         if f not in existing_files and 
                         not os.path.basename(f).lower().startswith(('readme', 'summary'))]
        
        markdown_files.extend(filtered_files)
        
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
            
            # 标准化格式
            if self.config['preprocessing']['standardize_format']:
                content = self.standardize_markdown_format(content)
            
            # 修复代码块
            if self.config['preprocessing']['fix_code_blocks']:
                content = self.fix_code_blocks(content)
            
            # 优化图片引用
            if self.config['preprocessing']['optimize_images']:
                content = self.optimize_image_references(content)
            
            # 保存处理后的文件
            processed_file = os.path.join(temp_dir, os.path.basename(input_file))
            with open(processed_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            processed_files.append(processed_file)
        
        print(f"✓ 预处理完成，处理了 {len(processed_files)} 个文件")
        return processed_files
    
    def standardize_markdown_format(self, content: str) -> str:
        """标准化Markdown格式"""
        # 统一标题格式
        content = re.sub(r'^#+\s*(.+?)\s*#+?\s*$', r'## \1', content, flags=re.MULTILINE)
        
        # 统一代码块格式
        content = re.sub(r'```(\w+)?\s*\n', r'```\1\n', content)
        
        # 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def fix_code_blocks(self, content: str) -> str:
        """修复代码块格式"""
        # 为没有语言标识的代码块添加默认标识
        content = re.sub(r'```\s*\n(.*?using.*?;)', r'```csharp\n\1', content, flags=re.DOTALL)
        content = re.sub(r'```\s*\n(.*?<.*?>)', r'```xml\n\1', content, flags=re.DOTALL)
        content = re.sub(r'```\s*\n(.*?function.*?\()', r'```javascript\n\1', content, flags=re.DOTALL)
        content = re.sub(r'```\s*\n(.*?def .*?\()', r'```python\n\1', content, flags=re.DOTALL)
        
        return content
    
    def optimize_image_references(self, content: str) -> str:
        """优化图片引用"""
        # 将SVG引用转换为通用格式
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+\.svg)\)', r'![\1](\2)', content)
        
        # 标准化图片路径
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', self.normalize_image_path, content)
        
        return content
    
    def normalize_image_path(self, match) -> str:
        """标准化图片路径"""
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # 将绝对路径转换为相对路径
        if os.path.isabs(image_path):
            image_path = os.path.basename(image_path)
        
        # 确保图片在images目录中
        if not image_path.startswith('images/'):
            image_path = f"images/{image_path}"
        
        return f"![{alt_text}]({image_path})"
    
    def convert_to_latex(self, input_files: List[str], output_file: str) -> bool:
        """转换为LaTeX格式（分章节结构）"""
        print(f"开始转换为LaTeX（分章节结构）：{output_file}")
        
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
            if self.convert_files_to_latex(organized_files['main_files'], main_tex_file, is_main=True):
                chapter_tex_files.append('main_content.tex')
        
        # 处理各章节
        for chapter_name, files in organized_files.items():
            if chapter_name == 'main_files':
                continue
                
            chapter_tex_file = os.path.join(latex_chapters_dir, f'{chapter_name}.tex')
            if self.convert_files_to_latex(files, chapter_tex_file, is_main=False):
                chapter_tex_files.append(f'chapters/{chapter_name}.tex')
        
        # 创建主LaTeX文件
        success = self.create_main_latex_file(output_file, chapter_tex_files)
        
        if success:
            print("✓ LaTeX分章节转换成功")
        
        return success
    
    def organize_files_by_chapter(self, input_files: List[str]) -> dict:
        """按章节组织文件"""
        organized = {}
        main_files = []
        
        for file_path in input_files:
            filename = os.path.basename(file_path)
            
            # 主要文件（index.md, 前言.md等）
            if filename in ['index.md', '前言.md']:
                main_files.append(file_path)
            # 章节主文件（chapter01.md, chapter02.md等）
            elif filename.startswith('chapter') and filename.endswith('.md'):
                # 从文件名提取章节号
                chapter_num = filename.replace('chapter', '').replace('.md', '')
                chapter_key = f'chapter{chapter_num}'
                if chapter_key not in organized:
                    organized[chapter_key] = []
                organized[chapter_key].append(file_path)
            # 章节小节文件（section01-01.md等）
            elif filename.startswith('section') and filename.endswith('.md'):
                # 从文件名提取章节号（section01-01.md -> chapter01）
                parts = filename.split('-')
                if len(parts) >= 2:
                    section_prefix = parts[0]  # section01
                    chapter_num = section_prefix.replace('section', '')
                    chapter_key = f'chapter{chapter_num}'
                    if chapter_key not in organized:
                        organized[chapter_key] = []
                    organized[chapter_key].append(file_path)
                else:
                    main_files.append(file_path)
            else:
                # 其他文件暂时归入主文件
                main_files.append(file_path)
        
        if main_files:
            organized['main_files'] = main_files
        
        # 调试输出
        print(f"文件组织结果：")
        for key, files in organized.items():
            print(f"  {key}: {len(files)} 个文件")
        
        return organized
    
    def convert_files_to_latex(self, files: List[str], output_file: str, is_main: bool = False) -> bool:
        """转换文件列表为LaTeX"""
        # 构建pandoc命令
        cmd = ['pandoc'] + files + ['-o', output_file]
        cmd.extend([
            '--from=markdown',
            '--to=latex',
            '--no-highlight'  # 避免代码高亮冲突
        ])
        
        # 主文件使用完整模板，章节文件只转换内容
        if is_main:
            template_file = os.path.join(self.config['template_dir'], '智慧水利Pandoc模板.tex')
            if os.path.exists(template_file):
                cmd.extend(['--template', template_file])
        else:
            # 章节文件使用简单模板，只包含内容部分
            pass  # 不使用模板，让pandoc生成纯内容
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ 转换文件成功: {os.path.basename(output_file)}")
            
            # 如果是章节文件，进行后处理以移除不必要的包声明
            if not is_main:
                self.cleanup_chapter_latex(output_file)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 转换文件失败：{files[0]} - {e}")
            print(f"错误输出：{e.stderr}")
            return False
    
    def cleanup_chapter_latex(self, latex_file: str):
        """清理章节LaTeX文件，移除文档结构元素"""
        with open(latex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除文档类声明和包引入
        content = re.sub(r'\\documentclass.*?\n', '', content)
        content = re.sub(r'\\usepackage.*?\n', '', content)
        content = re.sub(r'\\begin\{document\}', '', content)
        content = re.sub(r'\\end\{document\}', '', content)
        
        # 清理空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
        
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_main_latex_file(self, output_file: str, chapter_files: List[str]) -> bool:
        """创建主LaTeX文件"""
        
        # 创建简化的LaTeX主文件内容
        main_content = r"""% ========================================
% 智慧水利教材 - 主文件
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

% 代码高亮
\usepackage{fancyvrb}
\usepackage{listings}

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
    
    def postprocess_latex(self, latex_file: str) -> bool:
        """后处理LaTeX文件（支持分章节结构）"""
        print("开始后处理LaTeX文件...")
        
        # 复制图片文件到输出目录
        self.copy_images_to_output(latex_file)
        
        # 处理主LaTeX文件
        with open(latex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复主文件中的图片路径（如果有的话）
        content = self.fix_image_paths(content)
        
        # 修复中文字体
        if self.config['postprocessing']['fix_chinese_fonts']:
            content = self.fix_chinese_fonts(content)
        
        # 优化布局
        if self.config['postprocessing']['beautify_layout']:
            content = self.beautify_layout(content)
        
        # 保存处理后的主文件
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 处理所有章节文件
        output_dir = os.path.dirname(latex_file)
        chapters_dir = os.path.join(output_dir, 'chapters')
        
        if os.path.exists(chapters_dir):
            for chapter_file in os.listdir(chapters_dir):
                if chapter_file.endswith('.tex'):
                    chapter_path = os.path.join(chapters_dir, chapter_file)
                    self.postprocess_chapter_file(chapter_path)
        
        # 处理主内容文件
        main_content_file = os.path.join(output_dir, 'main_content.tex')
        if os.path.exists(main_content_file):
            self.postprocess_chapter_file(main_content_file)
        
        print("✓ LaTeX后处理完成")
        return True
    
    def postprocess_chapter_file(self, chapter_file: str):
        """后处理单个章节文件"""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复章节文件中的图片路径
        content = self.fix_image_paths(content)
        
        # 优化布局
        if self.config['postprocessing']['beautify_layout']:
            content = self.beautify_layout(content)
        
        # 保存处理后的章节文件
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def add_listings_config(self, content: str) -> str:
        """添加代码高亮配置"""
        config_file = os.path.join(self.config['template_dir'], '代码高亮配置.tex')
        if os.path.exists(config_file):
            # 将配置文件复制到输出目录
            import shutil
            dest_config = os.path.join(self.config['output_dir'], 'listings-config.tex')
            shutil.copy2(config_file, dest_config)
            
            # 在usepackage{listings}后添加配置，使用简单的文件名
            content = content.replace(
                r'\usepackage{listings}',
                r'\usepackage{listings}' + '\n' + r'\input{listings-config.tex}'
            )
        return content
    
    def fix_chinese_fonts(self, content: str) -> str:
        """修复中文字体配置"""
        # 添加中文字体设置
        font_config = r'''
\setCJKmainfont{SimSun}[BoldFont=SimHei, ItalicFont=KaiTi]
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}
'''
        
        # 在documentclass后添加字体配置
        # 使用 lambda 函数来避免替换字符串中的转义问题
        content = re.sub(
            r'(\\documentclass\[.*?\]\{ctexbook\})',
            lambda m: m.group(1) + font_config,
            content
        )
        
        return content
    
    def beautify_layout(self, content: str) -> str:
        """美化布局"""
        # 优化章节标题
        content = re.sub(r'\\section\{第(.*)章', r'\\chapter{第\1章', content)
        
        # 优化表格格式
        content = content.replace(r'\begin{longtabu}', r'\begin{longtable}')
        content = content.replace(r'\end{longtabu}', r'\end{longtable}')
        
        return content
    
    def fix_image_paths(self, content: str) -> str:
        """修复图片路径"""
        # 修复错误的图片路径格式
        # 将 images/../images/chapter02/image1.png 修复为 chapters/images/chapter02/image1.png
        content = re.sub(
            r'\\includegraphics\{images/\.\./images/(chapter\d+/[^}]+)\}',
            r'\\includegraphics{chapters/images/\1}',
            content
        )
        
        # 修复其他可能的路径问题
        # 将 images/chapter02/image1.png 修复为 chapters/images/chapter02/image1.png
        content = re.sub(
            r'\\includegraphics\{images/(chapter\d+/[^}]+)\}',
            r'\\includegraphics{chapters/images/\1}',
            content
        )
        
        # 确保图片路径是相对于输出目录的正确路径
        # 如果有其他格式的路径问题，可以在这里继续添加修复规则
        
        return content
    
    def copy_images_to_output(self, latex_file: str):
        """复制图片文件到输出目录"""
        import shutil
        
        output_dir = os.path.dirname(latex_file)
        # 修正源图片目录路径
        source_images_dir = os.path.join(self.source_dir, 'chapters', 'images')
        
        if os.path.exists(source_images_dir):
            target_images_dir = os.path.join(output_dir, 'chapters', 'images')
            
            # 创建目标目录的父目录
            os.makedirs(os.path.dirname(target_images_dir), exist_ok=True)
            
            # 复制整个images目录
            if os.path.exists(target_images_dir):
                shutil.rmtree(target_images_dir)
            shutil.copytree(source_images_dir, target_images_dir)
            print(f"✓ 图片文件已复制到: {target_images_dir}")
    
    def compile_pdf(self, latex_file: str) -> bool:
        """编译PDF"""
        print(f"开始编译PDF：{latex_file}")
        
        if not self.available_tools['xelatex']:
            print("错误：XeLaTeX不可用，无法编译PDF")
            return False
        
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
                    'xelatex', 
                    '-interaction=nonstopmode',
                    '-output-directory=.',
                    latex_name
                ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                # 检查是否生成了PDF文件
                pdf_file = latex_name.replace('.tex', '.pdf')
                if os.path.exists(pdf_file):
                    if i == 2:  # 最后一次编译
                        print("✓ PDF编译成功")
                        return True
                    continue  # 继续下一轮编译
                
                # 如果没有PDF文件且有错误，显示错误信息
                if result.returncode != 0:
                    print(f"编译失败：")
                    # 尝试读取日志文件以获取更详细的错误信息
                    log_file = latex_name.replace('.tex', '.log')
                    if os.path.exists(log_file):
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                        print("编译日志显示：")
                        # 显示包含错误关键词的行
                        lines = log_content.split('\n')
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['error', 'emergency', 'undefined', 'not found']):
                                print(f"  {line}")
                    return False
            
            # 如果执行到这里，检查最终是否有PDF文件
            pdf_file = latex_name.replace('.tex', '.pdf')
            if os.path.exists(pdf_file):
                print("✓ PDF编译成功")
                return True
            else:
                print("✗ PDF编译失败：未生成PDF文件")
                return False
            
        finally:
            os.chdir(original_dir)
    
    def convert_to_word(self, latex_file: str, word_file: str) -> bool:
        """转换为Word格式"""
        print(f"开始转换为Word：{word_file}")
        
        if not self.available_tools['pandoc']:
            print("错误：Pandoc不可用，无法转换Word")
            return False
        
        # 预处理LaTeX文件以提高转换成功率
        temp_latex = latex_file + '.temp'
        self.preprocess_latex_for_word(latex_file, temp_latex)
        
        cmd = [
            'pandoc',
            temp_latex,
            '-o', word_file,
            '--from=latex',
            '--to=docx',
            '--standalone',
            '--toc',
            '--number-sections'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✓ Word转换成功")
            
            # 清理临时文件
            if os.path.exists(temp_latex):
                os.remove(temp_latex)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Word转换失败：{e}")
            return False
    
    def preprocess_latex_for_word(self, input_file: str, output_file: str):
        """为Word转换预处理LaTeX文件"""
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简化复杂的LaTeX环境
        content = re.sub(
            r'\\begin{lstlisting}.*?\\end{lstlisting}',
            r'\\begin{verbatim}\n[代码块]\n\\end{verbatim}',
            content,
            flags=re.DOTALL
        )
        
        # 移除复杂的图形元素
        content = re.sub(
            r'\\includegraphics\[[^\]]*\]\{[^}]*\}',
            r'\\texttt{[图片]}',
            content
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def convert(self, source_dir: str, output_format: str = None) -> bool:
        """主转换函数"""
        if output_format:
            self.config['output_format'] = output_format
        
        # 保存源目录路径供其他方法使用
        self.source_dir = os.path.abspath(source_dir)
        
        print(f"开始教材转换流程...")
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
        
        elif self.config['output_format'] == 'docx':
            # 先转换为LaTeX再转换为Word
            latex_file = os.path.join(output_dir, '教材.tex')
            word_file = os.path.join(output_dir, '教材.docx')
            
            success = self.convert_to_latex(processed_files, latex_file)
            if success:
                success = self.postprocess_latex(latex_file)
                if success:
                    success = self.convert_to_word(latex_file, word_file)
        
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        if success:
            print(f"\n✓ 转换完成！输出文件在：{output_dir}")
        else:
            print(f"\n✗ 转换失败")
        
        return success


def main():
    parser = argparse.ArgumentParser(description='通用教材转换工具')
    parser.add_argument('source_dir', help='源文件目录')
    parser.add_argument('-f', '--format', choices=['latex', 'pdf', 'docx'], 
                       default='pdf', help='输出格式')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-o', '--output', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建转换器
    converter = TextbookConverter(args.config)
    
    # 设置输出目录
    if args.output:
        converter.config['output_dir'] = args.output
    
    # 执行转换
    success = converter.convert(args.source_dir, args.format)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
