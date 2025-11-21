-- ============================================================================
-- SCHEMA: Funciones SQL Adicionales y Optimizaciones Finales
-- ============================================================================
-- Funciones útiles adicionales para análisis y optimización
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Función para Análisis de Tendencias Temporales
-- ============================================================================
CREATE OR REPLACE FUNCTION analyze_troubleshooting_trends(
    p_days INTEGER DEFAULT 30,
    p_group_by VARCHAR DEFAULT 'day' -- day, week, month
)
RETURNS TABLE (
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    total_sessions BIGINT,
    resolution_rate NUMERIC,
    escalation_rate NUMERIC,
    avg_duration_minutes NUMERIC,
    trend_direction VARCHAR -- increasing, decreasing, stable
) AS $$
DECLARE
    v_previous_rate NUMERIC;
BEGIN
    RETURN QUERY
    WITH period_stats AS (
        SELECT 
            CASE 
                WHEN p_group_by = 'week' THEN DATE_TRUNC('week', s.started_at)
                WHEN p_group_by = 'month' THEN DATE_TRUNC('month', s.started_at)
                ELSE DATE_TRUNC('day', s.started_at)
            END as period_start,
            COUNT(*) as total_sessions,
            COUNT(CASE WHEN s.status = 'resolved' THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)::NUMERIC * 100 as resolution_rate,
            COUNT(CASE WHEN s.status = 'escalated' THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)::NUMERIC * 100 as escalation_rate,
            AVG(EXTRACT(EPOCH FROM (COALESCE(s.resolved_at, s.escalated_at, NOW()) - s.started_at)) / 60) as avg_duration_minutes
        FROM support_troubleshooting_sessions s
        WHERE s.started_at >= NOW() - (p_days || ' days')::INTERVAL
        GROUP BY 
            CASE 
                WHEN p_group_by = 'week' THEN DATE_TRUNC('week', s.started_at)
                WHEN p_group_by = 'month' THEN DATE_TRUNC('month', s.started_at)
                ELSE DATE_TRUNC('day', s.started_at)
            END
        ORDER BY period_start
    ),
    trend_analysis AS (
        SELECT 
            ps.*,
            CASE 
                WHEN p_group_by = 'week' THEN ps.period_start + INTERVAL '6 days'
                WHEN p_group_by = 'month' THEN ps.period_start + INTERVAL '1 month' - INTERVAL '1 day'
                ELSE ps.period_start + INTERVAL '1 day' - INTERVAL '1 second'
            END as period_end,
            LAG(ps.resolution_rate) OVER (ORDER BY ps.period_start) as prev_resolution_rate,
            CASE 
                WHEN ps.resolution_rate > LAG(ps.resolution_rate) OVER (ORDER BY ps.period_start) + 5 THEN 'increasing'
                WHEN ps.resolution_rate < LAG(ps.resolution_rate) OVER (ORDER BY ps.period_start) - 5 THEN 'decreasing'
                ELSE 'stable'
            END as trend_direction
        FROM period_stats ps
    )
    SELECT 
        ta.period_start,
        ta.period_end,
        ta.total_sessions,
        ROUND(ta.resolution_rate, 2) as resolution_rate,
        ROUND(ta.escalation_rate, 2) as escalation_rate,
        ROUND(ta.avg_duration_minutes::NUMERIC, 2) as avg_duration_minutes,
        COALESCE(ta.trend_direction, 'stable') as trend_direction
    FROM trend_analysis ta
    ORDER BY ta.period_start;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 2. Función para Identificar Problemas que Necesitan Mejora
