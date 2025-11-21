-- ============================================================================
-- SCHEMA: Mejoras Avanzadas para Troubleshooting
-- ============================================================================
-- Mejoras adicionales al esquema base:
-- - Tabla de notificaciones
-- - Tabla de aprendizaje automático
-- - Tabla de reportes
-- - Índices optimizados
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Notificaciones
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_notifications (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(128) NOT NULL,
    notification_type VARCHAR(64) NOT NULL, -- email, sms, push, slack, etc.
    recipient VARCHAR(256) NOT NULL,
    subject VARCHAR(512),
    message TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'sent', 'failed', 'delivered', 'read')),
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_session FOREIGN KEY (session_id) 
        REFERENCES support_troubleshooting_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notifications_session_id 
    ON support_troubleshooting_notifications(session_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status 
    ON support_troubleshooting_notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_type 
    ON support_troubleshooting_notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at 
    ON support_troubleshooting_notifications(created_at);

-- ============================================================================
-- 2. Tabla de Aprendizaje Automático Mejorada
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_ml_training (
    id SERIAL PRIMARY KEY,
    problem_description TEXT NOT NULL,
    detected_problem_id VARCHAR(128),
    actual_problem_id VARCHAR(128),
    confidence_score NUMERIC(5,2),
    correction_source VARCHAR(64), -- 'agent', 'customer_feedback', 'auto'
    corrected_by VARCHAR(256),
    correction_notes TEXT,
    training_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    used_for_training BOOLEAN DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_ml_training_detected 
    ON support_troubleshooting_ml_training(detected_problem_id);
CREATE INDEX IF NOT EXISTS idx_ml_training_actual 
    ON support_troubleshooting_ml_training(actual_problem_id);
CREATE INDEX IF NOT EXISTS idx_ml_training_used 
    ON support_troubleshooting_ml_training(used_for_training);

-- ============================================================================
-- 3. Tabla de Reportes Personalizados
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(128) UNIQUE NOT NULL,
    report_name VARCHAR(256) NOT NULL,
    report_type VARCHAR(64) NOT NULL, -- daily, weekly, monthly, custom
    created_by VARCHAR(256),
    parameters JSONB DEFAULT '{}'::jsonb,
    report_data JSONB NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_reports_report_id 
    ON support_troubleshooting_reports(report_id);
CREATE INDEX IF NOT EXISTS idx_reports_type 
    ON support_troubleshooting_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_generated_at 
    ON support_troubleshooting_reports(generated_at);

-- ============================================================================
-- 4. Tabla de Configuración del Sistema
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(128) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(32) DEFAULT 'string', -- string, number, boolean, json
    description TEXT,
    updated_by VARCHAR(256),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_config_key 
    ON support_troubleshooting_config(config_key);

-- Insertar configuraciones por defecto
INSERT INTO support_troubleshooting_config (config_key, config_value, config_type, description)
VALUES 
    ('auto_escalate_after_failures', '2', 'number', 'Número de pasos fallidos antes de escalar automáticamente'),
    ('default_timeout_minutes', '30', 'number', 'Timeout por defecto para sesiones (minutos)'),
    ('enable_llm_enhancement', 'true', 'boolean', 'Habilitar mejoras con LLM'),
    ('feedback_collection_enabled', 'true', 'boolean', 'Habilitar recolección de feedback'),
    ('notification_channels', '["email"]', 'json', 'Canales de notificación habilitados'),
    ('max_session_duration_hours', '24', 'number', 'Duración máxima de sesión (horas)')
ON CONFLICT (config_key) DO NOTHING;

-- ============================================================================
-- 5. Vista de Métricas en Tiempo Real
-- ============================================================================
CREATE OR REPLACE VIEW vw_troubleshooting_realtime_metrics AS
SELECT 
    COUNT(*) FILTER (WHERE status = 'started' OR status = 'in_progress') as active_sessions,
    COUNT(*) FILTER (WHERE status = 'resolved' AND resolved_at >= NOW() - INTERVAL '1 hour') as resolved_last_hour,
    COUNT(*) FILTER (WHERE status = 'escalated' AND escalated_at >= NOW() - INTERVAL '1 hour') as escalated_last_hour,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, escalated_at, NOW()) - started_at)) / 60) FILTER (WHERE resolved_at >= NOW() - INTERVAL '24 hours' OR escalated_at >= NOW() - INTERVAL '24 hours') as avg_resolution_time_minutes,
    COUNT(DISTINCT detected_problem_id) FILTER (WHERE started_at >= NOW() - INTERVAL '24 hours') as unique_problems_24h,
    (SELECT COUNT(*) FROM support_troubleshooting_feedback WHERE collected_at >= NOW() - INTERVAL '24 hours') as feedback_count_24h,
    (SELECT AVG(rating) FROM support_troubleshooting_feedback WHERE collected_at >= NOW() - INTERVAL '24 hours') as avg_rating_24h
FROM support_troubleshooting_sessions
WHERE started_at >= NOW() - INTERVAL '7 days';

