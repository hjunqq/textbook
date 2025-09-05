#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器 - 改进版主转换器
集成到现有LaTeX构建工作流程

主要改进:
1. 章节顺序修复：sections放在章节最后
2. 智能标题处理：保持现有中文标题
3. 自动内容清理：移除重复的"本章小节"
4. 图片统一管理：标准化图片路径
"""

import os
import sys
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging
from datetime import datetime

class ImprovedTextbookConverter:
    """改进的教材转换器 - 集成现有工作流程"""
    
    def __init__(self, project_root: Optional[Path] = None):
        # 设置项目路径
        if project_root:
            self.project_root = Path(project_root)
        else:
            # 自动检测项目根目录
            self.project_root = Path(__file__).parent.parent
        
        self.docs_dir = Path("./docs")
        self.latex_dir = Path("./output")
        self.output_dir = self.latex_dir / "chapters"
        
        # 设置日志
        self.setup_logging()
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"转换器初始化完成")
        self.logger.info(f"项目根目录: {self.project_root}")
        self.logger.info(f"文档目录: {self.docs_dir}")
        self.logger.info(f"LaTeX输出目录: {self.latex_dir}")
    
    def setup_logging(self):
        """设置日志系统"""
        log_file = self.project_root / "conversion.log"
        
        # 创建logger
        self.logger = logging.getLogger('TextbookConverter')
        self.logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def convert_all_chapters(self) -> bool:
        """转换所有章节 - 主入口函数"""
        self.logger.info("🚀 开始教材转换流程")
        
        try:
            # 1. 发现源文件
            chapters = self._discover_chapters()
            if not chapters:
                self.logger.error("未发现章节文件")
                return False
            
            self.logger.info(f"发现 {len(chapters)} 个章节目录")
            
            # 2. 处理前言
            self._convert_preface()
            
            # 3. 逐个转换章节（改进的顺序处理）
            for chapter_info in chapters:
                self._convert_chapter_improved(chapter_info)
            
            # 4. 处理附录
            self._convert_appendices()
            
            # 5. 处理图片
            self._process_images()
            
            self.logger.info("✅ 所有章节转换完成")
            return True
            
        except Exception as e:
            self.logger.error(f"转换过程出错: {e}")
            return False
    
    def _discover_chapters(self) -> List[Dict]:
        """发现章节目录"""
        chapters = []
        chapters_dir = self.docs_dir / "chapters"
        
        if not chapters_dir.exists():
            return chapters
        
        # 按顺序查找章节
        for i in range(1, 20):  # 支持最多19章
            chapter_key = f"chapter{i:02d}"
            chapter_dir = chapters_dir / chapter_key
            
            if chapter_dir.exists():
                chapters.append({
                    'key': chapter_key,
                    'number': i,
                    'dir': chapter_dir,
                    'main_file': chapter_dir / f"{chapter_key}.md",
                    'sections': sorted(chapter_dir.glob("section*.md"))
                })
        
        return chapters
    
    def _convert_preface(self):
        """转换前言"""
        preface_md = self.docs_dir / "前言.md"
        preface_tex = self.output_dir / "preface.tex"
        
        if preface_md.exists():
            self.logger.info("转换前言...")
            content = self._read_and_process_markdown(preface_md, 'preface')
            self._write_latex_file(preface_tex, content)
    
    def _convert_chapter_improved(self, chapter_info: Dict):
        """转换单个章节 - 改进版本"""
        chapter_key = chapter_info['key']
        chapter_number = chapter_info['number']
        chapter_dir = chapter_info['dir']
        main_file = chapter_info['main_file']
        sections = chapter_info['sections']
        
        self.logger.info(f"转换第{chapter_number}章: {chapter_key}")
        
        # 创建章节输出目录
        chapter_output_dir = self.output_dir / chapter_key
        chapter_output_dir.mkdir(exist_ok=True)
        
        # 准备合并内容
        merged_content = []
        
        # 1. 处理章节主文件 (改进：移除"本章小节"部分)
        if main_file.exists():
            self.logger.info(f"  处理主文件: {main_file.name}")
            main_content = self._read_and_process_markdown(main_file, 'chapter')
            
            # 移除"本章小节"部分
            main_content = self._remove_chapter_sections_summary(main_content)
            merged_content.append(main_content)
        
        # 2. 处理各节文件 (改进：按正确顺序添加)
        for section_file in sections:
            self.logger.info(f"  处理节文件: {section_file.name}")
            section_content = self._read_and_process_markdown(section_file, 'section')
            merged_content.append(section_content)
        
        # 3. 合并并输出
        final_content = "\n\n".join(merged_content)
        final_content = self._post_process_content(final_content)
        
        # 输出到LaTeX文件
        chapter_tex_file = chapter_output_dir / f"{chapter_key}.tex"
        self._write_latex_file(chapter_tex_file, final_content)
        
        # 同时输出到主章节目录（兼容现有系统）
        main_chapter_tex = self.output_dir / f"{chapter_key}.tex"
        self._write_latex_file(main_chapter_tex, final_content)
        
        self.logger.info(f"✅ 第{chapter_number}章转换完成")
    
    def _read_and_process_markdown(self, file_path: Path, file_type: str) -> str:
        """读取并处理Markdown文件"""
        # 尝试多种编码
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            self.logger.warning(f"无法读取文件: {file_path}")
            return ""
        
        # 预处理内容
        content = self._preprocess_content(content, file_path, file_type)
        return content
    
    def _preprocess_content(self, content: str, file_path: Path, file_type: str) -> str:
        """预处理Markdown内容并转换为LaTeX"""
        # 移除YAML前言
        content = self._remove_yaml_frontmatter(content)
        
        # 智能处理标题 (改进：保持现有中文标题)
        content = self._process_headings_intelligently(content, file_path, file_type)
        
        # 处理图片路径
        content = self._process_image_references(content, file_path)
        
        # 处理代码块
        content = self._process_code_blocks(content)
        
        # 处理特殊语法
        content = self._process_admonitions(content)
        
        # 转换为LaTeX格式
        content = self._convert_markdown_to_latex(content)
        
        return content
    
    def _remove_yaml_frontmatter(self, content: str) -> str:
        """移除YAML前言"""
        content = content.replace('\r\n', '\n')
        if content.startswith('---'):
            pattern = r'^---\s*\n.*?\n---\s*\n'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        return content
    
    def _process_headings_intelligently(self, content: str, file_path: Path, file_type: str) -> str:
        """智能处理标题 - 保持现有中文格式"""
        lines = content.split('\n')
        if not lines:
            return content
        
        # 检查第一行是否为标题
        first_line = lines[0].strip()
        if not first_line.startswith('#'):
            return content
        
        if file_type == 'chapter':
            # 章节主文件 - 检测是否已有中文标题
            chinese_chapter_pattern = r'^#\s*(第[一二三四五六七八九十\d]+章|第\d+章)\s+'
            if re.match(chinese_chapter_pattern, first_line):
                # 已经有中文格式的标题，保持原样
                self.logger.debug(f"保持原有中文章节标题: {first_line}")
                return content
            
            # 如果没有中文格式，尝试添加
            chapter_match = re.search(r'chapter(\d+)', file_path.name)
            if chapter_match:
                chapter_num = int(chapter_match.group(1))
                if not re.search(r'(第.*章|chapter|Chapter|\d+章)', first_line, re.IGNORECASE):
                    title_content = re.sub(r'^#\s*', '', first_line)
                    lines[0] = f"# 第{chapter_num}章 {title_content}"
                    self.logger.debug(f"添加中文章节标题: {lines[0]}")
        
        elif file_type == 'section':
            # 节文件 - 检测是否已有编号
            section_pattern = r'^##\s*\d+\.\d+\s+'
            if re.match(section_pattern, first_line):
                # 已经有正确的节标题格式，保持原样
                self.logger.debug(f"保持原有节标题: {first_line}")
                return content
            
            # 尝试添加节编号
            section_match = re.search(r'section(\d+)-(\d+)', file_path.name)
            if section_match:
                chapter_num = int(section_match.group(1))
                section_num = int(section_match.group(2))
                if not re.search(r'^\s*##+\s*\d+\.\d+', first_line):
                    title_content = re.sub(r'^#+\s*', '', first_line)
                    lines[0] = f"## {chapter_num}.{section_num} {title_content}"
                    self.logger.debug(f"添加节标题编号: {lines[0]}")
        
        return '\n'.join(lines)
    
    def _remove_chapter_sections_summary(self, content: str) -> str:
        """移除章节中的"本章小节"部分"""
        # 查找并移除"本章小节"部分
        patterns = [
            r'##\s*本章小节.*?(?=##|\Z)',  # 匹配"## 本章小节"到下一个##或文档结尾
            r'##\s*章节结构.*?(?=##|\Z)',   # 匹配"## 章节结构"
            r'##\s*内容概要.*?(?=##|\Z)',   # 匹配"## 内容概要"
            r'##\s*章节安排.*?(?=##|\Z)',   # 匹配"## 章节安排"
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _process_image_references(self, content: str, source_file: Path) -> str:
        """处理图片引用"""
        def replace_image_ref(match):
            alt_text = match.group(1)
            original_path = match.group(2)
            
            # 查找图片的实际位置
            image_file = self._find_image_file(original_path, source_file)
            if image_file:
                # 返回相对于LaTeX输出目录的路径
                relative_path = f"images/{image_file.name}"
                return f"![{alt_text}]({relative_path})"
            else:
                self.logger.warning(f"图片未找到: {original_path} in {source_file}")
                return match.group(0)  # 保持原样
        
        # 处理图片引用
        content = re.sub(r'!\\[(.*?)\\]\\((.*?)\\)', replace_image_ref, content)
        return content
    
    def _find_image_file(self, image_path: str, source_file: Path) -> Optional[Path]:
        """查找图片文件的实际位置"""
        image_name = Path(image_path).name
        
        # 可能的搜索路径
        search_paths = [
            source_file.parent / image_path,
            source_file.parent / "images" / image_name,
            source_file.parent.parent / "images" / image_name,
            self.docs_dir / "assets" / "images" / image_name,
            self.docs_dir / "chapters" / "images" / image_name,
        ]
        
        # 检查直接路径
        for search_path in search_paths:
            if search_path.exists():
                return search_path
        
        # 递归搜索
        for search_root in [self.docs_dir, source_file.parent.parent]:
            if search_root.exists():
                for img_file in search_root.rglob(image_name):
                    if img_file.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp'}:
                        return img_file
        
        return None
    
    def _process_code_blocks(self, content: str) -> str:
        """处理代码块"""
        def enhance_code_block(match):
            language = match.group(1).strip() if match.group(1) else ''
            code_content = match.group(2)
            
            # 智能检测语言
            if not language:
                language = self._detect_code_language(code_content)
            
            return f"```{language}\n{code_content}\n```"
        
        # 处理代码块
        pattern = r'```(\w*)\n(.*?)\n```'
        content = re.sub(pattern, enhance_code_block, content, flags=re.DOTALL)
        
        return content
    
    def _detect_code_language(self, code: str) -> str:
        """智能检测代码语言"""
        code_lower = code.lower()
        
        # 语言检测规则
        language_patterns = {
            'python': ['def ', 'import ', 'from ', 'print(', 'if __name__'],
            'javascript': ['function', 'const ', 'let ', 'var ', '=>', 'console.log'],
            'java': ['public class', 'private ', 'package ', 'import java'],
            'sql': ['select ', 'from ', 'where ', 'insert ', 'update ', 'create table'],
            'html': ['<html', '<div', '<span', '<!doctype'],
            'css': ['{', '}', 'color:', 'font-', '.class'],
            'bash': ['#!/bin/bash', 'echo ', 'cd ', 'ls ', 'mkdir '],
            'json': ['{', '}', '":']
        }
        
        for language, patterns in language_patterns.items():
            if any(pattern in code_lower for pattern in patterns):
                return language
        
        return 'text'
    
    def _process_admonitions(self, content: str) -> str:
        """处理提醒框语法"""
        def convert_admonition(match):
            adm_type = match.group(1).lower()
            title = match.group(2) or adm_type.capitalize()
            adm_content = match.group(3).strip()
            
            # 转换为简单的引用块格式
            return f'> **{title}**\n> \n> {adm_content.replace(chr(10), chr(10) + "> ")}\n'
        
        # 处理!!! 语法
        pattern = r'!!!\s+(\w+)(?:\s+"([^"]*)")?\n((?:(?!^\s*$).*\n?)*)'
        content = re.sub(pattern, convert_admonition, content, flags=re.MULTILINE)
        
        return content
    
    def _convert_markdown_to_latex(self, content: str) -> str:
        """将Markdown内容转换为LaTeX格式 - 使用Pandoc"""
        try:
            # 将内容写入临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
                temp_md.write(content)
                temp_md_path = temp_md.name
            
            # 使用Pandoc转换为LaTeX
            result = subprocess.run([
                'pandoc',
                temp_md_path,
                '-t', 'latex',
                '--no-highlight'  # 禁用语法高亮以避免复杂的LaTeX包依赖
            ], capture_output=True, text=True, encoding='utf-8')
            
            # 清理临时文件
            Path(temp_md_path).unlink()
            
            if result.returncode == 0:
                latex_content = result.stdout
                
                # 清理生成的LaTeX内容
                latex_content = self._cleanup_pandoc_latex(latex_content)
                return latex_content
            else:
                self.logger.warning(f"Pandoc转换失败: {result.stderr}")
                # 如果Pandoc失败，返回简单的文本处理版本
                return self._simple_markdown_to_latex(content)
                
        except FileNotFoundError:
            self.logger.warning("Pandoc未安装，使用简单转换")
            return self._simple_markdown_to_latex(content)
        except Exception as e:
            self.logger.warning(f"Pandoc转换出错: {e}，使用简单转换")
            return self._simple_markdown_to_latex(content)
    
    def _cleanup_pandoc_latex(self, latex_content: str) -> str:
        """清理Pandoc生成的LaTeX内容"""
        # 移除不需要的包和环境
        lines = latex_content.split('\n')
        clean_lines = []
        
        for line in lines:
            # 跳过文档类声明和包导入
            if line.strip().startswith(('\\documentclass', '\\usepackage', '\\begin{document}', '\\end{document}')):
                continue
            clean_lines.append(line)
        
        result = '\n'.join(clean_lines).strip()
        
        # 处理特殊LaTeX命令
        result = self._fix_latex_commands(result)
        
        # 移除emoji
        result = self._remove_emojis(result)
        
        return result
    
    def _fix_latex_commands(self, content: str) -> str:
        """修复LaTeX命令"""
        # 移除或替换 \tightlist 命令
        content = content.replace('\\tightlist', '')
        
        return content
    
    def _remove_emojis(self, content: str) -> str:
        """移除emoji字符，但保留中文和其他正常字符"""
        # 更精确的emoji模式，只移除表情符号
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U0001F018-\U0001F270\U0001F030-\U0001F093]'
        # 逐个替换emoji，保留空格以维护文本结构
        content = re.sub(emoji_pattern, ' ', content)
        
        # 清理多余的空格
        content = re.sub(r'\s+', ' ', content)
        
        return content
    
    def _simple_markdown_to_latex(self, content: str) -> str:
        """简单的Markdown到LaTeX转换作为fallback"""
        lines = content.split('\n')
        latex_lines = []
        
        for line in lines:
            # 处理标题
            if line.strip().startswith('#'):
                level = 0
                while level < len(line) and line[level] == '#':
                    level += 1
                
                title = line[level:].strip()
                if level == 1:
                    latex_lines.append(f'\\chapter{{{title}}}')
                elif level == 2:
                    latex_lines.append(f'\\section{{{title}}}')
                elif level == 3:
                    latex_lines.append(f'\\subsection{{{title}}}')
                elif level == 4:
                    latex_lines.append(f'\\subsubsection{{{title}}}')
                else:
                    latex_lines.append(f'\\paragraph{{{title}}}')
            else:
                # 简单文本处理
                line = self._process_simple_formatting(line)
                latex_lines.append(line)
        
        return '\n'.join(latex_lines)
    
    def _process_simple_formatting(self, line: str) -> str:
        """处理简单的文本格式化"""
        # 移除emoji和特殊符号
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
        line = re.sub(emoji_pattern, '', line)
        
        # 处理粗体
        line = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', line)
        
        # 处理内联代码
        line = re.sub(r'`([^`]+)`', r'\\texttt{\1}', line)
        
        return line
    
    def _convert_appendices(self):
        """转换附录"""
        appendix_dir = self.project_root / "appendix"
        if not appendix_dir.exists():
            return
        
        appendix_files = ['appendixA.md', 'appendixB.md', 'appendixC.md']
        
        for appendix_file in appendix_files:
            appendix_md = appendix_dir / appendix_file
            if appendix_md.exists():
                appendix_name = appendix_file.replace('.md', '')
                appendix_tex = self.output_dir / f"{appendix_name}.tex"
                
                self.logger.info(f"转换附录: {appendix_file}")
                content = self._read_and_process_markdown(appendix_md, 'appendix')
                self._write_latex_file(appendix_tex, content)
    
    def _process_images(self):
        """处理图片文件"""
        self.logger.info("处理图片文件...")
        
        # 创建图片输出目录
        images_output_dir = self.latex_dir / "images"
        images_output_dir.mkdir(exist_ok=True)
        
        # 搜索并复制图片
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp'}
        copied_count = 0
        
        # 从docs目录搜索图片
        for img_file in self.docs_dir.rglob("*"):
            if img_file.suffix.lower() in image_extensions:
                dest_file = images_output_dir / img_file.name
                try:
                    shutil.copy2(img_file, dest_file)
                    copied_count += 1
                except Exception as e:
                    self.logger.warning(f"复制图片失败 {img_file}: {e}")
        
        self.logger.info(f"复制了 {copied_count} 张图片")
    
    def _post_process_content(self, content: str) -> str:
        """后处理内容"""
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 确保段落间有适当的空行
        content = re.sub(r'\n+(?=#)', '\n\n', content)
        
        return content.strip() + '\n'
    
    def _write_latex_file(self, output_path: Path, content: str):
        """写入LaTeX文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.debug(f"写入LaTeX文件: {output_path}")
        except Exception as e:
            self.logger.error(f"写入文件失败 {output_path}: {e}")
    
    def build_latex(self) -> bool:
        """构建LaTeX文档"""
        self.logger.info("🔨 开始构建LaTeX文档...")
        
        # 切换到LaTeX目录
        original_cwd = os.getcwd()
        os.chdir(self.latex_dir)
        
        try:
            # 运行LaTeX构建
            commands = [
                "xelatex main.tex",
                "xelatex main.tex",  # 运行两次确保交叉引用正确
            ]
            
            for cmd in commands:
                self.logger.info(f"执行命令: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode != 0:
                    self.logger.error(f"LaTeX构建失败: {result.stderr}")
                    return False
                else:
                    self.logger.info("LaTeX命令执行成功")
            
            # 检查PDF是否生成（注意：在切换到latex_dir后，PDF在当前目录）
            pdf_file = Path("main.pdf")  # 直接查找当前目录的main.pdf
            self.logger.info(f"检查PDF路径: {pdf_file}")
            self.logger.info(f"绝对路径: {pdf_file.resolve()}")
            self.logger.info(f"文件是否存在: {pdf_file.exists()}")
            if pdf_file.exists():
                file_size = pdf_file.stat().st_size
                self.logger.info(f"✅ PDF构建成功: {pdf_file} ({file_size:,} bytes)")
                return True
            else:
                self.logger.error("PDF文件未生成")
                return False
                
        except Exception as e:
            self.logger.error(f"LaTeX构建过程出错: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def run_full_conversion(self) -> bool:
        """运行完整转换流程"""
        self.logger.info("=" * 60)
        self.logger.info("智慧水利教材转换器 - 改进版")
        self.logger.info("=" * 60)
        
        # 1. 转换所有章节
        if not self.convert_all_chapters():
            self.logger.error("章节转换失败")
            return False
        
        # 2. 构建LaTeX文档
        if not self.build_latex():
            self.logger.error("LaTeX构建失败")
            return False
        
        self.logger.info("🎉 完整转换流程完成！")
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智慧水利教材转换器 - 改进版')
    parser.add_argument('--project-root', help='项目根目录路径')
    parser.add_argument('--convert-only', action='store_true', help='仅转换，不构建PDF')
    parser.add_argument('--build-only', action='store_true', help='仅构建PDF，不转换')
    
    args = parser.parse_args()
    
    # 创建转换器
    converter = ImprovedTextbookConverter(args.project_root)
    
    # 执行转换
    try:
        if args.convert_only:
            success = converter.convert_all_chapters()
        elif args.build_only:
            success = converter.build_latex()
        else:
            success = converter.run_full_conversion()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        converter.logger.info("用户中断转换")
        sys.exit(1)
    except Exception as e:
        converter.logger.error(f"转换失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()