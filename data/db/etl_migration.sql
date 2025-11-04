-- ETL Improved - Migration Script
-- Safe migration from existing installations to full ETL system
-- Run this AFTER etl_setup.sql if you have existing data
-- Safe to re-run (uses IF NOT EXISTS / ALTER TABLE IF NOT EXISTS)

BEGIN;

-- ============================================================================
-- 1. Add missing columns to existing tables (if they don't exist)
-- ============================================================================

-- Add dry_run column to metrics if missing
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'etl_improved_metrics'
    ) AND NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'etl_improved_metrics' 
        AND column_name = 'dry_run'
    ) THEN
        ALTER TABLE public.etl_improved_metrics 
        ADD COLUMN dry_run BOOLEAN NOT NULL DEFAULT FALSE;
        RAISE NOTICE 'Added dry_run column to etl_improved_metrics';
    END IF;
END $$;

-- ============================================================================
-- 2. Create indexes if they don't exist (improve query performance)
-- ============================================================================

-- Indexes for metrics table
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'etl_improved_metrics'
    ) THEN
        -- Index on at (timestamp)
        IF NOT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'etl_improved_metrics' 
            AND indexname = 'etl_improved_metrics_at_idx'
        ) THEN
            CREATE INDEX etl_improved_metrics_at_idx ON public.etl_improved_metrics(at);
        END IF;
        
        -- Index on run_label
        IF NOT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'etl_improved_metrics' 
            AND indexname = 'etl_improved_metrics_run_label_idx'
        ) THEN
            CREATE INDEX etl_improved_metrics_run_label_idx ON public.etl_improved_metrics(run_label);
        END IF;
        
        -- Index on ratio (for filtering)
        IF NOT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'etl_improved_metrics' 
            AND indexname = 'etl_improved_metrics_ratio_idx'
        ) THEN
            CREATE INDEX etl_improved_metrics_ratio_idx ON public.etl_improved_metrics(ratio);
        END IF;
    END IF;
END $$;

-- Indexes for audit table
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'etl_improved_audit'
    ) THEN
        IF NOT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'etl_improved_audit' 
            AND indexname = 'etl_improved_audit_at_idx'
        ) THEN
            CREATE INDEX etl_improved_audit_at_idx ON public.etl_improved_audit(at);
        END IF;
        
        IF NOT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'etl_improved_audit' 
            AND indexname = 'etl_improved_audit_run_label_idx'
        ) THEN
            CREATE INDEX etl_improved_audit_run_label_idx ON public.etl_improved_audit(run_label);
        END IF;
    END IF;
END $$;

-- Indexes for alerts table
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'etl_improved_alerts'
    ) THEN
        IF NOT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'etl_improved_alerts' 
            AND indexname = 'etl_improved_alerts_at_idx'
        ) THEN
            CREATE INDEX etl_improved_alerts_at_idx ON public.etl_improved_alerts(at);
        END IF;
        
        IF NOT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'etl_improved_alerts' 
            AND indexname = 'etl_improved_alerts_kind_idx'
        ) THEN
            CREATE INDEX etl_improved_alerts_kind_idx ON public.etl_improved_alerts(kind);
        END IF;
        
        IF NOT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'etl_improved_alerts' 
            AND indexname = 'etl_improved_alerts_run_label_idx'
        ) THEN
            CREATE INDEX etl_improved_alerts_run_label_idx ON public.etl_improved_alerts(run_label);
        END IF;
    END IF;
END $$;

-- Index for events table (if exists)
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'etl_improved_events'
    ) AND NOT EXISTS (
        SELECT FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND tablename = 'etl_improved_events' 
        AND indexname = 'etl_improved_events_event_time_idx'
    ) THEN
        CREATE INDEX etl_improved_events_event_time_idx ON public.etl_improved_events(event_time);
    END IF;
END $$;

-- ============================================================================
-- 3. Create or update helper views
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

-- ============================================================================
-- 4. Ensure materialized views exist and refresh them
-- ============================================================================

-- Create MVs if they don't exist (from etl_metrics_views.sql logic)
DO $$
BEGIN
    -- Metrics daily MV
    IF NOT EXISTS (
        SELECT FROM pg_matviews 
        WHERE schemaname = 'public' AND matviewname = 'mv_etl_metrics_daily'
    ) THEN
        EXECUTE '
        CREATE MATERIALIZED VIEW public.mv_etl_metrics_daily AS
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
        ';
        
        CREATE UNIQUE INDEX mv_etl_metrics_daily_day_idx ON public.mv_etl_metrics_daily(day);
        RAISE NOTICE 'Created mv_etl_metrics_daily';
    END IF;
    
    -- Alerts daily MV
    IF NOT EXISTS (
        SELECT FROM pg_matviews 
        WHERE schemaname = 'public' AND matviewname = 'mv_etl_alerts_daily'
    ) THEN
        EXECUTE '
        CREATE MATERIALIZED VIEW public.mv_etl_alerts_daily AS
        SELECT
            DATE(at) AS day,
            kind,
            COUNT(*) AS alert_count,
            MAX(at) AS last_alert_at
        FROM public.etl_improved_alerts
        GROUP BY DATE(at), kind
        ORDER BY day DESC, kind;
        ';
        
        CREATE UNIQUE INDEX mv_etl_alerts_daily_day_kind_idx ON public.mv_etl_alerts_daily(day, kind);
        RAISE NOTICE 'Created mv_etl_alerts_daily';
    END IF;
END $$;

-- Ensure refresh function exists
CREATE OR REPLACE FUNCTION refresh_etl_mvs() RETURNS void AS $$
BEGIN
    IF EXISTS (
        SELECT FROM pg_matviews 
        WHERE schemaname = 'public' AND matviewname = 'mv_etl_metrics_daily'
    ) THEN
        REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_etl_metrics_daily;
    END IF;
    
    IF EXISTS (
        SELECT FROM pg_matviews 
        WHERE schemaname = 'public' AND matviewname = 'mv_etl_alerts_daily'
    ) THEN
        REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_etl_alerts_daily;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 5. Refresh materialized views with existing data
-- ============================================================================

SELECT refresh_etl_mvs();

COMMIT;

-- Migration complete
SELECT 'Migration completed successfully' AS status;

