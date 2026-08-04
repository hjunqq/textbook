"""
智慧水利教材转换器 - 核心处理器模块
软件工程设计：单一职责原则
"""

import re
import logging
from typing import List, Tuple, Optional, Dict, Any
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
    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
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
    
    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """处理章节编号"""
        self.log_processing("开始处理章节编号")

        unnumbered_titles = {
            '学习目标', '引言', '关键概念',
            '思考题与练习', '思考题', '练习',
            '本节小结', '本章小结', '参考文献'
        }

        def strip_numeric_prefix(title: str) -> str:
            t = title.strip()
            # 去除如 1.1 / 1.1.1 / 1.1.1.1 前缀（可无空格）
            t = re.sub(r'^(\d+(?:\.\d+){0,3})\s*', '', t)
            return t.strip()

        # 一级：章节标题（移除手写“第X章 ”前缀，让LaTeX自动编号）
        chap_re = re.compile(r'^#\s*第[一二三四五六七八九十]+章\s*(.*)$', re.MULTILINE)
        def repl_chap(m):
            title = m.group(1).strip() or '章节'
            return f'\\chapter{{{title}}}'
        if chap_re.search(content):
            content = chap_re.sub(repl_chap, content)

        # 二级：小节 → section 或 section*（main_body 全部无编号）
        sec_pattern = r'^## (.*?)$'
        sec_titles = re.findall(sec_pattern, content, re.MULTILINE)
        for raw in sec_titles:
            title = strip_numeric_prefix(raw)
            old = f'## {raw}'
            if context and context.get('main_body'):
                new = f'\\section*{{{title}}}'
            elif title in unnumbered_titles:
                new = f'\\section*{{{title}}}'
            else:
                new = f'\\section{{{title}}}'
            content = content.replace(old, new)

        # 三级：子小节 → subsection 或 subsection*（main_body 全部无编号）
        subsec_pattern = r'^### (.*?)$'
        subsec_titles = re.findall(subsec_pattern, content, re.MULTILINE)
        for raw in subsec_titles:
            title = strip_numeric_prefix(raw)
            old = f'### {raw}'
            if context and context.get('main_body'):
                new = f'\\subsection*{{{title}}}'
            elif title in unnumbered_titles:
                new = f'\\subsection*{{{title}}}'
            else:
                new = f'\\subsection{{{title}}}'
            content = content.replace(old, new)

        self.log_processing("处理完成", len(sec_titles) + len(subsec_titles))
        return content
    
    def _increment_section_count(self):
        """增加小节计数（用于日志）"""
        if not hasattr(self, '_section_count'):
            self._section_count = 0
        self._section_count += 1
        return None

class PreSanitizeProcessor(BaseProcessor):
    """预处理：移除常见emoji、规范行内破折列表、将 '=== ' 标题归一化"""

    EMOJI_TO_STRIP = [
        "📱", "🔍", "📑", "💡", "🧮", "📊", "🌓", "📖"
    ]

    def __init__(self):
        super().__init__("PreSanitize")

    def _normalize_inline_dash_lists(self, text: str) -> str:
        new_lines = []
        in_code = False
        for line in text.split('\n'):
            # 代码围栏内不做任何归一化
            if line.strip().startswith('```'):
                in_code = not in_code
                new_lines.append(line)
                continue
            if in_code:
                new_lines.append(line)
                continue
            # 含反引号（行内代码）时，为避免打断代码片段，不做“： - ”拆分
            if ('： - ' in line or ': - ' in line) and ('`' not in line):
                parts = re.split(r'(：|:)', line, maxsplit=1)
                if len(parts) == 3:
                    head = (parts[0] + parts[1]).strip()
                    rest = parts[2].strip()
                    items = [x.strip() for x in rest.split(' - ') if x.strip()]
                    if len(items) >= 2:
                        new_lines.append(head)
                        for it in items:
                            new_lines.append(f"- {it}")
                        continue
            # 归一化独立行 '=== ' 为四级标题，但仅在无缩进时处理，避免破坏告警框缩进正文
            stripped = line.lstrip('\t')
            leading_spaces = len(line) - len(line.lstrip(' '))
            if leading_spaces == 0 and stripped.startswith('=== '):
                title = stripped[4:].strip('`" ')
                new_lines.append(f"#### {title}")
            else:
                new_lines.append(line)
        return "\n".join(new_lines)

    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        self.log_processing("开始预处理")
        # 去除常见emoji
        for e in self.EMOJI_TO_STRIP:
            content = content.replace(e + " ", "").replace(e, "")
        # 规范行内破折列表
        content = self._normalize_inline_dash_lists(content)
        self.log_processing("预处理完成")
        return content

