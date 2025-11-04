-- ============================================================================
-- Sistema de Aprobaciones Internas
-- Esquema completo para gestión de solicitudes, aprobaciones y reglas automáticas
-- ============================================================================

-- Tabla de usuarios y roles para aprobaciones
CREATE TABLE IF NOT EXISTS approval_users (
    user_email VARCHAR(255) PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    department VARCHAR(128),
    role VARCHAR(64) NOT NULL, -- 'employee', 'manager', 'director', 'finance_manager', 'hr_manager', 'ceo'
    manager_email VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (manager_email) REFERENCES approval_users(user_email) ON DELETE SET NULL
);

-- Tabla de tipos de solicitudes
CREATE TYPE approval_request_type AS ENUM ('vacation', 'expense', 'document', 'purchase', 'other');
CREATE TYPE approval_request_status AS ENUM ('draft', 'pending', 'auto_approved', 'approved', 'rejected', 'cancelled');
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'delegated');
CREATE TYPE document_category AS ENUM ('contract', 'policy', 'invoice', 'report', 'proposal', 'other');

-- Tabla principal de solicitudes
CREATE TABLE IF NOT EXISTS approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_type approval_request_type NOT NULL,
    requester_email VARCHAR(255) NOT NULL,
    title VARCHAR(512) NOT NULL,
    description TEXT,
    status approval_request_status DEFAULT 'draft',
    
    -- Campos específicos para vacaciones
    vacation_start_date DATE,
    vacation_end_date DATE,
    vacation_days INTEGER,
    vacation_type VARCHAR(64), -- 'annual', 'sick', 'personal', 'unpaid'
    
    -- Campos específicos para gastos
    expense_amount DECIMAL(12,2),
    expense_currency VARCHAR(3) DEFAULT 'USD',
    expense_category VARCHAR(128), -- 'travel', 'meals', 'supplies', 'training', 'other'
    expense_receipt_url TEXT,
    expense_date DATE,
    
    -- Campos específicos para documentos
    document_category document_category,
    document_url TEXT,
    document_version VARCHAR(64),
    requires_review BOOLEAN DEFAULT true,
    
    -- Metadatos generales
    metadata JSONB DEFAULT '{}',
    priority VARCHAR(16) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    auto_approved BOOLEAN DEFAULT false,
    auto_approval_rule_id UUID,
    
    -- Tracking
    submitted_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    flowable_process_instance_id VARCHAR(255),
    kestra_execution_id VARCHAR(255),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (requester_email) REFERENCES approval_users(user_email) ON DELETE RESTRICT
);

-- Tabla de reglas de aprobación automática
CREATE TABLE IF NOT EXISTS approval_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255) NOT NULL,
    rule_description TEXT,
    request_type approval_request_type NOT NULL,
    enabled BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0, -- Para orden de evaluación
    
    -- Condiciones (evaluadas como JSONB)
    conditions JSONB NOT NULL DEFAULT '{}',
    -- Ejemplo de conditions:
    -- {
    --   "amount_max": 1000,
    --   "requester_role": ["employee", "manager"],
    --   "department": ["engineering", "sales"],
    --   "vacation_days_max": 5,
    --   "approver_role": "direct_manager"
    -- }
    
    -- Acción
    auto_approve BOOLEAN DEFAULT true,
    require_notification BOOLEAN DEFAULT true,
    notification_emails TEXT[],
    
    -- Metadata
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de cadenas de aprobación (para flujos multi-nivel)
CREATE TABLE IF NOT EXISTS approval_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,
    level INTEGER NOT NULL,
    approver_email VARCHAR(255),
    approver_role VARCHAR(64), -- Para aprobaciones por rol cuando no hay usuario específico
    required BOOLEAN DEFAULT true,
    status approval_status DEFAULT 'pending',
    delegated_to VARCHAR(255),
    comments TEXT,
    approved_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    timeout_date TIMESTAMPTZ,
    notified_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (request_id) REFERENCES approval_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (approver_email) REFERENCES approval_users(user_email) ON DELETE RESTRICT,
    FOREIGN KEY (delegated_to) REFERENCES approval_users(user_email) ON DELETE SET NULL
);

-- Tabla de historial de aprobaciones (auditoría completa)
CREATE TABLE IF NOT EXISTS approval_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,
    chain_id UUID,
    action VARCHAR(64) NOT NULL, -- 'created', 'submitted', 'approved', 'rejected', 'delegated', 'auto_approved', 'cancelled'
    actor_email VARCHAR(255),
    actor_role VARCHAR(64),
    previous_status approval_request_status,
    new_status approval_request_status,
    comments TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (request_id) REFERENCES approval_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (chain_id) REFERENCES approval_chains(id) ON DELETE SET NULL
);

