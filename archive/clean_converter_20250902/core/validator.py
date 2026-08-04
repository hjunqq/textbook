#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器 - 质量检查和验证模块
转换前后的质量保证
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from .config import config

class QualityValidator:
    """质量检查和验证器"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.stats = {
            'files_processed': 0,
            'images_found': 0,
            'code_blocks_found': 0,
            'chapters_found': 0
        }
    
    def validate_before_conversion(self) -> bool:
        """转换前的质量检查"""
        print("🔍 执行转换前质量检查...")
        self.issues.clear()
        self.warnings.clear()
        
        # 检查环境依赖
        self._check_dependencies()
        
        # 检查源文件结构
        self._check_source_structure()
        
        # 检查源文件内容
        self._check_source_content()
        
        # 输出检查结果
        self._report_pre_conversion_results()
        
        return len(self.issues) == 0
    
    def validate_after_conversion(self, output_format: str) -> bool:
        """转换后的质量检查"""
        print("✅ 执行转换后质量检查...")
        
        # 检查输出文件
        success = self._check_output_files(output_format)
        
        # 生成质量报告
        self._generate_quality_report()
        
        return success
    
    def _check_dependencies(self) -> None:
        """检查系统依赖"""
        print("  检查系统依赖...")
        
        # 检查Pandoc
        try:
            import subprocess
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.issues.append("Pandoc未正确安装")
            else:
                print("  ✅ Pandoc已安装")
        except FileNotFoundError:
            self.issues.append("Pandoc未安装或不在PATH中")
        
        # 检查XeLaTeX
        try:
            result = subprocess.run(['xelatex', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.warnings.append("XeLaTeX未安装，无法生成PDF")
            else:
                print("  ✅ XeLaTeX已安装")
        except FileNotFoundError:
            self.warnings.append("XeLaTeX未安装，无法生成PDF")
    
    def _check_source_structure(self) -> None:
        """检查源文件结构"""
        print("  检查源文件结构...")
        
        # 检查文档根目录
        if not config.docs_dir.exists():
            self.issues.append(f"文档根目录不存在: {config.docs_dir}")
            return
        
        # 检查章节目录
        chapters_dir = config.docs_dir / "chapters"
        if not chapters_dir.exists():
            self.issues.append(f"章节目录不存在: {chapters_dir}")
            return
        
        # 检查各章节
        found_chapters = 0
        for chapter_key in config.chapter_order.keys():
            chapter_dir = chapters_dir / chapter_key
            if chapter_dir.exists():
                found_chapters += 1
                # 检查章节主文件
                main_file = chapter_dir / f"{chapter_key}.md"
                if not main_file.exists():
                    self.warnings.append(f"章节主文件不存在: {main_file}")
            else:
                self.warnings.append(f"章节目录不存在: {chapter_dir}")
        
        self.stats['chapters_found'] = found_chapters
        print(f"  找到 {found_chapters} 个章节目录")
    
    def _check_source_content(self) -> None:
        """检查源文件内容质量"""
        print("  检查源文件内容...")
        
        chapters_dir = config.docs_dir / "chapters"
        if not chapters_dir.exists():
            return
        
        for chapter_key in config.chapter_order.keys():
            chapter_dir = chapters_dir / chapter_key
            if not chapter_dir.exists():
                continue
            
            # 检查所有Markdown文件
            md_files = list(chapter_dir.glob("*.md"))
            self.stats['files_processed'] += len(md_files)
            
            for md_file in md_files:
                self._check_markdown_file(md_file)
    
    def _check_markdown_file(self, file_path: Path) -> None:
        """检查单个Markdown文件"""
        try:
            # 尝试读取文件
            content = self._read_file_safe(file_path)
            if not content:
                self.issues.append(f"无法读取文件: {file_path}")
                return
            
            # 检查编码问题
            try:
                content.encode('utf-8')
            except UnicodeEncodeError:
                self.warnings.append(f"文件编码可能有问题: {file_path}")
            
            # 检查图片引用
            self._check_images_in_file(content, file_path)
            
            # 检查代码块
            self._check_code_blocks_in_file(content, file_path)
            
            # 检查标题结构
            self._check_heading_structure(content, file_path)
            
        except Exception as e:
            self.issues.append(f"检查文件 {file_path} 时出错: {e}")
    
    def _read_file_safe(self, file_path: Path) -> Optional[str]:
        """安全读取文件"""
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return None
    
    def _check_images_in_file(self, content: str, file_path: Path) -> None:
        """检查文件中的图片引用"""
        image_refs = re.findall(r'!\[.*?\]\((.*?)\)', content)
        self.stats['images_found'] += len(image_refs)
        
        for image_ref in image_refs:
            # 检查图片文件是否存在
            image_found = False
            
            # 可能的搜索路径
            search_paths = [
                file_path.parent / image_ref,
                file_path.parent / "images" / Path(image_ref).name,
                config.docs_dir / "assets" / "images" / Path(image_ref).name
            ]
            
            for search_path in search_paths:
                if search_path.exists():
                    image_found = True
                    break
            
            # 递归搜索
            if not image_found:
                for img_file in config.docs_dir.rglob(Path(image_ref).name):
                    if img_file.suffix.lower() in config.image_extensions:
                        image_found = True
                        break
            
            if not image_found:
                self.warnings.append(f"图片文件未找到: {image_ref} (在 {file_path})")
    
    def _check_code_blocks_in_file(self, content: str, file_path: Path) -> None:
        """检查代码块"""
        code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', content, re.DOTALL)
        self.stats['code_blocks_found'] += len(code_blocks)
        
        for i, (language, code_content) in enumerate(code_blocks):
            if not language or language.strip() == '':
                self.warnings.append(f"代码块缺少语言标识 (第{i+1}个) 在 {file_path}")
            
            # 检查代码块是否正确闭合
            if not code_content.strip():
                self.warnings.append(f"代码块内容为空 (第{i+1}个) 在 {file_path}")
    
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
                        f"标题级别跳跃过大 (第{line_no}行) 在 {file_path}: {line.strip()}"
                    )
                
                prev_level = level
    
    def _check_output_files(self, output_format: str) -> bool:
        """检查输出文件"""
        if output_format == 'pdf':
            output_file = config.get_output_path("textbook.pdf")
        elif output_format == 'latex':
            output_file = config.get_output_path("textbook.tex")
        else:
            return False
        
        if not output_file.exists():
            print(f"❌ 输出文件不存在: {output_file}")
            return False
        
        file_size = output_file.stat().st_size
        if file_size < 1024:  # 小于1KB可能有问题
            print(f"⚠️  输出文件过小: {output_file} ({file_size} bytes)")
            return False
        
        print(f"✅ 输出文件生成成功: {output_file} ({file_size} bytes)")
        return True
    
    def _report_pre_conversion_results(self) -> None:
        """报告转换前检查结果"""
        print("\n📊 转换前质量检查结果:")
        print(f"  处理文件: {self.stats['files_processed']}")
        print(f"  发现章节: {self.stats['chapters_found']}")
        print(f"  发现图片: {self.stats['images_found']}")
        print(f"  发现代码块: {self.stats['code_blocks_found']}")
        
        if self.issues:
            print(f"\n❌ 发现 {len(self.issues)} 个严重问题:")
            for issue in self.issues:
                print(f"  - {issue}")
        
        if self.warnings:
            print(f"\n⚠️  发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.issues and not self.warnings:
            print("✅ 所有检查通过！")
    
    def _generate_quality_report(self) -> None:
        """生成质量报告"""
        report_file = config.get_output_path("quality_report.txt")
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# 智慧水利教材转换质量报告\n\n")
                f.write(f"生成时间: {self._get_current_time()}\n\n")
                
                f.write("## 统计信息\n")
                for key, value in self.stats.items():
                    f.write(f"- {key}: {value}\n")
                f.write("\n")
                
                if self.issues:
                    f.write(f"## 严重问题 ({len(self.issues)})\n")
                    for i, issue in enumerate(self.issues, 1):
                        f.write(f"{i}. {issue}\n")
                    f.write("\n")
                
                if self.warnings:
                    f.write(f"## 警告信息 ({len(self.warnings)})\n")
                    for i, warning in enumerate(self.warnings, 1):
                        f.write(f"{i}. {warning}\n")
                    f.write("\n")
                
                f.write("## 建议\n")
                if self.issues:
                    f.write("- 请先解决所有严重问题后再进行转换\n")
                if self.warnings:
                    f.write("- 建议修复警告信息以获得更好的转换效果\n")
                if not self.issues and not self.warnings:
                    f.write("- 质量检查通过，可以安全进行转换\n")
            
            print(f"📄 质量报告已生成: {report_file}")
            
        except Exception as e:
            print(f"⚠️  生成质量报告失败: {e}")
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_issues_count(self) -> int:
        """获取问题数量"""
        return len(self.issues)
    
    def get_warnings_count(self) -> int:
        """获取警告数量"""
        return len(self.warnings)

# 导出验证器实例
validator = QualityValidator()