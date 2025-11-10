-- ============================================================================
-- Migraciones Adicionales para Sistema de Contratos
-- Versionado de Templates, Workflow de Aprobación, Tags y Comentarios
-- ============================================================================

BEGIN;

-- ============================================================================
-- Tabla de Versiones de Plantillas
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_template_versions (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(255) NOT NULL,
    version_number INTEGER NOT NULL,
    
    -- Contenido de la versión
    template_content TEXT NOT NULL,
    template_variables JSONB DEFAULT '{}',
    default_expiration_days INTEGER DEFAULT 365,
    signers_required JSONB DEFAULT '[]',
    
    -- Hash para comparación
    content_hash VARCHAR(64) NOT NULL,
    
    -- Notas de versión
    version_notes TEXT,
    
    -- Tracking
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (template_id) REFERENCES contract_templates(template_id) ON DELETE CASCADE,
    UNIQUE(template_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_template_versions_template_id ON contract_template_versions(template_id);
CREATE INDEX IF NOT EXISTS idx_template_versions_version ON contract_template_versions(template_id, version_number);

-- ============================================================================
-- Tabla de Aprobaciones de Contratos
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_approvals (
    id SERIAL PRIMARY KEY,
    approval_id VARCHAR(255) UNIQUE NOT NULL,
    contract_id VARCHAR(255) NOT NULL,
    
    -- Estado de aprobación
    approval_status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'cancelled'
    
    -- Notas
    approval_notes TEXT,
    
    -- Fechas
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    requested_by VARCHAR(255),
    approved_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE
);

-- ============================================================================
-- Tabla de Aprobadores
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_approvers (
    id SERIAL PRIMARY KEY,
    approval_id VARCHAR(255) NOT NULL,
    
    -- Información del aprobador
    approver_email VARCHAR(255) NOT NULL,
    approver_name VARCHAR(255) NOT NULL,
    approver_role VARCHAR(128), -- 'manager', 'legal', 'finance', 'executive'
    
    -- Orden de aprobación
    approval_order INTEGER NOT NULL,
    
    -- Estado
    approval_status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    
    -- Notas
    approval_notes TEXT,
    
    -- Fechas
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    
    FOREIGN KEY (approval_id) REFERENCES contract_approvals(approval_id) ON DELETE CASCADE,
    UNIQUE(approval_id, approver_email)
);

-- ============================================================================
-- Tabla de Comentarios de Contratos
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_comments (
    id SERIAL PRIMARY KEY,
    comment_id VARCHAR(255) UNIQUE NOT NULL,
    contract_id VARCHAR(255) NOT NULL,
    
    -- Contenido del comentario
    comment_text TEXT NOT NULL,
    
    -- Autor
    author_email VARCHAR(255) NOT NULL,
    author_name VARCHAR(255),
    
    -- Tipo y visibilidad
    comment_type VARCHAR(64) DEFAULT 'comment', -- 'comment', 'review', 'suggestion', 'question'
    is_internal BOOLEAN DEFAULT true, -- Comentarios internos no visibles para firmantes
    
    -- Fechas
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE
);

-- ============================================================================
-- Índices para Aprobaciones
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_approvals_contract_id ON contract_approvals(contract_id);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON contract_approvals(approval_status);
CREATE INDEX IF NOT EXISTS idx_approvals_requested_at ON contract_approvals(requested_at);

CREATE INDEX IF NOT EXISTS idx_approvers_approval_id ON contract_approvers(approval_id);
CREATE INDEX IF NOT EXISTS idx_approvers_email ON contract_approvers(approver_email);
CREATE INDEX IF NOT EXISTS idx_approvers_status ON contract_approvers(approval_status);

-- ============================================================================
-- Índices para Comentarios
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_comments_contract_id ON contract_comments(contract_id);
CREATE INDEX IF NOT EXISTS idx_comments_author_email ON contract_comments(author_email);
CREATE INDEX IF NOT EXISTS idx_comments_type ON contract_comments(comment_type);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON contract_comments(created_at);

-- ============================================================================
-- Índices para Tags (almacenados en metadata)
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_contracts_tags ON contracts USING gin(metadata jsonb_path_ops);

-- ============================================================================
-- Comentarios
-- ============================================================================
COMMENT ON TABLE contract_template_versions IS 'Historial de versiones de plantillas de contratos';
COMMENT ON TABLE contract_approvals IS 'Solicitudes de aprobación para contratos';
COMMENT ON TABLE contract_approvers IS 'Aprobadores individuales de contratos';
COMMENT ON TABLE contract_comments IS 'Comentarios y revisiones de contratos';

COMMIT;
