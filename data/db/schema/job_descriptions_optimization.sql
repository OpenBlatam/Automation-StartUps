-- Schema adicional para optimización y A/B testing de descripciones de puesto

-- Tabla de variantes para A/B testing
CREATE TABLE IF NOT EXISTS job_description_variants (
    variant_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id) ON DELETE CASCADE,
    variant_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    approach VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_description_id, variant_number)
);

CREATE INDEX IF NOT EXISTS idx_variants_job_desc ON job_description_variants(job_description_id);
CREATE INDEX IF NOT EXISTS idx_variants_number ON job_description_variants(variant_number);

-- Tabla de análisis (sentimiento, keywords, etc.)
CREATE TABLE IF NOT EXISTS job_description_analytics (
    analytics_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id) ON DELETE CASCADE,
    analysis_type VARCHAR(100) NOT NULL, -- 'sentiment', 'keywords', 'performance_comparison', 'optimization'
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_description_id, analysis_type)
);

CREATE INDEX IF NOT EXISTS idx_analytics_job_desc ON job_description_analytics(job_description_id);
CREATE INDEX IF NOT EXISTS idx_analytics_type ON job_description_analytics(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created ON job_description_analytics(created_at);

-- Agregar variant_id a job_postings para tracking
ALTER TABLE job_postings 
ADD COLUMN IF NOT EXISTS variant_id INTEGER REFERENCES job_description_variants(variant_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_postings_variant ON job_postings(variant_id);

-- Agregar posting_id a job_applications para tracking por variante
ALTER TABLE job_applications
ADD COLUMN IF NOT EXISTS posting_id INTEGER REFERENCES job_postings(posting_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_applications_posting ON job_applications(posting_id);

-- Vista para performance de variantes
CREATE OR REPLACE VIEW variant_performance AS
SELECT 
    v.variant_id,
    v.job_description_id,
    v.variant_number,
    v.approach,
    COUNT(DISTINCT jp.posting_id) as total_postings,
    COUNT(DISTINCT ja.application_id) as total_applications,
    AVG(ja.ai_score) as avg_application_score,
    COUNT(DISTINCT CASE WHEN ja.status = 'qualified' THEN ja.application_id END) as qualified_applications,
    COUNT(DISTINCT CASE WHEN ja.status = 'qualified' THEN ja.application_id END)::FLOAT / 
        NULLIF(COUNT(DISTINCT ja.application_id), 0) * 100 as conversion_rate,
    MAX(jp.published_at) as last_published_at
FROM job_description_variants v
LEFT JOIN job_postings jp ON v.variant_id = jp.variant_id
LEFT JOIN job_applications ja ON jp.posting_id = ja.posting_id
GROUP BY v.variant_id, v.job_description_id, v.variant_number, v.approach;

-- Vista para analytics consolidado
CREATE OR REPLACE VIEW job_description_analytics_consolidated AS
SELECT 
    jd.job_description_id,
    jd.role,
    jd.status,
    jd.created_at,
    -- Sentiment
    (SELECT analysis_data->>'score' FROM job_description_analytics 
     WHERE job_description_id = jd.job_description_id AND analysis_type = 'sentiment')::FLOAT as sentiment_score,
    (SELECT analysis_data->>'category' FROM job_description_analytics 
     WHERE job_description_id = jd.job_description_id AND analysis_type = 'sentiment') as sentiment_category,
    -- Keywords count
    (SELECT jsonb_array_length(analysis_data) FROM job_description_analytics 
     WHERE job_description_id = jd.job_description_id AND analysis_type = 'keywords') as keywords_count,
    -- Performance
    COUNT(DISTINCT jp.posting_id) as total_postings,
    COUNT(DISTINCT ja.application_id) as total_applications,
    AVG(ja.ai_score) as avg_application_score,
    COUNT(DISTINCT CASE WHEN ja.status = 'qualified' THEN ja.application_id END) as qualified_applications
FROM job_descriptions jd
LEFT JOIN job_postings jp ON jd.job_description_id = jp.job_description_id
LEFT JOIN job_applications ja ON jp.posting_id = ja.posting_id
GROUP BY jd.job_description_id, jd.role, jd.status, jd.created_at;






