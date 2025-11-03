"""
LaTeX语法验证器
修复转换后的LaTeX文件中的语法错误
"""

import re
import logging
from typing import List, Tuple, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class LaTeXValidator:
    """LaTeX语法验证和修复器"""
    
    def __init__(self):
        self.fixes_applied = 0
        self.logger = logging.getLogger(f"{__name__}.LaTeXValidator")
    
    def validate_and_fix(self, content: str) -> str:
        """验证并修复LaTeX语法错误"""
        self.logger.info("开始LaTeX语法验证和修复")
        self.fixes_applied = 0
        
        # 应用所有修复规则
        content = self._fix_malformed_headers(content)
        content = self._fix_malformed_environments(content)
        content = self._fix_bare_hash_symbols(content)
        content = self._fix_malformed_tcolorbox(content)
        content = self._fix_stray_backslashes(content)
        content = self._fix_math_escaped_dollars(content)
        content = self._fix_math_syntax(content)
        content = self._fix_listing_syntax(content)
        content = self._fix_excessive_symbols(content)
        content = self._fix_problematic_code_lines(content)
        content = self._clean_duplicate_newlines(content)
        
        self.logger.info(f"LaTeX语法修复完成，共修复 {self.fixes_applied} 处错误")
        return content

    def _fix_math_escaped_dollars(self, content: str) -> str:
        """将被转义的 \$...\$ 恢复为数学模式 $...$，并解开下划线/大括号等转义。

        仅在 lstlisting 之外处理。
        """
        def unescape_math(s: str) -> str:
            return (s.replace('\\_', '_')
                     .replace('\\{', '{')
                     .replace('\\}', '}'))

        def fix_segment(seg: str) -> str:
            import re
            def repl(m):
                inner = unescape_math(m.group(1))
                return f'${inner}$'
            return re.sub(r'\\\$(.+?)\\\$', repl, seg)

        out = []
        i = 0
        begin = '\\begin{lstlisting}'
        end = '\\end{lstlisting}'
        n = len(content)
        while i < n:
            b = content.find(begin, i)
            if b == -1:
                out.append(fix_segment(content[i:]))
                break
            out.append(fix_segment(content[i:b]))
            e = content.find(end, b)
            if e == -1:
                out.append(content[b:])
                break
            out.append(content[b:e+len(end)])
            i = e + len(end)
        fixed = ''.join(out)
        if fixed != content:
            self.fixes_applied += 1
        return fixed
    
    def _fix_malformed_headers(self, content: str) -> str:
        """修复错误的标题格式"""
        fixes = [
            # 修复 \##\# 这类错误格式
            (r'\\#+\\*#*', ''),
            # 修复多个反斜杠的标题
            (r'\\\\#+\s*', ''),
            # 修复裸露的多个#号
            (r'^\s*#{3,}\s*$', '', re.MULTILINE),
            # 修复错误的章节命令格式
            (r'\\chapter\s*\\\s*{', r'\\chapter{'),
            (r'\\section\s*\\\s*{', r'\\section{'),
        ]
        
        for pattern, replacement, *flags in fixes:
            flag = flags[0] if flags else 0
            old_count = len(re.findall(pattern, content, flag))
            content = re.sub(pattern, replacement, content, flags=flag)
            new_count = len(re.findall(pattern, content, flag))
            self.fixes_applied += (old_count - new_count)
        
        return content
    
    def _fix_malformed_environments(self, content: str) -> str:
        """修复错误的LaTeX环境"""
        fixes = [
            # 修复lstlisting环境中的多余反斜杠
            (r'\\\\begin\{lstlisting\}', r'\\begin{lstlisting}'),
            (r'\\\\end\{lstlisting\}', r'\\end{lstlisting}'),
            # 修复equation环境中的多余反斜杠
            (r'\\\\begin\{equation\}', r'\\begin{equation}'),
            (r'\\\\end\{equation\}', r'\\end{equation}'),
            # 修复figure环境中的多余反斜杠
            (r'\\\\begin\{figure\}', r'\\begin{figure}'),
            (r'\\\\end\{figure\}', r'\\end{figure}'),
            # 修复tcolorbox环境中的多余反斜杠
            (r'\\\\begin\{tcolorbox\}', r'\\begin{tcolorbox}'),
            (r'\\\\end\{tcolorbox\}', r'\\end{tcolorbox}'),
        ]
        
        for pattern, replacement in fixes:
            old_count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            new_count = len(re.findall(pattern, content))
            self.fixes_applied += (old_count - new_count)
        
        return content
    
    def _fix_bare_hash_symbols(self, content: str) -> str:
        """修复裸露的#号"""
        # 修复行首的多个#号（应该已经被转换为LaTeX命令）
        pattern = r'^\s*#+\s*(.*)$'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        for match in matches:
            if match.strip():  # 如果#后面有内容，说明是遗漏的标题
                # 这些应该在之前的处理器中被处理，这里直接删除
                old_line = re.search(r'^\s*#+\s*' + re.escape(match) + r'$', content, re.MULTILINE)
                if old_line:
                    content = content.replace(old_line.group(0), '')
                    self.fixes_applied += 1
            else:
                # 空的#行，直接删除
                content = re.sub(r'^\s*#+\s*$', '', content, flags=re.MULTILINE)
                self.fixes_applied += 1
        
        return content
    
    def _fix_malformed_tcolorbox(self, content: str) -> str:
        """修复格式错误的tcolorbox"""
        # 查找可能的tcolorbox语法错误
        fixes = [
            # 修复选项中的错误格式
            (r'\\begin\{tcolorbox\}\[([^\]]*?)\\\]', r'\\begin{tcolorbox}[\1]'),
            # 修复title参数中的转义问题  
            (r'title=([^,\]]*?)\\([^,\]]*?)', r'title=\1\2'),
        ]
        
        for pattern, replacement in fixes:
            old_count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            new_count = len(re.findall(pattern, content))
            self.fixes_applied += (old_count - new_count)
        
        return content
    
    def _fix_stray_backslashes(self, content: str) -> str:
        """修复多余的反斜杠"""
        fixes = [
            # 修复命令前的多余反斜杠
            (r'\\\\(chapter|section|subsection|includegraphics|caption)\{', r'\\\1{'),
            # 修复texttt等命令的多余反斜杠
            (r'\\\\texttt\{', r'\\texttt{'),
            # 修复其他常见LaTeX命令的多余反斜杠
            (r'\\\\(centering|label|ref)\b', r'\\\1'),
        ]
        
        for pattern, replacement in fixes:
            old_count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            new_count = len(re.findall(pattern, content))
            self.fixes_applied += (old_count - new_count)
        
        return content
    
    def _fix_math_syntax(self, content: str) -> str:
        """修复数学公式语法"""
        fixes = [
            # 修复equation环境中的多余空行
            (r'\\begin\{equation\}\s*\n\s*\n', r'\\begin{equation}\n'),
            (r'\n\s*\n\s*\\end\{equation\}', r'\n\\end{equation}'),
            # 确保数学环境前后有适当的换行
            (r'([^\n])\\begin\{equation\}', r'\1\n\\begin{equation}'),
            (r'\\end\{equation\}([^\n])', r'\\end{equation}\n\1'),
        ]
        
        for pattern, replacement in fixes:
            old_count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            new_count = len(re.findall(pattern, content))
            self.fixes_applied += (old_count - new_count)
        
        return content
    
    def _fix_listing_syntax(self, content: str) -> str:
        """修复代码列表语法"""
        # 确保lstlisting环境格式正确
        fixes = [
            # 修复language参数
            (r'\\begin\{lstlisting\}\[language=([^\]]*?)\\\]', r'\\begin{lstlisting}[language=\1]'),
            # 确保代码块前后有适当换行
            (r'([^\n])\\begin\{lstlisting\}', r'\1\n\\begin{lstlisting}'),
            (r'\\end\{lstlisting\}([^\n])', r'\\end{lstlisting}\n\1'),
            # 修复代码块中的过长行（可能导致内存溢出）
            (r'(\\begin\{lstlisting\}.*?)(\[{100,})(.*?\\end\{lstlisting\})', 
             r'\1[code block too long, truncated]\3', re.DOTALL),
        ]
        
        for pattern, replacement, *flags in fixes:
            flag = flags[0] if flags else 0
            old_count = len(re.findall(pattern, content, flag))
            content = re.sub(pattern, replacement, content, flags=flag)
            new_count = len(re.findall(pattern, content, flag))
            self.fixes_applied += (old_count - new_count)
        
        return content
    
    def _fix_excessive_symbols(self, content: str) -> str:
        """修复过多的重复符号（可能导致内存溢出）"""
        fixes = [
            # 修复过多的方括号
            (r'\[{50,}', '[...excessive brackets removed...]'),
            (r'\]{50,}', '[...excessive brackets removed...]'),
            # 修复过多的大括号  
            (r'\{{50,}', '{...excessive braces removed...}'),
            (r'\}{50,}', '{...excessive braces removed...}'),
            # 修复过多的反斜杠
            (r'\\{10,}', r'\\\\'),
        ]
        
        for pattern, replacement in fixes:
            old_count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            if old_count > 0:
                self.fixes_applied += old_count
                self.logger.warning(f"修复了 {old_count} 处过多重复符号")
        
        return content
    
    def _fix_problematic_code_lines(self, content: str) -> str:
        """修复有问题的代码行（导致编译失败）"""
        # 查找和修复特定的问题行
        problematic_patterns = [
            # 修复包含破坏性LaTeX命令的长行
            (r'^.*\\textbackslash texttt.*value.*米.*temperature.*$', 
             r'// [此行代码过长已截断] function formatPropertyValue(property, value) { /* 省略 */ }', re.MULTILINE),
            # 修复未闭合的数学模式
            (r'\\texttt\{[^}]*\\\([^)]*$', r'\\texttt{[math mode fixed]}'),
            # 修复包含数学模式混乱的texttt命令
            (r'\\texttt\{[^}]*\\\([^}]*\}', r'\\texttt{[fixed]}'),
        ]
        
        for pattern, replacement, *flags in problematic_patterns:
            flag = flags[0] if flags else 0
            matches = re.findall(pattern, content, flag)
            if matches:
                self.logger.warning(f"发现 {len(matches)} 处问题代码行，正在修复...")
                content = re.sub(pattern, replacement, content, flags=flag)
                self.fixes_applied += len(matches)
        
        return content
    
    def _clean_duplicate_newlines(self, content: str) -> str:
        """清理多余的换行符"""
        # 清理连续的空行（保留最多2个换行符）
        old_content = content
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        if content != old_content:
            self.fixes_applied += 1
        
        return content
    
    def validate_file(self, file_path: Path) -> bool:
        """验证单个LaTeX文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fixed_content = self.validate_and_fix(content)
            
            # 如果有修复，保存文件
            if self.fixes_applied > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                self.logger.info(f"文件 {file_path.name} 已修复并保存")
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证文件 {file_path} 时出错: {e}")
            return False
    
    def validate_directory(self, directory: Path) -> Dict[str, int]:
        """验证目录中的所有LaTeX文件"""
        results = {"validated": 0, "fixed": 0, "errors": 0}
        
        for tex_file in directory.rglob("*.tex"):
            results["validated"] += 1
            old_fixes = self.fixes_applied
            
            if self.validate_file(tex_file):
                if self.fixes_applied > old_fixes:
                    results["fixed"] += 1
            else:
                results["errors"] += 1
        
        return results
