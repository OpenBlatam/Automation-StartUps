-- ============================================================================
-- EXTENSIONES AVANZADAS AL SCHEMA DE TROUBLESHOOTING
-- ============================================================================
-- Este archivo contiene mejoras adicionales:
-- - Particionamiento de tablas grandes
-- - Sistema de caché
-- - Funciones de exportación
-- - Mantenimiento automático
-- - Integración con otros sistemas
-- - Análisis avanzado
-- ============================================================================

BEGIN;

-- ============================================================================
-- 19. PARTICIONAMIENTO DE TABLAS GRANDES
-- ============================================================================

-- Función para crear particiones mensuales de historial de intentos
CREATE OR REPLACE FUNCTION create_troubleshooting_attempts_partition(
    partition_date DATE
)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_name := 'support_troubleshooting_attempts_' || 
                      TO_CHAR(partition_date, 'YYYY_MM');
    start_date := DATE_TRUNC('month', partition_date);
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I PARTITION OF support_troubleshooting_attempts
        FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
    
    -- Crear índices en la partición
    EXECUTE format('
        CREATE INDEX IF NOT EXISTS %I ON %I(session_id, step_number)',
        partition_name || '_idx', partition_name
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 20. SISTEMA DE CACHÉ
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_troubleshooting_cache (
    cache_key VARCHAR(256) PRIMARY KEY,
    cache_value JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_troubleshooting_cache_expires 
    ON support_troubleshooting_cache(expires_at) 
    WHERE expires_at > NOW();

CREATE OR REPLACE FUNCTION cleanup_troubleshooting_cache()
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
-- 21. FUNCIONES DE EXPORTACIÓN
-- ============================================================================

CREATE OR REPLACE FUNCTION export_troubleshooting_sessions_json(
    start_date TIMESTAMP DEFAULT NOW() - INTERVAL '30 days',
    end_date TIMESTAMP DEFAULT NOW(),
    include_attempts BOOLEAN DEFAULT TRUE
)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_agg(
        jsonb_build_object(
            'session_id', s.session_id,
            'ticket_id', s.ticket_id,
            'customer_email', s.customer_email,
            'problem_description', s.problem_description,
            'status', s.status,
            'started_at', s.started_at,
            'resolved_at', s.resolved_at,
            'total_duration_seconds', s.total_duration_seconds,
            'customer_satisfaction_score', s.customer_satisfaction_score,
            'attempts', CASE 
                WHEN include_attempts THEN (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'step_number', a.step_number,
                            'success', a.success,
                            'attempted_at', a.attempted_at
                        )
                    )
                    FROM support_troubleshooting_attempts a
                    WHERE a.session_id = s.session_id
                )
                ELSE NULL
            END
        )
    ) INTO result
    FROM support_troubleshooting_sessions s
    WHERE s.started_at BETWEEN start_date AND end_date;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 22. MANTENIMIENTO AUTOMÁTICO
-- ============================================================================

CREATE OR REPLACE FUNCTION maintenance_troubleshooting_tables()
RETURNS TABLE (
    operation VARCHAR,
    status VARCHAR,
    details TEXT
) AS $$
BEGIN
    PERFORM cleanup_troubleshooting_cache();
    
    RETURN QUERY SELECT 
        'CACHE CLEANUP'::VARCHAR,
        'completed'::VARCHAR,
        format('Cleaned cache entries')::TEXT;
    
    PERFORM refresh_troubleshooting_daily_stats();
    
    RETURN QUERY SELECT 
        'REFRESH MATERIALIZED VIEWS'::VARCHAR,
        'completed'::VARCHAR,
        'Materialized views refreshed'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 23. VERIFICACIÓN DE INTEGRIDAD
-- ============================================================================

CREATE OR REPLACE FUNCTION verify_troubleshooting_data_integrity()
RETURNS TABLE (
    check_name VARCHAR,
    status VARCHAR,
    issue_count INTEGER,
    details TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'step_inconsistencies'::VARCHAR,
        CASE WHEN COUNT(*) > 0 THEN 'warning' ELSE 'ok' END::VARCHAR,
        COUNT(*)::INTEGER,
        format('Found %s sessions where current_step > total_steps', COUNT(*))::TEXT
    FROM support_troubleshooting_sessions
    WHERE current_step > total_steps;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 24. ANÁLISIS AVANZADO
-- ============================================================================

CREATE OR REPLACE FUNCTION analyze_troubleshooting_cohorts(
    cohort_period VARCHAR DEFAULT 'month'
)
RETURNS TABLE (
    cohort_period TEXT,
    total_sessions INTEGER,
    resolved_sessions INTEGER,
    avg_resolution_time NUMERIC,
    retention_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        TO_CHAR(DATE_TRUNC(cohort_period::TEXT, started_at), 'YYYY-MM') as cohort_period,
        COUNT(*)::INTEGER as total_sessions,
        COUNT(*) FILTER (WHERE status = 'resolved')::INTEGER as resolved_sessions,
        AVG(total_duration_seconds / 60.0)::NUMERIC as avg_resolution_time,
        (COUNT(*) FILTER (WHERE status = 'resolved')::NUMERIC / 
         NULLIF(COUNT(*), 0)::NUMERIC * 100)::NUMERIC as retention_rate
    FROM support_troubleshooting_sessions
    GROUP BY DATE_TRUNC(cohort_period::TEXT, started_at)
    ORDER BY DATE_TRUNC(cohort_period::TEXT, started_at) DESC;
END;
$$ LANGUAGE plpgsql;

COMMIT;



