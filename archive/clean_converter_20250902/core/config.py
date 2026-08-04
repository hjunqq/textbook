#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器 - 配置模块
简化统一的配置管理
"""

import os
from pathlib import Path
from typing import Dict, List

class Config:
    """统一配置管理"""
    
    def __init__(self):
        # 基础路径配置
        self.base_dir = Path(__file__).parent.parent
        self.project_root = self.base_dir.parent.parent
        self.docs_dir = self.project_root / "docs"
        self.output_dir = self.base_dir / "output"
        self.templates_dir = self.base_dir / "templates"
        
        # 创建必要目录
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        
        # 章节顺序配置
        self.chapter_order = {
            'chapter01': '第一章 智慧水利概述与平台架构基础',
            'chapter02': '第二章 软件工程基础与需求分析',
            'chapter03': '第三章 版本控制与协作开发',
            'chapter04': '第四章 数据库设计与数据管理',
            'chapter05': '第五章 后端开发与API设计',
            'chapter06': '第六章 倾斜摄影三维建模技术',
            'chapter07': '第七章 前端开发与用户界面设计',
            'chapter08': '第八章 系统集成与部署',
            'chapter09': '第九章 系统测试与质量保证'
        }
        
        # Pandoc配置
        self.pandoc_options = [
            '--from=markdown',
            '--to=latex',
            '--standalone',
            '--toc',
            '--number-sections',
            '--highlight-style=tango',
            '--pdf-engine=xelatex'
        ]
        
        # 图片处理配置
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp', '.wmf', '.emf'}
        
        # 预处理配置
        self.preprocessing_rules = {
            'fix_encoding': True,
            'standardize_headings': True,
            'unify_image_paths': True,
            'fix_code_blocks': True,
            'convert_admonitions': True,
            'remove_yaml_frontmatter': True
        }
    
    def get_chapter_title(self, chapter_key: str) -> str:
        """获取章节标题"""
        return self.chapter_order.get(chapter_key, f"第{chapter_key[-2:]}章")
    
    def get_output_path(self, filename: str) -> Path:
        """获取输出文件路径"""
        return self.output_dir / filename
    
    def get_template_path(self, template_name: str) -> Path:
        """获取模板文件路径"""
        return self.templates_dir / template_name

# 全局配置实例
config = Config()