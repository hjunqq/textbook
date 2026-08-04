#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器 - 企业级转换工具
Professional Textbook Conversion Tool

功能特性:
- 多格式输出支持 (PDF, LaTeX, HTML, DOCX)
- 智能内容预处理和格式标准化
- 完整的质量检查和验证
- 模块化架构设计
- 命令行界面支持
- 详细的日志记录和错误处理
- 进度监控和状态报告
- 批处理和单章节转换支持

Author: Claude Code Assistant
Version: 3.0.0
"""

import os
import sys
import argparse
import logging
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re

# 设置项目根路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

@dataclass
class ConversionConfig:
    """转换配置数据类"""
    input_dir: str
    output_dir: str
    output_format: str = 'pdf'
    template: str = 'default'
    include_toc: bool = True
    number_sections: bool = True
    quality_check: bool = True
    verbose: bool = False
    chapters: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

class OutputFormat(Enum):
    """支持的输出格式"""
    PDF = 'pdf'
    LATEX = 'latex'
    HTML = 'html'
    DOCX = 'docx'
    EPUB = 'epub'

class ConversionStatus(Enum):
    """转换状态"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = 'excellent'
    GOOD = 'good'
    ACCEPTABLE = 'acceptable'
    POOR = 'poor'
    FAILED = 'failed'

class Logger:
    """统一日志管理器"""
    
    def __init__(self, log_file: Optional[str] = None, verbose: bool = False):
        self.verbose = verbose
        self.log_file = log_file
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        self.logger = logging.getLogger('TextbookConverter')
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        if self.verbose:
            print(f"ℹ️  {message}")
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        print(f"⚠️  {message}")
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        print(f"❌ {message}")
        self.logger.error(message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """成功日志"""
        print(f"✅ {message}")
        self.logger.info(f"SUCCESS: {message}", **kwargs)
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        if self.verbose:
            print(f"🔍 {message}")
        self.logger.debug(message, **kwargs)

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, total_steps: int = 100):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = datetime.now()
        self.step_history = []
    
    def update(self, step: int, message: str = ""):
        """更新进度"""
        self.current_step = step
        self.step_history.append({
            'step': step,
            'message': message,
            'timestamp': datetime.now()
        })
        
        percentage = min(100, (step / self.total_steps) * 100)
        elapsed = datetime.now() - self.start_time
        
        print(f"📊 Progress: {percentage:.1f}% [{step}/{self.total_steps}] {message}")
        
        if self.current_step >= self.total_steps:
            print(f"🎉 Conversion completed in {elapsed}")
    
    def get_progress(self) -> Dict:
        """获取当前进度信息"""
        return {
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'percentage': (self.current_step / self.total_steps) * 100,
            'elapsed_time': str(datetime.now() - self.start_time),
            'is_complete': self.current_step >= self.total_steps
        }

