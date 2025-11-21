-- Schema para templates de descripciones de puesto por industria

CREATE TABLE IF NOT EXISTS job_description_templates (
    template_id SERIAL PRIMARY KEY,
    industry VARCHAR(100) NOT NULL, -- 'fintech', 'healthcare', 'ecommerce', 'saas', 'consulting', 'startup'
    role VARCHAR(255) NOT NULL,
    level VARCHAR(50),
    template_data JSONB NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(industry, role, level)
);

CREATE INDEX IF NOT EXISTS idx_templates_industry ON job_description_templates(industry);
CREATE INDEX IF NOT EXISTS idx_templates_role ON job_description_templates(role);
CREATE INDEX IF NOT EXISTS idx_templates_level ON job_description_templates(level);

-- Función para actualizar updated_at
CREATE TRIGGER update_templates_updated_at 
    BEFORE UPDATE ON job_description_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Vista de templates más usados
CREATE OR REPLACE VIEW popular_templates AS
SELECT 
    industry,
    role,
    level,
    usage_count,
    created_at,
    updated_at
FROM job_description_templates
ORDER BY usage_count DESC, updated_at DESC;






