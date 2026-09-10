"""从现役书稿提取学习层次与跨层引用；不修改正文或既有门禁。

python tools/audit_learning_path.py --out tools/review/current
编号节/小节未分层或重复分层时返回非零。跨层引用仅列为人工核查项：
引用拓展节可能是选读提示，不能靠正则判作必需依赖。
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = re.compile(r'^\\(section|subsection)(\*)?\{([^}]+)\}', re.M)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='tools/review/current')
    args = parser.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    rows, labels, citations, errors = [], {}, [], []
    for chapter in range(1, 10):
        path = ROOT / f'output/chapters/chapter{chapter:02}.tex'
        source = path.read_text(encoding='utf-8')
        # 去掉代码和注释，但保留字符位置以便定位到原文件行号。
        cleaned = re.sub(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}|(?<!\\)%[^\n]*',
                         lambda m: re.sub(r'[^\n]', ' ', m[0]), source, flags=re.S)
        headers = list(HEADER.finditer(cleaned))
        section = subsection = 0
        layers = {}
        parent_layer = ''
        for index, header in enumerate(headers):
            end = headers[index + 1].start() if index + 1 < len(headers) else len(cleaned)
            block = cleaned[header.end():end]
            if header[2]:
                continue
            if header[1] == 'section':
                section += 1
                subsection = 0
                key = f'{chapter}.{section}'
                match = re.search(r'\\paragraph\{本节层次\}([^\n]+)', block)
                stamp = match[1] if match else ''
                layers = {}
                parent_layer = stamp.split('。')[0] if stamp.startswith(('核心。', '指导实践。', '拓展。')) else ''
                for group in re.finditer(r'(核心|指导实践|拓展)：([^；。]+)', stamp):
                    for number in re.findall(r'\d+\.\d+\.\d+', group[2]):
                        if number in layers:
                            errors.append(f'{key} 重复分层 {number}')
                        layers[number] = group[1]
                # 兼容 4.5 原有的“核心。其中 4.5.5–4.5.7 为指导实践”写法。
                for group in re.finditer(r'(?:其中 |；)([\d.、 与–-]+) 为(指导实践|拓展)', stamp):
                    expanded = re.sub(r'(\d+\.\d+\.)(\d+)[–-]\1(\d+)',
                                      lambda m: '、'.join(m[1]+str(n) for n in range(int(m[2]), int(m[3])+1)), group[1])
                    for number in re.findall(r'\d+\.\d+\.\d+', expanded):
                        layers[number] = group[2]
                if not match:
                    errors.append(f'{key} 缺少层次说明')
                layer = parent_layer or '混合'
                prereq = bool(re.search(r'\\paragraph\{(?:进入本节所需知识|学习衔接)\}', block))
            else:
                subsection += 1
                key = f'{chapter}.{section}.{subsection}'
                layer = layers.pop(key, parent_layer)
                prereq = ''
                if not layer:
                    errors.append(f'{key} 未分层')
            row = dict(number=key, title=header[3], layer=layer, prerequisite=prereq,
                       file=str(path.relative_to(ROOT)).replace('\\', '/'),
                       line=source.count('\n', 0, header.start()) + 1)
            rows.append(row)
            for label in re.findall(r'\\label\{([^}]+)\}', block):
                labels[label] = row
            for ref in re.finditer(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', block):
                citations.append((row, ref[1], re.sub(r'\s+', ' ', block[max(0, ref.start()-70):ref.end()+90])))
            next_header = headers[index + 1] if index + 1 < len(headers) else None
            if next_header is None or next_header[1] == 'section':
                if layers:
                    errors.append(f'{chapter}.{section} 存在无对应小节的层次号：{list(layers)}')
    cross = []
    for row, label, context in citations:
        target = labels.get(label)
        if row['layer'] == '核心' and target and target['layer'] == '拓展':
            cross.append(dict(source=row['number'], target=target['number'], label=label, context=context))
    for name, data, fields in [('sections', rows, list(rows[0])),
                                ('core_to_extension', cross, ['source', 'target', 'label', 'context'])]:
        with (out / f'{name}.csv').open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(data)
    sections = [r for r in rows if r['number'].count('.') == 1]
    summary = dict(sections=len(sections), subsections=len(rows)-len(sections),
                   sections_with_prerequisites=sum(r['prerequisite'] for r in sections),
                   core_to_extension_refs=len(cross), errors=errors)
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