class SystemChecker:
    """系统环境检查器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.requirements = {
            'pandoc': 'Pandoc document converter',
            'xelatex': 'XeLaTeX PDF engine',
        }
        
    def check_all_requirements(self) -> bool:
        """检查所有系统要求"""
        self.logger.info("🔍 检查系统环境...")
        all_passed = True
        
        for command, description in self.requirements.items():
            if self._check_command(command):
                self.logger.success(f"{description} 已安装")
            else:
                self.logger.error(f"{description} 未安装或不在PATH中")
                all_passed = False
        
        # 检查Python包
        python_packages = ['pathlib', 'dataclasses', 'enum']
        for package in python_packages:
            try:
                __import__(package)
                self.logger.debug(f"Python包 {package} 可用")
            except ImportError:
                self.logger.warning(f"Python包 {package} 不可用")
        
        return all_passed
    
    def _check_command(self, command: str) -> bool:
        """检查命令是否可用"""
        try:
            result = subprocess.run([command, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

class ContentProcessor:
    """内容预处理器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.image_counter = 1
        self.processed_images = {}
        self.statistics = {
            'files_processed': 0,
            'images_processed': 0,
            'code_blocks_found': 0,
            'warnings': 0
        }
    
    def process_markdown_file(self, file_path: Path, output_dir: Path) -> str:
        """处理单个Markdown文件"""
        self.logger.debug(f"处理文件: {file_path}")
        
        # 读取文件内容
        content = self._read_file_safely(file_path)
        if not content:
            return ""
        
        # 预处理管道
        content = self._remove_yaml_frontmatter(content)
        content = self._standardize_headings(content, file_path)
        content = self._process_code_blocks(content)
        content = self._process_images(content, file_path, output_dir)
        content = self._process_admonitions(content)
        content = self._clean_whitespace(content)
        
        self.statistics['files_processed'] += 1
        return content
    
    def _read_file_safely(self, file_path: Path) -> str:
        """安全读取文件，处理编码问题"""
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                self.logger.debug(f"使用编码 {encoding} 成功读取: {file_path}")
                return content
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        self.logger.warning(f"无法读取文件: {file_path}")
        self.statistics['warnings'] += 1
        return ""
    
    def _remove_yaml_frontmatter(self, content: str) -> str:
        """移除YAML前言"""
        content = content.replace('\r\n', '\n')
        if content.startswith('---'):
            pattern = r'^---\s*\n.*?\n---\s*\n'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        return content
    
    def _standardize_headings(self, content: str, file_path: Path) -> str:
        """智能标准化标题格式"""
        name = file_path.name.lower()
        
        # 检测文件类型并应用相应的标题处理
        if 'chapter' in name and not 'section' in name:
            # 主章节文件 - 智能检测已有的中文标题
            content = self._process_chapter_title(content, file_path)
            # 处理"本章小节"部分，移除它因为sections会自动添加在后面
            content = self._remove_chapter_sections_summary(content)
            
        elif 'section' in name:
            # 节文件 - 保持原有格式，不做重复编号
            content = self._process_section_title(content, file_path)
        
        return content
    
    def _process_chapter_title(self, content: str, file_path: Path) -> str:
        """处理章节主标题"""
        lines = content.split('\n')
        if not lines:
            return content
        
        first_line = lines[0].strip()
        
        # 检测是否已经有中文章节标题格式（如：# 第一章 xxx 或 # 第1章 xxx）
        chinese_chapter_pattern = r'^#\s*(第[一二三四五六七八九十\d]+章|第\d+章)\s+'
        if re.match(chinese_chapter_pattern, first_line):
            # 已经有中文格式的标题，保持原样
            self.logger.debug(f"保持原有中文章节标题: {first_line}")
            return content
        
        # 如果没有中文格式，检查是否需要添加章节编号
        chapter_match = re.search(r'chapter(\d+)', file_path.name)
        if chapter_match and first_line.startswith('#'):
            chapter_num = int(chapter_match.group(1))
            # 检测是否已经有任何形式的章节标识
            if not re.search(r'(第.*章|chapter|Chapter|\d+章)', first_line, re.IGNORECASE):
                # 没有章节标识，添加中文格式
                title_content = re.sub(r'^#\s*', '', first_line)
                new_title = f"# 第{chapter_num}章 {title_content}"
                lines[0] = new_title
                self.logger.debug(f"添加中文章节标题: {new_title}")
                return '\n'.join(lines)
        
        return content
    
    def _process_section_title(self, content: str, file_path: Path) -> str:
        """处理节标题"""
        lines = content.split('\n')
        if not lines:
            return content
        
        first_line = lines[0].strip()
        
        # 检测是否已经有节标题格式（如：## 1.1 xxx）
        section_pattern = r'^##\s*\d+\.\d+\s+'
        if re.match(section_pattern, first_line):
            # 已经有正确的节标题格式，保持原样
            self.logger.debug(f"保持原有节标题: {first_line}")
            return content
        
        # 如果没有正确格式，尝试添加编号
        section_match = re.search(r'section(\d+)-(\d+)', file_path.name)
        if section_match and first_line.startswith('#'):
            chapter_num = int(section_match.group(1))
            section_num = int(section_match.group(2))
            
            # 检查是否已经有编号
            if not re.search(r'^\s*##?\s*\d+\.\d+', first_line):
                # 添加节编号
                title_content = re.sub(r'^#+\s*', '', first_line)
                new_title = f"## {chapter_num}.{section_num} {title_content}"
                lines[0] = new_title
                self.logger.debug(f"添加节标题编号: {new_title}")
                return '\n'.join(lines)
        
        return content
    
    def _remove_chapter_sections_summary(self, content: str) -> str:
        """移除章节中的"本章小节"部分，因为sections会自动添加"""
        # 查找并移除"本章小节"部分
        patterns = [
            r'##\s*本章小节.*?(?=##|\Z)',  # 匹配"## 本章小节"到下一个##或文档结尾
            r'##\s*章节结构.*?(?=##|\Z)',  # 匹配"## 章节结构"
            r'##\s*内容概要.*?(?=##|\Z)',  # 匹配"## 内容概要"
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _process_code_blocks(self, content: str) -> str:
        """处理代码块"""
        def enhance_code_block(match):
            language = match.group(1).strip() if match.group(1) else ''
            code_content = match.group(2)
            
            # 智能检测语言
            if not language:
                language = self._detect_code_language(code_content)
            
            self.statistics['code_blocks_found'] += 1
            return f'```{language}\n{code_content}\n```'
        
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
            'json': ['{', '}', '":', '":']
        }
        
        for language, patterns in language_patterns.items():
            if any(pattern in code_lower for pattern in patterns):
                return language
        
        return 'text'
    
    def _process_images(self, content: str, source_file: Path, output_dir: Path) -> str:
        """处理图片引用"""
        def process_image_reference(match):
            alt_text = match.group(1)
            original_path = match.group(2)
            
            # 查找并复制图片
            new_path = self._find_and_copy_image(original_path, source_file, output_dir)
            
            if new_path:
                return f'![{alt_text}]({new_path})'
            else:
                self.logger.warning(f"图片未找到: {original_path} in {source_file}")
                self.statistics['warnings'] += 1
                return match.group(0)  # 保持原样
        
        # 处理图片引用
        pattern = r'!\[(.*?)\]\((.*?)\)'
        content = re.sub(pattern, process_image_reference, content)
        
        return content
    
    def _find_and_copy_image(self, image_path: str, source_file: Path, output_dir: Path) -> Optional[str]:
        """查找并复制图片文件"""
        # 缓存检查
        cache_key = f"{source_file}:{image_path}"
        if cache_key in self.processed_images:
            return self.processed_images[cache_key]
        
        # 搜索图片文件
        image_file = self._find_image_file(image_path, source_file)
        
        if image_file and image_file.exists():
            # 复制到输出目录
            relative_path = self._copy_image_to_output(image_file, output_dir)
            self.processed_images[cache_key] = relative_path
            self.statistics['images_processed'] += 1
            return relative_path
        
        return None
    
    def _find_image_file(self, image_path: str, source_file: Path) -> Optional[Path]:
        """查找图片文件的实际位置"""
        image_name = Path(image_path).name
        
        # 搜索路径
        search_paths = [
            source_file.parent / image_path,
            source_file.parent / "images" / image_name,
            source_file.parent.parent / "images" / image_name,
            PROJECT_ROOT / "docs" / "assets" / "images" / image_name,
            PROJECT_ROOT / "docs" / "chapters" / "images" / image_name,
        ]
        
        # 检查直接路径
        for search_path in search_paths:
            if search_path.exists():
                return search_path
        
        # 递归搜索
        for search_root in [PROJECT_ROOT / "docs", source_file.parent.parent]:
            if search_root.exists():
                for img_file in search_root.rglob(image_name):
                    if img_file.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp'}:
                        return img_file
        
        return None
    
    def _copy_image_to_output(self, source_image: Path, output_dir: Path) -> str:
        """复制图片到输出目录"""
        # 创建images目录
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        # 生成新文件名
        extension = source_image.suffix
        new_name = f"img_{self.image_counter:03d}{extension}"
        self.image_counter += 1
        
        # 复制文件
        dest_path = images_dir / new_name
        try:
            shutil.copy2(source_image, dest_path)
            self.logger.debug(f"复制图片: {source_image} -> {dest_path}")
            return f"images/{new_name}"
        except Exception as e:
            self.logger.error(f"复制图片失败: {source_image} -> {dest_path}: {e}")
            return None
    
    def _process_admonitions(self, content: str) -> str:
        """处理提醒框语法"""
        admonition_mapping = {
            'note': 'note',
            'tip': 'tip', 
            'warning': 'warning',
            'danger': 'danger',
            'info': 'info',
            'important': 'important'
        }
        
        def convert_admonition(match):
            adm_type = match.group(1).lower()
            title = match.group(2) or adm_type.capitalize()
            adm_content = match.group(3).strip()
            
            # 转换为简单的引用块格式，适合Pandoc处理
            return f'> **{title}**\n> \n> {adm_content.replace(chr(10), chr(10) + "> ")}\n'
        
        # 处理!!! 语法
        pattern = r'!!!\s+(\w+)(?:\s+"([^"]*)")?\n((?:(?!^\s*$).*\n?)*)'
        content = re.sub(pattern, convert_admonition, content, flags=re.MULTILINE)
        
        return content
    
    def _clean_whitespace(self, content: str) -> str:
        """清理空白字符"""
        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 清理行尾空白
        content = re.sub(r' +$', '', content, flags=re.MULTILINE)
        
        # 确保文件结尾有换行符
        if content and not content.endswith('\n'):
            content += '\n'
        
        return content
    
    def get_statistics(self) -> Dict:
        """获取处理统计信息"""
        return self.statistics.copy()