class InlineListProcessor(BaseProcessor):
    """将形如 - `code`：说明 的行归并为 itemize 列表，避免行内代码与中文冒号混用导致的转义混乱"""

    def __init__(self):
        super().__init__("InlineList")

    @staticmethod
    def _escape_code(s: str) -> str:
        # 仅转义会破坏 LaTeX 的字符，并将 <> 安全输出
        rep = [
            ('\\', r'\\textbackslash '),  # 修复：使用空格而不是{}
            ('{', r'\\{'), ('}', r'\\}'),
            ('%', r'\\%'), ('$', r'\\$'), ('&', r'\\&'), ('#', r'\\#'),
            ('_', r'\\_'), ('^', r'\\^{}'), ('~', r'\\~{}'),
        ]
        # 先处理普通字符，再处理 < >
        for a, b in rep:
            s = s.replace(a, b)
        s = s.replace('<', r'\textless{}').replace('>', r'\textgreater{}')
        return s

    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        self.log_processing("开始处理内联代码说明型列表")
        lines = content.split('\n')
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # 匹配 - `code`：说明 或 - `code`: 说明（允许缩进）
            m = re.match(r'^\s*-\s*`([^`]+)`\s*([：:])\s*(.*)$', line)
            if not m:
                # 尝试匹配多代码标记列表：- `a`, `b`, `c`（允许缩进）
                mlist = re.match(r'^\s*-\s*((?:`[^`]+`\s*,\s*)+`[^`]+`)\s*$', line)
                if not mlist:
                    out.append(line)
                    i += 1
                    continue
                # 收集连续块的多代码标记列表
                block_tokens = []
                while i < len(lines):
                    mlist2 = re.match(r'^\s*-\s*((?:`[^`]+`\s*,\s*)+`[^`]+`)\s*$', lines[i])
                    if not mlist2:
                        break
                    token_line = mlist2.group(1)
                    # 提取反引号中的代码
                    tokens = re.findall(r'`([^`]+)`', token_line)
                    block_tokens.append(tokens)
                    i += 1
                # 输出为 itemize：每一行成为一组 item（每个 token 独立 item）
                out.append('\\begin{itemize}')
                out.append('\\tightlist')
                for tokens in block_tokens:
                    for code in tokens:
                        out.append(f"\\item \\texttt{{{self._escape_code(code)}}}")
                out.append('\\end{itemize}')
                continue
            # 收集连续块
            block = []
            while i < len(lines):
                m2 = re.match(r'^\s*-\s*`([^`]+)`\s*([：:])\s*(.*)$', lines[i])
                if not m2:
                    break
                code = m2.group(1)
                desc = m2.group(3)
                block.append((code, desc))
                i += 1
            # 输出 itemize
            out.append('\\begin{itemize}')
            out.append('\\tightlist')
            for code, desc in block:
                code_tex = self._escape_code(code)
                out.append(f"\\item \\texttt{{{code_tex}}}：{desc}")
            out.append('\\end{itemize}')
        new_content = '\n'.join(out)
        self.log_processing("内联代码说明型列表处理完成")
        return new_content

