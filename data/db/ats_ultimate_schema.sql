-- ============================================================================
-- Schema Ultimate para ATS - Funcionalidades Finales
-- ============================================================================

-- Tabla de candidate experience
CREATE TABLE IF NOT EXISTS ats_candidate_experience (
    id SERIAL PRIMARY KEY,
    experience_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL UNIQUE,
    overall_score DECIMAL(5, 2),
    response_time_score DECIMAL(5, 2),
    communication_score DECIMAL(5, 2),
    stability_score DECIMAL(5, 2),
    transparency_score DECIMAL(5, 2),
    factors JSONB,
    feedback_collected BOOLEAN DEFAULT FALSE,
    feedback_text TEXT,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de market intelligence
CREATE TABLE IF NOT EXISTS ats_market_intelligence (
    id SERIAL PRIMARY KEY,
    intelligence_id VARCHAR(255) UNIQUE NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    competition_data JSONB,
    talent_availability JSONB,
    trends JSONB,
    market_score DECIMAL(5, 2),
    recommendations TEXT[],
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de employer reputation
CREATE TABLE IF NOT EXISTS ats_employer_reputation (
    id SERIAL PRIMARY KEY,
    reputation_id VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    overall_rating DECIMAL(3, 2),
    glassdoor_rating DECIMAL(3, 2),
    indeed_rating DECIMAL(3, 2),
    linkedin_rating DECIMAL(3, 2),
    social_sentiment_score DECIMAL(5, 2),
    trend VARCHAR(64), -- 'improving', 'stable', 'declining'
    review_count INTEGER DEFAULT 0,
    positive_mentions INTEGER DEFAULT 0,
    negative_mentions INTEGER DEFAULT 0,
    reputation_data JSONB,
    recommendations TEXT[],
    monitored_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de retención predictiva
CREATE TABLE IF NOT EXISTS ats_retention_predictions (
    id SERIAL PRIMARY KEY,
    prediction_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    risk_score DECIMAL(5, 2),
    risk_level VARCHAR(64), -- 'low', 'medium', 'high'
    risk_factors JSONB,
    recommendations TEXT[],
    predicted_at TIMESTAMPTZ DEFAULT NOW(),
    actual_retention_days INTEGER, -- Actualizado después de que el empleado se vaya
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de reportes avanzados
CREATE TABLE IF NOT EXISTS ats_advanced_reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(255) UNIQUE NOT NULL,
    report_name VARCHAR(255) NOT NULL,
    report_type VARCHAR(128) NOT NULL, -- 'hiring_funnel', 'source_performance', 'time_to_hire', 'diversity', 'cost_per_hire'
    report_period VARCHAR(64), -- 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    job_id VARCHAR(255),
    department VARCHAR(255),
    report_data JSONB NOT NULL,
    charts JSONB, -- Datos para gráficos
    insights TEXT[],
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    generated_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de dashboards personalizados
CREATE TABLE IF NOT EXISTS ats_custom_dashboards (
    id SERIAL PRIMARY KEY,
    dashboard_id VARCHAR(255) UNIQUE NOT NULL,
    dashboard_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    widgets JSONB NOT NULL, -- Array de widgets configurados
    layout JSONB, -- Layout del dashboard
    filters JSONB, -- Filtros aplicados
    is_shared BOOLEAN DEFAULT FALSE,
    shared_with TEXT[], -- Lista de emails con acceso
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de alertas de mercado
CREATE TABLE IF NOT EXISTS ats_market_alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(255) UNIQUE NOT NULL,
    alert_type VARCHAR(128) NOT NULL, -- 'competition_change', 'salary_change', 'talent_shortage'
    job_title VARCHAR(255),
    location VARCHAR(255),
    alert_message TEXT NOT NULL,
    severity VARCHAR(64) DEFAULT 'medium', -- 'low', 'medium', 'high'
    alert_data JSONB,
    status VARCHAR(64) DEFAULT 'active', -- 'active', 'acknowledged', 'resolved'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

-- Tabla de benchmarking competitivo
CREATE TABLE IF NOT EXISTS ats_competitive_benchmarking (
    id SERIAL PRIMARY KEY,
    benchmark_id VARCHAR(255) UNIQUE NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    competitor_company VARCHAR(255),
    competitor_salary_range JSONB,
    competitor_benefits TEXT[],
    our_position VARCHAR(64), -- 'above', 'at', 'below'
    insights TEXT[],
    benchmarked_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_ats_candidate_experience_application_id ON ats_candidate_experience(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_candidate_experience_overall_score ON ats_candidate_experience(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_ats_market_intelligence_job_title ON ats_market_intelligence(job_title, location);
CREATE INDEX IF NOT EXISTS idx_ats_employer_reputation_company_name ON ats_employer_reputation(company_name);
CREATE INDEX IF NOT EXISTS idx_ats_retention_predictions_candidate_id ON ats_retention_predictions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_retention_predictions_risk_level ON ats_retention_predictions(risk_level);
CREATE INDEX IF NOT EXISTS idx_ats_advanced_reports_report_type ON ats_advanced_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_ats_advanced_reports_generated_at ON ats_advanced_reports(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ats_custom_dashboards_user_email ON ats_custom_dashboards(user_email);
CREATE INDEX IF NOT EXISTS idx_ats_market_alerts_alert_type ON ats_market_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_ats_market_alerts_status ON ats_market_alerts(status);

-- Vista para reportes de hiring funnel
CREATE OR REPLACE VIEW ats_hiring_funnel_report AS
SELECT 
    j.job_id,
    j.title,
    j.department,
    COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'applied') as applied,
    COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'screening') as screening,
    COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'interviewing') as interviewing,
    COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'offer') as offer,
    COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired') as hired,
    COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'rejected') as rejected,
    ROUND(COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired')::DECIMAL / 
          NULLIF(COUNT(DISTINCT a.application_id), 0) * 100, 2) as conversion_rate
FROM ats_job_postings j
LEFT JOIN ats_applications a ON j.job_id = a.job_id
GROUP BY j.job_id, j.title, j.department;

-- Vista para cost per hire
CREATE OR REPLACE VIEW ats_cost_per_hire AS
SELECT 
    j.job_id,
    j.title,
    j.department,
    COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired') as hires,
    COUNT(DISTINCT jp.platform_name) as platforms_used,
    COUNT(DISTINCT i.interview_id) as interviews,
    COUNT(DISTINCT t.test_id) as tests,
    -- Costos estimados (en producción vendrían de facturación)
    (COUNT(DISTINCT jp.platform_name) * 500) as platform_costs,
    (COUNT(DISTINCT i.interview_id) * 50) as interview_costs,
    (COUNT(DISTINCT t.test_id) * 100) as test_costs,
    ((COUNT(DISTINCT jp.platform_name) * 500) + 
     (COUNT(DISTINCT i.interview_id) * 50) + 
     (COUNT(DISTINCT t.test_id) * 100)) / 
    NULLIF(COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired'), 0) as cost_per_hire
FROM ats_job_postings j
LEFT JOIN ats_applications a ON j.job_id = a.job_id
LEFT JOIN ats_job_platforms jp ON j.job_id = jp.job_id
LEFT JOIN ats_interviews i ON a.application_id = i.application_id
LEFT JOIN ats_assessment_tests t ON a.application_id = t.application_id
WHERE a.status = 'hired'
GROUP BY j.job_id, j.title, j.department;

