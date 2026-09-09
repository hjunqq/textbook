# -*- coding: utf-8 -*-
"""核验书中代码清单与配套工程文件是否逐字一致。

背景：check_textbook.py 检查 label、引用、编译与字数，但查不到
"书上印的那段代码，和 companion 里那个文件，是不是同一段"。
清单一旦与配套代码漂移，读者照书敲出来的东西跑不起来，而门禁全绿。
本脚本补这一条，独立运行，不改动 check_textbook.py。

用法：
    python tools/check_listings.py          # 全部核验，有差异则 exit 1
    python tools/check_listings.py -v       # 同时打印逐行差异

判定口径：把两边都规整成"去掉注释、空行与缩进的代码骨架"，
要求书中清单的每一行都按顺序出现在配套文件中。
不比缩进：书中以片段形式印出的代码（"放在某某类里"）嵌进配套文件时必然重新缩进，
那不是内容差异；改了标识符、字面量或调用顺序才是。
配套文件可以多出内容（模块导入、导出、阶段页附加的挂载语句），
但不能少写或改写书中印出来的行。

ALLOWED 列出经过确认的差异及其原因——每一条都必须写明为什么，
不写原因的豁免等于把这个检查关掉。
"""
import io
import re
import sys
import difflib

# (清单 label, 书稿文件, 配套文件)
PAIRS = [
    ("lst:ch04-r1-load", "output/chapters/chapter04.tex",
     "companion/water-platform-demo/frontend/src/lesson45/detail.js"),
    ("lst:ch04-r1-state", "output/chapters/chapter04.tex",
     "companion/water-platform-demo/frontend/src/lesson45/state.js"),
    ("lst:ch04-r1-race", "output/chapters/chapter04.tex",
     "companion/water-platform-demo/frontend/src/lesson45/controller.js"),
    ("lst:ch06-first-scene", "output/chapters/chapter06.tex",
     "companion/water-platform-demo/frontend/src/lesson61/first-scene.js"),
    ("lst:ch06-bind-assets", "output/chapters/chapter06.tex",
     "companion/water-platform-demo/frontend/src/lesson61/bind-assets.js"),
    ("lst:ch07-link-controller", "output/chapters/chapter07.tex",
     "companion/water-platform-demo/frontend/src/lesson74/link.js"),
    ("lst:ch07-point-picker", "output/chapters/chapter07.tex",
     "companion/water-platform-demo/frontend/src/lesson74/picker.js"),
    ("lst:ch05-first-controller", "output/chapters/chapter05.tex",
     "companion/water-platform-demo/backend/src/main/java/edu/example/lesson52/AssetController.java"),
    ("lst:ch05-first-params", "output/chapters/chapter05.tex",
     "companion/water-platform-demo/backend/src/main/java/edu/example/lesson52/AssetController.java"),
]

