-- ============================================================================
-- SCHEMA: Sistema de Predicción y Aprendizaje Automático
-- ============================================================================
-- Tablas y funciones para predicción de problemas y aprendizaje automático
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Patrones de Usuario
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_user_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_email VARCHAR(255) NOT NULL,
    problem_id VARCHAR(100),
    problem_title VARCHAR(500),
    occurrence_count INTEGER DEFAULT 1,
    first_occurrence TIMESTAMP DEFAULT NOW(),
    last_occurrence TIMESTAMP DEFAULT NOW(),
    avg_resolution_time_minutes NUMERIC(10,2),
    success_rate NUMERIC(5,2),
    escalation_rate NUMERIC(5,2),
    pattern_confidence NUMERIC(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(customer_email, problem_id)
);

CREATE INDEX idx_user_patterns_email ON support_troubleshooting_user_patterns(customer_email);
CREATE INDEX idx_user_patterns_problem ON support_troubleshooting_user_patterns(problem_id);
CREATE INDEX idx_user_patterns_updated ON support_troubleshooting_user_patterns(updated_at DESC);

-- ============================================================================
-- 2. Tabla de Predicciones
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_email VARCHAR(255) NOT NULL,
    predicted_problem_id VARCHAR(100),
    predicted_problem_title VARCHAR(500),
    probability NUMERIC(5,2),
    confidence NUMERIC(5,2),
    prediction_reasons JSONB,
    recommended_actions JSONB,
    estimated_impact VARCHAR(20),
    predicted_at TIMESTAMP DEFAULT NOW(),
    was_correct BOOLEAN,
    actual_problem_id VARCHAR(100),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_predictions_email ON support_troubleshooting_predictions(customer_email);
CREATE INDEX idx_predictions_problem ON support_troubleshooting_predictions(predicted_problem_id);
CREATE INDEX idx_predictions_date ON support_troubleshooting_predictions(predicted_at DESC);
CREATE INDEX idx_predictions_correct ON support_troubleshooting_predictions(was_correct) WHERE was_correct IS NOT NULL;

-- ============================================================================
-- 3. Tabla de Análisis de Efectividad de Pasos
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_step_effectiveness (
    effectiveness_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id VARCHAR(100) NOT NULL,
    step_number INTEGER NOT NULL,
    total_attempts INTEGER DEFAULT 0,
    successful_attempts INTEGER DEFAULT 0,
    failed_attempts INTEGER DEFAULT 0,
    success_rate NUMERIC(5,2),
    avg_duration_seconds NUMERIC(10,2),
    needs_improvement BOOLEAN DEFAULT false,
    improvement_suggestions JSONB,
    analyzed_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(problem_id, step_number)
);

CREATE INDEX idx_effectiveness_problem ON support_troubleshooting_step_effectiveness(problem_id);
CREATE INDEX idx_effectiveness_improvement ON support_troubleshooting_step_effectiveness(needs_improvement) WHERE needs_improvement = true;

-- ============================================================================
-- 4. Tabla de Recomendaciones Proactivas
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_troubleshooting_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_email VARCHAR(255) NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL, -- preventive, improvement, efficiency
    title VARCHAR(500),
    description TEXT,
    priority VARCHAR(20), -- low, medium, high
    action_type VARCHAR(100),
    action_data JSONB,
    shown_at TIMESTAMP,
    clicked_at TIMESTAMP,
    dismissed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX idx_recommendations_email ON support_troubleshooting_recommendations(customer_email);
CREATE INDEX idx_recommendations_type ON support_troubleshooting_recommendations(recommendation_type);
CREATE INDEX idx_recommendations_active ON support_troubleshooting_recommendations(customer_email, created_at DESC) 
    WHERE dismissed_at IS NULL AND (expires_at IS NULL OR expires_at > NOW());

