-- ============================================================================
-- Queries para Dashboards y Visualizaciones
-- Ejemplos de queries útiles para Grafana, Metabase, etc.
-- ============================================================================

-- ============================================================================
-- 1. Pipeline Overview - Últimos 30 días
-- ============================================================================
SELECT 
    DATE_TRUNC('day', qualified_at) AS date,
    COUNT(*) AS total_qualified,
    COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
    COUNT(*) FILTER (WHERE stage = 'closed_lost') AS lost,
    SUM(estimated_value) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')) AS pipeline_value,
    SUM(estimated_value * probability_pct / 100.0) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')) AS weighted_pipeline,
    ROUND(
        COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE stage IN ('closed_won', 'closed_lost')), 0) * 100,
        2
    ) AS win_rate_pct
FROM sales_pipeline
WHERE qualified_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', qualified_at)
ORDER BY date DESC;

-- ============================================================================
-- 2. Conversion Funnel - Últimos 7 días
-- ============================================================================
SELECT 
    stage,
    COUNT(*) AS leads,
    LAG(COUNT(*)) OVER (ORDER BY 
        CASE stage
            WHEN 'qualified' THEN 1
            WHEN 'contacted' THEN 2
            WHEN 'meeting_scheduled' THEN 3
            WHEN 'proposal_sent' THEN 4
            WHEN 'negotiating' THEN 5
            WHEN 'closed_won' THEN 6
        END
    ) AS previous_stage_count,
    ROUND(
        COUNT(*)::NUMERIC / 
        NULLIF(LAG(COUNT(*)) OVER (ORDER BY 
            CASE stage
                WHEN 'qualified' THEN 1
                WHEN 'contacted' THEN 2
                WHEN 'meeting_scheduled' THEN 3
                WHEN 'proposal_sent' THEN 4
                WHEN 'negotiating' THEN 5
                WHEN 'closed_won' THEN 6
            END
        ), 0) * 100,
        2
    ) AS conversion_rate_pct
FROM sales_pipeline
WHERE qualified_at >= NOW() - INTERVAL '7 days'
GROUP BY stage
ORDER BY 
    CASE stage
        WHEN 'qualified' THEN 1
        WHEN 'contacted' THEN 2
        WHEN 'meeting_scheduled' THEN 3
        WHEN 'proposal_sent' THEN 4
        WHEN 'negotiating' THEN 5
        WHEN 'closed_won' THEN 6
        WHEN 'closed_lost' THEN 7
    END;

-- ============================================================================
-- 3. Sales Rep Performance - Últimos 30 días
-- ============================================================================
SELECT 
    assigned_to AS rep,
    COUNT(*) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')) AS active_leads,
    COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
    COUNT(*) FILTER (WHERE stage = 'closed_lost') AS lost,
    ROUND(
        COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE stage IN ('closed_won', 'closed_lost')), 0) * 100,
        2
    ) AS win_rate_pct,
    SUM(estimated_value) FILTER (WHERE stage = 'closed_won') AS revenue,
    AVG(EXTRACT(EPOCH FROM (closed_at - qualified_at) / 86400)) 
        FILTER (WHERE stage = 'closed_won') AS avg_days_to_close,
    COUNT(*) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS overdue_tasks
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
WHERE p.assigned_to IS NOT NULL
AND p.qualified_at >= NOW() - INTERVAL '30 days'
GROUP BY p.assigned_to
ORDER BY revenue DESC NULLS LAST;

-- ============================================================================
-- 4. Score Distribution - Últimos 90 días
-- ============================================================================
SELECT 
    CASE 
        WHEN score < 35 THEN 'Low (0-34)'
        WHEN score < 50 THEN 'Medium (35-49)'
        WHEN score < 70 THEN 'High (50-69)'
        ELSE 'Very High (70+)'
    END AS score_range,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE ext_id IN (SELECT lead_ext_id FROM sales_pipeline WHERE stage = 'closed_won')) AS won,
    ROUND(
        COUNT(*) FILTER (WHERE ext_id IN (SELECT lead_ext_id FROM sales_pipeline WHERE stage = 'closed_won'))::NUMERIC /
        NULLIF(COUNT(*), 0) * 100,
        2
    ) AS conversion_rate_pct
