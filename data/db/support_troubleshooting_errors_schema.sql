-- ============================================================================
-- SCHEMA: Tabla de Errores para Troubleshooting
-- ============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS support_troubleshooting_errors (
    id SERIAL PRIMARY KEY,
    error_type VARCHAR(128) NOT NULL,
    error_message TEXT NOT NULL,
    severity VARCHAR(32) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    category VARCHAR(64) NOT NULL,
    session_id VARCHAR(128),
    ticket_id VARCHAR(128),
    user_id VARCHAR(256),
    stack_trace TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_session FOREIGN KEY (session_id) 
        REFERENCES support_troubleshooting_sessions(session_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_troubleshooting_errors_severity 
    ON support_troubleshooting_errors(severity);
CREATE INDEX IF NOT EXISTS idx_troubleshooting_errors_category 
    ON support_troubleshooting_errors(category);
CREATE INDEX IF NOT EXISTS idx_troubleshooting_errors_occurred_at 
    ON support_troubleshooting_errors(occurred_at);
CREATE INDEX IF NOT EXISTS idx_troubleshooting_errors_session_id 
    ON support_troubleshooting_errors(session_id);

-- Vista de errores críticos recientes
CREATE OR REPLACE VIEW vw_critical_errors AS
SELECT 
    error_type,
    error_message,
    COUNT(*) as occurrence_count,
    MAX(occurred_at) as last_occurrence,
    COUNT(DISTINCT session_id) as affected_sessions
FROM support_troubleshooting_errors
WHERE severity = 'critical'
  AND occurred_at >= NOW() - INTERVAL '24 hours'
GROUP BY error_type, error_message
ORDER BY occurrence_count DESC;

COMMIT;

COMMENT ON TABLE support_troubleshooting_errors IS 
    'Registro de errores del sistema de troubleshooting';
COMMENT ON VIEW vw_critical_errors IS 
    'Errores críticos recientes agrupados';



