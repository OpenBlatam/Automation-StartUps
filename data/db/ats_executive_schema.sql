-- ============================================================================
-- Schema Ejecutivo y Estratégico para ATS
-- ============================================================================

-- Tabla de reportes ejecutivos
CREATE TABLE IF NOT EXISTS ats_executive_reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(255) UNIQUE NOT NULL,
    report_period VARCHAR(64) NOT NULL, -- 'monthly', 'quarterly', 'yearly'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    report_data JSONB NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    generated_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de predicciones de rotación
CREATE TABLE IF NOT EXISTS ats_turnover_predictions (
    id SERIAL PRIMARY KEY,
    prediction_id VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(255),
    turnover_analysis JSONB NOT NULL,
    predicted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de succession planning
CREATE TABLE IF NOT EXISTS ats_succession_plans (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(255) UNIQUE NOT NULL,
    position_id VARCHAR(255) NOT NULL,
    position_title VARCHAR(255),
    current_holder_id VARCHAR(255) NOT NULL,
    current_holder_name VARCHAR(255),
    potential_successors JSONB NOT NULL, -- Array de sucesores con readiness scores
    status VARCHAR(64) DEFAULT 'active', -- 'active', 'executed', 'archived'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de predicciones de éxito
CREATE TABLE IF NOT EXISTS ats_success_predictions (
    id SERIAL PRIMARY KEY,
    prediction_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    success_probability DECIMAL(5, 2) NOT NULL,
    success_level VARCHAR(64), -- 'very_high', 'high', 'medium', 'low'
    recommendation VARCHAR(64), -- 'strong_hire', 'hire', 'consider', 'reconsider'
    factors JSONB,
    predicted_at TIMESTAMPTZ DEFAULT NOW(),
    actual_success BOOLEAN, -- Actualizado después de 90 días
    actual_success_score DECIMAL(5, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de planes estratégicos de hiring
CREATE TABLE IF NOT EXISTS ats_strategic_plans (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(255) NOT NULL,
    timeframe_months INTEGER NOT NULL,
    business_goals JSONB,
    forecasts JSONB,
    estimated_budget DECIMAL(12, 2),
    total_hires_needed INTEGER,
    timeline JSONB,
    risks JSONB,
    status VARCHAR(64) DEFAULT 'draft', -- 'draft', 'approved', 'active', 'completed'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by VARCHAR(255),
    approved_at TIMESTAMPTZ
);

-- Tabla de KPIs ejecutivos
CREATE TABLE IF NOT EXISTS ats_executive_kpis (
    id SERIAL PRIMARY KEY,
    kpi_id VARCHAR(255) UNIQUE NOT NULL,
    kpi_name VARCHAR(255) NOT NULL,
    kpi_category VARCHAR(128), -- 'hiring', 'quality', 'cost', 'time', 'diversity', 'engagement'
    kpi_value DECIMAL(10, 2),
    kpi_target DECIMAL(10, 2),
    kpi_unit VARCHAR(64),
    period_start DATE,
    period_end DATE,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de dashboards ejecutivos
CREATE TABLE IF NOT EXISTS ats_executive_dashboards (
    id SERIAL PRIMARY KEY,
    dashboard_id VARCHAR(255) UNIQUE NOT NULL,
    dashboard_name VARCHAR(255) NOT NULL,
    dashboard_type VARCHAR(128), -- 'executive', 'department', 'recruiter', 'hiring_manager'
    kpis JSONB NOT NULL, -- Array de KPIs a mostrar
    widgets JSONB NOT NULL, -- Array de widgets
    filters JSONB,
    refresh_frequency VARCHAR(64), -- 'realtime', 'hourly', 'daily', 'weekly'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_ats_executive_reports_period ON ats_executive_reports(report_period, generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ats_turnover_predictions_department ON ats_turnover_predictions(department);
CREATE INDEX IF NOT EXISTS idx_ats_succession_plans_position_id ON ats_succession_plans(position_id);
CREATE INDEX IF NOT EXISTS idx_ats_succession_plans_status ON ats_succession_plans(status);
CREATE INDEX IF NOT EXISTS idx_ats_success_predictions_application_id ON ats_success_predictions(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_success_predictions_success_level ON ats_success_predictions(success_level);
CREATE INDEX IF NOT EXISTS idx_ats_strategic_plans_department ON ats_strategic_plans(department);
CREATE INDEX IF NOT EXISTS idx_ats_strategic_plans_status ON ats_strategic_plans(status);
CREATE INDEX IF NOT EXISTS idx_ats_executive_kpis_category ON ats_executive_kpis(kpi_category);
CREATE INDEX IF NOT EXISTS idx_ats_executive_kpis_calculated_at ON ats_executive_kpis(calculated_at DESC);

-- Vista para dashboard ejecutivo
CREATE OR REPLACE VIEW ats_executive_dashboard AS
SELECT 
    COUNT(DISTINCT j.job_id) FILTER (WHERE j.status = 'active') as active_jobs,
    COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired' AND a.updated_at > NOW() - INTERVAL '30 days') as hires_last_30_days,
    AVG(EXTRACT(EPOCH FROM (a.updated_at - j.posted_at)) / 86400) 
        FILTER (WHERE a.status = 'hired' AND a.updated_at > NOW() - INTERVAL '30 days') as avg_time_to_fill,
    AVG(q.actual_quality_score) FILTER (WHERE a.status = 'hired' AND a.updated_at > NOW() - INTERVAL '30 days') as avg_quality,
    AVG(roi.roi_percentage) FILTER (WHERE roi.calculated_at > NOW() - INTERVAL '30 days') as avg_roi,
    COUNT(DISTINCT e.application_id) FILTER (WHERE e.engagement_level = 'high') as high_engagement_count,
    COUNT(DISTINCT c.candidate_id) FILTER (WHERE c.gender = 'female' AND a.status = 'hired' AND a.updated_at > NOW() - INTERVAL '30 days') as female_hires
FROM ats_job_postings j
LEFT JOIN ats_applications a ON j.job_id = a.job_id
LEFT JOIN ats_quality_of_hire q ON a.candidate_id = q.candidate_id
LEFT JOIN ats_hiring_roi roi ON j.job_id = roi.job_id
LEFT JOIN ats_candidate_engagement e ON a.application_id = e.application_id
LEFT JOIN ats_candidates c ON a.candidate_id = c.candidate_id;