-- Tabla de documentos adjuntos
CREATE TABLE IF NOT EXISTS approval_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,
    file_name VARCHAR(512) NOT NULL,
    file_url TEXT NOT NULL,
    file_type VARCHAR(128),
    file_size BIGINT,
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (request_id) REFERENCES approval_requests(id) ON DELETE CASCADE
);

-- Tabla de notificaciones enviadas
CREATE TABLE IF NOT EXISTS approval_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,
    chain_id UUID,
    recipient_email VARCHAR(255) NOT NULL,
    notification_type VARCHAR(64) NOT NULL, -- 'new_request', 'pending_approval', 'approved', 'rejected', 'reminder'
    channel VARCHAR(64) NOT NULL, -- 'email', 'slack', 'teams', 'sms'
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    read_at TIMESTAMPTZ,
    status VARCHAR(64) DEFAULT 'sent', -- 'sent', 'delivered', 'failed', 'read'
    error_message TEXT,
    
    FOREIGN KEY (request_id) REFERENCES approval_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (chain_id) REFERENCES approval_chains(id) ON DELETE SET NULL
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_approval_requests_requester ON approval_requests(requester_email);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_type ON approval_requests(request_type);
CREATE INDEX IF NOT EXISTS idx_approval_requests_created ON approval_requests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_approval_requests_submitted ON approval_requests(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_approval_chains_request ON approval_chains(request_id);
CREATE INDEX IF NOT EXISTS idx_approval_chains_approver ON approval_chains(approver_email);
CREATE INDEX IF NOT EXISTS idx_approval_chains_status ON approval_chains(status);
CREATE INDEX IF NOT EXISTS idx_approval_history_request ON approval_history(request_id);
CREATE INDEX IF NOT EXISTS idx_approval_history_created ON approval_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_approval_rules_type ON approval_rules(request_type);
CREATE INDEX IF NOT EXISTS idx_approval_rules_enabled ON approval_rules(enabled) WHERE enabled = true;
CREATE INDEX IF NOT EXISTS idx_approval_notifications_request ON approval_notifications(request_id);
CREATE INDEX IF NOT EXISTS idx_approval_notifications_recipient ON approval_notifications(recipient_email);

-- Índices GIN para búsquedas JSONB
CREATE INDEX IF NOT EXISTS idx_approval_requests_metadata ON approval_requests USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_approval_rules_conditions ON approval_rules USING GIN (conditions);
CREATE INDEX IF NOT EXISTS idx_approval_history_metadata ON approval_history USING GIN (metadata);

-- Vistas útiles

-- Vista: Solicitudes pendientes por aprobador
CREATE OR REPLACE VIEW v_pending_approvals AS
SELECT 
    ac.id AS chain_id,
    ar.id AS request_id,
    ar.request_type,
    ar.title,
    ar.description,
    ar.requester_email,
    au.user_name AS requester_name,
    ac.approver_email,
    approver.user_name AS approver_name,
    ac.level,
    ar.priority,
    ar.created_at AS request_created_at,
    ar.submitted_at,
    ac.timeout_date,
    EXTRACT(EPOCH FROM (ac.timeout_date - NOW())) / 86400 AS days_until_timeout,
    ar.metadata
FROM approval_chains ac
JOIN approval_requests ar ON ac.request_id = ar.id
JOIN approval_users au ON ar.requester_email = au.user_email
LEFT JOIN approval_users approver ON ac.approver_email = approver.user_email
WHERE ac.status = 'pending' 
  AND ar.status = 'pending'
ORDER BY ar.priority DESC, ar.submitted_at ASC;

-- Vista: Resumen de solicitudes por usuario
CREATE OR REPLACE VIEW v_user_request_summary AS
SELECT 
    requester_email,
    request_type,
    status,
    COUNT(*) AS count,
    SUM(CASE WHEN request_type = 'expense' THEN expense_amount ELSE 0 END) AS total_expense_amount,
    SUM(CASE WHEN request_type = 'vacation' THEN vacation_days ELSE 0 END) AS total_vacation_days
FROM approval_requests
GROUP BY requester_email, request_type, status;

-- Vista: Métricas de aprobaciones
CREATE OR REPLACE VIEW v_approval_metrics AS
SELECT 
    request_type,
    status,
    COUNT(*) AS count,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) AS avg_hours_to_complete,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) FILTER (WHERE auto_approved = true) AS avg_hours_auto_approved,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) FILTER (WHERE auto_approved = false) AS avg_hours_manual_approved
FROM approval_requests
WHERE submitted_at IS NOT NULL
GROUP BY request_type, status;

