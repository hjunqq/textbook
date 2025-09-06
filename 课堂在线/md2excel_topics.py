#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 大纲 → Excel（空白对齐的知识点模板）
- 映射规则：
  * 标题 #..####### 与无序列表(-/*) → 一级..七级列；其余级别列留空（空白对齐、不跳级）。
  * 默认仅在≥3级的行解析行尾属性块：
      {标签=重点;认知=理解;分类=概念性;目标=会写HTML骨架;说明=...;前置=HTML;后置=CSS;关联=JS}
      [标签:重点; 认知:理解; 分类:概念性; 目标:...; 说明:...]
  * 关系覆盖：任意两知识点对仅保留一种关系；若重复出现，**以最后一次出现为准**。
- 可选：多文件输入、目录批量、CSV 同步输出。
"""
import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any
import pandas as pd

COLS = [
    "一级知识点","二级知识点","三级知识点","四级知识点","五级知识点","六级知识点","七级知识点",
    "前置知识点","后置知识点","关联知识点","标签","认知维度","分类","教学目标","知识点说明"
]

KEY_ALIASES = {
    # 属性别名映射（统一成中文表头）
    "标签": "标签", "tags": "标签",
    "认知": "认知维度", "认知维度": "认知维度", "cognition": "认知维度",
    "分类": "分类", "category": "分类",
    "目标": "教学目标", "教学目标": "教学目标", "objective": "教学目标",
    "说明": "知识点说明", "描述": "知识点说明", "desc": "知识点说明",
    "前置": "前置知识点", "prereq": "前置知识点",
    "后置": "后置知识点", "post": "后置知识点",
    "关联": "关联知识点", "related": "关联知识点",
}

HDR_RE = re.compile(r"^(?P<hash>#{1,7})\s+(?P<text>.+?)\s*$")
LIST_RE = re.compile(r"^(?P<indent>\s*)([-*+])\s+(?P<text>.+?)\s*$")
PROP_BRACE_RE = re.compile(r"\{([^{}]+)\}\s*$")  # {k=v; k2=v2}
PROP_BRACKET_RE = re.compile(r"\[([^\[\]]+)\]\s*$")  # [k:v; k2:v2]
CODEFENCE_RE = re.compile(r"^```")

PAIR_REL_IDX = {  # 用于覆盖逻辑：记录一对节点当前采用的关系列名
    "前置知识点": 0,
    "后置知识点": 1,
    "关联知识点": 2,
}


def parse_kv_blob(blob: str) -> Dict[str, str]:
    """解析属性块内容，支持 分号/中文分号 分隔；冒号/等号 赋值。"""
    out: Dict[str, str] = {}
    # 拆分项
    parts = re.split(r"[;；]", blob)
    for p in parts:
        if not p.strip():
            continue
        if ":" in p:
            k, v = p.split(":", 1)
        elif "=" in p:
            k, v = p.split("=", 1)
        else:
            # 允许单词直接作为标签追加
            k, v = "标签", p
        k = k.strip()
        v = v.strip()
        k = KEY_ALIASES.get(k, k)
        out[k] = v
    return out


def extract_props(text: str) -> Tuple[str, Dict[str, str]]:
    """从行尾提取属性块，返回(去除属性的正文, 属性dict)。支持{} 或 []。"""
    props: Dict[str, str] = {}
    m = PROP_BRACE_RE.search(text)
    if m:
        props.update(parse_kv_blob(m.group(1)))
        text = PROP_BRACE_RE.sub("", text).rstrip()
    m2 = PROP_BRACKET_RE.search(text)
    if m2:
        # 第二种方括号样式
        parsed2 = parse_kv_blob(m2.group(1))
        props.update(parsed2)  # 后者覆盖前者
        text = PROP_BRACKET_RE.sub("", text).rstrip()
    return text, props


def normalize_title(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip())


def level_from_list_indent(indent: str, base_level: int, indent_unit: int) -> int:
    depth = max(0, len(indent.replace("\t", "    ")) // indent_unit)
    return min(7, max(1, base_level + depth))


def md_to_rows(md_text: str, props_start_level: int = 3, indent_unit: int = 2) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    in_code = False
    last_hdr_level = 0
    # 关系覆盖跟踪
    pair_latest: Dict[Tuple[str, str], Tuple[str, int]] = {}

    # 当前“路径”用于生成节点ID（避免重名冲突）
    path: List[str] = ["" for _ in range(7)]

    def node_id(level: int, title: str) -> str:
        # 使用到当前层的路径作为唯一标识
        segs = [normalize_title(path[i]) for i in range(level-1) if path[i]] + [normalize_title(title)]
        return " > ".join(segs)

    for raw in md_text.splitlines():
        line = raw.rstrip("\n")
        if CODEFENCE_RE.match(line):
            in_code = not in_code
            continue
        if in_code or not line.strip():
            continue

        level = None
        text = None
        m = HDR_RE.match(line)
        if m:
            level = len(m.group("hash"))
            text = m.group("text")
            last_hdr_level = level
        else:
            m2 = LIST_RE.match(line)
            if m2:
                level = level_from_list_indent(m2.group("indent"), max(1, last_hdr_level), indent_unit)
                text = m2.group("text")
            else:
                continue  # 其它行忽略

        # 提取属性块
        text, props = extract_props(text)
        title = normalize_title(text)

        # 不跳级处理：若本行层级比上一个大于1级，则把空缺层视作逐级展开
        # 这里保持 last_hdr_level 只影响 list；标题天然不会跳很多
        # 填充当前路径
        for i in range(level-1):
            if not path[i]:
                path[i] = ""  # 保持空
        path[level-1] = title
        for j in range(level, 7):
            path[j] = ""

        # 构造一行
        row = {c: "" for c in COLS}
        row[COLS[level-1]] = title

        # 仅在≥props_start_level 的行填属性
        if level >= props_start_level:
            for k, v in props.items():
                col = KEY_ALIASES.get(k, k)
                if col in row:
                    row[col] = v

            # 关系覆盖：用 节点ID 作为端点，覆盖前记录
            this_id = node_id(level, title)
            for rel_col in ("前置知识点","后置知识点","关联知识点"):
                if not row.get(rel_col):
                    continue
                for target in [t.strip() for t in re.split(r"[;；]", row[rel_col]) if t.strip()]:
                    pair = tuple(sorted((this_id, target)))
                    prev = pair_latest.get(pair)
                    if prev and prev[0] != rel_col:
                        # 清除旧行里的该关系
                        old_rel_col, old_idx = prev
                        old_vals = rows[old_idx].get(old_rel_col, "")
                        kept = [x.strip() for x in re.split(r"[;；]", old_vals) if x.strip() and x.strip() != target]
                        rows[old_idx][old_rel_col] = ";".join(kept)
                    pair_latest[pair] = (rel_col, len(rows))

        rows.append(row)

    return rows


def build_dataframe(md_files: List[Path], props_start_level: int, indent_unit: int, encoding: str) -> pd.DataFrame:
    all_rows: List[Dict[str, Any]] = []
    for p in md_files:
        text = p.read_text(encoding=encoding)
        rows = md_to_rows(text, props_start_level=props_start_level, indent_unit=indent_unit)
        all_rows.extend(rows)
    if not all_rows:
        all_rows = [{c: "" for c in COLS}]
    df = pd.DataFrame(all_rows, columns=COLS)
    return df


def main():
    ap = argparse.ArgumentParser(description="Markdown 大纲 → 空白对齐 Excel")
    ap.add_argument("inputs", nargs="+", help="输入 Markdown 文件或目录（目录会递归 *.md）")
    ap.add_argument("-o", "--output", default="topics.xlsx", help="输出 Excel 文件名（.xlsx）")
    ap.add_argument("--csv", dest="csv", default=None, help="可选：同时导出 CSV 文件路径")
    ap.add_argument("--props-start-level", type=int, default=3, help="从第几级开始解析属性块，默认3")
    ap.add_argument("--indent-unit", type=int, default=2, help="列表缩进多少空格算一级，默认2")
    ap.add_argument("--encoding", default="utf-8", help="文件编码，默认utf-8")
    args = ap.parse_args()

    md_paths: List[Path] = []
    for s in args.inputs:
        p = Path(s)
        if p.is_dir():
            md_paths.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            md_paths.append(p)
    md_paths = [p for p in md_paths if p.suffix.lower() == ".md"]
    if not md_paths:
        raise SystemExit("未找到任何 .md 文件")

    df = build_dataframe(md_paths, args.props_start_level, args.indent_unit, args.encoding)

    # 导出
    out_xlsx = Path(args.output)
    out_xlsx.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    if args.csv:
        Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.csv, index=False, encoding="utf-8-sig")

    print(f"已生成: {out_xlsx.resolve()}")
    if args.csv:
        print(f"已生成: {Path(args.csv).resolve()}")

if __name__ == "__main__":
    main()