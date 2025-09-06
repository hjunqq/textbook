下面两样内容都已直接贴在本页，**不用下载**，你可一键全选复制：

* ① **Python 脚本：md2excel\_topics.py**（把 MD 大纲 → 你们模板的“空白对齐”Excel）
* ② **合并后的 Markdown 大纲（第1–6章）**（可自行增改；脚本会自动映射层级与属性块）

> 规则回顾：
>
> * `# / ## / ### / …` 与无序列表 `-/*` 映射到 **一级→七级**；同一行仅在对应层级列填值，其余层级列留空（**空白对齐**）。
> * 默认只在 **≥3级** 的行解析行尾属性块（可改 `--props-start-level`）：
>   `{标签=重点;认知=理解;分类=概念性;目标=会写HTML骨架;说明=…;前置=HTML;后置=CSS;关联=JS}` 或 `[标签:重点; 认知:理解; 分类:概念性; 目标:…]`
> * 关系字段遵循“**任意两知识点只存在一种关系**；**新导入覆盖旧关系**”。

---

## ① Python脚本：`md2excel_topics.py`

````python
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
````

**本地用法示例**

```bash
# 方式A：把合并文件直接转成 Excel
python md2excel_topics.py "智慧水利-全章知识点.md" -o topics.xlsx

# 方式B：目录批量（递归搜集 *.md），并从第2级起解析属性；同时导出 CSV
python md2excel_topics.py ./chapters -o topics_all.xlsx --csv topics_all.csv --props-start-level 2

# 若你的列表缩进为4空格
python md2excel_topics.py outline.md -o out.xlsx --indent-unit 4
```

---

## ② 合并后的 Markdown 大纲（第1–6章）

> 你可以把这份全文复制为 `智慧水利-全章知识点.md`，直接用上面的脚本转换。

```markdown
# 智慧水利课程 — 全章知识点合并大纲（MD）
> 说明：本大纲采用 Markdown 层级（# / ## / ### / -）表示“一级→七级”。
> - 行尾可追加属性块：{标签=重点;认知=理解;分类=概念性;目标=……;说明=……;前置=……;后置=……;关联=……}
> - 或方括号样式：[标签:重点; 认知:理解; 分类:概念性; 目标:……; 说明:……]
> - 默认仅在≥3级的条目解析属性（脚本可用 --props-start-level 修改）。

# 第1章 软件工程概述
## 第1节 软件工程与软件危机（1.1）
- 软件工程概念
  - 定义 {标签=重点;认知=理解;分类=概念性;目标=说出软件工程定义;说明=系统化、规范化、可度量的方法用于开发/运行/维护}
  - 目标 {标签=考点;认知=记忆;分类=概念性;目标=记忆主要目标;说明=质量高、成本低、按期、易维护与演化}
  - 软件构成
    - 程序 {标签=重点;认知=记忆;分类=事实性;目标=说出构成-程序;说明=可执行逻辑与算法实现}
    - 文档 {标签=重点;认知=记忆;分类=事实性;目标=说出构成-文档;说明=规格说明、设计、测试、运维文档}
    - 数据 {标签=重点;认知=记忆;分类=事实性;目标=说出构成-数据;说明=运行期与配置等数据}
  - 工程化转变 {标签=课程思政;认知=理解;分类=概念性;目标=认识从经验到工程;说明=引入过程与度量支撑团队协作}
- 软件工程体系
  - SWEBOK知识域 {标签=考点;认知=记忆;分类=概念性;目标=列举知识域;说明=需/设/构/测/维/度/过/管/工与方法}
  - 三要素
    - 方法 {标签=重点;认知=理解;分类=概念性;目标=说明方法;说明=形成完成任务的技术路线与步骤}
    - 工具 {标签=重点;认知=理解;分类=概念性;目标=说明工具;说明=自动/半自动化环境支撑方法落地}
    - 过程 {标签=重点;认知=理解;分类=概念性;目标=说明过程;说明=明确任务顺序、里程碑与质量活动}
- 软件危机
  - 介绍 {标签=重点;认知=理解;分类=概念性;目标=解释术语;说明=软件开发与维护中的系统性问题集合}
  - 表现
    - 成本增长 {标签=考点;认知=记忆;分类=概念性;目标=列举表现;说明=成本比例上升、失败率较高}
    - 进度失控 {标签=考点;认知=记忆;分类=概念性;目标=列举表现;说明=需求反复、延期与返工}
    - 质量问题 {标签=考点;认知=记忆;分类=概念性;目标=列举表现;说明=缺陷多、稳定性差}
    - 维护困难 {标签=考点;认知=记忆;分类=概念性;目标=列举表现;说明=扩展难、定位慢、成本高}
  - 原因
    - 技术原因 {标签=难点;认知=分析;分类=概念性;目标=分析技术成因;说明=规模扩张、复杂度/耦合升高}
    - 管理原因 {标签=难点;认知=分析;分类=概念性;目标=分析管理成因;说明=缺乏标准化过程、度量与风险管理}
  - 代价随时间上升 {标签=重点;认知=理解;分类=概念性;目标=阐释曲线;说明=越晚修复代价越高}
  - 消除途径
    - 技术与工具 {标签=重点;认知=应用;分类=程序性;目标=制定技术改进;说明=自动化构建/测试、组件复用、标准化}
    - 管理与组织 {标签=重点;认知=应用;分类=程序性;目标=建立治理机制;说明=评审、变更/风险管理、里程碑控制}

## 第2节 开发过程、质量与设计、维护（1.2）
- 软件生命周期
  - 定义与范围 {标签=重点;认知=理解;分类=概念性;目标=正确定义SDLC;说明=需→设→实→测→交付/运维全过程}
  - 阶段与工件
    - 需求说明 {标签=考点;认知=记忆;分类=事实性;目标=识别工件;说明=SRS等}
    - 设计说明 {标签=考点;认知=记忆;分类=事实性;目标=识别工件;说明=系统/结构设计说明}
    - 源代码 {标签=考点;认知=记忆;分类=事实性;目标=识别工件}
    - 测试计划 {标签=考点;认知=记忆;分类=事实性;目标=识别工件;说明=范围/策略/用例/准入/退出}
    - 交付与运维文档 {标签=考点;认知=记忆;分类=事实性;目标=识别工件;说明
```
