#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材单章节转换器 v1.0
分章节逐个转换，确保每个章节都能正确处理
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chapter_conversion.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChapterConverter:
    """单章节转换器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent.parent
        self.source_dir = self.project_root / 'docs'
        self.output_dir = self.script_dir / '逐章节输出'
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 章节配置
        self.chapters = {
            'preface': {
                'name': '前言',
                'file': self.source_dir / '前言.md',
                'sections': []
            },
            'chapter01': {
                'name': '第一章 智慧水利概述与平台架构基础',
                'file': self.source_dir / 'chapters' / 'chapter01' / 'chapter01.md',
                'sections': [
                    'section01-01.md', 'section01-02.md', 'section01-03.md'
                ]
            },
            'chapter02': {
                'name': '第二章 软件工程基础与需求分析', 
                'file': self.source_dir / 'chapters' / 'chapter02' / 'chapter02.md',
                'sections': [
                    'section02-01.md', 'section02-02.md', 'section02-03.md',
                    'section02-04.md', 'section02-05.md', 'section02-06.md'
                ]
            },
            'chapter03': {
                'name': '第三章 版本控制系统',
                'file': self.source_dir / 'chapters' / 'chapter03' / 'chapter03.md',
                'sections': [
                    'section03-01.md', 'section03-02.md', 'section03-03.md',
                    'section03-04.md', 'section03-05.md', 'section03-06.md', 'section03-07.md'
                ]
            },
            # 可以继续添加其他章节
        }
        
        logger.info(f"初始化完成 - 源目录: {self.source_dir}, 输出目录: {self.output_dir}")

    def clean_content(self, content: str, file_type: str = 'chapter') -> str:
        """清理内容"""
        # 移除YAML frontmatter
        if content.startswith('---'):
            content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        
        # 转换特殊块（在清理其他内容之前）
        content = self.convert_special_blocks(content)
        
        # 移除不需要的章节
        remove_patterns = [
            r'##\s+本章小结.*?(?=\n##|\n#|\Z)',
            r'##\s+重点难点.*?(?=\n##|\n#|\Z)',
            r'##\s+思考题与练习.*?(?=\n##|\n#|\Z)',
            r'##\s+参考文献.*?(?=\n##|\n#|\Z)',
        ]
        
        for pattern in remove_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # 修复图片路径
        content = self.fix_image_paths(content)
        
        # 确保代码块前后有空行
        content = re.sub(r'(?<!\n)\n(```)', r'\n\n\1', content)
        content = re.sub(r'(```)\n(?!\n)', r'\1\n\n', content)
        
        # 清理多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()

    def convert_special_blocks(self, content: str) -> str:
        """转换特殊块语法（借鉴现有脚本的做法）"""
        
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
        
        # 清理缩进（移除四个空格的缩进）
        content = re.sub(r'^    ', '', content, flags=re.MULTILINE)
        
        return content

    def fix_image_paths(self, content: str) -> str:
        """修复图片路径"""
        # 统一图片路径格式
        patterns = [
            (r'!\[(.*?)\]\(\.\./assets/images/(.*?)\)', r'![\1](images/\2)'),
            (r'!\[(.*?)\]\(assets/images/(.*?)\)', r'![\1](images/\2)'),
            (r'!\[(.*?)\]\(\.\./\.\./assets/images/(.*?)\)', r'![\1](images/\2)'),
            (r'!\[(.*?)\]\(\.\./(.*?\.(?:png|jpg|jpeg|gif|svg|bmp))\)', r'![\1](images/\2)'),
            (r'!\[(.*?)\]\(chapters/images/(.*?)\)', r'![\1](images/\2)'),
            (r'!\[(.*?)\]\((?!images/)([^/\s][^)]*\.(png|jpg|jpeg|gif|svg|bmp|webp))\)', r'![\1](images/\2)'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content

    def create_simple_latex_template(self) -> str:
        """创建基于智慧水利Pandoc模板的LaTeX模板"""
        return r"""
\documentclass[12pt,a4paper]{article}

% ========================================
% 基础包引入（基于智慧水利模板）
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

% 字体和编码
\usepackage{fontspec}
\usepackage{setspace}
\onehalfspacing  % 1.5倍行距

% 中文字体配置（基于智慧水利模板）
\setCJKmainfont{SimSun}[BoldFont=SimHei, ItalicFont=KaiTi]
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}

