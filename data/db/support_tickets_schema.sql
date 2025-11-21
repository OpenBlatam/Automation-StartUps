-- ============================================================================
-- SCHEMA: Sistema de Automatización de Soporte al Cliente / Tickets
-- ============================================================================
-- Este esquema soporta:
-- - Tickets de soporte con clasificación y priorización automática
-- - Enrutamiento inteligente a departamentos/agentes
-- - Historial de interacciones con chatbot
-- - Respuestas de FAQs automatizadas
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Tickets de Soporte
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(128) UNIQUE NOT NULL, -- ID externo (UUID o hash)
    source VARCHAR(64) NOT NULL DEFAULT 'web', -- web, email, chat, phone, api, whatsapp, etc.
    subject VARCHAR(512),
    description TEXT NOT NULL,
    customer_email VARCHAR(256) NOT NULL,
    customer_name VARCHAR(256),
    customer_id VARCHAR(128), -- ID del cliente en CRM (HubSpot, etc.)
    
    -- Clasificación automática
    category VARCHAR(64), -- billing, technical, sales, general, etc.
    subcategory VARCHAR(128), -- payment_issue, bug_report, feature_request, etc.
    tags TEXT[], -- Array de tags para búsqueda
    
    -- Priorización automática
    priority VARCHAR(16) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent', 'critical')),
    priority_score NUMERIC(5,2) DEFAULT 0.0, -- Score calculado (0.0 a 100.0)
    urgency_factors JSONB, -- Factores que influyen en la urgencia
    
    -- Enrutamiento
    assigned_department VARCHAR(64), -- sales, support, billing, technical, etc.
    assigned_agent_id VARCHAR(128), -- ID del agente asignado
    assigned_agent_name VARCHAR(256),
    routing_reason TEXT, -- Razón de la asignación
    
    -- Estado del ticket
    status VARCHAR(32) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'chatbot_handled', 'assigned', 'in_progress', 'waiting_customer', 'resolved', 'closed', 'escalated')),
    
    -- Chatbot y FAQ
    chatbot_attempted BOOLEAN DEFAULT false,
    chatbot_resolved BOOLEAN DEFAULT false,
    chatbot_response TEXT, -- Respuesta del chatbot si resolvió
    faq_matched BOOLEAN DEFAULT false,
    faq_article_id VARCHAR(128), -- ID del artículo de FAQ que resolvió
    
    -- Métricas de atención
    first_response_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    time_to_first_response_minutes INT,
    time_to_resolution_minutes INT,
    customer_satisfaction_score INT CHECK (customer_satisfaction_score >= 1 AND customer_satisfaction_score <= 5),
    
    -- Metadata
    metadata JSONB DEFAULT '{}', -- Información adicional (canal, dispositivo, etc.)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Índices implícitos
    CONSTRAINT support_tickets_email_check CHECK (customer_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- ============================================================================
-- 2. Tabla de Interacciones con Chatbot
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_chatbot_interactions (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(128) NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    interaction_number INT NOT NULL DEFAULT 1,
    user_message TEXT NOT NULL,
    chatbot_response TEXT,
    intent_detected VARCHAR(128), -- Intención detectada por NLP
    confidence_score NUMERIC(5,4), -- Confianza del modelo (0.0 a 1.0)
    faq_matched BOOLEAN DEFAULT false,
    faq_article_id VARCHAR(128),
    resolved_by_chatbot BOOLEAN DEFAULT false,
    escalation_reason TEXT, -- Razón por la que escaló a agente humano
    metadata JSONB DEFAULT '{}', -- Modelo usado, tokens, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 3. Tabla de Artículos FAQ
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_faq_articles (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(128) UNIQUE NOT NULL,
    title VARCHAR(512) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT, -- Resumen corto para preview
    category VARCHAR(64),
    tags TEXT[],
    keywords TEXT[], -- Palabras clave para matching
    intent_mappings TEXT[], -- Intenciones que mapean a este artículo
    
    -- Métricas
    view_count INT DEFAULT 0,
    helpful_count INT DEFAULT 0,
    not_helpful_count INT DEFAULT 0,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- ============================================================================
-- 4. Tabla de Historial de Cambios de Estado
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_ticket_history (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(128) NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    field_changed VARCHAR(64) NOT NULL, -- status, priority, assigned_agent_id, etc.
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(128), -- system, agent_id, customer_email, etc.
    change_reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 5. Tabla de Agentes y Capacidad
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(128) UNIQUE NOT NULL,
    agent_name VARCHAR(256) NOT NULL,
    email VARCHAR(256) UNIQUE NOT NULL,
    department VARCHAR(64) NOT NULL,
    specialties TEXT[], -- Especialidades (billing, technical, sales, etc.)
    max_concurrent_tickets INT DEFAULT 5,
    current_active_tickets INT DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    timezone VARCHAR(64) DEFAULT 'UTC',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 6. Tabla de Reglas de Enrutamiento
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_routing_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(256) NOT NULL,
    priority_order INT NOT NULL, -- Orden de evaluación (menor = primero)
    conditions JSONB NOT NULL, -- Condiciones en formato JSON (category, tags, keywords, etc.)
    target_department VARCHAR(64) NOT NULL,
    target_specialties TEXT[], -- Especialidades requeridas del agente
    auto_assign BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ============================================================================

-- Tickets
CREATE INDEX IF NOT EXISTS idx_support_tickets_ticket_id ON support_tickets(ticket_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_customer_email ON support_tickets(customer_email);
CREATE INDEX IF NOT EXISTS idx_support_tickets_customer_id ON support_tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_priority ON support_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_support_tickets_category ON support_tickets(category);
CREATE INDEX IF NOT EXISTS idx_support_tickets_department ON support_tickets(assigned_department);
CREATE INDEX IF NOT EXISTS idx_support_tickets_agent ON support_tickets(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_created_at ON support_tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_support_tickets_chatbot ON support_tickets(chatbot_attempted, chatbot_resolved);
CREATE INDEX IF NOT EXISTS idx_support_tickets_source ON support_tickets(source);
CREATE INDEX IF NOT EXISTS idx_support_tickets_tags ON support_tickets USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_support_tickets_priority_score ON support_tickets(priority_score DESC);

-- Chatbot interactions
CREATE INDEX IF NOT EXISTS idx_chatbot_interactions_ticket ON support_chatbot_interactions(ticket_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_interactions_created_at ON support_chatbot_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_chatbot_interactions_resolved ON support_chatbot_interactions(resolved_by_chatbot);

-- FAQ articles
CREATE INDEX IF NOT EXISTS idx_faq_articles_article_id ON support_faq_articles(article_id);
CREATE INDEX IF NOT EXISTS idx_faq_articles_category ON support_faq_articles(category);
CREATE INDEX IF NOT EXISTS idx_faq_articles_tags ON support_faq_articles USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_faq_articles_keywords ON support_faq_articles USING GIN(keywords);
CREATE INDEX IF NOT EXISTS idx_faq_articles_active ON support_faq_articles(is_active) WHERE is_active = true;

-- Ticket history
CREATE INDEX IF NOT EXISTS idx_ticket_history_ticket ON support_ticket_history(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_history_created_at ON support_ticket_history(created_at);

-- Agents
CREATE INDEX IF NOT EXISTS idx_support_agents_agent_id ON support_agents(agent_id);
CREATE INDEX IF NOT EXISTS idx_support_agents_department ON support_agents(department);
CREATE INDEX IF NOT EXISTS idx_support_agents_available ON support_agents(is_available) WHERE is_available = true;
CREATE INDEX IF NOT EXISTS idx_support_agents_specialties ON support_agents USING GIN(specialties);

-- Routing rules
CREATE INDEX IF NOT EXISTS idx_routing_rules_priority ON support_routing_rules(priority_order);
CREATE INDEX IF NOT EXISTS idx_routing_rules_active ON support_routing_rules(is_active) WHERE is_active = true;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_support_tickets_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_support_tickets_updated_at
    BEFORE UPDATE ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_support_tickets_updated_at();

-- Trigger para registrar cambios de estado
CREATE OR REPLACE FUNCTION log_support_ticket_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO support_ticket_history (ticket_id, field_changed, old_value, new_value, changed_by)
        VALUES (NEW.ticket_id, 'status', OLD.status, NEW.status, 'system');
    END IF;
    
    IF OLD.priority IS DISTINCT FROM NEW.priority THEN
        INSERT INTO support_ticket_history (ticket_id, field_changed, old_value, new_value, changed_by)
        VALUES (NEW.ticket_id, 'priority', OLD.priority, NEW.priority, 'system');
    END IF;
    
    IF OLD.assigned_agent_id IS DISTINCT FROM NEW.assigned_agent_id THEN
        INSERT INTO support_ticket_history (ticket_id, field_changed, old_value, new_value, changed_by)
        VALUES (NEW.ticket_id, 'assigned_agent_id', OLD.assigned_agent_id, NEW.assigned_agent_id, 'system');
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_support_ticket_changes
    AFTER UPDATE ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION log_support_ticket_changes();

-- ============================================================================
-- 12. Tabla de Acciones Preventivas de Churn
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_churn_prevention_actions (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(256) NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    agent_id VARCHAR(128),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_churn_prevention_customer ON support_churn_prevention_actions(customer_id);
CREATE INDEX idx_churn_prevention_created ON support_churn_prevention_actions(created_at);

-- ============================================================================
-- 13. Tabla de Mensajes de Redes Sociales
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_social_messages (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(128) NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    platform VARCHAR(32) NOT NULL,
    message_id VARCHAR(128) NOT NULL,
    message_type VARCHAR(32) NOT NULL,
    author_id VARCHAR(128),
    author_name VARCHAR(256),
    author_username VARCHAR(128),
    content TEXT NOT NULL,
    url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(platform, message_id)
);

CREATE INDEX idx_social_messages_ticket ON support_social_messages(ticket_id);
CREATE INDEX idx_social_messages_platform ON support_social_messages(platform);
CREATE INDEX idx_social_messages_author ON support_social_messages(author_username);

-- ============================================================================
-- 14. Tabla de Respuestas a Redes Sociales
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_social_responses (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(128) NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    platform VARCHAR(32) NOT NULL,
    to_username VARCHAR(128) NOT NULL,
    response_text TEXT NOT NULL,
    agent_id VARCHAR(128),
    responded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_social_responses_ticket ON support_social_responses(ticket_id);
CREATE INDEX idx_social_responses_platform ON support_social_responses(platform);

-- ============================================================================
-- 15. Tabla de Usuarios del Sistema
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_users (
    user_id VARCHAR(128) PRIMARY KEY,
    email VARCHAR(256) UNIQUE NOT NULL,
    username VARCHAR(128) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(32) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

CREATE INDEX idx_support_users_email ON support_users(email);
CREATE INDEX idx_support_users_role ON support_users(role);

-- ============================================================================
-- 16. Tabla de Tokens de Autenticación
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_auth_tokens (
    token VARCHAR(512) PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL REFERENCES support_users(user_id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_auth_tokens_user ON support_auth_tokens(user_id);
CREATE INDEX idx_auth_tokens_expires ON support_auth_tokens(expires_at);

-- ============================================================================
-- 17. Tabla de Claves API
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_api_keys (
    key_id VARCHAR(128) PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL REFERENCES support_users(user_id) ON DELETE CASCADE,
    key_hash VARCHAR(256) NOT NULL UNIQUE,
    name VARCHAR(256) NOT NULL,
    permissions TEXT[] NOT NULL,
    expires_at TIMESTAMPTZ,
    last_used TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_api_keys_user ON support_api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON support_api_keys(key_hash);

-- ============================================================================
-- 18. Tabla de Módulos de Capacitación
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_training_modules (
    module_id VARCHAR(128) PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    description TEXT,
    topic VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    duration_minutes INT NOT NULL,
    prerequisites TEXT[], -- IDs de módulos requeridos
    assessment_questions JSONB, -- Preguntas de evaluación
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_training_modules_topic ON support_training_modules(topic);

-- ============================================================================
-- 19. Tabla de Capacitación de Agentes
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_agent_training (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(128) NOT NULL,
    module_id VARCHAR(128) NOT NULL REFERENCES support_training_modules(module_id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    due_date TIMESTAMPTZ,
    score NUMERIC(5,2),
    notes TEXT,
    UNIQUE(agent_id, module_id)
);

CREATE INDEX idx_agent_training_agent ON support_agent_training(agent_id);
CREATE INDEX idx_agent_training_status ON support_agent_training(status);
CREATE INDEX idx_agent_training_due_date ON support_agent_training(due_date);

-- ============================================================================
-- 20. Tabla de Templates de Tickets
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_ticket_templates (
    template_id VARCHAR(128) PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    description TEXT,
    template_type VARCHAR(32) NOT NULL,
    category VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    variables TEXT[], -- Variables usadas en el template
    tags TEXT[],
    usage_count INT DEFAULT 0,
    success_rate NUMERIC(5,2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_templates_type ON support_ticket_templates(template_type);
CREATE INDEX idx_templates_category ON support_ticket_templates(category);
CREATE INDEX idx_templates_active ON support_ticket_templates(is_active);

-- ============================================================================
-- 21. Tabla de Uso de Templates
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_template_usage (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(128) NOT NULL REFERENCES support_ticket_templates(template_id) ON DELETE CASCADE,
    ticket_id VARCHAR(128) NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    satisfaction_score NUMERIC(3,1),
    used_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_template_usage_template ON support_template_usage(template_id);
CREATE INDEX idx_template_usage_ticket ON support_template_usage(ticket_id);

-- ============================================================================
-- 22. Tabla de Acciones Proactivas
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_proactive_actions (
    action_id VARCHAR(128) PRIMARY KEY,
    action_type VARCHAR(64) NOT NULL,
    priority VARCHAR(32) NOT NULL,
    title VARCHAR(256) NOT NULL,
    description TEXT,
    target_audience TEXT[],
    recommended_action TEXT,
    status VARCHAR(32) DEFAULT 'pending',
    executed_by VARCHAR(128),
    executed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_proactive_actions_type ON support_proactive_actions(action_type);
CREATE INDEX idx_proactive_actions_priority ON support_proactive_actions(priority);
CREATE INDEX idx_proactive_actions_status ON support_proactive_actions(status);

COMMIT;

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista de tickets pendientes por prioridad
CREATE OR REPLACE VIEW v_support_tickets_pending AS
SELECT 
    ticket_id,
    subject,
    customer_email,
    customer_name,
    priority,
    priority_score,
    category,
    assigned_department,
    assigned_agent_name,
    status,
    created_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))/60 AS minutes_since_creation
FROM support_tickets
WHERE status IN ('open', 'assigned', 'in_progress')
ORDER BY 
    CASE priority 
        WHEN 'critical' THEN 1
        WHEN 'urgent' THEN 2
        WHEN 'high' THEN 3
        WHEN 'medium' THEN 4
        WHEN 'low' THEN 5
    END,
    priority_score DESC,
    created_at ASC;

-- Vista de estadísticas de chatbot
CREATE OR REPLACE VIEW v_support_chatbot_stats AS
SELECT 
    DATE(created_at) AS date,
    COUNT(*) AS total_interactions,
    COUNT(*) FILTER (WHERE resolved_by_chatbot = true) AS resolved_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE resolved_by_chatbot = true) / COUNT(*), 2) AS resolution_rate_pct,
    AVG(confidence_score) AS avg_confidence,
    COUNT(*) FILTER (WHERE faq_matched = true) AS faq_matches
FROM support_chatbot_interactions
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Vista de carga de trabajo por agente
CREATE OR REPLACE VIEW v_support_agents_workload AS
SELECT 
    a.agent_id,
    a.agent_name,
    a.department,
    a.max_concurrent_tickets,
    COUNT(t.ticket_id) AS current_tickets,
    COUNT(t.ticket_id) FILTER (WHERE t.status = 'in_progress') AS in_progress_count,
    COUNT(t.ticket_id) FILTER (WHERE t.priority IN ('critical', 'urgent')) AS urgent_tickets
FROM support_agents a
LEFT JOIN support_tickets t ON a.agent_id = t.assigned_agent_id 
    AND t.status IN ('open', 'assigned', 'in_progress')
WHERE a.is_available = true
GROUP BY a.agent_id, a.agent_name, a.department, a.max_concurrent_tickets
ORDER BY current_tickets DESC;



