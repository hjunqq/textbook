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


# ---------------------------------------------------------------------------
# 测点位置：先在坝址局部坐标里布置，再反算成 CGCS2000 经纬度。
#
# 局部坐标与第 6 章场景一致：原点 (111.2E, 30.5N) 取在坝轴线中点，x 轴沿坝轴线向东，
# z 轴向南（上游/水库在 -z 一侧），y 为 1985 国家高程基准高程。教学坝体（表
# tab:ch06-teaching-geometry）：坝轴线长 160 m（x 从 -80 到 80），底宽 40 m（z 从 -20
# 到 20，上游面 z=-20），顶宽 8 m，坝基 120 m，坝顶 172 m。
#   PZ 渗压计：4 个坝段断面 × 3 个高程，埋在坝体内；
#   D  位移标点：4 个在坝顶，4 个在 150 m 高程的下游坡面上；
#   WL 库水位计：上游库区 150–700 m；
#   RF 雨量站：坝址右岸 1 个，近坝流域 1.1–1.7 km 4 个（高程高于坝顶）。
# 经纬度由高斯—克吕格反算（GRS80/CGCS2000，中央经线 111°，东偏 500 km），保留 6 位小数。
ORIGIN_LONLAT = (111.2, 30.5)
PZ_SECTIONS = (-60.0, -20.0, 20.0, 60.0)
PZ_LEVELS = ((123.5, -6.0), (138.0, -9.0), (152.5, -12.0))     # (高程, z)
LAYOUT: dict[str, tuple[float, float, float]] = {}            # code -> (x, 高程, z)
for _x in PZ_SECTIONS:
    for _y, _z in PZ_LEVELS:
        LAYOUT[f"PZ-{len(LAYOUT) + 1:02d}"] = (_x, _y, _z)
for _k, _x in enumerate(PZ_SECTIONS, 1):
    LAYOUT[f"D-{_k:02d}"] = (_x, 172.0, -16.0)                # 坝顶（顶宽中线）
for _k, _x in enumerate(PZ_SECTIONS, 5):
    LAYOUT[f"D-{_k:02d}"] = (_x, 150.0, 1.5)                  # 下游坡面 150 m 高程处
LAYOUT.update({
    "WL-01": (-30.0, 150.0, -150.0), "WL-02": (60.0, 151.5, -400.0), "WL-03": (-120.0, 149.0, -700.0),
    "RF-01": (110.0, 176.0, 10.0), "RF-02": (-650.0, 205.0, -900.0), "RF-03": (900.0, 232.0, -1400.0),
    "RF-04": (-1500.0, 218.0, -600.0), "RF-05": (1200.0, 190.0, 600.0),
})

_A, _F = 6378137.0, 1 / 298.257222101
_E2 = 2 * _F - _F * _F
_EP2 = _E2 / (1 - _E2)
_LON0, _FE = math.radians(111.0), 500000.0


def gauss_kruger(lon: float, lat: float) -> tuple[float, float]:
    """CGCS2000 经纬度 -> 高斯—克吕格 (E, N)，中央经线 111°，与 proj4 的 tmerc 一致到毫米。"""
    phi, lam = math.radians(lat), math.radians(lon) - _LON0
    n = _A / math.sqrt(1 - _E2 * math.sin(phi) ** 2)
    t, c, a = math.tan(phi) ** 2, _EP2 * math.cos(phi) ** 2, lam * math.cos(phi)
    e2 = _E2
    m = _A * ((1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256) * phi
              - 3 / 8 * (e2 + e2**2 / 4 + 15 * e2**3 / 128) * math.sin(2 * phi)
              + 15 / 256 * (e2**2 + 3 * e2**3 / 4) * math.sin(4 * phi)
              - 35 * e2**3 / 3072 * math.sin(6 * phi))
    east = n * (a + (1 - t + c) * a**3 / 6 + (5 - 18 * t + t**2 + 72 * c - 58 * _EP2) * a**5 / 120)
    north = m + n * math.tan(phi) * (a**2 / 2 + (5 - t + 9 * c + 4 * c**2) * a**4 / 24
                                     + (61 - 58 * t + t**2 + 600 * c - 330 * _EP2) * a**6 / 720)
    return _FE + east, north


def lonlat_from_local(x: float, z: float) -> tuple[float, float]:
    """场景局部坐标 (x 东, z 南) -> 经纬度：对正算做牛顿迭代反算。"""
    e0, n0 = gauss_kruger(*ORIGIN_LONLAT)
    target_e, target_n = e0 + x, n0 - z
    lon, lat = ORIGIN_LONLAT
    for _ in range(20):
        e, n = gauss_kruger(lon, lat)
        de, dn = target_e - e, target_n - n
        if abs(de) < 1e-6 and abs(dn) < 1e-6:
            break
        h = 1e-6
        e1, n1 = gauss_kruger(lon + h, lat)
        e2_, n2 = gauss_kruger(lon, lat + h)
        j00, j01, j10, j11 = (e1 - e) / h, (e2_ - e) / h, (n1 - n) / h, (n2 - n) / h
        det = j00 * j11 - j01 * j10
        lon += (de * j11 - dn * j01) / det
        lat += (dn * j00 - de * j10) / det
    return round(lon, 6), round(lat, 6)


def stations() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    specs = [("PZ", 12, "渗压", "kPa", 0.0, 500.0, 0.01),
             ("D", 8, "位移", "mm", -50.0, 50.0, 0.01),
             ("WL", 3, "库水位", "m", 148.0, 171.6, 0.001),
             ("RF", 5, "雨量", "mm", 0.0, 200.0, 0.1)]
    for prefix, count, kind, unit, lo, hi, precision in specs:
        for idx in range(1, count + 1):
            code = f"DAM-A-{prefix}-{idx:02d}"
            # Keep the exercise's well-known PZ-07 code.
            if prefix == "PZ" and idx == 7:
                code = "DAM-A-PZ-07"
            x, elevation, z = LAYOUT[f"{prefix}-{idx:02d}"]
            longitude, latitude = lonlat_from_local(x, z)
            rows.append({
                "asset_id": code,
                "asset_type": kind,
                "display_name": f"案例{kind}{idx:02d}",
                "unit": unit,
                "longitude": longitude,
                "latitude": latitude,
                "elevation_m": round(elevation, 3),
                "range_min": lo,
                "range_max": hi,
                "precision": precision,
                "threshold": round((lo + hi) / 2, 3),
                "commissioned_date": "2025-06-01",
            })
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