-- ============================================================================
CREATE OR REPLACE FUNCTION identify_problems_needing_improvement(
    p_min_sessions INTEGER DEFAULT 5,
    p_max_resolution_rate NUMERIC DEFAULT 70.0
)
RETURNS TABLE (
    problem_id VARCHAR,
    problem_title VARCHAR,
    total_sessions BIGINT,
    resolution_rate NUMERIC,
    escalation_rate NUMERIC,
    avg_duration_minutes NUMERIC,
    common_failed_step INTEGER,
    recommendation TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH problem_stats AS (
        SELECT 
            s.detected_problem_id,
            s.detected_problem_title,
            COUNT(*) as total_sessions,
            COUNT(CASE WHEN s.status = 'resolved' THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)::NUMERIC * 100 as resolution_rate,
            COUNT(CASE WHEN s.status = 'escalated' THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)::NUMERIC * 100 as escalation_rate,
            AVG(EXTRACT(EPOCH FROM (COALESCE(s.resolved_at, s.escalated_at, NOW()) - s.started_at)) / 60) as avg_duration_minutes
        FROM support_troubleshooting_sessions s
        WHERE s.detected_problem_id IS NOT NULL
          AND s.started_at >= NOW() - INTERVAL '30 days'
        GROUP BY s.detected_problem_id, s.detected_problem_title
        HAVING COUNT(*) >= p_min_sessions
    ),
    failed_steps AS (
        SELECT 
            s.detected_problem_id,
            a.step_number,
            COUNT(*) as failure_count
        FROM support_troubleshooting_sessions s
        JOIN support_troubleshooting_attempts a ON s.session_id = a.session_id
        WHERE a.success = false
          AND s.started_at >= NOW() - INTERVAL '30 days'
        GROUP BY s.detected_problem_id, a.step_number
    ),
    most_failed_step AS (
        SELECT 
            fs.detected_problem_id,
            fs.step_number,
            ROW_NUMBER() OVER (PARTITION BY fs.detected_problem_id ORDER BY fs.failure_count DESC) as rn
        FROM failed_steps fs
    )
    SELECT 
        ps.detected_problem_id::VARCHAR,
        ps.detected_problem_title::VARCHAR,
        ps.total_sessions::BIGINT,
        ROUND(ps.resolution_rate::NUMERIC, 2) as resolution_rate,
        ROUND(ps.escalation_rate::NUMERIC, 2) as escalation_rate,
        ROUND(ps.avg_duration_minutes::NUMERIC, 2) as avg_duration_minutes,
        mfs.step_number::INTEGER as common_failed_step,
        CASE 
            WHEN ps.resolution_rate < 50 THEN 'Revisar completamente la guía de troubleshooting'
            WHEN ps.resolution_rate < p_max_resolution_rate THEN 'Mejorar instrucciones del paso ' || mfs.step_number::TEXT
            WHEN ps.escalation_rate > 40 THEN 'Considerar simplificar pasos o agregar más recursos'
            WHEN ps.avg_duration_minutes > 30 THEN 'Optimizar pasos para reducir tiempo de resolución'
            ELSE 'Monitorear y ajustar según feedback'
        END::TEXT as recommendation
    FROM problem_stats ps
    LEFT JOIN most_failed_step mfs ON ps.detected_problem_id = mfs.detected_problem_id AND mfs.rn = 1
    WHERE ps.resolution_rate < p_max_resolution_rate
    ORDER BY ps.resolution_rate ASC, ps.total_sessions DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 3. Función para Análisis de Satisfacción del Cliente
-- ============================================================================
CREATE OR REPLACE FUNCTION analyze_customer_satisfaction(
    p_days INTEGER DEFAULT 30
)
RETURNS TABLE (
    problem_id VARCHAR,
    problem_title VARCHAR,
    total_feedback BIGINT,
    avg_rating NUMERIC,
    nps_score NUMERIC,
    helpful_percentage NUMERIC,
    improvement_priority INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH feedback_stats AS (
        SELECT 
            f.problem_detected_id,
            COUNT(*) as total_feedback,
            AVG(f.rating) as avg_rating,
            COUNT(CASE WHEN f.rating >= 4 THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)::NUMERIC * 100 as promoters,
            COUNT(CASE WHEN f.rating <= 2 THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)::NUMERIC * 100 as detractors,
            COUNT(CASE WHEN f.was_helpful = true THEN 1 END)::NUMERIC / NULLIF(COUNT(*), 0)::NUMERIC * 100 as helpful_percentage
        FROM support_troubleshooting_feedback f
        WHERE f.collected_at >= NOW() - (p_days || ' days')::INTERVAL
          AND f.problem_detected_id IS NOT NULL
        GROUP BY f.problem_detected_id
        HAVING COUNT(*) >= 3
    ),
    problem_titles AS (
        SELECT DISTINCT 
            detected_problem_id,
            detected_problem_title
        FROM support_troubleshooting_sessions
        WHERE detected_problem_id IS NOT NULL
    )
    SELECT 
        fs.problem_detected_id::VARCHAR,
        COALESCE(pt.detected_problem_title, fs.problem_detected_id)::VARCHAR as problem_title,
        fs.total_feedback::BIGINT,
        ROUND(fs.avg_rating::NUMERIC, 2) as avg_rating,
        ROUND((fs.promoters - fs.detractors)::NUMERIC, 2) as nps_score,
        ROUND(fs.helpful_percentage::NUMERIC, 2) as helpful_percentage,
        CASE 
            WHEN fs.avg_rating < 3.0 THEN 1
            WHEN fs.avg_rating < 4.0 THEN 2
            ELSE 3
        END::INTEGER as improvement_priority
    FROM feedback_stats fs
    LEFT JOIN problem_titles pt ON fs.problem_detected_id = pt.detected_problem_id
    ORDER BY improvement_priority ASC, fs.avg_rating ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 4. Función para Optimización Automática de Queries
-- ============================================================================
CREATE OR REPLACE FUNCTION optimize_troubleshooting_tables()
RETURNS TABLE (
    table_name VARCHAR,
    action_taken VARCHAR,
    rows_affected BIGINT,
    execution_time_ms NUMERIC
) AS $$
DECLARE
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
    v_rows BIGINT;
BEGIN
    -- Vacuum y Analyze en tablas principales
    FOR table_name IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename LIKE 'support_troubleshooting%'
    LOOP
        v_start_time := clock_timestamp();
        
        EXECUTE format('VACUUM ANALYZE %I', table_name);
        
        GET DIAGNOSTICS v_rows = ROW_COUNT;
        v_end_time := clock_timestamp();
        
        RETURN QUERY SELECT 
            table_name::VARCHAR,
            'VACUUM ANALYZE'::VARCHAR,
            v_rows::BIGINT,
            EXTRACT(EPOCH FROM (v_end_time - v_start_time)) * 1000::NUMERIC;
    END LOOP;
    
    -- Refresh vistas materializadas
    FOR table_name IN 
        SELECT matviewname FROM pg_matviews 
        WHERE schemaname = 'public' 
        AND matviewname LIKE 'mv_%troubleshooting%'
    LOOP
        v_start_time := clock_timestamp();
        
        EXECUTE format('REFRESH MATERIALIZED VIEW CONCURRENTLY %I', table_name);
        
        v_end_time := clock_timestamp();
        
        RETURN QUERY SELECT 
            table_name::VARCHAR,
            'REFRESH MATERIALIZED VIEW'::VARCHAR,
            0::BIGINT,
            EXTRACT(EPOCH FROM (v_end_time - v_start_time)) * 1000::NUMERIC;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 5. Vista de Resumen Ejecutivo
-- ============================================================================
CREATE OR REPLACE VIEW vw_executive_summary AS
SELECT 
    -- Métricas generales
    (SELECT COUNT(*) FROM support_troubleshooting_sessions 
     WHERE started_at >= CURRENT_DATE - INTERVAL '30 days') as total_sessions_30d,
    
    (SELECT COUNT(*) FROM support_troubleshooting_sessions 
     WHERE status = 'resolved' 
     AND started_at >= CURRENT_DATE - INTERVAL '30 days') as resolved_30d,
    
    (SELECT COUNT(*) FROM support_troubleshooting_sessions 
     WHERE status = 'escalated' 
     AND started_at >= CURRENT_DATE - INTERVAL '30 days') as escalated_30d,
    
    -- Tasa de resolución
    ROUND(
        (SELECT COUNT(*) FROM support_troubleshooting_sessions 
         WHERE status = 'resolved' 
         AND started_at >= CURRENT_DATE - INTERVAL '30 days')::NUMERIC /
        NULLIF((SELECT COUNT(*) FROM support_troubleshooting_sessions 
                WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'), 0)::NUMERIC * 100,
        2
    ) as resolution_rate_30d,
    
    -- Tiempo promedio
    (SELECT AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, escalated_at, NOW()) - started_at)) / 60)
     FROM support_troubleshooting_sessions
     WHERE started_at >= CURRENT_DATE - INTERVAL '30 days')::NUMERIC(10,2) as avg_duration_minutes_30d,
    
    -- Satisfacción
    (SELECT AVG(rating) FROM support_troubleshooting_feedback 
     WHERE collected_at >= CURRENT_DATE - INTERVAL '30 days')::NUMERIC(3,2) as avg_rating_30d,
    
    -- Problemas más comunes
    (SELECT detected_problem_title 
     FROM support_troubleshooting_sessions 
     WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
       AND detected_problem_title IS NOT NULL
     GROUP BY detected_problem_title 
     ORDER BY COUNT(*) DESC 
     LIMIT 1) as most_common_problem_30d,
    
    -- Sesiones activas
    (SELECT COUNT(*) FROM support_troubleshooting_sessions 
     WHERE status IN ('started', 'in_progress')) as active_sessions_now;

