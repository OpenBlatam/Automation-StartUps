-- ============================================================================
-- Contract Management Schema - Sistema Completo de Gestión de Contratos
-- Incluye plantillas, versiones, firmas electrónicas y recordatorios de renovación
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tipos ENUM para estados y categorías
-- ============================================================================
CREATE TYPE contract_type AS ENUM (
    'employment',           -- Contrato laboral
    'service',              -- Contrato de servicios
    'nda',                  -- Acuerdo de confidencialidad
    'vendor',               -- Contrato con proveedor
    'client',               -- Contrato con cliente
    'lease',                -- Contrato de arrendamiento
    'partnership',          -- Contrato de asociación
    'other'                  -- Otro tipo
);

CREATE TYPE contract_status AS ENUM (
    'draft',                -- Borrador
    'pending_signature',   -- Pendiente de firma
    'partially_signed',     -- Parcialmente firmado
    'fully_signed',         -- Completamente firmado
    'expired',              -- Expirado
    'terminated',           -- Terminado
    'renewed',              -- Renovado
    'cancelled'             -- Cancelado
);

CREATE TYPE signature_status AS ENUM (
    'pending',              -- Pendiente
    'sent',                 -- Enviado
    'viewed',               -- Visto
    'signed',                -- Firmado
    'declined',             -- Rechazado
    'expired',              -- Expirado
    'cancelled'             -- Cancelado
);

CREATE TYPE esignature_provider AS ENUM (
    'docusign',             -- DocuSign
    'pandadoc',             -- PandaDoc
    'hellosign',            -- HelloSign
    'adobesign',            -- Adobe Sign
    'manual'                -- Manual (sin servicio)
);

-- ============================================================================
-- 2. Tabla de Plantillas de Contratos
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    contract_type contract_type NOT NULL,
    template_content TEXT NOT NULL, -- Contenido del template (HTML, Markdown, etc.)
    template_variables JSONB DEFAULT '{}', -- Variables disponibles: {{variable_name}}
    default_expiration_days INTEGER DEFAULT 365, -- Días de validez por defecto
    default_reminder_days INTEGER[] DEFAULT ARRAY[90, 60, 30, 14, 7], -- Días antes de expiración para recordatorios
    requires_legal_review BOOLEAN DEFAULT false,
    requires_manager_approval BOOLEAN DEFAULT false,
    signers_required JSONB DEFAULT '[]', -- Array de roles requeridos: [{"role": "employee", "order": 1}, {"role": "manager", "order": 2}]
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. Tabla Principal de Contratos
-- ============================================================================
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(255) UNIQUE NOT NULL,
    template_id VARCHAR(255) NOT NULL,
    contract_type contract_type NOT NULL,
    
    -- Información de las partes
    primary_party_type VARCHAR(64) NOT NULL, -- 'employee', 'customer', 'vendor', 'partner'
    primary_party_email VARCHAR(255) NOT NULL,
    primary_party_name VARCHAR(255) NOT NULL,
    primary_party_id VARCHAR(255), -- ID en sistema externo (HRIS, CRM, etc.)
    
    -- Información del contrato
    title VARCHAR(500) NOT NULL,
    description TEXT,
    contract_content TEXT NOT NULL, -- Contenido generado con variables reemplazadas
    contract_variables JSONB DEFAULT '{}', -- Valores de variables usadas
    
    -- Fechas importantes
    start_date DATE,
    end_date DATE,
    expiration_date DATE,
    signed_date TIMESTAMPTZ,
    
    -- Estado y flujo
    status contract_status DEFAULT 'draft',
    requires_legal_review BOOLEAN DEFAULT false,
    legal_reviewed BOOLEAN DEFAULT false,
    legal_reviewed_by VARCHAR(255),
    legal_reviewed_at TIMESTAMPTZ,
    
    -- Integración con servicios de firma electrónica
    esignature_provider esignature_provider,
    esignature_envelope_id VARCHAR(255), -- ID del sobre en DocuSign/PandaDoc
    esignature_document_id VARCHAR(255), -- ID del documento en el servicio
    esignature_url TEXT, -- URL para firmar
    
    -- Metadatos
    metadata JSONB DEFAULT '{}',
    renewal_reminder_sent BOOLEAN DEFAULT false,
    auto_renew BOOLEAN DEFAULT false,
    renewal_notice_days INTEGER DEFAULT 90,
    
    -- Tracking
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (template_id) REFERENCES contract_templates(template_id) ON DELETE RESTRICT
);

