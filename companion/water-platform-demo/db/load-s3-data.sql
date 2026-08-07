-- Run after 001_init.sql. The host-side loader maps S3 CSV columns to these fields.
-- Example: python ../../datasets/load_to_postgres.py --dsn "$DATABASE_URL"
INSERT INTO asset(asset_id, asset_type, display_name, unit, geometry, elevation_m, metadata)
VALUES ('DAM-A-PZ-07', '渗压', '清源渗压07', 'kPa', ST_SetSRID(ST_MakePoint(111.2072,30.5054,160.8),4490), 160.8, '{"source":"S3"}')
ON CONFLICT (asset_id) DO NOTHING;
