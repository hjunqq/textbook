#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材健壮转换器 v6.0
解决中文字体、LaTeX错误、图片路径等常见问题
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversion.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RobustTextbookConverter:
    """健壮的教材转换器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent.parent
        self.source_dir = self.project_root / 'docs'
        self.output_dir = self.script_dir / '输出'
        self.images_dir = self.output_dir / 'images'
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 章节配置
        self.chapter_order = {
            'chapter01': '第一章 智慧水利概述与平台架构基础',
            'chapter02': '第二章 软件工程基础与需求分析',
            'chapter03': '第三章 版本控制系统',
            'chapter04': '第四章 系统开发技术基础',
            'chapter05': '第五章 后端开发技术',
            'chapter06': '第六章 前端开发技术',
            'chapter07': '第七章 智慧水利三维场景构建',
            'chapter08': '第八章 系统优化与维护',
            'chapter09': '第九章 典型应用',
        }
        
        # 需要移除的内容模式
        self.remove_patterns = [
            r'---\n.*?\n---\n',  # YAML frontmatter
            r'##\s+本章小结.*?(?=\n##|\n#|\Z)',
            r'##\s+重点难点.*?(?=\n##|\n#|\Z)',
            r'##\s+思考题与练习.*?(?=\n##|\n#|\Z)',
            r'##\s+本节小结.*?(?=\n##|\n#|\Z)',
            r'##\s+参考文献.*?(?=\n##|\n#|\Z)',
        ]
        
        logger.info(f"初始化完成 - 源目录: {self.source_dir}, 输出目录: {self.output_dir}")

    def discover_files(self) -> List[Tuple[str, str]]:
        """发现所有需要处理的文件"""
        files = []
        
        # 前言
        preface = self.source_dir / '前言.md'
        if preface.exists():
            files.append(('preface', str(preface)))
            logger.info(f"发现前言: {preface.name}")
        
        # 章节文件
        chapters_dir = self.source_dir / 'chapters'
        if chapters_dir.exists():
            for chapter_key in self.chapter_order.keys():
                chapter_dir = chapters_dir / chapter_key
                if not chapter_dir.exists():
                    continue
                    
                # 主章节文件
                main_file = chapter_dir / f'{chapter_key}.md'
                if main_file.exists():
                    files.append(('chapter', str(main_file)))
                    logger.info(f"发现章节: {main_file.name}")
                
                # 章节下的小节文件
                for section in sorted(chapter_dir.glob('section*.md')):
                    files.append(('section', str(section)))
                    logger.info(f"发现小节: {section.name}")
        
        # 附录
        appendix_dir = self.project_root / 'appendix'
        if appendix_dir.exists():
            for appendix in sorted(appendix_dir.glob('*.md')):
                files.append(('appendix', str(appendix)))
                logger.info(f"发现附录: {appendix.name}")
        
        logger.info(f"总共发现 {len(files)} 个文件")
        return files

    def clean_markdown_content(self, content: str, file_type: str, file_path: str) -> str:
        """清理和标准化Markdown内容"""
        original_length = len(content)
        
        # 移除YAML frontmatter
        if content.startswith('---'):
            content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        
        # 移除不需要的章节
        for pattern in self.remove_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # 标准化标题格式
        content = self.standardize_headings(content, file_type, file_path)
        
        # 修复图片路径
        content = self.fix_image_paths(content)
        
        # 修复表格格式
        content = self.fix_table_format(content)
        
        # 修复代码块
        content = self.fix_code_blocks(content)
        
        # 修复特殊字符
        content = self.fix_special_characters(content)
        
        # 清理多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        cleaned_length = len(content)
        reduction = original_length - cleaned_length
        logger.info(f"清理文件 {Path(file_path).name}: {original_length} -> {cleaned_length} 字符 (减少 {reduction})")
        
        return content

    def standardize_headings(self, content: str, file_type: str, file_path: str) -> str:
        """标准化标题格式"""
        file_name = Path(file_path).name
        
        if file_type == 'preface':
            # 前言使用一级标题
            content = re.sub(r'^#\s+(.+)', r'# 前言', content, count=1, flags=re.MULTILINE)
        
        elif file_type == 'chapter':
            # 章节主文件
            match = re.search(r'chapter(\d+)', file_name)
            if match:
                chapter_num = match.group(1)
                chapter_key = f'chapter{chapter_num.zfill(2)}'
                if chapter_key in self.chapter_order:
                    title = self.chapter_order[chapter_key]
                    content = re.sub(r'^#\s+.*', f'# {title}', content, count=1, flags=re.MULTILINE)
        
        elif file_type == 'section':
            # 小节文件
            match = re.search(r'section(\d+)-(\d+)', file_name)
            if match:
                chapter_num = int(match.group(1))
                section_num = int(match.group(2))
                # 调整小节标题层级
                content = re.sub(r'^#\s+(.+)', f'## {chapter_num}.{section_num} \\1', content, count=1, flags=re.MULTILINE)
                # 调整子标题层级
                content = re.sub(r'^##\s+(?!{}\\.{})(.+)'.format(chapter_num, section_num), r'### \\1', content, flags=re.MULTILINE)
        
        elif file_type == 'appendix':
            # 附录
            content = re.sub(r'^#\s+(.+)', r'# 附录 \1', content, count=1, flags=re.MULTILINE)
        
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
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content

    def fix_table_format(self, content: str) -> str:
        """修复表格格式问题"""
        # 确保表格前后有空行
        content = re.sub(r'(?<!\n)\n(\|.*?\|)\n', r'\n\n\1\n', content)
        content = re.sub(r'\n(\|.*?\|)\n(?!\n)', r'\n\1\n\n', content)
        
        # 修复表格对齐符号
        content = re.sub(r'\|\s*:?-+:?\s*\|', lambda m: m.group(0).replace(' ', ''), content)
        
        return content

    def fix_code_blocks(self, content: str) -> str:
        """修复代码块格式"""
        # 确保代码块前后有空行
        content = re.sub(r'(?<!\n)\n(```)', r'\n\n\1', content)
        content = re.sub(r'(```)\n(?!\n)', r'\1\n\n', content)
        
        # 为没有语言标识的代码块添加标识
        content = re.sub(r'^```\s*$', '```text', content, flags=re.MULTILINE)
        
        return content

    def fix_special_characters(self, content: str) -> str:
        """修复特殊字符问题"""
        # 转义LaTeX特殊字符
        replacements = [
            (r'(?<!\\)&', r'\\&'),  # & 符号
            (r'(?<!\\)%', r'\\%'),  # % 符号
            (r'(?<!\\)\$(?!\$)', r'\\$'),  # 单个$符号（但不影响数学公式）
            (r'(?<!\\)#(?![#\s])', r'\\#'),  # # 符号（但不影响标题）
            (r'(?<!\\)_(?!_)', r'\\_'),  # 单个下划线
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        return content

    def copy_images(self) -> int:
        """复制图片文件"""
        image_dirs = [
            self.source_dir / 'assets' / 'images',
            self.source_dir / 'chapters' / 'images',
            self.source_dir / 'images',
            self.project_root / 'images',
        ]
        
        copied_count = 0
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp'}
        
        for img_dir in image_dirs:
            if not img_dir.exists():
                continue
                
            for img_file in img_dir.rglob('*'):
                if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                    target = self.images_dir / img_file.name
                    if not target.exists():
                        try:
                            shutil.copy2(img_file, target)
                            copied_count += 1
                            logger.debug(f"复制图片: {img_file.name}")
                        except Exception as e:
                            logger.warning(f"复制图片失败 {img_file}: {e}")
        
        logger.info(f"复制了 {copied_count} 个图片文件")
        
        # 如果没有图片，创建占位符
        if copied_count == 0:
            self.create_placeholder_images()
        
        return copied_count

    def create_placeholder_images(self):
        """创建占位符图片"""
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (400, 300), '#DDDDDD')
            draw = ImageDraw.Draw(img)
            draw.text((20, 140), "Placeholder Image", fill='black')
            
            placeholder_path = self.images_dir / 'placeholder.png'
            img.save(placeholder_path)
            logger.info("创建了占位符图片")
        except ImportError:
            # 如果没有PIL，创建文本占位符
            placeholder_path = self.images_dir / 'placeholder.png'
            placeholder_path.write_text("Placeholder", encoding='utf-8')
            logger.info("创建了文本占位符")

    def merge_files(self, files: List[Tuple[str, str]]) -> str:
        """合并所有文件"""
        content_parts = []
        total_original = 0
        total_cleaned = 0
        
        for file_type, file_path in files:
            try:
                logger.info(f"处理文件: {Path(file_path).name} ({file_type})")
                
                original_content = Path(file_path).read_text(encoding='utf-8')
                total_original += len(original_content)
                
                cleaned_content = self.clean_markdown_content(original_content, file_type, file_path)
                total_cleaned += len(cleaned_content)
                
                # 添加文件标记注释
                content_parts.append(f'\n<!-- [FILE: {Path(file_path).name}] -->\n')
                content_parts.append(cleaned_content)
                
                # 章节后添加分页
                if file_type in ('chapter', 'preface'):
                    content_parts.append('\n\\newpage\n')
                
            except Exception as e:
                logger.error(f"处理文件失败 {file_path}: {e}")
                continue
        
        merged_content = '\n'.join(content_parts)
        
        # 保存合并统计
        stats_content = f"""合并统计报告
