-- ============================================================================
-- SCHEMA: Sistema de Feedback para Troubleshooting
-- ============================================================================
-- Este esquema soporta:
-- - Recolección de feedback de clientes
-- - Análisis de satisfacción
-- - Métricas de efectividad
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Feedback
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_feedback (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(128) NOT NULL,
    ticket_id VARCHAR(128),
    customer_email VARCHAR(256) NOT NULL,
    
    -- Feedback
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    was_helpful BOOLEAN,
    
    -- Contexto
    problem_detected_id VARCHAR(128),
    total_steps INTEGER,
    completed_steps INTEGER,
    resolved BOOLEAN,
    
    -- Metadatos
    collected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT fk_session FOREIGN KEY (session_id) 
        REFERENCES support_troubleshooting_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket FOREIGN KEY (ticket_id) 
        REFERENCES support_tickets(ticket_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_troubleshooting_feedback_session_id 
    ON support_troubleshooting_feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_troubleshooting_feedback_rating 
    ON support_troubleshooting_feedback(rating);
CREATE INDEX IF NOT EXISTS idx_troubleshooting_feedback_collected_at 
    ON support_troubleshooting_feedback(collected_at);

-- ============================================================================
-- 2. Vista de Resumen de Feedback
-- ============================================================================
CREATE OR REPLACE VIEW vw_troubleshooting_feedback_summary AS
SELECT 
    DATE_TRUNC('day', collected_at) as date,
    COUNT(*) as total_feedback,
    AVG(rating)::NUMERIC(3,2) as average_rating,
    COUNT(CASE WHEN was_helpful = true THEN 1 END) as helpful_count,
    COUNT(CASE WHEN resolved = true THEN 1 END) as resolved_count,
    COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback_count
FROM support_troubleshooting_feedback
GROUP BY DATE_TRUNC('day', collected_at)
ORDER BY date DESC;

-- ============================================================================
-- 3. Función para Obtener Feedback por Problema
-- ============================================================================
CREATE OR REPLACE FUNCTION get_feedback_by_problem(
    start_date TIMESTAMP DEFAULT NOW() - INTERVAL '30 days',
    end_date TIMESTAMP DEFAULT NOW()
)
RETURNS TABLE (
    problem_id VARCHAR,
    total_feedback BIGINT,
    average_rating NUMERIC,
    helpful_percentage NUMERIC,
    resolution_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.problem_detected_id::VARCHAR as problem_id,
        COUNT(*)::BIGINT as total_feedback,
        AVG(f.rating)::NUMERIC(3,2) as average_rating,
        (COUNT(CASE WHEN f.was_helpful = true THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100)::NUMERIC(5,2) as helpful_percentage,
        (COUNT(CASE WHEN f.resolved = true THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100)::NUMERIC(5,2) as resolution_rate
    FROM support_troubleshooting_feedback f
    WHERE f.collected_at BETWEEN start_date AND end_date
      AND f.problem_detected_id IS NOT NULL
    GROUP BY f.problem_detected_id
    ORDER BY total_feedback DESC;
END;
$$ LANGUAGE plpgsql;

COMMIT;

COMMENT ON TABLE support_troubleshooting_feedback IS 
    'Feedback de clientes sobre sesiones de troubleshooting';
COMMENT ON VIEW vw_troubleshooting_feedback_summary IS 
    'Resumen diario de feedback de troubleshooting';
COMMENT ON FUNCTION get_feedback_by_problem IS 
    'Obtiene estadísticas de feedback agrupadas por problema';