class MathProcessor(BaseProcessor):
    """数学公式处理器"""
    
    def __init__(self):
        super().__init__("Math")
    
    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
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
                equation_env = f'\\begin{{equation}}\n{formula.strip()}\n\\end{{equation}}'
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
    
    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """处理图片：
        - 表格内的图片：保持为Markdown图片语法，仅规范路径，并添加宽度属性以适配单元格
        - 非表格图片：转换为 LaTeX figure 环境
        """
        self.log_processing("开始处理图片")

        lines = content.split('\n')
        in_code = False

        def is_table_context(lines: list, idx: int, line: str) -> bool:
            row = line.strip()
            if row.startswith('|') and row.endswith('|'):
                return True
            # 上下文有对齐线或管道表格迹象
            prev = lines[idx-1].strip() if idx-1 >= 0 else ''
            nextl = lines[idx+1].strip() if idx+1 < len(lines) else ''
            align_re = r'^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+$'
            if re.match(align_re, prev) or re.match(align_re, nextl):
                return True
            # 本行有多个竖线，且看起来是表格行
            if '|' in line and (line.count('|') >= 2):
                return True
            return False

        img_re = re.compile(r'!\[([^\]]*?)\]\(([^)]+?)\)')
        chapter_prefix = None
        if context and isinstance(context, dict) and 'chapter_num' in context:
            try:
                chapter_prefix = f"images/chapter{int(context['chapter_num']):02d}/"
            except Exception:
                chapter_prefix = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('```'):
                in_code = not in_code
                continue
            if in_code:
                continue

            def norm_path(p: str) -> str:
                cp = p.replace('../docs/chapters/', '').replace('docs/chapters/', '')
                # 归一化为 images/ 开头
                if cp.startswith('images/'):
                    norm = cp
                elif cp.startswith('../images/'):
                    norm = cp[3:]
                else:
                    norm = 'images/' + cp.lstrip('./')
                # 注入章节子目录，与复制路径一致
                if chapter_prefix and norm.startswith('images/') and not norm.startswith(chapter_prefix):
                    norm = chapter_prefix + norm[len('images/'):]
                return norm

            # 表格内：仅规范路径并添加宽度属性（pandoc 支持）
            if img_re.search(line):
                if is_table_context(lines, i, line):
                    def repl_table(m):
                        alt, p = m.group(1), m.group(2)
                        cp = norm_path(p)
                        return f'![{alt}]({cp}){{width=45%}}'
                    lines[i] = img_re.sub(repl_table, line)
                else:
                    def repl_block(m):
                        alt, p = m.group(1), m.group(2)
                        cp = norm_path(p)
                        caption = alt if alt else '图片'
                        return (f"\\begin{{figure}}[htbp]\n"
                                f"\\centering\n"
                                f"\\includegraphics[width=0.8\\textwidth]{{{cp}}}\n"
                                f"\\caption{{{caption}}}\n"
                                f"\\end{{figure}}")
                    lines[i] = img_re.sub(repl_block, line)

        result = '\n'.join(lines)
        self.log_processing("图片处理完成")
        return result

class CodeProcessor(BaseProcessor):
    """代码处理器"""
    
    def __init__(self):
        super().__init__("Code")
    
    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
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
                    latex_code = f'''\\begin{{lstlisting}}[language={language.title()}]
{code_content.strip()}
\\end{{lstlisting}}'''
                else:
                    latex_code = f'''\\begin{{lstlisting}}
{code_content.strip()}
\\end{{lstlisting}}'''
                
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
            content = re.sub(inline_code_pattern, r'\\texttt{\1}', content)
        
        self.log_processing("代码处理完成")
        return content

