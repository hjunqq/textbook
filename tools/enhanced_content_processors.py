"""
增强版内容处理器
处理代码环境、章节结构优化等
"""

import re
import logging
from typing import List, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedCodeProcessor:
    """增强版代码处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.EnhancedCodeProcessor")
    
    def process_code_blocks(self, content: str) -> str:
        """处理代码块，转换为安全的listing环境"""
        self.logger.info("开始处理代码块")
        
        # 处理各种代码块模式
        content = self._fix_verbatim_blocks(content)
        content = self._convert_inline_code(content) 
        content = self._escape_special_chars_in_code(content)
        content = self._fix_broken_code_blocks(content)
        
        return content
    
    def _fix_verbatim_blocks(self, content: str) -> str:
        """修复和优化verbatim代码块"""
        # 查找verbatim环境并转换为lstlisting
        verbatim_pattern = r'\\begin\{verbatim\}(.*?)\\end\{verbatim\}'
        
        def replace_verbatim(match):
            code_content = match.group(1).strip()
            
            # 检测代码语言
            language = self._detect_language(code_content)
            
            # 转义代码中的特殊字符
            escaped_code = self._escape_code_content(code_content)
            
            return f"""\\begin{{lstlisting}}[language={language}]
{escaped_code}
\\end{{lstlisting}}"""
        
        content = re.sub(verbatim_pattern, replace_verbatim, content, flags=re.DOTALL)
        return content
    
    def _convert_inline_code(self, content: str) -> str:
        """转换行内代码"""
        # 修复各种破损的texttt命令
        fixes = [
            # 修复包含特殊字符的texttt
            (r'\\texttt\{[^}]*\\textbackslash[^}]*\}', r'\\lstinline{[code]}'),
            (r'\\texttt\{[^}]*\$[^}]*\}', r'\\lstinline{[code]}'),
            (r'\\texttt\{[^}]*\\\([^}]*\}', r'\\lstinline{[code]}'),
            # 修复超长的texttt
            (r'\\texttt\{[^}]{50,}\}', r'\\lstinline{[long code]}'),
            # 转换简单的texttt为lstinline
            (r'\\texttt\{([^}]{1,30})\}', r'\\lstinline{\1}'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _escape_special_chars_in_code(self, content: str) -> str:
        """转义代码中的特殊字符"""
        # 在lstlisting环境中的特殊字符处理
        def escape_lstlisting(match):
            code_content = match.group(1)
            # 转义常见的LaTeX特殊字符
            escaped = code_content.replace('\\', '\\textbackslash{}')
            escaped = escaped.replace('$', '\\$')
            escaped = escaped.replace('&', '\\&')
            escaped = escaped.replace('%', '\\%')
            escaped = escaped.replace('#', '\\#')
            escaped = escaped.replace('^', '\\textasciicircum{}')
            escaped = escaped.replace('_', '\\_')
            escaped = escaped.replace('{', '\\{')
            escaped = escaped.replace('}', '\\}')
            escaped = escaped.replace('~', '\\textasciitilde{}')
            
            return f"\\begin{{lstlisting}}{escaped}\\end{{lstlisting}}"
        
        # 应用到lstlisting环境
        content = re.sub(
            r'\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}',
            escape_lstlisting,
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def _fix_broken_code_blocks(self, content: str) -> str:
        """修复破损的代码块"""
        # 修复常见的代码块问题
        fixes = [
            # 修复未闭合的代码块
            (r'\\begin\{lstlisting\}(?!.*\\end\{lstlisting\})', 
             r'\\begin{lstlisting}\n[code block was incomplete]\n\\end{lstlisting}'),
            # 修复嵌套的代码环境
            (r'\\begin\{lstlisting\}.*\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}.*\\end\{lstlisting\}',
             r'\\begin{lstlisting}\n\\1\n\\end{lstlisting}'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        return content
    
    def _detect_language(self, code_content: str) -> str:
        """检测代码语言"""
        # 简单的语言检测
        if 'function' in code_content or 'const ' in code_content or 'let ' in code_content:
            return 'JavaScript'
        elif 'def ' in code_content or 'import ' in code_content:
            return 'Python'
        elif 'public class' in code_content or 'import java' in code_content:
            return 'Java'
        elif '<' in code_content and '>' in code_content:
            return 'HTML'
        elif '{' in code_content and '}' in code_content:
            return 'JavaScript'
        else:
            return 'text'
    
    def _escape_code_content(self, code_content: str) -> str:
        """转义代码内容中的特殊字符"""
        # 基本转义，避免LaTeX解析错误
        escaped = code_content
        # 只进行最基本的转义，让lstlisting处理其他
        escaped = escaped.replace('\\textbackslash', '\\')
        return escaped


class ChapterStructureProcessor:
    """章节结构处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ChapterStructureProcessor")
    
    def restructure_chapter(self, content: str) -> str:
        """重构章节结构"""
        self.logger.info("开始重构章节结构")
        
        # 提取章节各部分
        parts = self._extract_chapter_parts(content)
        
        # 重新组织结构
        restructured = self._rebuild_chapter_structure(parts)
        
        return restructured
    
    def _extract_chapter_parts(self, content: str) -> Dict[str, str]:
        """提取章节的各个部分"""
        parts = {
            'chapter_title': '',
            'learning_objectives': '',
            'introduction': '',
            'main_content': '',
            'summary': ''
        }
        
        # 提取章节标题
        chapter_match = re.search(r'\\chapter\{([^}]+)\}', content)
        if chapter_match:
            parts['chapter_title'] = chapter_match.group(0)
        
        # 提取学习目标 (通常在"学习目标"或"Learning Objectives"后)
        objectives_match = re.search(
            r'\\section\{学习目标\}(.*?)(?=\\section\{|\\chapter\{|$)',
            content,
            re.DOTALL
        )
        if objectives_match:
            parts['learning_objectives'] = objectives_match.group(1).strip()
        
        # 提取引言
        intro_match = re.search(
            r'\\section\{引言\}(.*?)(?=\\section\{|\\chapter\{|$)',
            content,
            re.DOTALL
        )
        if intro_match:
            parts['introduction'] = intro_match.group(1).strip()
        
        # 提取小结
        summary_match = re.search(
            r'\\section\{本章小结\}(.*?)(?=\\section\{|\\chapter\{|$)',
            content,
            re.DOTALL
        )
        if summary_match:
            parts['summary'] = summary_match.group(1).strip()
        
        # 提取主要内容（除去上述部分）
        main_content = content
        if objectives_match:
            main_content = main_content.replace(objectives_match.group(0), '')
        if intro_match:
            main_content = main_content.replace(intro_match.group(0), '')
        if summary_match:
            main_content = main_content.replace(summary_match.group(0), '')
        
        parts['main_content'] = main_content
        
        return parts
    
    def _rebuild_chapter_structure(self, parts: Dict[str, str]) -> str:
        """重建章节结构"""
        result = []
        
        # 章节标题
        if parts['chapter_title']:
            result.append(parts['chapter_title'])
            result.append('')
        
        # 学习目标（无编号）
        if parts['learning_objectives']:
            result.append('\\section*{学习目标}')
            result.append(parts['learning_objectives'])
            result.append('')
        
        # 引言（无编号）
        if parts['introduction']:
            result.append('\\section*{引言}')
            result.append(parts['introduction'])
            result.append('')
        
        # 主要内容
        result.append(parts['main_content'])
        
        # 小结（移动到最后）
        if parts['summary']:
            result.append('')
            result.append('\\section{本章小结}')
            result.append(parts['summary'])
        
        return '\n'.join(result)


class EnhancedContentProcessor:
    """增强版内容处理器主类"""
    
    def __init__(self):
        self.code_processor = EnhancedCodeProcessor()
        self.structure_processor = ChapterStructureProcessor()
        self.logger = logging.getLogger(f"{__name__}.EnhancedContentProcessor")
    
    def process_chapter_content(self, content: str, chapter_number: int) -> str:
        """处理章节内容"""
        self.logger.info(f"处理第{chapter_number}章内容")
        
        # 从第4章开始重点处理代码
        if chapter_number >= 4:
            content = self.code_processor.process_code_blocks(content)
        
        # 重构章节结构
        content = self.structure_processor.restructure_chapter(content)
        
        return content
    
    def process_preface_content(self, content: str) -> str:
        """处理前言内容"""
        self.logger.info("处理前言内容")
        
        # 前言也可能包含代码，进行相同处理
        content = self.code_processor.process_code_blocks(content)
        
        return content