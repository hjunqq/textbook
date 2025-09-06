"""
内容处理器模块
提供Markdown内容到LaTeX的转换处理
"""

import re
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..utils.logger import Logger

class IContentProcessor(ABC):
    """内容处理器接口"""
    
    @abstractmethod
    def process(self, content: str, context: Dict[str, Any] = None) -> str:
        """处理内容"""
        pass
    
    @abstractmethod
    def supports(self, content_type: str) -> bool:
        """是否支持该内容类型"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """获取处理优先级（数值越小优先级越高）"""
        pass

class BaseProcessor(IContentProcessor):
    """处理器基类"""
    
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority
        self.logger = Logger(f"Processor.{name}")
    
    def get_priority(self) -> int:
        return self.priority
    
    def log_processing(self, action: str, count: int = 0):
        """记录处理日志"""
        if count > 0:
            self.logger.info(f"{action}: {count} 项")
        else:
            self.logger.info(f"{action}")

class ChapterNumberProcessor(BaseProcessor):
    """章节编号处理器"""
    
    def __init__(self):
        super().__init__("ChapterNumber", priority=10)
    
    def supports(self, content_type: str) -> bool:
        return content_type in ["chapter", "all"]
    
    def process(self, content: str, context: Dict[str, Any] = None) -> str:
        """处理章节编号"""
        self.log_processing("开始处理章节编号")
        
        # 处理主标题 - 转换为LaTeX章节
        chapter_pattern = r'^# (第[一二三四五六七八九十]+章.*?)$'
        matches = re.findall(chapter_pattern, content, re.MULTILINE)
        
        if matches:
            self.log_processing("找到章节标题", len(matches))
            # 将Markdown一级标题转换为LaTeX章节
            content = re.sub(chapter_pattern, r'\\chapter{\1}', content, flags=re.MULTILINE)
        
        # 处理子标题层级
        # 二级标题 -> section
        content = re.sub(r'^## (.*?)$', r'\\section{\1}', content, flags=re.MULTILINE)
        
        # 三级标题 -> subsection  
        content = re.sub(r'^### (.*?)$', r'\\subsection{\1}', content, flags=re.MULTILINE)
        
        # 四级标题 -> subsubsection
        content = re.sub(r'^#### (.*?)$', r'\\subsubsection{\1}', content, flags=re.MULTILINE)
        
        return content

class MathProcessor(BaseProcessor):
    """数学公式处理器"""
    
    def __init__(self):
        super().__init__("Math", priority=20)
    
    def supports(self, content_type: str) -> bool:
        return content_type in ["math", "all"]
    
    def process(self, content: str, context: Dict[str, Any] = None) -> str:
        """处理数学公式"""
        self.log_processing("开始处理数学公式")
        
        # 处理独立数学公式 ($$...$$)
        display_math_count = 0
        def replace_display_math(match):
            nonlocal display_math_count
            display_math_count += 1
            formula = match.group(1).strip()
            return f"\\begin{{equation}}\n{formula}\n\\end{{equation}}"
        
        content = re.sub(r'\$\$(.*?)\$\$', replace_display_math, content, flags=re.DOTALL)
        
        if display_math_count > 0:
            self.log_processing("处理独立数学公式", display_math_count)
        
        # 行内数学公式保持不变 ($...$)
        inline_math_count = len(re.findall(r'(?<!\\)\$[^$]+\$', content))
        if inline_math_count > 0:
            self.log_processing("发现行内数学公式", inline_math_count)
        
        return content

class CodeBlockProcessor(BaseProcessor):
    """代码块处理器"""
    
    def __init__(self):
        super().__init__("CodeBlock", priority=30)
        
        # 支持的语言映射
        self.language_mapping = {
            'python': 'Python',
            'java': 'Java', 
            'javascript': 'JavaScript',
            'js': 'JavaScript',
            'sql': 'SQL',
            'bash': 'bash',
            'shell': 'bash',
            'html': 'HTML',
            'css': 'HTML',
            'xml': 'XML',
            'json': 'Python',  # JSON使用Python高亮
            'yaml': 'Python',  # YAML使用Python高亮
            'yml': 'Python'
        }
    
    def supports(self, content_type: str) -> bool:
        return content_type in ["code", "all"]
    
    def process(self, content: str, context: Dict[str, Any] = None) -> str:
        """处理代码块"""
        self.log_processing("开始处理代码块")
        
        code_block_count = 0
        
        def replace_code_block(match):
            nonlocal code_block_count
            code_block_count += 1
            
            language = match.group(1).lower() if match.group(1) else 'text'
            code_content = match.group(2).strip()
            
            # 映射语言名称
            latex_language = self.language_mapping.get(language, language)
            
            # 生成LaTeX代码块
            latex_code = f"""\\begin{{lstlisting}}[language={latex_language}]
{code_content}
\\end{{lstlisting}}"""
            
            return latex_code
        
        # 处理带语言标识的代码块
        content = re.sub(r'```([a-zA-Z0-9]*)\n(.*?)```', replace_code_block, content, flags=re.DOTALL)
        
        if code_block_count > 0:
            self.log_processing("处理代码块", code_block_count)
        
        return content

class ImageProcessor(BaseProcessor):
    """图片处理器"""
    
    def __init__(self):
        super().__init__("Image", priority=40)
    
    def supports(self, content_type: str) -> bool:
        return content_type in ["image", "all"]
    
    def process(self, content: str, context: Dict[str, Any] = None) -> str:
        """处理图片"""
        self.log_processing("开始处理图片")
        
        image_count = 0
        
        def replace_image(match):
            nonlocal image_count
            image_count += 1
            
            alt_text = match.group(1) or f"图片{image_count}"
            image_path = match.group(2)
            
            # 处理图片路径 - 确保使用相对路径
            if image_path.startswith('../'):
                image_path = image_path[3:]  # 移除 ../
            
            # 生成LaTeX图片环境
            latex_figure = f"""\\begin{{figure}}[h]
