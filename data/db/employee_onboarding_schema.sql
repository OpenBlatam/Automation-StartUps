-- ============================================================================
-- Employee Onboarding Schema - Sistema Completo de Onboarding y RRHH
-- Incluye checklist automatizada, capacitaciones y gestión de accesos
-- ============================================================================

-- Tabla principal de empleados en onboarding
CREATE TABLE IF NOT EXISTS employee_onboarding (
    id SERIAL PRIMARY KEY,
    employee_email VARCHAR(255) NOT NULL UNIQUE,
    employee_id VARCHAR(255),
    full_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    position VARCHAR(255),
    department VARCHAR(255),
    start_date DATE NOT NULL,
    manager_email VARCHAR(255),
    manager_name VARCHAR(255),
    office_location VARCHAR(255),
    phone VARCHAR(64),
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    hris_source VARCHAR(64) DEFAULT 'provided',
    status VARCHAR(64) DEFAULT 'in_progress', -- 'pending', 'in_progress', 'completed', 'failed', 'on_hold'
    contract_signed_date TIMESTAMPTZ,
    onboarding_started_at TIMESTAMPTZ DEFAULT NOW(),
    onboarding_completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de checklist de onboarding (tareas a completar)
CREATE TABLE IF NOT EXISTS onboarding_checklist (
    id SERIAL PRIMARY KEY,
    employee_email VARCHAR(255) NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    task_category VARCHAR(128) NOT NULL, -- 'account_setup', 'documents', 'training', 'access', 'hr', 'it'
    task_title VARCHAR(500) NOT NULL,
    task_description TEXT,
    assignee VARCHAR(255), -- Email de quien debe completar la tarea
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'skipped', 'blocked'
    due_date DATE,
    completed_at TIMESTAMPTZ,
    completed_by VARCHAR(255),
    metadata JSONB, -- Información adicional (links, documentos, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (employee_email) REFERENCES employee_onboarding(employee_email) ON DELETE CASCADE,
    UNIQUE(employee_email, task_id)
);

-- Tabla de capacitaciones asignadas
CREATE TABLE IF NOT EXISTS onboarding_trainings (
    id SERIAL PRIMARY KEY,
    employee_email VARCHAR(255) NOT NULL,
    training_id VARCHAR(255) NOT NULL,
    training_name VARCHAR(500) NOT NULL,
    training_type VARCHAR(128), -- 'mandatory', 'optional', 'department_specific', 'role_specific'
    training_provider VARCHAR(255), -- 'internal', 'external', 'platform_name'
    training_url TEXT,
    status VARCHAR(64) DEFAULT 'assigned', -- 'assigned', 'in_progress', 'completed', 'overdue', 'skipped'
    assigned_date DATE NOT NULL,
    due_date DATE,
    completed_date DATE,
    completion_percentage INTEGER DEFAULT 0,
    certificate_url TEXT,
    metadata JSONB, -- Información adicional del training
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (employee_email) REFERENCES employee_onboarding(employee_email) ON DELETE CASCADE,
    UNIQUE(employee_email, training_id)
);

-- Tabla de accesos y permisos
CREATE TABLE IF NOT EXISTS onboarding_accesses (
    id SERIAL PRIMARY KEY,
    employee_email VARCHAR(255) NOT NULL,
    access_type VARCHAR(128) NOT NULL, -- 'system', 'application', 'folder', 'network', 'database', 'api'
    access_name VARCHAR(255) NOT NULL,
    access_provider VARCHAR(255), -- 'okta', 'azure_ad', 'google_workspace', 'custom'
    access_id VARCHAR(255), -- ID del acceso en el sistema externo
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'provisioned', 'active', 'failed', 'revoked'
    provisioned_at TIMESTAMPTZ,
    access_level VARCHAR(128), -- 'read', 'write', 'admin', 'owner'
    metadata JSONB, -- Detalles del acceso (permissions, groups, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (employee_email) REFERENCES employee_onboarding(employee_email) ON DELETE CASCADE,
    UNIQUE(employee_email, access_type, access_name)
);

-- Tabla de acciones del onboarding (historial de todas las acciones)
CREATE TABLE IF NOT EXISTS onboarding_actions (
    id SERIAL PRIMARY KEY,
    employee_email VARCHAR(255) NOT NULL,
    action_type VARCHAR(64) NOT NULL, -- 'email_sent', 'account_created', 'training_assigned', 'access_granted', etc.
    action_status VARCHAR(64) NOT NULL, -- 'success', 'failed', 'pending'
    action_details JSONB,
    error_message TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    executed_by VARCHAR(255), -- Sistema o usuario que ejecutó la acción
    FOREIGN KEY (employee_email) REFERENCES employee_onboarding(employee_email) ON DELETE CASCADE
);

-- Tabla de cuentas creadas
CREATE TABLE IF NOT EXISTS onboarding_accounts (
    id SERIAL PRIMARY KEY,
    employee_email VARCHAR(255) NOT NULL,
    account_type VARCHAR(64) NOT NULL, -- 'idp', 'email', 'workspace', 'slack', 'jira', 'github', etc.
    account_provider VARCHAR(255), -- 'okta', 'google', 'microsoft', 'atlassian', etc.
    account_id VARCHAR(255),
    account_url TEXT,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'created', 'active', 'failed'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (employee_email) REFERENCES employee_onboarding(employee_email) ON DELETE CASCADE,
    UNIQUE(employee_email, account_type)
);

-- Tabla de emails enviados
CREATE TABLE IF NOT EXISTS onboarding_emails (
    id SERIAL PRIMARY KEY,
    employee_email VARCHAR(255) NOT NULL,
    email_type VARCHAR(128) NOT NULL, -- 'welcome', 'training_assignment', 'reminder', 'completion'
    subject VARCHAR(500),
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(64) DEFAULT 'sent', -- 'sent', 'failed', 'bounced'
    email_provider VARCHAR(255),
    metadata JSONB,
    FOREIGN KEY (employee_email) REFERENCES employee_onboarding(employee_email) ON DELETE CASCADE
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_onboarding_status ON employee_onboarding(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_start_date ON employee_onboarding(start_date);
CREATE INDEX IF NOT EXISTS idx_onboarding_department ON employee_onboarding(department);
CREATE INDEX IF NOT EXISTS idx_onboarding_manager ON employee_onboarding(manager_email);

CREATE INDEX IF NOT EXISTS idx_checklist_email ON onboarding_checklist(employee_email);
CREATE INDEX IF NOT EXISTS idx_checklist_status ON onboarding_checklist(status);
CREATE INDEX IF NOT EXISTS idx_checklist_category ON onboarding_checklist(task_category);
CREATE INDEX IF NOT EXISTS idx_checklist_due_date ON onboarding_checklist(due_date);

CREATE INDEX IF NOT EXISTS idx_trainings_email ON onboarding_trainings(employee_email);
CREATE INDEX IF NOT EXISTS idx_trainings_status ON onboarding_trainings(status);
CREATE INDEX IF NOT EXISTS idx_trainings_due_date ON onboarding_trainings(due_date);

CREATE INDEX IF NOT EXISTS idx_accesses_email ON onboarding_accesses(employee_email);
CREATE INDEX IF NOT EXISTS idx_accesses_type ON onboarding_accesses(access_type);
CREATE INDEX IF NOT EXISTS idx_accesses_status ON onboarding_accesses(status);

CREATE INDEX IF NOT EXISTS idx_actions_email ON onboarding_actions(employee_email);
CREATE INDEX IF NOT EXISTS idx_actions_type ON onboarding_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_actions_executed_at ON onboarding_actions(executed_at);

CREATE INDEX IF NOT EXISTS idx_accounts_email ON onboarding_accounts(employee_email);
CREATE INDEX IF NOT EXISTS idx_accounts_type ON onboarding_accounts(account_type);

CREATE INDEX IF NOT EXISTS idx_emails_email ON onboarding_emails(employee_email);
CREATE INDEX IF NOT EXISTS idx_emails_type ON onboarding_emails(email_type);

-- Vista para dashboard de progreso
CREATE OR REPLACE VIEW onboarding_progress AS
SELECT 
    eo.employee_email,
    eo.full_name,
    eo.department,
    eo.status,
    eo.start_date,
    -- Progreso de checklist
    COUNT(DISTINCT oc.id) as total_checklist_items,
    COUNT(DISTINCT CASE WHEN oc.status = 'completed' THEN oc.id END) as completed_checklist_items,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN oc.status = 'completed' THEN oc.id END) / NULLIF(COUNT(DISTINCT oc.id), 0), 2) as checklist_progress_pct,
    -- Progreso de capacitaciones
    COUNT(DISTINCT ot.id) as total_trainings,
    COUNT(DISTINCT CASE WHEN ot.status = 'completed' THEN ot.id END) as completed_trainings,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ot.status = 'completed' THEN ot.id END) / NULLIF(COUNT(DISTINCT ot.id), 0), 2) as training_progress_pct,
    -- Progreso de accesos
    COUNT(DISTINCT oa.id) as total_accesses,
    COUNT(DISTINCT CASE WHEN oa.status = 'active' THEN oa.id END) as active_accesses,
    -- Progreso general
    CASE 
        WHEN eo.status = 'completed' THEN 100
        ELSE ROUND(
            (COALESCE(COUNT(DISTINCT CASE WHEN oc.status = 'completed' THEN oc.id END), 0) * 0.4 +
             COALESCE(COUNT(DISTINCT CASE WHEN ot.status = 'completed' THEN ot.id END), 0) * 0.3 +
             COALESCE(COUNT(DISTINCT CASE WHEN oa.status = 'active' THEN oa.id END), 0) * 0.3) /
            NULLIF(
                (COALESCE(COUNT(DISTINCT oc.id), 1) * 0.4 +
                 COALESCE(COUNT(DISTINCT ot.id), 1) * 0.3 +
                 COALESCE(COUNT(DISTINCT oa.id), 1) * 0.3),
                0
            ) * 100, 2
        )
    END as overall_progress_pct,
    eo.onboarding_started_at,
    eo.onboarding_completed_at,
    CASE 
        WHEN eo.onboarding_completed_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (eo.onboarding_completed_at - eo.onboarding_started_at)) / 86400
        ELSE NULL
    END as days_to_complete
