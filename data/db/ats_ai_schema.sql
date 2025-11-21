-- ============================================================================
-- Schema para Funcionalidades de IA y Avanzadas
-- ============================================================================

-- Tabla de talent pools
CREATE TABLE IF NOT EXISTS ats_talent_pools (
    id SERIAL PRIMARY KEY,
    pool_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    pool_name VARCHAR(255) NOT NULL,
    tags TEXT[],
    added_at TIMESTAMPTZ DEFAULT NOW(),
    added_by VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de embeddings de candidatos (para búsqueda semántica)
CREATE TABLE IF NOT EXISTS ats_candidate_embeddings (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(255) NOT NULL,
    embedding_model VARCHAR(128) NOT NULL, -- 'openai', 'cohere', 'custom'
    embedding_vector REAL[], -- Vector de embeddings
    text_source TEXT, -- Texto del cual se generó el embedding
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    UNIQUE(candidate_id, embedding_model)
);

-- Tabla de calibración de entrevistas
CREATE TABLE IF NOT EXISTS ats_interview_calibration (
    id SERIAL PRIMARY KEY,
    calibration_id VARCHAR(255) UNIQUE NOT NULL,
    interview_id VARCHAR(255) NOT NULL,
    reviewer_count INTEGER NOT NULL,
    original_ratings JSONB NOT NULL,
    calibrated_rating DECIMAL(5, 2),
    std_deviation DECIMAL(5, 2),
    bias_detected BOOLEAN DEFAULT FALSE,
    bias_details JSONB,
    consensus_level VARCHAR(64), -- 'high', 'medium', 'low'
    calibrated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (interview_id) REFERENCES ats_interviews(interview_id) ON DELETE CASCADE
);

-- Tabla de métricas de diversidad
CREATE TABLE IF NOT EXISTS ats_diversity_metrics (
    id SERIAL PRIMARY KEY,
    metric_id VARCHAR(255) UNIQUE NOT NULL,
    job_id VARCHAR(255),
    metric_period VARCHAR(64), -- 'daily', 'weekly', 'monthly', 'quarterly'
    gender_distribution JSONB,
    location_distribution JSONB,
    age_distribution JSONB,
    ethnicity_distribution JSONB,
    representation_by_stage JSONB, -- Representación en cada etapa del proceso
    hiring_rate_by_group JSONB,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de benchmarks de salarios
CREATE TABLE IF NOT EXISTS ats_salary_benchmarks (
    id SERIAL PRIMARY KEY,
    benchmark_id VARCHAR(255) UNIQUE NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    experience_years INTEGER,
    benchmark_source VARCHAR(128), -- 'payscale', 'glassdoor', 'salary_com', 'internal'
    salary_min DECIMAL(12, 2),
    salary_max DECIMAL(12, 2),
    salary_median DECIMAL(12, 2),
    salary_mean DECIMAL(12, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    benchmark_data JSONB,
    benchmarked_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de calidad de hire
CREATE TABLE IF NOT EXISTS ats_quality_of_hire (
    id SERIAL PRIMARY KEY,
    quality_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    hire_date DATE NOT NULL,
    predicted_quality_score DECIMAL(5, 2),
    actual_quality_score DECIMAL(5, 2), -- Score post-hire (después de 90 días)
    quality_level VARCHAR(64), -- 'high', 'medium', 'low'
    evaluation_period INTEGER DEFAULT 90, -- Días desde hire
    performance_metrics JSONB, -- Métricas de performance post-hire
    retention_metrics JSONB, -- Métricas de retención
    feedback_metrics JSONB, -- Feedback de manager/equipo
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de video entrevistas
CREATE TABLE IF NOT EXISTS ats_video_interviews (
    id SERIAL PRIMARY KEY,
    video_interview_id VARCHAR(255) UNIQUE NOT NULL,
    interview_id VARCHAR(255) NOT NULL,
    platform VARCHAR(128) NOT NULL, -- 'zoom', 'teams', 'hiringvue', 'sparkhire'
    platform_interview_id VARCHAR(255),
    recording_url TEXT,
    transcription TEXT,
    analysis JSONB, -- Análisis de video (sentimiento, keywords, etc.)
    duration_seconds INTEGER,
    status VARCHAR(64) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'failed'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (interview_id) REFERENCES ats_interviews(interview_id) ON DELETE CASCADE
);

-- Tabla de integración con L&D (Learning & Development)
CREATE TABLE IF NOT EXISTS ats_learning_integration (
    id SERIAL PRIMARY KEY,
    integration_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    learning_platform VARCHAR(128) NOT NULL, -- 'coursera', 'udemy', 'linkedin_learning', 'internal'
    learning_path_id VARCHAR(255),
    courses_assigned JSONB,
    courses_completed JSONB,
    completion_percentage DECIMAL(5, 2),
    certification_urls TEXT[],
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_ats_talent_pools_candidate_id ON ats_talent_pools(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_talent_pools_pool_name ON ats_talent_pools(pool_name);
CREATE INDEX IF NOT EXISTS idx_ats_candidate_embeddings_candidate_id ON ats_candidate_embeddings(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_interview_calibration_interview_id ON ats_interview_calibration(interview_id);
CREATE INDEX IF NOT EXISTS idx_ats_diversity_metrics_job_id ON ats_diversity_metrics(job_id);
CREATE INDEX IF NOT EXISTS idx_ats_salary_benchmarks_job_title ON ats_salary_benchmarks(job_title, location);
CREATE INDEX IF NOT EXISTS idx_ats_quality_of_hire_candidate_id ON ats_quality_of_hire(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_quality_of_hire_quality_level ON ats_quality_of_hire(quality_level);
CREATE INDEX IF NOT EXISTS idx_ats_video_interviews_interview_id ON ats_video_interviews(interview_id);
CREATE INDEX IF NOT EXISTS idx_ats_video_interviews_platform ON ats_video_interviews(platform);
CREATE INDEX IF NOT EXISTS idx_ats_learning_integration_candidate_id ON ats_learning_integration(candidate_id);

-- Vista para talent pools con estadísticas
CREATE OR REPLACE VIEW ats_talent_pools_stats AS
SELECT 
    tp.pool_name,
    COUNT(DISTINCT tp.candidate_id) as total_candidates,
    COUNT(DISTINCT a.application_id) as active_applications,
    COUNT(DISTINCT CASE WHEN a.status = 'hired' THEN a.application_id END) as hired_count,
    AVG(ml.overall_score) as avg_ml_score,
    array_agg(DISTINCT tp.tags) as all_tags
FROM ats_talent_pools tp
LEFT JOIN ats_candidates c ON tp.candidate_id = c.candidate_id
LEFT JOIN ats_applications a ON c.candidate_id = a.candidate_id
LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
GROUP BY tp.pool_name;

