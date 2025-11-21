-- ============================================================================
-- Vistas Materializadas para Sistema de Aprobaciones
-- ============================================================================

-- Vista materializada: Métricas de aprobaciones diarias
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_approval_metrics AS
SELECT 
    DATE(submitted_at) AS metric_date,
    request_type,
    status,
    COUNT(*) AS request_count,
    COUNT(*) FILTER (WHERE auto_approved = true) AS auto_approved_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) AS avg_hours_to_complete,
    MIN(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) AS min_hours_to_complete,
    MAX(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) AS max_hours_to_complete,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) AS median_hours_to_complete
FROM approval_requests
WHERE submitted_at IS NOT NULL
GROUP BY DATE(submitted_at), request_type, status;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_approval_metrics_unique 
    ON mv_approval_metrics (metric_date, request_type, status);

-- Vista materializada: Estadísticas por usuario
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_approval_user_stats AS
SELECT 
    requester_email,
    request_type,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved_count,
    COUNT(*) FILTER (WHERE status = 'rejected') AS rejected_count,
    COUNT(*) FILTER (WHERE status = 'auto_approved') AS auto_approved_count,
    COUNT(*) FILTER (WHERE status = 'pending') AS pending_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) FILTER (WHERE completed_at IS NOT NULL) AS avg_hours_to_complete,
    SUM(CASE WHEN request_type = 'expense' THEN expense_amount ELSE 0 END) AS total_expense_amount,
    SUM(CASE WHEN request_type = 'vacation' THEN vacation_days ELSE 0 END) AS total_vacation_days,
    MAX(submitted_at) AS last_request_date
FROM approval_requests
GROUP BY requester_email, request_type;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_approval_user_stats_unique 
    ON mv_approval_user_stats (requester_email, request_type);

-- Vista materializada: Estadísticas de aprobadores
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_approval_approver_stats AS
SELECT 
    ac.approver_email,
    COUNT(*) AS total_approvals,
    COUNT(*) FILTER (WHERE ac.status = 'approved') AS approved_count,
    COUNT(*) FILTER (WHERE ac.status = 'rejected') AS rejected_count,
    COUNT(*) FILTER (WHERE ac.status = 'pending') AS pending_count,
    COUNT(*) FILTER (WHERE ac.timeout_date < NOW() AND ac.status = 'pending') AS overdue_count,
    AVG(EXTRACT(EPOCH FROM (ac.approved_at - ac.created_at)) / 3600) FILTER (WHERE ac.approved_at IS NOT NULL) AS avg_hours_to_approve,
    AVG(EXTRACT(EPOCH FROM (ac.rejected_at - ac.created_at)) / 3600) FILTER (WHERE ac.rejected_at IS NOT NULL) AS avg_hours_to_reject,
    AVG(ac.level) AS avg_approval_level
FROM approval_chains ac
GROUP BY ac.approver_email;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_approval_approver_stats_unique 
    ON mv_approval_approver_stats (approver_email);

-- Función para refrescar vistas materializadas
CREATE OR REPLACE FUNCTION refresh_approval_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_approval_metrics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_approval_user_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_approval_approver_stats;
END;
$$ LANGUAGE plpgsql;

-- Vista: Solicitudes por departamento
CREATE OR REPLACE VIEW v_approvals_by_department AS
SELECT 
    au.department,
    ar.request_type,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE ar.status = 'approved') AS approved_count,
    COUNT(*) FILTER (WHERE ar.status = 'rejected') AS rejected_count,
    COUNT(*) FILTER (WHERE ar.status = 'auto_approved') AS auto_approved_count,
    COUNT(*) FILTER (WHERE ar.status = 'pending') AS pending_count,
    AVG(EXTRACT(EPOCH FROM (ar.completed_at - ar.submitted_at)) / 3600) FILTER (WHERE ar.completed_at IS NOT NULL) AS avg_hours_to_complete
FROM approval_requests ar
JOIN approval_users au ON ar.requester_email = au.user_email
WHERE au.department IS NOT NULL
GROUP BY au.department, ar.request_type;

-- Vista: Tasa de auto-aprobación por tipo
CREATE OR REPLACE VIEW v_auto_approval_rates AS
SELECT 
    request_type,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE auto_approved = true) AS auto_approved_count,
    ROUND(
        (COUNT(*) FILTER (WHERE auto_approved = true)::numeric / COUNT(*)::numeric) * 100,
        2
    ) AS auto_approval_rate_percent,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) FILTER (WHERE auto_approved = true AND completed_at IS NOT NULL) AS avg_hours_auto_approved,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) FILTER (WHERE auto_approved = false AND completed_at IS NOT NULL) AS avg_hours_manual_approved
FROM approval_requests
WHERE submitted_at IS NOT NULL
GROUP BY request_type;

-- Vista: Solicitudes que requieren atención (vencidas o próximas a vencer)
CREATE OR REPLACE VIEW v_urgent_approvals AS
SELECT 
    ac.id AS chain_id,
    ar.id AS request_id,
    ar.request_type,
    ar.title,
    ar.requester_email,
    au.user_name AS requester_name,
    ac.approver_email,
    approver.user_name AS approver_name,
    ac.level,
    ar.priority,
    ac.timeout_date,
    CASE 
        WHEN ac.timeout_date < NOW() THEN 'overdue'
        WHEN ac.timeout_date <= NOW() + INTERVAL '1 day' THEN 'urgent'
        WHEN ac.timeout_date <= NOW() + INTERVAL '2 days' THEN 'due_soon'
        ELSE 'normal'
    END AS urgency_level,
    EXTRACT(EPOCH FROM (ac.timeout_date - NOW())) / 86400 AS days_until_timeout,
    ac.created_at AS approval_created_at,
    ac.notified_at AS last_notified_at
FROM approval_chains ac
JOIN approval_requests ar ON ac.request_id = ar.id
JOIN approval_users au ON ar.requester_email = au.user_email
LEFT JOIN approval_users approver ON ac.approver_email = approver.user_email
WHERE ac.status = 'pending' 
  AND ar.status = 'pending'
  AND ac.timeout_date IS NOT NULL
  AND ac.timeout_date <= NOW() + INTERVAL '3 days'
ORDER BY 
    CASE urgency_level
        WHEN 'overdue' THEN 1
        WHEN 'urgent' THEN 2
        WHEN 'due_soon' THEN 3
        ELSE 4
    END,
    ar.priority DESC,
    ac.timeout_date ASC;

-- Índices para mejorar performance de las vistas
CREATE INDEX IF NOT EXISTS idx_approval_requests_submitted_date 
    ON approval_requests(DATE(submitted_at)) WHERE submitted_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_approval_chains_timeout_status 
    ON approval_chains(timeout_date, status) 
    WHERE timeout_date IS NOT NULL AND status = 'pending';

