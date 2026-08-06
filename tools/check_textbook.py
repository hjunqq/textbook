#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教材扩写/修订的机器门禁。

    python tools/check_textbook.py              # 默认：不得倒退模式
    python tools/check_textbook.py --build      # 额外跑完整编译并检查日志
    python tools/check_textbook.py --report     # 只出报表，永远 exit 0
    python tools/check_textbook.py --strict     # 严格模式：所有指标必须归零（M1/终验用）
    python tools/check_textbook.py --init-baseline   # 写字数基线（只在启动时跑一次）
    python tools/check_textbook.py --init-gate       # 写软指标基线（只在启动时跑一次）

两类检查：

  硬失败（任何时候都不允许，一票否决）
    · 任何文件的正文汉字数低于 tools/wordcount_baseline.json
    · 环境未配对、悬空 \\ref、重复 label
    · 参考文献表有未引用条目或引用了不存在的键
    · 编译出现 Error / 未定义引用 / Overfull / 缺字

  软指标（存量问题，只要不比 tools/gate_baseline.json 更差就放行）
    · 未被 \\ref 引用的图表公式 label 数
    · 改稿批注残留处数
    · 缺失的章末要件数
    · 代码清单缺口、图缺口、载体密度缺口

这样设计的原因：全书有 86 个未引用 label、21 处改稿批注这类存量问题，
要到 O6、O5 以及整个 A 批做完才可能归零。若一开始就要求全零，
每个工作包都无法提交。改为"不得倒退"后，每一步只需保证自己不制造新问题、
并把本包负责的那部分往下压。M1 与终验时用 --strict 要求全部归零。
"""

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
CHAP = os.path.join(OUT, "chapters")
BASELINE = os.path.join(ROOT, "tools", "wordcount_baseline.json")
GATEFILE = os.path.join(ROOT, "tools", "gate_baseline.json")

FILES = [
    "preface.tex", "chapter01.tex", "chapter02.tex", "chapter03.tex",
    "chapter04.tex", "chapter05.tex", "chapter06.tex", "chapter07.tex",
    "chapter08.tex", "chapter09.tex",
]

# ── 终局目标：全书正文 200,000 汉字（不含代码清单与 TikZ 内部文字）──
TARGET = {
    "preface.tex":   2500,
    "chapter01.tex": 12000,
    "chapter02.tex": 20000,
    "chapter03.tex": 34000,
    "chapter04.tex": 26000,
    "chapter05.tex": 26000,
    "chapter06.tex": 28000,
    "chapter07.tex": 20000,
    "chapter08.tex": 26000,
    "chapter09.tex":  5500,
}

MIN_LISTINGS = {
    "chapter03.tex": 6, "chapter04.tex": 26, "chapter05.tex": 26,
    "chapter06.tex": 14, "chapter07.tex": 14, "chapter08.tex": 22,
}
MIN_FIGURES = {
    "chapter01.tex": 4, "chapter02.tex": 7, "chapter03.tex": 9,
    "chapter04.tex": 5, "chapter05.tex": 5, "chapter06.tex": 12,
    "chapter07.tex": 8, "chapter08.tex": 14,
}

EDITORIAL_FAIL = [
    (r"原稿", "出现『原稿』二字"),
    (r"不再(混用|使用|堆叠|重复绘制)", "『不再…』式改稿批注"),
    (r"不能写成", "『不能写成…』式改稿批注"),
    (r"不应(表述|写成)", "『不应表述/写成…』式改稿批注"),
    (r"过时表述", "『过时表述』"),
    (r"没有省略(语法|结构)", "自证式表述"),
    (r"不存在未闭合", "自证式表述"),
    (r"未获书面授权", "面向法务的自辩句"),
    (r"本节不再", "『本节不再…』式改稿批注"),
]
EDITORIAL_WARN = [
    (r"本教材(把|不复刻|据此采用)", "编者自述式表述，请确认面向学生还是面向审稿人"),
    (r"而不是[“\"]", "否定式排比，密集出现时改为直陈"),
]

REQUIRED_SECTIONS = ["学习目标", "小结", "习题"]
EXEMPT_REQUIRED = set()

CJK = re.compile(r"[\u4e00-\u9fff]")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_code(text):
    text = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", "", text, flags=re.S)
    text = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", "", text, flags=re.S)
    text = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", "", text, flags=re.S)
    text = re.sub(r"%.*", "", text)
    return text


def body_chars(text):
    return len(CJK.findall(strip_code(text)))


class Result:
    def __init__(self):
        self.fails = []
        self.warns = []
        self.lines = []
        self.metrics = {}
        self.labels = {}

    def fail(self, m):
        self.fails.append(m)

    def warn(self, m):
        self.warns.append(m)

    def log(self, m):
        self.lines.append(m)

    def metric(self, key, value, label):
        self.metrics[key] = value
        self.labels[key] = label


def check_wordcount(texts, r, init):
    cur = {f: body_chars(t) for f, t in texts.items()}
    total = sum(cur.values())
    if init:
        os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
        json.dump(cur, open(BASELINE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        r.log("已写入字数基线 tools/wordcount_baseline.json")
        return
    base = json.load(open(BASELINE, encoding="utf-8")) if os.path.exists(BASELINE) else {}
    if not base:
        r.warn("缺少 tools/wordcount_baseline.json，防删除检查未生效")
    r.log("")
    r.log("正文汉字数（不含代码清单与 TikZ）")
    r.log("%-16s %8s %8s %8s %8s %7s" % ("文件", "基线", "当前", "增量", "目标", "完成度"))
    for f in FILES:
        c, b, t = cur.get(f, 0), base.get(f, 0), TARGET[f]
        r.log("%-16s %8d %8d %+8d %8d %6d%%" % (f, b, c, c - b, t, round(100.0 * c / t)))
        if base and c < b:
            r.fail("【防删除】%s 正文汉字 %d < 基线 %d，净减少 %d 字。本方案只允许增写；"
                   "确需删除的段落必须在提交说明中逐段列出原文并说明替代内容。"
                   % (f, c, b, b - c))
    tb, tt = sum(base.values()) if base else 0, sum(TARGET.values())
    r.log("%-16s %8d %8d %+8d %8d %6d%%"
          % ("合计", tb, total, total - tb, tt, round(100.0 * total / tt)))


def check_refs(texts, r):
    labels, refs, dup = [], [], []
    for t in texts.values():
        for l in re.findall(r"\\label\{([^}]*)\}", t):
            if l in labels:
                dup.append(l)
            labels.append(l)
        refs += re.findall(r"\\(?:ref|autoref|eqref|pageref)\{([^}]*)\}", t)
    if dup:
        r.fail("重复 label：%s" % ", ".join(sorted(set(dup))))
    dangling = sorted(set(refs) - set(labels))
    if dangling:
        r.fail("悬空引用（\\ref 无对应 \\label）：%s" % ", ".join(dangling))
    # 随文引出：每个图/表/公式的 \\label 必须在它自己前后 PROX 行以内被 \\ref 到。
    # 这条直接编码"读者读到这段话时图就在附近"，章末集中罗列无法满足，
    # 因此不存在低成本的替代满足方式。
    PROX = 40
    far = []
    for f, t in texts.items():
        lines = t.split("\n")
        refpos = {}
        for i, line in enumerate(lines):
            for k in re.findall(r"\\(?:ref|autoref|eqref)\{([^}]*)\}", line):
                refpos.setdefault(k, []).append(i)
        env, envline = None, 0
        for i, line in enumerate(lines):
            m = re.search(r"\\begin\{(figure|table|longtable|equation)\*?\}", line)
            if m:
                env, envline = m.group(1), i
            if re.search(r"\\end\{(figure|table|longtable|equation)\*?\}", line):
                env = None
            for k in re.findall(r"\\label\{([^}]*)\}", line):
                if env is None and not k.startswith(("fig:", "tab:", "eq:")):
                    continue
                near = any(abs(p - i) <= PROX for p in refpos.get(k, []))
                if not near:
                    far.append("%s:%d %s" % (f, i + 1, k))
    if far:
        r.fail("以下 %d 个图/表/公式没有在自己前后 %d 行以内被正文引出：\n    %s\n"
               "  图表必须在讨论它的那一段附近引出（『……具体差异见表\\ref{...}』），"
               "章末集中罗列不算。若某个图表在正文中确实没有对应讨论，"
               "说明那是内容缺口，列出来交给对应的 A 系列工作包补正文，不要硬塞引导语。"
               % (len(far), PROX, "\n    ".join(far[:40])
                  + ("\n    …另有 %d 个" % (len(far) - 40) if len(far) > 40 else "")))
    # 反模板：引导语必须针对该图表本身，不能是一句套话到处盖章。
    # 把每个含 \\ref 的句子抽出来、抹掉 label 后归一化，同一句话复用 3 次以上即判失败。
    import collections
    forms = collections.Counter()
    where = {}
    for f, t in texts.items():
        for i, line in enumerate(t.split("\n")):
            if not re.search(r"\\(?:ref|autoref|eqref)\{", line):
                continue
            for sent in re.split(r"[。；]", line):
                if not re.search(r"\\(?:ref|autoref|eqref)\{", sent):
                    continue
                norm = re.sub(r"\\(?:ref|autoref|eqref)\{[^}]*\}", "@", sent)
                norm = re.sub(r"[\s\\{}]|\\textit|\\emph|[0-9]", "", norm)
                if len(norm) < 12:
                    continue
                forms[norm] += 1
                where.setdefault(norm, []).append("%s:%d" % (f, i + 1))
    dup = [(n, c) for n, c in forms.items() if c >= 3]
    if dup:
        msg = []
        for n, c in sorted(dup, key=lambda x: -x[1])[:6]:
            msg.append("  用了 %d 次：%s…\n    出现在：%s"
                       % (c, n[:44], "、".join(where[n][:6])))
        r.fail("检出 %d 种模板化引导语被反复套用：\n%s\n"
               "  引导语必须说明这一张图/表要回答什么问题，因此不同图表的引导语必然不同。"
               "同一句话盖在多个图表上，等于没有引出。"
               % (len(dup), "\n".join(msg)))

    unref = sorted(l for l in labels
                   if l not in refs and not l.startswith(("ch:", "sec:", "lst:")))
    r.metric("unref_labels", len(unref), "未被 \\ref 引用的图/表/公式 label")
    r.log("\nlabel 总数 %d，被引用 %d，待补 \\ref %d 个" % (len(labels), len(set(refs)), len(unref)))
    if unref:
        r.log("  " + "、".join(unref[:12]) + (" …" if len(unref) > 12 else ""))


def check_envs(texts, r):
    for f, t in texts.items():
        for env in ("lstlisting", "figure", "table", "tikzpicture", "enumerate",
                    "itemize", "equation", "tabular", "longtable"):
            b = len(re.findall(r"\\begin\{%s\}" % env, t))
            e = len(re.findall(r"\\end\{%s\}" % env, t))
            if b != e:
                r.fail("%s 的 %s 环境未配对：begin=%d end=%d" % (f, env, b, e))


def check_density(texts, r):
    dl = df = 0
    lines = []
    for f, t in texts.items():
        n = len(re.findall(r"\\begin\{lstlisting\}", t))
        need = MIN_LISTINGS.get(f)
        if need and n < need:
            dl += need - n
            lines.append("  %s 代码清单 %d/%d" % (f, n, need))
        nf = len(re.findall(r"\\begin\{figure\}", t))
        needf = MIN_FIGURES.get(f)
        if needf and nf < needf:
            df += needf - nf
            lines.append("  %s 图 %d/%d" % (f, nf, needf))
        for m in re.finditer(r"\\begin\{lstlisting\}(\[[^\]]*\])?", t):
            if "caption" not in (m.group(1) or ""):
                r.warn("%s 第 %d 行附近的代码清单缺 caption/label"
                       % (f, t[:m.start()].count("\n") + 1))
                break
    r.metric("listings_deficit", dl, "代码清单缺口")
    r.metric("figures_deficit", df, "图缺口")
    if lines:
        r.log("\n载体下限缺口：")
        r.lines.extend(lines)


def check_denseness(texts, r):
    deficit = 0
    for f in ("chapter04.tex", "chapter05.tex", "chapter06.tex",
              "chapter07.tex", "chapter08.tex"):
        t = texts[f]
        n = (len(re.findall(r"\\begin\{lstlisting\}", t))
             + len(re.findall(r"\\begin\{figure\}", t))
             + len(re.findall(r"\\begin\{table\}", t)))
        need = body_chars(t) // 1200
        if n < need:
            deficit += need - n
    r.metric("denseness_deficit", deficit, "载体密度缺口（每1200字1个）")


def check_editorial(texts, r):
    hits, soft = [], 0
    for f, t in texts.items():
        for i, line in enumerate(t.split("\n"), 1):
            for pat, why in EDITORIAL_FAIL:
                if re.search(pat, line):
                    hits.append("%s:%d [%s] %s" % (f, i, why, line.strip()[:60]))
            for pat, why in EDITORIAL_WARN:
                if re.search(pat, line):
                    soft += 1
    r.metric("editorial", len(hits), "改稿批注/编辑痕迹")
    if hits:
        r.log("\n待清理的改稿批注：")
        for h in hits[:10]:
            r.log("  " + h)
        if len(hits) > 10:
            r.log("  …另有 %d 处" % (len(hits) - 10))
    if soft:
        r.warn("另有 %d 处编者自述式/否定式排比表述，请人工判断语境" % soft)


def check_structure(texts, r):
    miss, lines = 0, []
    for f, t in texts.items():
        if f == "preface.tex" or f in EXEMPT_REQUIRED:
            continue
        for sec in REQUIRED_SECTIONS:
            if sec not in t:
                miss += 1
                lines.append("  %s 缺章末要件：%s" % (f, sec))
    r.metric("structure_missing", miss, "缺失的章末要件")
    if lines:
        r.log("")
        r.lines.extend(lines)


def check_bib(texts, r):
    bibp = os.path.join(OUT, "references.bib")
    if not os.path.exists(bibp):
        r.fail("找不到 references.bib")
        return
    keys = set(re.findall(r"@\w+\{([^,]+),", read(bibp)))
    cited = set()
    for t in texts.values():
        for c in re.findall(r"\\(?:cite|parencite|textcite|footcite)\{([^}]*)\}", t):
            cited |= {x.strip() for x in c.split(",")}
    if cited - keys:
        r.fail("引用了不存在的文献键：%s" % ", ".join(sorted(cited - keys)))
    if keys - cited:
        r.fail("参考文献表有 %d 条从未被引用：%s"
               % (len(keys - cited), ", ".join(sorted(keys - cited))))
    r.log("\n文献 %d 条，被引用 %d 条" % (len(keys), len(cited & keys)))


def check_build(r):
    for c in (["xelatex", "-interaction=nonstopmode", "main.tex"],
              ["biber", "main"],
              ["xelatex", "-interaction=nonstopmode", "main.tex"],
              ["xelatex", "-interaction=nonstopmode", "main.tex"]):
        try:
            p = subprocess.run(c, cwd=OUT, capture_output=True)
        except FileNotFoundError:
            r.warn("找不到 %s，跳过编译检查；编译验证请攒到里程碑统一做" % c[0])
            return
        if c[0] == "biber" and p.returncode != 0:
            r.fail("biber 执行失败：%s" % p.stdout.decode("utf-8", "ignore")[-300:])
    log = read(os.path.join(OUT, "main.log"))
    for pat, name in ((r"^! ", "Error"), (r"Overfull \\hbox", "Overfull hbox"),
                      (r"Overfull \\vbox", "Overfull vbox"),
                      (r"Missing character", "缺字"),
                      (r"There were undefined", "未定义引用/引文")):
        n = len(re.findall(pat, log, flags=re.M))
        if n:
            r.fail("编译日志中 %s：%d 处" % (name, n))
    m = re.search(r"Output written on \S+ \((\d+) pages\)", log)
    r.log("\n编译输出 %s 页" % (m.group(1) if m else "——未生成 PDF"))
    if not m:
        r.fail("未生成 PDF")


def judge_metrics(r, init_gate, strict):
    if init_gate:
        os.makedirs(os.path.dirname(GATEFILE), exist_ok=True)
        json.dump(r.metrics, open(GATEFILE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        r.log("\n已写入软指标基线 tools/gate_baseline.json：%s"
              % json.dumps(r.metrics, ensure_ascii=False))
        return
    base = json.load(open(GATEFILE, encoding="utf-8")) if os.path.exists(GATEFILE) else {}
    r.log("")
    r.log("存量问题（软指标，越小越好）")
    r.log("%-34s %8s %8s %8s" % ("指标", "起点", "当前", "变化"))
    for k, v in r.metrics.items():
        b = base.get(k)
        d = "" if b is None else "%+d" % (v - b)
        r.log("%-34s %8s %8d %8s" % (r.labels[k], "-" if b is None else b, v, d))
        if strict and v:
            r.fail("【严格模式】%s 仍有 %d 项未清零" % (r.labels[k], v))
        elif b is not None and v > b:
            r.fail("【倒退】%s 从 %d 涨到 %d。本轮只允许把存量往下压，"
                   "不允许制造新的同类问题。" % (r.labels[k], b, v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init-baseline", action="store_true")
    ap.add_argument("--init-gate", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    texts = {}
    for f in FILES:
        p = os.path.join(CHAP, f)
        if not os.path.exists(p):
            print("缺少文件：%s" % p)
            return 2
        texts[f] = read(p)

    r = Result()
    check_wordcount(texts, r, a.init_baseline)
    if not a.init_baseline:
        check_refs(texts, r)
        check_envs(texts, r)
        check_density(texts, r)
        check_denseness(texts, r)
        check_editorial(texts, r)
        check_structure(texts, r)
        check_bib(texts, r)
        if a.build:
            check_build(r)
        judge_metrics(r, a.init_gate, a.strict)

    print("\n".join(r.lines))
    if r.warns:
        print("\n提示（不阻断）：")
        for w in r.warns:
            print("  · " + w)
    if r.fails:
        print("\n不通过（%d 项）：" % len(r.fails))
        for i, x in enumerate(r.fails, 1):
            print("  %d. %s" % (i, x))
        print("\n以上未清零，禁止提交。不许通过删内容或放宽门禁阈值来过检。")
        return 0 if a.report else 1
    print("\n通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
