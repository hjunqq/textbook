#!/usr/bin/env python3
"""
Convert only the Preface (docs/前言.md) to clean LaTeX, and compile a standalone PDF.
Pipeline:
1) Read docs/前言.md
2) Sanitize (strip emoji bullets)
3) Use Pandoc (Windows fallback supported) to produce LaTeX fragment
4) Normalize the first heading to chapter* and add TOC entry
5) Write fragment to output/chapters/preface.tex
6) Generate minimal main (output/preface_main.tex) and compile with XeLaTeX
"""

import os
import re
import subprocess
from pathlib import Path

EMOJI_TO_STRIP = [
    "📱", "🔍", "📑", "💡", "🧮", "📊", "🌓", "📖"
]

ROOT = Path(__file__).resolve().parent.parent
PREFACE_MD = ROOT / "docs" / "前言.md"
OUTPUT_DIR = ROOT / "output"
CHAPTERS_DIR = OUTPUT_DIR / "chapters"


def find_pandoc() -> str:
    cmd = "pandoc"
    try:
        r = subprocess.run([cmd, "--version"], capture_output=True, text=True)
        if r.returncode == 0:
            return cmd
    except Exception:
        pass
    fallback = r"/mnt/c/Program Files/Pandoc/pandoc.exe"
    return fallback


def find_xelatex() -> str:
    cmd = "xelatex"
    try:
        r = subprocess.run([cmd, "--version"], capture_output=True, text=True)
        if r.returncode == 0:
            return cmd
    except Exception:
        pass
    fallback = r"/mnt/c/texlive/2025/bin/windows/xelatex.exe"
    return fallback


def sanitize_preface(md_text: str) -> str:
    # Strip common emoji bullets that cause missing glyphs
    for e in EMOJI_TO_STRIP:
        md_text = md_text.replace(e + " ", "")
        md_text = md_text.replace(e, "")
    return md_text


def transform_admonitions(md_text: str) -> str:
    """Convert MkDocs admonitions (!!! type "title") to LaTeX tcolorbox.
    Indented content (4 spaces) will be dedented into the box body.
    Also convert lines starting with '=== ' to level-4 markdown headers.
    """
    lines = md_text.splitlines()
    out = []
    i = 0
    color_map = {
        'note': ('注意', 'blue'),
        'tip': ('提示', 'green'),
        'warning': ('警告', 'orange'),
        'danger': ('危险', 'red'),
        'info': ('信息', 'cyan'),
    }

    while i < len(lines):
        line = lines[i]
        m = re.match(r'^!!!\s+(\w+)(?:\s+"([^"]+)")?\s*$', line)
        if not m:
            # Also normalize any standalone lines starting with '=== '
            if line.lstrip().startswith('=== '):
                title = line.strip()[4:].strip('`" ')
                out.append(f"#### {title}")
            else:
                out.append(line)
            i += 1
            continue

        # Found admonition
        a_type = m.group(1).lower()
        a_title = m.group(2) or ''
        default_title, color = color_map.get(a_type, ('提示', 'gray'))
        display_title = a_title if a_title else default_title

        # Collect indented block (>=4 spaces) following lines
        i += 1
        body_lines = []
        while i < len(lines):
            nxt = lines[i]
            if nxt.startswith('    ') or nxt.strip() == '':
                # Dedent 4 spaces if present
                body_line = nxt[4:] if nxt.startswith('    ') else ''
                # Convert any '=== ' headings inside
                if body_line.startswith('=== '):
                    title = body_line[4:].strip('`" ')
                    body_lines.append(f"#### {title}")
                else:
                    body_lines.append(body_line)
                i += 1
            else:
                break

        # Convert body Markdown-like syntax to LaTeX inline and simple lists
        def inline_format(s: str) -> str:
            # code
            s = re.sub(r"`([^`]+)`", r"\\texttt{\1}", s)
            # bold then italic
            s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
            s = re.sub(r"(?<!\*)\*(.+?)\*(?!\*)", r"\\textit{\1}", s)
            return s

        # Build LaTeX content with lists support (nesting by 2-space indents)
        latex_lines = []
        list_stack = []  # track levels for itemize

        def close_lists(to_level: int = 0):
            nonlocal latex_lines, list_stack
            while len(list_stack) > to_level:
                latex_lines.append("\\end{itemize}")
                list_stack.pop()

        code_mode = False
        code_lang = ''
        code_acc = []

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
            # fenced code start/end
            mcode = re.match(r"^```\s*([A-Za-z0-9_-]*)\s*$", raw)
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
                latex_lines.append("")
                continue
            mli = re.match(r"^(\s*)-\s+(.*)$", raw)
            if mli:
                indent = len(mli.group(1) or '')
                item = inline_format(mli.group(2))
                level = indent // 2
                # open/close lists to match level
                desired = level + 1  # ensure at least one itemize at top level
                if desired > len(list_stack):
                    for _ in range(desired - len(list_stack)):
                        latex_lines.append("\\begin{itemize}")
                        list_stack.append('itemize')
                elif desired < len(list_stack):
                    close_lists(desired)
                latex_lines.append(f"\\item {item}")
            else:
                # heading inside box like '#### Title' → bold line
                mh = re.match(r"^\s*####\s+(.*)$", raw)
                if mh:
                    close_lists(0)
                    latex_lines.append(f"\\textbf{{{inline_format(mh.group(1).strip())}}}")
                else:
                    close_lists(0)
                    latex_lines.append(inline_format(raw))

        close_lists(0)
        flush_code()
        body = "\n".join(latex_lines).strip("\n")
        out.append(
            f"\\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={display_title}]\n{body}\n\\end{{tcolorbox}}"
        )

    return '\n'.join(out)


