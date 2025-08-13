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
        
        # 查找章节目录
        chapter_dirs = glob.glob(os.path.join(source_dir, "第*章*"))
        chapter_dirs.sort()
        
        for chapter_dir in chapter_dirs:
            if os.path.isdir(chapter_dir):
                # 查找章节内的markdown文件
                md_files = glob.glob(os.path.join(chapter_dir, "*.md"))
                md_files.sort()
                markdown_files.extend(md_files)
        
        # 查找根目录的markdown文件
        root_md_files = glob.glob(os.path.join(source_dir, "*.md"))
        
        # 过滤掉README等文件
        filtered_files = [f for f in root_md_files 
                         if not os.path.basename(f).lower().startswith(('readme', 'summary'))]
        
        markdown_files.extend(filtered_files)
        
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
        """转换为LaTeX格式"""
        print(f"开始转换为LaTeX：{output_file}")
        
        if not self.available_tools['pandoc']:
            print("错误：Pandoc不可用，无法转换")
            return False
        
        # 构建pandoc命令
        cmd = ['pandoc'] + input_files + ['-o', output_file]
        cmd.extend(self.config['pandoc_options'])
        cmd.extend([
            '--from=markdown',
            '--to=latex',
            '--pdf-engine=' + self.config['latex_engine'],
            '--variable=documentclass:ctexbook',
            '--variable=geometry:margin=2.5cm',
            '--variable=fontsize:12pt',
            '--variable=linestretch:1.5',
            '--listings'
        ])
        
        # 添加模板文件
        template_file = os.path.join(self.config['template_dir'], '基础配置模板.tex')
        if os.path.exists(template_file):
            cmd.extend(['--template', template_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✓ Pandoc转换成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Pandoc转换失败：{e}")
            print(f"错误输出：{e.stderr}")
            return False
    
    def postprocess_latex(self, latex_file: str) -> bool:
        """后处理LaTeX文件"""
        print("开始后处理LaTeX文件...")
        
        with open(latex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加代码高亮配置
        if self.config['postprocessing']['add_listings_config']:
            content = self.add_listings_config(content)
        
        # 修复中文字体
        if self.config['postprocessing']['fix_chinese_fonts']:
            content = self.fix_chinese_fonts(content)
        
        # 优化布局
        if self.config['postprocessing']['beautify_layout']:
            content = self.beautify_layout(content)
        
        # 保存处理后的文件
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ LaTeX后处理完成")
        return True
    
    def add_listings_config(self, content: str) -> str:
        """添加代码高亮配置"""
        config_file = os.path.join(self.config['template_dir'], '代码高亮配置.tex')
        if os.path.exists(config_file):
            # 在usepackage{listings}后添加配置
            content = content.replace(
                r'\usepackage{listings}',
                r'\usepackage{listings}' + '\n' + r'\input{' + config_file + '}'
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
        content = re.sub(
            r'(\\documentclass\[.*?\]\{ctexbook\})',
            r'\1' + font_config,
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
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"编译失败：{result.stderr}")
                    return False
            
            print("✓ PDF编译成功")
            return True
            
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
