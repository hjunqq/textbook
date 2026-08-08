# 清源水库示例数据集

本目录提供第 7、8 章实践使用的可复现样例。`generate.py` 使用固定随机种子生成
`stations.csv/json`、`water_level.csv`、`rainfall.csv`、`piezometer.csv` 和
`warnings.json`；在仓库根目录运行两次，输出应完全一致。

## 字段与单位

- `stations`：`asset_id`、`asset_type`、`display_name`、`unit`、经纬度、`elevation_m`、量程、精度、阈值和投运日期。编码与第8章数据模型的 `asset.asset_id` 一致，空间坐标为 EPSG:4490。
- 观测 CSV：`asset_id`、`occurred_at`（ISO 8601，UTC+8）、`version`、`event_id`、`value`、`unit`、`quality`、`source`。质量码只取 `valid`、`suspect`、`missing`。
- 水位物理范围为死水位 148.0 m 至校核洪水位 171.6 m；超量程和跳变样例明确标记为 `suspect`，缺测以空值和 `missing` 表示。
- 测点数量为 12 个渗压、8 个位移、3 个库水位、5 个雨量，共 28 个；`DAM-A-PZ-07` 是贯穿案例测点。

## 许可与使用

数据由本仓库脚本生成，仅用于教材教学、测试和演示。不得把它当作清源水库真实监测资料，
不得据此作出工程调度或安全判断。数据文件采用仓库同一许可；第三方使用时请保留本说明和生成脚本。