\\centering
\\includegraphics[width=0.8\\textwidth]{{{image_path}}}
\\caption{{{alt_text}}}
\\end{{figure}}"""
            
            return latex_figure
        
        # 处理Markdown图片语法
        content = re.sub(r'!\\[(.*?)\\]\\((.*?)\\)', replace_image, content)
        
        if image_count > 0:
            self.log_processing("处理图片", image_count)
        
        return content

class AdmonitionProcessor(BaseProcessor):
    """告警框处理器"""
    
    def __init__(self):
        super().__init__("Admonition", priority=50)
        
        # 告警框类型映射
        self.admonition_mapping = {
            'note': ('注意', 'blue'),
            'tip': ('提示', 'green'),
            'warning': ('警告', 'orange'),
            'danger': ('危险', 'red'),
            'info': ('信息', 'cyan'),
            'example': ('示例', 'purple')
        }
    
    def supports(self, content_type: str) -> bool:
        return content_type in ["admonition", "all"]
    
    def process(self, content: str, context: Dict[str, Any] = None) -> str:
        """处理告警框"""
        self.log_processing("开始处理告警框")
        
        admonition_count = 0
        
        def replace_admonition(match):
            nonlocal admonition_count
            admonition_count += 1
            
            admonition_type = match.group(1).lower()
            title = match.group(2) if match.group(2) else None
            content_text = match.group(3).strip()
            
            # 获取告警框配置
            if admonition_type in self.admonition_mapping:
                default_title, color = self.admonition_mapping[admonition_type]
                display_title = title or default_title
            else:
                display_title = title or "提示"
                color = "gray"
            
            # 生成LaTeX告警框
            latex_admonition = f"""\\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={display_title}]
{content_text}
\\end{{tcolorbox}}"""
            
            return latex_admonition
        
        # 处理MkDocs风格的告警框
        # 匹配模式：!!! type "title"\\n内容
        admonition_pattern = r'!!! (\\w+)(?: \"([^\"]+)\")?\\n([\\s\\S]*?)(?=\\n\\n|\\n!|$)'
        content = re.sub(admonition_pattern, replace_admonition, content)
        
        if admonition_count > 0:
            self.log_processing("处理告警框", admonition_count)
        
        return content

class TableProcessor(BaseProcessor):
    """表格处理器"""
    
    def __init__(self):
        super().__init__("Table", priority=60)
    
    def supports(self, content_type: str) -> bool:
        return content_type in ["table", "all"]
    
    def process(self, content: str, context: Dict[str, Any] = None) -> str:
        """处理表格"""
        self.log_processing("开始处理表格")
        
        table_count = 0
        
        def replace_table(match):
            nonlocal table_count
            table_count += 1
            
            table_content = match.group(0)
            lines = table_content.strip().split('\\n')
            
            if len(lines) < 3:  # 至少需要标题行、分隔行和一行数据
                return table_content
            
            # 解析表格
            header_line = lines[0]
            separator_line = lines[1]
            data_lines = lines[2:]
            
            # 解析表头
            headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
            col_count = len(headers)
            
            # 生成LaTeX表格
            column_spec = '|' + 'c|' * col_count
            
            latex_table = f"""\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{{column_spec}}}
\\hline
"""
            
            # 添加表头
            latex_table += ' & '.join(headers) + ' \\\\\n\\hline\n'
            
            # 添加数据行
            for line in data_lines:
                if line.strip():
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(cells) == col_count:
                        latex_table += ' & '.join(cells) + ' \\\\\n'
            
            latex_table += """\\hline
