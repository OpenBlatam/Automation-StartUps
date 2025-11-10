-- Schema para aprobación y análisis predictivo

-- Tabla de workflows de aprobación
CREATE TABLE IF NOT EXISTS approval_workflows (
    workflow_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id) ON DELETE CASCADE,
    workflow_data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_description_id)
);

CREATE INDEX IF NOT EXISTS idx_workflows_job_desc ON approval_workflows(job_description_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON approval_workflows(status);

-- Tabla de registros de aprobación
CREATE TABLE IF NOT EXISTS approval_records (
    record_id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES approval_workflows(workflow_id) ON DELETE CASCADE,
    approver_email VARCHAR(255) NOT NULL,
    decision VARCHAR(50) NOT NULL, -- 'approve' or 'reject'
    comments TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approval_records_workflow ON approval_records(workflow_id);
CREATE INDEX IF NOT EXISTS idx_approval_records_approver ON approval_records(approver_email);

-- Tabla de predicciones
CREATE TABLE IF NOT EXISTS job_predictions (
    prediction_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id) ON DELETE CASCADE,
    prediction_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_description_id)
);

CREATE INDEX IF NOT EXISTS idx_predictions_job_desc ON job_predictions(job_description_id);

-- Tabla de recomendaciones
CREATE TABLE IF NOT EXISTS job_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id) ON DELETE CASCADE,
    recommendations JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_description_id)
);

CREATE INDEX IF NOT EXISTS idx_recommendations_job_desc ON job_recommendations(job_description_id);

-- Vista de workflows pendientes
CREATE OR REPLACE VIEW pending_approvals AS
SELECT 
    aw.workflow_id,
    aw.job_description_id,
    jd.role,
    jd.level,
    aw.status,
    aw.workflow_data->>'current_step' as current_step,
    aw.workflow_data->'approvers' as approvers,
    aw.created_at
FROM approval_workflows aw
JOIN job_descriptions jd ON aw.job_description_id = jd.job_description_id
WHERE aw.status = 'pending'
ORDER BY aw.created_at DESC;

