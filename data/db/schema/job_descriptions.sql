-- Schema para el sistema de generación de descripciones de puesto con IA

-- Tabla de caché de descripciones
CREATE TABLE IF NOT EXISTS job_descriptions_cache (
    cache_key VARCHAR(32) PRIMARY KEY,
    description TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cache_created_at ON job_descriptions_cache(created_at);

-- Tabla de descripciones de puesto
CREATE TABLE IF NOT EXISTS job_descriptions (
    job_description_id SERIAL PRIMARY KEY,
    role VARCHAR(255) NOT NULL,
    level VARCHAR(50),
    department VARCHAR(255),
    description TEXT NOT NULL,
    required_skills JSONB,
    preferred_skills JSONB,
    location VARCHAR(255),
    salary_range VARCHAR(100),
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    tokens_used INTEGER,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_desc_role ON job_descriptions(role);
CREATE INDEX IF NOT EXISTS idx_job_desc_status ON job_descriptions(status);
CREATE INDEX IF NOT EXISTS idx_job_desc_created ON job_descriptions(created_at);

-- Tabla de publicaciones en portales
CREATE TABLE IF NOT EXISTS job_postings (
    posting_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id),
    board VARCHAR(100) NOT NULL,
    external_job_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'published',
    published_at TIMESTAMP DEFAULT NOW(),
    views_count INTEGER DEFAULT 0,
    applications_count INTEGER DEFAULT 0,
    UNIQUE(job_description_id, board)
);

CREATE INDEX IF NOT EXISTS idx_postings_job_desc ON job_postings(job_description_id);
CREATE INDEX IF NOT EXISTS idx_postings_board ON job_postings(board);
CREATE INDEX IF NOT EXISTS idx_postings_status ON job_postings(status);

-- Tabla de aplicaciones procesadas
CREATE TABLE IF NOT EXISTS job_applications (
    application_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id),
    candidate_name VARCHAR(255),
    candidate_email VARCHAR(255),
    ai_score DECIMAL(5,2),
    fit_level VARCHAR(50),
    recommendation VARCHAR(50),
    strengths JSONB,
    weaknesses JSONB,
    status VARCHAR(50) DEFAULT 'new',
    processed_at TIMESTAMP DEFAULT NOW(),
    ai_provider VARCHAR(50),
    tokens_used INTEGER
);

CREATE INDEX IF NOT EXISTS idx_applications_job_desc ON job_applications(job_description_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_score ON job_applications(ai_score);

-- Tabla de métricas
CREATE TABLE IF NOT EXISTS job_description_metrics (
    metric_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2),
    metric_data JSONB,
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_job_desc ON job_description_metrics(job_description_id);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON job_description_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_recorded ON job_description_metrics(recorded_at);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para actualizar updated_at
CREATE TRIGGER update_job_descriptions_updated_at 
    BEFORE UPDATE ON job_descriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Vista para estadísticas de descripciones
CREATE OR REPLACE VIEW job_descriptions_stats AS
SELECT 
    jd.job_description_id,
    jd.role,
    jd.status,
    jd.created_at,
    COUNT(DISTINCT jp.posting_id) as total_postings,
    COUNT(DISTINCT ja.application_id) as total_applications,
    AVG(ja.ai_score) as avg_application_score,
    COUNT(DISTINCT CASE WHEN ja.status = 'qualified' THEN ja.application_id END) as qualified_applications
FROM job_descriptions jd
LEFT JOIN job_postings jp ON jd.job_description_id = jp.job_description_id
LEFT JOIN job_applications ja ON jd.job_description_id = ja.job_description_id
GROUP BY jd.job_description_id, jd.role, jd.status, jd.created_at;






