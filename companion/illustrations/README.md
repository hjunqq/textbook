# 水库监测导学图

本组图用于《智慧水利平台架构与开发》的课堂导入与读图练习。

R10-04新增入书素材：工程识读渲染见 `../../output/images/generated/`；真实程序运行截图见 `../../output/images/runtime/`，采集与复现见本目录 `runtime/README.md`。下列场景插画是上一包保留的补充导学材料。

- reservoir-monitoring-overview.png：1536 × 1024 场景插画，展示代表性水位、雨量、位移、渗压测点，采集网关与监测平台。
- reservoir-monitoring-study.pdf：可打印的导学页，含读图顺序、缺测情境与自测要点。
- reservoir-monitoring-study.tex：导学页的排版源，使用 XeLaTeX 编译。
- reservoir-monitoring-overview.prompt.txt：场景生成提示词。
- provenance.json：生成工具、源文件与审查记录。

沿图中的数据箭头，从现场测量走到监测页面。先说清各测项观察的工程现象，再区分工程对象、采集设备和页面中的业务对象。主教材第1章介绍平台分层，第4章实现数据请求，第6章定位三维对象，第7章处理观测与质量码，第8章将预警、工单和部署串联。

图中仅展示代表性传感器，坝体剖面与设备位置为概念示意；案例实际参数、监测数量与对象编码统一查第8章8.1节。图中的水流箭头表示水流方向，蓝色虚线表示数据传递。屏幕曲线的空缺表示没有可用观测，不能解读成数值为零或工程安全。

该插画由 imagegen 生成，经审查后修正屏幕中跨越缺测的虚线。它是配套导学素材；教材正文中的精确过程图仍使用可编辑的 TikZ 矢量图。本组素材不包含第8章受单独授权限制的51WIM产品截图。

## 编译

在本目录运行：

    xelatex -interaction=nonstopmode -halt-on-error reservoir-monitoring-study.tex

需安装 Noto Sans CJK SC、TeX Gyre Heros 与 TeX Live。图中汉字已内嵌于PNG；导学页说明文字在PDF中保持可选择。
