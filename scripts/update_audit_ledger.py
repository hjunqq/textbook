"""Update remediation status/evidence for one work package in the audit ledger."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROW_RE = re.compile(r"^\|\s*AUD-\d{3}\s*\|")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--wp", required=True)
    parser.add_argument("--status", default="已完成")
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()

    lines = args.ledger.read_text(encoding="utf-8").splitlines()
    updated = 0
    output: list[str] = []
    for line in lines:
        if ROW_RE.match(line):
            cells = [cell.strip() for cell in line.strip().strip("|").split(" | ")]
            if len(cells) == 8 and cells[-3] == args.wp:
                cells[-2] = args.status
                cells[-1] = args.evidence.replace("|", r"\|")
                updated += 1
            if len(cells) == 8:
                line = "| " + " | ".join(cells) + " |"
        output.append(line)

    if updated == 0:
        raise SystemExit(f"No rows found for {args.wp}")

    closed = 0
    for line in output:
        if not ROW_RE.match(line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split(" | ")]
        if len(cells) == 8 and cells[-2] == "已完成":
            closed += 1

    output = [
        re.sub(r"^- 当前闭环：\d+/182$", f"- 当前闭环：{closed}/182", line)
        for line in output
    ]
    args.ledger.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"updated {updated} rows for {args.wp}; closed={closed}/182")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
