-- 教学种子数据：让 compose 启动后页面即刻有内容。
-- 坐标与高程与 companion/datasets/stations.csv 保持一致(权威来源:生成脚本 generate.py)。
-- 完整 28 测点数据集见 companion/datasets/，可用 load-s3-data.sql 导入。
INSERT INTO asset(asset_id, asset_type, display_name, unit, geometry, elevation_m) VALUES
  ('DAM-A-PZ-07', '渗压', '案例渗压07', 'kPa',  ST_SetSRID(ST_MakePoint(111.2072, 30.5054, 160.8), 4490), 160.8),
  ('DAM-A-PZ-08', '渗压', '案例渗压08', 'kPa',  ST_SetSRID(ST_MakePoint(111.2084, 30.5063, 150.0), 4490), 150.0),
  ('DAM-A-WL-01', '库水位', '案例库水位01', 'm', ST_SetSRID(ST_MakePoint(111.224, 30.518, 160.8), 4490), 160.8),
  ('DAM-A-RF-01', '雨量', '案例雨量01', 'mm',  ST_SetSRID(ST_MakePoint(111.2276, 30.5207, 153.6), 4490), 153.6),
  -- 刻意不给它任何观测：契约要求“对象存在但尚无观测”返回 204，
  -- 没有这样一个测点，真实后端就演示不出第4章的“暂无观测”状态（只能演示 404）。
  ('DAM-A-D-01',  '位移', '案例位移01', 'mm',  ST_SetSRID(ST_MakePoint(111.2144, 30.5108, 159.0), 4490), 159.0)
ON CONFLICT (asset_id) DO NOTHING;

INSERT INTO reading(asset_id, occurred_at, version, event_id, value, unit, quality, source) VALUES
  ('DAM-A-PZ-07', now() - interval '50 minutes', 1, 'SEED-PZ07-001', 118.2, 'kPa', 'valid',   'seed'),
  ('DAM-A-PZ-07', now() - interval '40 minutes', 1, 'SEED-PZ07-002', 118.6, 'kPa', 'valid',   'seed'),
  ('DAM-A-PZ-07', now() - interval '30 minutes', 1, 'SEED-PZ07-003', NULL,  'kPa', 'missing', 'seed'),
  ('DAM-A-PZ-07', now() - interval '20 minutes', 1, 'SEED-PZ07-004', 121.9, 'kPa', 'suspect', 'seed'),
  ('DAM-A-PZ-07', now() - interval '10 minutes', 1, 'SEED-PZ07-005', 119.1, 'kPa', 'valid',   'seed'),
  ('DAM-A-WL-01', now() - interval '30 minutes', 1, 'SEED-WL01-001', 166.82, 'm', 'valid',    'seed'),
  ('DAM-A-WL-01', now() - interval '10 minutes', 1, 'SEED-WL01-002', 166.85, 'm', 'valid',    'seed')
ON CONFLICT (occurred_at, event_id) DO NOTHING;
