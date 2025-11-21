# 🔧 Guía de Troubleshooting del Sistema de Soporte

## Problemas Comunes y Soluciones

### 1. Chatbot no responde

**Síntomas:**
- Los tickets no se resuelven automáticamente
- No hay interacciones registradas en `support_chatbot_interactions`

**Diagnóstico:**
```sql
-- Verificar que hay FAQs activos
SELECT COUNT(*) FROM support_faq_articles WHERE is_active = true;

-- Verificar interacciones recientes
SELECT * FROM support_chatbot_interactions 
ORDER BY created_at DESC LIMIT 10;

-- Verificar configuración
SELECT ticket_id, chatbot_attempted, chatbot_resolved 
FROM support_tickets 
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

**Soluciones:**
1. Verificar que `enable_chatbot = true` en Kestra
2. Verificar API key de OpenAI si está habilitado
3. Cargar FAQs: `psql -d support_db -f data/db/support_faq_seed.sql`
4. Revisar logs de Kestra para errores

### 2. Priorización incorrecta

**Síntomas:**
- Tickets con prioridad incorrecta
- Scores de prioridad inconsistentes

**Diagnóstico:**
```sql
-- Ver factores de priorización
SELECT 
    ticket_id,
    priority,
    priority_score,
    urgency_factors
FROM support_tickets
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY priority_score DESC;
```

**Soluciones:**
1. Verificar configuración de VIP/Enterprise customers
2. Revisar keywords en `support_priority.py`
3. Ajustar pesos en cálculo de prioridad
4. Verificar análisis de sentimiento está habilitado

### 3. Enrutamiento no funciona

**Síntomas:**
- Tickets no se asignan a departamentos
- Agentes no reciben tickets

**Diagnóstico:**
```sql
-- Verificar reglas activas
SELECT * FROM support_routing_rules 
WHERE is_active = true 
ORDER BY priority_order;

-- Verificar agentes disponibles
SELECT * FROM support_agents 
WHERE is_available = true;

-- Ver tickets sin asignar
SELECT COUNT(*) FROM support_tickets
WHERE assigned_department IS NULL
AND status NOT IN ('resolved', 'closed', 'chatbot_handled');
```

**Soluciones:**
1. Verificar que hay reglas de enrutamiento activas
2. Verificar que hay agentes disponibles
3. Revisar condiciones de reglas en BD
4. Verificar que `enable_auto_routing = true`

### 4. Escalación no funciona

**Síntomas:**
- Tickets críticos no se escalan
- No hay cambios de prioridad automáticos

**Diagnóstico:**
```sql
-- Ver tickets que deberían escalarse
SELECT 
    ticket_id,
    priority,
    status,
    created_at,
    first_response_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_open
FROM support_tickets
WHERE priority IN ('critical', 'urgent')
AND status NOT IN ('resolved', 'closed')
AND created_at < NOW() - INTERVAL '30 minutes'
ORDER BY created_at ASC;

-- Ver historial de escalaciones
SELECT * FROM support_ticket_history
WHERE field_changed = 'escalation'
ORDER BY created_at DESC
LIMIT 10;
```

**Soluciones:**
1. Verificar que workflow de escalación está activo en Kestra
2. Verificar trigger schedule (debe ser cada 10 minutos)
3. Revisar logs del workflow de escalación
4. Verificar que hay agentes senior disponibles

### 5. Base de datos lenta

**Síntomas:**
- Queries lentas
- Timeouts en workflows

**Diagnóstico:**
```sql
-- Verificar índices
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename LIKE 'support_%';

-- Analizar tablas
ANALYZE support_tickets;
ANALYZE support_chatbot_interactions;
ANALYZE support_faq_articles;
```

**Soluciones:**
1. Ejecutar `ANALYZE` en tablas grandes
2. Verificar índices: `data/db/support_optimizations.sql`
3. Refresh vistas materializadas
4. Considerar particionado para tablas grandes

### 6. API REST no responde

**Síntomas:**
- Endpoints retornan error 500
- Timeouts en requests

**Diagnóstico:**
```bash
# Verificar conexión a BD
curl http://localhost:3000/api/support/tickets/stats

