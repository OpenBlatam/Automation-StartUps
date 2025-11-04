-- Materialized views for robust KPI queries

-- Hourly revenue for last 24h
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_revenue_24h_hourly AS
SELECT date_trunc('hour', created_at) AS hour,
       SUM(amount) AS revenue
FROM payments
WHERE created_at >= NOW() - interval '24 hours'
  AND status IN ('succeeded','paid','payment_intent.succeeded')
GROUP BY 1
ORDER BY 1;

CREATE INDEX IF NOT EXISTS idx_mv_revenue_24h_hourly_hour ON mv_revenue_24h_hourly(hour);

-- Daily revenue for last 7 days
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_revenue_7d_daily AS
SELECT date_trunc('day', created_at)::date AS day,
       SUM(amount) AS revenue,
       COUNT(*) AS payments_count
FROM payments
WHERE created_at >= NOW() - interval '7 days'
  AND status IN ('succeeded','paid','payment_intent.succeeded')
GROUP BY 1
ORDER BY 1;

CREATE INDEX IF NOT EXISTS idx_mv_revenue_7d_daily_day ON mv_revenue_7d_daily(day);

-- Daily KPIs aggregated (last 120 days)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_kpi_daily AS
WITH leads_daily AS (
    SELECT date_trunc('day', created_at)::date AS day,
           COUNT(*)::bigint AS leads
    FROM leads
    WHERE created_at >= NOW() - interval '120 days'
    GROUP BY 1
),
payments_daily AS (
    SELECT date_trunc('day', created_at)::date AS day,
           SUM(amount)::numeric(18,2) AS revenue,
           COUNT(*)::bigint AS payments_count,
           SUM(CASE WHEN status IN ('succeeded','paid','payment_intent.succeeded') THEN 1 ELSE 0 END)::bigint AS payments_success
    FROM payments
    WHERE created_at >= NOW() - interval '120 days'
    GROUP BY 1
),
joined AS (
    SELECT d.day,
           COALESCE(l.leads, 0) AS leads,
           COALESCE(p.revenue, 0) AS revenue,
           COALESCE(p.payments_count, 0) AS payments_count,
           COALESCE(p.payments_success, 0) AS payments_success
    FROM (
        SELECT generate_series((CURRENT_DATE - interval '119 days')::date, CURRENT_DATE, interval '1 day')::date AS day
    ) d
    LEFT JOIN leads_daily l ON l.day = d.day
    LEFT JOIN payments_daily p ON p.day = d.day
)
SELECT
    day,
    leads,
    CASE WHEN leads = 0 THEN 0 ELSE ROUND((payments_success::numeric / NULLIF(leads,0)) * 100, 2) END AS conversion_pct,
    revenue,
    payments_count,
    CASE WHEN payments_count = 0 THEN 0 ELSE ROUND((payments_success::numeric / payments_count::numeric) * 100, 2) END AS payments_success_rate
FROM joined
ORDER BY day;

CREATE INDEX IF NOT EXISTS idx_mv_kpi_daily_day ON mv_kpi_daily(day);

-- 90-day timeseries, optionally segmentable later
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_kpi_timeseries_90d AS
SELECT day,
       leads,
       conversion_pct,
       revenue,
       payments_count,
       payments_success_rate
FROM mv_kpi_daily
WHERE day >= CURRENT_DATE - interval '90 days'
ORDER BY day;

CREATE INDEX IF NOT EXISTS idx_mv_kpi_timeseries_90d_day ON mv_kpi_timeseries_90d(day);

-- Segmented daily KPIs by country/source (last 120 days)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_kpi_daily_segment AS
WITH leads_daily AS (
    SELECT date_trunc('day', created_at)::date AS day,
           COALESCE(NULLIF(country,''),'unknown') AS country,
           COALESCE(NULLIF(source,''),'unknown') AS source,
           COUNT(*)::bigint AS leads
    FROM leads
    WHERE created_at >= NOW() - interval '120 days'
    GROUP BY 1,2,3
),
payments_daily AS (
    SELECT date_trunc('day', created_at)::date AS day,
           COALESCE(NULLIF(country,''),'unknown') AS country,
           COALESCE(NULLIF(source,''),'unknown') AS source,
           SUM(amount)::numeric(18,2) AS revenue,
           COUNT(*)::bigint AS payments_count,
           SUM(CASE WHEN status IN ('succeeded','paid','payment_intent.succeeded') THEN 1 ELSE 0 END)::bigint AS payments_success
    FROM payments
    WHERE created_at >= NOW() - interval '120 days'
    GROUP BY 1,2,3
),
keys AS (
    SELECT DISTINCT day FROM mv_kpi_daily
),
dim AS (
    SELECT DISTINCT COALESCE(NULLIF(country,''),'unknown') AS country,
                    COALESCE(NULLIF(source,''),'unknown') AS source
    FROM (
        SELECT country, source FROM leads
        UNION ALL
        SELECT country, source FROM payments
    ) s
)
SELECT d.day,
       dim.country,
       dim.source,
       COALESCE(l.leads,0) AS leads,
       COALESCE(p.revenue,0) AS revenue,
       COALESCE(p.payments_count,0) AS payments_count,
       CASE WHEN COALESCE(p.payments_count,0)=0 THEN 0 ELSE ROUND((COALESCE(p.payments_success,0)::numeric/COALESCE(p.payments_count,1)::numeric)*100,2) END AS payments_success_rate
FROM keys d
CROSS JOIN dim
LEFT JOIN leads_daily l ON l.day = d.day AND l.country = dim.country AND l.source = dim.source
LEFT JOIN payments_daily p ON p.day = d.day AND p.country = dim.country AND p.source = dim.source
ORDER BY d.day, dim.country, dim.source;

CREATE INDEX IF NOT EXISTS idx_mv_kpi_daily_segment_day_cs ON mv_kpi_daily_segment(day, country, source);
CREATE INDEX IF NOT EXISTS idx_mv_kpi_daily_segment_revenue ON mv_kpi_daily_segment(revenue DESC) WHERE revenue > 0;
CREATE INDEX IF NOT EXISTS idx_mv_kpi_daily_segment_country ON mv_kpi_daily_segment(country, day DESC);

-- Additional indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_mv_kpi_daily_revenue ON mv_kpi_daily(revenue DESC) WHERE revenue > 0;
CREATE INDEX IF NOT EXISTS idx_mv_kpi_daily_leads ON mv_kpi_daily(leads DESC) WHERE leads > 0;

-- Index for payments table (if not exists) to speed up materialized view refreshes
CREATE INDEX IF NOT EXISTS idx_payments_created_status ON payments(created_at, status) WHERE status IN ('succeeded','paid','payment_intent.succeeded');
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_country_source ON payments(created_at, country, source);
CREATE INDEX IF NOT EXISTS idx_leads_country_source ON leads(created_at, country, source);
