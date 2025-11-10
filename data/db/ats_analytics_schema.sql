-- ============================================================================
-- Schema de Analytics Avanzado para ATS
-- ============================================================================

-- Tabla de forecasting de hiring
CREATE TABLE IF NOT EXISTS ats_hiring_forecasts (
    id SERIAL PRIMARY KEY,
    forecast_id VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(255),
    forecast_period_months INTEGER NOT NULL,
    forecasts JSONB NOT NULL, -- Forecasts por departamento/rol
    confidence_level DECIMAL(5, 2), -- 0-100
    forecast_method VARCHAR(128), -- 'historical', 'ml', 'combined'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de ROI de hiring
CREATE TABLE IF NOT EXISTS ats_hiring_roi (
    id SERIAL PRIMARY KEY,
    roi_id VARCHAR(255) UNIQUE NOT NULL,
    job_id VARCHAR(255),
    department VARCHAR(255),
    period_days INTEGER NOT NULL,
    total_costs DECIMAL(12, 2) NOT NULL,
    total_value DECIMAL(12, 2) NOT NULL,
    roi_percentage DECIMAL(10, 2),
    cost_per_hire DECIMAL(12, 2),
    hires_count INTEGER,
    metrics JSONB,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de engagement de candidatos
CREATE TABLE IF NOT EXISTS ats_candidate_engagement (
    id SERIAL PRIMARY KEY,
    engagement_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL UNIQUE,
    overall_score DECIMAL(5, 2),
    email_engagement DECIMAL(5, 2),
    response_score DECIMAL(5, 2),
    interview_score DECIMAL(5, 2),
    test_score DECIMAL(5, 2),
    chatbot_score DECIMAL(5, 2),
    metrics JSONB,
    engagement_level VARCHAR(64), -- 'high', 'medium', 'low'
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de análisis de cohortes
CREATE TABLE IF NOT EXISTS ats_cohort_analysis (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(255) UNIQUE NOT NULL,
    cohort_period VARCHAR(64) NOT NULL, -- 'monthly', 'quarterly'
    cohort_data JSONB NOT NULL,
    start_date DATE,
    end_date DATE,
    total_cohorts INTEGER,
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de calidad de fuente
CREATE TABLE IF NOT EXISTS ats_source_quality (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(255) UNIQUE NOT NULL,
    source_metrics JSONB NOT NULL, -- Métricas por fuente
    best_source VARCHAR(128),
    worst_source VARCHAR(128),
    recommendations TEXT[],
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de predicción de demanda de talento
CREATE TABLE IF NOT EXISTS ats_talent_demand_forecast (
    id SERIAL PRIMARY KEY,
    forecast_id VARCHAR(255) UNIQUE NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    forecast_period_months INTEGER NOT NULL,
    predicted_demand INTEGER,
    current_supply INTEGER,
    supply_gap INTEGER,
    market_trends JSONB,
    recommendations TEXT[],
    forecasted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de análisis de costo-beneficio
CREATE TABLE IF NOT EXISTS ats_cost_benefit_analysis (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(255) UNIQUE NOT NULL,
    job_id VARCHAR(255),
    department VARCHAR(255),
    hiring_costs DECIMAL(12, 2),
    training_costs DECIMAL(12, 2),
    onboarding_costs DECIMAL(12, 2),
    total_costs DECIMAL(12, 2),
    productivity_gain DECIMAL(12, 2),
    quality_gain DECIMAL(12, 2),
    retention_gain DECIMAL(12, 2),
    total_benefits DECIMAL(12, 2),
    net_benefit DECIMAL(12, 2),
    benefit_cost_ratio DECIMAL(10, 2),
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_ats_hiring_forecasts_department ON ats_hiring_forecasts(department);
CREATE INDEX IF NOT EXISTS idx_ats_hiring_roi_job_id ON ats_hiring_roi(job_id);
CREATE INDEX IF NOT EXISTS idx_ats_hiring_roi_roi_percentage ON ats_hiring_roi(roi_percentage DESC);
CREATE INDEX IF NOT EXISTS idx_ats_candidate_engagement_application_id ON ats_candidate_engagement(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_candidate_engagement_overall_score ON ats_candidate_engagement(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_ats_source_quality_calculated_at ON ats_source_quality(calculated_at DESC);

-- Vista para ROI por departamento
CREATE OR REPLACE VIEW ats_roi_by_department AS
SELECT 
    department,
    COUNT(DISTINCT roi_id) as analyses_count,
    AVG(roi_percentage) as avg_roi,
    AVG(cost_per_hire) as avg_cost_per_hire,
    SUM(total_costs) as total_costs,
    SUM(total_value) as total_value,
    SUM(hires_count) as total_hires
FROM ats_hiring_roi
WHERE department IS NOT NULL
GROUP BY department
ORDER BY avg_roi DESC;

-- Vista para engagement por fuente
CREATE OR REPLACE VIEW ats_engagement_by_source AS
SELECT 
    c.source,
    COUNT(DISTINCT e.application_id) as total_applications,
    AVG(e.overall_score) as avg_engagement,
    COUNT(DISTINCT e.application_id) FILTER (WHERE e.engagement_level = 'high') as high_engagement,
    COUNT(DISTINCT e.application_id) FILTER (WHERE e.engagement_level = 'medium') as medium_engagement,
    COUNT(DISTINCT e.application_id) FILTER (WHERE e.engagement_level = 'low') as low_engagement
FROM ats_candidate_engagement e
JOIN ats_applications a ON e.application_id = a.application_id
JOIN ats_candidates c ON a.candidate_id = c.candidate_id
WHERE c.source IS NOT NULL
GROUP BY c.source
ORDER BY avg_engagement DESC;

