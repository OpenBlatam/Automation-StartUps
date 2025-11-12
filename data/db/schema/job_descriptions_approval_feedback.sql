-- Schema para aprobaciones y feedback

-- Tabla de workflows de aprobación
CREATE TABLE IF NOT EXISTS approval_workflows (
    workflow_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id),
    status VARCHAR(50) DEFAULT 'pending',
    approvers JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_approval_workflows_job_desc ON approval_workflows(job_description_id);
CREATE INDEX IF NOT EXISTS idx_approval_workflows_status ON approval_workflows(status);

-- Tabla de historial de aprobaciones
CREATE TABLE IF NOT EXISTS approval_history (
    history_id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES approval_workflows(workflow_id),
    approver_email VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'approved', 'rejected', 'requested_changes'
    comments TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approval_history_workflow ON approval_history(workflow_id);
CREATE INDEX IF NOT EXISTS idx_approval_history_approver ON approval_history(approver_email);

-- Tabla de feedback de candidatos
CREATE TABLE IF NOT EXISTS candidate_feedback (
    feedback_id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES job_applications(application_id),
    feedback_data JSONB NOT NULL,
    sentiment_score DECIMAL(3,2),
    sentiment_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_candidate_feedback_application ON candidate_feedback(application_id);
CREATE INDEX IF NOT EXISTS idx_candidate_feedback_sentiment ON candidate_feedback(sentiment_category);

-- Vista de workflows pendientes
CREATE OR REPLACE VIEW pending_approvals AS
SELECT 
    aw.workflow_id,
    aw.job_description_id,
    jd.role,
    aw.status,
    aw.approvers,
    COUNT(ah.history_id) as approvals_count,
    jsonb_array_length(aw.approvers) as total_approvers_required
FROM approval_workflows aw
JOIN job_descriptions jd ON aw.job_description_id = jd.job_description_id
LEFT JOIN approval_history ah ON aw.workflow_id = ah.workflow_id AND ah.action = 'approved'
WHERE aw.status = 'pending'
GROUP BY aw.workflow_id, aw.job_description_id, jd.role, aw.status, aw.approvers;






