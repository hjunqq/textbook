-- 导入完整 28 测点示例数据集(companion/datasets/)。
-- 用法:在 companion/water-platform-demo/ 目录下执行
--   psql "$DATABASE_URL" -f db/load-s3-data.sql
-- 依赖 psql 客户端侧 \copy,CSV 路径相对当前工作目录解析。
-- 先执行 001_init.sql(建表);002_seed.sql 的少量种子行与本脚本兼容(ON CONFLICT 跳过)。

\set ON_ERROR_STOP on

BEGIN;

-- 1) 测点台账:stations.csv -> asset
CREATE TEMP TABLE _import_stations (
  asset_id text, asset_type text, display_name text, unit text,
  longitude double precision, latitude double precision, elevation_m double precision,
  range_min double precision, range_max double precision, precision_ double precision,
  threshold double precision, commissioned_date date
);
\copy _import_stations FROM '../datasets/stations.csv' WITH (FORMAT csv, HEADER true)

INSERT INTO asset(asset_id, asset_type, display_name, unit, geometry, elevation_m, metadata)
SELECT asset_id, asset_type, display_name, unit,
       ST_SetSRID(ST_MakePoint(longitude, latitude, elevation_m), 4490),
       elevation_m,
       jsonb_build_object('source', 'dataset',
                          'range_min', range_min, 'range_max', range_max,
                          'precision', precision_, 'threshold', threshold,
                          'commissioned_date', commissioned_date)
FROM _import_stations
ON CONFLICT (asset_id) DO UPDATE
  SET display_name = EXCLUDED.display_name,
      geometry     = EXCLUDED.geometry,
      elevation_m  = EXCLUDED.elevation_m,
      metadata     = EXCLUDED.metadata;

-- 2) 观测序列:三个 CSV -> reading(质量码 valid/suspect/missing)
CREATE TEMP TABLE _import_readings (
  asset_id text, occurred_at timestamptz, version int, event_id text,
  value double precision, unit text, quality text, source text
);
\copy _import_readings FROM '../datasets/water_level.csv' WITH (FORMAT csv, HEADER true)
\copy _import_readings FROM '../datasets/rainfall.csv' WITH (FORMAT csv, HEADER true)
\copy _import_readings FROM '../datasets/piezometer.csv' WITH (FORMAT csv, HEADER true)

INSERT INTO reading(asset_id, occurred_at, version, event_id, value, unit, quality, source)
SELECT asset_id, occurred_at, version, event_id, value, unit, quality, source
FROM _import_readings
ON CONFLICT (asset_id, occurred_at, version) DO NOTHING;

COMMIT;

-- 导入结果核对:28 个测点,观测行数应与 CSV 行数一致
SELECT (SELECT count(*) FROM asset)   AS assets,
       (SELECT count(*) FROM reading) AS readings;
