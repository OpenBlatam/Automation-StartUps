-- Vistas materializadas y vistas para análisis de reembolsos

-- Vista para estadísticas rápidas
CREATE OR REPLACE VIEW stripe_refunds_summary AS
SELECT 
    status,
    COUNT(*) as count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    MIN(created_at) as first_refund,
    MAX(created_at) as last_refund,
    AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) as avg_processing_seconds
FROM stripe_refunds
GROUP BY status;

-- Vista para reembolsos por cliente
CREATE OR REPLACE VIEW stripe_refunds_by_customer AS
SELECT 
    customer_email,
    COUNT(*) as total_refunds,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_refunds,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_refunds,
    SUM(amount) as total_refunded,
    SUM(amount) FILTER (WHERE status = 'completed') as total_refunded_completed,
    AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) FILTER (WHERE processed_at IS NOT NULL) as avg_processing_seconds
FROM stripe_refunds
GROUP BY customer_email
ORDER BY total_refunds DESC;

-- Vista para tendencias diarias
CREATE OR REPLACE VIEW stripe_refunds_daily_trends AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    SUM(amount) as total_amount,
    SUM(amount) FILTER (WHERE status = 'completed') as completed_amount,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::numeric / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as success_rate_pct,
    AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) FILTER (WHERE processed_at IS NOT NULL) as avg_processing_seconds
FROM stripe_refunds
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Vista materializada para reportes (se refresca con el DAG)
CREATE MATERIALIZED VIEW IF NOT EXISTS stripe_refunds_monthly_summary AS
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_refunds,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_refunds,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_refunds,
    SUM(amount) as total_amount,
    SUM(amount) FILTER (WHERE status = 'completed') as completed_amount,
    AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) FILTER (WHERE processed_at IS NOT NULL) as avg_processing_seconds,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::numeric / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as success_rate_pct
FROM stripe_refunds
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- Índice para la vista materializada
CREATE UNIQUE INDEX IF NOT EXISTS idx_stripe_refunds_monthly_summary_month 
ON stripe_refunds_monthly_summary(month);

-- Función para refrescar la vista materializada
CREATE OR REPLACE FUNCTION refresh_stripe_refunds_mv()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY stripe_refunds_monthly_summary;
END;
$$ LANGUAGE plpgsql;



