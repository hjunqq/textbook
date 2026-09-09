# -*- coding: utf-8 -*-
"""第九轮 R0 盘点：从 output/chapters/*.tex 生成
   tools/r0/sections.csv   小节层次草表（每个 section/subsection：字数、清单、图、表、公式）
   tools/r0/listings.csv   代码清单台账（203 项）
   tools/r0/params.md      案例参数宏与跨章引用
只读脚本，不改正文。"""
import re, os, csv, json, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "output", "chapters")
FILES = ["preface.tex"] + ["chapter%02d.tex" % i for i in range(1, 10)]
CJK = re.compile(r"[\u4e00-\u9fff]")
def strip_code(t):
    t = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", "", t, flags=re.S)
    t = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", "", t, flags=re.S)
    t = re.sub(r"%.*", "", t); return t
HEAD = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}")
allref = ""
for f in FILES: allref += open(os.path.join(CH, f), encoding="utf-8").read()
allref += open(os.path.join(ROOT,"output","main.tex"),encoding="utf-8").read()
refs = re.findall(r"\\(?:ref|pageref|autoref|eqref)\{([^}]*)\}", allref)
refcount = {}
for r in refs: refcount[r] = refcount.get(r, 0) + 1

sec_rows, lst_rows = [], []
for f in FILES:
    t = open(os.path.join(CH, f), encoding="utf-8").read()
    heads = [(m.start(), m.group(1), m.group(2)) for m in HEAD.finditer(t)]
    heads.append((len(t), None, None))
    ch = f.replace("chapter", "ch").replace(".tex", "")
    cur_sec = ""
    for i in range(len(heads) - 1):
        pos, lvl, title = heads[i]; end = heads[i + 1][0]
        body = t[pos:end]
        if lvl == "section": cur_sec = title
        n = len(CJK.findall(strip_code(body)))
        nl = len(re.findall(r"\\begin\{lstlisting\}", body))
        nf = len(re.findall(r"\\begin\{figure\}", body))
        nt = len(re.findall(r"\\begin\{table\}", body))
        ne = len(re.findall(r"\\begin\{(?:equation|align)", body))
        # 直接子内容（不含下级标题）字数
        sub = HEAD.search(body[1:])
        own = len(CJK.findall(strip_code(body[: sub.start() + 1] if sub else body)))
        sec_rows.append(dict(chapter=ch, level=lvl, section=cur_sec if lvl != "section" else "", title=title,
                             chars_total=n, chars_own=own, listings=nl, figures=nf, tables=nt, equations=ne, layer="", note=""))
        for m in re.finditer(r"\\begin\{lstlisting\}(\[[^\]]*\])?(.*?)\\end\{lstlisting\}", body, flags=re.S):
            opt = m.group(1) or ""
            code = m.group(2)
            lab = re.search(r"label=\{?([^,\]}]*)", opt); cap = re.search(r"caption=\{([^}]*)\}", opt)
            lang = re.search(r"language=\{?([^,\]}]*)", opt)
            lst_rows.append(dict(chapter=ch, section=(cur_sec if lvl != "section" else title), subsection=(title if lvl != "section" else ""),
                                 label=lab.group(1) if lab else "", caption=cap.group(1) if cap else "",
                                 language=lang.group(1) if lang else "", lines=len(code.strip("\n").splitlines()),
                                 refs=refcount.get(lab.group(1), 0) if lab else 0,
                                 has_imports=int(bool(re.search(r"^\s*(import |from |#include|using |package )", code, re.M))),
                                 category="", layer="", prereq="", run_entry="", disposition=""))
os.makedirs(os.path.join(ROOT, "tools", "r0"), exist_ok=True)
with open(os.path.join(ROOT, "tools", "r0", "sections.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(sec_rows[0].keys())); w.writeheader(); w.writerows(sec_rows)
with open(os.path.join(ROOT, "tools", "r0", "listings.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(lst_rows[0].keys())); w.writeheader(); w.writerows(lst_rows)
# 参数宏
cp = open(os.path.join(ROOT, "output", "case-params.tex"), encoding="utf-8").read()
macros = re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}", cp)
out = ["# 案例参数宏（output/case-params.tex）与跨章使用\n", "| 宏 | 值 | 使用章（次数） |", "|---|---|---|"]
for name, val in macros:
    uses = []
    for f in FILES:
        c = len(re.findall(r"\\" + name + r"\b", open(os.path.join(CH, f), encoding="utf-8").read()))
        if c: uses.append("%s(%d)" % (f.replace("chapter", "ch").replace(".tex", ""), c))
    out.append("| \\%s | %s | %s |" % (name, val.replace("|", "\\|"), " ".join(uses) or "—"))
# 8.1 节的表/图被其他章引用
ch8 = open(os.path.join(CH, "chapter08.tex"), encoding="utf-8").read()
s81 = ch8[: HEAD.search(ch8, HEAD.search(ch8).end()).start()]
labels81 = re.findall(r"\\label\{([^}]*)\}", s81)
out += ["\n# 8.1 节 label 被其他章引用情况\n", "| label | 引用章 |", "|---|---|"]
for lab in labels81:
    uses = []
    for f in FILES:
        if f == "chapter08.tex": continue
        c = len(re.findall(r"\\(?:ref|autoref|eqref)\{" + re.escape(lab) + r"\}", open(os.path.join(CH, f), encoding="utf-8").read()))
        if c: uses.append("%s(%d)" % (f.replace("chapter", "ch").replace(".tex", ""), c))
    out.append("| %s | %s |" % (lab, " ".join(uses) or "—"))
open(os.path.join(ROOT, "tools", "r0", "params.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("sections", len(sec_rows), "listings", len(lst_rows), "macros", len(macros), "labels81", len(labels81))
