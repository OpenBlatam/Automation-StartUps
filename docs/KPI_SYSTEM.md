# Sistema de KPIs Automatizado

## Resumen Ejecutivo

Sistema completo de dashboards automáticos, reportes programados, alertas de KPIs críticos y visualización de métricas en tiempo real.

### Resumen de Componentes

| Componente | Ubicación | Frecuencia | Función Principal |
|------------|-----------|------------|-------------------|
| **Vistas Materializadas** | `data/db/materialized_views.sql` | Auto-refresh cada 4h | KPIs agregados diarios, series temporales, segmentación |
| **DAG: Reportes Diarios** | `kpi_reports` | Diario 08:00 UTC | CSV export, Slack summary, Prometheus metrics, anomalías |
| **DAG: Reportes Semanales** | `kpi_reports_weekly` | Lunes 09:00 UTC | HTML comparativo 7/28d, Slack |
| **DAG: Reportes Mensuales** | `kpi_reports_monthly` | Día 1, 09:00 UTC | HTML tendencias mensuales, top fuentes/países, Slack |
| **DAG: Auto-refresh** | `kpi_refresh_materialized` | Cada 4h (configurable) | Refresh concurrente de vistas |
| **DAG: Health Checks** | `kpi_dq_health_checks` | Cada 6h | Verificación de frescura, nulos, consistencia |
| **DAG: Performance** | `kpi_query_performance` | Cada 30min | Métricas de latencia de queries |
| **Alertas Prometheus** | `observability/prometheus/alertrules.yaml` | Continuo | Alertas por umbrales (leads, revenue, pagos, segmentos) |
| **Alertas Grafana Backup** | `observability/grafana/alerts/kpi_backup_postgres.json` | Cada 1min | Alertas redundantes desde Postgres |
| **Dashboard Grafana** | `observability/grafana/dashboards/kpi.json` | Tiempo real (10s refresh) | Visualización completa con calidad de datos y performance |
| **Dashboard Web** | `web/kpis-next/` | Tiempo real (SSE + fallback) | Interfaz web con actualizaciones en tiempo real |

## Componentes

### 1. Vistas Materializadas (`data/db/materialized_views.sql`)

- `mv_kpi_daily`: KPIs diarios agregados (últimos 120 días)
  - Leads, conversión, revenue, éxito de pagos
- `mv_kpi_timeseries_90d`: Series temporales de 90 días
- `mv_kpi_daily_segment`: KPIs segmentados por `country/source`

**Índices optimizados**: 
- Índices en vistas materializadas para filtros por fecha y agregaciones
- Índices en tablas base (`payments`, `leads`) para acelerar refreshes
- Índices parciales (WHERE clauses) para queries comunes

**Uso**: Ejecutar en Postgres y refrescar periódicamente (ver DAG `kpi_refresh_materialized`).

### 2. DAGs de Airflow

#### `kpi_reports` (Diario, 08:00 UTC)
- Exporta CSV de últimos 30 días
- Sube CSV a S3 o ADLS (Azure) si está configurado
- Resumen en Slack con métricas del día
- Publica métricas a Prometheus Pushgateway
- Trackea métricas a MLflow si `MLFLOW_TRACKING_URI` está configurado
- Detecta anomalías (z-score, ratio vs promedio) y alerta

#### `kpi_reports_weekly` (Lunes, 09:00 UTC)
- Genera HTML con comparativas 7/28 días
- Sube HTML a S3 o ADLS (Azure) si está configurado
- Notifica resumen en Slack

#### `kpi_reports_monthly` (Día 1 de cada mes, 09:00 UTC)
- Genera HTML con tendencias mensuales y comparativas mes anterior
- Top 5 fuentes y países por revenue (del mes anterior)
- Sube HTML a S3 o ADLS (Azure) si está configurado
- Notifica resumen ejecutivo en Slack

#### `kpi_refresh_materialized` (Programado: cada 4 horas, configurable)
- Refresca vistas materializadas concurrentemente
- Opcional: `ANALYZE` después del refresh (`KPI_ANALYZE_AFTER_REFRESH=1`)
- Schedule configurable via `KPI_REFRESH_SCHEDULE` (default: `0 */4 * * *`)

#### `kpi_dq_health_checks` (Programado: cada 6 horas)
- Verifica frescura de datos (lag, datos faltantes)
- Detecta tasas de nulos elevadas
- Valida consistencia de datos (rangos válidos)
- Verifica tamaños de vistas (empty/unusual)
- Notifica en Slack si hay problemas

#### `kpi_query_performance` (Programado: cada 30 minutos)
- Mide latencia de queries comunes a vistas materializadas
- Detecta queries lentas (>500ms) y registra en logs
- Proporciona métricas de performance para optimización

### 3. Alertas Prometheus (`observability/prometheus/alertrules.yaml`)

