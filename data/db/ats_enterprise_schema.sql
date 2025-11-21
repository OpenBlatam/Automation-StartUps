-- ============================================================================
-- Schema Enterprise para ATS - Funcionalidades Avanzadas
-- ============================================================================

-- Tabla de gamificación
CREATE TABLE IF NOT EXISTS ats_gamification (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL UNIQUE,
    points INTEGER DEFAULT 0,
    level VARCHAR(64) DEFAULT 'bronze', -- 'bronze', 'silver', 'gold', 'platinum'
    badges TEXT[],
    total_referrals INTEGER DEFAULT 0,
    successful_hires INTEGER DEFAULT 0,
    achievements JSONB,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de employee advocacy
CREATE TABLE IF NOT EXISTS ats_employee_advocacy (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(255) UNIQUE NOT NULL,
    employee_email VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    platform VARCHAR(128) NOT NULL, -- 'linkedin', 'twitter', 'facebook', 'instagram'
    post_content TEXT NOT NULL,
    post_url TEXT,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'published', 'scheduled', 'failed'
    engagement_metrics JSONB, -- Likes, shares, clicks, etc.
    scheduled_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de A/B tests
CREATE TABLE IF NOT EXISTS ats_ab_tests (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(255) UNIQUE NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(128) NOT NULL, -- 'email_template', 'interview_process', 'job_description', 'application_form'
    variants JSONB NOT NULL, -- Array de variantes
    traffic_split REAL[] NOT NULL, -- Distribución de tráfico [0.5, 0.5]
    status VARCHAR(64) DEFAULT 'draft', -- 'draft', 'active', 'paused', 'completed'
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    results JSONB, -- Resultados del test
    winner_variant INTEGER, -- Índice de la variante ganadora
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de asignaciones de A/B tests
CREATE TABLE IF NOT EXISTS ats_ab_test_assignments (
    id SERIAL PRIMARY KEY,
    assignment_id VARCHAR(255) UNIQUE NOT NULL,
    test_id VARCHAR(255) NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    variant_index INTEGER NOT NULL,
    variant_name VARCHAR(255),
    conversion_event VARCHAR(128), -- 'application_completed', 'interview_scheduled', 'hired'
    conversion_achieved BOOLEAN DEFAULT FALSE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    converted_at TIMESTAMPTZ,
    FOREIGN KEY (test_id) REFERENCES ats_ab_tests(test_id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de compliance y auditoría
CREATE TABLE IF NOT EXISTS ats_compliance_audit (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(128) NOT NULL, -- 'data_access', 'data_modification', 'data_deletion', 'export', 'consent'
    entity_type VARCHAR(128) NOT NULL, -- 'candidate', 'application', 'interview', 'test'
    entity_id VARCHAR(255) NOT NULL,
    action VARCHAR(128) NOT NULL, -- 'view', 'create', 'update', 'delete', 'export', 'download'
    user_email VARCHAR(255),
    user_role VARCHAR(128),
    ip_address VARCHAR(64),
    user_agent TEXT,
    details JSONB,
    compliance_flags TEXT[], -- 'gdpr', 'ccpa', 'eeoc', etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de consentimientos (GDPR, CCPA)
CREATE TABLE IF NOT EXISTS ats_consents (
    id SERIAL PRIMARY KEY,
    consent_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    consent_type VARCHAR(128) NOT NULL, -- 'data_processing', 'marketing', 'data_sharing', 'background_check'
    consent_status VARCHAR(64) NOT NULL, -- 'granted', 'denied', 'withdrawn'
    consent_version VARCHAR(64),
    consent_text TEXT,
    granted_at TIMESTAMPTZ,
    withdrawn_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    ip_address VARCHAR(64),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de documentación automatizada
CREATE TABLE IF NOT EXISTS ats_documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    document_type VARCHAR(128) NOT NULL, -- 'offer_letter', 'contract', 'nda', 'policy', 'onboarding'
    entity_type VARCHAR(128) NOT NULL, -- 'candidate', 'application', 'job', 'general'
    entity_id VARCHAR(255),
    document_name VARCHAR(255) NOT NULL,
    document_url TEXT,
    document_content TEXT,
    template_id VARCHAR(255),
    variables JSONB, -- Variables usadas en el template
    status VARCHAR(64) DEFAULT 'draft', -- 'draft', 'sent', 'signed', 'expired'
    signed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de eventos de documentación
CREATE TABLE IF NOT EXISTS ats_document_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(128) NOT NULL, -- 'created', 'sent', 'viewed', 'signed', 'declined', 'expired'
    user_email VARCHAR(255),
    ip_address VARCHAR(64),
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (document_id) REFERENCES ats_documents(document_id) ON DELETE CASCADE
);

-- Tabla de mobile app sessions
CREATE TABLE IF NOT EXISTS ats_mobile_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    device_type VARCHAR(64), -- 'ios', 'android', 'web'
    device_id VARCHAR(255),
    app_version VARCHAR(64),
    push_token TEXT,
    last_active_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de notificaciones push
CREATE TABLE IF NOT EXISTS ats_push_notifications (
    id SERIAL PRIMARY KEY,
    notification_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    notification_type VARCHAR(128) NOT NULL, -- 'interview_reminder', 'test_deadline', 'status_update', 'offer'
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'opened', 'failed'
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES ats_mobile_sessions(session_id) ON DELETE SET NULL
);

-- Tabla de métricas de employer branding
CREATE TABLE IF NOT EXISTS ats_branding_metrics (
    id SERIAL PRIMARY KEY,
    metric_id VARCHAR(255) UNIQUE NOT NULL,
    job_id VARCHAR(255),
    platform VARCHAR(128) NOT NULL, -- 'linkedin', 'twitter', 'facebook', 'instagram'
    metric_type VARCHAR(128) NOT NULL, -- 'impressions', 'clicks', 'applications', 'engagement'
    metric_value DECIMAL(10, 2),
    metric_data JSONB,
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_ats_gamification_user_email ON ats_gamification(user_email);
CREATE INDEX IF NOT EXISTS idx_ats_gamification_level ON ats_gamification(level);
CREATE INDEX IF NOT EXISTS idx_ats_employee_advocacy_employee_email ON ats_employee_advocacy(employee_email);
CREATE INDEX IF NOT EXISTS idx_ats_employee_advocacy_status ON ats_employee_advocacy(status);
CREATE INDEX IF NOT EXISTS idx_ats_ab_tests_status ON ats_ab_tests(status);
CREATE INDEX IF NOT EXISTS idx_ats_ab_tests_test_type ON ats_ab_tests(test_type);
CREATE INDEX IF NOT EXISTS idx_ats_ab_test_assignments_test_id ON ats_ab_test_assignments(test_id);
CREATE INDEX IF NOT EXISTS idx_ats_ab_test_assignments_conversion ON ats_ab_test_assignments(conversion_achieved);
CREATE INDEX IF NOT EXISTS idx_ats_compliance_audit_event_type ON ats_compliance_audit(event_type);
CREATE INDEX IF NOT EXISTS idx_ats_compliance_audit_user_email ON ats_compliance_audit(user_email);
CREATE INDEX IF NOT EXISTS idx_ats_compliance_audit_created_at ON ats_compliance_audit(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ats_consents_candidate_id ON ats_consents(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_consents_consent_status ON ats_consents(consent_status);
CREATE INDEX IF NOT EXISTS idx_ats_documents_entity_type ON ats_documents(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_ats_documents_status ON ats_documents(status);
CREATE INDEX IF NOT EXISTS idx_ats_document_events_document_id ON ats_document_events(document_id);
CREATE INDEX IF NOT EXISTS idx_ats_mobile_sessions_candidate_id ON ats_mobile_sessions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_push_notifications_candidate_id ON ats_push_notifications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_push_notifications_status ON ats_push_notifications(status);
CREATE INDEX IF NOT EXISTS idx_ats_branding_metrics_platform ON ats_branding_metrics(platform);

-- Vista para leaderboard de gamificación
CREATE OR REPLACE VIEW ats_gamification_leaderboard AS
SELECT 
    user_email,
    points,
    level,
    badges,
    total_referrals,
    successful_hires,
    RANK() OVER (ORDER BY points DESC) as rank,
    last_updated
FROM ats_gamification
ORDER BY points DESC
LIMIT 100;

-- Vista para resultados de A/B tests
CREATE OR REPLACE VIEW ats_ab_test_results AS
SELECT 
    t.test_id,
    t.test_name,
    t.test_type,
    a.variant_index,
    a.variant_name,
    COUNT(*) as total_assignments,
    COUNT(*) FILTER (WHERE a.conversion_achieved = true) as conversions,
    ROUND(COUNT(*) FILTER (WHERE a.conversion_achieved = true)::DECIMAL / 
          NULLIF(COUNT(*), 0) * 100, 2) as conversion_rate
FROM ats_ab_tests t
JOIN ats_ab_test_assignments a ON t.test_id = a.test_id
WHERE t.status = 'active'
GROUP BY t.test_id, t.test_name, t.test_type, a.variant_index, a.variant_name
ORDER BY t.test_id, a.variant_index;

