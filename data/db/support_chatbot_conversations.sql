-- ============================================================================
-- SCHEMA: Historial de Conversaciones del Chatbot
-- ============================================================================
-- Tabla para almacenar el historial de conversaciones del chatbot
-- Permite mantener contexto en conversaciones multi-turno
-- ============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS support_chatbot_conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(128) UNIQUE NOT NULL,
    customer_email VARCHAR(256),
    customer_name VARCHAR(256),
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    confidence_score NUMERIC(5,4),
    resolved BOOLEAN DEFAULT false,
    escalation_needed BOOLEAN DEFAULT false,
    ticket_id VARCHAR(128) REFERENCES support_tickets(ticket_id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para búsqueda rápida
CREATE INDEX IF NOT EXISTS idx_chatbot_conversations_customer_email 
    ON support_chatbot_conversations(customer_email);
CREATE INDEX IF NOT EXISTS idx_chatbot_conversations_conversation_id 
    ON support_chatbot_conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_conversations_created_at 
    ON support_chatbot_conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chatbot_conversations_ticket_id 
    ON support_chatbot_conversations(ticket_id);

-- Vista para análisis de conversaciones
CREATE OR REPLACE VIEW v_chatbot_conversations_summary AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_conversations,
    COUNT(DISTINCT customer_email) as unique_customers,
    COUNT(*) FILTER (WHERE resolved = true) as resolved_conversations,
    COUNT(*) FILTER (WHERE escalation_needed = true) as escalated_conversations,
    AVG(confidence_score) as avg_confidence,
    COUNT(*) FILTER (WHERE ticket_id IS NOT NULL) as tickets_created
FROM support_chatbot_conversations
GROUP BY DATE(created_at)
ORDER BY date DESC;

COMMIT;