Reglas configuradas:
- `LowDailyLeads`: Leads < 50 por 15m → critical
- `LowRevenueVsAvg7d`: Revenue hoy < 70% promedio 7d por 30m → critical
- `LowPaymentSuccessRate`: Éxito pagos < 92% por 15m → warning
- `LowRevenueBySegment`: Revenue por segmento (country/source) < 70% promedio 7d por 30m → warning
- `LowLeadsBySegment`: Leads por segmento < 20 por 15m → warning

**Requisito**: Métricas publicadas vía Pushgateway desde `kpi_reports` (`PUSHGATEWAY_URL`). Las métricas por segmento se publican automáticamente para los top 10 segmentos por revenue.

### 3b. Alertas Backup Grafana (Postgres Directo)

Archivo: `observability/grafana/alerts/kpi_backup_postgres.json`

Alertas redundantes que consultan Postgres directamente como backup si Prometheus falla:
- `LowDailyLeads (Postgres Backup)`: Leads < 50 por 15m
- `LowRevenueVsAvg7d (Postgres Backup)`: Revenue hoy < 70% promedio 7d por 30m
- `LowPaymentSuccessRate (Postgres Backup)`: Éxito pagos < 92% por 15m
- `LowRevenueBySegment (Postgres Backup)`: Revenue por segmento < 70% promedio 7d por 30m (detecta automáticamente todos los segmentos)

**Uso**: 
1. Via Grafana UI: Ir a Alerting → Alert rules → New alert rule → Import JSON → pegar contenido de `kpi_backup_postgres.json`
2. Via API: `POST /api/v1/provisioning/alert-rules` con el JSON como body (requiere permisos de admin/alerting)

**Ventaja**: Funcionan independientemente de Prometheus, consultando Postgres directamente cada 1 minuto. Las alertas por segmento evalúan todos los segmentos activos automáticamente.

### 4. Dashboard Grafana (`observability/grafana/dashboards/kpi.json`)

Paneles incluidos:
- Ingresos última hora / 24h
- Leads por prioridad (hoy)
- Conversión leads→pagos (7d)
- Revenue por hora (24h)
- Revenue diario (90d)
- Revenue diario segmentado (country/source)
- Éxito de pagos (hoy)
- Tablas de pagos/leads recientes
- **Calidad de datos**: Frescura (días atrás), Nulls revenue (%), Tabla de estado de vistas
- Métricas de infraestructura (5xx, reinicios pods)

**Variables**: `country`, `source` (filtros opcionales)

**Paneles de calidad de datos**:
- Frescura: muestra días de retraso de los datos (verde/amarillo/rojo según thresholds)
- Nulls revenue: porcentaje de nulos en últimos 7 días
- Tabla de calidad: estado de todas las vistas materializadas (rows, max_day, days_behind)

**Paneles de performance**:
- Query latency (Daily View): latencia de queries a `mv_kpi_daily` (verde<100ms, amarillo<500ms, rojo≥500ms)
- Query latency (Segment View): latencia de queries a `mv_kpi_daily_segment`
- Query Latency Trends: evolución de latencias en 24h

### 5. Dashboard Web (`web/kpis-next/`)

- SSE (Server-Sent Events) para actualizaciones en tiempo real
- Fallback automático a polling cada 10s si SSE falla
- Endpoints:
  - `/api/kpi/summary`: Resumen actual
  - `/api/kpi/timeseries`: Series 24h
  - `/api/kpi/events`: SSE stream (actualizaciones cada 10s)
  - `/api/kpi/query`: **API REST consolidada con filtros avanzados**

#### API Query (`/api/kpi/query`)

Endpoint flexible para consultar KPIs con múltiples opciones:

**Parámetros de query:**
- `metric`: `revenue` | `leads` | `conversion_pct` | `payments_success_rate` (opcional, default: todos)
- `start_date`: ISO date o `today` | `7d` | `30d` | `90d` (default: `7d`)
- `end_date`: ISO date (default: hoy)
- `country`: filtrar por país
- `source`: filtrar por fuente
- `aggregate`: `daily` | `weekly` | `monthly` (default: `daily`)
- `limit`: máximo de filas (default: 1000)

**Ejemplos:**
```bash
# Revenue últimos 30 días agregado por semana
GET /api/kpi/query?metric=revenue&start_date=30d&aggregate=weekly

# Todos los KPIs de un país específico
GET /api/kpi/query?country=Mexico&start_date=7d

# Leads de una fuente específica, agregado mensual
GET /api/kpi/query?metric=leads&source=google&start_date=90d&aggregate=monthly

# Revenue de un segmento específico
GET /api/kpi/query?metric=revenue&country=USA&source=facebook&start_date=30d
```

**Respuesta:**
```json
{
  "data": [...],
  "params": {...},
  "count": 42,
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z"
}
```

## Configuración

### Variables de Entorno Requeridas

