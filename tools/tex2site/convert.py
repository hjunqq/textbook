#!/usr/bin/env python3
"""LaTeX -> MkDocs Markdown 迁移流水线
输入: ~/rework/output/chapters/*.tex, ~/rework/output/appendix/answers.tex
输出: ~/site-mig/out/docs/... 与 tikz 片段 ~/site-mig/tikz/
"""
import re, sys, os, pathlib, subprocess, json, shutil
from svg_provenance import source_hash, verified_svg
from hybrid_graphics import graphics_paths, graphics_dependencies

# 仓库路径约定:本脚本位于 tools/tex2site/,唯一事实来源是 output/ 下的 LaTeX。
HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path(os.environ.get("TEX2SITE_REPO", HERE.parent.parent))
ROOT = pathlib.Path(os.environ.get("TEX2SITE_BUILD", REPO / "temp" / "tex2site-build"))
ROOT.mkdir(parents=True, exist_ok=True)
SRC = REPO / "output/chapters"
APPENDIX = REPO / "output/appendix/answers.tex"
APPENDIX_B = REPO / "output/appendix/prep.tex"
APPENDIX_C = REPO / "output/appendix/extended.tex"
OUT = REPO / "docs"
TIKZ = ROOT / "tikz"
AUX = REPO / "output/main.aux"
WEBFIGS = HERE / "webfigs"

CHAPTERS = [("preface", 0), ("chapter01", 1), ("chapter02", 2), ("chapter03", 3),
            ("chapter04", 4), ("chapter05", 5), ("chapter06", 6), ("chapter07", 7),
            ("chapter08", 8), ("chapter09", 9), ("answers", "A"), ("prep", "B"), ("extended", "C")]

LANG_MAP = {"javascript": "javascript", "js": "javascript", "vue": "vue", "css": "css",
            "html": "html", "json": "json", "yaml": "yaml", "yml": "yaml", "sql": "sql",
            "java": "java", "python": "python", "bash": "bash", "sh": "bash",
            "nginx": "nginx", "http": "http", "glsl": "glsl", "xml": "xml", "text": "text",
            "dockerfile": "dockerfile", "properties": "properties", "ini": "ini"}

BOXES = {"tipbox": ("tip", "提示"), "notebox": ("note", "说明"),
         "warningbox": ("warning", "注意"), "importantbox": ("danger", "重要")}

# ---------- 工具 ----------

def balanced(s, i):
    """s[i]=='{' -> 返回(内容, 结束位置后一位)"""
    assert s[i] == '{'
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '{' and (j == 0 or s[j-1] != '\\'):
            depth += 1
        elif s[j] == '}' and s[j-1] != '\\':
            depth -= 1
            if depth == 0:
                return s[i+1:j], j+1
    raise ValueError("unbalanced")

def flatten_shortstack(t):
    """\\shortstack 只为纸面窄列手工折行；网页表格会自动换行。
    不展开的话 pandoc 把栈内的 \\\\ 当成表格行结束，一条路径被拆成两三行残片。
    这里把各段首尾相接：相邻的 \\texttt 合并成一个，其余文字直接连接。"""
    out, pos = [], 0
    for mo in re.finditer(r"\\shortstack\s*(\[[lcr]\])?\s*\{", t):
        if mo.start() < pos:
            continue
        body, end = balanced(t, mo.end() - 1)
        parts = [x.strip() for x in re.split(r"\\\\(?:\[[^\]]*\])?", body)]
        joined = "".join(parts).replace("}\\texttt{", "")
        out.append(t[pos:mo.start()] + joined)
        pos = end
    out.append(t[pos:])
    return "".join(out)

def find_env(s, env, start=0):
    b = s.find(r"\begin{%s}" % env, start)
    if b < 0:
        return None
    e = s.find(r"\end{%s}" % env, b)
    if e < 0:
        return None
    e2 = e + len(r"\end{%s}" % env)
    return b, e2

