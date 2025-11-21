-- ============================================================================
-- OPTIMIZACIONES SQL para Sistema de Soporte
-- ============================================================================
-- Índices adicionales, optimizaciones de queries, y materialized views
-- ============================================================================

BEGIN;

-- ============================================================================
-- ÍNDICES ADICIONALES PARA PERFORMANCE
-- ============================================================================

-- Índice compuesto para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_support_tickets_status_priority_created 
ON support_tickets(status, priority, created_at DESC)
WHERE status IN ('open', 'assigned', 'in_progress');

-- Índice para búsqueda por cliente y fecha
CREATE INDEX IF NOT EXISTS idx_support_tickets_customer_date 
ON support_tickets(customer_email, created_at DESC);

-- Índice para escalación (tickets sin respuesta)
CREATE INDEX IF NOT EXISTS idx_support_tickets_escalation 
ON support_tickets(priority, status, first_response_at, created_at)
WHERE status NOT IN ('resolved', 'closed', 'chatbot_handled')
AND first_response_at IS NULL;

-- Índice para feedback reciente
CREATE INDEX IF NOT EXISTS idx_feedback_recent 
ON support_ticket_feedback(submitted_at DESC, satisfaction_score)
WHERE submitted_at >= NOW() - INTERVAL '30 days';

-- Índice GIN para búsqueda full-text en descripciones
CREATE INDEX IF NOT EXISTS idx_support_tickets_description_gin 
ON support_tickets USING GIN(to_tsvector('spanish', description));

-- Índice para búsqueda de FAQs por contenido
CREATE INDEX IF NOT EXISTS idx_faq_content_gin 
ON support_faq_articles USING GIN(to_tsvector('spanish', content));

-- ============================================================================
-- VISTA MATERIALIZADA: Métricas Agregadas por Día
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_support_daily_metrics AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_tickets,
    COUNT(*) FILTER (WHERE chatbot_resolved = true) as chatbot_resolved,
    COUNT(*) FILTER (WHERE status = 'resolved') as manually_resolved,
    COUNT(*) FILTER (WHERE status IN ('open', 'assigned', 'in_progress')) as pending,
    COUNT(*) FILTER (WHERE priority IN ('critical', 'urgent')) as critical_urgent,
    AVG(priority_score) as avg_priority_score,
    AVG(time_to_first_response_minutes) FILTER (WHERE chatbot_resolved = false) as avg_first_response,
    AVG(time_to_resolution_minutes) FILTER (WHERE status = 'resolved') as avg_resolution,
    COUNT(*) FILTER (WHERE chatbot_attempted = true) as chatbot_attempted,
    AVG(confidence) FILTER (WHERE chatbot_resolved = true) as avg_chatbot_confidence
FROM support_tickets
WHERE created_at >= NOW() - INTERVAL '90 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_metrics_date ON mv_support_daily_metrics(date);

-- ============================================================================
-- VISTA MATERIALIZADA: Métricas por Agente
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_support_agent_metrics AS
SELECT 
    assigned_agent_id,
    assigned_agent_name,
    COUNT(*) as total_tickets,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved_tickets,
    AVG(time_to_resolution_minutes) FILTER (WHERE status = 'resolved') as avg_resolution_time,
    AVG(customer_satisfaction_score) FILTER (WHERE customer_satisfaction_score IS NOT NULL) as avg_satisfaction,
    COUNT(*) FILTER (WHERE priority IN ('critical', 'urgent')) as urgent_tickets_handled,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_tickets
FROM support_tickets
WHERE assigned_agent_id IS NOT NULL
AND created_at >= NOW() - INTERVAL '90 days'
GROUP BY assigned_agent_id, assigned_agent_name;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_agent_metrics_agent ON mv_support_agent_metrics(assigned_agent_id);

-- ============================================================================
-- FUNCIÓN: Actualizar estadísticas de agentes
-- ============================================================================
CREATE OR REPLACE FUNCTION update_agent_statistics()
RETURNS void AS $$
BEGIN
    UPDATE support_agents a
    SET 
        current_active_tickets = (
            SELECT COUNT(*)
            FROM support_tickets t
            WHERE t.assigned_agent_id = a.agent_id
            AND t.status IN ('open', 'assigned', 'in_progress')
        ),
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCIÓN: Buscar tickets similares
-- ============================================================================
CREATE OR REPLACE FUNCTION find_similar_tickets(
    p_description TEXT,
    p_limit INT DEFAULT 5
)
RETURNS TABLE (
    ticket_id VARCHAR(128),
    subject VARCHAR(512),
    description TEXT,
    priority VARCHAR(16),
    status VARCHAR(32),
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.ticket_id,
        t.subject,
        t.description,
        t.priority,
        t.status,
        ts_rank(
            to_tsvector('spanish', t.description),
            plainto_tsquery('spanish', p_description)
        ) as similarity_score
    FROM support_tickets t
    WHERE t.status = 'resolved'
    AND to_tsvector('spanish', t.description) @@ plainto_tsquery('spanish', p_description)
    ORDER BY similarity_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGER: Actualizar estadísticas cuando cambia un ticket
-- ============================================================================
CREATE OR REPLACE FUNCTION trigger_update_agent_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar estadísticas del agente si cambió la asignación
    IF OLD.assigned_agent_id IS DISTINCT FROM NEW.assigned_agent_id THEN
        PERFORM update_agent_statistics();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_agent_stats_on_ticket_change ON support_tickets;
CREATE TRIGGER trigger_update_agent_stats_on_ticket_change
    AFTER UPDATE ON support_tickets
    FOR EACH ROW
    WHEN (OLD.assigned_agent_id IS DISTINCT FROM NEW.assigned_agent_id)
    EXECUTE FUNCTION trigger_update_agent_stats();

COMMIT;

-- ============================================================================
-- REFRESH DE VISTAS MATERIALIZADAS (ejecutar periódicamente)
-- ============================================================================
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_support_daily_metrics;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_support_agent_metrics;

