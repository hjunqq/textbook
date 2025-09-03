"""
智慧水利教材转换器 - 修复后的核心处理器模块
软件工程设计：单一职责原则 + 修复过度转义问题
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
    """章节编号处理器 - 修复版：不做LaTeX转换，保持markdown格式"""
    
    def __init__(self):
        super().__init__("ChapterNumber")
    
    def process(self, content: str) -> str:
        """处理章节编号 - 保持markdown格式，让Pandoc处理"""
        self.log_processing("开始处理章节编号")
        
        # 确保章节标题格式正确 - 保持markdown格式
        chapter_pattern = r'^# (第[一二三四五六七八九十]+章.*?)$'
        matches = re.findall(chapter_pattern, content, re.MULTILINE)
        
        if matches:
            self.log_processing("找到章节标题", len(matches))
            # 章节标题保持一级标题格式，让Pandoc处理
            for match in matches:
                # 确保标题格式规范
                old_pattern = f'# {re.escape(match)}'
                new_pattern = f'# {match}'  # 保持原格式
                content = re.sub(old_pattern, new_pattern, content)
        
        # 小节标题也保持markdown格式
        section_count = len(re.findall(r'^## ', content, re.MULTILINE))
        self.log_processing("小节标题", section_count)
        
        self.log_processing("处理完成")
        return content

class MathProcessor(BaseProcessor):
    """数学公式处理器 - 修复版：保持markdown格式"""
    
    def __init__(self):
        super().__init__("Math")
    
    def process(self, content: str) -> str:
        """处理数学公式 - 保持markdown格式，让Pandoc处理"""
        self.log_processing("开始处理数学公式")
        
        # 处理行内公式 - 保持$格式
        inline_count = len(re.findall(r'\$[^$]+\$', content))
        if inline_count > 0:
            self.log_processing("行内公式", inline_count)
        
        # 处理块级公式 - 保持$$格式  
        block_pattern = r'\$\$([^$]+?)\$\$'
        block_matches = re.findall(block_pattern, content, re.DOTALL)
        if block_matches:
            self.log_processing("块级公式", len(block_matches))
        
        self.log_processing("数学公式处理完成")
        return content

class FigureProcessor(BaseProcessor):
    """图片处理器 - 修复版：保持markdown格式"""
    
    def __init__(self):
        super().__init__("Figure")
    
    def process(self, content: str) -> str:
        """处理图片 - 保持markdown格式，让Pandoc处理"""
        self.log_processing("开始处理图片")
        
        # 匹配markdown图片语法
        figure_pattern = r'!\[([^\]]*?)\]\(([^)]+?)\)'
        figures = re.findall(figure_pattern, content)
        
        if figures:
            self.log_processing("找到图片", len(figures))
            
            for alt_text, image_path in figures:
                # 仅清理图片路径，保持markdown格式
                clean_path = image_path.replace('../docs/chapters/', '').replace('docs/chapters/', '')
                
                # 替换为清理后的markdown格式
                old_syntax = f'![{alt_text}]({image_path})'
                new_syntax = f'![{alt_text}]({clean_path})'
                content = content.replace(old_syntax, new_syntax)
        
        self.log_processing("图片处理完成")
        return content

class CodeProcessor(BaseProcessor):
    """代码处理器 - 修复版：保持markdown格式"""
    
    def __init__(self):
        super().__init__("Code")
    
    def process(self, content: str) -> str:
        """处理代码 - 保持markdown格式，让Pandoc处理"""
        self.log_processing("开始处理代码")
        
        # 统计代码块但不转换
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        code_blocks = re.findall(code_block_pattern, content, re.DOTALL)
        
        if code_blocks:
            self.log_processing("找到代码块", len(code_blocks))
        
        # 统计行内代码但不转换
        inline_code_pattern = r'`([^`]+)`'
        inline_codes = re.findall(inline_code_pattern, content)
        
        if inline_codes:
            self.log_processing("行内代码", len(inline_codes))
        
        self.log_processing("代码处理完成")
        return content

class AdmonitionProcessor(BaseProcessor):
    """告警框处理器 - 修复版：生成正确的LaTeX语法"""
    
    def __init__(self):
        super().__init__("Admonition")
    
    def process(self, content: str) -> str:
        """处理告警框 - 转换为正确的LaTeX tcolorbox语法"""
        self.log_processing("开始处理告警框")
        
        # 匹配!!! 语法 - 改进的正则表达式
        admonition_pattern = r'!!! (\w+)(.*?)\n\n(.*?)(?=\n\n!!! |\n[#]{1,6} |\Z)'
        admonitions = re.findall(admonition_pattern, content, re.DOTALL)
        
        if admonitions:
            self.log_processing("找到告警框", len(admonitions))
            
            for admon_type, title, admon_content in admonitions:
                # 根据类型选择颜色
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
                
                # 生成正确的tcolorbox环境 - 修复语法错误
                if clean_title:
                    latex_admon = f'''\\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={admon_type.title()}: {clean_title}]
{admon_content.strip()}
\\end{{tcolorbox}}'''
                else:
                    latex_admon = f'''\\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={admon_type.title()}]
{admon_content.strip()}
\\end{{tcolorbox}}'''
                
                # 替换原语法
                old_syntax = f'!!! {admon_type}{title}\n\n{admon_content}'
                content = content.replace(old_syntax, latex_admon)
        
        self.log_processing("告警框处理完成")
        return content

class YamlProtectionProcessor(BaseProcessor):
    """YAML保护处理器 - 修复版"""
    
    def __init__(self):
        super().__init__("YamlProtection")
    
    def process(self, content: str) -> str:
        """处理裸露的YAML内容"""
        self.log_processing("开始保护YAML内容")
        
        yaml_fixes = 0
        
        # 移除文件开头的YAML front matter
        if content.startswith('---'):
            # 找到第二个---的位置
            second_yaml = content.find('---', 3)
            if second_yaml != -1:
                content = content[second_yaml + 3:].lstrip('\n')
                yaml_fixes += 1
                self.log_processing("移除YAML front matter", 1)
        
        # 处理其他裸露的---分隔符
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
                protected_lines.append('% YAML separator removed')
                yaml_fixes += 1
            else:
                protected_lines.append(line)
        
        if yaml_fixes > 0:
            self.log_processing("保护YAML分隔符", yaml_fixes)
        
        self.log_processing("YAML保护完成")
        return '\n'.join(protected_lines)

class LatexEscapeFixProcessor(BaseProcessor):
    """LaTeX转义修复处理器 - 新增：修复过度转义问题"""
    
    def __init__(self):
        super().__init__("LatexEscapeFix")
    
    def process(self, content: str) -> str:
        """修复过度转义的LaTeX命令"""
        self.log_processing("开始修复LaTeX过度转义")
        
        fixes_count = 0
        
        # 修复过度转义的LaTeX命令
        escape_fixes = [
            # 修复 \textbackslash section{} 为正确的 \section{}
            (r'\\textbackslash section\\{([^}]+)\\}', r'\\section{\1}'),
            (r'\\textbackslash chapter\\{([^}]+)\\}', r'\\chapter{\1}'),
            (r'\\textbackslash subsection\\{([^}]+)\\}', r'\\subsection{\1}'),
            
            # 修复 tcolorbox 语法错误
            (r'\\textbackslash begin\\{tcolorbox\\}\\{\\[\\]([^}]+)\\{\\]\\}', r'\\begin{tcolorbox}[\1]'),
            (r'\\textbackslash end\\{tcolorbox\\}', r'\\end{tcolorbox}'),
            
            # 修复其他常见的过度转义
            (r'\\textbackslash begin\\{([^}]+)\\}', r'\\begin{\1}'),
            (r'\\textbackslash end\\{([^}]+)\\}', r'\\end{\1}'),
        ]
        
        for pattern, replacement in escape_fixes:
            before_count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            after_count = len(re.findall(pattern, content))
            fix_count = before_count - after_count
            fixes_count += fix_count
            if fix_count > 0:
                self.log_processing(f"修复模式 {pattern[:30]}...", fix_count)
        
        self.log_processing("LaTeX转义修复完成", fixes_count)
        return content

class ContentProcessor:
    """内容处理器管理类 - 修复版"""
    
    def __init__(self):
        # 重新设计处理器流水线，避免过度转换
        self.processors: List[BaseProcessor] = [
            YamlProtectionProcessor(),    # 首先保护YAML内容
            AdmonitionProcessor(),        # 只处理告警框（转换为LaTeX）
            ChapterNumberProcessor(),     # 保持markdown格式
            MathProcessor(),              # 保持markdown格式
            FigureProcessor(),            # 保持markdown格式
            CodeProcessor(),              # 保持markdown格式
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

class PostLaTeXProcessor:
    """LaTeX后处理器 - 新增：处理Pandoc生成后的tex文件"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def post_process_tex(self, latex_content: str) -> str:
        """处理Pandoc生成的LaTeX文件，修复各种问题"""
        self.logger.info("开始LaTeX后处理")
        
        # 创建转义修复处理器
        escape_fixer = LatexEscapeFixProcessor()
        latex_content = escape_fixer.process(latex_content)
        
        # 其他LaTeX语法修复
        fixes = [
            # 修复tcolorbox语法问题
            (r'\\begin\{tcolorbox\}\{([^}]+)\}', r'\\begin{tcolorbox}[\1]'),
            
            # 修复章节标题后的换行
            (r'\\chapter\{([^}]+)\}\s*\n', r'\\chapter{\1}\n\n'),
            (r'\\section\{([^}]+)\}\s*\n', r'\\section{\1}\n\n'),
            
            # 修复列表环境
            (r'\n\\begin\{', r'\n\n\\begin{'),
            (r'\\end\{([^}]+)\}\n', r'\\end{\1}\n\n'),
            
            # 清理多余的空行
            (r'\n\s*\n\s*\n', r'\n\n'),
            
            # 修复特殊字符转义问题
            (r'\\#\\#\\#', r'###'),
            (r"''", r'``'),
        ]
        
        total_fixes = 0
        for pattern, replacement in fixes:
            before_count = len(re.findall(pattern, latex_content))
            latex_content = re.sub(pattern, replacement, latex_content)
            after_count = len(re.findall(pattern, latex_content))
            fix_count = before_count - after_count
            total_fixes += fix_count
        
        self.logger.info(f"LaTeX后处理完成，总共修复 {total_fixes} 个问题")
        return latex_content