-- ============================================================================
-- 6. Función para Generar Reporte Ejecutivo Completo
-- ============================================================================
CREATE OR REPLACE FUNCTION generate_executive_report(
    p_start_date TIMESTAMP DEFAULT NOW() - INTERVAL '30 days',
    p_end_date TIMESTAMP DEFAULT NOW()
)
RETURNS JSONB AS $$
DECLARE
    v_report JSONB;
BEGIN
    SELECT jsonb_build_object(
        'period', jsonb_build_object(
            'start', p_start_date,
            'end', p_end_date
        ),
        'summary', (
            SELECT jsonb_build_object(
                'total_sessions', COUNT(*)::BIGINT,
                'resolved', COUNT(CASE WHEN status = 'resolved' THEN 1 END)::BIGINT,
                'escalated', COUNT(CASE WHEN status = 'escalated' THEN 1 END)::BIGINT,
                'resolution_rate', ROUND(
                    COUNT(CASE WHEN status = 'resolved' THEN 1 END)::NUMERIC / 
                    NULLIF(COUNT(*), 0)::NUMERIC * 100, 
                    2
                ),
                'avg_duration_minutes', ROUND(
                    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, escalated_at, NOW()) - started_at)) / 60),
                    2
                )
            )
            FROM support_troubleshooting_sessions
            WHERE started_at BETWEEN p_start_date AND p_end_date
        ),
        'top_problems', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'problem_id', detected_problem_id,
                    'problem_title', detected_problem_title,
                    'total_sessions', total_sessions,
                    'resolution_rate', resolution_rate
                )
            )
            FROM (
                SELECT 
                    detected_problem_id,
                    detected_problem_title,
                    COUNT(*) as total_sessions,
                    ROUND(
                        COUNT(CASE WHEN status = 'resolved' THEN 1 END)::NUMERIC / 
                        NULLIF(COUNT(*), 0)::NUMERIC * 100, 
                        2
                    ) as resolution_rate
                FROM support_troubleshooting_sessions
                WHERE started_at BETWEEN p_start_date AND p_end_date
                  AND detected_problem_id IS NOT NULL
                GROUP BY detected_problem_id, detected_problem_title
                ORDER BY total_sessions DESC
                LIMIT 5
            ) top5
        ),
        'satisfaction', (
            SELECT jsonb_build_object(
                'avg_rating', ROUND(AVG(rating)::NUMERIC, 2),
                'total_feedback', COUNT(*)::BIGINT,
                'helpful_percentage', ROUND(
                    COUNT(CASE WHEN was_helpful = true THEN 1 END)::NUMERIC / 
                    NULLIF(COUNT(*), 0)::NUMERIC * 100, 
                    2
                )
            )
            FROM support_troubleshooting_feedback
            WHERE collected_at BETWEEN p_start_date AND p_end_date
        ),
        'trends', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'date', period_start,
                    'sessions', total_sessions,
                    'resolution_rate', resolution_rate
                )
            )
            FROM analyze_troubleshooting_trends(
                EXTRACT(DAY FROM (p_end_date - p_start_date))::INTEGER,
                'day'
            )
        ),
        'recommendations', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'problem_id', problem_id,
                    'problem_title', problem_title,
                    'recommendation', recommendation
                )
            )
            FROM identify_problems_needing_improvement(5, 70.0)
            LIMIT 5
        ),
        'generated_at', NOW()
    ) INTO v_report;
    
    RETURN v_report;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. Índices Adicionales para Queries Específicas