FROM leads
WHERE score IS NOT NULL
AND created_at >= NOW() - INTERVAL '90 days'
GROUP BY score_range
ORDER BY 
    CASE score_range
        WHEN 'Low (0-34)' THEN 1
        WHEN 'Medium (35-49)' THEN 2
        WHEN 'High (50-69)' THEN 3
        WHEN 'Very High (70+)' THEN 4
    END;

-- ============================================================================
-- 5. Campaign Performance - Últimos 30 días
-- ============================================================================
SELECT 
    c.name AS campaign_name,
    c.campaign_type,
    COUNT(DISTINCT ce.id) AS total_executions,
    COUNT(DISTINCT ce.lead_ext_id) AS unique_leads,
    COUNT(DISTINCT CASE WHEN ce.status = 'completed' THEN ce.id END) AS completed,
    COUNT(DISTINCT CASE WHEN p.stage = 'closed_won' THEN p.id END) AS won,
    ROUND(
        COUNT(DISTINCT CASE WHEN ce.status = 'completed' THEN ce.id END)::NUMERIC /
        NULLIF(COUNT(DISTINCT ce.id), 0) * 100,
        2
    ) AS completion_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN p.stage = 'closed_won' THEN p.id END)::NUMERIC /
        NULLIF(COUNT(DISTINCT ce.lead_ext_id), 0) * 100,
        2
    ) AS win_rate_pct
FROM sales_campaigns c
LEFT JOIN sales_campaign_executions ce ON c.id = ce.campaign_id
LEFT JOIN sales_pipeline p ON ce.lead_ext_id = p.lead_ext_id
WHERE c.enabled = true
AND ce.started_at >= NOW() - INTERVAL '30 days'
GROUP BY c.id, c.name, c.campaign_type
ORDER BY win_rate_pct DESC, completion_rate_pct DESC;

-- ============================================================================
-- 6. Task Completion Rate - Últimos 7 días
-- ============================================================================
SELECT 
    DATE_TRUNC('day', created_at) AS date,
    COUNT(*) AS total_tasks,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed,
    COUNT(*) FILTER (WHERE status = 'pending' AND due_date <= NOW()) AS overdue,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100,
        2
    ) AS completion_rate_pct,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at) / 3600)) 
        FILTER (WHERE status = 'completed') AS avg_completion_hours
FROM sales_followup_tasks
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;

-- ============================================================================
-- 7. Source Performance - Últimos 90 días
-- ============================================================================
SELECT 
    source,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
    COUNT(*) FILTER (WHERE stage = 'closed_lost') AS lost,
    ROUND(
        COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100,
        2
    ) AS conversion_rate_pct,
    AVG(score) AS avg_score,
    SUM(estimated_value) FILTER (WHERE stage = 'closed_won') AS total_revenue,
    AVG(EXTRACT(EPOCH FROM (closed_at - qualified_at) / 86400)) 
        FILTER (WHERE stage = 'closed_won') AS avg_days_to_close
FROM sales_pipeline
WHERE qualified_at >= NOW() - INTERVAL '90 days'
GROUP BY source
ORDER BY conversion_rate_pct DESC, total_revenue DESC;

-- ============================================================================
-- 8. High Value Opportunities - Actual
-- ============================================================================
SELECT 
    p.lead_ext_id,
    p.email,
    p.first_name || ' ' || COALESCE(p.last_name, '') AS full_name,
    p.stage,
    p.estimated_value,
    p.probability_pct,
    p.estimated_value * p.probability_pct / 100.0 AS expected_value,
    p.assigned_to,
    p.next_followup_at,
    EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact
FROM sales_pipeline p
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
AND p.estimated_value >= 10000
AND p.estimated_value IS NOT NULL
ORDER BY expected_value DESC
LIMIT 20;

