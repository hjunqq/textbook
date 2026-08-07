CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE TABLE IF NOT EXISTS asset (
  asset_id text PRIMARY KEY, asset_type text NOT NULL, display_name text NOT NULL,
  unit text, geometry geometry(PointZ,4490) NOT NULL, elevation_m numeric,
  active boolean NOT NULL DEFAULT true, metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS reading (
  asset_id text NOT NULL REFERENCES asset(asset_id), occurred_at timestamptz NOT NULL,
  version integer NOT NULL DEFAULT 1, reading_id bigserial, event_id text NOT NULL UNIQUE,
  value numeric, unit text NOT NULL, quality text NOT NULL, source text NOT NULL,
  revision_reason text, received_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (asset_id, occurred_at, version),
  CHECK (quality IN ('valid','suspect','missing')),
  CHECK (value IS NOT NULL OR quality = 'missing')
);
SELECT create_hypertable('reading', by_range('occurred_at'), if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS reading_asset_time_idx ON reading(asset_id, occurred_at DESC);
CREATE TABLE IF NOT EXISTS warning (
  warning_id bigserial PRIMARY KEY, asset_id text NOT NULL REFERENCES asset(asset_id),
  level text NOT NULL CHECK (level IN ('NONE','BLUE','YELLOW','ORANGE','RED')),
  evaluable boolean NOT NULL, score numeric, reason text NOT NULL,
  rule_version text NOT NULL, evidence jsonb NOT NULL, status text NOT NULL DEFAULT 'open',
  created_at timestamptz NOT NULL DEFAULT now()
);
