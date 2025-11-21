-- ============================================================================
-- QUERIES ÚTILES PARA ONBOARDING
-- ============================================================================

-- 1. Ver estado actual de un empleado
SELECT 
    eo.*,
    COUNT(DISTINCT oa.id) as actions_count,
    COUNT(DISTINCT oac.id) as accounts_count,
    COUNT(DISTINCT oft.id) as followup_tasks_count,
    COUNT(DISTINCT CASE WHEN oft.status = 'pending' THEN oft.id END) as pending_followups
FROM employee_onboarding eo
LEFT JOIN onboarding_actions oa ON eo.employee_email = oa.employee_email
LEFT JOIN onboarding_accounts oac ON eo.employee_email = oac.employee_email
LEFT JOIN onboarding_follow_up_tasks oft ON eo.employee_email = oft.employee_email
WHERE eo.employee_email = 'empleado@empresa.com'
GROUP BY eo.id;

-- 2. Listar onboarding recientes con resumen
SELECT 
    eo.employee_email,
    eo.full_name,
    eo.department,
    eo.position,
    eo.start_date,
    eo.status,
    COUNT(DISTINCT oa.id) as actions_completed,
    COUNT(DISTINCT oac.id) as accounts_created,
    eo.created_at,
    eo.updated_at
FROM employee_onboarding eo
LEFT JOIN onboarding_actions oa ON eo.employee_email = oa.employee_email AND oa.action_status = 'completed'
LEFT JOIN onboarding_accounts oac ON eo.employee_email = oac.employee_email
WHERE eo.created_at >= NOW() - INTERVAL '30 days'
GROUP BY eo.id
ORDER BY eo.created_at DESC
LIMIT 20;

-- 3. Estadísticas por departamento
SELECT 
    department,
    COUNT(*) as total_onboardings,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    ROUND(100.0 * COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(*), 2) as success_rate
FROM employee_onboarding
GROUP BY department
ORDER BY total_onboardings DESC;

-- 4. Tasa de éxito por mes
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    ROUND(100.0 * COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(*), 2) as success_rate
FROM employee_onboarding
WHERE created_at >= NOW() - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- 5. Acciones más comunes y su tasa de éxito
SELECT 
    action_type,
    COUNT(*) as total_executions,
    COUNT(CASE WHEN action_status = 'completed' THEN 1 END) as successful,
    COUNT(CASE WHEN action_status = 'failed' THEN 1 END) as failed,
    ROUND(100.0 * COUNT(CASE WHEN action_status = 'completed' THEN 1 END) / COUNT(*), 2) as success_rate,
    AVG(EXTRACT(EPOCH FROM (executed_at - created_at))) as avg_duration_seconds
FROM onboarding_actions
WHERE executed_at >= NOW() - INTERVAL '30 days'
GROUP BY action_type
ORDER BY total_executions DESC;

-- 6. Cuentas creadas por tipo
SELECT 
    account_type,
    COUNT(*) as total,
    COUNT(CASE WHEN account_status = 'active' THEN 1 END) as active,
    COUNT(CASE WHEN account_status = 'pending' THEN 1 END) as pending,
    COUNT(CASE WHEN account_status = 'failed' THEN 1 END) as failed
FROM onboarding_accounts
GROUP BY account_type
ORDER BY total DESC;

-- 7. Tareas de seguimiento pendientes
SELECT 
    oft.*,
    eo.full_name,
    eo.department,
    eo.start_date
FROM onboarding_follow_up_tasks oft
JOIN employee_onboarding eo ON oft.employee_email = eo.employee_email
WHERE oft.status = 'pending'
  AND oft.due_date <= CURRENT_DATE + INTERVAL '7 days'
ORDER BY oft.due_date ASC, oft.priority DESC;

-- 8. Empleados con onboarding incompleto
SELECT 
    eo.*,
    COUNT(DISTINCT oa.id) as actions_count,
    COUNT(DISTINCT CASE WHEN oa.action_status = 'failed' THEN oa.id END) as failed_actions
