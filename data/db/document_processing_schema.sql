-- Schema para procesamiento de documentos
-- ========================================

-- Tabla principal de documentos procesados
CREATE TABLE IF NOT EXISTS processed_documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(128) UNIQUE NOT NULL,
    original_filename VARCHAR(512) NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    document_type VARCHAR(64) NOT NULL,
    classification_confidence DECIMAL(5,4) NOT NULL,
    extracted_text TEXT,
    ocr_confidence DECIMAL(5,4),
    ocr_provider VARCHAR(64),
    archive_path TEXT,
    file_size BIGINT,
    file_extension VARCHAR(16),
    mime_type VARCHAR(128),
    keywords_matched TEXT[], -- Array de keywords
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para campos extraídos (estructura flexible)
CREATE TABLE IF NOT EXISTS document_extracted_fields (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(128) NOT NULL REFERENCES processed_documents(document_id) ON DELETE CASCADE,
    field_name VARCHAR(128) NOT NULL,
    field_value TEXT,
    field_type VARCHAR(64), -- string, number, date, etc.
    confidence DECIMAL(5,4),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, field_name)
);

-- Tabla para metadatos adicionales (JSONB para flexibilidad)
CREATE TABLE IF NOT EXISTS document_metadata (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(128) NOT NULL REFERENCES processed_documents(document_id) ON DELETE CASCADE,
    metadata_key VARCHAR(128) NOT NULL,
    metadata_value JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, metadata_key)
);

