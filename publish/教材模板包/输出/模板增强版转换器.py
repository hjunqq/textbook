#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版教材转换脚本 - 支持样式模板应用
主要功能：
1. 自动应用LaTeX模板中的预定义样式
2. 智能识别Markdown中的特殊语法
3. 转换为对应的LaTeX环境命令
4. 支持学习目标、关键概念、实践练习等

版本: v4.0 (模板增强版)
更新: 2025年8月27日
"""

import os
import sys
import subprocess
import glob
import shutil
import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class TemplateEnhancedConverter:
    """模板增强版教材转换器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.supported_formats = ['latex', 'pdf', 'docx', 'html']
        self.check_dependencies()
        
        # 样式模板映射
        self.style_patterns = {
            # 特殊环境识别模式
            'learning_objectives': [
                r'## 学习目标\s*\n(.*?)(?=\n## |\Z)',
                r'(?:学习目标|Learning Objectives?):?\s*\n((?:.*\n)*?)(?=\n\s*#+|\n\s*$|$)',
                r'!!! (?:note|info) "?(?:学习目标|Learning Objectives?)"?\s*\n((?:.*\n)*?)(?=\n!!!|\n\s*#+|\n\s*$|$)'
            ],
            'key_points': [
                r'## 关键概念\s*\n(.*?)(?=\n## |\Z)',
                r'(?:关键概念|Key Points?):?\s*\n((?:.*\n)*?)(?=\n\s*#+|\n\s*$|$)',
                r'!!! (?:important|warning) "?(?:关键概念|Key Points?)"?\s*\n((?:.*\n)*?)(?=\n!!!|\n\s*#+|\n\s*$|$)'
            ],
            'practice_exercise': [
                r'## 实践练习\s*\n(.*?)(?=\n## |\Z)',
                r'(?:实践练习|Practice Exercises?):?\s*\n((?:.*\n)*?)(?=\n\s*#+|\n\s*$|$)',
                r'!!! (?:note|tip) "?(?:实践练习|Practice Exercises?)"?\s*\n((?:.*\n)*?)(?=\n!!!|\n\s*#+|\n\s*$|$)'
            ],
            'attention': [
                r'!!! warning "注意"\s*\n((?:(?!\n!!!|\n##).*\n)*?)(?=\n!!!|\n## |\Z)',
                r'(?:注意|Attention|Warning):?\s*\n((?:.*\n)*?)(?=\n\s*#+|\n\s*$|$)',
                r'!!! (?:warning|danger|caution) "?(?:注意|Attention|Warning)"?\s*\n((?:.*\n)*?)(?=\n!!!|\n\s*#+|\n\s*$|$)'
            ],
            'chapter_summary': [
                r'## 本章小结\s*\n(.*?)(?=\n## |\Z)',
                r'(?:本章小结|章节摘要|Summary):?\s*\n((?:.*\n)*?)(?=\n\s*#+|\n\s*$|$)',
                r'!!! (?:summary|abstract) "?(?:本章小结|章节摘要|Summary)"?\s*\n((?:.*\n)*?)(?=\n!!!|\n\s*#+|\n\s*$|$)'
            ]
        }
        
        # Emoji到LaTeX图标的映射
        self.icon_map = {
            '💡': r'\faLightbulb',
            '🔑': r'\faKey', 
            '⚙️': r'\faCogs',
            '⚠️': r'\faExclamationTriangle',
            '📋': r'\faClipboardList',
            '🎯': r'\faTarget',
            '✅': r'\faCheck',
            '❌': r'\faTimes',
            '🔍': r'\faSearch',
            '📝': r'\faEdit',
        }

    def load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "input_format": "markdown",
            "output_format": "latex",
            "template_dir": "LaTeX模板",
            "output_dir": "输出",
            "source_encoding": "utf-8",
            "latex_engine": "xelatex",
            "use_custom_template": True,
            "apply_style_enhancements": True,
            "chapters": [],
            "preprocessing": {
                "fix_encoding": True,
                "standardize_format": True,
                "optimize_images": True,
                "fix_code_blocks": True,
                "remove_emojis": True,  # 启用emoji移除
                "apply_template_styles": True
            },
            "postprocessing": {
                "optimize_latex": True,
                "fix_chinese_fonts": True,
                "add_listings_config": True,
                "beautify_layout": True,
                "fix_document_structure": True,
                "apply_custom_environments": True
            },
            "style_settings": {
                "auto_detect_environments": True,
                "convert_code_blocks": True,
                "enhance_lists": True,
                "apply_emphasis": True
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"警告：读取配置文件失败，使用默认配置：{e}")
        
        return default_config
    
    def check_dependencies(self):
        """检查依赖工具"""
        self.available_tools = {}
        
        # 检查pandoc
        try:
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.available_tools['pandoc'] = True
            print("✓ Pandoc 可用")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.available_tools['pandoc'] = False
            print("✗ Pandoc 不可用")
        
        # 检查LaTeX
        for engine in ['xelatex', 'lualatex', 'pdflatex']:
            try:
                result = subprocess.run([engine, '--version'], 
                                      capture_output=True, text=True, check=True)
                self.available_tools[engine] = True
                print(f"✓ {engine} 可用")
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.available_tools[engine] = False
    
    def discover_chapters(self, source_dir: str) -> List[str]:
        """自动发现章节文件"""
        markdown_files = []
        
        print(f"正在扫描源目录: {source_dir}")
        
        # 首先添加根目录的主要文件
        main_files = ['index.md', '前言.md', 'README.md']
        for filename in main_files:
            filepath = os.path.join(source_dir, filename)
            if os.path.exists(filepath):
                markdown_files.append(filepath)
                print(f"找到主要文件: {filepath}")
        
        # 查找chapters目录 - 直接在source_dir下
        chapters_dir = os.path.join(source_dir, 'chapters')
        if os.path.exists(chapters_dir):
            print(f"找到章节目录: {chapters_dir}")
            chapter_dirs = sorted([d for d in os.listdir(chapters_dir) 
                                  if d.startswith('chapter') and 
                                  os.path.isdir(os.path.join(chapters_dir, d))])
            
            for chapter_dirname in chapter_dirs:
                chapter_path = os.path.join(chapters_dir, chapter_dirname)
                # 查找章节主文件
                main_chapter_file = os.path.join(chapter_path, f"{chapter_dirname}.md")
                if os.path.exists(main_chapter_file):
                    markdown_files.append(main_chapter_file)
                    print(f"找到章节文件: {main_chapter_file}")
                
                # 查找节文件
                section_files = sorted([f for f in os.listdir(chapter_path) 
                                       if f.startswith('section') and f.endswith('.md')])
                for section_file in section_files:
                    section_path = os.path.join(chapter_path, section_file)
                    markdown_files.append(section_path)
                    print(f"找到节文件: {section_path}")
        else:
            print(f"未找到章节目录: {chapters_dir}")
        
        print(f"总共找到 {len(markdown_files)} 个文件")
        return list(dict.fromkeys(markdown_files))  # 去重
    
    def apply_template_style_enhancements(self, content: str) -> str:
        """应用模板样式增强"""
        if not self.config['preprocessing']['apply_template_styles']:
            return content
        
        print("  应用模板样式增强...")
        
        # 1. 识别并转换特殊环境
        content = self.convert_special_environments(content)
        
        # 2. 增强代码块
        content = self.enhance_code_blocks(content)
        
        # 3. 转换强调文本
        content = self.convert_emphasis(content)
        
        # 4. 转换emoji为图标
        content = self.convert_emojis_to_icons(content)
        
        return content
    
    def convert_special_environments(self, content: str) -> str:
        """转换特殊环境"""
        if not self.config['style_settings']['auto_detect_environments']:
            return content
            
        for env_type, patterns in self.style_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
                # 从后往前替换，避免位置偏移问题
                for match in reversed(matches):
                    env_content = match.group(1).strip()
                    if env_content:
                        latex_env = self.create_latex_environment(env_type, env_content)
                        content = content[:match.start()] + latex_env + content[match.end():]
        
        return content
    
    def create_latex_environment(self, env_type: str, content: str) -> str:
        """创建LaTeX环境"""
        env_mapping = {
            'learning_objectives': 'learningobjectives',
            'key_points': 'keypoints', 
            'practice_exercise': 'practiceexercise',
            'attention': 'attention',
            'chapter_summary': 'chaptersummary'
        }
        
        latex_command = env_mapping.get(env_type, env_type)
        
        # 清理内容
        content = content.strip()
        
        return f"\n\\{latex_command}{{\n{content}\n}}\n"
    
    def enhance_code_blocks(self, content: str) -> str:
        """增强代码块"""
        if not self.config['style_settings']['convert_code_blocks']:
            return content
        
        # 转换带语言标识的代码块
        def replace_code_block(match):
            lang = match.group(1) if match.group(1) else ''
            code_content = match.group(2)
            
            # 语言映射
            lang_mapping = {
                'csharp': 'csharp',
                'cs': 'csharp', 
                'javascript': 'javascript',
                'js': 'javascript',
                'python': 'python',
                'py': 'python',
                'java': 'java',
                'sql': 'sql',
                'xml': 'xml',
                'html': 'xml',
                'css': 'css',
                'json': 'json',
                'bash': 'terminal',
                'shell': 'terminal',
                'terminal': 'terminal'
            }
            
            style = lang_mapping.get(lang.lower(), 'default')
            
            if style == 'default':
                return f"\\begin{{lstlisting}}\n{code_content}\n\\end{{lstlisting}}"
            else:
                return f"\\begin{{lstlisting}}[style={style}]\n{code_content}\n\\end{{lstlisting}}"
        
        # 匹配代码块模式
        code_block_pattern = r'```(\w+)?\s*\n(.*?)\n```'
        content = re.sub(code_block_pattern, replace_code_block, content, flags=re.DOTALL)
        
        return content
    
    def convert_emphasis(self, content: str) -> str:
        """转换强调文本"""
        if not self.config['style_settings']['apply_emphasis']:
            return content
            
        # 转换**重要**为\important{重要}
        content = re.sub(r'\*\*(.*?)\*\*', r'\\important{\1}', content)
        
        # 转换*高亮*为\highlight{高亮}  
        content = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\\highlight{\1}', content)
        
        # 转换`代码`为\code{代码}
        content = re.sub(r'`([^`]+)`', r'\\code{\1}', content)
        
        return content
    
    def convert_emojis_to_icons(self, content: str) -> str:
        """转换emoji为LaTeX图标"""
        if self.config['preprocessing']['remove_emojis']:
            # 如果设置移除emoji，则使用原来的移除逻辑
            return self.remove_emojis(content)
        
        # 转换已知的emoji
        for emoji, latex_icon in self.icon_map.items():
            content = content.replace(emoji, latex_icon)
        
        # 不移除其他未知的emoji，以避免误删中文字符
        # 原来的emoji正则表达式过于宽泛，会匹配到中文字符
        # 如需移除特定emoji，应使用更精确的模式
        
        return content
    
    def remove_emojis(self, content: str) -> str:
        """移除emoji字符，使用更精确的匹配"""
        # 首先转换已知的emoji为图标
        for emoji, latex_icon in self.icon_map.items():
            content = content.replace(emoji, latex_icon)
        
        # 然后移除常见的emoji字符，使用更精确的模式
        # 只移除确定的emoji范围，避免影响中文字符
        emoji_patterns = [
            r'[\U0001F600-\U0001F64F]',  # 表情符号
            r'[\U0001F300-\U0001F5FF]',  # 符号和象形文字
            r'[\U0001F680-\U0001F6FF]',  # 交通和地图符号
            r'[\U0001F1E0-\U0001F1FF]',  # 国旗
            r'[\U0001F700-\U0001F77F]',  # 炼金术符号
            r'[\U0001F780-\U0001F7FF]',  # 几何形状扩展
            r'[\U0001F800-\U0001F8FF]',  # 补充箭头-C
            r'[\U0001F900-\U0001F9FF]',  # 补充符号和象形文字
            r'[\U0001FA00-\U0001FA6F]',  # 国际象棋符号
            r'[\U0001FA70-\U0001FAFF]',  # 符号和象形文字扩展-A
        ]
        
        for pattern in emoji_patterns:
            content = re.sub(pattern, '', content, flags=re.UNICODE)
        
        return content
    
    def preprocess_markdown(self, input_files: List[str], temp_dir: str) -> List[str]:
        """预处理Markdown文件"""
        print("开始预处理Markdown文件...")
        
        os.makedirs(temp_dir, exist_ok=True)
        processed_files = []
        
        for input_file in input_files:
            print(f"处理文件：{input_file}")
            
            # 尝试多种编码读取文件
            content = None
            encodings_to_try = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'big5']
            
            for encoding in encodings_to_try:
                try:
                    with open(input_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    print(f"  使用编码 {encoding} 读取成功")
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if content is None:
                print(f"  警告：无法正确解码文件 {input_file}，跳过")
                continue
                
            # 清理可能干扰的字符
            content = content.replace('\ufeff', '')  # 移除BOM
            content = content.replace('\r\n', '\n')  # 统一换行符
            content = content.replace('\r', '\n')
            
            # 验证中文内容是否正常
            chinese_chars = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
            print(f"  检测到 {chinese_chars} 个中文字符")
            
            # 应用样式模板增强
            if self.config['preprocessing']['apply_template_styles']:
                content = self.apply_template_style_enhancements(content)
            
            # 标准化格式
            if self.config['preprocessing']['standardize_format']:
                content = self.standardize_markdown_format(content)
            
            # 修复代码块
            if self.config['preprocessing']['fix_code_blocks']:
                content = self.fix_code_blocks(content)
            
            # 优化图片引用
            if self.config['preprocessing']['optimize_images']:
                content = self.optimize_image_references(content, input_file)
            
            # 保存处理后的文件（强制使用 UTF-8）
            processed_file = os.path.join(temp_dir, os.path.basename(input_file))
            with open(processed_file, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            # 再次验证保存的文件
            with open(processed_file, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            saved_chinese_chars = len([c for c in saved_content if '\u4e00' <= c <= '\u9fff'])
            print(f"  保存后检测到 {saved_chinese_chars} 个中文字符")
            
            processed_files.append(processed_file)
        
        print(f"✓ 预处理完成，处理了 {len(processed_files)} 个文件")
        return processed_files
    
    def standardize_markdown_format(self, content: str) -> str:
        """标准化Markdown格式"""
        # 修复列表项格式
        content = re.sub(r'^(\s*)-\s+(.+)$', r'\1- \2', content, flags=re.MULTILINE)
        
        # 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 修复表格格式中的问题
        content = re.sub(r'\|([^|\n]*)\|', lambda m: '|' + m.group(1).strip() + '|', content)
        
        return content
    
    def fix_code_blocks(self, content: str) -> str:
        """修复代码块格式"""
        patterns = [
            (r'```\s*\n(.*?using.*?;)', r'```csharp\n\1'),
            (r'```\s*\n(.*?<.*?>)', r'```xml\n\1'),  
            (r'```\s*\n(.*?function.*?\()', r'```javascript\n\1'),
            (r'```\s*\n(.*?def .*?\()', r'```python\n\1'),
            (r'```\s*\n(.*?public class)', r'```java\n\1')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        return content
    
    def optimize_image_references(self, content: str, source_file: str) -> str:
        """优化图片引用，统一图片路径"""
        def normalize_image_path(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            if os.path.isabs(image_path):
                image_path = os.path.basename(image_path)
            
            image_path = image_path.replace('../', '').replace('./', '')
            
            if not image_path.startswith('images/'):
                if 'chapter' in image_path:
                    if not image_path.startswith('chapter'):
                        chapter_match = re.search(r'(chapter\d+)', source_file)
                        if chapter_match:
                            chapter_name = chapter_match.group(1)
                            image_path = f"images/{chapter_name}/{os.path.basename(image_path)}"
                        else:
                            image_path = f"images/{image_path}"
                    else:
                        image_path = f"images/{image_path}"
                else:
                    chapter_match = re.search(r'(chapter\d+)', source_file)
                    if chapter_match:
                        chapter_name = chapter_match.group(1)
                        image_path = f"images/{chapter_name}/{os.path.basename(image_path)}"
                    else:
                        image_path = f"images/{os.path.basename(image_path)}"
            
            return f"![{alt_text}]({image_path})"
        
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', normalize_image_path, content)
        return content
    
    def create_template_enhanced_main_latex_file(self, output_file: str, chapter_files: List[str]) -> bool:
        """创建基于模板的增强主LaTeX文件"""
        
        template_file = os.path.join(self.config['template_dir'], '基础配置模板.tex')
        
        if self.config['use_custom_template'] and os.path.exists(template_file):
            # 使用自定义模板
            print("使用自定义LaTeX模板...")
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 替换文档类为book，并调整配置
            template_content = re.sub(r'\\documentclass\[.*?\]\{ctexbook\}', 
                                    r'\\documentclass[12pt,a4paper,twoside,openright]{ctexbook}', 
                                    template_content)
            
            # 添加必要的包和命令定义
            additional_packages = r"""
% 额外必需包
\usepackage{calc}
\usepackage{pdfpages}

% Pandoc兼容性命令
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 防止过长行
\setlength{\emergencystretch}{3em}
\setcounter{secnumdepth}{5}
"""
            
            # 在文档开始前插入额外包
            template_content = template_content.replace(
                '% ========================================\n% 文档开始前的最后配置',
                additional_packages + '\n% ========================================\n% 文档开始前的最后配置'
            )
            
            # 移除模板中的使用说明注释（从% ========================================开始的最后部分）
            comment_start = template_content.rfind('% ========================================\n% 模板使用说明')
            if comment_start != -1:
                template_content = template_content[:comment_start]
            
            # 添加文档开始
            template_content += '\n% ========================================\n% 文档开始\n% ========================================\n\n\\begin{document}\n\n'
            
            # 添加目录
            template_content += '% 目录\n\\tableofcontents\n\\newpage\n\n'
            
        else:
            # 使用默认模板（原有逻辑的增强版）
            print("使用默认增强LaTeX模板...")
            template_content = self.create_default_enhanced_template()
        
        # 添加章节包含命令
        for chapter_file in chapter_files:
            template_content += f'\\input{{{chapter_file}}}\n'
        
        # 结束文档
        template_content += '\n\\end{document}\n'
        
        # 写入主文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return True
    
    def create_default_enhanced_template(self) -> str:
        """创建默认的增强模板"""
        return r"""% ========================================
% 智慧水利教材 - 增强版主文件
% ========================================

\documentclass[12pt,a4paper,twoside,openright]{ctexbook}

% ========================================
% 基础包引入
% ========================================

% 数学支持
\usepackage{amsmath,amssymb,amsthm}

% 图形和颜色
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning}

% 页面布局
\usepackage[
    top=2.5cm,
    bottom=2.5cm,
    left=2.8cm,
    right=2.2cm,
    bindingoffset=0.5cm,
    headheight=15pt,
    footskip=1.5cm
]{geometry}

% 字体和编码
\usepackage{fontspec}
\usepackage{setspace}
\onehalfspacing  % 1.5倍行距

% 中文字体配置
\setCJKmainfont{SimSun}[BoldFont=SimHei, ItalicFont=KaiTi]
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}

% 表格增强
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage{multirow}
\usepackage{multicol}
\usepackage{calc}

% 列表环境
\usepackage{enumitem}

% 代码环境
\usepackage{listings}

% 美化框架
\usepackage{tcolorbox}
\tcbuselibrary{most}

% 页眉页脚
\usepackage{fancyhdr}

% 超链接
\usepackage{hyperref}

% 图标字体
\usepackage{fontawesome5}

% ========================================
% 配色方案定义
% ========================================

% 主色调
\definecolor{primarycolor}{RGB}{52, 152, 219}      % 主蓝色
\definecolor{secondarycolor}{RGB}{230, 126, 34}    % 橙色
\definecolor{accentcolor}{RGB}{39, 174, 96}        % 绿色
\definecolor{warningcolor}{RGB}{241, 196, 15}      % 黄色
\definecolor{dangercolor}{RGB}{231, 76, 60}        % 红色

% 灰度系列
\definecolor{lightgray}{RGB}{248, 249, 250}
\definecolor{mediumgray}{RGB}{173, 181, 189}
\definecolor{darkgray}{RGB}{73, 80, 87}

% 代码配色
\definecolor{codeblue}{RGB}{40, 90, 200}
\definecolor{codegreen}{RGB}{0, 150, 0}
\definecolor{codered}{RGB}{200, 0, 0}
\definecolor{codegray}{RGB}{128, 128, 128}
\definecolor{backcolour}{RGB}{248, 248, 248}

% ========================================
% 页面样式配置
% ========================================

% 页眉页脚样式
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\leftmark}
\fancyhead[RO]{\rightmark}
\fancyfoot[LE,RO]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

% 章节样式
\ctexset{
    chapter={
        format={\centering\Huge\bfseries},
        name={第,章},
        number={\chinese{chapter}},
        beforeskip=20pt,
        afterskip=40pt
    },
    section={
        format={\Large\bfseries},
        beforeskip=20pt,
        afterskip=10pt
    },
    subsection={
        format={\large\bfseries},
        beforeskip=15pt,
        afterskip=8pt
    }
}

% ========================================
% 定理环境配置
% ========================================

% 定义定理样式
\theoremstyle{definition}
\newtheorem{definition}{定义}[chapter]
\newtheorem{theorem}{定理}[chapter]
\newtheorem{lemma}{引理}[chapter]
\newtheorem{example}{例}[chapter]
\newtheorem{exercise}{练习}[chapter]

% ========================================
% 列表样式配置
% ========================================

% 设置列表样式
\setlist[itemize,1]{label=\textbullet}
\setlist[itemize,2]{label=\textendash}
\setlist[itemize,3]{label=\textasteriskcentered}

\setlist[enumerate,1]{label=\arabic*.}
\setlist[enumerate,2]{label=(\alph*)}
\setlist[enumerate,3]{label=\roman*.}

% ========================================
% 自定义命令
% ========================================

% Pandoc兼容性命令
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 强调命令
\newcommand{\highlight}[1]{\textcolor{primarycolor}{\textbf{#1}}}
\newcommand{\important}[1]{\textcolor{dangercolor}{\textbf{#1}}}
\newcommand{\note}[1]{\textcolor{secondarycolor}{\textit{#1}}}

% 代码相关命令
\newcommand{\code}[1]{\texttt{#1}}
\newcommand{\file}[1]{\texttt{\textbf{#1}}}
\newcommand{\variable}[1]{\texttt{\textit{#1}}}

% 快捷符号
\providecommand{\checkmark}{\textcolor{accentcolor}{\faCheck}}
\newcommand{\crossmark}{\textcolor{dangercolor}{\faTimes}}
\newcommand{\infomark}{\textcolor{primarycolor}{\faInfoCircle}}
\newcommand{\warningmark}{\textcolor{warningcolor}{\faExclamationTriangle}}

% ========================================
% 特殊环境定义
% ========================================

% 学习目标
\newcommand{\learningobjectives}[1]{
    \begin{tcolorbox}[
        colback=primarycolor!10,
        colframe=primarycolor,
        title=\faLightbulb\ 学习目标,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% 关键概念
\newcommand{\keypoints}[1]{
    \begin{tcolorbox}[
        colback=secondarycolor!10,
        colframe=secondarycolor,
        title=\faKey\ 关键概念,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% 实践练习
\newcommand{\practiceexercise}[1]{
    \begin{tcolorbox}[
        colback=accentcolor!10,
        colframe=accentcolor,
        title=\faCogs\ 实践练习,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% 注意事项
\newcommand{\attention}[1]{
    \begin{tcolorbox}[
        colback=warningcolor!10,
        colframe=warningcolor,
        title=\faExclamationTriangle\ 注意,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% 章节摘要
\newcommand{\chaptersummary}[1]{
    \begin{tcolorbox}[
        colback=lightgray,
        colframe=primarycolor,
        title=本章要点,
        fonttitle=\bfseries,
        left=5pt,
        right=5pt,
        top=5pt,
        bottom=5pt
    ]
    #1
    \end{tcolorbox}
}

% ========================================
% 代码高亮配置
% ========================================

\lstset{
    backgroundcolor=\color{backcolour},
    commentstyle=\color{codegreen}\itshape,
    keywordstyle=\color{codeblue}\bfseries,
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codered},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,
    breaklines=true,
    captionpos=b,
    keepspaces=true,
    numbers=left,
    numbersep=8pt,
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    tabsize=4,
    frame=single,
    rulecolor=\color{mediumgray},
    framexleftmargin=8pt,
    framexrightmargin=8pt,
    framextopmargin=8pt,
    framexbottommargin=8pt,
    xleftmargin=15pt,
    xrightmargin=15pt
}

% 代码语言样式
\lstdefinestyle{csharp}{
    language=[Sharp]C,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

\lstdefinestyle{javascript}{
    language=JavaScript,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

\lstdefinestyle{python}{
    language=Python,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

\lstdefinestyle{java}{
    language=Java,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

\lstdefinestyle{sql}{
    language=SQL,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

\lstdefinestyle{terminal}{
    basicstyle=\ttfamily\footnotesize\color{white},
    backgroundcolor=\color{black},
    showstringspaces=false,
    numbers=none,
    frame=single
}

\lstdefinestyle{xml}{
    language=XML,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

\lstdefinestyle{css}{
    language=CSS,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

\lstdefinestyle{html}{
    language=HTML,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

\lstdefinestyle{json}{
    basicstyle=\ttfamily\footnotesize,
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered}
}

% ========================================
% 超链接配置
% ========================================

\hypersetup{
    colorlinks=true,
    linkcolor=primarycolor,
    filecolor=primarycolor,
    urlcolor=primarycolor,
    citecolor=primarycolor,
    bookmarksnumbered=true,
    bookmarksopen=true
}

% ========================================
% 文档配置
% ========================================

% 设置段落缩进
\setlength{\parindent}{2em}
\setlength{\parskip}{0.5ex plus 0.2ex minus 0.1ex}

% 防止过长行
\setlength{\emergencystretch}{3em}
\setcounter{secnumdepth}{5}

% 图表标题样式
\usepackage{caption}
\captionsetup{
    font=small,
    labelfont=bf,
    textfont=it,
    margin=10pt
}

% ========================================
% 文档开始
% ========================================

\begin{document}

% 目录
\tableofcontents
\newpage

"""
    
    def convert_to_latex(self, input_files: List[str], output_file: str) -> bool:
        """转换为LaTeX格式（模板增强版）"""
        print(f"开始转换为LaTeX（模板增强版）：{output_file}")
        
        if not self.available_tools['pandoc']:
            print("错误：Pandoc不可用，无法转换")
            return False
        
        # 按章节组织文件
        organized_files = self.organize_files_by_chapter(input_files)
        
        # 创建输出目录结构
        output_dir = os.path.dirname(output_file)
        latex_chapters_dir = os.path.join(output_dir, 'chapters')
        os.makedirs(latex_chapters_dir, exist_ok=True)
        
        # 转换每个章节
        chapter_tex_files = []
        
        # 处理前言和主要文件
        if 'main_files' in organized_files:
            main_tex_file = os.path.join(output_dir, 'main_content.tex')
            if self.convert_files_to_latex_content_only(organized_files['main_files'], main_tex_file):
                chapter_tex_files.append('main_content.tex')
        
        # 处理各章节
        for chapter_name, files in organized_files.items():
            if chapter_name == 'main_files':
                continue
                
            chapter_tex_file = os.path.join(latex_chapters_dir, f'{chapter_name}.tex')
            if self.convert_files_to_latex_content_only(files, chapter_tex_file):
                chapter_tex_files.append(f'chapters/{chapter_name}.tex')
        
        # 创建模板增强的主LaTeX文件
        success = self.create_template_enhanced_main_latex_file(output_file, chapter_tex_files)
        
        if success:
            print("✓ LaTeX模板增强版转换成功")
        
        return success
    
    def convert_files_to_latex_content_only(self, files: List[str], output_file: str) -> bool:
        """转换文件为纯LaTeX内容"""
        # 为中文支持添加特殊参数
        cmd = ['pandoc'] + files + ['-o', output_file]
        cmd.extend([
            '--from=markdown+east_asian_line_breaks+raw_html',  # 中文支持和原始 HTML
            '--to=latex',
            '--no-highlight',
            '--wrap=none',  # 不自动换行，避免破坏中文
            '--columns=1000',  # 设置很大的列数
            '--preserve-tabs',  # 保持制表符
            '--eol=lf'  # 使用Unix换行符
        ])
        
        try:
            # 设置环境变量支持中文
            env = os.environ.copy()
            env['LANG'] = 'C.UTF-8'  # 使用更通用的UTF-8设置
            env['LC_ALL'] = 'C.UTF-8'
            env['PYTHONIOENCODING'] = 'utf-8'
            
            print(f"  正在运行: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True, encoding='utf-8', env=env)
            print(f"✓ 转换文件成功: {os.path.basename(output_file)}")
            
            # 检查转换后的文件是否包含中文
            with open(output_file, 'r', encoding='utf-8') as f:
                latex_content = f.read()
            
            chinese_chars_in_latex = len([c for c in latex_content if '\u4e00' <= c <= '\u9fff'])
            print(f"  LaTeX输出中检测到 {chinese_chars_in_latex} 个中文字符")
            
            if chinese_chars_in_latex == 0:
                print(f"  警告：转换后的LaTeX文件不包含中文字符！")
                # 输出LaTeX文件的前100个字符用于调试
                print(f"  LaTeX内容预览: {latex_content[:200]}...")
            
            self.cleanup_latex_content_thoroughly(output_file)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 转换文件失败：{files[0]} - {e}")
            if e.stderr:
                print(f"  错误信息：{e.stderr}")
            if e.stdout:
                print(f"  标准输出：{e.stdout}")
            return False
    
    def cleanup_latex_content_thoroughly(self, latex_file: str):
        """彻底清理LaTeX文件"""
        with open(latex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        unwanted_patterns = [
            r'\\documentclass.*?\n',
            r'\\usepackage.*?\n',
            r'\\begin\{document\}.*?\n',
            r'\\end\{document\}.*?\n',
            r'\\title\{.*?\}',
            r'\\author\{.*?\}',
            r'\\date\{.*?\}',
            r'\\maketitle',
            r'\\PassOptionsToPackage.*?\n',
            r'\\providecommand.*?\n',
            r'\\newcommand.*?\n',
            r'\\definecolor.*?\n',
            r'\\setcounter.*?\n',
            r'\\setlength.*?\n',
            r'% Options for packages.*?\n'
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        content = re.sub(r'^\s*%.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = content.strip()
        
        if not content.strip():
            content = "% 此章节暂无内容\n"
        
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def organize_files_by_chapter(self, input_files: List[str]) -> dict:
        """按章节组织文件"""
        organized = {}
        main_files = []
        
        for file_path in input_files:
            filename = os.path.basename(file_path)
            
            if filename in ['index.md', '前言.md', 'README.md']:
                main_files.append(file_path)
            elif filename.startswith('chapter') and filename.endswith('.md'):
                chapter_num = re.search(r'chapter(\d+)', filename)
                if chapter_num:
                    chapter_key = f'chapter{chapter_num.group(1).zfill(2)}'
                    if chapter_key not in organized:
                        organized[chapter_key] = []
                    organized[chapter_key].append(file_path)
            elif filename.startswith('section') and filename.endswith('.md'):
                section_match = re.search(r'section(\d+)', filename)
                if section_match:
                    chapter_num = section_match.group(1)
                    chapter_key = f'chapter{chapter_num.zfill(2)}'
                    if chapter_key not in organized:
                        organized[chapter_key] = []
                    organized[chapter_key].append(file_path)
                else:
                    main_files.append(file_path)
            else:
                main_files.append(file_path)
        
        if main_files:
            organized['main_files'] = main_files
        
        for key, files in organized.items():
            organized[key] = sorted(files)
        
        print(f"文件组织结果：")
        for key, files in organized.items():
            print(f"  {key}: {len(files)} 个文件")
        
        return organized
    
    def postprocess_latex(self, latex_file: str) -> bool:
        """后处理LaTeX文件"""
        print("开始后处理LaTeX文件...")
        
        self.unified_image_management(latex_file)
        
        with open(latex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = self.fix_image_paths_unified(content)
        
        if self.config['postprocessing']['fix_document_structure']:
            content = self.fix_document_structure(content)
        
        if self.config['postprocessing']['apply_custom_environments']:
            content = self.apply_custom_environment_fixes(content)
        
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        output_dir = os.path.dirname(latex_file)
        self.postprocess_all_chapter_files(output_dir)
        
        # 复制代码高亮配置
        if self.config['postprocessing']['add_listings_config']:
            self.copy_listings_config(output_dir)
        
        print("✓ LaTeX后处理完成")
        return True
    
    def apply_custom_environment_fixes(self, content: str) -> str:
        """应用自定义环境修复"""
        # 修复可能的环境嵌套问题
        # 这里可以添加更多的环境修复逻辑
        return content
    
    def copy_listings_config(self, output_dir: str):
        """复制代码高亮配置"""
        config_file = os.path.join(self.config['template_dir'], '代码高亮配置.tex')
        if os.path.exists(config_file):
            dest_config = os.path.join(output_dir, 'listings-config.tex')
            shutil.copy2(config_file, dest_config)
            print(f"✓ 复制代码高亮配置到: {dest_config}")
    
    def unified_image_management(self, latex_file: str):
        """统一图片管理"""
        output_dir = os.path.dirname(latex_file)
        unified_images_dir = os.path.join(output_dir, 'images')
        
        os.makedirs(unified_images_dir, exist_ok=True)
        
        source_image_dirs = [
            os.path.join(self.source_dir, 'docs', 'chapters', 'images'),
            os.path.join(self.source_dir, 'docs', 'assets', 'images'),
            os.path.join(self.source_dir, 'chapters', 'images'),
            os.path.join(self.source_dir, 'images'),
            os.path.join(self.source_dir, 'assets', 'images')
        ]
        
        copied_count = 0
        for source_images_dir in source_image_dirs:
            if os.path.exists(source_images_dir):
                for root, dirs, files in os.walk(source_images_dir):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf')):
                            source_path = os.path.join(root, file)
                            rel_path = os.path.relpath(source_path, source_images_dir)
                            target_path = os.path.join(unified_images_dir, rel_path)
                            
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            if not os.path.exists(target_path) or \
                               os.path.getmtime(source_path) > os.path.getmtime(target_path):
                                shutil.copy2(source_path, target_path)
                                copied_count += 1
        
        print(f"✓ 统一图片管理完成，复制了 {copied_count} 个图片文件到: {unified_images_dir}")
    
    def fix_image_paths_unified(self, content: str) -> str:
        """修复图片路径为统一路径"""
        patterns = [
            (r'\\includegraphics\{[^}]*?/images/([^}]+)\}', r'\\includegraphics{images/\1}'),
            (r'\\includegraphics\{images/\.\./images/([^}]+)\}', r'\\includegraphics{images/\1}'),
            (r'\\includegraphics\{chapters/images/([^}]+)\}', r'\\includegraphics{images/\1}'),
            (r'\\includegraphics\{docs/chapters/images/([^}]+)\}', r'\\includegraphics{images/\1}'),
            (r'\\includegraphics\{[^}]*?docs/assets/images/([^}]+)\}', r'\\includegraphics{images/\1}')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_document_structure(self, content: str) -> str:
        """修复文档结构问题"""
        seen_packages = set()
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.startswith('\\usepackage'):
                package_match = re.search(r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}', line)
                if package_match:
                    package_name = package_match.group(1)
                    if package_name not in seen_packages:
                        seen_packages.add(package_name)
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def postprocess_all_chapter_files(self, output_dir: str):
        """后处理所有章节文件"""
        chapters_dir = os.path.join(output_dir, 'chapters')
        if os.path.exists(chapters_dir):
            for chapter_file in os.listdir(chapters_dir):
                if chapter_file.endswith('.tex'):
                    chapter_path = os.path.join(chapters_dir, chapter_file)
                    self.postprocess_chapter_file_unified(chapter_path)
        
        main_content_file = os.path.join(output_dir, 'main_content.tex')
        if os.path.exists(main_content_file):
            self.postprocess_chapter_file_unified(main_content_file)
    
    def postprocess_chapter_file_unified(self, chapter_file: str):
        """后处理单个章节文件"""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = self.fix_image_paths_unified(content)
        content = self.fix_table_issues(content)
        content = self.fix_latex_syntax_issues(content)
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def fix_table_issues(self, content: str) -> str:
        """修复表格相关问题"""
        content = re.sub(r'\\real\{([0-9.]+)\}', r'\1', content)
        
        content = re.sub(
            r'>\\{raggedright\\arraybackslash\\}p\\{\\(\\columnwidth - 4\\tabcolsep\\) \\* ([0-9.]+)\\}',
            r'>{\raggedright\\arraybackslash}p{(\\columnwidth - 4\\tabcolsep) * \1}',
            content
        )
        
        return content
    
    def fix_latex_syntax_issues(self, content: str) -> str:
        """修复其他LaTeX语法问题"""
        content = re.sub(r'\\textbackslash\\{', r'\\{', content)
        content = re.sub(r'\\}', r'}', content)
        
        return content
    
    def compile_pdf(self, latex_file: str) -> bool:
        """编译PDF"""
        print(f"开始编译PDF：{latex_file}")
        
        available_engine = None
        for engine in ['xelatex', 'lualatex', 'pdflatex']:
            if self.available_tools.get(engine, False):
                available_engine = engine
                break
        
        if not available_engine:
            print("错误：未找到可用的LaTeX引擎")
            return False
        
        print(f"使用 {available_engine} 编译...")
        
        original_dir = os.getcwd()
        latex_dir = os.path.dirname(os.path.abspath(latex_file))
        latex_name = os.path.basename(latex_file)
        
        try:
            os.chdir(latex_dir)
            
            for i in range(3):
                print(f"第 {i+1} 次编译...")
                result = subprocess.run([
                    available_engine,
                    '-interaction=nonstopmode',
                    '-output-directory=.',
                    latex_name
                ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                pdf_file = latex_name.replace('.tex', '.pdf')
                if os.path.exists(pdf_file):
                    if i == 2:
                        print("✓ PDF编译成功")
                        return True
                    continue
                
                if result.returncode != 0:
                    print(f"编译失败，显示关键错误：")
                    log_file = latex_name.replace('.tex', '.log')
                    if os.path.exists(log_file):
                        self.show_compilation_errors(log_file)
                    return False
            
            return False
            
        finally:
            os.chdir(original_dir)
    
    def show_compilation_errors(self, log_file: str):
        """显示编译错误信息"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            
            error_patterns = [
                r'! (.+)',
                r'(.+Error.+)',
                r'(.+not found.+)',
                r'(.+Undefined.+)',
                r'(.+Missing.+)'
            ]
            
            lines = log_content.split('\n')
            for line_num, line in enumerate(lines):
                for pattern in error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        print(f"  行 {line_num+1}: {line.strip()}")
                        if line_num + 1 < len(lines):
                            print(f"         {lines[line_num+1].strip()}")
                        break
        except Exception as e:
            print(f"无法读取日志文件: {e}")
    
    def convert(self, source_dir: str, output_format: str = None) -> bool:
        """主转换函数"""
        if output_format:
            self.config['output_format'] = output_format
        
        self.source_dir = os.path.abspath(source_dir)
        
        print(f"开始教材转换流程 (模板增强版)...")
        print(f"源目录：{source_dir}")
        print(f"输出格式：{self.config['output_format']}")
        print(f"使用自定义模板：{'是' if self.config['use_custom_template'] else '否'}")
        print(f"应用样式增强：{'是' if self.config['apply_style_enhancements'] else '否'}")
        
        output_dir = self.config['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        if not self.config['chapters']:
            self.config['chapters'] = self.discover_chapters(source_dir)
        
        if not self.config['chapters']:
            print("错误：未找到任何章节文件")
            return False
        
        print(f"发现 {len(self.config['chapters'])} 个章节文件")
        
        temp_dir = os.path.join(output_dir, 'temp')
        processed_files = self.preprocess_markdown(self.config['chapters'], temp_dir)
        
        success = False
        
        if self.config['output_format'] in ['latex', 'pdf']:
            latex_file = os.path.join(output_dir, '教材.tex')
            success = self.convert_to_latex(processed_files, latex_file)
            
            if success:
                success = self.postprocess_latex(latex_file)
                
                if success and self.config['output_format'] == 'pdf':
                    success = self.compile_pdf(latex_file)
        
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        if success:
            print(f"\n✓ 转换完成！输出文件在：{output_dir}")
            print("模板增强功能:")
            if self.config['use_custom_template']:
                print("  ✓ 使用了自定义LaTeX模板")
            if self.config['apply_style_enhancements']:
                print("  ✓ 应用了样式增强功能")
                print("  ✓ 自动识别学习目标、关键概念等环境")
                print("  ✓ 转换emoji为LaTeX图标")
                print("  ✓ 增强代码块高亮")
            print("  ✓ 统一了图片路径管理")
            print("  ✓ 修复了文档结构问题")
        else:
            print(f"\n✗ 转换失败")
        
        return success


def main():
    parser = argparse.ArgumentParser(description='模板增强版教材转换工具')
    parser.add_argument('source_dir', help='源文件目录')
    parser.add_argument('-f', '--format', choices=['latex', 'pdf', 'docx'], 
                       default='pdf', help='输出格式')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('--no-template', action='store_true', help='不使用自定义模板')
    parser.add_argument('--no-enhancement', action='store_true', help='不应用样式增强')
    
    args = parser.parse_args()
    
    converter = TemplateEnhancedConverter(args.config)
    
    if args.output:
        converter.config['output_dir'] = args.output
    
    if args.no_template:
        converter.config['use_custom_template'] = False
    
    if args.no_enhancement:
        converter.config['apply_style_enhancements'] = False
    
    success = converter.convert(args.source_dir, args.format)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()