-- ============================================================================

-- Índice para búsquedas por rango de fechas y estado
CREATE INDEX IF NOT EXISTS idx_sessions_date_status_resolved 
    ON support_troubleshooting_sessions(started_at DESC, status) 
    WHERE status = 'resolved';

CREATE INDEX IF NOT EXISTS idx_sessions_date_status_escalated 
    ON support_troubleshooting_sessions(started_at DESC, status) 
    WHERE status = 'escalated';

-- Índice compuesto para análisis de problemas
CREATE INDEX IF NOT EXISTS idx_sessions_problem_date 
    ON support_troubleshooting_sessions(detected_problem_id, started_at DESC) 
    WHERE detected_problem_id IS NOT NULL;

-- Índice para feedback por problema y fecha
CREATE INDEX IF NOT EXISTS idx_feedback_problem_date 
    ON support_troubleshooting_feedback(problem_detected_id, collected_at DESC) 
    WHERE problem_detected_id IS NOT NULL;

-- Índice para búsquedas de sesiones por cliente
CREATE INDEX IF NOT EXISTS idx_sessions_customer_date 
    ON support_troubleshooting_sessions(customer_email, started_at DESC);

COMMIT;

-- ============================================================================
-- COMENTARIOS
-- ============================================================================
COMMENT ON FUNCTION analyze_troubleshooting_trends IS 
    'Analiza tendencias temporales en troubleshooting';
COMMENT ON FUNCTION identify_problems_needing_improvement IS 
    'Identifica problemas que necesitan mejoras en sus guías';
COMMENT ON FUNCTION analyze_customer_satisfaction IS 
    'Analiza satisfacción del cliente por problema';
COMMENT ON FUNCTION optimize_troubleshooting_tables IS 
    'Ejecuta optimizaciones automáticas en tablas';
COMMENT ON FUNCTION generate_executive_report IS 
    'Genera reporte ejecutivo completo en formato JSON';
COMMENT ON VIEW vw_executive_summary IS 
    'Resumen ejecutivo de métricas principales';