-- ============================================================================
-- 4. Tabla de Firmantes (Signers)
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_signers (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(255) NOT NULL,
    signer_email VARCHAR(255) NOT NULL,
    signer_name VARCHAR(255) NOT NULL,
    signer_role VARCHAR(128) NOT NULL, -- 'employee', 'manager', 'legal', 'client', 'vendor', etc.
    signer_order INTEGER NOT NULL, -- Orden de firma (1, 2, 3...)
    
    -- Estado de firma
    signature_status signature_status DEFAULT 'pending',
    signature_provider_id VARCHAR(255), -- ID del firmante en DocuSign/PandaDoc
    
    -- Fechas de firma
    signature_sent_at TIMESTAMPTZ,
    signature_viewed_at TIMESTAMPTZ,
    signature_signed_at TIMESTAMPTZ,
    signature_declined_at TIMESTAMPTZ,
    signature_expires_at TIMESTAMPTZ,
    
    -- Documento firmado
    signed_document_url TEXT,
    signed_document_hash VARCHAR(255), -- Hash para verificación de integridad
    
    -- Metadatos
    metadata JSONB DEFAULT '{}',
    reminder_sent_count INTEGER DEFAULT 0,
    last_reminder_sent_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE,
    UNIQUE(contract_id, signer_email)
);

-- ============================================================================
-- 5. Tabla de Versiones de Contratos Firmados
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_versions (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(255) NOT NULL,
    version_number INTEGER NOT NULL,
    version_reason VARCHAR(255), -- 'initial', 'amendment', 'renewal', 'correction'
    
    -- Contenido de la versión
    contract_content TEXT NOT NULL,
    contract_variables JSONB DEFAULT '{}',
    
    -- Documento firmado
    signed_document_url TEXT NOT NULL,
    signed_document_hash VARCHAR(255) NOT NULL,
    signed_document_size_bytes BIGINT,
    signed_document_format VARCHAR(64) DEFAULT 'pdf',
    
    -- Información de almacenamiento
    storage_provider VARCHAR(128), -- 's3', 'gcs', 'azure', 'local'
    storage_bucket VARCHAR(255),
    storage_path TEXT,
    
    -- Estado
    is_current BOOLEAN DEFAULT false, -- Versión actual
    is_archived BOOLEAN DEFAULT false,
    
    -- Fechas
    created_at TIMESTAMPTZ DEFAULT NOW(),
    signed_at TIMESTAMPTZ,
    
    -- Metadatos
    metadata JSONB DEFAULT '{}',
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE,
    UNIQUE(contract_id, version_number)
);

-- ============================================================================
-- 6. Tabla de Recordatorios de Renovación
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_renewal_reminders (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(255) NOT NULL,
    reminder_type VARCHAR(64) NOT NULL, -- 'expiration_warning', 'renewal_due', 'renewal_overdue'
    days_before_expiration INTEGER, -- Días antes de expiración (90, 60, 30, etc.)
    
    -- Información del recordatorio
    reminder_sent_at TIMESTAMPTZ DEFAULT NOW(),
    reminder_sent_to VARCHAR(255) NOT NULL, -- Email del destinatario
    reminder_recipient_role VARCHAR(128), -- 'contract_owner', 'manager', 'legal', 'all'
    
    -- Estado
    reminder_status VARCHAR(64) DEFAULT 'sent', -- 'sent', 'delivered', 'opened', 'clicked', 'failed'
    reminder_channel VARCHAR(64) DEFAULT 'email', -- 'email', 'slack', 'sms', 'in_app'
    
    -- Metadatos
    metadata JSONB DEFAULT '{}',
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE
);

-- ============================================================================
-- 7. Tabla de Eventos de Contratos (Auditoría)
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract_events (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(128) NOT NULL, -- 'created', 'template_applied', 'sent_for_signature', 'signed', 'declined', 'expired', 'renewed', 'reminder_sent', etc.
    event_description TEXT,
    
    -- Usuario/actor
    event_actor_email VARCHAR(255),
    event_actor_role VARCHAR(128),
    
    -- Datos del evento
    event_data JSONB DEFAULT '{}',
    
    -- Timestamp
    event_timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE
);

-- ============================================================================
-- 8. Índices para consultas rápidas
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_contracts_template_id ON contracts(template_id);
CREATE INDEX IF NOT EXISTS idx_contracts_primary_party_email ON contracts(primary_party_email);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_type ON contracts(contract_type);
CREATE INDEX IF NOT EXISTS idx_contracts_expiration_date ON contracts(expiration_date);
CREATE INDEX IF NOT EXISTS idx_contracts_start_date ON contracts(start_date);
CREATE INDEX IF NOT EXISTS idx_contracts_end_date ON contracts(end_date);
CREATE INDEX IF NOT EXISTS idx_contracts_created_at ON contracts(created_at);
CREATE INDEX IF NOT EXISTS idx_contracts_esignature_envelope_id ON contracts(esignature_envelope_id);