def parse_aux():
    m = {}
    txt = AUX.read_text(encoding="utf-8", errors="ignore")
    for mo in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^{}]*)\}", txt):
        m[mo.group(1)] = mo.group(2)
    return m

AUXMAP = parse_aux()

def parse_case_params():
    p = SRC.parent / "case-params.tex"
    m = {}
    if p.exists():
        for mo in re.finditer(r"\\newcommand\{\\(cp[A-Za-z]+)\}\{([^}]*)\}", p.read_text(encoding="utf-8")):
            m[mo.group(1)] = mo.group(2)
    return m

CASEPARAMS = parse_case_params()

def expand_case_params(t):
    for name in sorted(CASEPARAMS, key=len, reverse=True):
        t = re.sub(r"\\%s(?![A-Za-z]) ?" % name, CASEPARAMS[name].replace("\\", r"\\"), t)
    return t

def strip_comments(t):
    out = []
    for line in t.split("\n"):
        # 找到未转义的 %
        i, n = 0, len(line)
        while i < n:
            if line[i] == '%' and (i == 0 or line[i-1] != '\\'):
                line = line[:i]
                break
            i += 1
        out.append(line)
    return "\n".join(out)

# ---------- 主转换 ----------

class Conv:
    def __init__(self, name, chap):
        self.name, self.chap = name, chap
        self.tokens = {}   # token -> markdown 替换文本
        self.tikz_jobs = []  # (fname, snippet)
        self.raster_jobs = []  # (source, fname), 仅复制原创图与配套程序截图
        self.cnt = {"fig": 0, "tab": 0, "lst": 0}
        self.missing_ref = set()

    def tok(self, md):
        k = "QQTOK%03dQQ" % len(self.tokens)
        self.tokens[k] = md
        return "\n\n%s\n\n" % k

    def num(self, kind, label):
        self.cnt[kind] += 1
        if label and label in AUXMAP:
            return AUXMAP[label]
        return "%s.%d" % (self.chap, self.cnt[kind])

    # ---- lstlisting ----
    def extract_lst(self, t):
        out = []
        pos = 0
        while True:
            r = find_env(t, "lstlisting", pos)
            if not r:
                out.append(t[pos:]); break
            b, e2 = r
            out.append(t[pos:b])
            block = t[b:e2]
            body_start = block.index("}") + 1  # after \begin{lstlisting}
            opts = ""
            if block[body_start] == "[":
                ob = block.index("]", body_start)
                opts = block[body_start+1:ob]
                body_start = ob + 1
            body = block[body_start:block.rindex(r"\end{lstlisting}")]
            body = body.strip("\n")
            lang = ""
            mo = re.search(r"language=([A-Za-z]+)", opts)
            if mo:
                lang = LANG_MAP.get(mo.group(1).lower(), mo.group(1).lower())
            cap = ""
            mo = re.search(r"caption=\{", opts)
            if mo:
                cap, _ = balanced(opts, mo.end()-1)
            lab = ""
            mo = re.search(r"label=\{?([A-Za-z0-9:_-]+)\}?", opts)
            if mo:
                lab = mo.group(1)
            n = self.num("lst", lab)
            cap = latex_inline_to_md(cap)
            head = "**清单 %s  %s**\n\n" % (n, cap) if cap else "**清单 %s**\n\n" % n
            fence = "````" if "```" in body else "```"
            md = head + "%s%s\n%s\n%s" % (fence, lang, body, fence)
            out.append(self.tok(md))
            pos = e2
        return "".join(out)

    # ---- figure ----
    def raster_source(self, tex_path):
        rel = pathlib.Path(tex_path.replace(r"\_", "_").replace("\\", "/"))
        if not rel.parts or rel.parts[0] != "images":
            rel = pathlib.Path("images") / rel
        allowed = {("images", "generated"), ("images", "runtime")}
        if tuple(rel.parts[:2]) not in allowed or rel.suffix.lower() != ".png":
            raise ValueError("网站栅格图仅允许 images/generated 或 images/runtime 下的 PNG: " + tex_path)
        source = (SRC.parent / rel).resolve()
        if not source.is_relative_to((SRC.parent / rel.parts[0] / rel.parts[1]).resolve()):
            raise ValueError("栅格图路径越界: " + tex_path)
        if not source.is_file():
            raise FileNotFoundError(source)
        return source

    def copy_rasters(self, dest):
        if self.raster_jobs:
            image_dir = dest.parent / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            for source, fname in self.raster_jobs:
                target = image_dir / fname
                data = source.read_bytes()
                if not target.is_file() or target.read_bytes() != data:
                    target.write_bytes(data)

    def extract_fig(self, t):
        out, pos = [], 0
        while True:
            r = find_env(t, "figure", pos)
            if not r:
                out.append(t[pos:]); break
            b, e2 = r
            out.append(t[pos:b])
            block = t[b:e2]
            cap = ""
            mo = re.search(r"\\caption\s*(?:\[[^\]]*\]\s*)?\{", block)
            if mo:
                cap, _ = balanced(block, mo.end()-1)
            lab = ""
            mo = re.search(r"\\label\{([^}]+)\}", block)
            if mo:
                lab = mo.group(1)
            n = self.num("fig", lab)
            cap = latex_inline_to_md(cap)
            # includegraphics?
            graphics = graphics_paths(block)
            for path in graphics:
                if "51wim" in path.lower():
                    web = WEBFIGS / (pathlib.Path(path).stem + ".tex")
                    if not web.is_file():
                        raise FileNotFoundError("51WIM 授权截图缺少网站重绘替代，禁止复制: " + path)
            rr = find_env(block, "tikzpicture")
            if graphics and rr:
                # Keep portraits, exact connectors and labels in one composed SVG.
                snippet = block[rr[0]:rr[1]]
                if graphics_paths(snippet) != graphics:
                    raise ValueError("混合图的全部图片必须位于同一个 TikZ 环境内: " + (lab or n))
                graphics_dependencies(snippet, SRC.parent)
                fname = "%s_fig_%s.svg" % (self.name, n.replace(".", "_"))
                self.tikz_jobs.append((fname, snippet))
                imgs = ["images/" + fname]
            elif graphics:
                imgs, has_licensed = [], False
                for i, path in enumerate(graphics, 1):
                    suffix = "_%d" % i if len(graphics) > 1 else ""
                    fname = "%s_fig_%s%s" % (self.name, n.replace(".", "_"), suffix)
                    if "51wim" in path.lower():
                        # 授权截图仅限纸质/PDF版，线上只排入重绘任务。
                        web = WEBFIGS / (pathlib.Path(path).stem + ".tex")
                        fname += ".svg"
                        self.tikz_jobs.append((fname, web.read_text(encoding="utf-8")))
                        has_licensed = True
                    else:
                        fname += ".png"
                        self.raster_jobs.append((self.raster_source(path), fname))
                    imgs.append("images/" + fname)
                if has_licensed:
                    cap = re.sub(r"（图片来源：[^）]*）", "", cap) + "（教学示意图，界面布局据51WIM产品重绘；产品截图经授权仅刊于纸质版）"
            else:
                # tikzpicture 或宏调用
                rr = find_env(block, "tikzpicture")
                if rr:
                    snippet = block[rr[0]:rr[1]]
                else:
                    mo2 = re.search(r"\\(uavObliquePhotographySystem|obliqueImagePreprocessQC)", block)
                    snippet = "\\" + mo2.group(1) if mo2 else None
                if snippet is None:
                    out.append(self.tok("*<!-- 图 %s 未能提取 -->*" % n))
                    pos = e2; continue
                fname = "%s_fig_%s.svg" % (self.name, n.replace(".", "_"))
                self.tikz_jobs.append((fname, snippet))
                imgs = ["images/" + fname]
            images_md = "\n\n".join("![图%s](%s)" % (n, img) for img in imgs)
            md = "<figure markdown>\n%s\n<figcaption>图 %s  %s</figcaption>\n</figure>" % (images_md, n, cap)
            out.append(self.tok(md))
            pos = e2
        return "".join(out)

    # ---- table ----
    def extract_tab(self, t):
        out, pos = [], 0
        while True:
            r = find_env(t, "table", pos)
            if not r:
                out.append(t[pos:]); break
            b, e2 = r
            out.append(t[pos:b])
            block = t[b:e2]
            cap = ""
            mo = re.search(r"\\caption\s*(?:\[[^\]]*\]\s*)?\{", block)
            if mo:
                cap, _ = balanced(block, mo.end()-1)
            lab = ""
            mo = re.search(r"\\label\{([^}]+)\}", block)
            if mo:
                lab = mo.group(1)
            n = self.num("tab", lab)
            cap = latex_inline_to_md(cap)
            rr = find_env(block, "tabular")
            tab_tex = block[rr[0]:rr[1]] if rr else ""
            head = "**表 %s  %s**" % (n, cap) if cap else "**表 %s**" % n
            out.append("\n\n" + self.tok(head).strip("\n") + "\n\n" + tab_tex + "\n\n")
            pos = e2
        return "".join(out)

    # ---- boxes ----
    def mark_boxes(self, t):
        for env, (cls, title) in BOXES.items():
            t = t.replace("\\begin{%s}" % env, "\n\nQQBOXS%sQQ\n\n" % cls)
            t = t.replace("\\end{%s}" % env, "\n\nQQBOXEQQ\n\n")
        return t

    # ---- refs & cites ----
    def replace_refs(self, t):
        def rref(mo):
            lab = mo.group(1)
            if lab in AUXMAP:
                return AUXMAP[lab]
            self.missing_ref.add(lab)
            return "?"
        t = re.sub(r"\\ref\{([^}]+)\}", rref, t)
        t = re.sub(r"\\cite\{([^}]+)\}", lambda m: "QQCITE:%s:QQ" % m.group(1), t)
        return t

    def protect_inline_quotes(self, t):
        # Pandoc 3.1 会把 texttt 内的单引号排成弯引号；仅保护代码内的字面引号。
        out, pos = [], 0
        for mo in re.finditer(r"\\texttt\s*\{", t):
            if mo.start() < pos:
                continue  # 外层 texttt 已覆盖的嵌套内容。
            body, end = balanced(t, mo.end() - 1)
            out.append(t[pos:mo.end()])
            for quote in ("'", '"'):
                if quote in body:
                    body = body.replace(quote, self.tok(quote).strip("\n"))
            out.append(body + "}")
            pos = end
        out.append(t[pos:])
        return "".join(out)

    def run(self, texpath):
        t = texpath.read_text(encoding="utf-8")
        t = expand_case_params(t)        # 案例参数宏先展开为数值
        t = self.extract_lst(t)          # 先取代码,避免注释剥离伤及代码
        t = strip_comments(t)
        t = flatten_shortstack(t)
        t = self.extract_fig(t)
        t = self.extract_tab(t)
        t = self.mark_boxes(t)
        t = self.replace_refs(t)
        t = misc_tex_fix(t)
        t = self.protect_inline_quotes(t)
        pre = ROOT / ("pre_%s.tex" % self.name)
        pre.write_text(t, encoding="utf-8")
        md = subprocess.run(
            ["pandoc", "-f", "latex", "-t", "gfm+tex_math_dollars", "--wrap=none", str(pre)],
            capture_output=True, text=True)
        if md.returncode != 0 and "tex_math_dollars" in md.stderr:
            # 旧版 pandoc（<2.10）不认识该扩展；gfm 默认已保留 $…$ 数学
            md = subprocess.run(
                ["pandoc", "-f", "latex", "-t", "gfm", "--wrap=none", str(pre)],
                capture_output=True, text=True)
        if md.returncode != 0:
            print("PANDOC FAIL", self.name, md.stderr[:2000]); sys.exit(1)
        out = md.stdout
        out = self.post(out)
        return out

    # ---- markdown 后处理 ----
    def post(self, md):
        lines = md.split("\n")
        # 1) 标题编号(preface/appendix 跳过)
        if isinstance(self.chap, int) and self.chap > 0:
            sec = sub = sss = 0
            for i, ln in enumerate(lines):
                if ln.startswith("## ") and not ln.startswith("###"):
                    sec += 1; sub = 0; sss = 0
                    lines[i] = "## %d.%d %s" % (self.chap, sec, ln[3:].strip())
                elif ln.startswith("### ") and not ln.startswith("####"):
                    sub += 1; sss = 0
                    lines[i] = "### %d.%d.%d %s" % (self.chap, sec, sub, ln[4:].strip())
                elif ln.startswith("#### ") and not ln.startswith("#####"):
                    sss += 1
                    lines[i] = "#### %d.%d.%d.%d %s" % (self.chap, sec, sub, sss, ln[5:].strip())
        # 章标题
        for i, ln in enumerate(lines):
            if ln.startswith("# "):
                if isinstance(self.chap, int) and self.chap > 0:
                    lines[i] = "# 第%d章 %s" % (self.chap, ln[2:].strip())
                break
        # \paragraph -> 加粗行
        for i, ln in enumerate(lines):
            if ln.startswith("##### "):
                lines[i] = "**%s**" % ln[6:].strip()
        md = "\n".join(lines)
        # 2) 盒子 -> admonition
        md = self.boxes_to_admonitions(md)
        # 3) token 替换
        for k, v in self.tokens.items():
            md = md.replace(k, v)
        # 4) cite
        md = re.sub(r"QQCITE:([^:]+):QQ", cite_md, md)
        # 清理多余空行
        md = re.sub(r"\n{3,}", "\n\n", md)
        return md

    def boxes_to_admonitions(self, md):
        out = []
        box = None
        for ln in md.split("\n"):
            s = ln.strip()
            mo = re.match(r"QQBOXS(\w+)QQ", s)
            if mo:
                box = mo.group(1)
                title = {"tip": "提示", "note": "说明", "warning": "注意", "danger": "重要"}[box]
                out.append('!!! %s "%s"' % (box, title))
                out.append("")
                continue
            if s == "QQBOXEQQ":
                box = None
                continue
            if box:
                if ln.startswith("#### ") or ln.startswith("##### "):
                    ln = "**%s**" % ln.lstrip("#").strip()
                out.append(("    " + ln) if ln.strip() else "")
            else:
                out.append(ln)
        return "\n".join(out)

