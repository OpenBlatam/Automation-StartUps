-- Schema para colaboración y reglas de negocio
-- ==============================================

-- Tabla de revisiones de documentos
CREATE TABLE IF NOT EXISTS document_reviews (
    id SERIAL PRIMARY KEY,
    review_id VARCHAR(128) UNIQUE NOT NULL,
    document_id VARCHAR(128) NOT NULL REFERENCES processed_documents(document_id) ON DELETE CASCADE,
    reviewer_id VARCHAR(256) NOT NULL,
    reviewer_email VARCHAR(256),
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Tabla de comentarios en revisiones
CREATE TABLE IF NOT EXISTS review_comments (
    id SERIAL PRIMARY KEY,
    comment_id VARCHAR(128) UNIQUE NOT NULL,
    review_id VARCHAR(128) NOT NULL REFERENCES document_reviews(review_id) ON DELETE CASCADE,
    document_id VARCHAR(128) NOT NULL,
    user_id VARCHAR(256) NOT NULL,
    user_email VARCHAR(256),
    text TEXT NOT NULL,
    page_number INTEGER,
    coordinates JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(256)
);

-- Tabla de reglas de negocio
CREATE TABLE IF NOT EXISTS business_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(128) UNIQUE NOT NULL,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    conditions JSONB NOT NULL,
    action VARCHAR(64) NOT NULL,
    action_params JSONB,
    priority INTEGER DEFAULT 5,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ejecución de reglas
CREATE TABLE IF NOT EXISTS rule_executions (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(128) REFERENCES business_rules(rule_id),
    document_id VARCHAR(128) REFERENCES processed_documents(document_id),
    matched BOOLEAN NOT NULL,
    action_executed VARCHAR(64),
    execution_result JSONB,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_reviews_doc_id ON document_reviews(document_id);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON document_reviews(status);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON document_reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_comments_review_id ON review_comments(review_id);
CREATE INDEX IF NOT EXISTS idx_comments_doc_id ON review_comments(document_id);
CREATE INDEX IF NOT EXISTS idx_comments_resolved ON review_comments(resolved);
CREATE INDEX IF NOT EXISTS idx_business_rules_enabled ON business_rules(enabled);
CREATE INDEX IF NOT EXISTS idx_business_rules_priority ON business_rules(priority DESC);
CREATE INDEX IF NOT EXISTS idx_rule_executions_doc_id ON rule_executions(document_id);
CREATE INDEX IF NOT EXISTS idx_rule_executions_rule_id ON rule_executions(rule_id);

-- Triggers
CREATE TRIGGER update_reviews_updated_at 
    BEFORE UPDATE ON document_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_business_rules_updated_at 
    BEFORE UPDATE ON business_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vistas
CREATE OR REPLACE VIEW pending_reviews AS
SELECT 
    dr.*,
    pd.original_filename,
    pd.document_type
FROM document_reviews dr
JOIN processed_documents pd ON dr.document_id = pd.document_id
WHERE dr.status = 'pending'
ORDER BY dr.created_at ASC;

CREATE OR REPLACE VIEW review_statistics AS
SELECT 
    reviewer_id,
    COUNT(*) as total_reviews,
    COUNT(*) FILTER (WHERE status = 'approved') as approved,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 3600) as avg_hours_to_complete
FROM document_reviews
WHERE completed_at IS NOT NULL
GROUP BY reviewer_id;

