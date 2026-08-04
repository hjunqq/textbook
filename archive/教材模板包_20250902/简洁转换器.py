#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材简洁转换器
一键解决所有LaTeX转换问题
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

class SimpleTextbookConverter:
    def __init__(self):
        self.project_root = Path.cwd()
        self.source_dir = self.project_root / "docs"
        self.output_dir = self.project_root / "publish" / "教材模板包" / "输出"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def discover_files(self):
        """发现所有Markdown文件"""
        files = []
        
        # 前言
        preface = self.source_dir / "前言.md"
        if preface.exists():
            files.append(str(preface))
            
        # 章节文件
        chapters_dir = self.source_dir / "chapters"
        if chapters_dir.exists():
            for i in range(1, 10):
                chapter_dir = chapters_dir / f"chapter{i:02d}"
                if chapter_dir.exists():
                    # 主章节文件
                    main_file = chapter_dir / f"chapter{i:02d}.md"
                    if main_file.exists():
                        files.append(str(main_file))
                    
                    # 节文件
                    for section_file in sorted(chapter_dir.glob("section*.md")):
                        files.append(str(section_file))
        
        # 附录
        appendix_dir = self.project_root / "appendix"
        if appendix_dir.exists():
            for appendix_file in sorted(appendix_dir.glob("*.md")):
                files.append(str(appendix_file))
                
        print(f"发现 {len(files)} 个文件")
        return files
    
    def process_markdown(self, content):
        """处理Markdown内容"""
        # 1. 修复图片路径
        content = re.sub(r'!\[([^\]]*)\]\([^)]*?([^/\s]+\.(png|jpg|jpeg|gif|svg))\)', r'![\1](images/\2)', content, flags=re.IGNORECASE)
        
        # 2. 转换特殊块 - 简化处理
        content = re.sub(r'!!! (\w+)(?:\s+"([^"]*)")?\s*\n((?:    .*\n?)*)', 
                        lambda m: f'\\begin{{tcolorbox}}[title=\\textbf{{{m.group(1).upper()}{f": {m.group(2)}" if m.group(2) else ""}}}]\n{(m.group(3) or "").replace("    ", "")}\n\\end{{tcolorbox}}\n', 
                        content, flags=re.MULTILINE)
        
        # 3. 清理多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def create_simple_template(self):
        """创建简洁的LaTeX模板"""
        return r"""
\documentclass[12pt,a4paper]{book}

\usepackage[UTF8]{ctex}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{listings}
\usepackage{longtable}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{url}

\geometry{margin=2.5cm}
\graphicspath{{images/}}

% 修复命令
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 代码设置
\lstset{
    basicstyle=\ttfamily\small,
    backgroundcolor=\color{gray!10},
    frame=single,
    breaklines=true,
    showstringspaces=false
}

\title{智慧水利平台架构与开发}
\author{教材编写组}

\begin{document}
\maketitle
\tableofcontents
\cleardoublepage

$body$

\end{document}
"""
    
    def fix_latex_content(self, content):
        """修复LaTeX内容中的所有问题"""
        print("修复LaTeX内容...")
        
        # 1. 修复章节级别 - 将第X章转换为chapter级别
        content = re.sub(r'\\section\{第([一二三四五六七八九])章([^}]*)\}', r'\\chapter{第\1章\2}', content)
        content = re.sub(r'\\section\{第([0-9]+)章([^}]*)\}', r'\\chapter{第\1章\2}', content)
        
        # 2. 修复表格 - 统一处理所有表格定义问题
        content = re.sub(r'\\begin\{longtable\}[^\{]*\{[^}]*\}', r'\\begin{longtable}{|l|l|l|}', content)
        content = re.sub(r'\\begin\{longtable\}\[[^\]]*\]\{[^}]*\}', r'\\begin{longtable}{|l|l|l|}', content)
        
        # 3. 修复表格头部和分割线
        content = re.sub(r'\\toprule.*?(?=\\midrule|\\bottomrule|\\\\)', r'\\hline', content, flags=re.DOTALL)
        content = re.sub(r'\\midrule.*?(?=\\bottomrule|\\\\)', r'\\hline', content, flags=re.DOTALL) 
        content = re.sub(r'\\bottomrule.*?(?=\\end|\\\\)', r'\\hline', content, flags=re.DOTALL)
        content = re.sub(r'\\endhead|\\endlastfoot|\\endfoot', '', content)
        
        # 4. 修复图片引用
        content = re.sub(r'\\includegraphics\{([^}]+)\}', r'\\includegraphics[width=0.8\\textwidth]{\1}', content)
        content = re.sub(r'\\includegraphics\[width=[^]]*\]\[width=[^]]*\]', r'\\includegraphics[width=0.8\\textwidth]', content)
        
        # 5. 清理所有问题命令和引用
        content = re.sub(r'\\[0-9]+', '', content)  # 清理错误引用
        content = re.sub(r'\\fa[A-Z][A-Za-z]*\\?', '\\textbf{※}', content)  # 替换FontAwesome
        
        # 6. 修复前言
        content = re.sub(r'\\chapter\{前言\}', r'\\chapter*{前言}', content)
        
        # 7. 修复特殊块中的问题
        content = re.sub(r'title=.*?\\\\1.*?\]', 'title=\\textbf{注意}]', content)
        content = re.sub(r'title=.*?\\1.*?\]', 'title=\\textbf{注意}]', content)
        
        # 8. 清理空的或破损的环境
        content = re.sub(r'\\begin\{[^}]+\}\s*\\end\{[^}]+\}', '', content)
        content = re.sub(r'\\begin\{tcolorbox\}\[[^\]]*\]\s*\\end\{tcolorbox\}', '', content)
        
        # 9. 修复URL格式
        content = re.sub(r'\\url\s*\{([^}]*)\}', r'\\url{\1}', content)
        
        # 10. 最终清理
        content = re.sub(r'\n{4,}', '\n\n', content)  # 清理多余空行
        content = re.sub(r'\\\\1|\\\\2', '', content)  # 清理剩余的错误引用
        
        return content
    
    def convert(self):
        """执行转换"""
        print("=" * 50)
        print("智慧水利教材简洁转换器")
        print("=" * 50)
        
        # 1. 发现文件
        files = self.discover_files()
        if not files:
            print("❌ 未找到Markdown文件")
            return
            
        # 2. 合并内容
        print("合并Markdown文件...")
        merged_content = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                processed_content = self.process_markdown(content)
                merged_content.append(processed_content)
            except Exception as e:
                print(f"⚠️ 跳过文件 {file_path}: {e}")
                
        full_content = '\n\n\\newpage\n\n'.join(merged_content)
        
        # 3. 创建临时Markdown文件
        temp_md = self.output_dir / "temp.md"
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(full_content)
            
        # 4. 创建模板
        template_path = self.output_dir / "template.tex"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(self.create_simple_template())
            
        # 5. Pandoc转换
        print("转换为LaTeX...")
        output_tex = self.output_dir / "教材.tex"
        
        try:
            cmd = [
                'pandoc', str(temp_md),
                '--template', str(template_path),
                '--to', 'latex',
                '--output', str(output_tex)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ Pandoc转换成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ Pandoc转换失败: {e}")
            return
        except FileNotFoundError:
            print("❌ 未找到pandoc命令，请先安装pandoc")
            return
            
        # 6. 修复LaTeX文件
        with open(output_tex, 'r', encoding='utf-8') as f:
            latex_content = f.read()
            
        fixed_content = self.fix_latex_content(latex_content)
        
        with open(output_tex, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
            
        # 7. 清理临时文件
        temp_md.unlink()
        
        print("=" * 50)
        print("✅ 转换完成!")
        print(f"📄 输出文件: {output_tex}")
        print(f"📏 文件大小: {output_tex.stat().st_size / 1024:.1f} KB")
        print("💡 现在可以使用LaTeX编译器编译该文件")
        print("=" * 50)

def main():
    converter = SimpleTextbookConverter()
    converter.convert()

if __name__ == "__main__":
    main()