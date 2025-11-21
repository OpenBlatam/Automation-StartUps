-- Schema para versionado y auditoría de documentos
-- ==================================================

-- Tabla de versiones de documentos
CREATE TABLE IF NOT EXISTS document_versions (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(128) NOT NULL,
    version INTEGER NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    extracted_text TEXT,
    extracted_fields JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(256),
    changes JSONB,
    UNIQUE(document_id, version)
);

-- Tabla de auditoría
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(128),
    action VARCHAR(64) NOT NULL,
    user_id VARCHAR(256),
    user_email VARCHAR(256),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    result VARCHAR(32) NOT NULL,
    error_message TEXT
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_doc_versions_doc_id ON document_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_versions_version ON document_versions(document_id, version DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_doc_id ON audit_logs(document_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id, user_email);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_result ON audit_logs(result);

-- Vista para última versión de cada documento
CREATE OR REPLACE VIEW latest_document_versions AS
SELECT DISTINCT ON (document_id)
    document_id,
    version,
    file_hash,
    extracted_text,
    extracted_fields,
    metadata,
    created_at,
    created_by
FROM document_versions
ORDER BY document_id, version DESC;

-- Vista para actividad reciente
CREATE OR REPLACE VIEW recent_audit_activity AS
SELECT 
    DATE_TRUNC('hour', timestamp) AS hour,
    action,
    COUNT(*) AS action_count,
    COUNT(*) FILTER (WHERE result = 'success') AS success_count,
    COUNT(DISTINCT document_id) AS unique_documents
FROM audit_logs
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', timestamp), action
ORDER BY hour DESC, action_count DESC;

-- Función para obtener cambios entre versiones
CREATE OR REPLACE FUNCTION get_version_changes(
    p_document_id VARCHAR,
    p_version1 INTEGER,
    p_version2 INTEGER
)
RETURNS TABLE (
    field_name TEXT,
    old_value TEXT,
    new_value TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        key::TEXT,
        v1.value::TEXT,
        v2.value::TEXT
    FROM 
        (SELECT * FROM jsonb_each(
            (SELECT extracted_fields FROM document_versions 
             WHERE document_id = p_document_id AND version = p_version1)
        )) v1
    FULL OUTER JOIN
        (SELECT * FROM jsonb_each(
            (SELECT extracted_fields FROM document_versions 
             WHERE document_id = p_document_id AND version = p_version2)
        )) v2 ON v1.key = v2.key
    WHERE v1.value IS DISTINCT FROM v2.value;
END;
$$ LANGUAGE plpgsql;

-- Comentarios
COMMENT ON TABLE document_versions IS 'Versiones históricas de documentos procesados';
COMMENT ON TABLE audit_logs IS 'Log de auditoría de todas las acciones';
COMMENT ON VIEW latest_document_versions IS 'Última versión de cada documento';
COMMENT ON VIEW recent_audit_activity IS 'Actividad reciente de auditoría';

