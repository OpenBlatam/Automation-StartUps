-- ============================================================================
-- Queries SQL Optimizadas para Sistema de Ventas
-- Colección de queries útiles para análisis y reportes
-- ============================================================================

-- ============================================================================
-- 1. Dashboard de Pipeline - Vista Completa
-- ============================================================================
CREATE OR REPLACE VIEW v_sales_dashboard AS
SELECT 
    p.id,
    p.lead_ext_id,
    p.email,
    p.first_name || ' ' || p.last_name AS full_name,
    p.score,
    p.priority,
    p.stage,
    p.assigned_to,
    p.estimated_value,
    p.probability_pct,
    p.estimated_value * p.probability_pct / 100.0 AS expected_value,
    p.qualified_at,
    p.last_contact_at,
    p.next_followup_at,
    EXTRACT(EPOCH FROM (NOW() - p.qualified_at) / 86400) AS days_in_pipeline,
    EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
    COUNT(t.id) FILTER (WHERE t.status = 'pending') AS pending_tasks,
    COUNT(t.id) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS overdue_tasks,
    COUNT(t.id) FILTER (WHERE t.status = 'completed') AS completed_tasks,
    (p.metadata->'ml_predictions'->>'probability')::int AS ml_probability,
    (p.metadata->'ml_predictions'->>'risk_score')::float AS ml_risk_score,
    CASE 
        WHEN p.stage = 'qualified' THEN 'Inicial'
        WHEN p.stage = 'contacted' THEN 'Contactado'
        WHEN p.stage = 'meeting_scheduled' THEN 'Reunión'
        WHEN p.stage = 'proposal_sent' THEN 'Propuesta'
        WHEN p.stage = 'negotiating' THEN 'Negociación'
        WHEN p.stage = 'closed_won' THEN 'Ganado'
        WHEN p.stage = 'closed_lost' THEN 'Perdido'
    END AS stage_label
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
GROUP BY p.id, p.lead_ext_id, p.email, p.first_name, p.last_name,
         p.score, p.priority, p.stage, p.assigned_to, p.estimated_value,
         p.probability_pct, p.qualified_at, p.last_contact_at,
         p.next_followup_at, p.metadata;

COMMENT ON VIEW v_sales_dashboard IS 'Vista completa del pipeline para dashboards';

-- ============================================================================
-- 2. Leads que Requieren Atención Inmediata
-- ============================================================================
CREATE OR REPLACE VIEW v_leads_requires_attention AS
SELECT 
    p.*,
    EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
    COUNT(t.id) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS overdue_tasks,
    (p.metadata->'ml_predictions'->>'risk_score')::float AS ml_risk_score
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
AND (
    -- Alto valor sin contacto reciente
    (p.estimated_value >= 10000 AND p.last_contact_at <= NOW() - INTERVAL '7 days')
    OR
    -- Tareas vencidas
    EXISTS (
        SELECT 1 FROM sales_followup_tasks t2
        WHERE t2.pipeline_id = p.id
        AND t2.status = 'pending'
        AND t2.due_date <= NOW()
    )
    OR
    -- Alto riesgo según ML
    (p.metadata->'ml_predictions'->>'risk_score')::float > 0.7
    OR
    -- Sin contacto en 14 días
    (p.last_contact_at IS NULL OR p.last_contact_at <= NOW() - INTERVAL '14 days')
)
GROUP BY p.id
ORDER BY 
    p.priority DESC,
    p.estimated_value DESC NULLS LAST,
    days_since_contact DESC;

COMMENT ON VIEW v_leads_requires_attention IS 'Leads que requieren atención inmediata';

-- ============================================================================
-- 3. Performance de Vendedores - Vista Agregada
-- ============================================================================
CREATE OR REPLACE VIEW v_sales_rep_performance AS
SELECT 
    p.assigned_to,
    COUNT(*) FILTER (WHERE p.stage NOT IN ('closed_won', 'closed_lost')) AS active_leads,
    COUNT(*) FILTER (WHERE p.stage = 'closed_won') AS won_last_30d,
    COUNT(*) FILTER (WHERE p.stage = 'closed_lost') AS lost_last_30d,
    COUNT(*) FILTER (WHERE p.stage IN ('closed_won', 'closed_lost')) AS total_closed,
    ROUND(
        COUNT(*) FILTER (WHERE p.stage = 'closed_won')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE p.stage IN ('closed_won', 'closed_lost')), 0) * 100,
        2
    ) AS win_rate_pct,
    SUM(p.estimated_value) FILTER (WHERE p.stage = 'closed_won') AS total_revenue,
    AVG(EXTRACT(EPOCH FROM (p.closed_at - p.qualified_at) / 86400)) 
        FILTER (WHERE p.stage = 'closed_won') AS avg_days_to_close,
    COUNT(*) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS overdue_tasks,
    AVG(p.score) FILTER (WHERE p.stage NOT IN ('closed_won', 'closed_lost')) AS avg_lead_score,
    SUM(p.estimated_value * p.probability_pct / 100.0) 
        FILTER (WHERE p.stage NOT IN ('closed_won', 'closed_lost')) AS weighted_pipeline
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
WHERE p.assigned_to IS NOT NULL
AND p.qualified_at >= NOW() - INTERVAL '30 days'
GROUP BY p.assigned_to
ORDER BY total_revenue DESC NULLS LAST;

