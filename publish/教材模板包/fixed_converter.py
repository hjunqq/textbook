#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版本的章节转换器
解决Markdown和LaTeX混合、空章节等问题
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
    PANDOC_ARGS
)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedChapterConverter:
    """修复版章节转换器"""
    
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
        """清理内容，但保持纯Markdown格式"""
        # 移除HTML注释
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # 确保段落之间有适当的空行
        content = re.sub(r'\n\n\n+', r'\n\n', content)
        
        return content.strip()
    
    def convert_admonitions(self, content: str) -> str:
        """转换admonition语法为tcolorbox占位符"""
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 检查是否是admonition开始
            admonition_match = re.match(r'^!!!\s+(\w+)\s*(?:"([^"]*)")?', line)
            if admonition_match:
                admonition_type = admonition_match.group(1)
                title = admonition_match.group(2) if admonition_match.group(2) else admonition_type
                
                # 颜色映射
                color_map = {
                    'note': 'blue',
                    'tip': 'green', 
                    'warning': 'orange',
                    'danger': 'red',
                    'info': 'cyan',
                    'important': 'red'
                }
                color = color_map.get(admonition_type, 'blue')
                
                # 开始占位符
                result_lines.append(f'TCOLORBOX_START_{color}_{title}_TCOLORBOX_TITLE')
                
                # 收集admonition内容
                i += 1
                admonition_content = []
                
                while i < len(lines):
                    next_line = lines[i]
                    
                    # 如果遇到新的标题（同级或更高级），结束admonition
                    if re.match(r'^#', next_line):
                        break
                    
                    # 如果遇到新的admonition，结束当前admonition
                    if re.match(r'^!!!\s+\w+', next_line):
                        break
                    
                    # 如果是缩进内容，移除缩进并添加
                    if next_line.startswith('    '):
                        admonition_content.append(next_line[4:])  # 移除4个空格的缩进
                    elif not next_line.strip():  # 空行
                        admonition_content.append('')
                    else:
                        # 非缩进非空行，可能是admonition结束
                        break
                    
                    i += 1
                
                # 添加内容并清理多余空行
                if admonition_content:
                    # 移除开头和结尾的空行
                    while admonition_content and not admonition_content[0].strip():
                        admonition_content.pop(0)
                    while admonition_content and not admonition_content[-1].strip():
                        admonition_content.pop()
                    
                    result_lines.extend(admonition_content)
                
                # 结束占位符
                result_lines.append('TCOLORBOX_END')
                continue
            
            result_lines.append(line)
            i += 1
            
        return '\n'.join(result_lines)
    
    def reorganize_chapter_structure(self, content: str) -> str:
        """重新组织章节结构，保持纯Markdown格式"""
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
        
        # 提取本章小节/概览（包含完整的tcolorbox块）
        overview_pattern = r'## 本章(?:小节|概览)\n(.*?)(?=^## 关键概念|\Z)'
        overview_match = re.search(overview_pattern, content, re.DOTALL | re.MULTILINE)
        if overview_match:
            overview_content = overview_match.group(1).strip()
            # 确保内容是纯Markdown格式
            parts['chapter_overview'] = f"## 本章概览\n\n{overview_content}\n\n"
        
        # 提取关键概念
        concepts_pattern = r'## 关键概念\n(.*?)(?=##|\Z)'
        concepts_match = re.search(concepts_pattern, content, re.DOTALL)
        if concepts_match:
            concepts_content = concepts_match.group(1).strip()
            parts['key_concepts'] = f"## 关键概念\n\n{concepts_content}\n\n"
        
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
                
                # 清理单个文件内容
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
        
        # 处理特殊块语法
        combined_content = self.convert_admonitions(combined_content)
        
        # 重新组织结构
        reorganized_content = self.reorganize_chapter_structure(combined_content)
        
        # 保存重组后的Markdown
        md_file = chapter_output_dir / f"{chapter_key}.md"
        md_file.write_text(reorganized_content, encoding='utf-8')
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
                
                # 修复标题层次和清理问题
                tex_content = self.fix_latex_content(tex_content)
                
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
    
    def fix_latex_content(self, latex_content: str) -> str:
        """修复LaTeX内容中的问题"""
        # 恢复tcolorbox占位符（处理Pandoc转义的下划线）
        latex_content = re.sub(
            r'TCOLORBOX\\?_START\\?_([^\\]+)\\?_([^\\]+)\\?_TCOLORBOX\\?_TITLE(.*?)TCOLORBOX\\?_END',
            lambda m: f'\\begin{{tcolorbox}}[colback={m.group(1)}!5!white,colframe={m.group(1)}!75!black,title={m.group(2)}]\n{m.group(3).strip()}\n\\end{{tcolorbox}}',
            latex_content,
            flags=re.DOTALL
        )
        
        lines = latex_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 跳过空的章节
            if re.match(r'^\\chapter\{\}\s*\\label\{.*\}?$', line.strip()):
                continue
            
            # 清理Markdown语法残留
            line = re.sub(r'\\#\\#\\#', r'', line)
            line = re.sub(r'\\#\\#', r'', line) 
            line = re.sub(r'\\#', r'', line)
            
            # 清理链接格式（将href转换为简单文本）
            line = re.sub(r'\\href\{[^}]+\}\{([^}]+)\}', r'\\textbf{\1}', line)
            
            # 将第一个包含"第X章"的section转换为chapter
            if re.match(r'^\\section\{', line) and re.search(r'第\d+章|第[一二三四五六七八九十]+章', line):
                line = re.sub(r'^\\section\{([^}]*)\}\\label\{[^}]*\}?', r'\\chapter{\1}', line)
                line = re.sub(r'^\\section\{([^}]*)\}', r'\\chapter{\1}', line)
            
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
        print("用法: python fixed_converter.py <chapter_key>")
        print("可用章节: preface, chapter01, chapter02, chapter03")
        sys.exit(1)
    
    chapter_key = sys.argv[1]
    converter = FixedChapterConverter()
    
    if converter.convert_chapter(chapter_key):
        print(f"章节 {chapter_key} 转换完成")
    else:
        print(f"章节 {chapter_key} 转换失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
