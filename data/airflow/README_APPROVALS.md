# Sistema de Aprobaciones - Guía Completa

Sistema completo de automatización de aprobaciones internas con monitoreo, reportes y mantenimiento.

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Componentes del Sistema](#-componentes-del-sistema)
- [DAGs Disponibles](#-dags-disponibles)
- [Monitoreo y Alertas](#-monitoreo-y-alertas)
- [Reportes](#-reportes)
- [Mantenimiento](#-mantenimiento)
- [CLI de Gestión](#-cli-de-gestión)
- [Configuración](#-configuración)

## 🎯 Descripción General

El sistema de aprobaciones automatiza la gestión de solicitudes internas (vacaciones, gastos, documentos) con:

- ✅ **Aprobaciones automáticas** basadas en reglas configurables
- ✅ **Flujos multi-nivel** según criticidad y monto
- ✅ **Monitoreo en tiempo real** de aprobaciones pendientes
- ✅ **Alertas automáticas** para timeouts y prioridades altas
- ✅ **Reportes diarios y semanales** de métricas
- ✅ **Recordatorios automáticos** para aprobadores
- ✅ **Limpieza y mantenimiento** automatizado

## 🏗️ Componentes del Sistema

### 1. Base de Datos

Schema completo en `data/db/approvals_schema.sql` con:
- `approval_users`: Usuarios y roles
- `approval_requests`: Solicitudes principales
- `approval_rules`: Reglas de auto-aprobación
- `approval_chains`: Cadenas de aprobación multi-nivel
- `approval_history`: Historial de auditoría
- `approval_notifications`: Notificaciones enviadas

### 2. DAGs de Airflow

#### `approval_cleanup` - Limpieza y Mantenimiento
- **Schedule**: Domingos a las 2 AM
- **Funciones**:
  - Archivar solicitudes completadas antiguas (> 1 año)
  - Limpiar notificaciones antiguas (> 6 meses)
  - Identificar solicitudes pendientes antiguas (> 90 días)
  - Optimizar índices (ANALYZE)
  - Refrescar vistas materializadas
  - Vacuum de tablas principales
  - Generar reporte de limpieza

**Parámetros**:
```json
{
  "archive_retention_years": 1,
  "notification_retention_months": 6,
  "dry_run": false,
  "notify_on_completion": true
}
```

#### `approval_monitoring` - Monitoreo y Alertas
- **Schedule**: Cada 30 minutos
- **Funciones**:
  - Verificar aprobaciones próximas a timeout (< 24 horas)
  - Identificar aprobaciones expiradas
  - Detectar solicitudes pendientes antiguas (> 30 días)
  - Monitorear aprobaciones de alta prioridad
  - Enviar alertas a Slack según condiciones

**Alertas enviadas**:
- ⚠️ Aprobaciones expiradas
- ⏰ Aprobaciones urgentes próximas a expirar (< 2 horas)
- 🔴 Solicitudes muy antiguas (> 60 días)
- 🚨 Aprobaciones urgentes pendientes > 24 horas

#### `approval_reports_daily` - Reportes Diarios
- **Schedule**: Cada día a las 8 AM
- **Métricas**:
  - Total de solicitudes por estado
  - Solicitudes enviadas y completadas
  - Tiempo promedio de completación
  - Desglose por tipo de solicitud
  - Top aprobadores del día

#### `approval_reports_weekly` - Reportes Semanales
- **Schedule**: Lunes a las 9 AM
- **Métricas**:
  - Resumen de la semana
  - Tasa de aprobación
  - Tiempo promedio de completación
  - Desglose diario
  - Métricas por tipo de solicitud

#### `approval_reminders` - Recordatorios
- **Schedule**: 9 AM, 2 PM, 5 PM (lunes a viernes)
- **Funciones**:
  - Enviar recordatorios a aprobadores
  - Notificar aprobaciones pendientes no notificadas en 24h
  - Priorizar por urgencia y timeout
  - Actualizar timestamp de notificación

#### `approval_analytics` - Análisis Avanzado
- **Schedule**: Cada lunes a las 10 AM
- **Funciones**:
  - Analizar patrones de aprobación (día, hora, aprobador)
  - Detectar cuellos de botella
  - Calcular recomendaciones de optimización
  - Enviar alertas para problemas críticos

#### `approval_health_check` - Verificación de Salud
- **Schedule**: Cada 6 horas
- **Funciones**:
  - Verificar integridad de datos
  - Verificar salud del sistema (tablas, índices, conexiones)
  - Detectar problemas y warnings
  - Enviar reportes de salud

#### `approval_export` - Exportación de Datos
- **Schedule**: Cada lunes a las 3 AM
- **Funciones**:
  - Exportar solicitudes de aprobación (JSON/CSV)
  - Exportar cadenas de aprobación (JSON/CSV)
  - Exportar resumen de métricas (JSON)
  - Generar reporte de exportación

## 📊 Monitoreo y Alertas

### Consultar Aprobaciones Pendientes

```sql
-- Por aprobador
SELECT 
    ar.title,
    ar.request_type,
    ar.requester_email,
    ar.priority,
    ac.timeout_date,
    EXTRACT(EPOCH FROM (ac.timeout_date - NOW())) / 3600 as hours_until_timeout
FROM approval_chains ac
JOIN approval_requests ar ON ac.request_id = ar.id
WHERE ac.status = 'pending'
  AND ac.approver_email = 'approver@example.com'
ORDER BY ar.priority DESC, ac.timeout_date ASC;
```

### Verificar Timeouts Próximos

```sql
SELECT 
    ar.title,
    ac.approver_email,
    ac.timeout_date,
    EXTRACT(EPOCH FROM (ac.timeout_date - NOW())) / 3600 as hours_until_timeout
FROM approval_chains ac
JOIN approval_requests ar ON ac.request_id = ar.id
WHERE ac.status = 'pending'
  AND ac.timeout_date IS NOT NULL
  AND ac.timeout_date <= NOW() + INTERVAL '24 hours'
ORDER BY ac.timeout_date ASC;
```

## 📈 Reportes

### Métricas Disponibles

- Total de solicitudes
- Tasa de aprobación/rechazo
- Tiempo promedio de completación
- Solicitudes por tipo
- Solicitudes por estado
- Aprobadores más activos
- Solicitudes pendientes antiguas

### Consultar Métricas Manualmente

```sql
-- Métricas del último mes
SELECT 
    request_type,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'approved') as approved,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) as avg_hours
FROM approval_requests
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY request_type;
```

## 🧹 Mantenimiento

### Limpieza Automática

El DAG `approval_cleanup` ejecuta automáticamente:

1. **Archivado**: Solicitudes completadas > 1 año
2. **Limpieza de notificaciones**: Notificaciones > 6 meses
3. **Identificación de stale**: Solicitudes pendientes > 90 días
4. **Optimización**: ANALYZE y VACUUM de tablas

### Modo Dry-Run

Para probar sin ejecutar cambios:

```json
{
  "dry_run": true,
  "archive_retention_years": 1,
  "notification_retention_months": 6
}
```

### Verificar Estado de Limpieza

```sql
-- Solicitudes antiguas pendientes de archivar
SELECT COUNT(*) 
FROM approval_requests
WHERE status IN ('approved', 'rejected', 'auto_approved')
  AND completed_at < NOW() - INTERVAL '1 year';

-- Notificaciones antiguas
SELECT COUNT(*) 
FROM approval_notifications
WHERE sent_at < NOW() - INTERVAL '6 months'
  AND status IN ('sent', 'delivered', 'read');
```

## 🛠️ CLI de Gestión

### Instalación

```bash
chmod +x scripts/approval_cli.py
```

### Uso

#### Ver estado de solicitud

```bash
python scripts/approval_cli.py status \
  --request-id "123e4567-e89b-12d3-a456-426614174000" \
  --db-url "jdbc:postgresql://localhost:5432/approvals" \
  --db-user "user" \
  --db-password "password"
```

#### Listar aprobaciones pendientes

```bash
python scripts/approval_cli.py list-pending \
  --approver-email "approver@example.com" \
  --limit 20 \
  --db-url "jdbc:postgresql://localhost:5432/approvals" \
  --db-user "user" \
  --db-password "password"
```

#### Ver estadísticas

```bash
python scripts/approval_cli.py stats \
  --db-url "jdbc:postgresql://localhost:5432/approvals" \
  --db-user "user" \
  --db-password "password"
```

#### Crear solicitud

```bash
python scripts/approval_cli.py create \
  --api-url "https://api.example.com" \
  --api-token "token" \
  --payload-file request.json
```

**request.json**:
```json
{
  "request_type": "vacation",
  "requester_email": "user@example.com",
  "title": "Vacation Request",
  "description": "Annual leave",
  "vacation_start_date": "2025-02-01",
  "vacation_end_date": "2025-02-05",
  "vacation_days": 5,
  "priority": "normal"
}
```

#### Aprobar solicitud

```bash
python scripts/approval_cli.py approve \
  --api-url "https://api.example.com" \
  --api-token "token" \
  --request-id "123e4567-e89b-12d3-a456-426614174000" \
  --approver-email "approver@example.com" \
  --comments "Approved"
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# Base de datos
APPROVALS_DB_CONN_ID=approvals_db

# Notificaciones (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Conexión de Base de Datos en Airflow

```bash
# Airflow UI → Admin → Connections → Add
Connection Id: approvals_db
Connection Type: Postgres
Host: your-postgres-host
Schema: approvals_db
Login: your_user
Password: your_password
Port: 5432
```

### Configuración de Notificaciones

El sistema usa `notify_slack` de `etl_notifications`. Asegúrate de tener configurado:

```python
# En plugins/etl_notifications.py
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
```

## 📚 Referencias

- Schema: `/data/db/approvals_schema.sql`
- DAG Limpieza: `/data/airflow/dags/approval_cleanup.py`
- DAG Monitoreo: `/data/airflow/dags/approval_monitoring.py`
- DAG Reportes: `/data/airflow/dags/approval_reports.py`
- DAG Recordatorios: `/data/airflow/dags/approval_reminders.py`
- DAG Analytics: `/data/airflow/dags/approval_analytics.py`
- DAG Health Check: `/data/airflow/dags/approval_health_check.py`
- DAG Export: `/data/airflow/dags/approval_export.py`
- CLI: `/scripts/approval_cli.py`
- Documentación Sistema: `/workflow/APPROVALS_SYSTEM.md`

## 🔍 Análisis Avanzado

### DAG `approval_analytics`

Análisis profundo del sistema de aprobaciones (ejecuta cada lunes a las 10 AM):

- **Análisis de patrones**:
  - Patrones por día de la semana
  - Patrones por hora del día
  - Rendimiento de aprobadores
  - Tiempo promedio por tipo y prioridad

- **Detección de cuellos de botella**:
  - Aprobadores con más aprobaciones pendientes
  - Tipos de solicitud más lentos
  - Cadenas de aprobación más largas

- **Recomendaciones de optimización**:
  - Sugerencias automáticas basadas en análisis
  - Priorización de mejoras (alta/media/baja)
  - Alertas para problemas críticos

### Ejemplo de Uso

```sql
-- Ver patrones de aprobación por día
SELECT 
    EXTRACT(DOW FROM submitted_at) as day_of_week,
    COUNT(*) as total,
    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) as avg_hours
FROM approval_requests
WHERE submitted_at >= NOW() - INTERVAL '90 days'
GROUP BY EXTRACT(DOW FROM submitted_at);
```

## 🏥 Health Check

### DAG `approval_health_check`

Verificación de salud del sistema (ejecuta cada 6 horas):

- **Verificación de integridad**:
  - Referencias huérfanas
  - Cadenas sin aprobador
  - Estados inconsistentes
  - Duplicados

- **Verificación de salud del sistema**:
  - Tamaño de tablas
  - Índices no utilizados
  - Conexiones activas
  - Locks esperando
  - Bloat de tablas

- **Alertas automáticas**:
  - Notifica problemas de alta severidad
  - Reporta warnings del sistema
  - Estado general de salud

### Consultar Estado de Salud

```sql
-- Verificar referencias huérfanas
SELECT COUNT(*) 
FROM approval_chains ac
LEFT JOIN approval_requests ar ON ac.request_id = ar.id
WHERE ar.id IS NULL;

-- Verificar bloat de tablas
SELECT 
    tablename,
    n_dead_tup,
    n_live_tup,
    ROUND((n_dead_tup::numeric / NULLIF(n_live_tup, 0)) * 100, 2) as dead_percent
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'approval%'
  AND n_dead_tup > 1000;
```

## 🚀 Próximas Mejoras

- [ ] Dashboard web de métricas
- [ ] Integración con más sistemas de notificación
- [ ] Machine learning para optimizar tiempos de aprobación
- [ ] Análisis predictivo de aprobaciones
- [ ] Exportación de reportes a múltiples formatos
- [ ] API REST completa para gestión de aprobaciones
- [ ] Visualización de flujos de aprobación
- [ ] Análisis de sentimiento en comentarios