#### Airflow DAGs
```bash
# Base de datos
KPIS_PG_DSN=postgresql://user:pass@host:5432/dbname

# Slack (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
ENABLE_SLACK=1

# Pushgateway (para alertas Prometheus)
PUSHGATEWAY_URL=http://pushgateway:9091

# Reportes (opcional)
KPI_REPORTS_DIR=/tmp
KPI_ANALYZE_AFTER_REFRESH=1

# S3 export (opcional)
KPI_REPORTS_S3_BUCKET=your-bucket-name
KPI_REPORTS_S3_PREFIX=reports/daily  # Para semanal/mensual usa reports/weekly o reports/monthly

# ADLS (Azure Data Lake Storage) export (opcional, alternativa a S3)
KPI_REPORTS_ADLS_SHARE=your-file-share-name
KPI_REPORTS_ADLS_PATH=reports/daily  # Para semanal/mensual usa reports/weekly o reports/monthly
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...

# Auto-refresh schedule (opcional)
KPI_REFRESH_SCHEDULE=0 */4 * * *  # Default: cada 4 horas (cron format)
```

#### Next.js (`web/kpis-next/`)
```bash
KPIS_PG_HOST=localhost
KPIS_PG_DB=analytics
KPIS_PG_USER=analytics
KPIS_PG_PASSWORD=...
KPIS_PG_PORT=5432
KPIS_PG_POOL=10
KPIS_PG_STMT_TIMEOUT_MS=5000
```

#### Grafana
- Datasource Postgres configurado como `KPIs-Postgres`
- Datasource Prometheus configurado como `prometheus`

## Setup Rápido

1. **Migraciones DB**: Ejecutar `data/db/materialized_views.sql` en Postgres
2. **Airflow**: Los DAGs se cargan automáticamente si están en `data/airflow/dags/`
3. **Grafana**: Importar `observability/grafana/dashboards/kpi.json`
4. **Web**: `cd web/kpis-next && npm install && npm run dev`

## Operación

### Refrescar Vistas Materializadas
```bash
# Manual desde Airflow UI
Trigger DAG: kpi_refresh_materialized

# O programar en cron/kubernetes job
```

### Revisar Alertas
- Prometheus: `/alerts` endpoint o Grafana Alerting UI
- Grafana: Configurar alertas basadas en queries Postgres (backup si Prometheus falla)

### Troubleshooting

- **Vistas desactualizadas**: Ejecutar `kpi_refresh_materialized`
- **Alertas no disparan**: Verificar `PUSHGATEWAY_URL` y que Prometheus scrape Pushgateway
- **SSE no funciona**: Revisar logs de Next.js; fallback a polling debería activarse automáticamente
- **Slack no recibe notificaciones**: Verificar `SLACK_WEBHOOK_URL` y `ENABLE_SLACK`

## Configuración por Ambiente

Los thresholds y schedules se configuran en `environments/{dev,stg,prod}.yaml`:

```yaml
kpi:
  thresholds:
    leads_critical: 50  # Umbral crítico de leads diarios
    leads_warning: 80
    revenue_vs_avg7d_critical: 0.7  # 70% del promedio 7d
    revenue_vs_avg7d_warning: 0.85
    payment_success_critical: 92
    payment_success_warning: 95
  refresh_schedule: "0 */4 * * *"  # Schedule del refresh (cron)
  dq_health_schedule: "0 */6 * * *"  # Schedule de health checks
```

**Diferencias por ambiente**:
- **dev**: Thresholds más permisivos, schedules menos frecuentes
- **stg**: Thresholds intermedios, similar a prod
- **prod**: Thresholds estrictos, schedules frecuentes

## Flujo de Datos Completo

```
┌─────────────────┐
│  Source Tables  │  (payments, leads)
│  Postgres DB    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Materialized Views      │  (mv_kpi_daily, mv_kpi_daily_segment, etc.)
│ Refreshed cada 4h       │
└────────┬────────────────┘
         │
         ├─────────────────────────────────────────────────┐
         │                                                 │
         ▼                                                 ▼
┌──────────────────┐                            ┌────────────────────┐
│  Airflow DAGs    │                            │  Dashboards        │
│  - Reports       │                            │  - Grafana         │
│  - Health Checks │                            │  - Web (Next.js)   │
│  - Performance   │                            └────────────────────┘
└────────┬─────────┘
         │
         ├──────────────┬──────────────┬────────────────┐
         ▼              ▼              ▼                ▼
┌─────────────┐ ┌──────────┐ ┌──────────────┐ ┌─────────────┐
│ CSV/HTML    │ │  Slack   │ │ Prometheus   │ │  S3/ADLS    │
│ Reports     │ │  Alerts  │ │  Metrics     │ │  Storage    │
└─────────────┘ └──────────┘ └──────────────┘ └─────────────┘
```

## Próximas Mejoras Sugeridas

- Realtime con Postgres `LISTEN/NOTIFY` para SSE instantáneo cuando hay nuevos pagos/leads
- Alertas avanzadas por segmento con umbrales dinámicos basados en percentiles
- Machine Learning para detección de anomalías más sofisticada
- Exportación a Google Sheets/Excel para usuarios no técnicos

