#!/usr/bin/env python3
# 仅处理最常见的 "!!! kind" 语法；更复杂的标题可自行扩展
import re, sys

def convert(text):
    # 匹配开头的 !!! kind
    pat = re.compile(r'(?m)^\s*!!!\s+(\w+)\s*(?:\"([^\"]+)\")?\s*$')
    lines = text.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        m = pat.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        kind, title = m.group(1).lower(), m.group(2)
        out.append(f"::: admonition {kind}")
        if title: out.append(f"**{title}**")
        i += 1
        # 收集缩进内容（直到遇到空行+非缩进或文件结尾）
        while i < n and (lines[i].startswith('    ') or lines[i].strip()=='' ):
            out.append(lines[i][4:] if lines[i].startswith('    ') else '')
            i += 1
        out.append(":::")
    return "\n".join(out)

if __name__ == '__main__':
    txt = sys.stdin.read()
    sys.stdout.write(convert(txt))