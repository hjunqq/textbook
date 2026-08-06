#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教材扩写/修订的机器门禁。
用法（在仓库根目录执行）：

    python tools/check_textbook.py                 # 全量检查，返回 0 表示通过
    python tools/check_textbook.py --init-baseline # 只在方案启动时执行一次，写基线
    python tools/check_textbook.py --build         # 额外执行完整编译并检查日志
    python tools/check_textbook.py --report        # 只出报表，不判定成败（exit 0）

设计目标：把"不许删内容""图表必须随文引出""改稿批注不许印出来"这类
人来判断很累、机器判断很准的规则固化成门禁。任何一条 FAIL，禁止 git commit。
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

# 各章代码清单数量下限（技术章必须有足量可读代码）
MIN_LISTINGS = {
    "chapter03.tex": 6, "chapter04.tex": 26, "chapter05.tex": 26,
    "chapter06.tex": 14, "chapter07.tex": 14, "chapter08.tex": 22,
}
# 各章图数量下限
MIN_FIGURES = {
    "chapter01.tex": 4, "chapter02.tex": 7, "chapter03.tex": 9,
    "chapter04.tex": 5, "chapter05.tex": 5, "chapter06.tex": 12,
    "chapter07.tex": 8, "chapter08.tex": 14,
}

# 改稿批注 / 编辑痕迹：这些模式一旦出现在正文，读者会莫名其妙
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
# 需人工确认语境的，只提示不阻断
EDITORIAL_WARN = [
    (r"本教材(把|不复刻|据此采用)", "编者自述式表述，请确认是面向学生还是面向审稿人"),
    (r"而不是[“\"]", "否定式排比，密集出现时改为直陈"),
]

# 必备章末要件（第9章若定为不编号结语可在 EXEMPT 中豁免）
REQUIRED_SECTIONS = ["学习目标", "小结", "习题"]
EXEMPT_REQUIRED = set()          # 例：{"chapter09.tex"}

CJK = re.compile(r"[\u4e00-\u9fff]")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_code(text):
    """去掉代码清单与 TikZ 内部文字，避免用代码注释刷字数。"""
    text = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", "", text, flags=re.S)
    text = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", "", text, flags=re.S)
    text = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", "", text, flags=re.S)
    text = re.sub(r"%.*", "", text)
    return text


def body_chars(text):
    return len(CJK.findall(strip_code(text)))


def count_env(text, name):
    b = len(re.findall(r"\\begin\{%s\}" % name, text))
    e = len(re.findall(r"\\end\{%s\}" % name, text))
    return b, e


class Result:
    def __init__(self):
        self.fails = []
        self.warns = []
        self.lines = []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def log(self, msg):
        self.lines.append(msg)


def check_wordcount(texts, r, init):
    cur = {f: body_chars(t) for f, t in texts.items()}
    total = sum(cur.values())
    if init:
        os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
        with open(BASELINE, "w", encoding="utf-8") as fh:
            json.dump(cur, fh, ensure_ascii=False, indent=2)
        r.log("已写入基线 tools/wordcount_baseline.json")
        return

    base = {}
    if os.path.exists(BASELINE):
        base = json.load(open(BASELINE, encoding="utf-8"))
    else:
        r.warn("缺少 tools/wordcount_baseline.json，无法执行防删除检查；请先 --init-baseline")

    r.log("")
    r.log("正文汉字数（不含代码清单与 TikZ）")
    r.log("%-16s %8s %8s %8s %8s %7s" % ("文件", "基线", "当前", "增量", "目标", "完成度"))
    for f in FILES:
        c, b, t = cur.get(f, 0), base.get(f, 0), TARGET[f]
        pct = "%d%%" % round(100.0 * c / t) if t else "-"
        r.log("%-16s %8d %8d %+8d %8d %7s" % (f, b, c, c - b, t, pct))
        # 铁律一：任何文件的正文字数不得低于基线
        if base and c < b:
            r.fail("【防删除】%s 正文汉字 %d < 基线 %d，净减少 %d 字。"
                   "本方案只允许增写；确需删除的段落必须在提交说明中逐段列出并说明替代内容。"
                   % (f, c, b, b - c))
    tb, tt = sum(base.values()) if base else 0, sum(TARGET.values())
    r.log("%-16s %8d %8d %+8d %8d %7s"
          % ("合计", tb, total, total - tb, tt, "%d%%" % round(100.0 * total / tt)))


def check_refs(texts, r):
    labels, refs, dup = [], [], []
    for f, t in texts.items():
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
    # 铁律二：图、表、公式必须随文引出
    unref = [l for l in labels if l not in refs and not l.startswith(("ch:", "sec:", "lst:"))]
    if unref:
        r.fail("以下 %d 个图/表/公式 label 从未被 \\ref 引用（教材编校要求图表必须随文引出，"
               "如『如图6-3所示』『见表8-4』）：\n    %s" % (len(unref), "\n    ".join(sorted(unref))))
    r.log("\nlabel 总数 %d，被引用 %d，未引用 %d" % (len(labels), len(set(refs)), len(unref)))


def check_envs(texts, r):
    for f, t in texts.items():
        for env in ("lstlisting", "figure", "table", "tikzpicture", "enumerate",
                    "itemize", "equation", "tabular", "longtable"):
            b, e = count_env(t, env)
            if b != e:
                r.fail("%s 的 %s 环境未配对：begin=%d end=%d" % (f, env, b, e))