def to_windows_path(p: Path) -> str:
    """Convert WSL path to Windows path if needed."""
    try:
        r = subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return str(p)


def normalize_preface_fragment(tex_text: str) -> str:
    # Replace the first section heading to chapter* and add TOC entry
    # Typical pandoc start: \section{前言}
    tex_text = re.sub(r"^\\section\{前言\}.*$",
                      "\\chapter*{前言}\n\\addcontentsline{toc}{chapter}{前言}",
                      tex_text, count=1, flags=re.MULTILINE)
    return tex_text


def write_minimal_main() -> Path:
    main_tex = OUTPUT_DIR / "preface_main.tex"
    preamble = r"""\documentclass[12pt,a4paper]{book}
\usepackage[UTF8]{ctex}
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{setspace}
\onehalfspacing
\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=black,urlcolor=blue,citecolor=black}
\usepackage{graphicx}
\usepackage{longtable,booktabs,array}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{tcolorbox}
\tcbuselibrary{breakable}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\begin{document}
\tableofcontents
\input{chapters/preface.tex}
\end{document}
"""
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    CHAPTERS_DIR.mkdir(exist_ok=True, parents=True)
    main_tex.write_text(preamble, encoding="utf-8")
    return main_tex


def main() -> int:
    if not PREFACE_MD.exists():
        print(f"Preface not found: {PREFACE_MD}")
        return 1

    md = PREFACE_MD.read_text(encoding="utf-8")
    md = sanitize_preface(md)
    # Normalize inline dash lists like "： - A - B - C" into proper bullets
    def normalize_inline_dash_lists(text: str) -> str:
        new_lines = []
        for line in text.splitlines():
            if '： - ' in line or ': - ' in line:
                # split after the first colon-like
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
            new_lines.append(line)
        return "\n".join(new_lines)

    md = normalize_inline_dash_lists(md)
    md = transform_admonitions(md)

    tmp_md = OUTPUT_DIR / "preface.sanitized.md"
    tmp_md.write_text(md, encoding="utf-8")

    # Pandoc convert to fragment
    pandoc = find_pandoc()
    frag_tex = CHAPTERS_DIR / "preface.tex"
    # If using Windows pandoc.exe, convert paths to Windows style
    in_path = str(tmp_md)
    out_path = str(frag_tex)
    if pandoc.lower().endswith('.exe'):
        in_path = to_windows_path(tmp_md)
        out_path = to_windows_path(frag_tex)
    cmd = [pandoc, in_path, "-o", out_path, "--wrap=none",
           "--from=markdown", "--to=latex"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print("Pandoc failed:\n", r.stderr)
        return 1

    # Normalize heading to chapter*
    tex = frag_tex.read_text(encoding="utf-8")
    # Preface headings should be unnumbered; convert subsections to starred
    tex = tex.replace("\\section{前言}",
                      "\\chapter*{前言}\n\\addcontentsline{toc}{chapter}{前言}", 1)
    tex = re.sub(r"^\\subsection\{([^}]+)\}",
                 r"\\section*{\1}\n\\addcontentsline{toc}{section}{\1}", tex, flags=re.MULTILINE)
    tex = re.sub(r"^\\subsubsection\{([^}]+)\}",
                 r"\\subsection*{\1}\n\\addcontentsline{toc}{subsection}{\1}", tex, flags=re.MULTILINE)
    frag_tex.write_text(tex, encoding="utf-8")

    # Write minimal main and compile
    main_tex = write_minimal_main()
    xelatex = find_xelatex()
    for _ in range(2):
        rr = subprocess.run([xelatex, "-interaction=nonstopmode", main_tex.name],
                            cwd=OUTPUT_DIR, capture_output=True)
        # don't exit early; run twice for ToC
    pdf = OUTPUT_DIR / "preface_main.pdf"
    if pdf.exists():
        print(f"OK: {pdf}")
        return 0
    else:
        print("XeLaTeX did not produce preface_main.pdf")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
