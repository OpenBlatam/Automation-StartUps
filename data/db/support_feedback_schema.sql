-- ============================================================================
-- SCHEMA: Sistema de Feedback de Clientes para Tickets de Soporte
-- ============================================================================
-- Tabla para almacenar feedback de clientes sobre resolución de tickets
-- ============================================================================

BEGIN;

-- ============================================================================
-- Tabla de Feedback de Tickets
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_ticket_feedback (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(128) NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    customer_email VARCHAR(256) NOT NULL,
    
    -- Calificación
    satisfaction_score INT NOT NULL CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5),
    response_time_rating INT CHECK (response_time_rating >= 1 AND response_time_rating <= 5),
    resolution_quality_rating INT CHECK (resolution_quality_rating >= 1 AND resolution_quality_rating <= 5),
    
    -- Feedback textual
    feedback_text TEXT,
    positive_aspects TEXT,
    improvement_suggestions TEXT,
    
    -- Detalles
    would_recommend BOOLEAN,
    chatbot_was_helpful BOOLEAN,
    agent_was_helpful BOOLEAN,
    
    -- Metadata
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_via VARCHAR(32) DEFAULT 'email', -- email, web, api
    
    -- Índices
    CONSTRAINT support_feedback_ticket_unique UNIQUE (ticket_id, customer_email)
);

-- ============================================================================
-- Tabla de Encuestas de Satisfacción
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_satisfaction_surveys (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(128) NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    customer_email VARCHAR(256) NOT NULL,
    
    -- Preguntas específicas
    question_1_rating INT CHECK (question_1_rating >= 1 AND question_1_rating <= 5),
    question_2_rating INT CHECK (question_2_rating >= 1 AND question_2_rating <= 5),
    question_3_rating INT CHECK (question_3_rating >= 1 AND question_3_rating <= 5),
    
    -- Respuestas abiertas
    comments TEXT,
    
    -- Metadata
    survey_type VARCHAR(32) DEFAULT 'post_resolution', -- post_resolution, follow_up
    sent_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT support_survey_ticket_unique UNIQUE (ticket_id)
);

-- ============================================================================
-- ÍNDICES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_feedback_ticket_id ON support_ticket_feedback(ticket_id);
CREATE INDEX IF NOT EXISTS idx_feedback_customer_email ON support_ticket_feedback(customer_email);
CREATE INDEX IF NOT EXISTS idx_feedback_satisfaction_score ON support_ticket_feedback(satisfaction_score);
CREATE INDEX IF NOT EXISTS idx_feedback_submitted_at ON support_ticket_feedback(submitted_at);

CREATE INDEX IF NOT EXISTS idx_survey_ticket_id ON support_satisfaction_surveys(ticket_id);
CREATE INDEX IF NOT EXISTS idx_survey_customer_email ON support_satisfaction_surveys(customer_email);
CREATE INDEX IF NOT EXISTS idx_survey_submitted_at ON support_satisfaction_surveys(submitted_at);

-- ============================================================================
-- VISTA: Resumen de Feedback
-- ============================================================================
CREATE OR REPLACE VIEW v_support_feedback_summary AS
SELECT 
    DATE(submitted_at) as date,
    COUNT(*) as total_feedback,
    AVG(satisfaction_score) as avg_satisfaction,
    AVG(response_time_rating) as avg_response_time_rating,
    AVG(resolution_quality_rating) as avg_resolution_quality_rating,
    COUNT(*) FILTER (WHERE would_recommend = true) as would_recommend_count,
    COUNT(*) FILTER (WHERE chatbot_was_helpful = true) as chatbot_helpful_count,
    COUNT(*) FILTER (WHERE agent_was_helpful = true) as agent_helpful_count
FROM support_ticket_feedback
GROUP BY DATE(submitted_at)
ORDER BY date DESC;

-- ============================================================================
-- VISTA: Feedback por Agente
-- ============================================================================
CREATE OR REPLACE VIEW v_support_agent_feedback AS
SELECT 
    t.assigned_agent_name,
    COUNT(f.id) as feedback_count,
    AVG(f.satisfaction_score) as avg_satisfaction,
    AVG(f.response_time_rating) as avg_response_time_rating,
    AVG(f.resolution_quality_rating) as avg_resolution_quality_rating,
    COUNT(*) FILTER (WHERE f.would_recommend = true) as would_recommend_count
FROM support_tickets t
INNER JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
WHERE t.assigned_agent_name IS NOT NULL
GROUP BY t.assigned_agent_name
ORDER BY avg_satisfaction DESC;

COMMIT;

