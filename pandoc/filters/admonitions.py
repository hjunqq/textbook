#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import panflute as pf

MAP = {
    'note': ('Note', 'blue!5'),
    'tip': ('Tip', 'green!5'),
    'warning': ('Warning', 'yellow!10'),
    'danger': ('Danger', 'red!5'),
}

def action(elem, doc):
    # 识别经预处理转成 fenced_divs 的块：::: admonition note
    if isinstance(elem, pf.Div) and 'admonition' in elem.classes:
        kind = next((c for c in elem.classes if c in MAP), 'note')
        title, color = MAP.get(kind, ('Note', 'blue!5'))
        before = pf.RawBlock(
            rf'\begin{{tcolorbox}}[colback={color},title={{{title}}}]',
            format='latex'
        )
        after = pf.RawBlock(r'\end{tcolorbox}', format='latex')
        return [before] + list(elem.content) + [after]

def main(doc=None):
    return pf.run_filter(action, doc=doc)

if __name__ == "__main__":
    main()