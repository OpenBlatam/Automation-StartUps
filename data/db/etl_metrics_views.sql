-- Materialized views for Grafana monitoring
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_etl_metrics_daily AS
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

CREATE UNIQUE INDEX IF NOT EXISTS mv_etl_metrics_daily_day_idx ON mv_etl_metrics_daily(day);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_etl_alerts_daily AS
SELECT
    DATE(at) AS day,
    kind,
    COUNT(*) AS alert_count,
    MAX(at) AS last_alert_at
FROM public.etl_improved_alerts
GROUP BY DATE(at), kind
ORDER BY day DESC, kind;

CREATE UNIQUE INDEX IF NOT EXISTS mv_etl_alerts_daily_day_kind_idx ON mv_etl_alerts_daily(day, kind);

-- Refresh function (can be called via cron or Airflow)
CREATE OR REPLACE FUNCTION refresh_etl_mvs() RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_etl_metrics_daily;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_etl_alerts_daily;
END;
$$ LANGUAGE plpgsql;


