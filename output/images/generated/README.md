# 教材写实教学图

本目录七幅PNG由内置 `image_gen` 生成。`provenance.json`记录原文件、像素尺寸、使用位置和SHA-256；完整提示词及后续修改见其中的 `prompts` 清单。

| 文件 | 教学用途 |
|---|---|
| reservoir-dam.png | 辨认上游库面、坝体、三孔闸门、下游消能及河道 |
| monitoring-sensors.png | 对照水位雷达、雨量计、GNSS天线和渗压计外观 |
| acquisition-cabinet.png | 按供电、采集和通信功能识读柜内设备 |
| appearance-components.png | 对照表面纹理与可区分的工程构件 |
| personnel-duty-officer.png | 图3.1的值班员、图3.8的软件用户 |
| personnel-analyst.png | 图3.1的专业分析员 |
| cover-reservoir-r11.png | 封面主视觉：晨光中的库区、坝体与轻微数据纹理 |

全部为AI教学渲染，工程与人物均为虚构，不是现场照片、工程测绘、BIM软件输出或接线设计图。案例数值以第8章8.1节参数表为准；精确原理、流程与数据关系使用正文中的TikZ图。

这些原创图可随教材网站使用。本目录不含受单独授权限制的51WIM截图。

R11-06-cover新增封面主视觉，采用深青蓝水面、自然晨光和山体层次。图片作为装饰性封面图使用，未赋予工程参数或数据含义；书名继续由LaTeX排版，版权页注明“封面主视觉为AI生成教学渲染”。完整提示词见 `revision/r11/cover-image-prompt.json`。替换的抽象坝体封面图保留于Git基线 `4f299a3:output/main.tex`。

R10-06新增两幅虚构人物半身像，替换用例图中的火柴人和MVC图中的用户圆圈。人物仅表示参与角色，不代表真实员工；角色名称、系统边界与关系线由TikZ准确绘制。两幅合成图的图注均注明“人物为AI生成教学渲染”。网站SVG内嵌人物PNG，构建缓存同时校验TikZ源码与图片内容，完整提示词见 `tools/review/r10-06-image-prompts.json`。

R10-05对 `acquisition-cabinet.png` 作局部修正：蓝色以太网线两端改为RJ45插头，连接采集器与工业路由器的网口；路由器天线保留独立射频接口。修正继续使用内置image_gen，图源和指纹已更新至provenance；不将该图作为接线设计依据。
