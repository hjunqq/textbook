"""
转换器应用程序核心模块
"""

import logging
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .config import ConverterConfig, ConfigManager, PathManager
from ..processors.content_processor import ContentProcessor
from ..templates.template_engine import TemplateEngine
from ..utils.file_manager import FileManager
from ..utils.logger import Logger

@dataclass
class ConversionResult:
    """转换结果数据类"""
    success: bool
    message: str
    output_files: List[Path] = None
    errors: List[str] = None
    warnings: List[str] = None
    execution_time: float = 0.0
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class ConverterApplication:
    """转换器主应用程序 - 外观模式"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化应用程序"""
        # 加载配置
        self.config_manager = ConfigManager(Path(config_path) if config_path else None)
        self.config = self.config_manager.load_config()
        
        # 验证配置
        config_errors = self.config.validate()
        if config_errors:
            raise ValueError(f"配置验证失败: {config_errors}")
        
        # 初始化核心组件
        self.path_manager = PathManager(self.config)
        self.file_manager = FileManager()
        self.content_processor = ContentProcessor(self.config)
        self.template_engine = TemplateEngine(self.config)
        
        # 初始化日志
        self.logger = Logger("ConverterApplication")
        
        # 初始化状态
        self.is_initialized = True
    
    def validate_environment(self) -> ConversionResult:
        """验证运行环境"""
        self.logger.info("验证运行环境...")
        
        errors = []
        warnings = []
        
        try:
            # 检查Pandoc
            import subprocess
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                errors.append("Pandoc未安装或无法访问")
            else:
                self.logger.info(f"Pandoc版本: {result.stdout.split()[1] if len(result.stdout.split()) > 1 else '未知'}")
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("Pandoc未安装或无法访问")
        except Exception as e:
            warnings.append(f"Pandoc检查时出现异常: {e}")
        
        try:
            # 检查XeLaTeX
            result = subprocess.run(['xelatex', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                errors.append("XeLaTeX未安装或无法访问")
            else:
                self.logger.info("XeLaTeX可用")
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("XeLaTeX未安装或无法访问")
        except Exception as e:
            warnings.append(f"XeLaTeX检查时出现异常: {e}")
        
        # 检查源目录
        if not Path(self.config.source_dir).exists():
            errors.append(f"源目录不存在: {self.config.source_dir}")
        
        success = len(errors) == 0
        message = "环境验证通过" if success else f"环境验证失败: {len(errors)}个错误"
        
        return ConversionResult(
            success=success,
            message=message,
            errors=errors,
            warnings=warnings
        )
    
    def convert_single_chapter(self, chapter_num: int) -> ConversionResult:
        """转换单个章节"""
        start_time = time.time()
        self.logger.info(f"开始转换第{chapter_num}章...")
        
        try:
            # 查找章节源文件
            chapter_file = self.path_manager.get_source_chapter_file(chapter_num)
            if not chapter_file.exists():
                return ConversionResult(
                    success=False,
                    message=f"第{chapter_num}章源文件不存在: {chapter_file}",
                    execution_time=time.time() - start_time
                )
            
            # 读取内容
            content = self.file_manager.read_file(chapter_file)
            self.logger.info(f"读取章节内容: {len(content)}字符")
            
            # 处理内容
            processed_content = self.content_processor.process_chapter_content(
                content, chapter_num, self.config.get_chapter_title(chapter_num)
            )
            
            # 生成LaTeX
            latex_content = self.template_engine.render_chapter_template(
                chapter_num=chapter_num,
                title=self.config.get_chapter_title(chapter_num),
                content=processed_content
            )
            
            # 保存输出文件
            output_file = self.path_manager.get_output_chapter_tex(chapter_num)
            self.file_manager.write_file(output_file, latex_content)
            
            execution_time = time.time() - start_time
            self.logger.info(f"第{chapter_num}章转换完成，耗时: {execution_time:.2f}秒")
            
            return ConversionResult(
                success=True,
                message=f"第{chapter_num}章转换成功",
                output_files=[output_file],
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"第{chapter_num}章转换失败: {str(e)}"
            self.logger.error(error_msg)
            
            return ConversionResult(
                success=False,
                message=error_msg,
                errors=[str(e)],
                execution_time=execution_time
            )
    
    def convert_preface(self) -> ConversionResult:
        """转换前言"""
        start_time = time.time()
        self.logger.info("开始转换前言...")
        
        try:
            preface_file = self.path_manager.get_preface_path()
            if not preface_file.exists():
                return ConversionResult(
                    success=False,
                    message=f"前言文件不存在: {preface_file}",
                    execution_time=time.time() - start_time
                )
            
            # 读取前言内容
            content = self.file_manager.read_file(preface_file)
            
            # 处理前言内容
            processed_content = self.content_processor.process_preface_content(content)
            
            # 生成LaTeX
            latex_content = self.template_engine.render_preface_template(
                title="前言",
                content=processed_content
            )
            
            # 保存输出文件
            output_file = Path(self.config.output_dir) / "chapters" / "preface.tex"
            self.file_manager.write_file(output_file, latex_content)
            
            execution_time = time.time() - start_time
            self.logger.info(f"前言转换完成，耗时: {execution_time:.2f}秒")
            
            return ConversionResult(
                success=True,
                message="前言转换成功",
                output_files=[output_file],
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"前言转换失败: {str(e)}"
            self.logger.error(error_msg)
            
            return ConversionResult(
                success=False,
                message=error_msg,
                errors=[str(e)],
                execution_time=execution_time
            )
    
    def convert_full_document(self) -> ConversionResult:
        """转换完整文档"""
        start_time = time.time()
        self.logger.info("开始转换完整文档...")
        
        all_errors = []
        all_warnings = []
        output_files = []
        
        try:
            # 转换前言
            preface_result = self.convert_preface()
            if preface_result.success:
                output_files.extend(preface_result.output_files)
            else:
                all_errors.extend(preface_result.errors)
                all_warnings.append("前言转换失败，继续处理章节")
            
            # 转换所有章节
            for chapter_num in range(1, self.config.chapter_count + 1):
                chapter_result = self.convert_single_chapter(chapter_num)
                
                if chapter_result.success:
                    output_files.extend(chapter_result.output_files)
                    self.logger.info(f"第{chapter_num}章转换成功")
                else:
                    all_errors.extend(chapter_result.errors)
                    all_warnings.append(f"第{chapter_num}章转换失败")
            
            # 生成主文档
            if output_files:  # 只有在有成功转换的内容时才生成主文档
                main_result = self._generate_main_document()
                if main_result.success:
                    output_files.extend(main_result.output_files)
                else:
                    all_errors.extend(main_result.errors)
            
            execution_time = time.time() - start_time
            
            success = len(all_errors) == 0
            message = f"文档转换完成，成功处理{len(output_files)}个文件" if success else f"文档转换部分成功，{len(all_errors)}个错误"
            
            self.logger.info(f"完整文档转换完成，总耗时: {execution_time:.2f}秒")
            
            return ConversionResult(
                success=success,
                message=message,
                output_files=output_files,
                errors=all_errors,
                warnings=all_warnings,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"完整文档转换失败: {str(e)}"
            self.logger.error(error_msg)
            
            return ConversionResult(
                success=False,
                message=error_msg,
                errors=[str(e)] + all_errors,
                warnings=all_warnings,
                execution_time=execution_time
            )
    
    def _generate_main_document(self) -> ConversionResult:
        """生成主LaTeX文档"""
        try:
            self.logger.info("生成主LaTeX文档...")
            
            # 查找所有章节文件
            chapters_dir = Path(self.config.output_dir) / "chapters"
            chapter_files = []
            
            # 前言
            preface_file = chapters_dir / "preface.tex"
            if preface_file.exists():
                chapter_files.append(("preface", "前言"))
            
            # 章节
            for i in range(1, self.config.chapter_count + 1):
                chapter_file = chapters_dir / f"chapter{i:02d}.tex"
                if chapter_file.exists():
                    chapter_files.append((f"chapter{i:02d}", self.config.get_chapter_title(i)))
            
            # 生成主模板
            main_content = self.template_engine.render_main_template(chapter_files)
            
            # 保存主文件
            main_file = self.path_manager.get_main_tex_path()
            self.file_manager.write_file(main_file, main_content)
            
            return ConversionResult(
                success=True,
                message="主文档生成成功",
                output_files=[main_file]
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                message=f"主文档生成失败: {str(e)}",
                errors=[str(e)]
            )
    
    def generate_pdf(self) -> ConversionResult:
        """生成PDF文件"""
        start_time = time.time()
        self.logger.info("开始生成PDF...")
        
        try:
            import subprocess
            
            main_tex_file = self.path_manager.get_main_tex_path()
            if not main_tex_file.exists():
                return ConversionResult(
                    success=False,
                    message="主LaTeX文件不存在，请先进行转换",
                    execution_time=time.time() - start_time
                )
            
            # 切换到输出目录
            output_dir = Path(self.config.output_dir)
            
            # 执行XeLaTeX编译
            cmd = ['xelatex', '-interaction=nonstopmode', main_tex_file.name]
            
            self.logger.info(f"执行编译命令: {' '.join(cmd)}")
            
            # 编译两次以生成正确的目录和引用
            for i in range(2):
                result = subprocess.run(
                    cmd,
                    cwd=output_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode != 0:
                    self.logger.error(f"XeLaTeX编译失败 (第{i+1}次)")
                    return ConversionResult(
                        success=False,
                        message=f"PDF编译失败: {result.stderr}",
                        errors=[result.stderr],
                        execution_time=time.time() - start_time
                    )
            
            # 检查PDF文件是否生成
            pdf_file = output_dir / main_tex_file.stem + ".pdf"
            if not pdf_file.exists():
                return ConversionResult(
                    success=False,
                    message="PDF文件未生成",
                    execution_time=time.time() - start_time
                )
            
            execution_time = time.time() - start_time
            file_size = pdf_file.stat().st_size / (1024 * 1024)  # MB
            
            self.logger.info(f"PDF生成成功: {pdf_file} ({file_size:.1f}MB)，耗时: {execution_time:.2f}秒")
            
            return ConversionResult(
                success=True,
                message=f"PDF生成成功 ({file_size:.1f}MB)",
                output_files=[pdf_file],
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired:
            return ConversionResult(
                success=False,
                message="PDF编译超时",
                errors=["编译过程超时（5分钟）"],
                execution_time=time.time() - start_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"PDF生成失败: {str(e)}"
            self.logger.error(error_msg)
            
            return ConversionResult(
                success=False,
                message=error_msg,
                errors=[str(e)],
                execution_time=execution_time
            )
    
    def cleanup_temp_files(self) -> None:
        """清理临时文件"""
        try:
            temp_dir = Path(self.config.temp_dir)
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                temp_dir.mkdir(exist_ok=True)
                self.logger.info("临时文件清理完成")
        except Exception as e:
            self.logger.warning(f"临时文件清理失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取转换器状态"""
        output_dir = Path(self.config.output_dir)
        
        status = {
            "initialized": self.is_initialized,
            "config_valid": len(self.config.validate()) == 0,
            "output_dir_exists": output_dir.exists(),
            "main_tex_exists": (output_dir / self.config.main_tex_name).exists(),
            "chapters_converted": 0,
            "pdf_exists": False
        }
        
        # 统计已转换的章节
        chapters_dir = output_dir / "chapters"
        if chapters_dir.exists():
            status["chapters_converted"] = len(list(chapters_dir.glob("chapter*.tex")))
        
        # 检查PDF是否存在
        pdf_file = output_dir / (self.config.main_tex_name.replace('.tex', '.pdf'))
        status["pdf_exists"] = pdf_file.exists()
        
        return status