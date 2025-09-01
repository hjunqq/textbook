#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的章节转换器，修复结构和表格问题
"""

import os
import re
import sys
import logging
import subprocess
from pathlib import Path
from latex_config import (
    CHAPTER_MAPPING, 
    LATEX_TEMPLATE, 
    ADMONITION_PATTERNS,
    PANDOC_ARGS
)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedChapterConverter:
    """改进的章节转换器，修复结构和表格问题"""
    
    def __init__(self, source_dir: str = None, output_dir: str = None):
        """初始化转换器"""
        self.source_dir = Path(source_dir) if source_dir else Path(__file__).parent.parent.parent / 'docs'
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / '逐章节输出'
        
        # 从配置文件获取章节映射
        self.chapter_mapping = CHAPTER_MAPPING
        
        logger.info(f"初始化完成 - 源目录: {self.source_dir}, 输出目录: {self.output_dir}")
    
    def get_latex_template(self) -> str:
        """获取LaTeX模板"""
        return LATEX_TEMPLATE
    
    def clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        # 转换特殊块语法
        content = self.convert_admonitions(content)
        # 修复表格
        content = self.fix_tables(content)
        return content.strip()
    
    def fix_tables(self, content: str) -> str:
        """修复Markdown表格为LaTeX格式"""
        # 匹配markdown表格
        table_pattern = r'(\|[^\n]+\|\n\|[-:|\s]+\|\n(?:\|[^\n]+\|\n?)+)'
        
        def convert_table(match):
            table_text = match.group(1)
            lines = table_text.strip().split('\n')
            
            if len(lines) < 3:
                return table_text  # 不是完整表格
            
            # 解析表头
            header_line = lines[0]
            # separator_line = lines[1]  # 分隔符行（不需要使用）
            data_lines = lines[2:]
            
            # 提取表头
            headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
            
            # 计算列数
            col_count = len(headers)
            
            # 生成LaTeX表格
            latex_table = "\\begin{table}[htbp]\n"
            latex_table += "\\centering\n"
            latex_table += f"\\begin{{tabular}}{{{('|l' * col_count) + '|'}}}\n"
            latex_table += "\\hline\n"
            
            # 添加表头
            latex_table += " & ".join(f"\\textbf{{{header}}}" for header in headers) + " \\\\\n"
            latex_table += "\\hline\n"
            
            # 添加数据行
            for line in data_lines:
                if line.strip():
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(cells) == col_count:
                        latex_table += " & ".join(cells) + " \\\\\n"
                        latex_table += "\\hline\n"
            
            latex_table += "\\end{tabular}\n"
            latex_table += "\\end{table}\n"
            
            return latex_table
        
        return re.sub(table_pattern, convert_table, content)
    
    def convert_admonitions(self, content: str) -> str:
        """转换特殊块语法"""
        for adm_type, config in ADMONITION_PATTERNS.items():
            pattern = config['pattern']
            color = config['color'] 
            title_default = config['title_default']
            
            def replacement_func(match):
                title = match.group(1) if match.group(1) else title_default
                body = match.group(2)
                
                # 处理嵌套的=== "标题"语法，转换为子标题并添加前后换行
                body = re.sub(r'^\s*=== "([^"]*)"', r'\n\n\\textbf{\1}\n\n', body, flags=re.MULTILINE)
                
                # 移除缩进（通常是4个空格）
                body = re.sub(r'^    ', '', body, flags=re.MULTILINE)
                
                # 确保段落之间有适当的空行，但避免开头有多余空行
                body = re.sub(r'\n\n\n+', r'\n\n', body)
                body = body.strip()
                
                return f'''\\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={title}]
{body}
\\end{{tcolorbox}}

'''
            
            content = re.sub(pattern, replacement_func, content)
        
        return content
    
    def reorganize_chapter_structure(self, content: str) -> str:
        """重新组织章节结构"""
        # 分离不同部分
        parts = {
            'title': '',
            'learning_objectives': '',
            'introduction': '',
            'chapter_overview': '',
            'key_concepts': '',
            'sections': '',
            'summary': ''
        }
        
        # 提取标题
        title_match = re.search(r'^# (.+)', content, re.MULTILINE)
        if title_match:
            parts['title'] = f"# {title_match.group(1)}\n\n"
        
        # 提取学习目标
        learning_obj_pattern = r'## 学习目标\n(.*?)(?=##|\Z)'
        learning_match = re.search(learning_obj_pattern, content, re.DOTALL)
        if learning_match:
            parts['learning_objectives'] = f"## 学习目标\n\n{learning_match.group(1).strip()}\n\n"
        
        # 提取引言
        intro_pattern = r'## 引言\n(.*?)(?=##|\Z)'
        intro_match = re.search(intro_pattern, content, re.DOTALL)
        if intro_match:
            parts['introduction'] = f"## 引言\n\n{intro_match.group(1).strip()}\n\n"
        
        # 提取本章小节
        overview_pattern = r'## 本章小节\n(.*?)(?=##|\Z)'
        overview_match = re.search(overview_pattern, content, re.DOTALL)
        if overview_match:
            parts['chapter_overview'] = f"## 本章概览\n\n{overview_match.group(1).strip()}\n\n"
        
        # 提取关键概念
        concepts_pattern = r'## 关键概念\n(.*?)(?=##|\Z)'
        concepts_match = re.search(concepts_pattern, content, re.DOTALL)
        if concepts_match:
            parts['key_concepts'] = f"## 关键概念\n\n{concepts_match.group(1).strip()}\n\n"
        
        # 提取所有1.x节的内容
        sections_content = ""
        section_pattern = r'(## 1\.\d+.*?)(?=## 1\.\d+|## \d+\.\d+|## [^1]|\Z)'
        for match in re.finditer(section_pattern, content, re.DOTALL):
            sections_content += match.group(1) + "\n\n"
        
        if sections_content:
            parts['sections'] = sections_content.strip() + "\n\n"
        
        # 提取小结（通常在最后）
        summary_pattern = r'## (?:1\.3 )?小结\n(.*?)(?=##|\Z)'
        summary_match = re.search(summary_pattern, content, re.DOTALL)
        if summary_match:
            parts['summary'] = f"## 本章小结\n\n{summary_match.group(1).strip()}\n\n"
        
        # 重新组织内容
        reorganized = ""
        reorganized += parts['title']
        reorganized += parts['learning_objectives']
        reorganized += parts['introduction']
        reorganized += parts['chapter_overview']
        reorganized += parts['key_concepts']
        reorganized += parts['sections']
        reorganized += parts['summary']
        
        return reorganized.strip()
    
    def convert_chapter(self, chapter_key: str) -> bool:
        """转换单个章节，支持多文件"""
        if chapter_key not in self.chapter_mapping:
            logger.error(f"未知章节: {chapter_key}")
            return False
        
        chapter_info = self.chapter_mapping[chapter_key]
        logger.info(f"开始转换章节: {chapter_info['title']}")
        
        # 创建输出目录
        chapter_output_dir = self.output_dir / chapter_key
        chapter_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 合并多个文件内容
        combined_content = ""
        
        # 检查是否有多个文件
        if 'files' in chapter_info:
            # 多文件章节
            for file_path in chapter_info['files']:
                source_file = self.source_dir / file_path
                if not source_file.exists():
                    logger.error(f"源文件不存在: {source_file}")
                    return False
                
                logger.info(f"处理文件: {file_path}")
                file_content = source_file.read_text(encoding='utf-8')
                
                # 对每个文件进行基本清理
                file_content = self.clean_content(file_content)
                
                # 添加到合并内容中
                if combined_content:
                    combined_content += "\n\n"
                combined_content += file_content
        else:
            # 单文件章节
            source_file = self.source_dir / chapter_info['file']
            if not source_file.exists():
                logger.error(f"源文件不存在: {source_file}")
                return False
            
            logger.info(f"处理主文件: {chapter_info['file']}")
            combined_content = source_file.read_text(encoding='utf-8')
            combined_content = self.clean_content(combined_content)
        
        # 重新组织章节结构
        combined_content = self.reorganize_chapter_structure(combined_content)
        
        # 保存重组后的Markdown
        md_file = chapter_output_dir / f"{chapter_key}.md"
        md_file.write_text(combined_content, encoding='utf-8')
        logger.info(f"保存重组的Markdown文件: {md_file}")
        
        # 转换为LaTeX
        tex_file = chapter_output_dir / f"{chapter_key}.tex"
        if not self.convert_to_latex(md_file, tex_file):
            return False
        
        # 生成PDF
        pdf_file = chapter_output_dir / f"{chapter_key}.pdf"
        if not self.compile_latex(tex_file, pdf_file):
            return False
        
        logger.info(f"章节 {chapter_info['title']} 转换成功: {pdf_file}")
        return True
    
    def convert_to_latex(self, md_file: Path, tex_file: Path) -> bool:
        """使用Pandoc转换为LaTeX"""
        try:
            logger.info("开始Pandoc转换...")
            
            # 先生成基本的LaTeX内容
            temp_tex = tex_file.with_suffix('.temp.tex')
            
            cmd = ['pandoc', str(md_file), '-o', str(temp_tex)] + PANDOC_ARGS
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                logger.info("Pandoc转换成功")
                
                # 读取生成的LaTeX内容
                tex_content = temp_tex.read_text(encoding='utf-8')
                
                # 手动修复标题层次
                tex_content = self.fix_heading_levels(tex_content)
                
                # 应用自定义模板
                template = self.get_latex_template()
                
                # 替换模板中的占位符
                final_content = template.replace('CONTENT_PLACEHOLDER', tex_content)
                tex_file.write_text(final_content, encoding='utf-8')
                
                # 清理临时文件
                temp_tex.unlink()
                
                logger.info("已应用LaTeX模板")
                return True
            else:
                logger.error(f"Pandoc转换失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"转换过程出错: {e}")
            return False
    
    def fix_heading_levels(self, latex_content: str) -> str:
        """修复标题层次，将章标题转换为chapter，其他保持为section"""
        lines = latex_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 检查是否是section标题
            if re.match(r'\\section\{', line):
                # 如果包含"第X章"，转换为chapter
                if re.search(r'第\d+章|第[一二三四五六七八九十]+章', line):
                    line = re.sub(r'\\section\{([^}]*)\}\\label\{[^}]*\}', r'\\chapter{\1}', line)
                    line = re.sub(r'\\section\{([^}]*)\}', r'\\chapter{\1}', line)
                # 其他section保持不变
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def compile_latex(self, tex_file: Path, pdf_file: Path) -> bool:
        """编译LaTeX为PDF"""
        try:
            os.chdir(tex_file.parent)
            
            logger.info("使用XeLaTeX编译...")
            
            # 第一次编译
            cmd = ['xelatex', '-interaction=nonstopmode', tex_file.name]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                logger.warning("第一次编译有警告")
            
            # 第二次编译（确保目录正确）
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if pdf_file.exists():
                logger.info(f"PDF编译成功: {pdf_file}")
                return True
            else:
                logger.error("PDF文件未生成")
                return False
                
        except Exception as e:
            logger.error(f"LaTeX编译出错: {e}")
            return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python improved_converter.py <chapter_key>")
        print("可用章节: preface, chapter01, chapter02, chapter03")
        sys.exit(1)
    
    chapter_key = sys.argv[1]
    converter = ImprovedChapterConverter()
    
    if converter.convert_chapter(chapter_key):
        print(f"章节 {chapter_key} 转换完成")
    else:
        print(f"章节 {chapter_key} 转换失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