# ---------- 行内 LaTeX 简化(用于 caption 等) ----------

def latex_inline_to_md(s):
    s = re.sub(r"\\texttt\{([^}]*)\}", r"`\1`", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", s)
    s = re.sub(r"\\textit\{([^}]*)\}", r"*\1*", s)
    s = re.sub(r"\\ref\{([^}]+)\}", lambda m: AUXMAP.get(m.group(1), "?"), s)
    s = s.replace(r"\%", "%").replace(r"\&", "&").replace(r"\_", "_").replace(r"\#", "#")
    s = re.sub(r"\$([^$]*)\$", r"\1", s)
    s = s.replace(r"\rightarrow", "→").replace(r"\leq", "≤").replace(r"\geq", "≥")
    s = re.sub(r"\\[a-zA-Z]+ ?", "", s)
    return s.strip()

def misc_tex_fix(t):
    t = expand_enumerate_resume(t)
    t = t.replace(r"\htmltag{", r"\texttt{<")  # 粗略: 后面手查
    t = re.sub(r"\\code\{", r"\\texttt{", t)
    t = re.sub(r"\\label\{[^}]*\}", "", t)  # 编号已由 aux 解析,标签一律清除
    t = t.replace("~", " ")
    return t


def expand_enumerate_resume(t):
    """把 enumitem 的 resume 转成 Pandoc 可识别的标准计数器命令。"""
    pattern = re.compile(
        r"\\(?P<edge>begin|end)\{(?P<env>enumerate|itemize|description)\}"
        r"(?P<opts>\[[^\]]*\])?|\\item\b(?P<label>\s*\[[^\]]*\])?")
    stack, previous = [], {}

    def replace(m):
        env, edge = m.group("env"), m.group("edge")
        if edge == "begin":
            depth = 1 + sum(x["env"] == "enumerate" for x in stack)
            resume = env == "enumerate" and (m.group("opts") or "") == "[resume]"
            count = previous.get(depth, 0) if resume else 0
            stack.append({"env": env, "depth": depth, "count": count})
            if resume:
                counter = ("enumi", "enumii", "enumiii", "enumiv")[depth - 1]
                return r"\begin{enumerate}" + "\n" + r"\setcounter{%s}{%d}" % (counter, count)
        elif edge == "end":
            if stack and stack[-1]["env"] == env:
                item = stack.pop()
                if env == "enumerate":
                    previous[item["depth"]] = item["count"]
        elif stack and stack[-1]["env"] == "enumerate" and not m.group("label"):
            stack[-1]["count"] += 1
        return m.group(0)

    return pattern.sub(replace, t)

# ---------- 参考文献 ----------

def parse_bib():
    txt = (REPO / "output" / "references.bib").read_text(encoding="utf-8")
    entries = {}
    for mo in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", txt):
        typ, key = mo.group(1).lower(), mo.group(2)
        start = mo.end()
        depth, j = 1, txt.index("{", mo.start())
        j += 1
        while depth > 0 and j < len(txt):
            if txt[j] == "{": depth += 1
            elif txt[j] == "}": depth -= 1
            j += 1
        body = txt[mo.end():j-1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{", body):
            try:
                val, _ = balanced(body, fm.end()-1)
            except Exception:
                continue
            fields[fm.group(1).lower()] = re.sub(r"[{}]", "", val).replace("\n", " ").strip()
        entries[key] = (typ, fields)
    return entries

BIB = None
CITE_ORDER = []   # keys in first-cite order

def cite_md(mo):
    keys = [k.strip() for k in mo.group(1).split(",")]
    parts = []
    for k in keys:
        if k not in CITE_ORDER:
            CITE_ORDER.append(k)
        n = CITE_ORDER.index(k) + 1
        parts.append("[[%d]](%s#ref%d)" % (n, REFPATH, n))
    return "<sup>%s</sup>" % "".join(parts)

REFPATH = "../../references.md"

def fmt_ref(n, key):
    if key not in BIB:
        return "[%d] %s（bib 中未找到）" % (n, key)
    typ, f = BIB[key]
    au = f.get("author", f.get("organization", f.get("institution", "")))
    au = au.replace(" and ", ", ")
    ti = f.get("title", key)
    yr = f.get("year", f.get("date", ""))[:4]
    tail = ""
    if typ == "article":
        tail = "%s, %s" % (f.get("journal", f.get("journaltitle", "")), yr)
        if f.get("volume"): tail += ", %s" % f["volume"]
        if f.get("number"): tail += "(%s)" % f["number"]
        if f.get("pages"): tail += ": %s" % f["pages"]
        mark = "[J]"
    elif typ == "book":
        tail = "%s: %s, %s" % (f.get("address", f.get("location", "")), f.get("publisher", ""), yr)
        mark = "[M]"
    elif typ in ("online", "electronic", "misc") and (f.get("url") or f.get("howpublished")):
        tail = "%s" % (f.get("url", f.get("howpublished", "")))
        mark = "[EB/OL]"
    elif typ in ("techreport", "standard"):
        tail = "%s, %s" % (f.get("institution", f.get("organization", "")), yr)
        mark = "[S]"
    else:
        tail = yr
        mark = ""
    s = "%s. %s%s. %s" % (au, ti, mark, tail) if au else "%s%s. %s" % (ti, mark, tail)
    s = re.sub(r"\s+", " ", s).strip().rstrip(",. ") + "."
    if f.get("url") and typ not in ("online", "electronic", "misc"):
        s += " <%s>" % f["url"]
    return s

# ---------- main ----------

def main():
    global BIB
    BIB = parse_bib()
    OUT.mkdir(parents=True, exist_ok=True)
    TIKZ.mkdir(exist_ok=True)
    report = {}
    expected_jobs = []
    preamble = (HERE / "preamble.tex").read_text(encoding="utf-8")
    definitions = (REPO / "output/tikz-diagrams.tex").read_text(encoding="utf-8")
    only = sys.argv[1:] or None
    for name, chap in CHAPTERS:
        if only and name not in only:
            continue
        src = APPENDIX if name == "answers" else APPENDIX_B if name == "prep" else APPENDIX_C if name == "extended" else SRC / (name + ".tex")
        global REFPATH
        REFPATH = {"preface": "references.md", "answers": "../references.md", "prep": "../references.md", "extended": "../references.md"}.get(name, "../../references.md")
        c = Conv(name, chap)
        md = c.run(src)
        # 输出路径
        if name == "preface":
            dest = OUT / "前言.md"
        elif name == "answers":
            dest = OUT / "appendix" / "answers.md"
        elif name == "prep":
            dest = OUT / "appendix" / "prep.md"
        elif name == "extended":
            dest = OUT / "appendix" / "extended.md"
        else:
            dest = OUT / "chapters" / name / (name + ".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        c.copy_rasters(dest)
        # 保持现有docs的CRLF约定，避免不同平台重新生成时改动整份文件。
        dest.write_text(md, encoding="utf-8", newline="\r\n")
        for fname, snip in c.tikz_jobs:
            dependencies = graphics_dependencies(snip, SRC.parent)
            (TIKZ / (fname[:-4] + ".tex")).write_text(snip, encoding="utf-8", newline="\n")
            job = {"file": fname, "source_sha256": source_hash(snip, preamble, definitions, dependencies)}
            if dependencies:
                job["graphics_sha256"] = dependencies
            expected_jobs.append(job)
        if name.startswith("chapter"):
            active_images = {fname for fname, _ in c.tikz_jobs} | {fname for _, fname in c.raster_jobs}
            image_dir = dest.parent / "images"
            if image_dir.is_dir():
                for old in image_dir.iterdir():
                    if re.fullmatch(r"chapter\d+_fig_[\d_]+\.(?:svg|png)", old.name) and old.name not in active_images:
                        old.unlink()
        report[name] = {"figs": c.cnt["fig"], "tabs": c.cnt["tab"], "lsts": c.cnt["lst"],
                        "tikz": len(c.tikz_jobs), "raster": len(c.raster_jobs),
                        "missing_ref": sorted(c.missing_ref)}
    # 参考文献页
    refs = ["# 参考文献", ""]
    for i, k in enumerate(CITE_ORDER, 1):
        refs.append('<a id="ref%d"></a>[%d] %s' % (i, i, fmt_ref(i, k)))
        refs.append("")
    (OUT / "references.md").write_text("\n".join(refs), encoding="utf-8", newline="\r\n")
    (TIKZ / "expected-jobs.json").write_text(json.dumps(expected_jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    # 图号会随增图改变；文件名相同也必须核对当前图源和共享定义。
    n, pending = 0, 0
    for job in expected_jobs:
        fname = job["file"]
        ch = fname.split("_")[0]
        d = OUT / "chapters" / ch / "images"
        d.mkdir(parents=True, exist_ok=True)
        svg = verified_svg(TIKZ, fname, job["source_sha256"])
        if svg is None:
            (d / fname).unlink(missing_ok=True)
            pending += 1
        else:
            target = d / fname
            data = svg.read_bytes()
            if not target.is_file() or target.read_bytes() != data:
                target.write_bytes(data)
            n += 1
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("cited keys:", len(CITE_ORDER), "| verified SVG distributed:", n, "| pending rebuild:", pending)

if __name__ == "__main__":
    main()