% 表格增强
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage{multirow}
\usepackage{multicol}

% 列表环境
\usepackage{enumitem}

% 代码环境
\usepackage{listings}

% 美化框架
\usepackage{tcolorbox}
\tcbuselibrary{most}

% 页眉页脚
\usepackage{fancyhdr}

% 超链接
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=blue,
    citecolor=blue,
    urlcolor=blue,
    hidelinks=false,
    pdfcreator={LaTeX via pandoc}
}

% ========================================
% 颜色定义（基于智慧水利模板）
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

% 字体图标支持
\usepackage{fontawesome5}

% ========================================
% 自定义命令定义
% ========================================

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

% 代码高亮设置（基于智慧水利模板）
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

% 图片路径
\graphicspath{{images/}}

% 防止过长行
\setlength{\emergencystretch}{3em}
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 页眉页脚设置
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\leftmark}
\fancyhead[R]{\thepage}
\fancyfoot[C]{}

\begin{document}

"""

    def convert_chapter(self, chapter_key: str) -> Optional[str]:
        """转换单个章节"""
        if chapter_key not in self.chapters:
            logger.error(f"章节 {chapter_key} 不存在")
            return None
        
        chapter_info = self.chapters[chapter_key]
        chapter_name = chapter_info['name']
        
        logger.info(f"开始转换章节: {chapter_name}")
        
        # 创建章节输出目录
        chapter_output = self.output_dir / chapter_key
        chapter_output.mkdir(exist_ok=True)
        
        # 创建images目录
        images_dir = chapter_output / 'images'
        images_dir.mkdir(exist_ok=True)
        
        try:
            # 收集章节内容
            content_parts = []
            
            # 主章节文件
            main_file = chapter_info['file']
            if main_file.exists():
                logger.info(f"处理主文件: {main_file.name}")
                main_content = main_file.read_text(encoding='utf-8')
                
                # 设置标题
                if chapter_key == 'preface':
                    main_content = f"# 前言\n\n{main_content}"
                else:
                    main_content = f"# {chapter_name}\n\n{main_content}"
                
                cleaned_content = self.clean_content(main_content, 'chapter')
                content_parts.append(cleaned_content)
            
            # 处理小节
            if chapter_key != 'preface':
                chapter_dir = self.source_dir / 'chapters' / chapter_key
                if chapter_dir.exists():
                    for section_file in chapter_info['sections']:
                        section_path = chapter_dir / section_file
                        if section_path.exists():
                            logger.info(f"处理小节: {section_file}")
                            section_content = section_path.read_text(encoding='utf-8')
                            
                            # 调整小节标题层级
                            match = re.search(r'section(\d+)-(\d+)', section_file)
                            if match:
                                chapter_num = int(match.group(1))
                                section_num = int(match.group(2))
                                section_content = re.sub(
                                    r'^#\s+(.+)', 
                                    f'## {chapter_num}.{section_num} \\1', 
                                    section_content, 
                                    count=1, 
                                    flags=re.MULTILINE
                                )
                                # 调整子标题
                                section_content = re.sub(
                                    r'^##\s+(?!{}\\.{})(.+)'.format(chapter_num, section_num),
                                    r'### \1', 
                                    section_content, 
                                    flags=re.MULTILINE
                                )
                            
                            cleaned_section = self.clean_content(section_content, 'section')
                            content_parts.append(cleaned_section)
            
            # 合并内容
            merged_content = '\n\n'.join(content_parts)
            
            # 保存Markdown文件用于调试
            md_output = chapter_output / f'{chapter_key}.md'
            md_output.write_text(merged_content, encoding='utf-8')
            logger.info(f"保存Markdown文件: {md_output}")
            
            # 复制相关图片
            self.copy_chapter_images(chapter_key, images_dir)
            
            # 转换为LaTeX
            tex_file = self.convert_md_to_latex(merged_content, chapter_output, chapter_key)
            
            # 编译PDF
            if tex_file:
                pdf_file = self.compile_chapter_pdf(tex_file, chapter_output)
                if pdf_file:
                    logger.info(f"章节 {chapter_name} 转换成功: {pdf_file}")
                    return str(pdf_file)
                else:
                    logger.warning(f"章节 {chapter_name} PDF编译失败，但LaTeX文件已生成: {tex_file}")
                    return str(tex_file)
            
        except Exception as e:
            logger.error(f"转换章节 {chapter_key} 失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def convert_md_to_latex(self, content: str, output_dir: Path, chapter_key: str) -> Optional[str]:
        """转换Markdown到LaTeX"""
        temp_md = output_dir / 'temp.md'
        temp_md.write_text(content, encoding='utf-8')
        
        output_tex = output_dir / f'{chapter_key}.tex'
        
        # 使用Pandoc转换（借鉴智慧水利模板的参数配置）
        pandoc_cmd = [
            'pandoc',
            str(temp_md),
            '--from', 'markdown',
            '--to', 'latex',
            '--output', str(output_tex),
            '--standalone',
            '--variable', 'fontsize=12pt',
            '--variable', 'documentclass=article',
            '--variable', 'geometry:margin=2.5cm',
            '--metadata', f'title={self.chapters[chapter_key]["name"]}',
            '--metadata', 'author=教材编写组',
            '--listings',  # 使用listings包处理代码
            '--number-sections',  # 章节编号
        ]
        
        try:
            logger.info("开始Pandoc转换...")
            subprocess.run(pandoc_cmd, check=True, capture_output=True, text=True, encoding='utf-8')
            logger.info("Pandoc转换成功")
            
            # 后处理LaTeX
            self.postprocess_latex(str(output_tex))
            
            return str(output_tex)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc转换失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"转换过程出错: {e}")
            return None

    def postprocess_latex(self, tex_file: str):
        """后处理LaTeX文件"""
        content = Path(tex_file).read_text(encoding='utf-8')
        
        # 查找并替换整个文档头部
        # 找到documentclass和begin{document}之间的部分
        doc_start = content.find('\\documentclass')
        begin_doc = content.find('\\begin{document}')
        
        if doc_start == -1 or begin_doc == -1:
            logger.error("未找到LaTeX文档结构")
            return
        
        # 提取文档主体内容
        doc_body = content[begin_doc + len('\\begin{document}'):content.rfind('\\end{document}')]
        
        # 创建新的完整文档
        template = self.create_simple_latex_template()
        new_content = template + doc_body.strip() + '\n\n\\end{document}'
        
        # 修复常见问题
        fixes = [
            # 修复图片路径
            (r'\\includegraphics\{([^}]+)\}', r'\\includegraphics[width=0.8\\textwidth,keepaspectratio]{\1}'),
            # 修复代码块
            (r'\\begin\{verbatim\}', r'\\begin{lstlisting}'),
            (r'\\end\{verbatim\}', r'\\end{lstlisting}'),
            # 移除多余空行
            (r'\n\n\n+', r'\n\n'),
            # 确保中文标点正常显示
            (r'，', '，'),
            (r'。', '。'),
        ]
        
        for pattern, replacement in fixes:
            new_content = re.sub(pattern, replacement, new_content)
        
        # 保存修改后的文件
        Path(tex_file).write_text(new_content, encoding='utf-8')
        logger.info("LaTeX后处理完成 - 已添加中文字体支持和tcolorbox样式")
        
        # 调试：保存处理后的前20行到日志
        lines = new_content.split('\n')[:30]
        debug_content = '\n'.join(lines)
        logger.info(f"LaTeX文件前30行:\n{debug_content}")

    def copy_chapter_images(self, chapter_key: str, target_dir: Path):
        """复制章节相关图片"""
        # 可能的图片源目录
        image_sources = [
            self.source_dir / 'assets' / 'images',
            self.source_dir / 'chapters' / 'images',
            self.source_dir / 'chapters' / chapter_key / 'images',
        ]
        
        copied_count = 0
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp'}
        
        for img_dir in image_sources:
            if not img_dir.exists():
                continue
                
            for img_file in img_dir.rglob('*'):
                if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                    target = target_dir / img_file.name
                    if not target.exists():
                        try:
                            shutil.copy2(img_file, target)
                            copied_count += 1
                            logger.debug(f"复制图片: {img_file.name}")
                        except Exception as e:
                            logger.warning(f"复制图片失败 {img_file}: {e}")
        
        logger.info(f"复制了 {copied_count} 个图片文件到 {chapter_key}")
        
        # 如果没有图片，创建占位符
        if copied_count == 0:
            placeholder_path = target_dir / 'placeholder.png'
            placeholder_path.write_text("Placeholder", encoding='utf-8')
            logger.info("创建了占位符图片")

    def compile_chapter_pdf(self, tex_file: str, output_dir: Path) -> Optional[str]:
        """编译单章节PDF"""
        tex_path = Path(tex_file)
        old_cwd = os.getcwd()
        
        try:
            os.chdir(output_dir)
            
            # 检测LaTeX引擎
            engines = ['xelatex', 'pdflatex', 'lualatex']
            available_engine = None
            
            for engine in engines:
                try:
                    subprocess.run(
                        [engine, '--version'], 
                        capture_output=True, 
                        text=True, 
                        timeout=10,
                        check=True
                    )
                    available_engine = engine
                    logger.info(f"使用LaTeX引擎: {engine}")
                    break
                except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    continue
            
            if not available_engine:
                logger.warning("未找到可用的LaTeX引擎")
                return None
            
            # 编译LaTeX
            for i in range(2):
                logger.info(f"第 {i+1} 次LaTeX编译...")
                
                compile_cmd = [
                    available_engine,
                    '-interaction=nonstopmode',
                    '-file-line-error',
                    tex_path.name
                ]
                
                try:
                    result = subprocess.run(
                        compile_cmd,
                        capture_output=True,
                        text=True,
                        timeout=120,  # 2分钟超时
                        encoding='utf-8'
                    )
                    
                    if result.returncode != 0:
                        logger.warning(f"第 {i+1} 次编译有警告或错误")
                        # 保存编译日志
                        log_file = output_dir / f'compile_log_{i+1}.txt'
                        log_file.write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
                
                except subprocess.TimeoutExpired:
                    logger.error(f"第 {i+1} 次编译超时")
                    break
                except Exception as e:
                    logger.error(f"第 {i+1} 次编译出错: {e}")
                    break
            
            # 检查PDF
            pdf_file = tex_path.with_suffix('.pdf')
            if pdf_file.exists() and pdf_file.stat().st_size > 10 * 1024:  # 至少10KB
                logger.info(f"PDF编译成功: {pdf_file}")
                return str(pdf_file)
            else:
                logger.warning("PDF未生成或太小")
                return None
                
        finally:
            os.chdir(old_cwd)

    def list_available_chapters(self) -> List[str]:
        """列出可用的章节"""
        available = []
        for key, info in self.chapters.items():
            if info['file'].exists():
                available.append(f"{key}: {info['name']}")
        return available

    def convert_all_chapters(self) -> List[str]:
        """转换所有章节"""
        logger.info("开始转换所有章节")
        results = []
        
        for chapter_key in self.chapters.keys():
            if self.chapters[chapter_key]['file'].exists():
                result = self.convert_chapter(chapter_key)
                if result:
                    results.append(result)
                else:
                    logger.error(f"章节 {chapter_key} 转换失败")
        
        return results

def main():
    """主函数"""
    converter = ChapterConverter()
    
    if len(sys.argv) > 1:
        # 转换指定章节
        chapter_key = sys.argv[1]
        if chapter_key in converter.chapters:
            result = converter.convert_chapter(chapter_key)
            if result:
                print(f"\n章节 {chapter_key} 转换完成: {result}")
            else:
                print(f"\n章节 {chapter_key} 转换失败")
        else:
            print(f"未找到章节: {chapter_key}")
            print("可用章节:")
            for ch in converter.list_available_chapters():
                print(f"  {ch}")
    else:
        # 交互式菜单
        print("\n智慧水利教材单章节转换器")
        print("=" * 50)
        print("可用章节:")
        available = converter.list_available_chapters()
        for i, ch in enumerate(available, 1):
            print(f"  {i}. {ch}")
        print(f"  {len(available)+1}. 转换所有章节")
        print("  0. 退出")
        
        while True:
            try:
                choice = input(f"\n请选择 (0-{len(available)+1}): ").strip()
                
                if choice == '0':
                    break
                elif choice == str(len(available)+1):
                    results = converter.convert_all_chapters()
                    print(f"\n转换完成! 成功转换了 {len(results)} 个章节")
                    for result in results:
                        print(f"  - {result}")
                    break
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(available):
                        chapter_key = available[idx].split(':')[0]
                        result = converter.convert_chapter(chapter_key)
                        if result:
                            print(f"\n章节转换完成: {result}")
                        else:
                            print("\n章节转换失败")
                    else:
                        print("无效选择，请重试")
                        
            except (ValueError, KeyboardInterrupt):
                print("\n退出")
                break

if __name__ == '__main__':
    main()