# 已确认的差异：(label, 书中原行) -> 原因
ALLOWED = {
    ("lst:ch04-r1-load", "const output = document.querySelector('#latest');"):
        "书中 4.5.2 的页面入口块，4.5.5 起由 main.js 接管后必须删除（正文已说明）；"
        "留在模块顶层会导致每次 import 重新登录并抢先渲染一次",
    ("lst:ch04-r1-load", "await login('duty01', 'duty123');"): "同上，入口块已移入 main.js",
    ("lst:ch04-r1-load", "const assets = await loadAssets();"): "同上，入口块已移入 main.js",
    ("lst:ch04-r1-load", "const pz07 = assets.find(a => a.assetId === 'DAM-A-PZ-07');"):
        "同上，入口块已移入 main.js",
    ("lst:ch04-r1-load", "renderLatest(output, pz07, await loadLatest(pz07.assetId));"):
        "同上，入口块已移入 main.js",
    ("lst:ch07-link-controller", "function createLinkController(chart, scene, readings) {"):
        "配套文件加 export 前缀：书中按全局函数印出，工程用 ES 模块导入（picker.js 同）",
    ("lst:ch07-point-picker", "class PointPicker {"):
        "配套文件加 export 前缀，并把书中默认的全局 THREE 改为模块导入",
    ("lst:ch05-first-params", "// —— 放在 AssetController 里 ——"):
        "该行是书中给读者的放置说明，不是代码；配套已按它把两个清单合并成一个类",
    ("lst:ch05-first-controller", "import org.springframework.web.bind.annotation.GetMapping;"):
        "两个清单合并成一个类后，清单 lst:ch05-first-params 的通配导入已覆盖此行",
    ("lst:ch05-first-controller", "import org.springframework.web.bind.annotation.RequestMapping;"):
        "同上，通配导入已覆盖",
    ("lst:ch05-first-controller", "import org.springframework.web.bind.annotation.RestController;"):
        "同上，通配导入已覆盖",
    ("lst:ch05-first-controller", "package edu.example.qingyuan;"):
        "配套改为 package edu.example.lesson52，避免与完整工程的 AssetController "
        "撞包名和 /api/assets 映射；5.2.3 节正文已说明这一点，读者自建工程时用书上的包名即可",
}

# 各语言的整行注释前缀
LINE_COMMENT = ("//", "/*", "*", "#", "*/")


def extract(tex_path, label):
    s = io.open(tex_path, encoding="utf-8").read()
    m = re.search(
        r"\\begin\{lstlisting\}\[[^\]]*label=\{" + re.escape(label) + r"\}[^\]]*\](.*?)\\end\{lstlisting\}",
        s, re.S)
    if not m:
        return None
    return m.group(1).strip("\n").split("\n")


def skeleton(lines):
    out = []
    for ln in lines:
        st = ln.strip()
        if not st or st.startswith(LINE_COMMENT):
            continue
        out.append(st)
    return out


def main():
    verbose = "-v" in sys.argv
    bad, allowed_used = 0, 0
    for label, tex, src in PAIRS:
        book = extract(tex, label)
        if book is None:
            print("?? 清单未找到：%s（%s）" % (label, tex))
            bad += 1
            continue
        try:
            pkg = io.open(src, encoding="utf-8").read().split("\n")
        except FileNotFoundError:
            print("?? 配套文件缺失：%s" % src)
            bad += 1
            continue

        b, p = skeleton(book), skeleton(pkg)
        matched = set()
        for tag, i1, i2, _j1, _j2 in difflib.SequenceMatcher(None, b, p).get_opcodes():
            if tag == "equal":
                matched.update(range(i1, i2))

        missing, excused = [], []
        for i, ln in enumerate(b):
            if i in matched:
                continue
            key = (label, ln.strip())
            if key in ALLOWED:
                excused.append((ln.strip(), ALLOWED[key]))
            else:
                missing.append(ln)

        allowed_used += len(excused)
        if missing:
            bad += 1
            print("!! %-28s 书中 %d 行，配套未包含 %d 行" % (label, len(b), len(missing)))
            for ln in missing[:10]:
                print("     书: %s" % ln.strip()[:100])
            if len(missing) > 10:
                print("     …另有 %d 行" % (len(missing) - 10))
        else:
            note = "（%d 行为已确认差异）" % len(excused) if excused else ""
            print("OK %-28s 书中 %d 行与 %s 一致%s"
                  % (label, len(b), src.split("/")[-1], note))
        if verbose:
            for ln, why in excused:
                print("     · 已确认：%s\n       原因：%s" % (ln[:80], why))

    print("\n核验 %d 组清单，不一致 %d 组，已确认差异 %d 行" % (len(PAIRS), bad, allowed_used))
    if bad:
        print("清单与配套代码漂移后，读者照书敲出来的代码跑不起来。"
              "请修配套或修书稿，不要在 ALLOWED 里加无理由的豁免。")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
