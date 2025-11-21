-- Tabla de auditoría para integración HubSpot → ManyChat
-- Crea la tabla y índices necesarios para tracking de mensajes enviados

CREATE TABLE IF NOT EXISTS hubspot_manychat_audit (
    id BIGSERIAL PRIMARY KEY,
    execution_id VARCHAR(255),
    contact_id VARCHAR(128),
    contact_name VARCHAR(256),
    manychat_user_id VARCHAR(128),
    interes_producto VARCHAR(256),
    message_hash BIGINT,
    message_length INT,
    status VARCHAR(32) NOT NULL CHECK (status IN ('sent', 'error', 'skipped')),
    skip_reason VARCHAR(128),
    http_status_code INT,
    is_rate_limited BOOLEAN DEFAULT FALSE,
    duration_ms NUMERIC(10,2),
    manychat_response JSONB,
    error_details JSONB,
    parse_duration_ms NUMERIC(10,2),
    prepared_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para queries comunes
CREATE INDEX IF NOT EXISTS idx_hubspot_manychat_audit_contact_id ON hubspot_manychat_audit(contact_id);
CREATE INDEX IF NOT EXISTS idx_hubspot_manychat_audit_status ON hubspot_manychat_audit(status);
CREATE INDEX IF NOT EXISTS idx_hubspot_manychat_audit_sent_at ON hubspot_manychat_audit(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_hubspot_manychat_audit_message_hash ON hubspot_manychat_audit(message_hash);
CREATE INDEX IF NOT EXISTS idx_hubspot_manychat_audit_execution_id ON hubspot_manychat_audit(execution_id);
CREATE INDEX IF NOT EXISTS idx_hubspot_manychat_audit_manychat_user_id ON hubspot_manychat_audit(manychat_user_id);
CREATE INDEX IF NOT EXISTS idx_hubspot_manychat_audit_created_at ON hubspot_manychat_audit(created_at DESC);

-- Vista materializada para estadísticas diarias (opcional, para análisis rápido)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hubspot_manychat_daily_stats AS
SELECT 
    DATE(sent_at) as date,
    COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE status = 'sent') as sent_count,
    COUNT(*) FILTER (WHERE status = 'error') as error_count,
    COUNT(*) FILTER (WHERE status = 'skipped') as skipped_count,
    COUNT(*) FILTER (WHERE is_rate_limited = true) as rate_limited_count,
    AVG(duration_ms) as avg_duration_ms,
    AVG(parse_duration_ms) as avg_parse_duration_ms,
    AVG(message_length) as avg_message_length,
    COUNT(DISTINCT contact_id) as unique_contacts,
    COUNT(DISTINCT manychat_user_id) as unique_manychat_users,
    COUNT(DISTINCT interes_producto) as unique_products
FROM hubspot_manychat_audit
GROUP BY DATE(sent_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_hubspot_manychat_daily_stats_date 
    ON mv_hubspot_manychat_daily_stats(date DESC);

-- Comentarios en la tabla
COMMENT ON TABLE hubspot_manychat_audit IS 'Auditoría de mensajes enviados desde HubSpot a ManyChat';
COMMENT ON COLUMN hubspot_manychat_audit.execution_id IS 'ID de ejecución de Kestra';
COMMENT ON COLUMN hubspot_manychat_audit.message_hash IS 'Hash del mensaje para deduplicación';
COMMENT ON COLUMN hubspot_manychat_audit.manychat_response IS 'Respuesta completa de ManyChat API (JSON)';
COMMENT ON COLUMN hubspot_manychat_audit.error_details IS 'Detalles de error si el envío falló (JSON)';