FROM employee_onboarding eo
LEFT JOIN onboarding_actions oa ON eo.employee_email = oa.employee_email
WHERE eo.status != 'completed'
  AND eo.created_at >= NOW() - INTERVAL '7 days'
GROUP BY eo.id
HAVING COUNT(DISTINCT CASE WHEN oa.action_status = 'failed' THEN oa.id END) > 0
ORDER BY failed_actions DESC, eo.created_at DESC;

-- 9. Tiempo promedio de onboarding
SELECT 
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) / 60 as avg_minutes,
    MIN(EXTRACT(EPOCH FROM (updated_at - created_at))) / 60 as min_minutes,
    MAX(EXTRACT(EPOCH FROM (updated_at - created_at))) / 60 as max_minutes,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (updated_at - created_at)) / 60) as median_minutes
FROM employee_onboarding
WHERE status = 'completed'
  AND created_at >= NOW() - INTERVAL '30 days';

-- 10. Integración HRIS: empleados con datos de HRIS vs proporcionados
SELECT 
    hris_source,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM employee_onboarding
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY hris_source
ORDER BY count DESC;

-- 11. Detalle completo de acciones para un empleado
SELECT 
    oa.action_type,
    oa.action_status,
    oa.action_details,
    oa.error_message,
    oa.executed_at
FROM onboarding_actions oa
WHERE oa.employee_email = 'empleado@empresa.com'
ORDER BY oa.executed_at DESC;

-- 12. Resumen de compliance por empleado
SELECT 
    eo.employee_email,
    eo.full_name,
    eo.department,
    BOOL_AND(CASE WHEN oa.action_type = 'validation' AND oa.action_status = 'completed' THEN TRUE ELSE FALSE END) as validation_passed,
    BOOL_AND(CASE WHEN oa.action_type = 'idempotency_check' AND oa.action_status = 'completed' THEN TRUE ELSE FALSE END) as idempotency_verified,
    BOOL_OR(CASE WHEN oa.action_type = 'hris_lookup' THEN TRUE ELSE FALSE END) as hris_integrated,
    COUNT(DISTINCT CASE WHEN oac.account_type = 'idp' THEN oac.id END) > 0 as idp_account_created,
    COUNT(DISTINCT CASE WHEN oac.account_type = 'workspace' THEN oac.id END) > 0 as workspace_account_created,
    BOOL_OR(CASE WHEN oa.action_type = 'welcome_email' AND oa.action_status = 'completed' THEN TRUE ELSE FALSE END) as welcome_email_sent
FROM employee_onboarding eo
LEFT JOIN onboarding_actions oa ON eo.employee_email = oa.employee_email
LEFT JOIN onboarding_accounts oac ON eo.employee_email = oac.employee_email
WHERE eo.created_at >= NOW() - INTERVAL '7 days'
GROUP BY eo.id, eo.employee_email, eo.full_name, eo.department;

-- 13. Empleados que necesitan seguimiento (tareas vencidas)
SELECT 
    eo.full_name,
    eo.employee_email,
    eo.department,
    COUNT(*) as overdue_tasks,
    MIN(oft.due_date) as oldest_overdue
FROM employee_onboarding eo
JOIN onboarding_follow_up_tasks oft ON eo.employee_email = oft.employee_email
WHERE oft.status = 'pending'
  AND oft.due_date < CURRENT_DATE
GROUP BY eo.employee_email, eo.full_name, eo.department
ORDER BY overdue_tasks DESC, oldest_overdue ASC;

-- 14. Reporte de errores por tipo
SELECT 
    action_type,
    error_message,
    COUNT(*) as occurrence_count,
    MIN(executed_at) as first_occurrence,
    MAX(executed_at) as last_occurrence
FROM onboarding_actions
WHERE action_status = 'failed'
  AND executed_at >= NOW() - INTERVAL '30 days'
GROUP BY action_type, error_message
ORDER BY occurrence_count DESC
LIMIT 20;

-- 15. Métricas de onboarding por semana
SELECT 
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) as total_onboardings,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 60) as avg_duration_minutes
FROM employee_onboarding
WHERE created_at >= NOW() - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', created_at)
ORDER BY week DESC;

