-- ============================================================================
-- SCHEMA: Optimizaciones Avanzadas y Mejoras de Performance
-- ============================================================================
-- Mejoras adicionales:
-- - Particionado de tablas grandes
-- - Triggers avanzados para auditoría
-- - Materialized views para reportes rápidos
-- - Funciones de mantenimiento automático
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Auditoría Completa
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(128) NOT NULL,
    record_id VARCHAR(128) NOT NULL,
    action VARCHAR(32) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(256),
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_table_record 
    ON support_troubleshooting_audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_changed_at 
    ON support_troubleshooting_audit_log(changed_at);
CREATE INDEX IF NOT EXISTS idx_audit_action 
    ON support_troubleshooting_audit_log(action);

-- ============================================================================
-- 2. Función de Auditoría Genérica
-- ============================================================================
CREATE OR REPLACE FUNCTION audit_troubleshooting_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO support_troubleshooting_audit_log (
            table_name, record_id, action, new_values, changed_at
        ) VALUES (
            TG_TABLE_NAME,
            COALESCE(NEW.session_id::TEXT, NEW.id::TEXT, NEW.webhook_id::TEXT),
            'INSERT',
            row_to_json(NEW),
            NOW()
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO support_troubleshooting_audit_log (
            table_name, record_id, action, old_values, new_values, changed_at
        ) VALUES (
            TG_TABLE_NAME,
            COALESCE(NEW.session_id::TEXT, NEW.id::TEXT, NEW.webhook_id::TEXT),
            'UPDATE',
            row_to_json(OLD),
            row_to_json(NEW),
            NOW()
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO support_troubleshooting_audit_log (
            table_name, record_id, action, old_values, changed_at
        ) VALUES (
            TG_TABLE_NAME,
            COALESCE(OLD.session_id::TEXT, OLD.id::TEXT, OLD.webhook_id::TEXT),
            'DELETE',
            row_to_json(OLD),
            NOW()
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Aplicar auditoría a tablas principales
CREATE TRIGGER audit_sessions_changes
    AFTER INSERT OR UPDATE OR DELETE ON support_troubleshooting_sessions
    FOR EACH ROW EXECUTE FUNCTION audit_troubleshooting_changes();

CREATE TRIGGER audit_webhooks_changes
    AFTER INSERT OR UPDATE OR DELETE ON support_webhooks
    FOR EACH ROW EXECUTE FUNCTION audit_troubleshooting_changes();

-- ============================================================================
-- 3. Materialized Views para Reportes Rápidos
-- ============================================================================

-- Vista materializada de resumen diario
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_troubleshooting_summary AS
SELECT 
    DATE_TRUNC('day', started_at) as date,
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
    COUNT(CASE WHEN status = 'escalated' THEN 1 END) as escalated,
    COUNT(CASE WHEN status IN ('started', 'in_progress') THEN 1 END) as active,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, escalated_at, NOW()) - started_at)) / 60) as avg_duration_minutes,
    COUNT(DISTINCT detected_problem_id) as unique_problems,
    COUNT(DISTINCT customer_email) as unique_customers
FROM support_troubleshooting_sessions
WHERE started_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE_TRUNC('day', started_at);

CREATE UNIQUE INDEX ON mv_daily_troubleshooting_summary(date);
CREATE INDEX ON mv_daily_troubleshooting_summary(date DESC);

-- Vista materializada de problemas más comunes
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_problems AS
SELECT 
    detected_problem_id,
    detected_problem_title,
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_count,
    COUNT(CASE WHEN status = 'escalated' THEN 1 END) as escalated_count,
    ROUND(
        COUNT(CASE WHEN status = 'resolved' THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(*), 0)::NUMERIC * 100, 
        2
    ) as resolution_rate,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, escalated_at, NOW()) - started_at)) / 60) as avg_duration_minutes,
    MAX(started_at) as last_occurrence
FROM support_troubleshooting_sessions
WHERE detected_problem_id IS NOT NULL
  AND started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY detected_problem_id, detected_problem_title
HAVING COUNT(*) >= 3
ORDER BY total_sessions DESC;

CREATE UNIQUE INDEX ON mv_top_problems(detected_problem_id);

-- Vista materializada de feedback agregado
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_feedback_summary AS
SELECT 
    problem_detected_id,
    COUNT(*) as total_feedback,
    AVG(rating)::NUMERIC(3,2) as avg_rating,
    COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_count,
    COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_count,
    COUNT(CASE WHEN was_helpful = true THEN 1 END) as helpful_count,
    ROUND(
        COUNT(CASE WHEN was_helpful = true THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(*), 0)::NUMERIC * 100, 
        2
    ) as helpful_percentage,
    MAX(collected_at) as last_feedback
FROM support_troubleshooting_feedback
WHERE collected_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY problem_detected_id;

