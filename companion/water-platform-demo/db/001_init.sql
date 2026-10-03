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
  version integer NOT NULL DEFAULT 1, reading_id bigserial, event_id text NOT NULL,
  value numeric, unit text NOT NULL, quality text NOT NULL, source text NOT NULL,
  revision_reason text, received_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (asset_id, occurred_at, version),
  CHECK (quality IN ('valid','suspect','missing')),
  CHECK (value IS NOT NULL OR quality = 'missing')
);
SELECT create_hypertable('reading', by_range('occurred_at'), if_not_exists => TRUE);
-- 超表唯一索引必须包含分区列，幂等键用复合唯一索引表达
CREATE UNIQUE INDEX IF NOT EXISTS reading_event_uidx ON reading(occurred_at, event_id);
CREATE INDEX IF NOT EXISTS reading_asset_time_idx ON reading(asset_id, occurred_at DESC);
CREATE TABLE IF NOT EXISTS warning (
  warning_id bigserial PRIMARY KEY, asset_id text NOT NULL REFERENCES asset(asset_id),
  level text NOT NULL CHECK (level IN ('NONE','BLUE','YELLOW','ORANGE','RED')),
  evaluable boolean NOT NULL, score numeric, reason text NOT NULL,
  rule_version text NOT NULL, evidence jsonb NOT NULL, status text NOT NULL DEFAULT 'open',
  created_at timestamptz NOT NULL DEFAULT now()
);
-- ── 以下为第8章 8.3.3 节补充：约束、索引与业务过程表（可重复执行） ──
-- asset：编码格式约束、空间索引与“有效测点”列表索引
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'asset_id_format') THEN
    ALTER TABLE asset ADD CONSTRAINT asset_id_format CHECK (asset_id ~ '^[A-Z0-9-]+$');
  END IF;
END $$;
CREATE INDEX IF NOT EXISTS asset_geometry_gist_idx ON asset USING GIST (geometry);
CREATE INDEX IF NOT EXISTS asset_type_active_idx ON asset(asset_type, active);
-- reading：版本号为正数，质量码分布统计的索引
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'reading_version_positive') THEN
    ALTER TABLE reading ADD CONSTRAINT reading_version_positive CHECK (version > 0);
  END IF;
END $$;
CREATE INDEX IF NOT EXISTS reading_quality_time_idx ON reading(quality, occurred_at DESC);
-- warning：追溯字段、状态约束与待处理队列索引
ALTER TABLE warning ADD COLUMN IF NOT EXISTS source_event_id text NOT NULL;
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'warning_status_check') THEN
    ALTER TABLE warning ADD CONSTRAINT warning_status_check
      CHECK (status IN ('open','acknowledged','assigned','closed'));
  END IF;
END $$;
CREATE INDEX IF NOT EXISTS warning_open_queue_idx ON warning(status, level, created_at DESC);
-- work_order：一创建就是 in_progress，结束于 completed 或 cancelled
CREATE TABLE IF NOT EXISTS work_order (
  work_order_id bigserial PRIMARY KEY,
  warning_id bigint NOT NULL REFERENCES warning(warning_id),
  owner_role text NOT NULL,
  due_at timestamptz NOT NULL,
  action text NOT NULL,
  result text,
  status text NOT NULL DEFAULT 'in_progress',
  created_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  CONSTRAINT work_order_status_check
    CHECK (status IN ('in_progress','completed','cancelled'))
);
CREATE INDEX IF NOT EXISTS work_order_due_idx ON work_order(status, due_at);
-- model_run：模型运行记录，input_snapshot 保存可复现的输入范围
CREATE TABLE IF NOT EXISTS model_run (
  run_id uuid PRIMARY KEY,
  model_name text NOT NULL,
  model_version text NOT NULL,
  input_snapshot jsonb NOT NULL,
  started_at timestamptz NOT NULL,
  finished_at timestamptz,
  status text NOT NULL,
  result jsonb,
  error_message text,
  requested_by text NOT NULL,
  CONSTRAINT model_run_status_check
    CHECK (status IN ('queued','running','succeeded','failed')),
  CONSTRAINT model_run_finish_check
    CHECK (finished_at IS NULL OR finished_at >= started_at)
);
CREATE INDEX IF NOT EXISTS model_run_status_time_idx ON model_run(status, started_at DESC);
