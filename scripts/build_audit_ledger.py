"""Build the 182-item remediation ledger from the Pandoc audit Markdown."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


SEVERITIES = {"高", "中", "低"}


def clean_cell(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^\*\*(.*?)\*\*$", r"\1", value)
    value = value.replace("<br>", " ").replace("<br/>", " ")
    return re.sub(r"\s+", " ", value).strip()


def split_row(line: str) -> list[str]:
    body = line.strip().strip("|")
    return [clean_cell(part.replace(r"\|", "|")) for part in re.split(r"(?<!\\)\|", body)]


def detect_scope(line: str, current: str) -> str:
    if "二、全书性与跨章问题" in line:
        return "跨章共性"
    match = re.fullmatch(r"\*\*(第[1-9]章[^*]*)\*\*", line.strip())
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()
    for label in ("前言", "主文件（main.tex）", "参考文献（references.bib）"):
        if line.strip() == f"**{label}**":
            return label
    return current


def assign_wp(scope: str, location: str, problem: str, suggestion: str) -> str:
    text = f"{location} {problem} {suggestion}"

    if scope == "跨章共性":
        if "前瞻引用" in text or "分部划分" in text or "全书九章" in text:
            return "WP8"
        if "坐标转换技术路线" in text or "UTM" in text:
            return "WP6"
        if any(key in text for key in ("重复讲", "四层架构图", "生命周期两章")):
            return "WP13"
        if any(key in text for key in ("很重要", "值得关注")):
            return "WP15"
        return "WP16"

    if scope.startswith("第1章"):
        if "全章无案例" in text:
            return "WP14"
        return "WP9"

    if scope.startswith("第2章"):
        if any(key in text for key in ("SRS", "模板/标准目录")):
            return "WP14"
        return "WP9"

    if scope.startswith("第3章"):
        if any(key in text for key in ("SafeHome", "armSystem", "disarmSystem", "入侵检测", "在家模式", "外出模式", "安全系统", "网游", "社交")):
            return "WP5"
        if any(key in text for key in ("时序图", "示例图", "ATAM")):
            return "WP14"
        if any(key in text for key in ("篇幅失衡", "三处重复", "四层架构图")):
            return "WP13"
        if any(key in text for key in ("口语化", "比喻腔")):
            return "WP15"
        if any(key in text for key in ("连字符", "paragraph", "标签体系")):
            return "WP16"
        return "WP5"

    if scope.startswith("第4章"):
        if any(key in text for key in ("引号", "表格", "paragraph", "层级")):
            return "WP16"
        return "WP2"

    if scope.startswith("第5章"):
        if any(key in text for key in ("引号", "表格体例", "paragraph", "层级")):
            return "WP16"
        if any(key in text for key in ("很重要", "值得关注", "宣传")):
            return "WP15"
        return "WP3"

    if scope.startswith("第6章"):
        if "ch6_image61/62" in text or "两处 \\includegraphics" in text:
            return "WP1"
        if any(key in text for key in ("本文", "经多次实验", "经济效益", "论文", "拼接", "手工编号", "6.3.3 与 6.3.5")):
            return "WP5"
        if any(key in text for key in ("数字孪生", "五维模型", "元宇宙", "6.4")):
            return "WP10"
        if any(key in text for key in ("Markdown", "引号", "表格体例", "GLSL标language")):
            return "WP16"
        return "WP4"

    if scope.startswith("第7章"):
        if any(key in text for key in ("全章无案例", "图不足", "示意图")):
            return "WP14"
        if any(key in text for key in ("两版文稿合并", "第6章", "重复")):
            return "WP13"
        if any(key in text for key in ("小结模板化", "AI", "自评")):
            return "WP15"
        if any(key in text for key in ("学习目标层级", "下一节预告", "章末体例")):
            return "WP16"
        if "习题" in text:
            return "WP17"
        return "WP6"

    if scope.startswith("第8章"):
        if any(key in text for key in ("数字孪生", "8.5")):
            return "WP11"
        if any(key in text for key in ("AI腔", "自评式", "决策大脑")):
            return "WP15"
        if any(key in text for key in ("paragraph", "层级", "Unicode")):
            return "WP16"
        return "WP7"

    if scope.startswith("第9章"):
        return "WP8"

    if scope == "前言":
        if "第8章案例" in text or "数字孪生" in text:
            return "WP11"
        return "WP8"

    if scope == "主文件（main.tex）":
        if "第8章章名" in text:
            return "WP7"
        return "WP18"

    if scope == "参考文献（references.bib）":
        return "WP12"

    raise ValueError(f"Unmapped scope: {scope}")


def md_cell(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: build_audit_ledger.py INPUT.md OUTPUT.md", file=sys.stderr)
        return 2

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    scope = ""
    findings: list[dict[str, str]] = []

    for raw_line in source.read_text(encoding="utf-8").splitlines():
        scope = detect_scope(raw_line, scope)
        if not re.match(r"^\| \*\*(高|中|低)\*\*", raw_line):
            continue
        columns = split_row(raw_line)
        if len(columns) != 4 or columns[0] not in SEVERITIES:
            raise ValueError(f"Unexpected audit row: {raw_line}")
        severity, location, problem, suggestion = columns
        wp = assign_wp(scope, location, problem, suggestion)
        finding_id = f"AUD-{len(findings) + 1:03d}"
        done = wp == "WP1"
        findings.append(
            {
                "id": finding_id,
                "severity": severity,
                "scope": scope,
                "location": location,
                "problem": problem,
                "suggestion": suggestion,
                "wp": wp,
                "status": "已完成" if done else "待处理",
                "evidence": (
                    "图6.4/图6.5已改为TikZ；正式编译与页面检查通过"
                    if done
                    else "—"
                ),
            }
        )

    if len(findings) != 182:
        raise ValueError(f"Expected 182 findings, got {len(findings)}")
    severity_counts = Counter(item["severity"] for item in findings)
    expected = Counter({"高": 42, "中": 88, "低": 52})
    if severity_counts != expected:
        raise ValueError(f"Severity counts mismatch: {severity_counts}")

    wp_counts = Counter(item["wp"] for item in findings)
    done_count = sum(item["status"] == "已完成" for item in findings)
    lines = [
        "# 教材审计问题闭环清单（2026-08-05）",
        "",
        "- 来源：《教材标准审计报告-2026-08-04》",
        "- 总数：182项（高42、中88、低52）",
        f"- 当前闭环：{done_count}/182",
        "- 状态口径：只有完成正文修改、编译/结构验证并填写证据后，才可标记“已完成”。",
        "",
        "## 工作包分布",
        "",
        "| 工作包 | 条目数 |",
        "|---|---:|",
    ]
    for wp in sorted(wp_counts, key=lambda value: int(value[2:])):
        lines.append(f"| {wp} | {wp_counts[wp]} |")

    current_scope = None
    for item in findings:
        if item["scope"] != current_scope:
            current_scope = item["scope"]
            lines.extend(
                [
                    "",
                    f"## {current_scope}",
                    "",
                    "| 编号 | 级别 | 位置 | 问题 | 修改建议 | 工作包 | 状态 | 验证证据 |",
                    "|---|---|---|---|---|---|---|---|",
                ]
            )
        lines.append(
            "| {id} | {severity} | {location} | {problem} | {suggestion} | {wp} | {status} | {evidence} |".format(
                **{key: md_cell(value) for key, value in item.items()}
            )
        )

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {output} with {len(findings)} findings; closed={done_count}")
    print("severity=" + ", ".join(f"{key}:{severity_counts[key]}" for key in ("高", "中", "低")))
    print("work_packages=" + ", ".join(f"{key}:{wp_counts[key]}" for key in sorted(wp_counts, key=lambda value: int(value[2:]))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
