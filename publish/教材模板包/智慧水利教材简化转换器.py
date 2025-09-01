#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材简化转换器
避免Pandoc YAML解析问题，直接生成基础LaTeX
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class SmartWaterTextbookConverterSimple:
    """智慧水利教材转换器 - 简化版"""
    
    def __init__(self):
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
        
        print("智慧水利教材简化转换器初始化完成")
    
    def discover_chapters(self) -> List[str]:
        """发现并排序章节文件"""
        chapters_dir = self.source_dir / "chapters"
        if not chapters_dir.exists():
            raise FileNotFoundError(f"章节目录不存在: {chapters_dir}")
            
        chapter_files = []
        
        # 添加前言
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
    
    def copy_images(self):
        """复制图片文件"""
        possible_source_dirs = [
            self.source_dir / "assets" / "images",
            self.source_dir / "chapters" / "images",
            self.project_root / "参考" / "extracted_images_ch6",
            self.project_root / "参考" / "images"
        ]
        
        copied_count = 0
        print("🖼️  开始复制图片文件...")
        
        for source_images_dir in possible_source_dirs:
            if not source_images_dir.exists():
                continue
                
            print(f"   检查目录: {source_images_dir}")
            
            for image_file in source_images_dir.rglob("*"):
                if image_file.is_file() and image_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp', '.wmf', '.emf']:
                    try:
                        if 'extracted_images_ch6' in str(image_file):
                            new_name = f"ch6_{image_file.name}"
                        else:
                            new_name = image_file.name
                            
                        target_path = self.images_dir / new_name
                        
                        if target_path.exists():
                            continue
                            
                        shutil.copy2(image_file, target_path)
                        copied_count += 1
                        
                    except Exception as e:
                        print(f"   ❌ 复制失败 {image_file}: {e}")
        
        if copied_count == 0:
            self.create_placeholder_images()
        else:
            print(f"✅ 图片复制完成，共复制 {copied_count} 个文件")
    
    def create_placeholder_images(self):
        """创建占位符图片"""
        placeholder_names = [
            "placeholder.png",
            "image_001.png",
            "image_002.png",
            "image_003.png"
        ]
        
        for name in placeholder_names:
            placeholder_path = self.images_dir / name
            if not placeholder_path.exists():
                placeholder_path.write_text(f"Placeholder for {name}", encoding='utf-8')
                print(f"   创建占位符: {name}")
    
    def process_markdown_content(self, content: str, file_type: str, file_path: str) -> str:
        """处理Markdown内容，转换为LaTeX"""
        
        # 移除YAML前言
        if content.startswith('---\\n'):
            second_delimiter = content.find('\\n---\\n', 4)
            if second_delimiter != -1:
                content = content[second_delimiter + 5:]
        
        file_name = Path(file_path).name
        
        # 处理标题
        if file_type == "preface":
            content = re.sub(r'^# (.+)', r'\\chapter*{\\1}', content, count=1, flags=re.MULTILINE)
        elif file_type == "chapter":
            chapter_num = re.search(r'chapter(\\d+)', file_name)
            if chapter_num:
                chapter_key = f"chapter{chapter_num.group(1).zfill(2)}"
                if chapter_key in self.chapter_order:
                    title = self.chapter_order[chapter_key]['title']
                    content = re.sub(r'^# .+', f'\\\\chapter{{{title}}}', content, count=1, flags=re.MULTILINE)
        elif file_type == "section":
            section_match = re.search(r'section(\\d+)-(\\d+)', file_name)
            if section_match:
                chapter_num = int(section_match.group(1))
                section_num = int(section_match.group(2))
                content = re.sub(r'^# (.+)', f'\\\\section{{{chapter_num}.{section_num} \\\\1}}', content, count=1, flags=re.MULTILINE)
        
        # 转换其他标题
        content = re.sub(r'^## (.+)', r'\\\\section{\\1}', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)', r'\\\\subsection{\\1}', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.+)', r'\\\\subsubsection{\\1}', content, flags=re.MULTILINE)
        
        # 转换列表
        content = re.sub(r'^- (.+)', r'\\\\item \\1', content, flags=re.MULTILINE)
        content = re.sub(r'^\\d+\\. (.+)', r'\\\\item \\1', content, flags=re.MULTILINE)
        
        # 转换粗体和斜体
        content = re.sub(r'\\*\\*(.+?)\\*\\*', r'\\\\textbf{\\1}', content)
        content = re.sub(r'\\*(.+?)\\*', r'\\\\textit{\\1}', content)
        
        # 转换图片
        content = re.sub(r'!\\[([^\\]]*)\\]\\(([^)]+)\\)', r'\\\\includegraphics[width=0.8\\\\textwidth]{images/\\2}', content)
        
        # 转换代码块
        content = re.sub(r'```([\\w]*)\\n([\\s\\S]*?)\\n```', r'\\\\begin{verbatim}\\n\\2\\n\\\\end{verbatim}', content)
        content = re.sub(r'`([^`]+)`', r'\\\\texttt{\\1}', content)
        
        # 转换特殊块
        content = re.sub(
            r'!!! (\\w+)(?:\\s+"([^"]*)")?\\s*\\n((?:    .*\\n?)*)',
            lambda m: f'\\\\begin{{quote}}\\n\\\\textbf{{{m.group(1).upper()}{f": {m.group(2)}" if m.group(2) else ""}}}\\\\\\\\\\n{m.group(3) or ""}\\n\\\\end{{quote}}',
            content,
            flags=re.MULTILINE
        )
        
        # 清理缩进
        content = re.sub(r'^    ', '', content, flags=re.MULTILINE)
        
        return content
    
    def generate_latex_document(self, chapter_files: List[tuple]) -> str:
        """直接生成LaTeX文档"""
        
        latex_content = []
        
        # LaTeX文档头部
        latex_content.append(r"""\\documentclass[12pt,a4paper]{book}
\\usepackage[UTF8]{ctex}
\\usepackage{geometry}
\\usepackage{graphicx}
\\usepackage{xcolor}
\\usepackage{listings}
\\usepackage{hyperref}
\\usepackage{verbatim}

\\geometry{
    top=2.5cm,
    bottom=2.5cm,
    left=2.8cm,
    right=2.2cm
}

\\graphicspath{{images/}}

\\begin{document}

\\title{智慧水利平台架构与开发}
\\author{教材编写组}
\\date{\\today}
\\maketitle

\\tableofcontents
\\newpage

""")
        
        # 处理章节内容
        for file_type, file_path in chapter_files:
            print(f"处理文件: {Path(file_path).name} (类型: {file_type})")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                processed_content = self.process_markdown_content(content, file_type, file_path)
                latex_content.append(processed_content)
                latex_content.append('\\n\\n')
                
                # 在章节间添加分页
                if file_type in ["chapter", "preface"]:
                    latex_content.append('\\\\newpage\\n\\n')
                
            except Exception as e:
                print(f"错误：处理文件失败 {file_path}: {e}")
                continue
        
        # LaTeX文档结尾
        latex_content.append('\\n\\\\end{document}')
        
        return ''.join(latex_content)
    
    def compile_pdf(self, tex_file: str) -> str:
        """编译PDF"""
        tex_path = Path(tex_file)
        output_dir = tex_path.parent
        
        original_dir = os.getcwd()
        os.chdir(output_dir)
        
        try:
            print("🚀 开始PDF编译...")
            
            # 找到LaTeX编译器
            latex_commands = ['xelatex', 'pdflatex', 'lualatex']
            working_latex = None
            
            for cmd in latex_commands:
                try:
                    result = subprocess.run([cmd, '--version'], capture_output=True, text=True, encoding='utf-8')
                    if result.returncode == 0:
                        working_latex = cmd
                        print(f"   找到LaTeX编译器: {cmd}")
                        break
                except FileNotFoundError:
                    continue
            
            if not working_latex:
                print("❌ 未找到LaTeX编译器")
                return str(tex_path)
            
            # 编译LaTeX
            for i in range(2):
                print(f"📝 第{i+1}次编译...")
                
                cmd = [working_latex, '-interaction=nonstopmode', tex_path.name]
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8',
                    errors='ignore'
                )
                
                if result.returncode == 0:
                    print(f"✅ 第{i+1}次编译成功")
                else:
                    print(f"⚠️  第{i+1}次编译有警告")
            
            # 检查PDF
            pdf_path = output_dir / "教材.pdf"
            if pdf_path.exists():
                file_size = pdf_path.stat().st_size / (1024*1024)
                print(f"🎉 PDF文件生成成功!")
                print(f"📊 文件路径: {pdf_path}")
                print(f"📏 文件大小: {file_size:.1f} MB")
                return str(pdf_path)
            
            return str(tex_path)
                
        finally:
            os.chdir(original_dir)
    
    def run_conversion(self):
        """运行转换过程"""
        print("=" * 60)
        print("智慧水利教材简化转换器")
        print("=" * 60)
        
        try:
            # 1. 发现章节文件
            print("\\n1. 发现章节文件...")
            chapter_files = self.discover_chapters()
            
            # 2. 复制图片
            print("\\n2. 复制图片文件...")
            self.copy_images()
            
            # 3. 生成LaTeX
            print("\\n3. 生成LaTeX文档...")
            latex_content = self.generate_latex_document(chapter_files)
            
            # 4. 保存LaTeX文件
            tex_file = self.output_dir / "教材.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            print(f"LaTeX文件已生成: {tex_file}")
            
            # 5. 编译PDF
            print("\\n4. 编译PDF...")
            result_file = self.compile_pdf(str(tex_file))
            
            print("\\n" + "=" * 60)
            print("转换完成！")
            print("=" * 60)
            print(f"输出目录: {self.output_dir}")
            print(f"最终输出: {result_file}")
            
        except Exception as e:
            print(f"转换失败: {e}")
            raise

def main():
    converter = SmartWaterTextbookConverterSimple()
    converter.run_conversion()

if __name__ == "__main__":
    main()