生成时间: {datetime.now()}
原始总字符数: {total_original:,}
清理后字符数: {total_cleaned:,}
压缩率: {(1-total_cleaned/total_original)*100:.1f}%
处理文件数: {len(files)}
"""
        (self.output_dir / '合并统计.txt').write_text(stats_content, encoding='utf-8')
        
        logger.info(f"文件合并完成: {total_original:,} -> {total_cleaned:,} 字符")
        return merged_content

    def create_latex_template(self) -> str:
        """创建LaTeX模板"""
        template = r"""
\documentclass[12pt,a4paper]{book}

% 基础包
\usepackage[UTF8,heading=true]{ctex}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{longtable}
\usepackage{listings}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{titlesec}

% 页面设置
\geometry{
    left=2.5cm,
    right=2.0cm,
    top=2.5cm,
    bottom=2.0cm
}

% 字体设置 - 使用系统默认中文字体
\setCJKmainfont{SimSun}[BoldFont=SimHei]
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}

% 标题格式
\titleformat{\chapter}[display]
    {\centering\Huge\bfseries}
    {\chaptertitlename\ \thechapter}
    {20pt}
    {\Huge}

% 代码环境设置
\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    backgroundcolor=\color{gray!10},
    keywordstyle=\color{blue},
    commentstyle=\color{green!50!black},
    stringstyle=\color{red},
    numbers=left,
    numberstyle=\tiny\color{gray},
    stepnumber=1,
    tabsize=4,
    showspaces=false,
    showstringspaces=false,
    captionpos=b
}

