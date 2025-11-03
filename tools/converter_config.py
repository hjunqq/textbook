"""
智慧水利教材转换器 - 核心配置模块
软件工程设计：配置管理
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ConverterConfig:
    """转换器配置类"""
    
    # 输入输出路径
    # 使用仓库根相对路径，支持从仓库根或 tools 目录运行
    source_dir: str = "docs/chapters"
    preface_file: str = "docs/前言.md"
    output_dir: str = "output"
    temp_dir: str = "temp"
    
    # LaTeX配置
    main_tex_name: str = "main.tex"
    documentclass: str = "book"
    font_family: str = "Microsoft YaHei"
    paper_size: str = "a4paper"
    font_size: str = "12pt"
    
    # 转换选项
    enable_chapter_numbering: bool = True
    enable_section_numbering: bool = True
    enable_math_processing: bool = True
    enable_figure_processing: bool = True
    enable_code_processing: bool = True
    enable_admonition_processing: bool = True
    
    # 章节配置
    chapter_count: int = 9
    chapter_names: Dict[int, str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.chapter_names is None:
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
        return f"第{self._num_to_chinese(chapter_num)}章 {self.chapter_names.get(chapter_num, '未知章节')}"
    
    def _num_to_chinese(self, num: int) -> str:
        """数字转中文"""
        chinese_nums = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        return chinese_nums[num] if 1 <= num <= 10 else str(num)

class PathManager:
    """路径管理器"""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        Path(self.config.output_dir).mkdir(exist_ok=True)
        Path(self.config.temp_dir).mkdir(exist_ok=True)
        Path(os.path.join(self.config.output_dir, "chapters")).mkdir(exist_ok=True)
        Path(os.path.join(self.config.output_dir, "images")).mkdir(exist_ok=True)
    
    def get_source_chapter_dir(self, chapter_num: int) -> Path:
        """获取源章节目录"""
        return Path(self.config.source_dir) / f"chapter{chapter_num:02d}"
    
    def get_output_chapter_tex(self, chapter_num: int) -> Path:
        """获取输出章节tex文件路径"""
        return Path(self.config.output_dir) / "chapters" / f"chapter{chapter_num:02d}.tex"
    
    def get_main_tex_path(self) -> Path:
        """获取主tex文件路径"""
        return Path(self.config.output_dir) / self.config.main_tex_name

# 默认配置实例
DEFAULT_CONFIG = ConverterConfig()
