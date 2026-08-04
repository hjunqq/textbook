#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节PDF转换工具 - 将处理好的章节Markdown转换为LaTeX和PDF
"""

import os
import sys
import subprocess
from pathlib import Path

class ChapterPDFConverter:
    """章节PDF转换器"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        self.output_dir = script_dir / "output"
        self.chapter_output_dir = self.output_dir / "chapters"
        
        # 章节标题映射
        self.chapter_titles = {
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
\usepackage{fancyhdr}

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

% 页眉页脚
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{智慧水利平台架构与开发}
\fancyhead[R]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

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
    basicstyle=\ttfamily\footnotesize,
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
    aboveskip=8pt,
    belowskip=8pt,
    xleftmargin=8pt,
    xrightmargin=8pt,
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{gray!70}\itshape,
    stringstyle=\color{red!80},
    identifierstyle=\color{black}
}

% 图片设置
\graphicspath{{../images/}}

% 超链接设置
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=cyan,
    pdftitle={智慧水利平台架构与开发},
    pdfauthor={教材编写组}
}

\begin{document}

% 正文内容
$body$

\end{document}
"""
        return template
    
    def convert_chapter_to_latex(self, chapter_id: str) -> str:
        """将章节转换为LaTeX"""
        chapter_md = self.chapter_output_dir / f"{chapter_id}.md"
        chapter_tex = self.chapter_output_dir / f"{chapter_id}.tex"
        
        if not chapter_md.exists():
            raise FileNotFoundError(f"章节Markdown文件不存在: {chapter_md}")
        
        # 创建模板
        template = self.create_chapter_template()
        template_path = self.chapter_output_dir / f"{chapter_id}_template.tex"
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"转换章节 {chapter_id} 到LaTeX...")
        
        # 执行Pandoc转换 - 使用成功版本的确切命令参数
        pandoc_cmd = [
            'pandoc',
            str(chapter_md),
            '--template', str(template_path),
            '--to', 'latex',  # 明确指定输出为LaTeX
            '--no-highlight',  # 禁用Pandoc的语法高亮
            '--toc',
            # 注意：不使用 --number-sections，因为我们手工管理编号
            '--variable', 'geometry:margin=2.5cm',
            '--variable', 'fontsize=12pt',
            '--variable', 'mainfont=SimSun',
            '--variable', 'CJKmainfont=SimSun',
            '-o', str(chapter_tex)
        ]
        
        try:
            result = subprocess.run(pandoc_cmd, capture_output=True, text=True, 
                                  check=True, cwd=self.output_dir)
            print(f"✅ LaTeX转换成功: {chapter_tex}")
            
            # 清理临时模板文件
            if template_path.exists():
                template_path.unlink()
            
            return str(chapter_tex)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ LaTeX转换失败: {e}")
            print(f"错误输出: {e.stderr}")
            raise
    
    def compile_chapter_pdf(self, chapter_id: str) -> str:
        """编译章节PDF"""
        chapter_tex = self.chapter_output_dir / f"{chapter_id}.tex"
        chapter_pdf = self.chapter_output_dir / f"{chapter_id}.pdf"
        
        if not chapter_tex.exists():
            raise FileNotFoundError(f"章节LaTeX文件不存在: {chapter_tex}")
        
        print(f"编译章节 {chapter_id} PDF...")
        
        # 切换到章节输出目录
        original_dir = os.getcwd()
        os.chdir(self.chapter_output_dir)
        
        try:
            # 编译PDF（两次以处理交叉引用）
            for i in range(2):
                cmd = ['xelatex', '-interaction=nonstopmode', f"{chapter_id}.tex"]
                env = os.environ.copy()
                env['LC_ALL'] = 'C.UTF-8'
                
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      encoding='utf-8', errors='ignore', env=env)
                
                if result.returncode != 0:
                    print(f"⚠️  编译警告（第{i+1}次）")
                    if i == 1:  # 最后一次检查
                        if chapter_pdf.exists():
                            print(f"✅ PDF已生成（有警告）: {chapter_pdf}")
                            break
                        else:
                            print(f"❌ PDF编译失败")
                            # 显示部分日志
                            log_file = self.chapter_output_dir / f"{chapter_id}.log"
                            if log_file.exists():
                                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    log_content = f.read()
                                    # 查找错误行
                                    error_lines = [line for line in log_content.split('\n') 
                                                 if 'error' in line.lower() or '!' in line]
                                    if error_lines:
                                        print("关键错误信息:")
                                        for line in error_lines[-5:]:  # 显示最后5个错误
                                            print(f"  {line}")
                            raise subprocess.CalledProcessError(result.returncode, cmd)
                else:
                    print(f"✅ 编译成功（第{i+1}次）")
            
            if chapter_pdf.exists():
                size_kb = chapter_pdf.stat().st_size // 1024
                print(f"✅ PDF生成成功: {chapter_pdf} ({size_kb} KB)")
                return str(chapter_pdf)
            else:
                raise FileNotFoundError("PDF文件未生成")
                
        finally:
            os.chdir(original_dir)
    
    def process_chapter(self, chapter_id: str) -> None:
        """处理单个章节的完整转换流程"""
        if chapter_id not in self.chapter_titles:
            raise ValueError(f"未知章节: {chapter_id}")
        
        print(f"处理章节: {chapter_id} - {self.chapter_titles[chapter_id]}")
        print("=" * 60)
        
        try:
            # 转换为LaTeX
            tex_file = self.convert_chapter_to_latex(chapter_id)
            
            # 编译PDF
            pdf_file = self.compile_chapter_pdf(chapter_id)
            
            print("=" * 60)
            print(f"章节 {chapter_id} 转换完成！")
            print(f"LaTeX文件: {tex_file}")
            print(f"PDF文件: {pdf_file}")
            print("=" * 60)
            
        except Exception as e:
            print(f"章节 {chapter_id} 转换失败: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    converter = ChapterPDFConverter()
    
    if len(sys.argv) < 2:
        print("章节PDF转换工具")
        print("=" * 30)
        print("使用方法:")
        print("  python chapter_to_pdf.py <chapter_id>")
        print("  python chapter_to_pdf.py chapter01")
        print("\n或者:")
        print("  python chapter_to_pdf.py all")
        return
    
    chapter_arg = sys.argv[1].lower()
    
    if chapter_arg == 'all':
        # 处理所有章节
        for chapter_id in converter.chapter_titles.keys():
            chapter_md = converter.chapter_output_dir / f"{chapter_id}.md"
            if chapter_md.exists():
                try:
                    converter.process_chapter(chapter_id)
                except Exception as e:
                    print(f"章节 {chapter_id} 处理失败: {e}")
                    continue
            else:
                print(f"跳过章节 {chapter_id}：Markdown文件不存在")
    else:
        # 处理单个章节
        converter.process_chapter(chapter_arg)

if __name__ == '__main__':
    main()