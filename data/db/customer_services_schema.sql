-- ============================================================================
-- Customer Services Schema
-- Tablas para gestionar servicios activados para clientes
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de API Keys para Clientes
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer_api_keys (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_key_name VARCHAR(255), -- Nombre descriptivo de la API key
    permissions JSONB DEFAULT '{}', -- Permisos específicos de la API key
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Referencia al contrato que activó este servicio
    contract_id VARCHAR(255),
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_customer_api_keys_email ON customer_api_keys(customer_email);
CREATE INDEX IF NOT EXISTS idx_customer_api_keys_key ON customer_api_keys(api_key);
CREATE INDEX IF NOT EXISTS idx_customer_api_keys_active ON customer_api_keys(is_active);
CREATE INDEX IF NOT EXISTS idx_customer_api_keys_contract ON customer_api_keys(contract_id);

-- ============================================================================
-- 2. Tabla de Servicios de Clientes
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer_services (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    service_name VARCHAR(128) NOT NULL, -- 'api_access', 'dashboard', 'support', etc.
    service_config JSONB DEFAULT '{}', -- Configuración específica del servicio
    status VARCHAR(64) DEFAULT 'active', -- 'active', 'suspended', 'cancelled', 'expired'
    
    -- Referencia al contrato que activó este servicio
    contract_id VARCHAR(255),
    
    -- Fechas
    activated_at TIMESTAMPTZ DEFAULT NOW(),
    suspended_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    
    -- Metadatos
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE SET NULL,
    UNIQUE(customer_email, service_name)
);

CREATE INDEX IF NOT EXISTS idx_customer_services_email ON customer_services(customer_email);
CREATE INDEX IF NOT EXISTS idx_customer_services_name ON customer_services(service_name);
CREATE INDEX IF NOT EXISTS idx_customer_services_status ON customer_services(status);
CREATE INDEX IF NOT EXISTS idx_customer_services_contract ON customer_services(contract_id);
CREATE INDEX IF NOT EXISTS idx_customer_services_activated ON customer_services(activated_at);

-- ============================================================================
-- 3. Tabla de Eventos de Activación de Servicios
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer_service_events (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    service_name VARCHAR(128),
    contract_id VARCHAR(255),
    event_type VARCHAR(128) NOT NULL, -- 'activated', 'suspended', 'cancelled', 'renewed', 'expired'
    event_description TEXT,
    event_data JSONB DEFAULT '{}',
    event_timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_service_events_email ON customer_service_events(customer_email);
CREATE INDEX IF NOT EXISTS idx_service_events_type ON customer_service_events(event_type);
CREATE INDEX IF NOT EXISTS idx_service_events_timestamp ON customer_service_events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_service_events_contract ON customer_service_events(contract_id);

-- ============================================================================
-- 4. Vistas útiles
-- ============================================================================

-- Vista de servicios activos por cliente
CREATE OR REPLACE VIEW customer_active_services AS
SELECT 
    cs.customer_email,
    cs.service_name,
    cs.status,
    cs.activated_at,
    cs.contract_id,
    c.title as contract_title,
    c.status as contract_status,
    cs.metadata
FROM customer_services cs
LEFT JOIN contracts c ON cs.contract_id = c.contract_id
WHERE cs.status = 'active'
ORDER BY cs.activated_at DESC;

-- Vista de resumen de servicios por cliente
CREATE OR REPLACE VIEW customer_services_summary AS
SELECT 
    customer_email,
    COUNT(*) as total_services,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_services,
    COUNT(CASE WHEN status = 'suspended' THEN 1 END) as suspended_services,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_services,
    MIN(activated_at) as first_service_activated,
    MAX(activated_at) as last_service_activated
FROM customer_services
GROUP BY customer_email;

-- ============================================================================
-- 5. Comentarios
-- ============================================================================
COMMENT ON TABLE customer_api_keys IS 'API keys generadas para clientes';
COMMENT ON TABLE customer_services IS 'Servicios activados para cada cliente';
COMMENT ON TABLE customer_service_events IS 'Auditoría de eventos de servicios';

COMMIT;












