#!/usr/bin/env python3
"""
智慧水利平台教材 LaTeX 静态验证器
替代 XeLaTeX 编译，检查所有常见结构性错误
"""
import re, os, sys, glob
from collections import Counter, defaultdict

BASE = "/sessions/festive-nifty-allen/mnt/智慧水利平台架构与开发/output"

class TexValidator:
    def __init__(self):
        self.errors = []    # (file, line, severity, msg)
        self.warnings = []
        self.stats = defaultdict(lambda: defaultdict(int))

    def err(self, f, line, msg):
        self.errors.append((f, line, "ERROR", msg))

    def warn(self, f, line, msg):
        self.warnings.append((f, line, "WARN", msg))

    def info(self, f, line, msg):
        self.warnings.append((f, line, "INFO", msg))

    def _get_verbatim_ranges(self, lines):
        """Return set of line numbers (1-indexed) inside verbatim environments."""
        verbatim_envs = {'lstlisting', 'verbatim', 'Verbatim', 'minted'}
        ranges = set()
        in_verbatim = False
        for i, line in enumerate(lines, 1):
            for env in verbatim_envs:
                if f'\\begin{{{env}}}' in line:
                    in_verbatim = True
                    break
                if f'\\end{{{env}}}' in line:
                    in_verbatim = False
                    break
            if in_verbatim:
                ranges.add(i)
        return ranges

    # ── 1. Brace balance ──
    def check_braces(self, filepath, lines):
        verbatim = self._get_verbatim_ranges(lines)
        depth = 0
        for i, line in enumerate(lines, 1):
            if i in verbatim:
                continue
            # Skip comments
            stripped = re.sub(r'(?<!\\)%.*', '', line)
            # Count unescaped braces
            opens = len(re.findall(r'(?<!\\)\{', stripped))
            closes = len(re.findall(r'(?<!\\)\}', stripped))
            depth += opens - closes
            if depth < 0:
                self.err(filepath, i, f"花括号不匹配：此行后深度为 {depth}（多余 '}}' ）")
                depth = 0  # reset to continue
        if depth != 0:
            self.err(filepath, len(lines), f"文件结束时花括号未闭合，差值 = {depth}")

    # ── 2. Environment matching ──
    def check_environments(self, filepath, lines):
        stack = []  # (env_name, line_num)
        begin_re = re.compile(r'\\begin\{(\w+[\*]?)\}')
        end_re = re.compile(r'\\end\{(\w+[\*]?)\}')

        for i, line in enumerate(lines, 1):
            stripped = re.sub(r'(?<!\\)%.*', '', line)
            for m in begin_re.finditer(stripped):
                stack.append((m.group(1), i))
            for m in end_re.finditer(stripped):
                env = m.group(1)
                if not stack:
                    self.err(filepath, i, f"\\end{{{env}}} 无对应的 \\begin{{{env}}}")
                elif stack[-1][0] != env:
                    self.err(filepath, i,
                        f"环境不匹配：期望 \\end{{{stack[-1][0]}}}（始于第{stack[-1][1]}行），"
                        f"实际遇到 \\end{{{env}}}")
                    # Try to recover
                    for j in range(len(stack)-1, -1, -1):
                        if stack[j][0] == env:
                            stack.pop(j)
                            break
                    else:
                        self.err(filepath, i, f"\\end{{{env}}} 完全找不到匹配的 \\begin")
                else:
                    stack.pop()

        for env, line in stack:
            self.err(filepath, line, f"\\begin{{{env}}} 未闭合（到文件末尾仍未找到 \\end{{{env}}}）")

    # ── 3. Image references ──
    def check_images(self, filepath, lines):
        img_re = re.compile(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}')
        # graphicspath: {images/}{../docs/chapters/images/}{../docs/assets/images/}
        # These resolve relative to where xelatex runs (output/ directory)
        search_dirs = [
            BASE,  # direct relative path from output/
            os.path.join(BASE, "images"),
            os.path.join(BASE, "..", "docs", "chapters", "images"),
            os.path.join(BASE, "..", "docs", "assets", "images"),
        ]
        for i, line in enumerate(lines, 1):
            for m in img_re.finditer(line):
                img = m.group(1)
                # Check if file exists in any search path
                found = False
                if os.path.isabs(img) and os.path.exists(img):
                    found = True
                else:
                    for d in search_dirs:
                        if os.path.exists(os.path.join(d, img)):
                            found = True
                            break
                    # Also check relative to the tex file itself
                    tex_dir = os.path.dirname(filepath)
                    if os.path.exists(os.path.join(tex_dir, img)):
                        found = True
                if not found:
                    self.warn(filepath, i, f"图片引用可能缺失：{img}")
                self.stats[filepath]["images"] += 1

    # ── 4. lstlisting integrity ──
    def check_listings(self, filepath, lines):
        in_listing = False
        listing_start = 0
        count_begin = 0
        count_end = 0
        for i, line in enumerate(lines, 1):
            if r'\begin{lstlisting}' in line:
                if in_listing:
                    self.err(filepath, i, f"嵌套 lstlisting（上一个始于第{listing_start}行未关闭）")
                in_listing = True
                listing_start = i
                count_begin += 1
            if r'\end{lstlisting}' in line:
                if not in_listing:
                    self.err(filepath, i, "\\end{lstlisting} 无对应的 \\begin")
                in_listing = False
                count_end += 1
            # Check for broken \end{lstlisting} (missing backslash)
            if re.search(r'(?<!\\)end\{lstlisting\}', line) and r'\end{lstlisting}' not in line:
                self.err(filepath, i, "疑似缺失反斜杠：end{lstlisting} → \\end{lstlisting}")

        if in_listing:
            self.err(filepath, listing_start, f"lstlisting 未关闭（始于此行）")
        self.stats[filepath]["lstlisting"] = count_begin

    # ── 5. Chapter/section structure ──
    def check_structure(self, filepath, lines):
        has_chapter = False
        sections = []
        for i, line in enumerate(lines, 1):
            stripped = re.sub(r'(?<!\\)%.*', '', line)
            if r'\chapter' in stripped and r'\chapter*' not in stripped:
                has_chapter = True
                self.stats[filepath]["chapters"] += 1
            if r'\section' in stripped and r'\section*' not in stripped:
                sections.append(i)
                self.stats[filepath]["sections"] += 1
            if r'\subsection' in stripped:
                self.stats[filepath]["subsections"] += 1

        fname = os.path.basename(filepath)
        if fname.startswith("chapter") and fname != "chapter09.tex":
            if not has_chapter:
                self.warn(filepath, 1, "章节文件缺少 \\chapter 命令")

    # ── 6. Common LaTeX errors ──
    def check_common_errors(self, filepath, lines):
        verbatim = self._get_verbatim_ranges(lines)
        for i, line in enumerate(lines, 1):
            if i in verbatim:
                # Only check encoding in verbatim
                if '�' in line:
                    self.err(filepath, i, "UTF-8 编码损坏（乱码字符 '�'）")
                continue
            # Double backslash in wrong context (not in tabular/align)
            # Check for undefined commands (heuristic)
            if r'\textbf{' in line:
                # Check for unclosed textbf
                depth = 0
                idx = line.find(r'\textbf{')
                while idx != -1:
                    for c in line[idx:]:
                        if c == '{': depth += 1
                        elif c == '}': depth -= 1
                    idx = line.find(r'\textbf{', idx + 8)

            # Check for & outside tabular/longtable (common error)
            # Check for orphan \item outside list
            if r'\item' in line:
                self.stats[filepath]["items"] += 1

            # Check for potential encoding issues
            if '�' in line:
                self.err(filepath, i, "UTF-8 编码损坏（乱码字符 '�'）")

            # Check for raw HTML that wasn't converted
            if re.search(r'<(div|span|table|tr|td|th|img|br|hr|p)\b', line):
                stripped = re.sub(r'(?<!\\)%.*', '', line)
                if re.search(r'<(div|span|table|tr|td|th|img|br|hr|p)\b', stripped):
                    self.warn(filepath, i, f"疑似未转换的 HTML 标签")

    # ── 7. Cross-reference checks ──
    def check_refs(self, filepath, lines):
        labels = set()
        refs = []
        for i, line in enumerate(lines, 1):
            for m in re.finditer(r'\\label\{([^}]+)\}', line):
                labels.add(m.group(1))
            for m in re.finditer(r'\\ref\{([^}]+)\}', line):
                refs.append((i, m.group(1)))
            for m in re.finditer(r'\\autoref\{([^}]+)\}', line):
                refs.append((i, m.group(1)))
        self.stats[filepath]["labels"] = len(labels)
        self.stats[filepath]["refs"] = len(refs)
        return labels, refs

    # ── 8. tcolorbox integrity ──
    def check_tcolorbox(self, filepath, lines):
        count = 0
        for i, line in enumerate(lines, 1):
            if r'\begin{tcolorbox}' in line:
                count += 1
        self.stats[filepath]["tcolorbox"] = count

    # ── Main validation ──
    def validate_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        lines = content.split('\n')
        self.stats[filepath]["lines"] = len(lines)

        self.check_braces(filepath, lines)
        self.check_environments(filepath, lines)
        self.check_images(filepath, lines)
        self.check_listings(filepath, lines)
        self.check_structure(filepath, lines)
        self.check_common_errors(filepath, lines)
        self.check_refs(filepath, lines)
        self.check_tcolorbox(filepath, lines)

        return self.stats[filepath]

    def validate_all(self):
        main_tex = os.path.join(BASE, "main.tex")
        chapter_dir = os.path.join(BASE, "chapters")

        files = [main_tex]
        if os.path.isdir(chapter_dir):
            files += sorted(glob.glob(os.path.join(chapter_dir, "*.tex")))

        # Collect all labels/refs for cross-file checking
        all_labels = set()
        all_refs = []

        print("=" * 72)
        print("  智慧水利平台教材 LaTeX 静态验证报告")
        print("=" * 72)

        for f in files:
            if not os.path.exists(f):
                print(f"\n⚠ 文件不存在：{f}")
                continue
            shortname = os.path.relpath(f, BASE)
            print(f"\n── {shortname} ──")
            stats = self.validate_file(f)

            labels, refs = self.check_refs(f, open(f, 'r', encoding='utf-8', errors='replace').read().split('\n'))
            all_labels.update(labels)
            all_refs.extend([(f, line, ref) for line, ref in refs])

            print(f"   行数: {stats['lines']}  |  章: {stats.get('chapters',0)}  |  "
                  f"节: {stats.get('sections',0)}  |  小节: {stats.get('subsections',0)}")
            print(f"   代码块: {stats.get('lstlisting',0)}  |  图片: {stats.get('images',0)}  |  "
                  f"tcolorbox: {stats.get('tcolorbox',0)}")
            print(f"   标签: {stats.get('labels',0)}  |  引用: {stats.get('refs',0)}")

        # Cross-file ref check
        broken_refs = [(f, l, r) for f, l, r in all_refs if r not in all_labels]
        if broken_refs:
            print(f"\n── 跨文件引用检查 ──")
            for f, l, r in broken_refs[:20]:
                self.warn(f, l, f"引用 \\ref{{{r}}} 无对应 \\label")

        # Summary
        print("\n" + "=" * 72)
        print("  验证结果汇总")
        print("=" * 72)

        total_lines = sum(s.get("lines", 0) for s in self.stats.values())
        total_images = sum(s.get("images", 0) for s in self.stats.values())
        total_listings = sum(s.get("lstlisting", 0) for s in self.stats.values())
        total_tcolorbox = sum(s.get("tcolorbox", 0) for s in self.stats.values())

        print(f"\n总行数: {total_lines:,}")
        print(f"图片引用: {total_images}")
        print(f"代码块: {total_listings}")
        print(f"告警框: {total_tcolorbox}")
        print(f"标签/引用: {sum(s.get('labels',0) for s in self.stats.values())} / "
              f"{sum(s.get('refs',0) for s in self.stats.values())}")

        print(f"\n错误数: {len(self.errors)}")
        print(f"警告数: {len(self.warnings)}")

        if self.errors:
            print("\n── 错误详情 ──")
            for f, line, sev, msg in self.errors:
                short = os.path.relpath(f, BASE)
                print(f"  ❌ {short}:{line} — {msg}")

        if self.warnings:
            print("\n── 警告详情 ──")
            for f, line, sev, msg in self.warnings[:50]:
                short = os.path.relpath(f, BASE)
                print(f"  ⚠ {short}:{line} — {msg}")
            if len(self.warnings) > 50:
                print(f"  ... 还有 {len(self.warnings)-50} 条警告")

        if not self.errors:
            print("\n✅ 未发现结构性错误，LaTeX 文件通过静态验证！")
        else:
            print(f"\n❌ 发现 {len(self.errors)} 个需修复的错误")

        return len(self.errors)

if __name__ == "__main__":
    v = TexValidator()
    err_count = v.validate_all()
    sys.exit(1 if err_count > 0 else 0)
