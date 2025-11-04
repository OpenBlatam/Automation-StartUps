-- ============================================================================
-- SCHEMA: Sistema de Auditoría Avanzado
-- ============================================================================
-- Tracking completo de cambios, accesos, y acciones del sistema
-- ============================================================================

BEGIN;

-- ============================================================================
-- Tabla de Auditoría de Tickets
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_audit_tickets (
    id SERIAL PRIMARY KEY,
    audit_id VARCHAR(128) UNIQUE NOT NULL,
    
    -- Referencia
    ticket_id VARCHAR(128) NOT NULL,
    
    -- Acción
    action_type VARCHAR(64) NOT NULL,  -- 'create', 'update', 'delete', 'view', 'assign', 'escalate'
    action_description TEXT,
    
    -- Cambios
    field_changed VARCHAR(128),
    old_value TEXT,
    new_value TEXT,
    changes JSONB,  -- Cambios múltiples en formato JSON
    
    -- Actor
    actor_type VARCHAR(32) NOT NULL,  -- 'user', 'system', 'agent', 'chatbot'
    actor_id VARCHAR(128),
    actor_name VARCHAR(256),
    
    -- Contexto
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(128),
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id) ON DELETE CASCADE
);

-- ============================================================================
-- Tabla de Auditoría de Accesos
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_audit_access (
    id SERIAL PRIMARY KEY,
    audit_id VARCHAR(128) UNIQUE NOT NULL,
    
    -- Usuario/Agente
    user_id VARCHAR(128) NOT NULL,
    user_type VARCHAR(32) NOT NULL,  -- 'agent', 'admin', 'customer'
    
    -- Acceso
    resource_type VARCHAR(64) NOT NULL,  -- 'ticket', 'dashboard', 'report', 'settings'
    resource_id VARCHAR(128),
    action VARCHAR(64) NOT NULL,  -- 'view', 'edit', 'delete', 'export'
    
    -- Contexto
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(128),
    
    -- Resultado
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Tabla de Auditoría de Configuración
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_audit_config (
    id SERIAL PRIMARY KEY,
    audit_id VARCHAR(128) UNIQUE NOT NULL,
    
    -- Configuración
    config_type VARCHAR(64) NOT NULL,  -- 'rule', 'agent', 'sla', 'faq', 'routing'
    config_id VARCHAR(128),
    config_name VARCHAR(256),
    
    -- Acción
    action_type VARCHAR(32) NOT NULL,  -- 'create', 'update', 'delete', 'enable', 'disable'
    
    -- Cambios
    old_config JSONB,
    new_config JSONB,
    changes JSONB,
    
    -- Actor
    actor_id VARCHAR(128),
    actor_name VARCHAR(256),
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Función: Registrar auditoría de ticket
-- ============================================================================
CREATE OR REPLACE FUNCTION audit_ticket_change()
RETURNS TRIGGER AS $$
DECLARE
    v_audit_id VARCHAR(128);
    v_changes JSONB := '{}'::JSONB;
    v_field TEXT;
    v_old_val TEXT;
    v_new_val TEXT;
BEGIN
    v_audit_id := 'audit-' || gen_random_uuid()::text;
    
    -- Si es UPDATE, detectar cambios
    IF TG_OP = 'UPDATE' THEN
        -- Comparar campos importantes
        IF OLD.status IS DISTINCT FROM NEW.status THEN
            v_changes := v_changes || jsonb_build_object('status', jsonb_build_object(
                'old', OLD.status,
                'new', NEW.status
            ));
        END IF;
        
        IF OLD.priority IS DISTINCT FROM NEW.priority THEN
            v_changes := v_changes || jsonb_build_object('priority', jsonb_build_object(
                'old', OLD.priority,
                'new', NEW.priority
            ));
        END IF;
        
        IF OLD.assigned_agent_id IS DISTINCT FROM NEW.assigned_agent_id THEN
            v_changes := v_changes || jsonb_build_object('assigned_agent_id', jsonb_build_object(
                'old', OLD.assigned_agent_id,
                'new', NEW.assigned_agent_id
            ));
        END IF;
        
        IF OLD.assigned_department IS DISTINCT FROM NEW.assigned_department THEN
            v_changes := v_changes || jsonb_build_object('assigned_department', jsonb_build_object(
                'old', OLD.assigned_department,
                'new', NEW.assigned_department
            ));
        END IF;
    END IF;
    
    INSERT INTO support_audit_tickets (
        audit_id,
        ticket_id,
        action_type,
        action_description,
        changes,
        actor_type,
        actor_id,
        actor_name,
        created_at
    ) VALUES (
        v_audit_id,
        NEW.ticket_id,
        TG_OP,
        CASE 
            WHEN TG_OP = 'INSERT' THEN 'Ticket creado'
            WHEN TG_OP = 'UPDATE' THEN 'Ticket actualizado'
            WHEN TG_OP = 'DELETE' THEN 'Ticket eliminado'
        END,
        v_changes,
        COALESCE(NEW.updated_by_type, 'system'),
        COALESCE(NEW.updated_by_id, 'system'),
        COALESCE(NEW.updated_by_name, 'System'),
        NOW()
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Triggers de Auditoría
-- ============================================================================
DROP TRIGGER IF EXISTS trigger_audit_ticket_insert ON support_tickets;
CREATE TRIGGER trigger_audit_ticket_insert
    AFTER INSERT ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION audit_ticket_change();

DROP TRIGGER IF EXISTS trigger_audit_ticket_update ON support_tickets;
CREATE TRIGGER trigger_audit_ticket_update
    AFTER UPDATE ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION audit_ticket_change();

DROP TRIGGER IF EXISTS trigger_audit_ticket_delete ON support_tickets;
CREATE TRIGGER trigger_audit_ticket_delete
    AFTER DELETE ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION audit_ticket_change();

-- ============================================================================
-- Función: Registrar acceso
-- ============================================================================
CREATE OR REPLACE FUNCTION log_access(
    p_user_id VARCHAR(128),
    p_user_type VARCHAR(32),
    p_resource_type VARCHAR(64),
    p_resource_id VARCHAR(128),
    p_action VARCHAR(64),
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_session_id VARCHAR(128) DEFAULT NULL,
    p_success BOOLEAN DEFAULT true,
    p_error_message TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
)
RETURNS VARCHAR(128) AS $$
DECLARE
    v_audit_id VARCHAR(128);
BEGIN
    v_audit_id := 'access-' || gen_random_uuid()::text;
    
    INSERT INTO support_audit_access (
        audit_id,
        user_id,
        user_type,
        resource_type,
        resource_id,
        action,
        ip_address,
        user_agent,
        session_id,
        success,
        error_message,
        metadata,
        created_at
    ) VALUES (
        v_audit_id,
        p_user_id,
        p_user_type,
        p_resource_type,
        p_resource_id,
        p_action,
        p_ip_address,
        p_user_agent,
        p_session_id,
        p_success,
        p_error_message,
        p_metadata,
        NOW()
    );
    
    RETURN v_audit_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ÍNDICES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_audit_tickets_ticket_id ON support_audit_tickets(ticket_id);
CREATE INDEX IF NOT EXISTS idx_audit_tickets_action_type ON support_audit_tickets(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_tickets_actor ON support_audit_tickets(actor_type, actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_tickets_created_at ON support_audit_tickets(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_access_user ON support_audit_access(user_id, user_type);
CREATE INDEX IF NOT EXISTS idx_audit_access_resource ON support_audit_access(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_access_created_at ON support_audit_access(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_config_config ON support_audit_config(config_type, config_id);
CREATE INDEX IF NOT EXISTS idx_audit_config_created_at ON support_audit_config(created_at DESC);

-- ============================================================================
-- VISTA: Resumen de Auditoría
-- ============================================================================
CREATE OR REPLACE VIEW v_support_audit_summary AS
SELECT 
    DATE(created_at) as audit_date,
    action_type,
    actor_type,
    COUNT(*) as action_count,
    COUNT(DISTINCT ticket_id) as unique_tickets
FROM support_audit_tickets
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at), action_type, actor_type
ORDER BY audit_date DESC, action_count DESC;

COMMIT;