-- Tabla para tracking de procesamiento
CREATE TABLE IF NOT EXISTS document_processing_log (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(128),
    filename VARCHAR(512),
    status VARCHAR(64) NOT NULL, -- processing, completed, failed, archived
    error_message TEXT,
    processing_time_ms INTEGER,
    ocr_provider VARCHAR(64),
    steps_completed TEXT[], -- Array de pasos completados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para archivos pendientes de procesar
CREATE TABLE IF NOT EXISTS pending_documents (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    filename VARCHAR(512),
    file_size BIGINT,
    source VARCHAR(128), -- webhook, email, upload, etc.
    priority INTEGER DEFAULT 5, -- 1-10, mayor = más prioridad
    status VARCHAR(64) DEFAULT 'pending', -- pending, processing, failed
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Tabla para reglas de archivado automático
CREATE TABLE IF NOT EXISTS archive_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(128) UNIQUE NOT NULL,
    document_type VARCHAR(64) NOT NULL,
    conditions JSONB, -- Condiciones para aplicar la regla
    target_path_template TEXT, -- Template para ruta de destino
    enabled BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para integraciones con Zapier/Make
CREATE TABLE IF NOT EXISTS document_webhooks (
    id SERIAL PRIMARY KEY,
    webhook_name VARCHAR(128) UNIQUE NOT NULL,
    webhook_url TEXT NOT NULL,
    trigger_events TEXT[] NOT NULL, -- ['document_processed', 'document_classified', etc.]
    document_types TEXT[], -- Tipos de documentos que activan el webhook
    enabled BOOLEAN DEFAULT true,
    secret_token VARCHAR(256), -- Para autenticación
    headers JSONB, -- Headers adicionales
    retry_count INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para logs de webhooks enviados
CREATE TABLE IF NOT EXISTS webhook_logs (
    id SERIAL PRIMARY KEY,
    webhook_id INTEGER REFERENCES document_webhooks(id) ON DELETE SET NULL,
    document_id VARCHAR(128) REFERENCES processed_documents(document_id) ON DELETE SET NULL,
    event_type VARCHAR(64) NOT NULL,
    status VARCHAR(64) NOT NULL, -- sent, failed, retrying
    response_code INTEGER,
    response_body TEXT,
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_processed_docs_document_id ON processed_documents(document_id);
CREATE INDEX IF NOT EXISTS idx_processed_docs_type ON processed_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_processed_docs_hash ON processed_documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_processed_docs_processed_at ON processed_documents(processed_at);
CREATE INDEX IF NOT EXISTS idx_extracted_fields_doc_id ON document_extracted_fields(document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_fields_name ON document_extracted_fields(field_name);
CREATE INDEX IF NOT EXISTS idx_metadata_doc_id ON document_metadata(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_log_status ON document_processing_log(status);
CREATE INDEX IF NOT EXISTS idx_processing_log_doc_id ON document_processing_log(document_id);
CREATE INDEX IF NOT EXISTS idx_pending_docs_status ON pending_documents(status);
CREATE INDEX IF NOT EXISTS idx_pending_docs_scheduled ON pending_documents(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook_id ON webhook_logs(webhook_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_doc_id ON webhook_logs(document_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_status ON webhook_logs(status);

-- Vista para documentos por tipo
CREATE OR REPLACE VIEW documents_by_type AS
SELECT 
    document_type,
    COUNT(*) AS total_documents,
    AVG(classification_confidence) AS avg_confidence,
    AVG(ocr_confidence) AS avg_ocr_confidence,
    SUM(file_size) AS total_size_bytes,
    MIN(processed_at) AS first_processed,
    MAX(processed_at) AS last_processed
FROM processed_documents
GROUP BY document_type;

-- Vista para estadísticas de procesamiento
CREATE OR REPLACE VIEW processing_stats AS
SELECT 
    DATE_TRUNC('day', processed_at) AS processing_date,
    COUNT(*) AS documents_processed,
    COUNT(DISTINCT document_type) AS unique_types,
    AVG(classification_confidence) AS avg_classification_confidence,
    AVG(ocr_confidence) AS avg_ocr_confidence,
    COUNT(DISTINCT ocr_provider) AS providers_used
FROM processed_documents
GROUP BY DATE_TRUNC('day', processed_at)
ORDER BY processing_date DESC;

-- Vista para documentos recientes con campos extraídos
CREATE OR REPLACE VIEW recent_documents_with_fields AS
SELECT 
    pd.document_id,
    pd.original_filename,
    pd.document_type,
    pd.classification_confidence,
    pd.processed_at,
    pd.archive_path,
    jsonb_object_agg(def.field_name, def.field_value) AS extracted_fields
FROM processed_documents pd
LEFT JOIN document_extracted_fields def ON pd.document_id = def.document_id
WHERE pd.processed_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY pd.document_id, pd.original_filename, pd.document_type, 
         pd.classification_confidence, pd.processed_at, pd.archive_path
ORDER BY pd.processed_at DESC;

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_processed_documents_updated_at 
    BEFORE UPDATE ON processed_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archive_rules_updated_at 
    BEFORE UPDATE ON archive_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_webhooks_updated_at 
    BEFORE UPDATE ON document_webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para buscar documentos por campo extraído
CREATE OR REPLACE FUNCTION search_documents_by_field(
    p_field_name VARCHAR,
    p_field_value TEXT DEFAULT NULL,
    p_document_type VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    document_id VARCHAR,
    original_filename VARCHAR,
    document_type VARCHAR,
    field_value TEXT,
    processed_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pd.document_id,
        pd.original_filename,
        pd.document_type,
        def.field_value,
        pd.processed_at
    FROM processed_documents pd
    JOIN document_extracted_fields def ON pd.document_id = def.document_id
    WHERE def.field_name = p_field_name
        AND (p_field_value IS NULL OR def.field_value ILIKE '%' || p_field_value || '%')
        AND (p_document_type IS NULL OR pd.document_type = p_document_type)
    ORDER BY pd.processed_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Comentarios
COMMENT ON TABLE processed_documents IS 'Documentos procesados con OCR y clasificación';
COMMENT ON TABLE document_extracted_fields IS 'Campos extraídos de documentos procesados';
COMMENT ON TABLE document_metadata IS 'Metadatos adicionales de documentos';
COMMENT ON TABLE document_processing_log IS 'Log de procesamiento de documentos';
COMMENT ON TABLE pending_documents IS 'Documentos pendientes de procesar';
COMMENT ON TABLE archive_rules IS 'Reglas de archivado automático';
COMMENT ON TABLE document_webhooks IS 'Configuración de webhooks para integraciones';
COMMENT ON TABLE webhook_logs IS 'Log de webhooks enviados';

