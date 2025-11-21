-- ============================================================================
-- Schema Completo Final para ATS - Todas las Funcionalidades
-- ============================================================================

-- Tabla de ofertas y negociación
CREATE TABLE IF NOT EXISTS ats_offers (
    id SERIAL PRIMARY KEY,
    offer_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    base_salary DECIMAL(12, 2) NOT NULL,
    equity DECIMAL(12, 2),
    benefits JSONB,
    start_date DATE NOT NULL,
    offer_expiry TIMESTAMPTZ NOT NULL,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'sent', 'negotiating', 'accepted', 'declined', 'expired'
    negotiation_rounds INTEGER DEFAULT 0,
    offer_data JSONB,
    document_url TEXT,
    accepted_at TIMESTAMPTZ,
    declined_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de pipelines de talento
CREATE TABLE IF NOT EXISTS ats_talent_pipelines (
    id SERIAL PRIMARY KEY,
    pipeline_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    pipeline_role VARCHAR(255) NOT NULL,
    expected_hire_date DATE,
    priority VARCHAR(64) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    status VARCHAR(64) DEFAULT 'active', -- 'active', 'contacted', 'hired', 'archived'
    notes TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    contacted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de learning paths
CREATE TABLE IF NOT EXISTS ats_learning_paths (
    id SERIAL PRIMARY KEY,
    path_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    path_type VARCHAR(128) NOT NULL, -- 'onboarding', 'technical', 'leadership', 'custom'
    path_name VARCHAR(255) NOT NULL,
    courses JSONB NOT NULL,
    status VARCHAR(64) DEFAULT 'active', -- 'active', 'completed', 'paused'
    completion_percentage DECIMAL(5, 2) DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de feedback 360
CREATE TABLE IF NOT EXISTS ats_360_feedback (
    id SERIAL PRIMARY KEY,
    feedback_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    feedback_type VARCHAR(128) NOT NULL, -- 'post_hire', 'quarterly', 'annual'
    feedback_requests JSONB NOT NULL, -- Array de solicitudes de feedback
    feedback_responses JSONB, -- Array de respuestas recibidas
    overall_score DECIMAL(5, 2),
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de compensación total
CREATE TABLE IF NOT EXISTS ats_compensation (
    id SERIAL PRIMARY KEY,
    compensation_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    base_salary DECIMAL(12, 2) NOT NULL,
    equity DECIMAL(12, 2),
    benefits_package VARCHAR(128), -- 'standard', 'premium', 'custom'
    benefits_breakdown JSONB,
    total_compensation DECIMAL(12, 2),
    location VARCHAR(255),
    currency VARCHAR(10) DEFAULT 'USD',
    effective_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de EVP personalizado
CREATE TABLE IF NOT EXISTS ats_evp_profiles (
    id SERIAL PRIMARY KEY,
    evp_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    evp_points TEXT[],
    personalized_message TEXT,
    evp_data JSONB,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES ats_job_postings(job_id) ON DELETE CASCADE
);

-- Tabla de relocations
CREATE TABLE IF NOT EXISTS ats_relocations (
    id SERIAL PRIMARY KEY,
    relocation_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    origin_location VARCHAR(255) NOT NULL,
    destination_location VARCHAR(255) NOT NULL,
    visa_required BOOLEAN DEFAULT FALSE,
    visa_type VARCHAR(128),
    visa_status VARCHAR(64), -- 'pending', 'approved', 'rejected'
    relocation_tasks JSONB,
    relocation_package JSONB,
    status VARCHAR(64) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'cancelled'
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de assessment centers
CREATE TABLE IF NOT EXISTS ats_assessment_centers (
    id SERIAL PRIMARY KEY,
    center_id VARCHAR(255) UNIQUE NOT NULL,
    application_id VARCHAR(255) NOT NULL,
    center_date DATE NOT NULL,
    center_location VARCHAR(255),
    activities JSONB NOT NULL, -- Array de actividades del assessment center
    evaluators JSONB, -- Array de evaluadores
    results JSONB,
    overall_score DECIMAL(5, 2),
    status VARCHAR(64) DEFAULT 'scheduled', -- 'scheduled', 'in_progress', 'completed', 'cancelled'
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (application_id) REFERENCES ats_applications(application_id) ON DELETE CASCADE
);

-- Tabla de networking interno
CREATE TABLE IF NOT EXISTS ats_internal_networking (
    id SERIAL PRIMARY KEY,
    networking_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    employee_id VARCHAR(255) NOT NULL, -- Empleado que hace networking
    connection_type VARCHAR(128) NOT NULL, -- 'referral', 'mentor', 'buddy', 'introduction'
    connection_date DATE NOT NULL,
    notes TEXT,
    status VARCHAR(64) DEFAULT 'active', -- 'active', 'completed', 'ended'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Tabla de alumni
CREATE TABLE IF NOT EXISTS ats_alumni (
    id SERIAL PRIMARY KEY,
    alumni_id VARCHAR(255) UNIQUE NOT NULL,
    candidate_id VARCHAR(255) NOT NULL,
    former_employee_id VARCHAR(255),
    last_position VARCHAR(255),
    last_department VARCHAR(255),
    exit_date DATE,
    exit_reason VARCHAR(128), -- 'resignation', 'termination', 'retirement', 'end_of_contract'
    rehire_eligible BOOLEAN DEFAULT TRUE,
    current_company VARCHAR(255),
    current_position VARCHAR(255),
    contact_info JSONB,
    engagement_level VARCHAR(64), -- 'high', 'medium', 'low', 'none'
    last_contacted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
);

-- Índices adicionales
CREATE INDEX IF NOT EXISTS idx_ats_offers_application_id ON ats_offers(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_offers_status ON ats_offers(status);
CREATE INDEX IF NOT EXISTS idx_ats_talent_pipelines_candidate_id ON ats_talent_pipelines(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_talent_pipelines_status ON ats_talent_pipelines(status);
CREATE INDEX IF NOT EXISTS idx_ats_learning_paths_candidate_id ON ats_learning_paths(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_360_feedback_candidate_id ON ats_360_feedback(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_360_feedback_status ON ats_360_feedback(status);
CREATE INDEX IF NOT EXISTS idx_ats_compensation_candidate_id ON ats_compensation(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_evp_profiles_candidate_id ON ats_evp_profiles(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_relocations_candidate_id ON ats_relocations(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_relocations_status ON ats_relocations(status);
CREATE INDEX IF NOT EXISTS idx_ats_assessment_centers_application_id ON ats_assessment_centers(application_id);
CREATE INDEX IF NOT EXISTS idx_ats_internal_networking_candidate_id ON ats_internal_networking(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_alumni_candidate_id ON ats_alumni(candidate_id);
CREATE INDEX IF NOT EXISTS idx_ats_alumni_rehire_eligible ON ats_alumni(rehire_eligible);

-- Vista para ofertas activas
CREATE OR REPLACE VIEW ats_active_offers AS
SELECT 
    o.offer_id,
    o.application_id,
    c.first_name || ' ' || c.last_name as candidate_name,
    j.title as job_title,
    o.base_salary,
    o.equity,
    o.status,
    o.offer_expiry,
    o.negotiation_rounds,
    CASE 
        WHEN o.offer_expiry < NOW() THEN 'expired'
        WHEN o.status = 'negotiating' THEN 'negotiating'
        ELSE o.status
    END as current_status
FROM ats_offers o
JOIN ats_candidates c ON o.candidate_id = c.candidate_id
JOIN ats_job_postings j ON o.job_id = j.job_id
WHERE o.status IN ('pending', 'sent', 'negotiating')
  AND o.offer_expiry > NOW();

-- Vista para pipelines activos
CREATE OR REPLACE VIEW ats_active_pipelines AS
SELECT 
    tp.pipeline_id,
    tp.pipeline_role,
    c.first_name || ' ' || c.last_name as candidate_name,
    c.email,
    tp.priority,
    tp.expected_hire_date,
    tp.status,
    tp.added_at
FROM ats_talent_pipelines tp
JOIN ats_candidates c ON tp.candidate_id = c.candidate_id
WHERE tp.status = 'active'
ORDER BY tp.priority DESC, tp.added_at DESC;