# Verificar logs de Next.js
# Revisar DATABASE_URL en variables de entorno
```

**Soluciones:**
1. Verificar `DATABASE_URL` está configurado
2. Verificar que PostgreSQL está accesible
3. Revisar logs de Next.js
4. Verificar permisos de usuario de BD

### 7. Notificaciones no se envían

**Síntomas:**
- No se reciben notificaciones de Slack/Email
- Tickets no notifican a agentes

**Diagnóstico:**
```sql
-- Verificar tickets recientes
SELECT 
    ticket_id,
    status,
    assigned_agent_id,
    created_at
FROM support_tickets
WHERE created_at >= NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

**Soluciones:**
1. Verificar webhook URLs en configuración
2. Verificar que `enable_notifications = true`
3. Probar webhook manualmente
4. Revisar logs de Kestra para errores de notificación

### 8. Monitoreo no funciona

**Síntomas:**
- DAG de monitoreo falla
- No hay métricas en Prometheus

**Diagnóstico:**
```bash
# Verificar DAG
airflow dags list-runs -d support_tickets_monitor

# Verificar última ejecución
airflow tasks list support_tickets_monitor

# Ver logs
airflow tasks logs support_tickets_monitor collect_ticket_metrics
```

**Soluciones:**
1. Verificar connection a BD en Airflow
2. Verificar variables de entorno
3. Verificar que DAG está activo
4. Revisar logs de Airflow

### 9. Feedback no se recopila

**Síntomas:**
- No se envían encuestas
- No hay feedback en BD

**Diagnóstico:**
```sql
-- Ver tickets resueltos sin feedback
SELECT 
    t.ticket_id,
    t.resolved_at,
    t.customer_email,
    f.id as feedback_id
FROM support_tickets t
LEFT JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
WHERE t.status = 'resolved'
AND t.resolved_at >= NOW() - INTERVAL '7 days'
AND f.id IS NULL;

-- Ver encuestas enviadas
SELECT * FROM support_satisfaction_surveys
WHERE submitted_at >= NOW() - INTERVAL '7 days'
ORDER BY submitted_at DESC;
```

**Soluciones:**
1. Verificar que workflow de feedback está activo
2. Verificar configuración de email API
3. Verificar que hay emails válidos en tickets
4. Revisar schedule del workflow (debe ser cada 6 horas)

### 10. Performance degradada

**Síntomas:**
- Sistema lento
- Timeouts frecuentes

**Soluciones:**
1. Ejecutar optimizaciones SQL: `data/db/support_optimizations.sql`
2. Refresh vistas materializadas
3. Verificar índices
4. Considerar cache en Redis
5. Ejecutar DAG de optimización semanal

## Comandos Útiles

### Health Check
```bash
python3 scripts/support_health_check.py
```

### Verificar Estado del Sistema
```sql
-- Resumen general
SELECT 
    (SELECT COUNT(*) FROM support_tickets WHERE status = 'open') as open_tickets,
    (SELECT COUNT(*) FROM support_tickets WHERE status = 'resolved') as resolved_tickets,
    (SELECT COUNT(*) FROM support_agents WHERE is_available = true) as available_agents,
    (SELECT COUNT(*) FROM support_faq_articles WHERE is_active = true) as active_faqs;
```

### Limpiar Datos de Prueba
```sql
-- Cuidado: Solo para desarrollo
DELETE FROM support_tickets WHERE customer_email LIKE '%test%';
DELETE FROM support_chatbot_interactions WHERE ticket_id IN (
    SELECT ticket_id FROM support_tickets WHERE customer_email LIKE '%test%'
);
```

### Resetear Estadísticas
```sql
-- Actualizar contadores de agentes
SELECT update_agent_statistics();

-- Refresh vistas materializadas
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_support_daily_metrics;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_support_agent_metrics;
```

## Logs Importantes

### Kestra
- Workflow logs: UI de Kestra → Executions → Logs
- Buscar por `support_ticket_automation`

### Airflow
- DAG logs: Airflow UI → DAGs → Logs
- Buscar por `support_tickets_*`

### Next.js
- Application logs: `npm run dev` output
- API logs: `/api/support/*` endpoints

### PostgreSQL
```sql
-- Ver queries lentas
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Contacto y Soporte

Para problemas adicionales:
1. Revisar documentación completa
2. Ejecutar health check
3. Revisar logs de todos los componentes
4. Verificar configuración de variables
5. Consultar con el equipo de desarrollo