-- ============================================================================
-- 5. Función para Actualizar Patrones de Usuario
-- ============================================================================
CREATE OR REPLACE FUNCTION update_user_patterns()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.detected_problem_id IS NOT NULL AND NEW.customer_email IS NOT NULL THEN
        INSERT INTO support_troubleshooting_user_patterns (
            customer_email,
            problem_id,
            problem_title,
            occurrence_count,
            first_occurrence,
            last_occurrence,
            avg_resolution_time_minutes,
            success_rate,
            escalation_rate
        )
        VALUES (
            NEW.customer_email,
            NEW.detected_problem_id,
            NEW.detected_problem_title,
            1,
            NEW.started_at,
            NEW.started_at,
            CASE 
                WHEN NEW.status = 'resolved' AND NEW.resolved_at IS NOT NULL 
                THEN EXTRACT(EPOCH FROM (NEW.resolved_at - NEW.started_at)) / 60
                ELSE NULL
            END,
            CASE WHEN NEW.status = 'resolved' THEN 100 ELSE 0 END,
            CASE WHEN NEW.status = 'escalated' THEN 100 ELSE 0 END
        )
        ON CONFLICT (customer_email, problem_id) DO UPDATE SET
            occurrence_count = support_troubleshooting_user_patterns.occurrence_count + 1,
            last_occurrence = NEW.started_at,
            avg_resolution_time_minutes = (
                SELECT AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, escalated_at, NOW()) - started_at)) / 60)
                FROM support_troubleshooting_sessions
                WHERE customer_email = NEW.customer_email
                  AND detected_problem_id = NEW.detected_problem_id
            ),
            success_rate = (
                SELECT COUNT(CASE WHEN status = 'resolved' THEN 1 END)::NUMERIC / 
                       NULLIF(COUNT(*), 0)::NUMERIC * 100
                FROM support_troubleshooting_sessions
                WHERE customer_email = NEW.customer_email
                  AND detected_problem_id = NEW.detected_problem_id
            ),
            escalation_rate = (
                SELECT COUNT(CASE WHEN status = 'escalated' THEN 1 END)::NUMERIC / 
                       NULLIF(COUNT(*), 0)::NUMERIC * 100
                FROM support_troubleshooting_sessions
                WHERE customer_email = NEW.customer_email
                  AND detected_problem_id = NEW.detected_problem_id
            ),
            updated_at = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_patterns
    AFTER INSERT OR UPDATE ON support_troubleshooting_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_patterns();

-- ============================================================================
-- 6. Función para Registrar Predicción
-- ============================================================================
CREATE OR REPLACE FUNCTION register_prediction(
    p_customer_email VARCHAR,
    p_predicted_problem_id VARCHAR,
    p_predicted_problem_title VARCHAR,
    p_probability NUMERIC,
    p_confidence NUMERIC,
    p_reasons JSONB,
    p_actions JSONB,
    p_impact VARCHAR
)
RETURNS UUID AS $$
DECLARE
    v_prediction_id UUID;
BEGIN
    INSERT INTO support_troubleshooting_predictions (
        customer_email,
        predicted_problem_id,
        predicted_problem_title,
        probability,
        confidence,
        prediction_reasons,
        recommended_actions,
        estimated_impact
    )
    VALUES (
        p_customer_email,
        p_predicted_problem_id,
        p_predicted_problem_title,
        p_probability,
        p_confidence,
        p_reasons,
        p_actions,
        p_impact
    )
    RETURNING prediction_id INTO v_prediction_id;
    
    RETURN v_prediction_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. Función para Verificar Predicción