COMMENT ON VIEW v_sales_rep_performance IS 'Performance agregada de vendedores';

-- ============================================================================
-- 4. Forecast de Ventas - Vista Predictiva
-- ============================================================================
CREATE OR REPLACE VIEW v_sales_forecast AS
SELECT 
    DATE_TRUNC('month', p.qualified_at) AS forecast_month,
    COUNT(*) AS total_deals,
    SUM(p.estimated_value) AS total_pipeline_value,
    SUM(p.estimated_value * p.probability_pct / 100.0) AS weighted_forecast,
    SUM(p.estimated_value * p.probability_pct / 100.0) 
        FILTER (WHERE p.priority = 'high') AS high_priority_forecast,
    AVG(p.probability_pct) AS avg_probability,
    COUNT(*) FILTER (WHERE p.stage = 'negotiating') AS negotiating_count,
    COUNT(*) FILTER (WHERE p.stage = 'proposal_sent') AS proposals_count
FROM sales_pipeline p
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
AND p.estimated_value IS NOT NULL
AND p.probability_pct > 0
GROUP BY DATE_TRUNC('month', p.qualified_at)
ORDER BY forecast_month DESC;

COMMENT ON VIEW v_sales_forecast IS 'Forecast mensual de ventas';

-- ============================================================================
-- 5. Análisis de Conversión por Etapa
-- ============================================================================
CREATE OR REPLACE VIEW v_conversion_funnel AS
SELECT 
    stage,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE priority = 'high') AS high_priority,
    COUNT(*) FILTER (WHERE priority = 'medium') AS medium_priority,
    COUNT(*) FILTER (WHERE priority = 'low') AS low_priority,
    AVG(score) AS avg_score,
    AVG(probability_pct) AS avg_probability,
    SUM(estimated_value) AS total_value,
    AVG(EXTRACT(EPOCH FROM (NOW() - qualified_at) / 86400)) AS avg_days_in_stage,
    -- Conversión desde etapa anterior
    LAG(COUNT(*)) OVER (ORDER BY 
        CASE stage
            WHEN 'qualified' THEN 1
            WHEN 'contacted' THEN 2
            WHEN 'meeting_scheduled' THEN 3
            WHEN 'proposal_sent' THEN 4
            WHEN 'negotiating' THEN 5
        END
    ) AS previous_stage_count
FROM sales_pipeline
WHERE qualified_at >= NOW() - INTERVAL '90 days'
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

COMMENT ON VIEW v_conversion_funnel IS 'Análisis de embudo de conversión por etapa';

