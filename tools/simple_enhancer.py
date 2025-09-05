"""
简化版内容增强器
专门处理关键的代码环境和章节结构问题
"""

import re
import logging

logger = logging.getLogger(__name__)

class SimpleContentEnhancer:
    """简化版内容增强器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SimpleContentEnhancer")
    
    def enhance_chapter(self, content: str, chapter_num: int) -> str:
        """增强章节内容"""
        self.logger.info(f"增强第{chapter_num}章内容")
        
        # 1. 修复学习目标和引言为无编号
        content = self._fix_unnumbered_sections(content)
        
        # 2. 处理代码环境（从第4章开始）
        if chapter_num >= 4:
            content = self._fix_code_environments(content)
        
        # 3. 移动小结到末尾
        content = self._move_summary_to_end(content)
        
        return content
    
    def _fix_unnumbered_sections(self, content: str) -> str:
        """修复学习目标和引言为无编号章节"""
        # 学习目标改为无编号
        content = re.sub(r'\\section\{学习目标\}', r'\\section*{学习目标}', content)
        # 引言改为无编号  
        content = re.sub(r'\\section\{引言\}', r'\\section*{引言}', content)
        
        return content
    
    def _fix_code_environments(self, content: str) -> str:
        """修复代码环境"""
        # 将verbatim转换为lstlisting
        content = re.sub(
            r'\\begin\{verbatim\}(.*?)\\end\{verbatim\}',
            r'\\begin{lstlisting}\1\\end{lstlisting}',
            content,
            flags=re.DOTALL
        )
        
        # 修复破损的行内代码
        content = re.sub(r'\\texttt\{[^}]*\\textbackslash[^}]*\}', r'\\code{[code]}', content)
        content = re.sub(r'\\texttt\{[^}]{50,}\}', r'\\code{[long-code]}', content)
        
        return content
    
    def _move_summary_to_end(self, content: str) -> str:
        """移动小结到章节末尾"""
        # 查找小结内容
        summary_pattern = r'(\\section\{本章小结\}.*?)(?=\\section\{(?!本章小结)[^}]*\}|$)'
        summary_match = re.search(summary_pattern, content, re.DOTALL)
        
        if summary_match:
            summary_content = summary_match.group(1)
            # 从原位置移除
            content = content.replace(summary_content, '')
            # 添加到末尾
            content = content.rstrip() + '\n\n' + summary_content
        
        return content