-- 教学种子数据：让 compose 启动后页面即刻有内容。
-- 完整 28 测点数据集见 companion/datasets/，可用 load-s3-data.sql 导入。
INSERT INTO asset(asset_id, asset_type, display_name, unit, geometry, elevation_m) VALUES
  ('DAM-A-PZ-07', '渗压', '清源渗压07', 'kPa',  ST_SetSRID(ST_MakePoint(113.752, 34.251, 148.2), 4490), 148.2),
  ('DAM-A-PZ-08', '渗压', '清源渗压08', 'kPa',  ST_SetSRID(ST_MakePoint(113.753, 34.251, 147.9), 4490), 147.9),
  ('DAM-A-WL-01', '库水位', '清源库水位01', 'm', ST_SetSRID(ST_MakePoint(113.750, 34.252, 152.0), 4490), 152.0),
  ('DAM-A-RG-01', '雨量', '清源雨量01', 'mm',  ST_SetSRID(ST_MakePoint(113.748, 34.253, 176.4), 4490), 176.4)
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