def check_density(texts, r):
    for f, t in texts.items():
        n = len(re.findall(r"\\begin\{lstlisting\}", t))
        need = MIN_LISTINGS.get(f)
        if need and n < need:
            r.fail("%s 代码清单 %d 个 < 下限 %d 个" % (f, n, need))
        nf = len(re.findall(r"\\begin\{figure\}", t))
        needf = MIN_FIGURES.get(f)
        if needf and nf < needf:
            r.fail("%s 图 %d 幅 < 下限 %d 幅" % (f, nf, needf))
        # 代码清单必须带 caption/label，便于正文引用
        for m in re.finditer(r"\\begin\{lstlisting\}(\[[^\]]*\])?", t):
            opt = m.group(1) or ""
            if "caption" not in opt:
                r.warn("%s 第 %d 行附近的代码清单缺 caption/label"
                       % (f, t[:m.start()].count("\n") + 1))
                break


def check_editorial(texts, r):
    hits, soft = [], 0
    for f, t in texts.items():
        for i, line in enumerate(t.split("\n"), 1):
            for pat, why in EDITORIAL_FAIL:
                if re.search(pat, line):
                    hits.append("%s:%d  [%s]  %s" % (f, i, why, line.strip()[:70]))
            for pat, why in EDITORIAL_WARN:
                if re.search(pat, line):
                    soft += 1
    if hits:
        r.fail("检出 %d 处改稿批注/编辑痕迹（应改为面向学生的正面表述）：\n    %s"
               % (len(hits), "\n    ".join(hits)))
    if soft:
        r.warn("另有 %d 处编者自述式/否定式排比表述，请人工判断语境" % soft)


def check_denseness(texts, r):
    """反注水：技术章每 1200 正文汉字至少配 1 个代码清单、图或表。"""
    for f in ("chapter04.tex", "chapter05.tex", "chapter06.tex",
              "chapter07.tex", "chapter08.tex"):
        t = texts[f]
        n = (len(re.findall(r"\\begin\{lstlisting\}", t))
             + len(re.findall(r"\\begin\{figure\}", t))
             + len(re.findall(r"\\begin\{table\}", t)))
        need = body_chars(t) // 1200
        if n < need:
            r.fail("%s 载体密度不足：正文 %d 字仅配 %d 个代码清单/图/表，下限 %d 个。"
                   "新增内容必须带可运行代码、公式推导、数据表、反例或水利实例，"
                   "不得是纯文字铺陈。" % (f, body_chars(t), n, need))


def check_structure(texts, r):
    for f, t in texts.items():
        if f == "preface.tex" or f in EXEMPT_REQUIRED:
            continue
        for sec in REQUIRED_SECTIONS:
            if sec not in t:
                r.fail("%s 缺少章末要件：%s" % (f, sec))


def check_bib(texts, r):
    bibp = os.path.join(OUT, "references.bib")
    if not os.path.exists(bibp):
        r.fail("找不到 references.bib")
        return
    bib = read(bibp)
    keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cited = set()
    for t in texts.values():
        for c in re.findall(r"\\(?:cite|parencite|textcite|footcite)\{([^}]*)\}", t):
            cited |= {x.strip() for x in c.split(",")}
    if cited - keys:
        r.fail("引用了不存在的文献键：%s" % ", ".join(sorted(cited - keys)))
    if keys - cited:
        r.fail("参考文献表中有 %d 条从未被引用：%s"
               % (len(keys - cited), ", ".join(sorted(keys - cited))))
    r.log("\n文献 %d 条，被引用 %d 条" % (len(keys), len(cited & keys)))


def check_build(r):
    env = dict(os.environ)
    cmds = [["xelatex", "-interaction=nonstopmode", "main.tex"],
            ["biber", "main"],
            ["xelatex", "-interaction=nonstopmode", "main.tex"],
            ["xelatex", "-interaction=nonstopmode", "main.tex"]]
    for c in cmds:
        p = subprocess.run(c, cwd=OUT, capture_output=True, env=env)
        if c[0] == "biber" and p.returncode != 0:
            r.fail("biber 执行失败：%s" % p.stdout.decode("utf-8", "ignore")[-400:])
    log = read(os.path.join(OUT, "main.log"))
    for pat, name in [(r"^! ", "Error"), (r"Overfull \\hbox", "Overfull hbox"),
                      (r"Overfull \\vbox", "Overfull vbox"),
                      (r"Missing character", "缺字"),
                      (r"There were undefined", "未定义引用/引文")]:
        n = len(re.findall(pat, log, flags=re.M))
        if n:
            r.fail("编译日志中 %s：%d 处" % (name, n))
    m = re.search(r"Output written on \S+ \((\d+) pages\)", log)
    if m:
        r.log("\n编译输出 %s 页" % m.group(1))
    else:
        r.fail("未生成 PDF")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init-baseline", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--root", default=None)
    a = ap.parse_args()

    global ROOT, OUT, CHAP, BASELINE
    if a.root:
        ROOT = os.path.abspath(a.root)
        OUT = os.path.join(ROOT, "output")
        CHAP = os.path.join(OUT, "chapters")
        BASELINE = os.path.join(ROOT, "tools", "wordcount_baseline.json")

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
        check_editorial(texts, r)
        check_structure(texts, r)
        check_bib(texts, r)
        check_denseness(texts, r)
        if a.build:
            check_build(r)

    print("\n".join(r.lines))
    if r.warns:
        print("\n提示（不阻断）：")
        for w in r.warns:
            print("  · " + w)
    if r.fails:
        print("\n不通过（%d 项）：" % len(r.fails))
        for i, x in enumerate(r.fails, 1):
            print("  %d. %s" % (i, x))
        print("\n以上任意一项未清零，禁止提交。")
        return 0 if a.report else 1
    print("\n全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
