-- Queries SQL útiles para monitoreo y análisis de sincronizaciones
-- ==================================================================

-- 1. Resumen de sincronizaciones del último día
SELECT 
    source_type,
    target_type,
    status,
    COUNT(*) as count,
    SUM(total_records) as total_records,
    SUM(successful) as total_successful,
    SUM(failed) as total_failed,
    AVG(duration_seconds) as avg_duration_seconds
FROM sync_history
WHERE started_at >= CURRENT_DATE
GROUP BY source_type, target_type, status
ORDER BY count DESC;

-- 2. Tasa de éxito por tipo de sincronización
SELECT 
    source_type,
    target_type,
    COUNT(*) as total_syncs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    ROUND(
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::numeric / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as success_rate_percent,
    AVG(duration_seconds) as avg_duration
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '7 days'
GROUP BY source_type, target_type
ORDER BY success_rate_percent DESC;

-- 3. Registros con errores frecuentes
SELECT 
    source_type,
    target_type,
    status,
    error_message,
    COUNT(*) as error_count,
    MAX(synced_at) as last_occurrence
FROM sync_records
WHERE status = 'failed'
    AND synced_at >= NOW() - INTERVAL '7 days'
GROUP BY source_type, target_type, status, error_message
ORDER BY error_count DESC
LIMIT 20;

-- 4. Conflictos pendientes de resolución
SELECT 
    sc.id,
    sc.conflict_type,
    sc.conflict_fields,
    sr.source_id,
    sr.source_type,
    sr.target_type,
    sc.created_at,
    AGE(NOW(), sc.created_at) as age
FROM sync_conflicts sc
JOIN sync_records sr ON sc.sync_record_id = sr.id
WHERE sc.resolved_at IS NULL
ORDER BY sc.created_at DESC;

-- 5. Performance de sincronizaciones por hora del día
SELECT 
    DATE_TRUNC('hour', started_at) as hour,
    source_type,
    target_type,
    COUNT(*) as sync_count,
    AVG(duration_seconds) as avg_duration,
    AVG(successful::float / NULLIF(total_records, 0)) * 100 as avg_success_rate,
    MAX(duration_seconds) as max_duration
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('hour', started_at), source_type, target_type
ORDER BY hour DESC, sync_count DESC;

-- 6. Sincronizaciones más lentas
SELECT 
    sync_id,
    source_type,
    target_type,
    total_records,
    duration_seconds,
    successful,
    failed,
    started_at
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '7 days'
ORDER BY duration_seconds DESC
LIMIT 20;

-- 7. Registros no sincronizados (sin target_id)
SELECT 
    source_type,
    target_type,
    COUNT(*) as unsynced_count,
    MAX(synced_at) as last_attempt
FROM sync_records
WHERE target_id IS NULL
    AND status != 'skipped'
    AND synced_at >= NOW() - INTERVAL '7 days'
GROUP BY source_type, target_type
ORDER BY unsynced_count DESC;

-- 8. Tendencias de sincronización (últimos 30 días)
SELECT 
    DATE_TRUNC('day', started_at) as sync_date,
    source_type,
    target_type,
    COUNT(*) as daily_syncs,
    SUM(total_records) as daily_records,
    AVG(successful::float / NULLIF(total_records, 0)) * 100 as daily_success_rate,
    AVG(duration_seconds) as avg_duration
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', started_at), source_type, target_type
ORDER BY sync_date DESC;

-- 9. Registros duplicados (mismo source_id múltiples veces)
SELECT 
    source_id,
    source_type,
    target_type,
    COUNT(*) as duplicate_count,
    ARRAY_AGG(id ORDER BY synced_at DESC) as record_ids,
    MAX(synced_at) as last_sync
FROM sync_records
GROUP BY source_id, source_type, target_type
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, last_sync DESC;

-- 10. Métricas de throughput por tipo
SELECT 
    source_type,
    target_type,
    COUNT(*) as total_syncs,
    SUM(total_records) as total_records_processed,
    SUM(duration_seconds) as total_time_seconds,
    ROUND(
        SUM(total_records) / NULLIF(SUM(duration_seconds), 0),
        2
    ) as records_per_second,
    AVG(successful::float / NULLIF(total_records, 0)) * 100 as avg_success_rate
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '7 days'
    AND duration_seconds > 0
GROUP BY source_type, target_type
ORDER BY records_per_second DESC;

-- 11. Alertas: Sincronizaciones con alta tasa de fallo
SELECT 
    sync_id,
    source_type,
    target_type,
    total_records,
    successful,
    failed,
    ROUND(failed::float / NULLIF(total_records, 0) * 100, 2) as failure_rate_percent,
    duration_seconds,
    started_at
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '24 hours'
    AND failed::float / NULLIF(total_records, 0) > 0.1  -- Más del 10% de fallos
ORDER BY failure_rate_percent DESC;

-- 12. Registros que necesitan reintento
SELECT 
    sr.id,
    sr.source_id,
    sr.source_type,
    sr.target_type,
    sr.error_message,
    sr.status,
    sr.synced_at,
    sh.sync_id,
    sh.started_at as sync_started_at
FROM sync_records sr
JOIN sync_history sh ON sr.sync_history_id = sh.id
WHERE sr.status = 'failed'
    AND sr.synced_at >= NOW() - INTERVAL '7 days'
    AND sr.error_message NOT LIKE '%timeout%'  -- Excluir timeouts temporales
ORDER BY sr.synced_at DESC
LIMIT 100;

-- 13. Estadísticas de conflictos resueltos vs pendientes
SELECT 
    CASE 
        WHEN resolved_at IS NULL THEN 'pending'
        ELSE 'resolved'
    END as resolution_status,
    conflict_type,
    COUNT(*) as count,
    AVG(AGE(COALESCE(resolved_at, NOW()), created_at)) as avg_resolution_time
FROM sync_conflicts
GROUP BY resolution_status, conflict_type
ORDER BY resolution_status, count DESC;

-- 14. Comparación de checksums (detección de cambios)
SELECT 
    source_id,
    source_type,
    target_type,
    checksum,
    COUNT(DISTINCT checksum) as checksum_versions,
    COUNT(*) as sync_count,
    MAX(synced_at) as last_sync
FROM sync_records
WHERE checksum IS NOT NULL
    AND synced_at >= NOW() - INTERVAL '30 days'
GROUP BY source_id, source_type, target_type, checksum
HAVING COUNT(DISTINCT checksum) > 1  -- Múltiples versiones del mismo registro
ORDER BY sync_count DESC;

-- 15. Dashboard resumen ejecutivo
SELECT 
    'Total Syncs' as metric,
    COUNT(*)::text as value
FROM sync_history
WHERE started_at >= CURRENT_DATE
UNION ALL
SELECT 
    'Successful Syncs',
    COUNT(*)::text
FROM sync_history
WHERE started_at >= CURRENT_DATE
    AND status = 'completed'
UNION ALL
SELECT 
    'Failed Syncs',
    COUNT(*)::text
FROM sync_history
WHERE started_at >= CURRENT_DATE
    AND status = 'failed'
UNION ALL
SELECT 
    'Total Records Processed',
    SUM(total_records)::text
FROM sync_history
WHERE started_at >= CURRENT_DATE
UNION ALL
SELECT 
    'Avg Duration (seconds)',
    ROUND(AVG(duration_seconds), 2)::text
FROM sync_history
WHERE started_at >= CURRENT_DATE
    AND duration_seconds IS NOT NULL
UNION ALL
SELECT 
    'Pending Conflicts',
    COUNT(*)::text
FROM sync_conflicts
WHERE resolved_at IS NULL;

-- 16. Análisis de patrones de error
SELECT 
    CASE 
        WHEN error_message LIKE '%timeout%' THEN 'Timeout'
        WHEN error_message LIKE '%authentication%' OR error_message LIKE '%auth%' THEN 'Authentication'
        WHEN error_message LIKE '%rate limit%' THEN 'Rate Limit'
        WHEN error_message LIKE '%not found%' THEN 'Not Found'
        WHEN error_message LIKE '%validation%' THEN 'Validation'
        ELSE 'Other'
    END as error_category,
    COUNT(*) as error_count,
    MAX(synced_at) as last_occurrence
FROM sync_records
WHERE status = 'failed'
    AND synced_at >= NOW() - INTERVAL '7 days'
GROUP BY error_category
ORDER BY error_count DESC;

-- 17. Sincronizaciones por usuario/responsable (si hay campo en metadata)
SELECT 
    (metadata->>'triggered_by')::text as triggered_by,
    COUNT(*) as sync_count,
    SUM(total_records) as total_records,
    AVG(duration_seconds) as avg_duration
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '30 days'
    AND metadata->>'triggered_by' IS NOT NULL
GROUP BY triggered_by
ORDER BY sync_count DESC;

-- 18. Registros que nunca se sincronizaron exitosamente
SELECT 
    source_id,
    source_type,
    target_type,
    COUNT(*) as attempt_count,
    MAX(synced_at) as last_attempt,
    STRING_AGG(DISTINCT status, ', ') as statuses,
    MAX(error_message) as latest_error
FROM sync_records
WHERE target_id IS NULL
    AND status != 'skipped'
GROUP BY source_id, source_type, target_type
HAVING COUNT(*) >= 3  -- Al menos 3 intentos fallidos
ORDER BY attempt_count DESC, last_attempt DESC;