-- Función: Obtener siguiente aprobador en la cadena
CREATE OR REPLACE FUNCTION get_next_approver(request_uuid UUID)
RETURNS TABLE(
    chain_id UUID,
    approver_email VARCHAR(255),
    level INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ac.id,
        ac.approver_email,
        ac.level
    FROM approval_chains ac
    WHERE ac.request_id = request_uuid
      AND ac.status = 'pending'
      AND ac.required = true
    ORDER BY ac.level ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Función: Crear cadena de aprobación automática basada en reglas
CREATE OR REPLACE FUNCTION create_approval_chain(
    p_request_id UUID,
    p_requester_email VARCHAR(255),
    p_request_type approval_request_type,
    p_amount DECIMAL DEFAULT NULL,
    p_vacation_days INTEGER DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_manager_email VARCHAR(255);
    v_chain_level INTEGER := 1;
    v_chain_id UUID;
BEGIN
    -- Obtener manager del solicitante
    SELECT manager_email INTO v_manager_email
    FROM approval_users
    WHERE user_email = p_requester_email;
    
    -- Nivel 1: Manager directo
    IF v_manager_email IS NOT NULL THEN
        INSERT INTO approval_chains (request_id, level, approver_email, required, timeout_date)
        VALUES (
            p_request_id,
            v_chain_level,
            v_manager_email,
            true,
            NOW() + INTERVAL '3 days'
        )
        RETURNING id INTO v_chain_id;
        
        v_chain_level := v_chain_level + 1;
    END IF;
    
    -- Si es gasto y supera cierto monto, agregar aprobación de finanzas
    IF p_request_type = 'expense' AND p_amount IS NOT NULL AND p_amount > 5000 THEN
        INSERT INTO approval_chains (request_id, level, approver_role, required, timeout_date)
        VALUES (
            p_request_id,
            v_chain_level,
            'finance_manager',
            true,
            NOW() + INTERVAL '5 days'
        );
        
        v_chain_level := v_chain_level + 1;
    END IF;
    
    -- Si es gasto muy grande, requiere aprobación de director
    IF p_request_type = 'expense' AND p_amount IS NOT NULL AND p_amount > 25000 THEN
        INSERT INTO approval_chains (request_id, level, approver_role, required, timeout_date)
        VALUES (
            p_request_id,
            v_chain_level,
            'director',
            true,
            NOW() + INTERVAL '7 days'
        );
        
        v_chain_level := v_chain_level + 1;
    END IF;
    
    -- Si son vacaciones de más de 10 días, requiere aprobación HR
    IF p_request_type = 'vacation' AND p_vacation_days IS NOT NULL AND p_vacation_days > 10 THEN
        INSERT INTO approval_chains (request_id, level, approver_role, required, timeout_date)
        VALUES (
            p_request_id,
            v_chain_level,
            'hr_manager',
            true,
            NOW() + INTERVAL '5 days'
        );
    END IF;
    
    RETURN v_chain_level - 1;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_approval_users_updated_at
    BEFORE UPDATE ON approval_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_requests_updated_at
    BEFORE UPDATE ON approval_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_chains_updated_at
    BEFORE UPDATE ON approval_chains
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_rules_updated_at
    BEFORE UPDATE ON approval_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Datos de ejemplo para testing
INSERT INTO approval_users (user_email, user_name, department, role, manager_email) VALUES
    ('john.doe@company.com', 'John Doe', 'Engineering', 'employee', 'jane.manager@company.com'),
    ('jane.manager@company.com', 'Jane Manager', 'Engineering', 'manager', 'bob.director@company.com'),
    ('bob.director@company.com', 'Bob Director', 'Engineering', 'director', 'alice.ceo@company.com'),
    ('alice.ceo@company.com', 'Alice CEO', 'Executive', 'ceo', NULL),
    ('finance@company.com', 'Finance Manager', 'Finance', 'finance_manager', 'alice.ceo@company.com'),
    ('hr@company.com', 'HR Manager', 'HR', 'hr_manager', 'alice.ceo@company.com')
ON CONFLICT (user_email) DO NOTHING;

-- Reglas automáticas de ejemplo
INSERT INTO approval_rules (rule_name, rule_description, request_type, conditions, auto_approve) VALUES
    (
        'Auto-aprobar gastos menores a $500',
        'Gastos menores a $500 se auto-aprueban si son de categorías comunes',
        'expense',
        '{"amount_max": 500, "expense_category": ["meals", "supplies", "travel"], "requester_role": ["employee", "manager"]}'::jsonb,
        true
    ),
    (
        'Auto-aprobar vacaciones cortas',
        'Vacaciones de 3 días o menos se auto-aprueban si el empleado tiene saldo disponible',
        'vacation',
        '{"vacation_days_max": 3, "vacation_type": "annual"}'::jsonb,
        true
    ),
    (
        'Auto-aprobar documentos de baja criticidad',
        'Documentos de categoría "other" o "report" se auto-aprueban',
        'document',
        '{"document_category": ["other", "report"], "requires_review": false}'::jsonb,
        true
    )
ON CONFLICT DO NOTHING;





