"""
智慧水利教材转换器 - 核心处理器模块
软件工程设计：单一职责原则
"""

import re
import logging
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
    """处理器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def process(self, content: str) -> str:
        """处理内容的抽象方法"""
        pass
    
    def log_processing(self, action: str, count: int = 0):
        """记录处理日志"""
        if count > 0:
            self.logger.info(f"{action}: {count} 项")
        else:
            self.logger.info(f"{action}")

class ChapterNumberProcessor(BaseProcessor):
    """章节编号处理器"""
    
    def __init__(self):
        super().__init__("ChapterNumber")
    
    def process(self, content: str) -> str:
        """处理章节编号"""
        self.log_processing("开始处理章节编号")
        
        # 确保章节标题格式正确
        chapter_pattern = r'^# (第[一二三四五六七八九十]+章.*?)$'
        matches = re.findall(chapter_pattern, content, re.MULTILINE)
        
        if matches:
            self.log_processing("找到章节标题", len(matches))
            # 章节标题保持一级标题
            for match in matches:
                old_pattern = f'# {re.escape(match)}'
                new_pattern = f'\\\\chapter{{{match}}}'
                content = re.sub(old_pattern, new_pattern, content)
        
        # 处理小节标题
        section_count = 0
        content = re.sub(r'^## (.*?)$', lambda m: (
            self._increment_section_count() or f'\\\\section{{{m.group(1)}}}'
        ), content, flags=re.MULTILINE)
        
        self.log_processing("处理完成", section_count)
        return content
    
    def _increment_section_count(self):
        """增加小节计数（用于日志）"""
        if not hasattr(self, '_section_count'):
            self._section_count = 0
        self._section_count += 1
        return None

class MathProcessor(BaseProcessor):
    """数学公式处理器"""
    
    def __init__(self):
        super().__init__("Math")
    
    def process(self, content: str) -> str:
        """处理数学公式"""
        self.log_processing("开始处理数学公式")
        
        # 处理行内公式
        inline_count = len(re.findall(r'\$[^$]+\$', content))
        if inline_count > 0:
            # 行内公式保持不变，LaTeX原生支持
            self.log_processing("行内公式", inline_count)
        
        # 处理块级公式
        block_pattern = r'\$\$([^$]+?)\$\$'
        block_matches = re.findall(block_pattern, content, re.DOTALL)
        
        if block_matches:
            self.log_processing("块级公式", len(block_matches))
            for i, formula in enumerate(block_matches):
                # 使用equation环境替换$$
                equation_env = f'\\\\begin{{equation}}\\\\n{formula.strip()}\\\\n\\\\end{{equation}}'
                content = content.replace(f'$${formula}$$', equation_env, 1)
        
        # 移除有问题的LaTeX命令（如果有的话）
        problematic_patterns = [
            (r'\\sqrt\s+\{', r'\\sqrt{'),  # 修复sqrt空格问题
            (r'\\frac\s+\{', r'\\frac{'),  # 修复frac空格问题
        ]
        
        fix_count = 0
        for pattern, replacement in problematic_patterns:
            before_count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            after_count = len(re.findall(pattern, content))
            fix_count += (before_count - after_count)
        
        if fix_count > 0:
            self.log_processing("修复数学公式语法", fix_count)
        
        self.log_processing("数学公式处理完成")
        return content

class FigureProcessor(BaseProcessor):
    """图片处理器"""
    
    def __init__(self):
        super().__init__("Figure")
    
    def process(self, content: str) -> str:
        """处理图片"""
        self.log_processing("开始处理图片")
        
        # 匹配markdown图片语法
        figure_pattern = r'!\[([^\]]*?)\]\(([^)]+?)\)'
        figures = re.findall(figure_pattern, content)
        
        if figures:
            self.log_processing("找到图片", len(figures))
            
            for alt_text, image_path in figures:
                # 清理图片路径
                clean_path = image_path.replace('../docs/chapters/', '').replace('docs/chapters/', '')
                
                # 生成LaTeX图片环境
                latex_figure = f'''\\\\begin{{figure}}[htbp]
\\\\centering
\\\\includegraphics[width=0.8\\\\textwidth]{{{clean_path}}}
\\\\caption{{{alt_text if alt_text else "图片"}}}
\\\\end{{figure}}'''
                
                # 替换原markdown语法
                old_syntax = f'![{alt_text}]({image_path})'
                content = content.replace(old_syntax, latex_figure)
        
        self.log_processing("图片处理完成")
        return content

class CodeProcessor(BaseProcessor):
    """代码处理器"""
    
    def __init__(self):
        super().__init__("Code")
    
    def process(self, content: str) -> str:
        """处理代码"""
        self.log_processing("开始处理代码")
        
        # 处理代码块
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        code_blocks = re.findall(code_block_pattern, content, re.DOTALL)
        
        if code_blocks:
            self.log_processing("找到代码块", len(code_blocks))
            
            for language, code_content in code_blocks:
                # 使用listings环境
                if language:
                    latex_code = f'''\\\\begin{{lstlisting}}[language={language.title()}]
{code_content.strip()}
\\\\end{{lstlisting}}'''
                else:
                    latex_code = f'''\\\\begin{{lstlisting}}
{code_content.strip()}
\\\\end{{lstlisting}}'''
                
                # 替换原语法
                if language:
                    old_syntax = f'```{language}\n{code_content}\n```'
                else:
                    old_syntax = f'```\n{code_content}\n```'
                content = content.replace(old_syntax, latex_code)
        
        # 处理行内代码
        inline_code_pattern = r'`([^`]+)`'
        inline_codes = re.findall(inline_code_pattern, content)
        
        if inline_codes:
            self.log_processing("行内代码", len(inline_codes))
            content = re.sub(inline_code_pattern, r'\\\\texttt{\1}', content)
        
        self.log_processing("代码处理完成")
        return content

class AdmonitionProcessor(BaseProcessor):
    """告警框处理器"""
    
    def __init__(self):
        super().__init__("Admonition")
    
    def process(self, content: str) -> str:
        """处理告警框"""
        self.log_processing("开始处理告警框")
        
        # 匹配!!! 语法
        admonition_pattern = r'!!! (\w+)(.*?)\n\n(.*?)(?=\n\n|\n!!! |\Z)'
        admonitions = re.findall(admonition_pattern, content, re.DOTALL)
        
        if admonitions:
            self.log_processing("找到告警框", len(admonitions))
            
            for admon_type, title, admon_content in admonitions:
                # 根据类型选择颜色和图标
                color_map = {
                    'note': 'blue',
                    'tip': 'green', 
                    'warning': 'orange',
                    'danger': 'red',
                    'info': 'cyan'
                }
                
                color = color_map.get(admon_type.lower(), 'gray')
                
                # 清理title中的特殊字符
                clean_title = title.replace('"', '').replace("'", "").strip()
                if clean_title and not clean_title.startswith(' '):
                    clean_title = ' ' + clean_title
                
                # 生成tcolorbox环境
                latex_admon = f'''\\\\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={admon_type.title()}{clean_title}]
{admon_content.strip()}
\\\\end{{tcolorbox}}'''
                
                # 替换原语法
                old_syntax = f'!!! {admon_type}{title}\n\n{admon_content}'
                content = content.replace(old_syntax, latex_admon)
        
        self.log_processing("告警框处理完成")
        return content

class YamlProtectionProcessor(BaseProcessor):
    """YAML保护处理器 - 将裸露的YAML内容包装在代码块中"""
    
    def __init__(self):
        super().__init__("YamlProtection")
    
    def process(self, content: str) -> str:
        """处理裸露的YAML内容"""
        self.log_processing("开始保护YAML内容")
        
        yaml_fixes = 0
        
        # 简单粗暴地替换所有裸露的 --- 为安全的格式
        lines = content.split('\n')
        protected_lines = []
        in_code_block = False
        
        for line in lines:
            # 检查是否在代码块内
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                protected_lines.append(line)
                continue
            
            # 如果发现裸露的YAML分隔符，替换为注释格式
            if line.strip() == '---' and not in_code_block:
                protected_lines.append('<!-- YAML separator -->')
                yaml_fixes += 1
            else:
                protected_lines.append(line)
        
        if yaml_fixes > 0:
            self.log_processing("保护YAML分隔符", yaml_fixes)
        
        self.log_processing("YAML保护完成")
        return '\n'.join(protected_lines)
    
    def _looks_like_yaml_context(self, lines: list, index: int) -> bool:
        """检查周围是否像YAML内容"""
        # 检查前后几行是否有YAML特征
        start = max(0, index - 3)
        end = min(len(lines), index + 4)
        
        for i in range(start, end):
            if i != index and ':' in lines[i] and not lines[i].strip().startswith('#'):
                # 有key:value格式，可能是YAML
                return True
        return False

class ContentProcessor:
    """内容处理器管理类"""
    
    def __init__(self):
        self.processors: List[BaseProcessor] = [
            YamlProtectionProcessor(),  # 首先保护YAML内容
            ChapterNumberProcessor(),
            MathProcessor(), 
            FigureProcessor(),
            CodeProcessor(),
            AdmonitionProcessor()
        ]
        self.logger = logging.getLogger(__name__)
    
    def process_all(self, content: str) -> str:
        """执行所有处理器"""
        self.logger.info("开始内容处理流水线")
        
        for processor in self.processors:
            self.logger.info(f"执行处理器: {processor.name}")
            content = processor.process(content)
        
        self.logger.info("内容处理流水线完成")
        return content