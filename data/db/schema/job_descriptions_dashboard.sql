-- Schema para dashboard y reportes

-- Tabla de métricas de dashboard
CREATE TABLE IF NOT EXISTS dashboard_metrics (
    metric_id SERIAL PRIMARY KEY,
    metrics_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_created ON dashboard_metrics(created_at);

-- Vista de métricas recientes
CREATE OR REPLACE VIEW latest_dashboard_metrics AS
SELECT 
    metrics_data,
    created_at
FROM dashboard_metrics
ORDER BY created_at DESC
LIMIT 1;

-- Vista de tendencias
CREATE OR REPLACE VIEW job_description_trends AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as descriptions_created,
    COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
    COUNT(DISTINCT jp.posting_id) as total_postings,
    COUNT(DISTINCT ja.application_id) as total_applications
FROM job_descriptions jd
LEFT JOIN job_postings jp ON jd.job_description_id = jp.job_description_id
LEFT JOIN job_applications ja ON jp.posting_id = ja.posting_id
WHERE jd.created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;






