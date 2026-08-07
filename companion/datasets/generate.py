"""Generate deterministic Qingyuan Reservoir teaching data.

The generator uses only the Python standard library.  Run it from the
repository root with ``python companion/datasets/generate.py``; every output
is overwritten from a fixed seed so two runs are byte-for-byte identical.
"""
from __future__ import annotations

import csv
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 20260807
UTC8 = timezone(timedelta(hours=8))
START = datetime(2026, 7, 1, 0, 0, tzinfo=UTC8)


def stations() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    specs = [("PZ", 12, "渗压", "kPa", 0.0, 500.0, 0.01),
             ("D", 8, "位移", "mm", -50.0, 50.0, 0.01),
             ("WL", 3, "库水位", "m", 148.0, 171.6, 0.001),
             ("RF", 5, "雨量", "mm", 0.0, 200.0, 0.1)]
    offset = 0
    for prefix, count, kind, unit, lo, hi, precision in specs:
        for idx in range(1, count + 1):
            code = f"DAM-A-{prefix}-{idx:02d}"
            # Keep the exercise's well-known PZ-07 code.
            if prefix == "PZ" and idx == 7:
                code = "DAM-A-PZ-07"
            rows.append({
                "asset_id": code,
                "asset_type": kind,
                "display_name": f"清源{kind}{idx:02d}",
                "unit": unit,
                "longitude": round(111.2000 + offset * 0.0012, 6),
                "latitude": round(30.5000 + offset * 0.0009, 6),
                "elevation_m": round(150.0 + (offset % 7) * 1.8, 3),
                "range_min": lo,
                "range_max": hi,
                "precision": precision,
                "threshold": round((lo + hi) / 2, 3),
                "commissioned_date": "2025-06-01",
            })
            offset += 1
    return rows


def write_stations(rows: list[dict[str, object]]) -> None:
    fields = list(rows[0])
    with (ROOT / "stations.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "stations.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reading_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rng = random.Random(SEED)
    wl = [r for r in rows if r["asset_type"] == "库水位"]
    output: list[dict[str, object]] = []
    for i in range(1200):
        ts = START + timedelta(minutes=5 * i)
        for j, station in enumerate(wl):
            # Physical range 148.0--171.6 m, with a slow flood pulse.
            pulse = 1.2 * math.sin(i / 90.0) + (i / 1199.0) * 1.0
            value = round(165.0 + pulse + j * 0.08 + rng.uniform(-0.015, 0.015), 3)
            quality = "valid"
            note = ""
            if i == 37 and j == 0:
                value, quality, note = None, "missing", "planned communication gap"
            elif i == 211 and j == 1:
                value, quality, note = 173.2, "suspect", "above physical range"
            elif i == 512 and j == 2:
                value, quality, note = 148.0, "suspect", "abrupt jump from previous sample"
            output.append({"asset_id": station["asset_id"], "occurred_at": ts.isoformat(),
                           "version": 1, "event_id": f"evt-wl-{i:04d}-{j}",
                           "value": value, "unit": "m", "quality": quality,
                           "source": "simulator", "note": note})
    return output


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0])
    with (ROOT / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def auxiliary_rows(rows: list[dict[str, object]]) -> None:
    rng = random.Random(SEED + 1)
    rain = [r for r in rows if r["asset_type"] == "雨量"]
    piezo = [r for r in rows if r["asset_type"] == "渗压"]
    rainfall, piezometer = [], []
    for i in range(288):
        ts = START + timedelta(minutes=5 * i)
        for j, station in enumerate(rain):
            rainfall.append({"asset_id": station["asset_id"], "occurred_at": ts.isoformat(),
                             "version": 1, "event_id": f"evt-rf-{i:04d}-{j}",
                             "value": round(max(0, rng.gauss(0.18 if i % 37 else 8.5, 0.3)), 2),
                             "unit": "mm", "quality": "valid", "source": "simulator"})
        for j, station in enumerate(piezo):
            piezometer.append({"asset_id": station["asset_id"], "occurred_at": ts.isoformat(),
                               "version": 1, "event_id": f"evt-pz-{i:04d}-{j}",
                               "value": round(180 + 5 * math.sin(i / 40) + j * 0.2, 3),
                               "unit": "kPa", "quality": "valid", "source": "simulator"})
    write_csv("rainfall.csv", rainfall)
    write_csv("piezometer.csv", piezometer)


def warnings() -> None:
    data = [
        {"warning_id": "w-0001", "asset_id": "DAM-A-WL-01", "level": "BLUE", "evaluable": True,
         "quality": "valid", "score": 0.36, "reason": "水位出现需关注变化", "status": "open"},
        {"warning_id": "w-0002", "asset_id": "DAM-A-PZ-07", "level": "YELLOW", "evaluable": True,
         "quality": "valid", "score": 0.58, "reason": "渗压趋势超过黄色阈值", "status": "acknowledged"},
        {"warning_id": "w-0003", "asset_id": "DAM-A-WL-02", "level": "ORANGE", "evaluable": True,
         "quality": "valid", "score": 0.74, "reason": "水位包络接近设计洪水位", "status": "open"},
        {"warning_id": "w-0004", "asset_id": "DAM-A-WL-03", "level": "RED", "evaluable": True,
         "quality": "valid", "score": 0.92, "reason": "校核洪水位情景需人工会商", "status": "open"},
        {"warning_id": "w-0005", "asset_id": "DAM-A-WL-01", "level": "NONE", "evaluable": False,
         "quality": "missing", "score": None, "reason": "缺测导致未评估", "status": "closed"},
    ]
    (ROOT / "warnings.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = stations()
    write_stations(rows)
    write_csv("water_level.csv", reading_rows(rows))
    auxiliary_rows(rows)
    warnings()


if __name__ == "__main__":
    main()