class RobustCodeProcessor(BaseProcessor):
    """更鲁棒的代码处理器
    - 兼容 CRLF/LF 换行
    - 支持可选语言标识
    - 去除相邻重复的 lstlisting 代码块
    - 行内代码转为 \texttt{}
    """

    def __init__(self):
        super().__init__("RobustCode")

    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        self.log_processing("开始处理代码（鲁棒版）")

        # 统一换行符
        text = content.replace('\r\n', '\n')

        # 语言名映射，提高 listings 兼容性
        lang_map = {
            'js': 'JavaScript', 'javascript': 'JavaScript', 'ts': 'JavaScript',
            'html': 'html', 'css': 'html', 'xml': 'xml', 'json': 'json',
            'yml': 'yaml', 'yaml': 'yaml',
            'bash': 'bash', 'shell': 'bash', 'sh': 'bash',
            'py': 'Python', 'python': 'Python', 'java': 'Java', 'sql': 'SQL',
        }

        def _map_lang(lang: str) -> str:
            l = (lang or '').strip().lower()
            return lang_map.get(l, (l.title() if l else ''))

        # 处理围栏代码块（```lang ... ```），基于行的稳健识别
        code_block_pattern = re.compile(r"(?m)^\s*```\s*([A-Za-z0-9_-]*)\s*\n([\s\S]*?)\n\s*```\s*$")
        parts: List[str] = []
        last = 0
        for m in code_block_pattern.finditer(text):
            parts.append(text[last:m.start()])
            lang = _map_lang(m.group(1) or '')
            body = (m.group(2) or '').rstrip('\n')
            if lang:
                latex = f"\\begin{{lstlisting}}[language={lang}]\n{body}\n\\end{{lstlisting}}"
            else:
                latex = f"\\begin{{lstlisting}}\n{body}\n\\end{{lstlisting}}"
            parts.append(latex)
            last = m.end()
        parts.append(text[last:])
        text = ''.join(parts)

        # 相邻重复 lstlisting 环境去重（内容与语言相同且中间仅空白）
        lst_re = re.compile(r"\\begin\{lstlisting\}(\[language=[^\]]+\])?\s*\n([\s\S]*?)\n\\end\{lstlisting\}")
        cleaned: List[str] = []
        pos = 0
        prev = None  # (lang_tag, body)
        for m in lst_re.finditer(text):
            inter = text[pos:m.start()]
            lang_tag = (m.group(1) or '')
            body = m.group(2)
            if prev and inter.strip() == '' and body == prev[1] and lang_tag == prev[0]:
                pos = m.end()
                continue
            cleaned.append(inter)
            cleaned.append(m.group(0))
            pos = m.end()
            prev = (lang_tag, body)
        cleaned.append(text[pos:])
        text = ''.join(cleaned)

        # 行内代码 -> \texttt{...}，并转义 LaTeX 特殊字符
        def escape_tex(s: str) -> str:
            # 不做任何转义，保持原样
            return s

        def inline_repl(m):
            content = m.group(1)
            # 检测是否是HTML标签格式
            if content.startswith('<') and content.endswith('>') and content.count('<') == 1 and content.count('>') == 1:
                # 提取标签名
                tag_name = content[1:-1]  # 去掉 < >
                # 使用自定义的LaTeX命令，让Pandoc将其识别为原始LaTeX
                return f"\\htmltag{{{tag_name}}}"
            else:
                # 普通行内代码保持不变
                return "`" + content + "`"

        inline_pattern = re.compile(r'`([^`]+)`')
        if inline_pattern.search(text):
            text = inline_pattern.sub(inline_repl, text)
            self.log_processing("行内代码", 1)

        # 配平 lstlisting：未匹配的 end 转义为文本；多余的 begin 自动闭合
        def balance_lstlisting(src: str) -> str:
            out: List[str] = []
            i = 0
            n = len(src)
            open_count = 0
            while i < n:
                b = src.find('\\begin{lstlisting}', i)
                e = src.find('\\end{lstlisting}', i)
                if b == -1 and e == -1:
                    out.append(src[i:])
                    break
                if e != -1 and (b == -1 or e < b):
                    if open_count > 0:
                        out.append(src[i:e+len('\\end{lstlisting}')])
                        i = e + len('\\end{lstlisting}')
                        open_count -= 1
                    else:
                        out.append(src[i:e])
                        out.append(r"\\textbackslash{}end\{lstlisting\}")
                        i = e + len('\\end{lstlisting}')
                else:
                    out.append(src[i:b+len('\\begin{lstlisting}')])
                    i = b + len('\\begin{lstlisting}')
                    open_count += 1
            if open_count > 0:
                out.append("\n" + "\\end{lstlisting}\n" * open_count)
            return ''.join(out)

        text = balance_lstlisting(text)

        self.log_processing("代码处理完成（鲁棒版）")
        return text

