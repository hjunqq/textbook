# Qingyuan Water Platform Demo

This companion project is the executable counterpart of the Chapter 4, 5 and 8
listings. It uses Vue 3.4 + Vite 5 + Pinia 2 + Vue Router 4 + ECharts +
Three.js r160+, and Java 17 + Spring Boot 3.2 + Jakarta Persistence + Spring
Security 6 + Kafka. PostgreSQL 16 with PostGIS and TimescaleDB, Redis 7 and
Kafka 3.7 are started by `docker compose`.

## Start

1. Run `python companion/datasets/generate.py` to create the deterministic S3 data.
2. Copy `secrets/*.example` to files without the `.example` suffix and replace the teaching passwords.
3. Run `docker compose up --build` in this directory.
4. Open `http://localhost:8080/monitoring`; API readiness is at `/readyz` and liveness at `/healthz`.
5. Load the CSV files with `db/load-s3-data.sql` after the migration has completed.

The Compose file is a single-node teaching baseline. Production deployment must
replace image tags, credentials, resource limits, TLS and persistence according to
the A8-4 runbook. Redis is a rebuildable cache, not the source of truth.

## Layout and mapping

`frontend/src` contains the request layer, Pinia store, router guard, monitoring
SFC and Three.js scene bridge shown in A8-3. `backend/src` contains the Java 17
Spring Boot entry point, a read-only asset controller and Spring Security 6
configuration; the full domain services follow the same package boundaries.
`db/001_init.sql` is the A8-1 schema baseline. The field names `asset_id`,
`occurred_at`, `event_id`, `value`, `unit`, `quality` and `version` are shared by
the SQL, Java DTOs, Vue API and S3 CSV files.

## Verification

Run `mvn test` in `backend` and `npm run build` in `frontend` when the toolchains
are installed. Check `/actuator/health/liveness` and `/actuator/health/readiness`,
then execute the recovery rehearsal described in Chapter 8 before using the demo
for a class. The data is synthetic teaching material, not real safety-monitoring data.