CREATE INDEX ON mv_feedback_summary(problem_detected_id);

-- ============================================================================
-- 4. Función para Refresh de Vistas Materializadas
-- ============================================================================
CREATE OR REPLACE FUNCTION refresh_troubleshooting_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_troubleshooting_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_problems;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_feedback_summary;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 5. Tabla de Cache para Resultados Costosos
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_cache (
    cache_key VARCHAR(256) PRIMARY KEY,
    cache_value JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    hit_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cache_expires_at 
    ON support_troubleshooting_cache(expires_at);

-- Función para limpiar cache expirado
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM support_troubleshooting_cache
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 6. Tabla de Límites y Rate Limiting
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_rate_limits (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(256) NOT NULL, -- email, IP, session_id
    limit_type VARCHAR(64) NOT NULL, -- session_per_hour, api_calls_per_minute
    current_count INTEGER DEFAULT 0,
    window_start TIMESTAMP NOT NULL DEFAULT NOW(),
    blocked_until TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(identifier, limit_type)
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_identifier 
    ON support_troubleshooting_rate_limits(identifier);
CREATE INDEX IF NOT EXISTS idx_rate_limits_window 
    ON support_troubleshooting_rate_limits(window_start);

-- Función para verificar y actualizar rate limits
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_identifier VARCHAR,
    p_limit_type VARCHAR,
    p_max_count INTEGER,
    p_window_minutes INTEGER DEFAULT 60
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_count INTEGER;
    v_window_start TIMESTAMP;
    v_blocked_until TIMESTAMP;
BEGIN
    -- Verificar si está bloqueado
    SELECT blocked_until INTO v_blocked_until
    FROM support_troubleshooting_rate_limits
    WHERE identifier = p_identifier AND limit_type = p_limit_type;
    
    IF v_blocked_until IS NOT NULL AND v_blocked_until > NOW() THEN
        RETURN FALSE; -- Bloqueado
    END IF;
    
    -- Obtener o crear registro
    INSERT INTO support_troubleshooting_rate_limits (
        identifier, limit_type, window_start, current_count
    ) VALUES (
        p_identifier, p_limit_type, NOW(), 1
    )
    ON CONFLICT (identifier, limit_type) DO UPDATE SET
        current_count = CASE 
            WHEN window_start < NOW() - (p_window_minutes || ' minutes')::INTERVAL 
            THEN 1 
            ELSE current_count + 1 
        END,
        window_start = CASE 
            WHEN window_start < NOW() - (p_window_minutes || ' minutes')::INTERVAL 
            THEN NOW() 
            ELSE window_start 
        END,
        updated_at = NOW()
    RETURNING current_count, window_start INTO v_current_count, v_window_start;
    
    -- Verificar límite
    IF v_current_count > p_max_count THEN
        -- Bloquear por 1 hora
        UPDATE support_troubleshooting_rate_limits
        SET blocked_until = NOW() + INTERVAL '1 hour'
        WHERE identifier = p_identifier AND limit_type = p_limit_type;
        RETURN FALSE;
    END IF;
    
    RETURN TRUE; -- Permitido
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. Tabla de Métricas de Performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(128) NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_unit VARCHAR(32), -- milliseconds, count, percentage
    context JSONB DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_performance_metric_name 
    ON support_troubleshooting_performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_recorded_at 
    ON support_troubleshooting_performance_metrics(recorded_at);

-- ============================================================================
-- 8. Función para Obtener Estadísticas de Performance
-- ============================================================================
CREATE OR REPLACE FUNCTION get_performance_stats(
    p_metric_name VARCHAR,
    p_hours INTEGER DEFAULT 24
)
RETURNS TABLE (
    avg_value NUMERIC,
    min_value NUMERIC,
    max_value NUMERIC,
    p95_value NUMERIC,
    sample_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        AVG(metric_value)::NUMERIC as avg_value,
        MIN(metric_value)::NUMERIC as min_value,
        MAX(metric_value)::NUMERIC as max_value,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY metric_value)::NUMERIC as p95_value,
        COUNT(*)::BIGINT as sample_count
    FROM support_troubleshooting_performance_metrics
    WHERE metric_name = p_metric_name
      AND recorded_at >= NOW() - (p_hours || ' hours')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 9. Job de Mantenimiento Automático
-- ============================================================================
CREATE OR REPLACE FUNCTION maintenance_troubleshooting_tables()
RETURNS TABLE (
    task VARCHAR,
    result TEXT,
    rows_affected BIGINT
) AS $$
DECLARE
    v_deleted_count BIGINT;
    v_refreshed_count INTEGER;
BEGIN
    -- Limpiar cache expirado
    SELECT cleanup_expired_cache() INTO v_deleted_count;
    RETURN QUERY SELECT 'cleanup_cache'::VARCHAR, 'OK'::TEXT, v_deleted_count::BIGINT;
    
    -- Refresh vistas materializadas
    PERFORM refresh_troubleshooting_views();
    RETURN QUERY SELECT 'refresh_views'::VARCHAR, 'OK'::TEXT, 0::BIGINT;
    
    -- Limpiar rate limits antiguos (más de 7 días)
    DELETE FROM support_troubleshooting_rate_limits
    WHERE window_start < NOW() - INTERVAL '7 days'
      AND blocked_until IS NULL;
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN QUERY SELECT 'cleanup_rate_limits'::VARCHAR, 'OK'::TEXT, v_deleted_count::BIGINT;
    
    -- Limpiar métricas antiguas (más de 90 días)
    DELETE FROM support_troubleshooting_performance_metrics
    WHERE recorded_at < NOW() - INTERVAL '90 days';
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN QUERY SELECT 'cleanup_metrics'::VARCHAR, 'OK'::TEXT, v_deleted_count::BIGINT;
    
    -- Vacuum y analyze tablas principales
    -- Nota: VACUUM no puede ejecutarse en función, debe hacerse manualmente o con pg_cron
    RETURN QUERY SELECT 'vacuum_recommended'::VARCHAR, 'Run VACUUM ANALYZE manually'::TEXT, 0::BIGINT;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 10. Índices Adicionales para Consultas Comunes
-- ============================================================================

-- Índice compuesto para búsquedas por cliente y fecha
CREATE INDEX IF NOT EXISTS idx_sessions_customer_date 
    ON support_troubleshooting_sessions(customer_email, started_at DESC);

-- Índice para búsquedas por problema y estado
CREATE INDEX IF NOT EXISTS idx_sessions_problem_status 
    ON support_troubleshooting_sessions(detected_problem_id, status) 
    WHERE detected_problem_id IS NOT NULL;

-- Índice parcial para sesiones activas (más eficiente)
CREATE INDEX IF NOT EXISTS idx_sessions_active 
    ON support_troubleshooting_sessions(started_at DESC) 
    WHERE status IN ('started', 'in_progress');

-- Índice GIN para búsqueda en JSONB
CREATE INDEX IF NOT EXISTS idx_sessions_metadata_gin 
    ON support_troubleshooting_sessions USING GIN(metadata);

CREATE INDEX IF NOT EXISTS idx_feedback_context_gin 
    ON support_troubleshooting_feedback USING GIN(metadata);

-- ============================================================================
-- 11. Función para Búsqueda Full-Text en Descripciones
-- ============================================================================
CREATE OR REPLACE FUNCTION search_troubleshooting_sessions(
    p_search_text TEXT,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    session_id VARCHAR,
    customer_email VARCHAR,
    problem_description TEXT,
    detected_problem_title VARCHAR,
    status VARCHAR,
    started_at TIMESTAMP,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.session_id,
        s.customer_email,
        s.problem_description,
        s.detected_problem_title,
        s.status,
        s.started_at,
        ts_rank(
            to_tsvector('spanish', COALESCE(s.problem_description, '') || ' ' || COALESCE(s.detected_problem_title, '')),
            plainto_tsquery('spanish', p_search_text)
        ) as rank
    FROM support_troubleshooting_sessions s
    WHERE 
        to_tsvector('spanish', COALESCE(s.problem_description, '') || ' ' || COALESCE(s.detected_problem_title, ''))
        @@ plainto_tsquery('spanish', p_search_text)
    ORDER BY rank DESC, s.started_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Índice para búsqueda full-text
CREATE INDEX IF NOT EXISTS idx_sessions_fts 
    ON support_troubleshooting_sessions 
    USING GIN(to_tsvector('spanish', COALESCE(problem_description, '') || ' ' || COALESCE(detected_problem_title, '')));

COMMIT;

-- ============================================================================
-- COMENTARIOS
-- ============================================================================
COMMENT ON TABLE support_troubleshooting_audit_log IS 
    'Log completo de auditoría para todas las operaciones';
COMMENT ON MATERIALIZED VIEW mv_daily_troubleshooting_summary IS 
    'Resumen diario optimizado para reportes rápidos';
COMMENT ON MATERIALIZED VIEW mv_top_problems IS 
    'Problemas más comunes con estadísticas agregadas';
COMMENT ON MATERIALIZED VIEW mv_feedback_summary IS 
    'Resumen de feedback por problema';
COMMENT ON FUNCTION refresh_troubleshooting_views IS 
    'Refresca todas las vistas materializadas';
COMMENT ON FUNCTION check_rate_limit IS 
    'Verifica y actualiza rate limits';
COMMENT ON FUNCTION maintenance_troubleshooting_tables IS 
    'Ejecuta tareas de mantenimiento automático';
COMMENT ON FUNCTION search_troubleshooting_sessions IS 
    'Búsqueda full-text en sesiones de troubleshooting';



