-- ============================================================================
-- Schema Extendido para ATS - Funcionalidades Avanzadas
-- ============================================================================

-- Tabla de sesiones de chatbot
CREATE TABLE IF NOT EXISTS ats_chatbot_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    application_id VARCHAR(255),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_interaction_at TIMESTAMPTZ DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE SET NULL
);

-- Tabla de background checks
CREATE TABLE IF NOT EXISTS ats_background_checks (
    id SERIAL PRIMARY KEY,
    check_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    application_id VARCHAR(255),
    check_type VARCHAR(128) NOT NULL, -- 'standard', 'comprehensive', 'criminal', 'education', 'employment'
    provider VARCHAR(128) NOT NULL, -- 'checkr', 'sterling', 'hireright'
    provider_check_id VARCHAR(255),
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'failed', 'cancelled'
    initiated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    result VARCHAR(64), -- 'passed', 'failed', 'clear', 'consider'
    result_details JSONB,
    report_url TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE SET NULL
);

-- Tabla de etapas de evaluación
CREATE TABLE IF NOT EXISTS ats_evaluation_stages (
    id SERIAL PRIMARY KEY,
    stage_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    stage_name VARCHAR(255) NOT NULL, -- 'initial_screening', 'phone_screen', 'technical', 'final', etc.
    stage_order INTEGER NOT NULL,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'skipped', 'failed'
    score DECIMAL(5, 2),
    max_score DECIMAL(5, 2),
    passed BOOLEAN,
    evaluator_email VARCHAR(255),
    evaluator_name VARCHAR(255),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    notes TEXT,
    criteria JSONB, -- Criterios de evaluación
    results JSONB, -- Resultados detallados
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de métricas en tiempo real
CREATE TABLE IF NOT EXISTS ats_realtime_metrics (
    id SERIAL PRIMARY KEY,
    metric_id VARCHAR(255) UNIQUE NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_category VARCHAR(128), -- 'applications', 'interviews', 'tests', 'hires', 'time'
    job_id VARCHAR(255),
    metric_value DECIMAL(10, 2),
    metric_unit VARCHAR(64),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    period VARCHAR(64), -- 'hour', 'day', 'week', 'month'
    metadata JSONB,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de integraciones con payroll/HRIS
CREATE TABLE IF NOT EXISTS ats_payroll_sync (
    id SERIAL PRIMARY KEY,
    sync_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    payroll_system VARCHAR(128) NOT NULL, -- 'adp', 'workday', 'bamboo', 'custom'
    payroll_employee_id VARCHAR(255),
    sync_type VARCHAR(128) NOT NULL, -- 'new_hire', 'update', 'termination'
    sync_data JSONB,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'synced', 'failed'
    synced_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de alertas y notificaciones
CREATE TABLE IF NOT EXISTS ats_alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(255) UNIQUE NOT NULL,
    alert_type VARCHAR(128) NOT NULL, -- 'abandonment_risk', 'stale_application', 'missing_feedback', 'test_expiring'
    severity VARCHAR(64) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    application_id VARCHAR(255),
    job_id VARCHAR(255),
    candidate_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(64) DEFAULT 'active', -- 'active', 'acknowledged', 'resolved', 'dismissed'
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de webhooks para integraciones externas
CREATE TABLE IF NOT EXISTS ats_webhooks (
    id SERIAL PRIMARY KEY,
    webhook_id VARCHAR(255) UNIQUE NOT NULL,
    webhook_url TEXT NOT NULL,
    event_type VARCHAR(128) NOT NULL, -- 'application_received', 'interview_scheduled', 'candidate_hired', etc.
    secret_token VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    headers JSONB,
    retry_count INTEGER DEFAULT 3,
    last_triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de logs de webhooks
CREATE TABLE IF NOT EXISTS ats_webhook_logs (
    id SERIAL PRIMARY KEY,
    log_id VARCHAR(255) UNIQUE NOT NULL,
    webhook_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    payload JSONB,
    response_status INTEGER,
    response_body TEXT,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (webhook_id) REFERENCES ats_webhooks(webhook_id) ON DELETE CASCADE
);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_ats_chatbot_sessions_candidate_id ON ats_chatbot_sessions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_chatbot_sessions_resolved ON ats_chatbot_sessions(resolved);
CREATE INDEX IF NOT EXISTS idx_ats_background_checks_candidate_id ON ats_background_checks(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_background_checks_status ON ats_background_checks(status);
CREATE INDEX IF NOT EXISTS idx_ats_evaluation_stages_application_id ON ats_evaluation_stages(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_evaluation_stages_status ON ats_evaluation_stages(status);
CREATE INDEX IF NOT EXISTS idx_ats_realtime_metrics_timestamp ON ats_realtime_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ats_realtime_metrics_job_id ON ats_realtime_metrics(job_id);
CREATE INDEX IF NOT EXISTS idx_ats_payroll_sync_candidate_id ON ats_payroll_sync(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_payroll_sync_status ON ats_payroll_sync(status);
CREATE INDEX IF NOT EXISTS idx_ats_alerts_status ON ats_alerts(status);
CREATE INDEX IF NOT EXISTS idx_ats_alerts_severity ON ats_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_ats_webhooks_event_type ON ats_webhooks(event_type, is_active);
CREATE INDEX IF NOT EXISTS idx_ats_webhook_logs_webhook_id ON ats_webhook_logs(webhook_id);

-- Vista para dashboard en tiempo real
CREATE OR REPLACE VIEW ats_dashboard_realtime AS
SELECT 
    j.job_id,
    j.title,
    j.status as job_status,
    COUNT(DISTINCT a.application_id) as total_applications,
    COUNT(DISTINCT CASE WHEN a.status = 'applied' AND a.applied_at > NOW() - INTERVAL '24 hours' THEN a.application_id END) as applications_today,
    COUNT(DISTINCT CASE WHEN a.status = 'interviewing' THEN a.application_id END) as active_interviews,
    COUNT(DISTINCT CASE WHEN i.scheduled_start > NOW() AND i.scheduled_start < NOW() + INTERVAL '24 hours' THEN i.interview_id END) as interviews_today,
    COUNT(DISTINCT CASE WHEN t.status = 'pending' AND t.due_date < NOW() + INTERVAL '3 days' THEN t.test_id END) as tests_expiring_soon,
    COUNT(DISTINCT CASE WHEN a.status = 'hired' AND a.updated_at > NOW() - INTERVAL '7 days' THEN a.application_id END) as hires_this_week,
    AVG(CASE WHEN ml.overall_score IS NOT NULL THEN ml.overall_score END) as avg_ml_score,
    COUNT(DISTINCT CASE WHEN alerts.alert_id IS NOT NULL AND alerts.status = 'active' THEN alerts.alert_id END) as active_alerts
FROM ats_job_postings j
LEFT JOIN ats_applications a ON j.job_id = a.job_id
LEFT JOIN ats_interviews i ON a.application_id = i.application_id
LEFT JOIN ats_assessment_tests t ON a.application_id = t.application_id
LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
LEFT JOIN ats_alerts alerts ON a.application_id = alerts.application_id
WHERE j.status = 'active'
GROUP BY j.job_id, j.title, j.status;

