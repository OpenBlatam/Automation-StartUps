-- ============================================================================
-- SCHEMA: Sistema de Versionado de FAQs
-- ============================================================================
-- Permite versionado de FAQs para tracking de cambios y rollback
-- ============================================================================

BEGIN;

-- ============================================================================
-- Tabla de Versiones de FAQs
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_faq_versions (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(128) NOT NULL,
    version_number INT NOT NULL,
    
    -- Contenido versionado
    title VARCHAR(512) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    category VARCHAR(64),
    tags TEXT[],
    keywords TEXT[],
    
    -- Metadata de versión
    created_by VARCHAR(128),
    change_reason TEXT,
    is_current BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Relación con artículo
    FOREIGN KEY (article_id) REFERENCES support_faq_articles(article_id) ON DELETE CASCADE,
    
    -- Una sola versión actual por artículo
    CONSTRAINT unique_current_version UNIQUE (article_id) WHERE is_current = true
);

-- ============================================================================
-- Trigger para versionado automático
-- ============================================================================
CREATE OR REPLACE FUNCTION create_faq_version()
RETURNS TRIGGER AS $$
DECLARE
    v_next_version INT;
BEGIN
    -- Obtener siguiente número de versión
    SELECT COALESCE(MAX(version_number), 0) + 1
    INTO v_next_version
    FROM support_faq_versions
    WHERE article_id = NEW.article_id;
    
    -- Marcar versión anterior como no actual
    UPDATE support_faq_versions
    SET is_current = false
    WHERE article_id = NEW.article_id
    AND is_current = true;
    
    -- Crear nueva versión
    INSERT INTO support_faq_versions (
        article_id,
        version_number,
        title,
        content,
        summary,
        category,
        tags,
        keywords,
        is_current,
        created_by
    ) VALUES (
        NEW.article_id,
        v_next_version,
        NEW.title,
        NEW.content,
        NEW.summary,
        NEW.category,
        NEW.tags,
        NEW.keywords,
        true,
        'system'
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_faq_versioning ON support_faq_articles;
CREATE TRIGGER trigger_faq_versioning
    AFTER UPDATE ON support_faq_articles
    FOR EACH ROW
    WHEN (
        OLD.title IS DISTINCT FROM NEW.title OR
        OLD.content IS DISTINCT FROM NEW.content OR
        OLD.summary IS DISTINCT FROM NEW.summary OR
        OLD.category IS DISTINCT FROM NEW.category OR
        OLD.tags IS DISTINCT FROM NEW.tags OR
        OLD.keywords IS DISTINCT FROM NEW.keywords
    )
    EXECUTE FUNCTION create_faq_version();

-- ============================================================================
-- Función: Rollback a versión anterior
-- ============================================================================
CREATE OR REPLACE FUNCTION rollback_faq_version(
    p_article_id VARCHAR(128),
    p_version_number INT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_version RECORD;
BEGIN
    -- Obtener versión específica
    SELECT * INTO v_version
    FROM support_faq_versions
    WHERE article_id = p_article_id
    AND version_number = p_version_number;
    
    IF NOT FOUND THEN
        RETURN false;
    END IF;
    
    -- Marcar versión actual como no actual
    UPDATE support_faq_versions
    SET is_current = false
    WHERE article_id = p_article_id
    AND is_current = true;
    
    -- Restaurar contenido desde versión
    UPDATE support_faq_articles
    SET 
        title = v_version.title,
        content = v_version.content,
        summary = v_version.summary,
        category = v_version.category,
        tags = v_version.tags,
        keywords = v_version.keywords,
        last_updated_at = NOW()
    WHERE article_id = p_article_id;
    
    -- Marcar versión como actual
    UPDATE support_faq_versions
    SET is_current = true
    WHERE article_id = p_article_id
    AND version_number = p_version_number;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ÍNDICES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_faq_versions_article ON support_faq_versions(article_id);
CREATE INDEX IF NOT EXISTS idx_faq_versions_current ON support_faq_versions(is_current) WHERE is_current = true;
CREATE INDEX IF NOT EXISTS idx_faq_versions_created_at ON support_faq_versions(created_at DESC);

COMMIT;

