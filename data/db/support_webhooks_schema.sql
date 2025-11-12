-- ============================================================================
-- SCHEMA: Sistema de Webhooks para Troubleshooting
-- ============================================================================

BEGIN;

-- ============================================================================
-- Tabla de Webhooks
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_webhooks (
    id SERIAL PRIMARY KEY,
    webhook_id VARCHAR(128) UNIQUE NOT NULL,
    url VARCHAR(512) NOT NULL,
    events TEXT[] NOT NULL, -- Array de eventos que escucha
    secret VARCHAR(256), -- Secret para firma HMAC
    headers JSONB DEFAULT '{}'::jsonb,
    timeout INTEGER DEFAULT 10,
    retry_attempts INTEGER DEFAULT 3,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_support_webhooks_webhook_id 
    ON support_webhooks(webhook_id);
CREATE INDEX IF NOT EXISTS idx_support_webhooks_enabled 
    ON support_webhooks(enabled);

-- ============================================================================
-- Tabla de Historial de Webhooks
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_webhook_events (
    id SERIAL PRIMARY KEY,
    webhook_id VARCHAR(128) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    triggered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_webhook FOREIGN KEY (webhook_id) 
        REFERENCES support_webhooks(webhook_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_webhook_events_webhook_id 
    ON support_webhook_events(webhook_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_event_type 
    ON support_webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_events_triggered_at 
    ON support_webhook_events(triggered_at);

-- ============================================================================
-- Vista de Estadísticas de Webhooks
-- ============================================================================
CREATE OR REPLACE VIEW vw_webhook_stats AS
SELECT 
    w.webhook_id,
    w.url,
    w.enabled,
    COUNT(e.id) as total_events,
    COUNT(CASE WHEN e.success = true THEN 1 END) as successful_events,
    COUNT(CASE WHEN e.success = false THEN 1 END) as failed_events,
    ROUND(
        COUNT(CASE WHEN e.success = true THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(e.id), 0)::NUMERIC * 100, 
        2
    ) as success_rate,
    MAX(e.triggered_at) as last_triggered_at
FROM support_webhooks w
LEFT JOIN support_webhook_events e ON w.webhook_id = e.webhook_id
GROUP BY w.webhook_id, w.url, w.enabled;

COMMIT;

COMMENT ON TABLE support_webhooks IS 
    'Webhooks registrados para eventos de troubleshooting';
COMMENT ON TABLE support_webhook_events IS 
    'Historial de eventos de webhooks disparados';
COMMENT ON VIEW vw_webhook_stats IS 
    'Estadísticas de webhooks con tasas de éxito';



