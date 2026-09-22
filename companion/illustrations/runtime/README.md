# 教材运行截图（R10-05；S4/S5 于 R11 按新测点布置重拍）

本目录保存截图采集脚本、教学查看器页面、源文件指纹和请求证据。图片输出到仓库根目录的 `output/images/runtime/`。查看器直接调用配套模块或教学 API；图片由浏览器截图生成，没有重画界面或替换观测值。

## 复现

要求 Node.js 18+、已经安装依赖的 `companion/water-platform-demo/frontend/`，以及 Playwright 和可用的 Chromium/Edge。采集时自动启动独立教学 API（18114）与 Vite（5194），完成或失败后关闭本次启动的服务。Windows 子进程使用 `windowsHide: true`。

在仓库根目录执行：

```powershell
npm ci --prefix companion/water-platform-demo/frontend
npm install --prefix companion/illustrations/runtime
node companion/illustrations/runtime/capture.cjs
```

Linux 下可用 `PLAYWRIGHT_MODULE_PATH` 指向全局安装的 playwright、`BROWSER_EXECUTABLE` 指向 Playwright 的 Chromium（R11 的 S4/S5 即这样重拍，字体回退为 Noto Sans CJK SC）。Windows 默认优先使用已经安装的 Edge。也可通过 `BROWSER_EXECUTABLE` 指定浏览器完整路径；没有系统 Edge 时，先在本目录执行 `npx playwright install chromium`。已有 Playwright 安装可用 `PLAYWRIGHT_MODULE_PATH` 指定模块路径。Codex 工作环境的预装 Playwright 是本机后备路径，其他机器不依赖该后备路径。

`capture.cjs` 会重新生成本目录的 HTML 查看器、`manifest.json`、`request-evidence.json`，以及九张 PNG。请先确认两个端口未被其他服务占用。

## 图片与证据

| 图片 | 采集入口 | 可观察结果 |
|---|---|---|
| `s1-asset-list.png` | 原 S1 `lesson44.html` | 输入 DAM-A-WL、降序排序后，裁取三个合法水位对象的列表区域 |
| `s2-four-states.png` | `four-states.html` | 原 `detail.js`、`state.js` 返回等待、成功、空、错误四态 |
| `s2-switch-trace.png` | `switch.html` | 原 `controller.js` 取消 PZ-07 旧请求，最终显示 WL-01 |
| `http-responses.png` | `http-records.html` | 教学 API 实际返回的 400、404 错误体 |
| `http-network-json.png` | `network-json.html` | 实际 HTTP 记录与选定响应体；这是教学查看器，不是 DevTools |
| `s4-scene.png` | S4 `lesson61.html` 加识读标记 | 聚焦PZ-07，显示真实绑定坐标、局部网格与垂直投影；场景实际绑定28个对象 |
| `s5-scene-chart.png` | S5 `lesson74.html` 加识读标记 | 实际鼠标点选PZ-07，原射线拾取器触发请求，右侧显示同编码288点曲线 |
| `s5-missing-gap.png` | `quality.html` | 原序列控制器与质量映射处理真实 CSV 中 WL-01 的缺测记录 |
| `s6-work-order.png` | `work-order.html` | 实际确认、创建、完成、回查归档响应，以及未确认派单的409失败例 |

S4/S5由 `scene-display.cjs` 调整原相机，添加10m局部参考网格、垂直投影和编码标签，并把坝体材质调为半透明（渗压计按台账埋在坝体内部，不透明时被挡住）；这是带识读标记的运行图，不是原阶段页的默认视图。网格平面高程120m取自阶段坝体底面。28个实际测点的台账坐标、几何体及阶段源码保持不变。S4同时显示 `bound.find` 定位对象的坐标。

S5先切换到WL-01，再用真实鼠标点击PZ-07，原 `PointPicker` 完成射线拾取，经事件和教学API更新曲线；采集器断言返回200、288条观测、状态文字及高亮编码一致。等待动画结束后仅调整显示字号、面板和日期刻度。轴标签与状态文字为22 CSS px，16cm宽印刷时等效8.91pt；显示调整前后序列SHA-256一致。实际点击坐标、请求、返回条数和字号记录于manifest。

S6 的工单与预警保存在本次教学服务的内存中，服务重启后恢复初始状态。它证明教学接口的受控转换，不作为 Java 后端持久化、角色鉴权或真实现场处置的证据。图中处置描述是提交给教学接口的演练文本。

`request-evidence.json` 保存完整请求路径、请求体及实际返回体，不保存令牌。`manifest.json` 记录采集时间、提交标识、关键源文件 SHA-256、图片尺寸/指纹、纸面16 cm宽时的高度、入口、动作和观察结果。采集脚本对状态、对象数、缺测记录和工单状态转换做断言，未捕获的 JavaScript 异常必须为零。