class AdmonitionProcessor(BaseProcessor):
    """增强的告警框处理器：支持缩进块、列表、代码块，与前言一致的体验"""
    
    def __init__(self):
        super().__init__("Admonition")
    
    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """处理告警框（!!! type "title" + 4空格缩进内容）"""
        self.log_processing("开始处理告警框")

        lines = content.splitlines()
        out: List[str] = []
        i = 0
        count = 0
        color_map = {
            'note': ('注意', 'blue'),
            'tip': ('提示', 'green'),
            'warning': ('警告', 'orange'),
            'danger': ('危险', 'red'),
            'info': ('信息', 'cyan'),
        }

        def _escape_inline(s: str) -> str:
            # 智能转义策略：HTML标签不转义尖括号，其他内容转义
            if s.startswith('<') and s.endswith('>') and s.count('<') == 1 and s.count('>') == 1:
                # 这是HTML标签，不转义尖括号
                repl = [
                    ('\\', r'\\textbackslash '),  # 反斜杠
                    ('%', r'\\%'), ('$', r'\\$'), ('&', r'\\&'), ('#', r'\\#'),
                    ('_', r'\\_'), ('^', r'\\^{}'), ('~', r'\\~{}'),
                ]
            else:
                # 非HTML标签，转义尖括号
                repl = [
                    ('\\', r'\\textbackslash '),  # 反斜杠
                    ('<', r'\\textless{}'), ('>', r'\\textgreater{}'),  # 尖括号
                    ('%', r'\\%'), ('$', r'\\$'), ('&', r'\\&'), ('#', r'\\#'),
                    ('_', r'\\_'), ('^', r'\\^{}'), ('~', r'\\~{}'),
                ]
            for a, b in repl:
                s = s.replace(a, b)
            return s

        def inline_format(s: str) -> str:
            # 行内代码采用转义后的 \texttt{}
            s = re.sub(r"`([^`]+)`", lambda m: r"\\texttt{" + _escape_inline(m.group(1)) + r"}", s)
            s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
            s = re.sub(r"(?<!\*)\*(.+?)\*(?!\*)", r"\\textit{\1}", s)
            return s

        while i < len(lines):
            line = lines[i]
            m = re.match(r'^!!!\s+(\w+)(?:\s+"([^"]+)")?\s*$', line)
            if not m:
                # 与前言一致：独立行以 '=== ' 开头，转成四级标题
                if line.lstrip().startswith('=== '):
                    title = line.strip()[4:].strip('`" ')
                    out.append(f"#### {title}")
                else:
                    out.append(line)
                i += 1
                continue

            a_type = m.group(1).lower()
            a_title = (m.group(2) or '').strip()
            default_title, color = color_map.get(a_type, ('提示', 'gray'))
            display_title = a_title if a_title else default_title

            # 收集缩进块（4空格）
            i += 1
            body_lines: List[str] = []
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith('    ') or nxt.strip() == '':
                    body_line = nxt[4:] if nxt.startswith('    ') else ''
                    # 允许在告警框内使用 '=== '
                    if body_line.startswith('=== '):
                        title = body_line[4:].strip('`" ')
                        body_lines.append(f"#### {title}")
                    else:
                        body_lines.append(body_line)
                    i += 1
                else:
                    break

            # 解析正文为 LaTeX（支持列表/代码块）
            latex_lines: List[str] = []
            list_stack: List[str] = []

            def close_lists(level: int = 0):
                nonlocal latex_lines, list_stack
                while len(list_stack) > level:
                    latex_lines.append('\\end{itemize}')
                    list_stack.pop()

            code_mode = False
            code_lang = ''
            code_acc: List[str] = []

            def flush_code():
                nonlocal code_mode, code_acc, latex_lines, code_lang
                if not code_mode:
                    return
                close_lists(0)
                lang_opt = f"[language={code_lang}]" if code_lang else ""
                latex_lines.append(f"\\begin{{lstlisting}}{lang_opt}")
                latex_lines.extend(code_acc)
                latex_lines.append("\\end{lstlisting}")
                code_mode = False
                code_lang = ''
                code_acc = []

            for raw in body_lines:
                mcode = re.match(r'^```\s*([A-Za-z0-9_-]*)\s*$', raw)
                if mcode:
                    if not code_mode:
                        code_mode = True
                        code_lang = mcode.group(1)
                        code_acc = []
                    else:
                        flush_code()
                    continue
                if code_mode:
                    code_acc.append(raw)
                    continue

                if raw.strip() == '':
                    close_lists(0)
                    latex_lines.append('')
                    continue

                mli = re.match(r'^(\s*)-\s+(.*)$', raw)
                if mli:
                    indent = len(mli.group(1) or '')
                    item = inline_format(mli.group(2))
                    level = indent // 2
                    desired = level + 1
                    if desired > len(list_stack):
                        for _ in range(desired - len(list_stack)):
                            latex_lines.append('\\begin{itemize}')
                            list_stack.append('itemize')
                    elif desired < len(list_stack):
                        close_lists(desired)
                    latex_lines.append(f"\\item {item}")
                else:
                    mh = re.match(r'^\s*####\s+(.*)$', raw)
                    if mh:
                        close_lists(0)
                        latex_lines.append(f"\\textbf{{{inline_format(mh.group(1).strip())}}}")
                    else:
                        close_lists(0)
                        latex_lines.append(inline_format(raw))

            close_lists(0)
            flush_code()
            body = "\n".join(latex_lines).strip('\n')
            out.append(f"\\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={display_title}]\n{body}\n\\end{{tcolorbox}}")
            count += 1

        new_content = "\n".join(out)
        if count:
            self.log_processing("找到告警框", count)
        self.log_processing("告警框处理完成")
        return new_content

class YamlProtectionProcessor(BaseProcessor):
    """YAML保护处理器 - 将裸露的YAML内容包装在代码块中"""
    
    def __init__(self):
        super().__init__("YamlProtection")
    
    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
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
            PreSanitizeProcessor(),
            YamlProtectionProcessor(),  # 保护YAML内容
            ChapterNumberProcessor(),
            MathProcessor(), 
            FigureProcessor(),
            InlineListProcessor(),      # 将形如 - `code`：说明 转为 itemize
            AdmonitionProcessor(),  # 先处理告警框，避免代码块被提前转换
            RobustCodeProcessor(),
        ]
        self.logger = logging.getLogger(__name__)
    
    def process_all(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """执行所有处理器"""
        self.logger.info("开始内容处理流水线")
        
        for processor in self.processors:
            self.logger.info(f"执行处理器: {processor.name}")
            content = processor.process(content, context)
        
        self.logger.info("内容处理流水线完成")
        return content
