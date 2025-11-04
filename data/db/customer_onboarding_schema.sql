-- ============================================================================
-- Customer Onboarding Schema
-- Sistema completo de onboarding automatizado de clientes
-- ============================================================================

-- Tabla principal de clientes en proceso de onboarding
CREATE TABLE IF NOT EXISTS customer_onboarding (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) UNIQUE,
    external_customer_id VARCHAR(255), -- ID en sistema externo (CRM, etc.)
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    phone VARCHAR(64),
    country VARCHAR(64),
    timezone VARCHAR(64),
    
    -- Información de identidad verificada
    identity_verified BOOLEAN DEFAULT FALSE,
    identity_verification_method VARCHAR(64), -- 'email', 'sms', 'document', 'kyc_provider'
    identity_verification_status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'in_progress', 'verified', 'failed', 'rejected'
    identity_verified_at TIMESTAMPTZ,
    identity_documents JSONB, -- Almacena información de documentos verificados
    
    -- Estado del onboarding
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'collecting_info', 'verifying_identity', 'activating_services', 'completed', 'failed', 'rejected'
    onboarding_started_at TIMESTAMPTZ DEFAULT NOW(),
    onboarding_completed_at TIMESTAMPTZ,
    
    -- Información del plan/servicio
    service_plan VARCHAR(128),
    service_tier VARCHAR(128),
    services_to_activate TEXT[], -- Array de servicios a activar
    
    -- Metadatos
    source VARCHAR(128), -- 'website', 'sales', 'api', 'import'
    utm_source VARCHAR(128),
    utm_campaign VARCHAR(128),
    sales_rep_email VARCHAR(255),
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    metadata JSONB, -- Información adicional flexible
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_customer_onboarding_email ON customer_onboarding(customer_email);
CREATE INDEX IF NOT EXISTS idx_customer_onboarding_status ON customer_onboarding(status);
CREATE INDEX IF NOT EXISTS idx_customer_onboarding_idempotency ON customer_onboarding(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_customer_onboarding_created_at ON customer_onboarding(created_at);
CREATE INDEX IF NOT EXISTS idx_customer_onboarding_external_id ON customer_onboarding(external_customer_id);

-- Tabla de información recolectada
CREATE TABLE IF NOT EXISTS customer_onboarding_data (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    data_type VARCHAR(64) NOT NULL, -- 'contact_info', 'business_info', 'preferences', 'billing', 'custom'
    field_name VARCHAR(128) NOT NULL,
    field_value TEXT,
    field_data JSONB, -- Para valores complejos
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (customer_email) REFERENCES customer_onboarding(customer_email) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_customer_onboarding_data_email ON customer_onboarding_data(customer_email);
CREATE INDEX IF NOT EXISTS idx_customer_onboarding_data_type ON customer_onboarding_data(data_type);

-- Tabla de acciones de verificación de identidad
CREATE TABLE IF NOT EXISTS customer_identity_verifications (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    verification_type VARCHAR(64) NOT NULL, -- 'email', 'sms', 'document', 'kyc', 'biometric'
    verification_provider VARCHAR(128), -- Nombre del proveedor (si aplica)
    verification_status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'in_progress', 'verified', 'failed', 'expired'
    verification_code VARCHAR(128), -- Para códigos OTP
    verification_token VARCHAR(512), -- Token de verificación
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    expires_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    provider_response JSONB, -- Respuesta completa del proveedor
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (customer_email) REFERENCES customer_onboarding(customer_email) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_identity_verifications_email ON customer_identity_verifications(customer_email);
CREATE INDEX IF NOT EXISTS idx_identity_verifications_status ON customer_identity_verifications(verification_status);
CREATE INDEX IF NOT EXISTS idx_identity_verifications_token ON customer_identity_verifications(verification_token);

-- Tabla de cuentas y servicios activados
CREATE TABLE IF NOT EXISTS customer_accounts (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    account_type VARCHAR(64) NOT NULL, -- 'user_account', 'api_key', 'dashboard', 'billing_account', 'support_account'
    service_name VARCHAR(128) NOT NULL, -- 'platform', 'api', 'dashboard', 'billing', 'support'
    account_id VARCHAR(255), -- ID de la cuenta en el sistema de servicio
    account_status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'creating', 'active', 'suspended', 'failed'
    activation_requested_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    credentials JSONB, -- Credenciales o tokens (encriptados en producción)
    metadata JSONB, -- Información adicional del servicio
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (customer_email) REFERENCES customer_onboarding(customer_email) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_customer_accounts_email ON customer_accounts(customer_email);
CREATE INDEX IF NOT EXISTS idx_customer_accounts_service ON customer_accounts(service_name);
CREATE INDEX IF NOT EXISTS idx_customer_accounts_status ON customer_accounts(account_status);

-- Tabla de eventos del onboarding (auditoría)
CREATE TABLE IF NOT EXISTS customer_onboarding_events (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    event_type VARCHAR(64) NOT NULL, -- 'info_collected', 'identity_verification_started', 'identity_verified', 'account_created', 'service_activated', 'onboarding_completed', 'error'
    event_details JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (customer_email) REFERENCES customer_onboarding(customer_email) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_onboarding_events_email ON customer_onboarding_events(customer_email);
CREATE INDEX IF NOT EXISTS idx_onboarding_events_type ON customer_onboarding_events(event_type);
CREATE INDEX IF NOT EXISTS idx_onboarding_events_created_at ON customer_onboarding_events(created_at);

-- Vista para métricas de onboarding
CREATE OR REPLACE VIEW customer_onboarding_metrics AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_onboardings,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected,
    COUNT(CASE WHEN identity_verified = TRUE THEN 1 END) as identity_verified,
    ROUND(AVG(EXTRACT(EPOCH FROM (onboarding_completed_at - onboarding_started_at)) / 3600), 2) as avg_hours_to_complete,
    COUNT(DISTINCT service_plan) as unique_plans,
    COUNT(DISTINCT source) as unique_sources
FROM customer_onboarding
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Vista para resumen de cuentas activadas
CREATE OR REPLACE VIEW customer_accounts_summary AS
SELECT 
    co.customer_email,
    co.status as onboarding_status,
    co.identity_verified,
    COUNT(ca.id) as total_accounts,
    COUNT(CASE WHEN ca.account_status = 'active' THEN 1 END) as active_accounts,
    COUNT(CASE WHEN ca.account_status = 'pending' THEN 1 END) as pending_accounts,
    COUNT(CASE WHEN ca.account_status = 'failed' THEN 1 END) as failed_accounts,
    ARRAY_AGG(DISTINCT ca.service_name) as services
FROM customer_onboarding co
LEFT JOIN customer_accounts ca ON co.customer_email = ca.customer_email
GROUP BY co.customer_email, co.status, co.identity_verified;

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_customer_onboarding_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_customer_onboarding_updated_at
    BEFORE UPDATE ON customer_onboarding
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_onboarding_updated_at();

CREATE TRIGGER trigger_update_identity_verifications_updated_at
    BEFORE UPDATE ON customer_identity_verifications
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_onboarding_updated_at();

CREATE TRIGGER trigger_update_customer_accounts_updated_at
    BEFORE UPDATE ON customer_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_onboarding_updated_at();

-- Comentarios en tablas
COMMENT ON TABLE customer_onboarding IS 'Tabla principal de clientes en proceso de onboarding';
COMMENT ON TABLE customer_onboarding_data IS 'Información recolectada durante el onboarding';
COMMENT ON TABLE customer_identity_verifications IS 'Verificaciones de identidad de clientes';
COMMENT ON TABLE customer_accounts IS 'Cuentas y servicios activados para clientes';
COMMENT ON TABLE customer_onboarding_events IS 'Eventos y auditoría del proceso de onboarding';