FROM employee_onboarding eo
LEFT JOIN onboarding_checklist oc ON eo.employee_email = oc.employee_email
LEFT JOIN onboarding_trainings ot ON eo.employee_email = ot.employee_email
LEFT JOIN onboarding_accesses oa ON eo.employee_email = oa.employee_email
GROUP BY eo.employee_email, eo.full_name, eo.department, eo.status, eo.start_date, 
         eo.onboarding_started_at, eo.onboarding_completed_at;

-- Comentarios en las tablas
COMMENT ON TABLE employee_onboarding IS 'Datos principales de empleados en proceso de onboarding';
COMMENT ON TABLE onboarding_checklist IS 'Checklist de tareas a completar durante el onboarding';
COMMENT ON TABLE onboarding_trainings IS 'Capacitaciones asignadas al empleado';
COMMENT ON TABLE onboarding_accesses IS 'Accesos y permisos otorgados al empleado';
COMMENT ON TABLE onboarding_actions IS 'Historial de todas las acciones ejecutadas durante el onboarding';
COMMENT ON TABLE onboarding_accounts IS 'Cuentas creadas en sistemas externos';
COMMENT ON TABLE onboarding_emails IS 'Historial de emails enviados durante el onboarding';
COMMENT ON VIEW onboarding_progress IS 'Vista consolidada del progreso de onboarding por empleado';

