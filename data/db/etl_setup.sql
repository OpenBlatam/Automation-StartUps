-- ETL Improved - Setup Script
-- Run this once to initialize all tables, views, and functions
-- Safe to re-run (uses IF NOT EXISTS / CREATE OR REPLACE)

BEGIN;

-- ============================================================================
-- 1. Main Event Table (created dynamically by DAG, but can be pre-created)
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS public;

-- This table is typically created by the DAG with configurable schema/table
-- but we create a default one here for reference
CREATE TABLE IF NOT EXISTS public.etl_improved_events (
    pk TEXT PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    attributes JSONB NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS etl_improved_events_event_time_idx 
    ON public.etl_improved_events(event_time);

-- ============================================================================
-- 2. Audit Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.etl_improved_audit (
    id BIGSERIAL PRIMARY KEY,
    run_label TEXT NOT NULL,
    num_rows INT NOT NULL,
    at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS etl_improved_audit_at_idx 
    ON public.etl_improved_audit(at);
CREATE INDEX IF NOT EXISTS etl_improved_audit_run_label_idx 
    ON public.etl_improved_audit(run_label);

-- ============================================================================
-- 3. Metrics Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.etl_improved_metrics (
    id BIGSERIAL PRIMARY KEY,
    run_label TEXT NOT NULL,
    total_rows INT NOT NULL,
    expected_rows INT NOT NULL,
    ratio DOUBLE PRECISION NOT NULL,
    num_chunks INT NOT NULL,
    dry_run BOOLEAN NOT NULL DEFAULT FALSE,
    at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS etl_improved_metrics_at_idx 
    ON public.etl_improved_metrics(at);
CREATE INDEX IF NOT EXISTS etl_improved_metrics_run_label_idx 
    ON public.etl_improved_metrics(run_label);
CREATE INDEX IF NOT EXISTS etl_improved_metrics_ratio_idx 
    ON public.etl_improved_metrics(ratio);

-- Add dry_run column if table exists without it (for existing deployments)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'etl_improved_metrics' 
        AND column_name = 'dry_run'
    ) THEN
        ALTER TABLE public.etl_improved_metrics 
        ADD COLUMN dry_run BOOLEAN NOT NULL DEFAULT FALSE;
    END IF;
END $$;

-- ============================================================================
-- 4. Alerts Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.etl_improved_alerts (
    id BIGSERIAL PRIMARY KEY,
    kind TEXT NOT NULL,
    message TEXT NOT NULL,
    run_label TEXT,
    ratio DOUBLE PRECISION,
    avg_ratio DOUBLE PRECISION,
    threshold_pct DOUBLE PRECISION,
    at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS etl_improved_alerts_at_idx 
    ON public.etl_improved_alerts(at);
CREATE INDEX IF NOT EXISTS etl_improved_alerts_kind_idx 
    ON public.etl_improved_alerts(kind);
CREATE INDEX IF NOT EXISTS etl_improved_alerts_run_label_idx 
    ON public.etl_improved_alerts(run_label);

-- ============================================================================
-- 5. Materialized Views (for Grafana)
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_etl_metrics_daily AS
SELECT
    DATE(at) AS day,
    COUNT(*) AS num_runs,
    SUM(total_rows) AS total_rows_sum,
    AVG(total_rows) AS total_rows_avg,
    SUM(expected_rows) AS expected_rows_sum,
    AVG(expected_rows) AS expected_rows_avg,
    AVG(ratio) AS ratio_avg,
    MIN(ratio) AS ratio_min,
    MAX(ratio) AS ratio_max,
    COUNT(CASE WHEN ratio < 1.0 THEN 1 END) AS low_ratio_count,
    COUNT(CASE WHEN dry_run THEN 1 END) AS dry_run_count,
    SUM(num_chunks) AS chunks_sum,
    MAX(at) AS last_run_at
FROM public.etl_improved_metrics
GROUP BY DATE(at)
ORDER BY day DESC;

CREATE UNIQUE INDEX IF NOT EXISTS mv_etl_metrics_daily_day_idx 
    ON public.mv_etl_metrics_daily(day);

CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_etl_alerts_daily AS
SELECT
    DATE(at) AS day,
    kind,
    COUNT(*) AS alert_count,
    MAX(at) AS last_alert_at
FROM public.etl_improved_alerts
GROUP BY DATE(at), kind
ORDER BY day DESC, kind;

CREATE UNIQUE INDEX IF NOT EXISTS mv_etl_alerts_daily_day_kind_idx 
    ON public.mv_etl_alerts_daily(day, kind);

-- ============================================================================
-- 6. Refresh Function
-- ============================================================================
CREATE OR REPLACE FUNCTION refresh_etl_mvs() RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_etl_metrics_daily;
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_etl_alerts_daily;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. Helper View: Latest Metrics Summary
-- ============================================================================
CREATE OR REPLACE VIEW public.v_etl_latest_metrics AS
SELECT
    run_label,
    total_rows,
    expected_rows,
    ratio,
    num_chunks,
    dry_run,
    at
FROM public.etl_improved_metrics
ORDER BY at DESC
LIMIT 1;

-- ============================================================================
-- 8. Helper View: Alert Summary (Last 24h)
-- ============================================================================
CREATE OR REPLACE VIEW public.v_etl_recent_alerts AS
SELECT
    kind,
    message,
    run_label,
    ratio,
    at
FROM public.etl_improved_alerts
WHERE at >= NOW() - INTERVAL '24 hours'
ORDER BY at DESC
LIMIT 50;

COMMIT;

-- ============================================================================
-- Post-setup: Refresh views with any existing data
-- ============================================================================
SELECT refresh_etl_mvs();


