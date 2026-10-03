# 教学坝体模型

`dam.glb` 由同目录的 `generate-dam-glb.py` 生成（只用 Python 标准库，重复运行输出逐字节一致）：

```
python3 generate-dam-glb.py                       # dam.glb：米、+Y 向上、底面 y=0
python3 generate-dam-glb.py --units mm --z-up     # 毫米、+Z 向上，用来触发 6.1.4 节的单位与轴向检查
```

几何取教材第 6 章表 tab:ch06-teaching-geometry 的教学尺寸：坝轴线长 160 m、底宽 40 m、顶宽 8 m、坝高 52 m，
断面为上游面铅直的梯形，与 6.1.2 节用 `ExtrudeGeometry` 拉伸出的坝体同形。文件为二进制 glTF 2.0（JSON 块 + BIN 块），
一个网格、位置 + 法线 + 索引、一种 PBR 材质，约 1.7 KB。

模型不承担真实工程语义，只用于 6.1.4 节“单位、轴向、基面”三项检查的练习；加载后应只需把底面从 0 抬到坝基高程 120 m。
`frontend/tests/lesson61-dam-glb.test.js` 用 Three.js 的 `GLTFLoader` 解析该文件并重放三项检查。
