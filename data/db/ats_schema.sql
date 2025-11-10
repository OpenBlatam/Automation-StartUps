-- ============================================================================
-- ATS (Applicant Tracking System) Schema - Sistema Completo de Reclutamiento
-- Publicación de vacantes, filtrado de CVs, entrevistas, tests y comunicación
-- ============================================================================

-- Tabla principal de vacantes/job postings
CREATE TABLE IF NOT EXISTS ats_job_postings (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    department VARCHAR(255),
    location VARCHAR(255),
    employment_type VARCHAR(128), -- 'full_time', 'part_time', 'contract', 'internship'
    remote_type VARCHAR(128), -- 'remote', 'hybrid', 'onsite'
    description TEXT NOT NULL,
    requirements TEXT,
    keywords TEXT[], -- Palabras clave para filtrado automático
    salary_range_min DECIMAL(12, 2),
    salary_range_max DECIMAL(12, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(64) DEFAULT 'draft', -- 'draft', 'active', 'paused', 'closed', 'filled'
    hiring_manager_email VARCHAR(255),
    recruiter_email VARCHAR(255),
    priority VARCHAR(64) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    max_applicants INTEGER,
    current_applicants INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    posted_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ
);

-- Tabla de plataformas donde se publican las vacantes
CREATE TABLE IF NOT EXISTS ats_job_platforms (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL,
    platform_name VARCHAR(128) NOT NULL, -- 'greenhouse', 'linkedin', 'indeed', 'glassdoor', 'monster', 'custom'
    platform_job_id VARCHAR(255), -- ID del job en la plataforma externa
    platform_url TEXT,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'posted', 'failed', 'paused', 'removed'
    posted_at TIMESTAMPTZ,
    removed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB, -- Información adicional de la plataforma
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE,
    UNIQUE(job_id, platform_name)
);

-- Tabla principal de candidatos
CREATE TABLE IF NOT EXISTS ats_candidates (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(64),
    location VARCHAR(255),
    resume_url TEXT,
    resume_text TEXT, -- Texto extraído del CV para búsqueda
    cover_letter TEXT,
    source VARCHAR(128), -- 'linkedin', 'indeed', 'greenhouse', 'referral', 'direct', 'website'
    referral_email VARCHAR(255), -- Email de quien refirió al candidato
    status VARCHAR(64) DEFAULT 'new', -- 'new', 'reviewing', 'shortlisted', 'interviewing', 'offer', 'hired', 'rejected', 'withdrawn'
    stage VARCHAR(128), -- Etapa actual del proceso
    job_id VARCHAR(255),
    application_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE SET NULL
);

-- Tabla de aplicaciones (candidato + vacante)
CREATE TABLE IF NOT EXISTS ats_applications (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    status VARCHAR(64) DEFAULT 'applied', -- 'applied', 'screening', 'interview', 'offer', 'hired', 'rejected', 'withdrawn'
    match_score DECIMAL(5, 2), -- Score de matching basado en keywords
    keyword_matches TEXT[], -- Palabras clave encontradas en el CV
    rejection_reason TEXT,
    rejection_stage VARCHAR(128),
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    reviewed_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE,
    UNIQUE(candidate_id, job_id)
);

-- Tabla de filtrado automático de CVs
CREATE TABLE IF NOT EXISTS ats_cv_filtering (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(255) NOT NULL,
    filter_type VARCHAR(128) NOT NULL, -- 'keyword', 'skill', 'experience', 'education', 'custom'
    filter_criteria JSONB NOT NULL, -- Criterios del filtro
    matched_keywords TEXT[], -- Palabras clave encontradas
    match_score DECIMAL(5, 2),
    passed BOOLEAN DEFAULT FALSE,
    filter_details JSONB, -- Detalles del análisis
    filtered_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de entrevistas programadas
CREATE TABLE IF NOT EXISTS ats_interviews (
    id SERIAL PRIMARY KEY,
    interview_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    interview_type VARCHAR(128) NOT NULL, -- 'phone_screen', 'technical', 'behavioral', 'panel', 'final', 'onsite'
    interview_stage VARCHAR(128), -- Etapa del proceso
    interviewer_email VARCHAR(255) NOT NULL,
    interviewer_name VARCHAR(255),
    candidate_email VARCHAR(255) NOT NULL,
    candidate_name VARCHAR(255),
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    timezone VARCHAR(64) DEFAULT 'UTC',
    location VARCHAR(255), -- 'zoom', 'meet', 'onsite_address', 'phone'
    meeting_link TEXT,
    calendar_event_id VARCHAR(255), -- ID del evento en calendario (Google Calendar, Outlook)
    status VARCHAR(64) DEFAULT 'scheduled', -- 'scheduled', 'confirmed', 'completed', 'cancelled', 'rescheduled', 'no_show'
    confirmation_sent_at TIMESTAMPTZ,
    reminder_sent_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    notes TEXT,
    feedback TEXT, -- Feedback post-entrevista
    rating INTEGER, -- Rating 1-5
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de tests de evaluación enviados
CREATE TABLE IF NOT EXISTS ats_assessment_tests (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    test_type VARCHAR(128) NOT NULL, -- 'technical', 'coding', 'personality', 'language', 'custom'
    test_platform VARCHAR(128), -- 'hackerrank', 'codility', 'custom', 'internal'
    test_name VARCHAR(255) NOT NULL,
    test_url TEXT,
    test_instructions TEXT,
    duration_minutes INTEGER,
    due_date TIMESTAMPTZ,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'sent', 'in_progress', 'completed', 'expired', 'not_taken'
    sent_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    score DECIMAL(5, 2),
    max_score DECIMAL(5, 2),
    passed BOOLEAN,
    results_url TEXT,
    metadata JSONB, -- Resultados detallados del test
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de comunicaciones con candidatos
CREATE TABLE IF NOT EXISTS ats_communications (
    id SERIAL PRIMARY KEY,
    communication_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    application_id VARCHAR(255),
    communication_type VARCHAR(128) NOT NULL, -- 'email', 'sms', 'call', 'in_app', 'slack'
    direction VARCHAR(64) NOT NULL, -- 'outbound', 'inbound'
    subject VARCHAR(500),
    body TEXT NOT NULL,
    channel VARCHAR(128), -- 'email', 'sms', 'phone', 'whatsapp', 'slack'
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(64),
    sender_email VARCHAR(255),
    sender_name VARCHAR(255),
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'read', 'failed', 'bounced'
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    template_id VARCHAR(255), -- ID del template usado
    metadata JSONB, -- Información adicional (message_id, tracking, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE SET NULL
);

-- Tabla de integración con Greenhouse u otros ATS
CREATE TABLE IF NOT EXISTS ats_external_sync (
    id SERIAL PRIMARY KEY,
    sync_id VARCHAR(255) UNIQUE NOT NULL,
    external_system VARCHAR(128) NOT NULL, -- 'greenhouse', 'lever', 'workday_recruiting', 'custom'
    external_id VARCHAR(255) NOT NULL, -- ID en el sistema externo
    internal_type VARCHAR(128) NOT NULL, -- 'job', 'candidate', 'application', 'interview'
    internal_id VARCHAR(255) NOT NULL, -- ID en nuestro sistema
    sync_direction VARCHAR(64) DEFAULT 'bidirectional', -- 'inbound', 'outbound', 'bidirectional'
    last_synced_at TIMESTAMPTZ,
    sync_status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'synced', 'failed', 'conflict'
    sync_data JSONB, -- Datos sincronizados
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(external_system, external_id, internal_type)
);

-- Tabla de configuración de filtros automáticos
CREATE TABLE IF NOT EXISTS ats_filter_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(255) UNIQUE NOT NULL,
    job_id VARCHAR(255),
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(128) NOT NULL, -- 'keyword', 'skill', 'experience', 'education', 'custom'
    rule_config JSONB NOT NULL, -- Configuración del filtro
    priority INTEGER DEFAULT 0, -- Prioridad del filtro (mayor = más importante)
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de templates de comunicación
CREATE TABLE IF NOT EXISTS ats_communication_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(255) UNIQUE NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    template_type VARCHAR(128) NOT NULL, -- 'email', 'sms', 'interview_invite', 'rejection', 'offer', etc.
    subject VARCHAR(500),
    body TEXT NOT NULL,
    variables JSONB, -- Variables disponibles en el template
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_ats_job_postings_status ON ats_job_postings(status);
CREATE INDEX IF NOT EXISTS idx_ats_job_postings_hiring_manager ON ats_job_postings(hiring_manager_email);
CREATE INDEX IF NOT EXISTS idx_ats_candidates_email ON ats_candidates(email);
CREATE INDEX IF NOT EXISTS idx_ats_candidates_status ON ats_candidates(status);
CREATE INDEX IF NOT EXISTS idx_ats_candidates_job_id ON ats_candidates(job_id);
CREATE INDEX IF NOT EXISTS idx_ats_applications_status ON ats_applications(status);
CREATE INDEX IF NOT EXISTS idx_ats_applications_job_id ON ats_applications(job_id);
CREATE INDEX IF NOT EXISTS idx_ats_applications_candidate_id ON ats_applications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_interviews_scheduled_start ON ats_interviews(scheduled_start);
CREATE INDEX IF NOT EXISTS idx_ats_interviews_status ON ats_interviews(status);
CREATE INDEX IF NOT EXISTS idx_ats_interviews_application_id ON ats_interviews(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_assessment_tests_status ON ats_assessment_tests(status);
CREATE INDEX IF NOT EXISTS idx_ats_assessment_tests_due_date ON ats_assessment_tests(due_date);
CREATE INDEX IF NOT EXISTS idx_ats_communications_candidate_id ON ats_communications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_communications_status ON ats_communications(status);
CREATE INDEX IF NOT EXISTS idx_ats_communications_sent_at ON ats_communications(sent_at);
CREATE INDEX IF NOT EXISTS idx_ats_external_sync_external_id ON ats_external_sync(external_id);
CREATE INDEX IF NOT EXISTS idx_ats_external_sync_internal_id ON ats_external_sync(internal_id);
CREATE INDEX IF NOT EXISTS idx_ats_job_platforms_job_id ON ats_job_platforms(job_id);
CREATE INDEX IF NOT EXISTS idx_ats_job_platforms_status ON ats_job_platforms(status);

-- Tabla de scoring avanzado con ML
CREATE TABLE IF NOT EXISTS ats_ml_scoring (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(255) NOT NULL,
    model_version VARCHAR(128),
    overall_score DECIMAL(5, 2),
    keyword_score DECIMAL(5, 2),
    experience_score DECIMAL(5, 2),
    skill_score DECIMAL(5, 2),
    education_score DECIMAL(5, 2),
    cultural_fit_score DECIMAL(5, 2),
    predicted_hire_probability DECIMAL(5, 2),
    scoring_factors JSONB,
    model_features JSONB,
    scored_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de workflows automáticos
CREATE TABLE IF NOT EXISTS ats_workflows (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) UNIQUE NOT NULL,
    workflow_name VARCHAR(255) NOT NULL,
    workflow_type VARCHAR(128) NOT NULL, -- 'auto_reject', 'auto_advance', 'auto_schedule', 'auto_notify'
    trigger_conditions JSONB NOT NULL, -- Condiciones que activan el workflow
    actions JSONB NOT NULL, -- Acciones a ejecutar
    job_id VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de ejecuciones de workflows
CREATE TABLE IF NOT EXISTS ats_workflow_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(255) UNIQUE NOT NULL,
    workflow_id VARCHAR(255) NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    trigger_event VARCHAR(128) NOT NULL,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'executing', 'completed', 'failed'
    actions_executed JSONB,
    error_message TEXT,
    executed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (workflow_id) REFERENCES ats_workflows(workflow_id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de referidos extendida
CREATE TABLE IF NOT EXISTS ats_referrals (
    id SERIAL PRIMARY KEY,
    referral_id VARCHAR(255) UNIQUE NOT NULL,
    referrer_email VARCHAR(255) NOT NULL,
    referrer_name VARCHAR(255),
    candidate_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255),
    referral_date TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'hired', 'rejected', 'withdrawn'
    bonus_amount DECIMAL(10, 2),
    bonus_paid BOOLEAN DEFAULT FALSE,
    bonus_paid_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE SET NULL
);

-- Tabla de feedback avanzado
CREATE TABLE IF NOT EXISTS ats_feedback (
    id SERIAL PRIMARY KEY,
    feedback_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    interview_id VARCHAR(255),
    feedback_type VARCHAR(128) NOT NULL, -- 'interview', 'test', 'application', 'overall'
    reviewer_email VARCHAR(255) NOT NULL,
    reviewer_name VARCHAR(255),
    overall_rating INTEGER, -- 1-5
    technical_skills INTEGER,
    communication_skills INTEGER,
    cultural_fit INTEGER,
    problem_solving INTEGER,
    leadership_potential INTEGER,
    recommendation VARCHAR(128), -- 'strong_yes', 'yes', 'maybe', 'no', 'strong_no'
    strengths TEXT,
    weaknesses TEXT,
    feedback_text TEXT,
    is_confidential BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (interview_id) REFERENCES ats_interviews(interview_id) ON DELETE SET NULL
);

-- Tabla de analytics y métricas
CREATE TABLE IF NOT EXISTS ats_analytics (
    id SERIAL PRIMARY KEY,
    metric_id VARCHAR(255) UNIQUE NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_type VARCHAR(128) NOT NULL, -- 'time_to_hire', 'time_to_fill', 'source_performance', 'conversion_rate'
    job_id VARCHAR(255),
    metric_value DECIMAL(10, 2),
    metric_unit VARCHAR(64),
    metric_data JSONB,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de onboarding post-hire
CREATE TABLE IF NOT EXISTS ats_post_hire_onboarding (
    id SERIAL PRIMARY KEY,
    onboarding_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    hire_date DATE NOT NULL,
    start_date DATE NOT NULL,
    onboarding_status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'failed'
    welcome_email_sent BOOLEAN DEFAULT FALSE,
    documents_sent BOOLEAN DEFAULT FALSE,
    background_check_status VARCHAR(64), -- 'pending', 'in_progress', 'passed', 'failed'
    onboarding_tasks JSONB,
    completed_tasks INTEGER DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_ats_ml_scoring_application_id ON ats_ml_scoring(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_ml_scoring_overall_score ON ats_ml_scoring(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_ats_workflows_enabled ON ats_workflows(enabled, workflow_type);
CREATE INDEX IF NOT EXISTS idx_ats_workflow_executions_status ON ats_workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_ats_referrals_referrer_email ON ats_referrals(referrer_email);
CREATE INDEX IF NOT EXISTS idx_ats_referrals_status ON ats_referrals(status);
CREATE INDEX IF NOT EXISTS idx_ats_feedback_application_id ON ats_feedback(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_feedback_overall_rating ON ats_feedback(overall_rating DESC);
CREATE INDEX IF NOT EXISTS idx_ats_analytics_metric_type ON ats_analytics(metric_type);
CREATE INDEX IF NOT EXISTS idx_ats_post_hire_onboarding_status ON ats_post_hire_onboarding(onboarding_status);

-- Vista para estadísticas de hiring
CREATE OR REPLACE VIEW ats_hiring_stats AS
SELECT 
    j.job_id,
    j.title,
    j.status as job_status,
    COUNT(DISTINCT a.application_id) as total_applications,
    COUNT(DISTINCT CASE WHEN a.status = 'hired' THEN a.application_id END) as hired_count,
    COUNT(DISTINCT CASE WHEN a.status = 'interviewing' THEN a.application_id END) as interviewing_count,
    COUNT(DISTINCT CASE WHEN a.status = 'offer' THEN a.application_id END) as offer_count,
    COUNT(DISTINCT CASE WHEN a.status = 'rejected' THEN a.application_id END) as rejected_count,
    AVG(a.match_score) as avg_match_score,
    COUNT(DISTINCT i.interview_id) as total_interviews,
    COUNT(DISTINCT CASE WHEN i.status = 'completed' THEN i.interview_id END) as completed_interviews,
    COUNT(DISTINCT t.test_id) as total_tests,
    COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.test_id END) as completed_tests,
    AVG(ml.overall_score) as avg_ml_score,
    AVG(ml.predicted_hire_probability) as avg_hire_probability
FROM ats_job_postings j
LEFT JOIN ats_applications a ON j.job_id = a.job_id
LEFT JOIN ats_interviews i ON a.application_id = i.application_id
LEFT JOIN ats_assessment_tests t ON a.application_id = t.application_id
LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
GROUP BY j.job_id, j.title, j.status;

-- Vista para analytics avanzados
CREATE OR REPLACE VIEW ats_advanced_analytics AS
SELECT 
    j.job_id,
    j.title,
    j.department,
    j.created_at as job_created_at,
    j.posted_at,
    COUNT(DISTINCT a.application_id) as total_applications,
    COUNT(DISTINCT CASE WHEN a.status = 'hired' THEN a.application_id END) as hired,
    COUNT(DISTINCT CASE WHEN a.status = 'rejected' THEN a.application_id END) as rejected,
    -- Time to fill (días desde publicación hasta contratación)
    AVG(CASE 
        WHEN a.status = 'hired' THEN EXTRACT(EPOCH FROM (a.updated_at - j.posted_at)) / 86400 
    END) as avg_time_to_fill_days,
    -- Time to hire (días desde aplicación hasta contratación)
    AVG(CASE 
        WHEN a.status = 'hired' THEN EXTRACT(EPOCH FROM (a.updated_at - a.applied_at)) / 86400 
    END) as avg_time_to_hire_days,
    -- Conversion rates
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'hired' THEN a.application_id END)::DECIMAL / 
          NULLIF(COUNT(DISTINCT a.application_id), 0) * 100, 2) as hire_conversion_rate,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'interviewing' THEN a.application_id END)::DECIMAL / 
          NULLIF(COUNT(DISTINCT a.application_id), 0) * 100, 2) as interview_conversion_rate,
    -- Source performance
    COUNT(DISTINCT CASE WHEN c.source = 'referral' THEN c.candidate_id END) as referral_count,
    COUNT(DISTINCT CASE WHEN c.source = 'linkedin' THEN c.candidate_id END) as linkedin_count,
    COUNT(DISTINCT CASE WHEN c.source = 'indeed' THEN c.candidate_id END) as indeed_count,
    -- Average scores
    AVG(a.match_score) as avg_match_score,
    AVG(ml.overall_score) as avg_ml_score,
    AVG(ml.predicted_hire_probability) as avg_hire_probability,
    -- Interview metrics
    AVG(i.rating) as avg_interview_rating,
    COUNT(DISTINCT CASE WHEN i.rating >= 4 THEN i.interview_id END) as high_rated_interviews,
    -- Test metrics
    AVG(t.score) as avg_test_score,
    COUNT(DISTINCT CASE WHEN t.passed = true THEN t.test_id END) as passed_tests
FROM ats_job_postings j
LEFT JOIN ats_applications a ON j.job_id = a.job_id
LEFT JOIN ats_candidates c ON a.candidate_id = c.candidate_id
LEFT JOIN ats_interviews i ON a.application_id = i.application_id
LEFT JOIN ats_assessment_tests t ON a.application_id = t.application_id
LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
GROUP BY j.job_id, j.title, j.department, j.created_at, j.posted_at;

