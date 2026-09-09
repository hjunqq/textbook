# -*- coding: utf-8 -*-
"""R2：按 tools/r0/sections.csv 的层次草标，在每个编号 \\section 开头写入
   \\paragraph{本节层次}……。幂等：已有该段落的节跳过。只处理 chapter01–09。"""
import csv, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "output", "chapters")
NAME = {"C": "核心", "G": "指导实践", "E": "拓展"}
rows = list(csv.DictReader(open(os.path.join(ROOT, "tools", "r0", "sections.csv"), encoding="utf-8-sig")))
by = {}
for r in rows:
    by.setdefault(r["chapter"], []).append(r)
HEAD = re.compile(r"^\\(section|subsection)\{([^}]*)\}")
total = 0
for chn in range(1, 10):
    ch = "ch%02d" % chn
    f = os.path.join(CH, "chapter%02d.tex" % chn)
    lines = open(f, encoding="utf-8").read().split("\n")
    # 建立标题 -> 层次
    sec_layer = {}
    sub_layers = {}
    cur = None
    for r in by[ch]:
        if r["level"] == "section":
            cur = r["title"]; sec_layer[cur] = r["layer"]; sub_layers[cur] = []
        elif r["level"] == "subsection" and cur:
            sub_layers[cur].append((r["title"], r["layer"]))
    out, si = [], 0
    i = 0
    while i < len(lines):
        line = lines[i]; out.append(line)
        m = HEAD.match(line)
        if m and m.group(1) == "section":
            si += 1
            title = m.group(2)
            if title in ("小结", "章末交付物", "思考题与练习题", "核心术语表") or sec_layer.get(title, "-") == "-":
                i += 1; continue
            # 已有则跳过
            if any("\\paragraph{本节层次}" in l for l in lines[i + 1:i + 8]):
                i += 1; continue
            subs = sub_layers.get(title, [])
            if subs:
                groups = {"C": [], "G": [], "E": []}
                for k, (t, l) in enumerate(subs, 1):
                    groups[l if l in groups else "C"].append("%d.%d.%d" % (chn, si, k))
                parts = ["%s：%s" % (NAME[k], "、".join(groups[k])) for k in ("C", "G", "E") if groups[k]]
                text = "；".join(parts) + "。"
                if groups["C"] and (groups["G"] or groups["E"]):
                    text += "核心路线只要求读完核心小节。"
                elif not groups["C"]:
                    text += "本节没有核心小节，课堂核心路线可整体跳过。"
            else:
                l = sec_layer.get(title, "C")
                text = NAME.get(l, "核心") + "。"
                if l == "E": text += "课堂核心路线可跳过。"
            out.append("")
            out.append("\\paragraph{本节层次}" + text)
            total += 1
        i += 1
    open(f, "w", encoding="utf-8").write("\n".join(out))
print("stamped", total)
