#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器 - 核心转换引擎
统一的文档转换处理
"""

import subprocess
import re
from pathlib import Path
from typing import List, Tuple, Optional
from .config import config
from .preprocessor import preprocessor

class TextbookConverter:
    """教材转换核心引擎"""
    
    def __init__(self):
        self.temp_files = []
    
    def convert_textbook(self, output_format: str = 'pdf') -> bool:
        """转换完整教材"""
        print("🚀 开始教材转换流程")
        
        try:
            # 1. 发现和收集文件
            print("📁 发现章节文件...")
            chapters = self._discover_chapters()
            if not chapters:
                print("❌ 未找到章节文件")
                return False
            
            print(f"✅ 发现 {len(chapters)} 个文件")
            
            # 2. 预处理并合并
            print("🔧 预处理Markdown内容...")
            merged_content = self._process_and_merge_chapters(chapters)
            
            # 3. 保存合并的Markdown文件
            merged_md = config.get_output_path("textbook_merged.md")
            with open(merged_md, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            print(f"✅ 合并文件保存到: {merged_md}")
            
            # 4. 使用Pandoc转换
            print("🔄 执行Pandoc转换...")
            if output_format == 'pdf':
                success = self._convert_to_pdf(merged_md)
            elif output_format == 'latex':
                success = self._convert_to_latex(merged_md)
            else:
                print(f"❌ 不支持的输出格式: {output_format}")
                return False
            
            if success:
                print("🎉 转换完成！")
                return True
            else:
                print("❌ 转换失败")
                return False
                
        except Exception as e:
            print(f"❌ 转换过程出错: {e}")
            return False
        finally:
            self._cleanup_temp_files()
    
    def _discover_chapters(self) -> List[Tuple[str, Path]]:
        """发现所有章节文件"""
        chapters = []
        
        # 前言文件
        preface = config.docs_dir / "前言.md"
        if preface.exists():
            chapters.append(('preface', preface))
        
        # 章节文件
        chapters_dir = config.docs_dir / "chapters"
        if chapters_dir.exists():
            # 按配置顺序处理章节
            for chapter_key in config.chapter_order.keys():
                chapter_dir = chapters_dir / chapter_key
                if not chapter_dir.exists():
                    continue
                
                # 章节主文件
                main_file = chapter_dir / f"{chapter_key}.md"
                if main_file.exists():
                    chapters.append(('chapter', main_file))
                
                # 章节的section文件
                section_files = sorted(chapter_dir.glob("section*.md"))
                for section_file in section_files:
                    chapters.append(('section', section_file))
        
        # 附录文件
        appendix_dir = config.project_root / "appendix"
        if appendix_dir.exists():
            appendix_files = sorted(appendix_dir.glob("*.md"))
            for appendix_file in appendix_files:
                chapters.append(('appendix', appendix_file))
        
        return chapters
    
    def _process_and_merge_chapters(self, chapters: List[Tuple[str, Path]]) -> str:
        """预处理并合并章节内容"""
        merged_parts = []
        
        for file_type, file_path in chapters:
            print(f"  处理 {file_type}: {file_path.name}")
            
            # 预处理文件内容
            processed_content = preprocessor.process_file(file_path, file_type)
            
            if processed_content.strip():
                merged_parts.append(processed_content)
                merged_parts.append("")  # 添加分隔空行
        
        # 合并所有内容
        merged_content = "\\n".join(merged_parts)
        
        # 最终清理
        merged_content = self._final_cleanup(merged_content)
        
        return merged_content
    
    def _final_cleanup(self, content: str) -> str:
        """最终内容清理"""
        # 修复多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 修复标题前的空行
        content = re.sub(r'\n+(?=#)', '\n\n', content)
        
        # 确保代码块前后有空行
        content = re.sub(r'(?<!\n)\n```', '\n\n```', content)
        content = re.sub(r'```\n(?!\n)', '```\n\n', content)
        
        return content.strip() + '\n'
    
    def _convert_to_pdf(self, input_file: Path) -> bool:
        """转换为PDF"""
        output_file = config.get_output_path("textbook.pdf")
        
        # 使用相对路径，因为我们在output目录中执行
        cmd = [
            'pandoc',
            'textbook_merged.md',  # 相对路径
            '-o', 'textbook.pdf',  # 相对路径
            '--from=markdown',
            '--to=pdf',
            '--pdf-engine=xelatex',
            '--standalone',
            '--toc',
            '--number-sections'
        ]
        
        return self._run_pandoc_command(cmd, output_file)
    
    def _convert_to_latex(self, input_file: Path) -> bool:
        """转换为LaTeX"""
        output_file = config.get_output_path("textbook.tex")
        
        # 使用相对路径，因为我们在output目录中执行
        cmd = [
            'pandoc',
            'textbook_merged.md',  # 相对路径
            '-o', 'textbook.tex',  # 相对路径
            '--from=markdown',
            '--to=latex',
            '--standalone',
            '--toc',
            '--number-sections'
        ]
        
        success = self._run_pandoc_command(cmd, output_file)
        
        if success:
            # 后处理LaTeX文件
            self._post_process_latex(output_file)
        
        return success
    
    def _run_pandoc_command(self, cmd: List[str], output_file: Path) -> bool:
        """执行Pandoc命令"""
        try:
            print(f"  执行命令: {' '.join(cmd)}")
            print(f"  工作目录: {config.output_dir}")
            
            # 在输出目录中执行命令，确保图片路径正确
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', cwd=config.output_dir)
            
            if result.returncode == 0:
                if output_file.exists():
                    print(f"✅ 生成文件: {output_file}")
                    return True
                else:
                    print(f"❌ 命令成功但输出文件不存在: {output_file}")
                    return False
            else:
                print(f"❌ Pandoc错误 (返回码: {result.returncode})")
                if result.stderr:
                    print(f"错误信息: {result.stderr}")
                if result.stdout:
                    print(f"输出信息: {result.stdout}")
                return False
                
        except FileNotFoundError:
            print("❌ Pandoc未安装或不在PATH中")
            return False
        except Exception as e:
            print(f"❌ 执行Pandoc命令时出错: {e}")
            return False
    
    def _post_process_latex(self, latex_file: Path) -> None:
        """后处理LaTeX文件"""
        print("🔧 后处理LaTeX文件...")
        
        try:
            with open(latex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复常见的LaTeX问题
            content = self._fix_latex_issues(content)
            
            with open(latex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ LaTeX后处理完成")
            
        except Exception as e:
            print(f"⚠️  LaTeX后处理失败: {e}")
    
    def _fix_latex_issues(self, content: str) -> str:
        """修复LaTeX常见问题"""
        # 修复中文引号
        content = content.replace('"', '``').replace('"', "''")
        
        # 修复图片路径
        content = re.sub(r'\\includegraphics\{([^}]+)\}', r'\\includegraphics[width=0.8\\textwidth]{\\1}', content)
        
        # 修复表格问题
        content = content.replace('longtabu', 'longtable')
        
        # 添加中文支持的包
        if '\\usepackage{ctex}' not in content and '\\documentclass' in content:
            content = content.replace('\\documentclass{article}', '\\documentclass[UTF8]{ctexart}')
            content = content.replace('\\documentclass{book}', '\\documentclass[UTF8]{ctexbook}')
        
        return content
    
    def _cleanup_temp_files(self) -> None:
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception as e:
                print(f"警告：清理临时文件失败 {temp_file}: {e}")
        self.temp_files.clear()

# 导出转换器实例
converter = TextbookConverter()