-- ============================================================================
CREATE OR REPLACE FUNCTION verify_prediction(
    p_prediction_id UUID,
    p_actual_problem_id VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    v_predicted_problem_id VARCHAR;
    v_was_correct BOOLEAN;
BEGIN
    SELECT predicted_problem_id INTO v_predicted_problem_id
    FROM support_troubleshooting_predictions
    WHERE prediction_id = p_prediction_id;
    
    v_was_correct := (v_predicted_problem_id = p_actual_problem_id);
    
    UPDATE support_troubleshooting_predictions
    SET was_correct = v_was_correct,
        actual_problem_id = p_actual_problem_id,
        verified_at = NOW()
    WHERE prediction_id = p_prediction_id;
    
    RETURN v_was_correct;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 8. Función para Actualizar Efectividad de Pasos
-- ============================================================================
CREATE OR REPLACE FUNCTION update_step_effectiveness()
RETURNS TRIGGER AS $$
DECLARE
    v_problem_id VARCHAR;
    v_success_rate NUMERIC;
BEGIN
    -- Obtener problem_id de la sesión
    SELECT detected_problem_id INTO v_problem_id
    FROM support_troubleshooting_sessions
    WHERE session_id = NEW.session_id;
    
    IF v_problem_id IS NOT NULL THEN
        -- Calcular tasa de éxito
        SELECT 
            COUNT(CASE WHEN success = true THEN 1 END)::NUMERIC / 
            NULLIF(COUNT(*), 0)::NUMERIC * 100
        INTO v_success_rate
        FROM support_troubleshooting_attempts
        WHERE session_id = NEW.session_id
          AND step_number = NEW.step_number;
        
        INSERT INTO support_troubleshooting_step_effectiveness (
            problem_id,
            step_number,
            total_attempts,
            successful_attempts,
            failed_attempts,
            success_rate,
            avg_duration_seconds,
            needs_improvement
        )
        VALUES (
            v_problem_id,
            NEW.step_number,
            1,
            CASE WHEN NEW.success THEN 1 ELSE 0 END,
            CASE WHEN NEW.success THEN 0 ELSE 1 END,
            v_success_rate,
            EXTRACT(EPOCH FROM (COALESCE(NEW.completed_at, NOW()) - NEW.started_at)),
            v_success_rate < 70
        )
        ON CONFLICT (problem_id, step_number) DO UPDATE SET
            total_attempts = support_troubleshooting_step_effectiveness.total_attempts + 1,
            successful_attempts = support_troubleshooting_step_effectiveness.successful_attempts + 
                CASE WHEN NEW.success THEN 1 ELSE 0 END,
            failed_attempts = support_troubleshooting_step_effectiveness.failed_attempts + 
                CASE WHEN NEW.success THEN 0 ELSE 1 END,
            success_rate = (
                SELECT COUNT(CASE WHEN success = true THEN 1 END)::NUMERIC / 
                       NULLIF(COUNT(*), 0)::NUMERIC * 100
                FROM support_troubleshooting_attempts
                WHERE session_id IN (
                    SELECT session_id FROM support_troubleshooting_sessions
                    WHERE detected_problem_id = v_problem_id
                )
                AND step_number = NEW.step_number
            ),
            avg_duration_seconds = (
                SELECT AVG(EXTRACT(EPOCH FROM (COALESCE(completed_at, NOW()) - started_at)))
                FROM support_troubleshooting_attempts
                WHERE session_id IN (
                    SELECT session_id FROM support_troubleshooting_sessions
                    WHERE detected_problem_id = v_problem_id
                )
                AND step_number = NEW.step_number
            ),
            needs_improvement = (
                SELECT COUNT(CASE WHEN success = true THEN 1 END)::NUMERIC / 
                       NULLIF(COUNT(*), 0)::NUMERIC * 100
                FROM support_troubleshooting_attempts
                WHERE session_id IN (
                    SELECT session_id FROM support_troubleshooting_sessions
                    WHERE detected_problem_id = v_problem_id
                )
                AND step_number = NEW.step_number
            ) < 70,
            last_updated = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_step_effectiveness
    AFTER INSERT OR UPDATE ON support_troubleshooting_attempts
    FOR EACH ROW
    EXECUTE FUNCTION update_step_effectiveness();

-- ============================================================================
-- 9. Vista de Predicciones Activas
-- ============================================================================
CREATE OR REPLACE VIEW vw_active_predictions AS
SELECT 
    p.prediction_id,
    p.customer_email,
    p.predicted_problem_id,
    p.predicted_problem_title,
    p.probability,
    p.confidence,
    p.estimated_impact,
    p.predicted_at,
    up.occurrence_count,
    up.success_rate as historical_success_rate
FROM support_troubleshooting_predictions p
LEFT JOIN support_troubleshooting_user_patterns up 
    ON p.customer_email = up.customer_email 
    AND p.predicted_problem_id = up.problem_id
WHERE p.verified_at IS NULL
ORDER BY p.probability DESC, p.confidence DESC;

-- ============================================================================
-- 10. Vista de Pasos que Necesitan Mejora
-- ============================================================================
CREATE OR REPLACE VIEW vw_steps_needing_improvement AS
SELECT 
    se.problem_id,
    se.step_number,
    se.total_attempts,
    se.success_rate,
    se.avg_duration_seconds,
    se.improvement_suggestions
FROM support_troubleshooting_step_effectiveness se
WHERE se.needs_improvement = true
ORDER BY se.success_rate ASC, se.total_attempts DESC;

COMMIT;

-- ============================================================================
-- COMENTARIOS
-- ============================================================================
COMMENT ON TABLE support_troubleshooting_user_patterns IS 
    'Patrones de comportamiento de usuarios para predicción';
COMMENT ON TABLE support_troubleshooting_predictions IS 
    'Predicciones de problemas futuros';
COMMENT ON TABLE support_troubleshooting_step_effectiveness IS 
    'Análisis de efectividad de pasos de troubleshooting';
COMMENT ON TABLE support_troubleshooting_recommendations IS 
    'Recomendaciones proactivas para usuarios';
COMMENT ON FUNCTION update_user_patterns IS 
    'Actualiza patrones de usuario automáticamente';
COMMENT ON FUNCTION register_prediction IS 
    'Registra una nueva predicción';
COMMENT ON FUNCTION verify_prediction IS 
    'Verifica si una predicción fue correcta';
COMMENT ON FUNCTION update_step_effectiveness IS 
    'Actualiza efectividad de pasos automáticamente';