-- ============================================================================
-- 6. Top Oportunidades por Valor Esperado
-- ============================================================================
CREATE OR REPLACE FUNCTION get_top_opportunities(
    p_limit INT DEFAULT 20,
    p_min_value DECIMAL DEFAULT 0
)
RETURNS TABLE (
    lead_ext_id VARCHAR(128),
    email VARCHAR(256),
    full_name TEXT,
    stage VARCHAR(32),
    estimated_value DECIMAL,
    probability_pct INT,
    expected_value DECIMAL,
    assigned_to VARCHAR(256),
    days_in_pipeline NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.lead_ext_id,
        p.email,
        p.first_name || ' ' || COALESCE(p.last_name, '') AS full_name,
        p.stage,
        p.estimated_value,
        p.probability_pct,
        p.estimated_value * p.probability_pct / 100.0 AS expected_value,
        p.assigned_to,
        EXTRACT(EPOCH FROM (NOW() - p.qualified_at) / 86400) AS days_in_pipeline
    FROM sales_pipeline p
    WHERE p.stage NOT IN ('closed_won', 'closed_lost')
    AND p.estimated_value >= p_min_value
    AND p.estimated_value IS NOT NULL
    ORDER BY expected_value DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_top_opportunities IS 'Obtiene top oportunidades por valor esperado';

-- ============================================================================
-- 7. Leads en Riesgo - Función
-- ============================================================================
CREATE OR REPLACE FUNCTION get_leads_at_risk(
    p_min_days_without_contact INT DEFAULT 7,
    p_min_risk_score DECIMAL DEFAULT 0.6
)
RETURNS TABLE (
    lead_ext_id VARCHAR(128),
    email VARCHAR(256),
    stage VARCHAR(32),
    estimated_value DECIMAL,
    days_since_contact NUMERIC,
    overdue_tasks_count BIGINT,
    ml_risk_score DECIMAL,
    risk_level VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.lead_ext_id,
        p.email,
        p.stage,
        p.estimated_value,
        EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
        COUNT(t.id) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS overdue_tasks_count,
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
        EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) >= p_min_days_without_contact
        OR (p.metadata->'ml_predictions'->>'risk_score')::float >= p_min_risk_score
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
        days_since_contact DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_leads_at_risk IS 'Obtiene leads en riesgo basado en múltiples factores';

-- ============================================================================
-- 8. Índices Adicionales para Performance
-- ============================================================================

-- Índice compuesto para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_pipeline_stage_priority_score 
    ON sales_pipeline(stage, priority DESC, score DESC)
    WHERE stage NOT IN ('closed_won', 'closed_lost');

-- Índice para búsquedas por vendedor y estado
CREATE INDEX IF NOT EXISTS idx_pipeline_assigned_stage 
    ON sales_pipeline(assigned_to, stage)
    WHERE assigned_to IS NOT NULL;

-- Índice para next_followup_at (usado frecuentemente)
CREATE INDEX IF NOT EXISTS idx_pipeline_next_followup 
    ON sales_pipeline(next_followup_at)
    WHERE next_followup_at IS NOT NULL
    AND stage NOT IN ('closed_won', 'closed_lost');

-- Índice para metadata (búsquedas ML)
CREATE INDEX IF NOT EXISTS idx_pipeline_metadata_gin 
    ON sales_pipeline USING GIN (metadata)
    WHERE metadata IS NOT NULL;

-- Índice para tareas vencidas
CREATE INDEX IF NOT EXISTS idx_tasks_overdue 
    ON sales_followup_tasks(status, due_date, priority)
    WHERE status = 'pending' AND due_date <= NOW();

-- ============================================================================
-- 9. Función para Actualizar Estadísticas de Vendedor
-- ============================================================================
CREATE OR REPLACE FUNCTION update_rep_stats(p_rep_email VARCHAR(256))
RETURNS void AS $$
DECLARE
    v_stats JSONB;
BEGIN
    SELECT jsonb_build_object(
        'active_leads', COUNT(*) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')),
        'won_count', COUNT(*) FILTER (WHERE stage = 'closed_won'),
        'lost_count', COUNT(*) FILTER (WHERE stage = 'closed_lost'),
        'win_rate', ROUND(
            COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC /
            NULLIF(COUNT(*) FILTER (WHERE stage IN ('closed_won', 'closed_lost')), 0) * 100,
            2
        ),
        'total_revenue', SUM(estimated_value) FILTER (WHERE stage = 'closed_won'),
        'weighted_pipeline', SUM(estimated_value * probability_pct / 100.0) 
            FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')),
        'updated_at', NOW()
    ) INTO v_stats
    FROM sales_pipeline
    WHERE assigned_to = p_rep_email
    AND qualified_at >= NOW() - INTERVAL '30 days';
    
    -- Guardar en metadata o tabla de estadísticas (implementar según necesidad)
    -- Por ahora solo retornamos
    RAISE NOTICE 'Stats for %: %', p_rep_email, v_stats;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_rep_stats IS 'Actualiza estadísticas de un vendedor';

-- ============================================================================
-- 10. Trigger para Actualizar next_followup_at Automáticamente
-- ============================================================================
CREATE OR REPLACE FUNCTION update_next_followup_on_contact()
RETURNS TRIGGER AS $$
BEGIN
    -- Si last_contact_at cambió, actualizar next_followup_at
    IF NEW.last_contact_at IS DISTINCT FROM OLD.last_contact_at THEN
        -- Usar delay de metadata si existe, sino default de 3 días
        NEW.next_followup_at = NEW.last_contact_at + INTERVAL '3 days';
        
        -- Si hay timing optimizado en metadata, usar ese
        IF NEW.metadata->'timing_optimized'->>'optimal_interval_days' IS NOT NULL THEN
            NEW.next_followup_at = NEW.last_contact_at + 
                (NEW.metadata->'timing_optimized'->>'optimal_interval_days')::int * INTERVAL '1 day';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_next_followup
    BEFORE UPDATE ON sales_pipeline
    FOR EACH ROW
    WHEN (NEW.last_contact_at IS DISTINCT FROM OLD.last_contact_at)
    EXECUTE FUNCTION update_next_followup_on_contact();

COMMENT ON TRIGGER trigger_update_next_followup ON sales_pipeline IS 
    'Actualiza next_followup_at automáticamente cuando cambia last_contact_at';

-- ============================================================================
-- Ejemplos de Uso
-- ============================================================================

-- Ver dashboard completo
-- SELECT * FROM v_sales_dashboard ORDER BY priority DESC, expected_value DESC;

-- Ver leads que requieren atención
-- SELECT * FROM v_leads_requires_attention LIMIT 20;

-- Ver performance de vendedores
-- SELECT * FROM v_sales_rep_performance;

-- Ver forecast
-- SELECT * FROM v_sales_forecast;

-- Ver embudo de conversión
-- SELECT * FROM v_conversion_funnel;

-- Top oportunidades
-- SELECT * FROM get_top_opportunities(20, 10000);

-- Leads en riesgo
-- SELECT * FROM get_leads_at_risk(7, 0.6);


