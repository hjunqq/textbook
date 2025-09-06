"""
配置管理模块
提供转换器的配置管理功能
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class ConverterConfig:
    """转换器配置类"""
    
    # 路径配置
    source_dir: str = "../docs/chapters"
    preface_file: str = "../docs/前言.md"
    output_dir: str = "output"
    temp_dir: str = "temp"
    template_dir: str = "templates"
    
    # LaTeX配置
    main_tex_name: str = "main.tex"
    document_class: str = "book"
    font_family: str = "Microsoft YaHei"
    paper_size: str = "a4paper" 
    font_size: str = "12pt"
    
    # 处理选项
    enable_chapter_numbering: bool = True
    enable_section_numbering: bool = True
    enable_math_processing: bool = True
    enable_figure_processing: bool = True
    enable_code_processing: bool = True
    enable_admonition_processing: bool = True
    
    # 章节配置
    chapter_count: int = 9
    chapter_names: Dict[int, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.chapter_names:
            self.chapter_names = {
                1: "智慧水利概述与平台架构基础",
                2: "软件工程基础与需求分析",
                3: "软件模块详细设计", 
                4: "前端开发技术",
                5: "后端开发技术",
                6: "三维场景技术基础",
                7: "三维场景的观测数据展示",
                8: "典型应用",
                9: "结语"
            }
    
    def get_chapter_title(self, chapter_num: int) -> str:
        """获取章节标题"""
        chinese_nums = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        chinese_num = chinese_nums[chapter_num] if 1 <= chapter_num <= 10 else str(chapter_num)
        return f"第{chinese_num}章 {self.chapter_names.get(chapter_num, '未知章节')}"
    
    def validate(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证路径
        if not Path(self.source_dir).exists():
            errors.append(f"源目录不存在: {self.source_dir}")
        
        if Path(self.preface_file).exists() and not Path(self.preface_file).is_file():
            errors.append(f"前言文件不是有效文件: {self.preface_file}")
        
        # 验证章节配置
        if self.chapter_count <= 0:
            errors.append("章节数量必须大于0")
        
        if len(self.chapter_names) != self.chapter_count:
            errors.append(f"章节名称数量({len(self.chapter_names)})与章节数量({self.chapter_count})不匹配")
        
        return errors

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """初始化配置管理器"""
        self.config_file = config_file or Path("config.yaml")
        self.config: Optional[ConverterConfig] = None
    
    def load_config(self) -> ConverterConfig:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    self.config = ConverterConfig(**data)
            except Exception as e:
                print(f"配置文件加载失败: {e}")
                self.config = ConverterConfig()
        else:
            self.config = ConverterConfig()
        
        return self.config
    
    def save_config(self, config: ConverterConfig) -> None:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                # 转换为字典以便序列化
                config_dict = {
                    'source_dir': config.source_dir,
                    'preface_file': config.preface_file,
                    'output_dir': config.output_dir,
                    'temp_dir': config.temp_dir,
                    'template_dir': config.template_dir,
                    'main_tex_name': config.main_tex_name,
                    'document_class': config.document_class,
                    'font_family': config.font_family,
                    'paper_size': config.paper_size,
                    'font_size': config.font_size,
                    'enable_chapter_numbering': config.enable_chapter_numbering,
                    'enable_section_numbering': config.enable_section_numbering,
                    'enable_math_processing': config.enable_math_processing,
                    'enable_figure_processing': config.enable_figure_processing,
                    'enable_code_processing': config.enable_code_processing,
                    'enable_admonition_processing': config.enable_admonition_processing,
                    'chapter_count': config.chapter_count,
                    'chapter_names': config.chapter_names
                }
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            self.config = config
        except Exception as e:
            raise Exception(f"配置保存失败: {e}")
    
    def get_config(self) -> ConverterConfig:
        """获取配置"""
        if self.config is None:
            self.config = self.load_config()
        return self.config

class PathManager:
    """路径管理器"""
    
    def __init__(self, config: ConverterConfig):
        """初始化路径管理器"""
        self.config = config
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """确保必要目录存在"""
        directories = [
            Path(self.config.output_dir),
            Path(self.config.temp_dir),
            Path(self.config.output_dir) / "chapters",
            Path(self.config.output_dir) / "images"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_source_chapter_dir(self, chapter_num: int) -> Path:
        """获取源章节目录"""
        return Path(self.config.source_dir) / f"chapter{chapter_num:02d}"
    
    def get_source_chapter_file(self, chapter_num: int) -> Path:
        """获取源章节主文件"""
        chapter_dir = self.get_source_chapter_dir(chapter_num)
        
        # 尝试不同的文件名模式
        patterns = [
            f"chapter{chapter_num:02d}.md",
            f"chapter{chapter_num}.md",
            f"section{chapter_num:02d}-*.md"
        ]
        
        for pattern in patterns:
            files = list(chapter_dir.glob(pattern))
            if files:
                return files[0]
        
        raise FileNotFoundError(f"未找到第{chapter_num}章的源文件")
    
    def get_output_chapter_tex(self, chapter_num: int) -> Path:
        """获取输出章节tex文件路径"""
        return Path(self.config.output_dir) / "chapters" / f"chapter{chapter_num:02d}.tex"
    
    def get_main_tex_path(self) -> Path:
        """获取主tex文件路径"""
        return Path(self.config.output_dir) / self.config.main_tex_name
    
    def get_temp_file_path(self, filename: str) -> Path:
        """获取临时文件路径"""
        return Path(self.config.temp_dir) / filename
    
    def get_preface_path(self) -> Path:
        """获取前言文件路径"""
        return Path(self.config.preface_file)

# 默认配置实例
DEFAULT_CONFIG = ConverterConfig()