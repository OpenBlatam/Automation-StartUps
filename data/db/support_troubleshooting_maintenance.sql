-- ============================================================================
-- Script de Mantenimiento Automático para Troubleshooting
-- ============================================================================
-- Ejecutar este script periódicamente (recomendado: diario vía cron o pg_cron)
-- ============================================================================

-- Refresh vistas materializadas (recomendado: cada hora)
SELECT refresh_troubleshooting_views();

-- Limpiar cache expirado (recomendado: cada hora)
SELECT cleanup_expired_cache();

-- Ejecutar mantenimiento completo (recomendado: diario)
SELECT * FROM maintenance_troubleshooting_tables();

-- Vacuum y Analyze (recomendado: semanal)
-- Nota: Ejecutar manualmente o con pg_cron
-- VACUUM ANALYZE support_troubleshooting_sessions;
-- VACUUM ANALYZE support_troubleshooting_attempts;
-- VACUUM ANALYZE support_troubleshooting_feedback;

-- ============================================================================
-- Configurar pg_cron para ejecución automática (si está disponible)
-- ============================================================================

-- Refresh vistas cada hora
-- SELECT cron.schedule('refresh-troubleshooting-views', '0 * * * *', 
--     'SELECT refresh_troubleshooting_views();');

-- Limpiar cache cada hora
-- SELECT cron.schedule('cleanup-troubleshooting-cache', '0 * * * *', 
--     'SELECT cleanup_expired_cache();');

-- Mantenimiento diario a las 2 AM
-- SELECT cron.schedule('maintenance-troubleshooting', '0 2 * * *', 
--     'SELECT * FROM maintenance_troubleshooting_tables();');

-- Vacuum semanal los domingos a las 3 AM
-- SELECT cron.schedule('vacuum-troubleshooting', '0 3 * * 0', 
--     'VACUUM ANALYZE support_troubleshooting_sessions; VACUUM ANALYZE support_troubleshooting_attempts;');