-- ============================================================================
-- 6. Función para Obtener Métricas por Período
-- ============================================================================
CREATE OR REPLACE FUNCTION get_troubleshooting_metrics_by_period(
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    group_by VARCHAR DEFAULT 'day' -- day, hour, week
)
RETURNS TABLE (
    period_label VARCHAR,
    total_sessions BIGINT,
    resolved_sessions BIGINT,
    escalated_sessions BIGINT,
    resolution_rate NUMERIC,
    avg_duration_minutes NUMERIC,
    avg_rating NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE 
            WHEN group_by = 'hour' THEN TO_CHAR(DATE_TRUNC('hour', s.started_at), 'YYYY-MM-DD HH24:MI')
            WHEN group_by = 'week' THEN TO_CHAR(DATE_TRUNC('week', s.started_at), 'YYYY-"W"IW')
            ELSE TO_CHAR(DATE_TRUNC('day', s.started_at), 'YYYY-MM-DD')
        END as period_label,
        COUNT(*)::BIGINT as total_sessions,
        COUNT(CASE WHEN s.status = 'resolved' THEN 1 END)::BIGINT as resolved_sessions,
        COUNT(CASE WHEN s.status = 'escalated' THEN 1 END)::BIGINT as escalated_sessions,
        ROUND(
            COUNT(CASE WHEN s.status = 'resolved' THEN 1 END)::NUMERIC / 
            NULLIF(COUNT(*), 0)::NUMERIC * 100, 
            2
        ) as resolution_rate,
        AVG(EXTRACT(EPOCH FROM (COALESCE(s.resolved_at, s.escalated_at, NOW()) - s.started_at)) / 60)::NUMERIC as avg_duration_minutes,
        (SELECT AVG(rating) FROM support_troubleshooting_feedback f 
         WHERE f.session_id = s.session_id 
         AND f.collected_at BETWEEN period_start AND period_end)::NUMERIC(3,2) as avg_rating
    FROM support_troubleshooting_sessions s
    WHERE s.started_at BETWEEN period_start AND period_end
    GROUP BY 
        CASE 
            WHEN group_by = 'hour' THEN DATE_TRUNC('hour', s.started_at)
            WHEN group_by = 'week' THEN DATE_TRUNC('week', s.started_at)
            ELSE DATE_TRUNC('day', s.started_at)
        END
    ORDER BY period_label;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. Función para Limpiar Datos Antiguos
-- ============================================================================
CREATE OR REPLACE FUNCTION cleanup_old_troubleshooting_data(
    days_to_keep INTEGER DEFAULT 90
)
RETURNS TABLE (
    table_name VARCHAR,
    deleted_count BIGINT
) AS $$
DECLARE
    cutoff_date TIMESTAMP;
BEGIN
    cutoff_date := NOW() - (days_to_keep || ' days')::INTERVAL;
    
    RETURN QUERY
    SELECT 
        'support_troubleshooting_sessions'::VARCHAR,
        COUNT(*)::BIGINT
    FROM support_troubleshooting_sessions
    WHERE started_at < cutoff_date
      AND status IN ('resolved', 'closed', 'escalated');
    
    -- Nota: En producción, ejecutar DELETE real aquí
    -- DELETE FROM support_troubleshooting_sessions 
    -- WHERE started_at < cutoff_date AND status IN ('resolved', 'closed', 'escalated');
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 8. Trigger para Actualizar Timestamps
-- ============================================================================
CREATE OR REPLACE FUNCTION update_troubleshooting_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_config_timestamp
    BEFORE UPDATE ON support_troubleshooting_config
    FOR EACH ROW
    EXECUTE FUNCTION update_troubleshooting_timestamp();

-- ============================================================================
-- 9. Índices Adicionales para Performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_sessions_status_started_at 
    ON support_troubleshooting_sessions(status, started_at);
CREATE INDEX IF NOT EXISTS idx_sessions_customer_email_status 
    ON support_troubleshooting_sessions(customer_email, status);
CREATE INDEX IF NOT EXISTS idx_attempts_session_success 
    ON support_troubleshooting_attempts(session_id, success);
CREATE INDEX IF NOT EXISTS idx_feedback_rating_collected_at 
    ON support_troubleshooting_feedback(rating, collected_at);

COMMIT;

-- ============================================================================
-- COMENTARIOS
-- ============================================================================
COMMENT ON TABLE support_troubleshooting_notifications IS 
    'Notificaciones enviadas a clientes y agentes';
COMMENT ON TABLE support_troubleshooting_ml_training IS 
    'Datos de entrenamiento para mejorar detección automática';
COMMENT ON TABLE support_troubleshooting_reports IS 
    'Reportes personalizados generados';
COMMENT ON TABLE support_troubleshooting_config IS 
    'Configuración del sistema de troubleshooting';
COMMENT ON VIEW vw_troubleshooting_realtime_metrics IS 
    'Métricas en tiempo real del sistema';
COMMENT ON FUNCTION get_troubleshooting_metrics_by_period IS 
    'Obtiene métricas agrupadas por período de tiempo';
COMMENT ON FUNCTION cleanup_old_troubleshooting_data IS 
    'Limpia datos antiguos del sistema';