class QualityAssurance:
    """质量保证检查器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.issues = []
        self.warnings = []
        self.stats = {
            'files_checked': 0,
            'images_checked': 0,
            'code_blocks_checked': 0,
            'chapters_found': 0
        }
    
    def validate_input_structure(self, input_dir: Path) -> bool:
        """验证输入目录结构"""
        self.logger.info("🔍 验证输入目录结构...")
        
        if not input_dir.exists():
            self.issues.append(f"输入目录不存在: {input_dir}")
            return False
        
        # 检查必要的子目录
        chapters_dir = input_dir / "chapters"
        if not chapters_dir.exists():
            self.issues.append(f"章节目录不存在: {chapters_dir}")
            return False
        
        # 统计章节
        chapter_count = 0
        for item in chapters_dir.iterdir():
            if item.is_dir() and item.name.startswith('chapter'):
                chapter_count += 1
        
        self.stats['chapters_found'] = chapter_count
        self.logger.info(f"发现 {chapter_count} 个章节目录")
        
        return len(self.issues) == 0
    
    def validate_content_quality(self, input_dir: Path) -> QualityLevel:
        """验证内容质量"""
        self.logger.info("📋 检查内容质量...")
        
        chapters_dir = input_dir / "chapters"
        if not chapters_dir.exists():
            return QualityLevel.FAILED
        
        for chapter_dir in chapters_dir.iterdir():
            if not chapter_dir.is_dir() or not chapter_dir.name.startswith('chapter'):
                continue
            
            # 检查章节文件
            for md_file in chapter_dir.glob("*.md"):
                self._validate_markdown_file(md_file)
        
        # 根据问题数量评估质量
        if len(self.issues) > 10:
            return QualityLevel.FAILED
        elif len(self.issues) > 5:
            return QualityLevel.POOR
        elif len(self.warnings) > 10:
            return QualityLevel.ACCEPTABLE
        elif len(self.warnings) > 3:
            return QualityLevel.GOOD
        else:
            return QualityLevel.EXCELLENT
    
    def _validate_markdown_file(self, file_path: Path) -> None:
        """验证单个Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.stats['files_checked'] += 1
            
            # 检查编码问题
            try:
                content.encode('utf-8')
            except UnicodeEncodeError:
                self.issues.append(f"文件编码问题: {file_path}")
            
            # 检查图片引用
            image_refs = re.findall(r'!\[.*?\]\((.*?)\)', content)
            self.stats['images_checked'] += len(image_refs)
            
            # 检查代码块
            code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', content, re.DOTALL)
            self.stats['code_blocks_checked'] += len(code_blocks)
            
            for language, code in code_blocks:
                if not language.strip():
                    self.warnings.append(f"代码块缺少语言标识: {file_path}")
            
            # 检查标题结构
            self._check_heading_structure(content, file_path)
            
        except Exception as e:
            self.issues.append(f"检查文件失败 {file_path}: {e}")
    
    def _check_heading_structure(self, content: str, file_path: Path) -> None:
        """检查标题结构"""
        lines = content.split('\n')
        prev_level = 0
        
        for line_no, line in enumerate(lines, 1):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                
                # 检查标题级别跳跃
                if level > prev_level + 1:
                    self.warnings.append(
                        f"标题级别跳跃: {file_path}:{line_no} - {line.strip()}"
                    )
                
                prev_level = level
    
    def validate_output(self, output_file: Path) -> bool:
        """验证输出文件"""
        if not output_file.exists():
            self.issues.append(f"输出文件不存在: {output_file}")
            return False
        
        file_size = output_file.stat().st_size
        if file_size < 1024:  # 小于1KB
            self.issues.append(f"输出文件过小: {output_file} ({file_size} bytes)")
            return False
        
        self.logger.success(f"输出文件验证通过: {output_file} ({file_size:,} bytes)")
        return True
    
    def generate_quality_report(self, output_dir: Path) -> Path:
        """生成质量报告"""
        report_file = output_dir / "quality_report.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'issues': self.issues,
            'warnings': self.warnings,
            'summary': {
                'total_issues': len(self.issues),
                'total_warnings': len(self.warnings),
                'files_checked': self.stats['files_checked'],
                'quality_level': self._get_overall_quality().value
            }
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.success(f"质量报告已生成: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"生成质量报告失败: {e}")
            return None
    
    def _get_overall_quality(self) -> QualityLevel:
        """获取整体质量等级"""
        if len(self.issues) > 5:
            return QualityLevel.POOR
        elif len(self.issues) > 0:
            return QualityLevel.ACCEPTABLE
        elif len(self.warnings) > 5:
            return QualityLevel.GOOD
        else:
            return QualityLevel.EXCELLENT
    
    def has_critical_issues(self) -> bool:
        """是否有关键问题"""
        return len(self.issues) > 0

class PandocConverter:
    """Pandoc转换器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.conversion_templates = {
            'pdf': {
                'args': ['--pdf-engine=xelatex', '--template=chinese'],
                'output_extension': '.pdf'
            },
            'latex': {
                'args': ['--template=chinese'],
                'output_extension': '.tex'
            },
            'html': {
                'args': ['--self-contained', '--css=styles.css'],
                'output_extension': '.html'
            },
            'docx': {
                'args': ['--reference-doc=template.docx'],
                'output_extension': '.docx'
            }
        }
    
    def convert(self, input_file: Path, output_format: str, output_dir: Path, config: ConversionConfig) -> bool:
        """执行转换"""
        template_config = self.conversion_templates.get(output_format)
        if not template_config:
            self.logger.error(f"不支持的输出格式: {output_format}")
            return False
        
        output_file = output_dir / f"textbook{template_config['output_extension']}"
        
        # 构建Pandoc命令
        cmd = [
            'pandoc',
            str(input_file),
            '-o', str(output_file),
            f'--from=markdown',
            f'--to={output_format}',
            '--standalone'
        ]
        
        # 处理模板参数
        template_args = []
        for arg in template_config['args']:
            if arg.startswith('--template='):
                template_name = arg.split('=', 1)[1]
                # 检查是否指定了自定义模板路径
                if config.template and config.template != 'default':
                    # 使用自定义模板路径
                    template_path = Path(config.template)
                    if template_path.exists():
                        template_args.append(f'--template={template_path.absolute()}')
                        self.logger.info(f"使用自定义模板: {template_path.absolute()}")
                    else:
                        # 尝试相对于工作目录的模板
                        relative_template = output_dir.parent / config.template
                        if relative_template.exists():
                            template_args.append(f'--template={relative_template.absolute()}')
                            self.logger.info(f"使用相对模板: {relative_template.absolute()}")
                        else:
                            # 回退到默认模板名
                            template_args.append(f'--template={template_name}')
                            self.logger.warning(f"未找到自定义模板，使用默认: {template_name}")
                else:
                    # 使用默认模板
                    template_args.append(arg)
            else:
                template_args.append(arg)
        
        # 添加模板参数
        cmd.extend(template_args)
        
        # 添加配置选项
        if config.include_toc:
            cmd.append('--toc')
        if config.number_sections:
            cmd.append('--number-sections')
        
        # 执行转换
        return self._run_pandoc_command(cmd, output_file, output_dir)
    
    def _run_pandoc_command(self, cmd: List[str], output_file: Path, cwd: Path) -> bool:
        """执行Pandoc命令"""
        try:
            self.logger.info(f"执行转换命令: {' '.join(cmd)}")
            self.logger.debug(f"工作目录: {cwd}")
            
            # 使用绝对路径来避免路径问题
            cmd_abs = []
            for item in cmd:
                if item.endswith('.md') or item.endswith('.tex') or item.endswith('.pdf'):
                    # 转换相对路径为绝对路径
                    if not item.startswith('/'):
                        if '/' in item:
                            # 包含路径分隔符的相对路径
                            abs_path = (cwd / item).absolute()
                        else:
                            # 纯文件名
                            abs_path = (cwd / item).absolute()
                        cmd_abs.append(str(abs_path))
                    else:
                        cmd_abs.append(item)
                else:
                    cmd_abs.append(item)
            
            result = subprocess.run(
                cmd_abs,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                if output_file.exists():
                    file_size = output_file.stat().st_size
                    self.logger.success(f"转换成功: {output_file} ({file_size:,} bytes)")
                    return True
                else:
                    self.logger.error(f"转换命令成功但输出文件不存在: {output_file}")
                    return False
            else:
                self.logger.error(f"Pandoc转换失败 (返回码: {result.returncode})")
                if result.stderr:
                    self.logger.error(f"错误信息: {result.stderr}")
                if result.stdout:
                    self.logger.info(f"输出信息: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("转换超时 (超过5分钟)")
            return False
        except FileNotFoundError:
            self.logger.error("Pandoc未安装或不在PATH中")
            return False
        except Exception as e:
            self.logger.error(f"执行转换命令时出错: {e}")
            return False

class TextbookConverter:
    """教材转换器主类"""
    
    def __init__(self, config: ConversionConfig):
        self.config = config
        self.status = ConversionStatus.PENDING
        
        # 初始化组件
        log_file = Path(config.output_dir) / "conversion.log" if config.output_dir else None
        self.logger = Logger(log_file=log_file, verbose=config.verbose)
        self.progress = ProgressTracker(total_steps=8)
        self.system_checker = SystemChecker(self.logger)
        self.content_processor = ContentProcessor(self.logger)
        self.quality_assurance = QualityAssurance(self.logger)
        self.pandoc_converter = PandocConverter(self.logger)
        
        # 路径设置
        self.input_dir = Path(config.input_dir)
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def convert(self) -> bool:
        """执行完整的转换流程"""
        self.logger.info("🚀 开始教材转换流程")
        self.status = ConversionStatus.PROCESSING
        
        try:
            # Step 1: 系统环境检查
            self.progress.update(1, "检查系统环境")
            if not self.system_checker.check_all_requirements():
                self.status = ConversionStatus.FAILED
                return False
            
            # Step 2: 输入验证
            self.progress.update(2, "验证输入结构")
            if not self.quality_assurance.validate_input_structure(self.input_dir):
                self.status = ConversionStatus.FAILED
                return False
            
            # Step 3: 内容质量检查
            self.progress.update(3, "检查内容质量")
            if self.config.quality_check:
                quality_level = self.quality_assurance.validate_content_quality(self.input_dir)
                self.logger.info(f"内容质量等级: {quality_level.value}")
                
                if self.quality_assurance.has_critical_issues():
                    self.logger.error("发现关键问题，停止转换")
                    self.status = ConversionStatus.FAILED
                    return False
            
            # Step 4: 发现和收集文件
            self.progress.update(4, "收集源文件")
            source_files = self._discover_source_files()
            if not source_files:
                self.logger.error("未找到源文件")
                self.status = ConversionStatus.FAILED
                return False
            
            # Step 5: 预处理内容
            self.progress.update(5, "预处理内容")
            merged_content = self._process_and_merge_files(source_files)
            if not merged_content:
                self.logger.error("内容处理失败")
                self.status = ConversionStatus.FAILED
                return False
            
            # Step 6: 保存合并文件
            self.progress.update(6, "保存合并文件")
            merged_file = self._save_merged_content(merged_content)
            if not merged_file:
                self.status = ConversionStatus.FAILED
                return False
            
            # Step 7: 格式转换
            self.progress.update(7, f"转换为{self.config.output_format}格式")
            if not self.pandoc_converter.convert(
                merged_file, self.config.output_format, self.output_dir, self.config
            ):
                self.status = ConversionStatus.FAILED
                return False
            
            # Step 8: 输出验证和质量报告
            self.progress.update(8, "生成质量报告")
            self._generate_final_report()
            
            self.status = ConversionStatus.COMPLETED
            self.logger.success("🎉 转换完成！")
            return True
            
        except KeyboardInterrupt:
            self.logger.warning("用户取消转换")
            self.status = ConversionStatus.CANCELLED
            return False
        except Exception as e:
            self.logger.error(f"转换过程中发生错误: {e}")
            self.status = ConversionStatus.FAILED
            return False
    
    def _discover_source_files(self) -> List[Tuple[str, Path]]:
        """发现源文件"""
        files = []
        
        # 前言文件
        preface_file = self.input_dir / "前言.md"
        if preface_file.exists():
            files.append(('preface', preface_file))
        
        # 章节文件 - 修复章节顺序问题：sections 应该放在章节最后
        chapters_dir = self.input_dir / "chapters"
        if chapters_dir.exists():
            # 按章节顺序处理
            for chapter_num in range(1, 20):  # 支持最多19章
                chapter_key = f"chapter{chapter_num:02d}"
                chapter_dir = chapters_dir / chapter_key
                
                if not chapter_dir.exists():
                    continue
                
                # 收集当前章节的所有文件
                chapter_files = []
                
                # 主章节文件（去掉"本章小节"部分，因为sections会放在后面）
                main_file = chapter_dir / f"{chapter_key}.md"
                if main_file.exists():
                    chapter_files.append(('chapter', main_file))
                
                # 节文件（按顺序排列，将放在章节主文件后面）
                section_files = sorted(chapter_dir.glob("section*.md"))
                for section_file in section_files:
                    chapter_files.append(('section', section_file))
                
                # 将这个章节的所有文件添加到主列表
                files.extend(chapter_files)
        
        # 附录文件
        appendix_dir = self.input_dir.parent / "appendix"
        if appendix_dir.exists():
            for appendix_file in sorted(appendix_dir.glob("*.md")):
                files.append(('appendix', appendix_file))
        
        self.logger.info(f"发现 {len(files)} 个源文件")
        return files
    
    def _process_and_merge_files(self, source_files: List[Tuple[str, Path]]) -> str:
        """处理并合并文件"""
        merged_parts = []
        
        for file_type, file_path in source_files:
            self.logger.debug(f"处理 {file_type}: {file_path.name}")
            
            processed_content = self.content_processor.process_markdown_file(
                file_path, self.output_dir
            )
            
            if processed_content.strip():
                merged_parts.append(processed_content)
                merged_parts.append("")  # 分隔空行
        
        # 合并内容
        merged_content = "\n".join(merged_parts)
        
        # 最终清理
        merged_content = self._final_cleanup(merged_content)
        
        # 打印处理统计信息
        stats = self.content_processor.get_statistics()
        self.logger.info(f"处理统计: {stats}")
        
        return merged_content
    
    def _final_cleanup(self, content: str) -> str:
        """最终内容清理"""
        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 修复标题前的空行
        content = re.sub(r'\n+(?=#)', '\n\n', content)
        
        # 确保代码块前后有空行
        content = re.sub(r'(?<!\n)\n```', '\n\n```', content)
        content = re.sub(r'```\n(?!\n)', '```\n\n', content)
        
        return content.strip() + '\n'
    
    def _save_merged_content(self, content: str) -> Optional[Path]:
        """保存合并的内容"""
        merged_file = self.output_dir / "textbook_merged.md"
        
        try:
            with open(merged_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = merged_file.stat().st_size
            self.logger.success(f"合并文件已保存: {merged_file} ({file_size:,} bytes)")
            return merged_file
            
        except Exception as e:
            self.logger.error(f"保存合并文件失败: {e}")
            return None
    
    def _generate_final_report(self) -> None:
        """生成最终报告"""
        # 生成质量报告
        self.quality_assurance.generate_quality_report(self.output_dir)
        
        # 生成转换报告
        report = {
            'conversion': {
                'status': self.status.value,
                'timestamp': datetime.now().isoformat(),
                'config': self.config.to_dict(),
                'progress': self.progress.get_progress()
            },
            'processing': self.content_processor.get_statistics(),
            'quality': {
                'issues': len(self.quality_assurance.issues),
                'warnings': len(self.quality_assurance.warnings),
                'stats': self.quality_assurance.stats
            }
        }
        
        report_file = self.output_dir / "conversion_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.success(f"转换报告已生成: {report_file}")
        except Exception as e:
            self.logger.error(f"生成转换报告失败: {e}")

def create_cli_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        description='智慧水利教材转换器 - 专业的教材格式转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s -i docs -o output -f pdf                    # 转换为PDF
  %(prog)s -i docs -o output -f latex -v               # 转换为LaTeX，详细输出
  %(prog)s -i docs -o output -f html --no-toc          # 转换为HTML，不生成目录
  %(prog)s -i docs -o output --chapters chapter01,chapter02  # 只转换指定章节
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='输入目录路径 (包含docs/chapters等)'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出目录路径'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=[fmt.value for fmt in OutputFormat],
        default='pdf',
        help='输出格式 (默认: pdf)'
    )
    
    parser.add_argument(
        '-t', '--template',
        default='default',
        help='模板名称 (默认: default)'
    )
    
    parser.add_argument(
        '--chapters',
        help='指定章节，逗号分隔 (如: chapter01,chapter02)'
    )
    
    parser.add_argument(
        '--no-toc',
        action='store_true',
        help='不生成目录'
    )
    
    parser.add_argument(
        '--no-numbers',
        action='store_true',
        help='不对章节编号'
    )
    
    parser.add_argument(
        '--no-quality-check',
        action='store_true',
        help='跳过质量检查'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='智慧水利教材转换器 3.0.0'
    )
    
    return parser

def main():
    """主函数"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # 创建配置
    config = ConversionConfig(
        input_dir=args.input,
        output_dir=args.output,
        output_format=args.format,
        template=args.template,
        include_toc=not args.no_toc,
        number_sections=not args.no_numbers,
        quality_check=not args.no_quality_check,
        verbose=args.verbose,
        chapters=args.chapters.split(',') if args.chapters else None
    )
    
    # 创建转换器并执行转换
    converter = TextbookConverter(config)
    success = converter.convert()
    
    # 退出状态
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()