-- ============================================================================
-- 9. Leads at Risk - Actual
-- ============================================================================
SELECT 
    p.lead_ext_id,
    p.email,
    p.stage,
    p.estimated_value,
    EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
    COUNT(t.id) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS overdue_tasks,
    COALESCE((p.metadata->'ml_predictions'->>'risk_score')::float, 0) AS ml_risk_score,
    CASE 
        WHEN (p.metadata->'ml_predictions'->>'risk_score')::float > 0.8 THEN 'CRITICAL'
        WHEN (p.metadata->'ml_predictions'->>'risk_score')::float > 0.6 THEN 'HIGH'
        WHEN EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) > 14 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS risk_level
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
AND (
    EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) >= 7
    OR (p.metadata->'ml_predictions'->>'risk_score')::float >= 0.6
)
GROUP BY p.id, p.lead_ext_id, p.email, p.stage, p.estimated_value,
         p.last_contact_at, p.qualified_at, p.metadata
ORDER BY 
    CASE risk_level
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END,
    ml_risk_score DESC,
    days_since_contact DESC
LIMIT 30;

-- ============================================================================
-- 10. Score Trends - Últimos 30 días
-- ============================================================================
SELECT 
    DATE_TRUNC('day', calculated_at) AS date,
    COUNT(*) AS score_updates,
    AVG(score) AS avg_score,
    AVG(score_change) AS avg_score_change,
    COUNT(*) FILTER (WHERE score_change > 0) AS increases,
    COUNT(*) FILTER (WHERE score_change < 0) AS decreases,
    COUNT(*) FILTER (WHERE score_change = 0) AS no_change
FROM lead_score_history
WHERE calculated_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', calculated_at)
ORDER BY date DESC;

-- ============================================================================
-- 11. Forecast por Mes - Próximos 3 meses
-- ============================================================================
SELECT 
    DATE_TRUNC('month', p.qualified_at) AS forecast_month,
    COUNT(*) AS total_deals,
    SUM(p.estimated_value) AS total_pipeline_value,
    SUM(p.estimated_value * p.probability_pct / 100.0) AS weighted_forecast,
    SUM(p.estimated_value * p.probability_pct / 100.0) 
        FILTER (WHERE p.priority = 'high') AS high_priority_forecast,
    AVG(p.probability_pct) AS avg_probability,
    COUNT(*) FILTER (WHERE p.stage = 'negotiating') AS negotiating_count
FROM sales_pipeline p
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
AND p.estimated_value IS NOT NULL
AND p.probability_pct > 0
AND p.qualified_at >= DATE_TRUNC('month', NOW())
AND p.qualified_at < DATE_TRUNC('month', NOW()) + INTERVAL '3 months'
GROUP BY DATE_TRUNC('month', p.qualified_at)
ORDER BY forecast_month;

-- ============================================================================
-- 12. Time in Stage Analysis - Promedio por etapa
-- ============================================================================
WITH stage_times AS (
    SELECT 
        p.lead_ext_id,
        p.stage,
        EXTRACT(EPOCH FROM (NOW() - p.qualified_at) / 86400) AS days_in_pipeline,
        EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact
    FROM sales_pipeline p
    WHERE p.stage NOT IN ('closed_won', 'closed_lost')
    AND p.qualified_at >= NOW() - INTERVAL '90 days'
)
SELECT 
    stage,
    COUNT(*) AS total_leads,
    AVG(days_in_pipeline) AS avg_days_in_pipeline,
    AVG(days_since_contact) AS avg_days_since_contact,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY days_in_pipeline) AS median_days,
    MAX(days_in_pipeline) AS max_days
FROM stage_times
GROUP BY stage
ORDER BY 
    CASE stage
        WHEN 'qualified' THEN 1
        WHEN 'contacted' THEN 2
        WHEN 'meeting_scheduled' THEN 3
        WHEN 'proposal_sent' THEN 4
        WHEN 'negotiating' THEN 5
    END;


