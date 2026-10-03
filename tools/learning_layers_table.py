"""从各章源码注释“% 本节层次：…”生成“各节学习层次”表，写入线上拓展专题。

python tools/learning_layers_table.py
表放在 output/online/online.tex 中“% BEGIN learning-layers”与“% END learning-layers”之间，
每次调整层次后重新运行一次。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONLINE = ROOT / 'output/online/online.tex'
BEGIN, END = '% BEGIN learning-layers', '% END learning-layers'


def rows():
    for ch in range(1, 10):
        text = (ROOT / f'output/chapters/chapter{ch:02}.tex').read_text(encoding='utf-8')
        sections = list(re.finditer(r'^\\section\{([^}]*)\}', text, re.M))
        for i, sec in enumerate(sections):
            end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
            m = re.search(r'%\s*本节层次：([^\n]+)', text[sec.end():end])
            yield f'{ch}.{i + 1}', sec.group(1), (m.group(1).strip().rstrip('。') if m else '未标注')


def main():
    body = [BEGIN,
            '\\section{各节学习层次}\\label{online:layers}',
            '',
            '\\paragraph{说明}本表供教师安排课时使用。“核心”是课堂讲授与闭卷考核的范围；“指导实践”在工程骨架上完成，主要安排在随堂实验；“拓展”供课程设计与自学。只写一个层次的节，表示该节所有小节都属于这一层次。',
            '',
            '\\begin{longtable}{p{1.2cm}p{4.6cm}p{8.0cm}}',
            '\\toprule',
            '节 & 标题 & 各小节层次 \\\\',
            '\\midrule']
    for num, title, layer in rows():
        body.append(f'{num} & {title} & {layer} \\\\')
    body += ['\\bottomrule', '\\end{longtable}', END]
    block = '\n'.join(body)
    src = ONLINE.read_text(encoding='utf-8')
    if BEGIN in src:
        src = src[:src.index(BEGIN)] + block + src[src.index(END) + len(END):]
    else:
        src = src.rstrip('\n') + '\n\n' + block + '\n'
    ONLINE.write_text(src, encoding='utf-8')
    print('写入', ONLINE.relative_to(ROOT))


if __name__ == '__main__':
    main()
