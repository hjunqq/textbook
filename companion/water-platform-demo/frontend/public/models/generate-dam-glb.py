#!/usr/bin/env python3
"""生成教学用坝体模型 dam.glb（二进制 glTF 2.0），只用 Python 标准库。

几何按教材第 6 章表 tab:ch06-teaching-geometry 的教学尺寸：坝轴线长 160 m（x 从 -80 到
80），底宽 40 m（z 从 -20 到 20，上游面 z=-20 铅直），顶宽 8 m（坝顶 z 从 -20 到 -12），
坝高 52 m。默认输出与 6.1.2 节用 ExtrudeGeometry 拉伸出的坝体同形：单位为米、+Y 向上、
底面在 y=0（不带坝基高程），因此 6.1.4 节 load-dam.js 的三项检查中前两项不触发，只需
把底面从 0 抬到坝基高程 120 m。

    python3 generate-dam-glb.py                 # dam.glb：米、+Y 向上、底面 y=0
    python3 generate-dam-glb.py --units mm      # 毫米单位，用来触发"单位"检查
    python3 generate-dam-glb.py --z-up          # +Z 向上（y = 北），用来触发"轴向"检查
    python3 generate-dam-glb.py -o dam-mm-zup.glb --units mm --z-up

--z-up 时顶点 (x, y, z) 写成 (x, -z, y)：加载后绕 x 轴旋转 -90° 即与默认文件重合。
文件结构：JSON 块 + BIN 块；一个 mesh、一个 primitive（位置 + 法线 + 索引）、一种材质。
模型不承担真实工程语义，只用于场景练习。
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

# 断面轮廓（z 指向下游、y 向上，单位 m），逆时针：上游坝踵 -> 下游坝趾 -> 坝顶下游边 -> 坝顶上游边
SECTION = [(-20.0, 0.0), (20.0, 0.0), (-12.0, 52.0), (-20.0, 52.0)]
HALF_LENGTH = 80.0          # 坝轴线长 160 m 的一半


def build_mesh(units: str, z_up: bool):
    scale = 1000.0 if units == "mm" else 1.0
    positions: list[tuple[float, float, float]] = []
    normals: list[tuple[float, float, float]] = []
    indices: list[int] = []

    def emit_polygon(poly, normal):
        """平面多边形扇形三角化；顶点顺序调整为对外法线呈逆时针（右手法则）。"""
        a, b, c = poly[0], poly[1], poly[2]
        e = [b[k] - a[k] for k in range(3)]
        f = [c[k] - a[k] for k in range(3)]
        cross = (e[1] * f[2] - e[2] * f[1], e[2] * f[0] - e[0] * f[2], e[0] * f[1] - e[1] * f[0])
        if sum(cross[k] * normal[k] for k in range(3)) < 0:
            poly = list(reversed(poly))
        base = len(positions)
        positions.extend(poly)
        normals.extend([normal] * len(poly))
        for k in range(1, len(poly) - 1):
            indices.extend([base, base + k, base + k + 1])

    n = len(SECTION)
    # 侧面：沿坝轴线拉伸每条断面边
    for i in range(n):
        (z0, y0), (z1, y1) = SECTION[i], SECTION[(i + 1) % n]
        # 断面在 (z, y) 平面内逆时针，向外法线为边向量 (dz, dy) 顺时针转 90°：(dy, -dz)
        dz, dy = z1 - z0, y1 - y0
        length = (dz * dz + dy * dy) ** 0.5
        nz, ny = dy / length, -dz / length
        emit_polygon([(-HALF_LENGTH, y0, z0), (HALF_LENGTH, y0, z0), (HALF_LENGTH, y1, z1), (-HALF_LENGTH, y1, z1)],
                     (0.0, ny, nz))
    # 两端断面
    emit_polygon([(HALF_LENGTH, y, z) for z, y in SECTION], (1.0, 0.0, 0.0))
    emit_polygon([(-HALF_LENGTH, y, z) for z, y in SECTION], (-1.0, 0.0, 0.0))

    def convert(v):
        x, y, z = (c * scale for c in v)
        return (x, -z, y) if z_up else (x, y, z)

    def convert_normal(v):
        x, y, z = v
        return (x, -z, y) if z_up else (x, y, z)

    return [convert(p) for p in positions], [convert_normal(m) for m in normals], indices


def write_glb(path: Path, positions, normals, indices, units: str, z_up: bool) -> None:
    pos_bytes = b"".join(struct.pack("<3f", *p) for p in positions)
    nrm_bytes = b"".join(struct.pack("<3f", *m) for m in normals)
    idx_bytes = b"".join(struct.pack("<H", i) for i in indices)
    if len(idx_bytes) % 4:
        idx_bytes += b"\0\0"
    bin_chunk = pos_bytes + nrm_bytes + idx_bytes
    mins = [min(p[k] for p in positions) for k in range(3)]
    maxs = [max(p[k] for p in positions) for k in range(3)]
    gltf = {
        "asset": {"version": "2.0", "generator": "generate-dam-glb.py (textbook companion)",
                  "extras": {"units": units, "up": "+Z" if z_up else "+Y", "base": "y=0 (坝基高程需在加载后加上)",
                             "source": "tab:ch06-teaching-geometry 教学尺寸，不承担真实工程语义"}},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "DamTeaching"}],
        "meshes": [{"name": "DamTeaching", "primitives": [
            {"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2, "material": 0}]}],
        "materials": [{"name": "Concrete", "pbrMetallicRoughness": {
            "baseColorFactor": [0.553, 0.6, 0.682, 1.0], "metallicFactor": 0.0, "roughnessFactor": 0.9}}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(positions), "type": "VEC3", "min": mins, "max": maxs},
            {"bufferView": 1, "componentType": 5126, "count": len(normals), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5123, "count": len(indices), "type": "SCALAR"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(pos_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": len(pos_bytes), "byteLength": len(nrm_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": len(pos_bytes) + len(nrm_bytes), "byteLength": len(idx_bytes), "target": 34963},
        ],
        "buffers": [{"byteLength": len(bin_chunk)}],
    }
    json_bytes = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * (-len(json_bytes) % 4)
    total = 12 + 8 + len(json_bytes) + 8 + len(bin_chunk)
    with path.open("wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, total))
        f.write(struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes)
        f.write(struct.pack("<I4s", len(bin_chunk), b"BIN\0") + bin_chunk)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output", default=str(Path(__file__).with_name("dam.glb")))
    parser.add_argument("--units", choices=["m", "mm"], default="m")
    parser.add_argument("--z-up", action="store_true")
    args = parser.parse_args()
    positions, normals, indices = build_mesh(args.units, args.z_up)
    out = Path(args.output)
    write_glb(out, positions, normals, indices, args.units, args.z_up)
    print(f"{out}: {len(positions)} vertices, {len(indices) // 3} triangles, units={args.units}, up={'+Z' if args.z_up else '+Y'}")


if __name__ == "__main__":
    main()