% 图片路径
\graphicspath{{images/}}

% 超链接设置
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    filecolor=blue,
    urlcolor=blue,
    citecolor=green,
    bookmarks=true,
    bookmarksopen=true,
    pdfauthor={教材编写组},
    pdftitle={智慧水利平台架构与开发}
}

% 页眉页脚
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[RE]{\leftmark}
\fancyhead[LO]{\rightmark}

\title{智慧水利平台架构与开发}
\author{教材编写组}
\date{\today}

\begin{document}

\frontmatter
\maketitle
\tableofcontents

\mainmatter

"""
        return template

    def convert_to_latex(self, merged_content: str) -> str:
        """转换为LaTeX"""
        # 保存临时Markdown文件
        temp_md = self.output_dir / 'temp_merged.md'
        temp_md.write_text(merged_content, encoding='utf-8')
        
        # 使用Pandoc转换
        output_tex = self.output_dir / '教材_raw.tex'
        
        pandoc_cmd = [
            'pandoc',
            str(temp_md),
            '--from', 'markdown',
            '--to', 'latex',
            '--output', str(output_tex),
            '--listings',  # 使用listings包处理代码
            '--top-level-division=chapter',
            '--metadata', 'title=智慧水利平台架构与开发',
            '--metadata', 'author=教材编写组',
        ]
        
        try:
            logger.info("开始Pandoc转换...")
            result = subprocess.run(
                pandoc_cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8'
            )
            logger.info("Pandoc转换成功")
            
            # 读取生成的内容
            raw_content = output_tex.read_text(encoding='utf-8')
            
            # 创建完整的LaTeX文件
            template = self.create_latex_template()
            
            # 移除raw_content中的文档类和前导内容
            content_start = raw_content.find('\\begin{document}')
            if content_start != -1:
                raw_content = raw_content[content_start + len('\\begin{document}'):].strip()
            
            content_end = raw_content.rfind('\\end{document}')
            if content_end != -1:
                raw_content = raw_content[:content_end].strip()
            
            # 合并模板和内容
            final_content = template + raw_content + '\n\n\\end{document}'
            
            # 后处理LaTeX内容
            final_content = self.postprocess_latex(final_content)
            
            # 保存最终文件
            final_tex = self.output_dir / '教材.tex'
            final_tex.write_text(final_content, encoding='utf-8')
            
            logger.info(f"LaTeX文件生成完成: {final_tex}")
            return str(final_tex)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc转换失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"LaTeX转换过程出错: {e}")
            raise

    def postprocess_latex(self, content: str) -> str:
        """LaTeX内容后处理"""
        logger.info("开始LaTeX后处理...")
        
        # 修复常见问题
        fixes = [
            # 修复前言标题
            (r'\\section\{前言\}', r'\\chapter*{前言}\\addcontentsline{toc}{chapter}{前言}'),
            
            # 修复图片路径
            (r'\\includegraphics\{([^}]+)\}', r'\\includegraphics[width=0.8\\textwidth,keepaspectratio]{\\1}'),
            
            # 修复代码块
            (r'\\begin\{verbatim\}', r'\\begin{lstlisting}'),
            (r'\\end\{verbatim\}', r'\\end{lstlisting}'),
            
            # 修复表格
            (r'\\begin\{longtable\}\[c\]\{@\{\}([^@]+)@\{\}\}', r'\\begin{longtable}{\1}'),
            
            # 修复特殊字符
            (r'(?<!\\)\\textbackslash\{\}', r'\\textbackslash'),
            
            # 移除多余的空行
            (r'\n\n\n+', r'\n\n'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        logger.info("LaTeX后处理完成")
        return content

    def compile_pdf(self, tex_file: str) -> str:
        """编译PDF"""
        tex_path = Path(tex_file)
        output_dir = tex_path.parent
        old_cwd = os.getcwd()
        
        try:
            os.chdir(output_dir)
            
            # 检测可用的LaTeX引擎
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
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            if not available_engine:
                logger.warning("未找到可用的LaTeX引擎，跳过PDF编译")
                return str(tex_path)
            
            # 编译LaTeX (通常需要运行2次以生成正确的目录和交叉引用)
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
                        timeout=300,  # 5分钟超时
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
            
            # 检查PDF是否成功生成
            pdf_file = tex_path.with_suffix('.pdf')
            if pdf_file.exists() and pdf_file.stat().st_size > 100 * 1024:  # 至少100KB
                logger.info(f"PDF编译成功: {pdf_file}")
                return str(pdf_file)
            else:
                logger.warning("PDF文件未生成或太小，可能编译失败")
                return str(tex_path)
                
        finally:
            os.chdir(old_cwd)

    def run_conversion(self) -> str:
        """运行完整的转换流程"""
        logger.info("=" * 60)
        logger.info("开始智慧水利教材转换 v6.0")
        logger.info("=" * 60)
        
        try:
            # 输出环境信息
            logger.info(f"工作目录: {os.getcwd()}")
            logger.info(f"脚本目录: {self.script_dir}")
            logger.info(f"项目根目录: {self.project_root}")
            logger.info(f"源目录: {self.source_dir}")
            logger.info(f"输出目录: {self.output_dir}")
            
            # 检查目录是否存在
            if not self.source_dir.exists():
                raise FileNotFoundError(f"源目录不存在: {self.source_dir}")
            
            # 1. 发现文件
            files = self.discover_files()
            if not files:
                raise ValueError("未找到任何需要转换的文件")
            
            # 2. 复制图片
            self.copy_images()
            
            # 3. 合并文件
            merged_content = self.merge_files(files)
            
            # 4. 保存调试信息
            debug_file = self.output_dir / 'debug_merged.md'
            debug_file.write_text(merged_content[:10000], encoding='utf-8')  # 只保存前10000字符用于调试
            
            # 5. 转换为LaTeX
            tex_file = self.convert_to_latex(merged_content)
            
            # 6. 编译PDF
            result_file = self.compile_pdf(tex_file)
            
            logger.info("=" * 60)
            logger.info(f"转换完成！输出文件: {result_file}")
            logger.info("=" * 60)
            
            return result_file
            
        except Exception as e:
            logger.error(f"转换过程出错: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            raise

def main():
    """主函数"""
    try:
        converter = RobustTextbookConverter()
        result = converter.run_conversion()
        print(f"\n转换完成！输出文件: {result}")
        return 0
    except Exception as e:
        print(f"\n转换失败: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