\\end{tabular}
\\end{table}"""
            
            return latex_table
        
        # 匹配Markdown表格
        table_pattern = r'(\\|[^\\n]+\\|\\n\\|[-:| ]+\\|(?:\\n\\|[^\\n]+\\|)*)'
        content = re.sub(table_pattern, replace_table, content, flags=re.MULTILINE)
        
        if table_count > 0:
            self.log_processing("处理表格", table_count)
        
        return content

class CleanupProcessor(BaseProcessor):
    """清理处理器 - 处理特殊字符和格式"""
    
    def __init__(self):
        super().__init__("Cleanup", priority=90)
    
    def supports(self, content_type: str) -> bool:
        return True  # 支持所有类型
    
    def process(self, content: str, context: Dict[str, Any] = None) -> str:
        """清理和格式化内容"""
        self.log_processing("开始清理内容")
        
        # 转义特殊LaTeX字符
        special_chars = {
            '&': '\\\\&',
            '%': '\\\\%',
            '$': '\\\\$',
            '#': '\\\\#',
            '^': '\\\\textasciicircum{}',
            '_': '\\\\_',
            '{': '\\\\{',
            '}': '\\\\}',
            '~': '\\\\textasciitilde{}'
        }
        
        # 但是要避免转义已经正确的LaTeX命令
        for char, replacement in special_chars.items():
            # 只转义不在LaTeX命令中的特殊字符
            content = re.sub(f'(?<!\\\\){re.escape(char)}(?![a-zA-Z])', replacement, content)
        
        # 处理空行 - 确保段落分隔正确
        content = re.sub(r'\\n\\n+', '\\n\\n', content)
        
        # 处理行尾空格
        content = re.sub(r' +\\n', '\\n', content)
        
        # 处理强调文本
        content = re.sub(r'\\*\\*(.*?)\\*\\*', r'\\\\textbf{\1}', content)  # 粗体
        content = re.sub(r'\\*(.*?)\\*', r'\\\\textit{\1}', content)        # 斜体
        
        # 处理行内代码
        content = re.sub(r'`([^`]+)`', r'\\\\texttt{\1}', content)
        
        self.log_processing("内容清理完成")
        
        return content

class ContentProcessor:
    """内容处理器主类 - 管理所有处理器"""
    
    def __init__(self, config=None):
        self.config = config
        self.logger = Logger("ContentProcessor")
        
        # 初始化处理器链
        self.processors = [
            ChapterNumberProcessor(),
            MathProcessor(),
            CodeBlockProcessor(), 
            ImageProcessor(),
            AdmonitionProcessor(),
            TableProcessor(),
            CleanupProcessor()
        ]
        
        # 按优先级排序
        self.processors.sort(key=lambda x: x.get_priority())
        
        self.logger.info(f"初始化了 {len(self.processors)} 个处理器")
    
    def add_processor(self, processor: IContentProcessor):
        """添加处理器"""
        self.processors.append(processor)
        self.processors.sort(key=lambda x: x.get_priority())
        self.logger.info(f"添加处理器: {processor.name}")
    
    def remove_processor(self, processor_name: str):
        """移除处理器"""
        self.processors = [p for p in self.processors if p.name != processor_name]
        self.logger.info(f"移除处理器: {processor_name}")
    
    def process_chapter_content(self, content: str, chapter_num: int, chapter_title: str) -> str:
        """处理章节内容"""
        self.logger.info(f"开始处理第{chapter_num}章内容: {chapter_title}")
        
        context = {
            'type': 'chapter',
            'chapter_num': chapter_num,
            'chapter_title': chapter_title
        }
        
        processed_content = content
        
        for processor in self.processors:
            if processor.supports('chapter') or processor.supports('all'):
                try:
                    processed_content = processor.process(processed_content, context)
                except Exception as e:
                    self.logger.error(f"处理器 {processor.name} 处理失败: {e}")
        
        self.logger.info(f"第{chapter_num}章内容处理完成")
        return processed_content
    
    def process_preface_content(self, content: str) -> str:
        """处理前言内容"""
        self.logger.info("开始处理前言内容")
        
        context = {
            'type': 'preface'
        }
        
        processed_content = content
        
        for processor in self.processors:
            if processor.supports('preface') or processor.supports('all'):
                try:
                    processed_content = processor.process(processed_content, context)
                except Exception as e:
                    self.logger.error(f"处理器 {processor.name} 处理失败: {e}")
        
        self.logger.info("前言内容处理完成")
        return processed_content
    
    def get_processor_status(self) -> Dict[str, Any]:
        """获取处理器状态"""
        return {
            'total_processors': len(self.processors),
            'processors': [
                {
                    'name': p.name,
                    'priority': p.get_priority(),
                    'supports_chapter': p.supports('chapter'),
                    'supports_preface': p.supports('preface')
                }
                for p in self.processors
            ]
        }