CREATE INDEX IF NOT EXISTS idx_signers_contract_id ON contract_signers(contract_id);
CREATE INDEX IF NOT EXISTS idx_signers_email ON contract_signers(signer_email);
CREATE INDEX IF NOT EXISTS idx_signers_status ON contract_signers(signature_status);
CREATE INDEX IF NOT EXISTS idx_signers_expires_at ON contract_signers(signature_expires_at);

CREATE INDEX IF NOT EXISTS idx_versions_contract_id ON contract_versions(contract_id);
CREATE INDEX IF NOT EXISTS idx_versions_current ON contract_versions(is_current) WHERE is_current = true;
CREATE INDEX IF NOT EXISTS idx_versions_created_at ON contract_versions(created_at);

CREATE INDEX IF NOT EXISTS idx_reminders_contract_id ON contract_renewal_reminders(contract_id);
CREATE INDEX IF NOT EXISTS idx_reminders_sent_at ON contract_renewal_reminders(reminder_sent_at);
CREATE INDEX IF NOT EXISTS idx_reminders_status ON contract_renewal_reminders(reminder_status);

CREATE INDEX IF NOT EXISTS idx_events_contract_id ON contract_events(contract_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON contract_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON contract_events(event_timestamp);

-- ============================================================================
-- 9. Vistas útiles
-- ============================================================================

-- Vista de contratos pendientes de firma
CREATE OR REPLACE VIEW contracts_pending_signature AS
SELECT 
    c.contract_id,
    c.title,
    c.primary_party_name,
    c.primary_party_email,
    c.status,
    COUNT(cs.id) as total_signers,
    COUNT(CASE WHEN cs.signature_status IN ('pending', 'sent', 'viewed') THEN cs.id END) as pending_signers,
    COUNT(CASE WHEN cs.signature_status = 'signed' THEN cs.id END) as signed_count,
    MIN(cs.signature_expires_at) as earliest_expiration,
    c.esignature_url,
    c.created_at
FROM contracts c
LEFT JOIN contract_signers cs ON c.contract_id = cs.contract_id
WHERE c.status IN ('pending_signature', 'partially_signed')
GROUP BY c.contract_id, c.title, c.primary_party_name, c.primary_party_email, 
         c.status, c.esignature_url, c.created_at;

-- Vista de contratos próximos a expirar
CREATE OR REPLACE VIEW contracts_expiring_soon AS
SELECT 
    c.contract_id,
    c.title,
    c.primary_party_name,
    c.primary_party_email,
    c.contract_type,
    c.expiration_date,
    c.end_date,
    CURRENT_DATE - c.expiration_date as days_until_expiration,
    c.auto_renew,
    c.renewal_reminder_sent,
    COUNT(crr.id) as reminders_sent_count,
    MAX(crr.reminder_sent_at) as last_reminder_sent_at
FROM contracts c
LEFT JOIN contract_renewal_reminders crr ON c.contract_id = crr.contract_id
WHERE c.status = 'fully_signed'
  AND c.expiration_date IS NOT NULL
  AND c.expiration_date >= CURRENT_DATE
  AND c.expiration_date <= CURRENT_DATE + INTERVAL '90 days'
GROUP BY c.contract_id, c.title, c.primary_party_name, c.primary_party_email,
         c.contract_type, c.expiration_date, c.end_date, c.auto_renew, c.renewal_reminder_sent;

-- Vista de estadísticas de contratos
CREATE OR REPLACE VIEW contract_statistics AS
SELECT 
    contract_type,
    status,
    COUNT(*) as contract_count,
    COUNT(CASE WHEN signed_date IS NOT NULL THEN 1 END) as signed_count,
    AVG(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as avg_days_to_sign,
    COUNT(CASE WHEN expiration_date < CURRENT_DATE THEN 1 END) as expired_count,
    COUNT(CASE WHEN expiration_date >= CURRENT_DATE AND expiration_date <= CURRENT_DATE + INTERVAL '30 days' THEN 1 END) as expiring_30_days,
    COUNT(CASE WHEN auto_renew = true THEN 1 END) as auto_renew_count
FROM contracts
GROUP BY contract_type, status;

-- ============================================================================
-- 10. Comentarios en las tablas
-- ============================================================================
COMMENT ON TABLE contract_templates IS 'Plantillas de contratos reutilizables con variables';
COMMENT ON TABLE contracts IS 'Contratos generados a partir de plantillas';
COMMENT ON TABLE contract_signers IS 'Firmantes de contratos y su estado de firma';
COMMENT ON TABLE contract_versions IS 'Versiones firmadas de contratos almacenadas';
COMMENT ON TABLE contract_renewal_reminders IS 'Recordatorios enviados para renovación de contratos';
COMMENT ON TABLE contract_events IS 'Auditoría de eventos relacionados con contratos';

COMMIT;

