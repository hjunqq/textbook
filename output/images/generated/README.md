# 教材工程识读图

本目录四幅PNG由内置 `image_gen` 生成，已用于R10-04正文。`provenance.json`记录原文件、像素尺寸、图号和SHA-256；完整提示词在仓库 `tools/review/r10-04-image-prompts.json` 与 `r10-04-components-prompt.json`。

| 文件 | 教学用途 |
|---|---|
| reservoir-dam.png | 辨认上游库面、坝体、三孔闸门、下游消能及河道 |
| monitoring-sensors.png | 对照水位雷达、雨量计、GNSS天线和渗压计外观 |
| acquisition-cabinet.png | 按供电、采集和通信功能识读柜内设备 |
| appearance-components.png | 对照表面纹理与可区分的工程构件 |

全部为虚构工程的AI教学渲染，不是现场照片、工程测绘、BIM软件输出或接线设计图。案例数值以第8章8.1节参数表为准；精确原理、流程与数据关系使用正文中的TikZ图。

这些原创图可随教材网站使用。本目录不含受单独授权限制的51WIM截图。

R10-05对 `acquisition-cabinet.png` 作局部修正：蓝色以太网线两端改为RJ45插头，连接采集器与工业路由器的网口；路由器天线保留独立射频接口。修正继续使用内置image_gen，图源和指纹已更新至provenance；不将该图作为接线设计依据。
