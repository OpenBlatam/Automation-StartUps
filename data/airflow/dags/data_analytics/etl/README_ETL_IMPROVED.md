# ETL Mejorado - Documentación

## Resumen

El DAG `etl_improved` es un pipeline ETL robusto con características avanzadas de observabilidad, validación de datos y manejo de errores.

## Características Principales

- **Idempotencia**: Upsert por clave primaria garantiza ejecuciones seguras
- **Validación de datos**: Validación básica + opcional Great Expectations
- **Chunking paralelo**: Procesamiento en paralelo con TaskFlow mapping
- **Retries inteligentes**: Backoff exponencial con clasificación de errores transitorios
- **Dry-run mode**: Ejecución sin escritura a BD para testing
- **Observabilidad**: Métricas en Stats, MLflow, y tablas Postgres
- **Alertas**: Notificaciones Slack en fallos y SLA misses
- **Dataset lineage**: Integración con Airflow Datasets para triggers

## Parámetros

### DAG Parameters (pueden sobrescribirse vía UI o Variables)

- `batch_size` (default: 500): Número de registros a extraer
- `run_label` (default: "etl_improved"): Etiqueta para identificar corridas
- `chunk_size` (default: 500): Tamaño de chunks para procesamiento paralelo
- `schema_name` (default: "public"): Schema de destino
- `table_name` (default: "etl_improved_events"): Tabla principal
- `audit_table_name` (default: "etl_improved_audit"): Tabla de auditoría
- `min_acceptance_ratio` (default: 1.0): Ratio mínimo aceptable (finalize falla si ratio < este valor)
- `enforce_ge` (default: False): Si True, requiere Great Expectations disponible
- `mlflow_enable` (default: False): Habilitar logging a MLflow
- `mlflow_experiment` (default: "etl_improved"): Nombre del experimento MLflow
- `dry_run` (default: False): Si True, no escribe a BD pero ejecuta todo el pipeline
- `db_statement_timeout_ms` (default: 0): Timeout de sentencias SQL (0 = sin límite)
- `db_max_retries` (default: 3): Intentos máximos para errores transitorios
- `db_retry_initial_ms` (default: 200): Delay inicial (ms) para backoff exponencial
- `db_page_size` (default: 1000): Tamaño de página para execute_values

### Variables de Airflow (fallback si params no están)

Todas las anteriores con prefijo `etl_improved__`, ej: `etl_improved__batch_size`

## Setup Inicial

### Base de Datos

#### Setup Nuevo

Ejecuta el script de setup para crear todas las tablas, vistas y funciones necesarias:

```bash
psql $KPIS_PG_DSN -f data/db/etl_setup.sql
```

O desde Python/psycopg:

```python
with open('data/db/etl_setup.sql') as f:
    sql = f.read()
conn.execute(sql)
```

El script es idempotente (safe to re-run) y crea:
- Tablas: `etl_improved_events`, `etl_improved_audit`, `etl_improved_metrics`, `etl_improved_alerts`
- Materialized views: `mv_etl_metrics_daily`, `mv_etl_alerts_daily`
- Función: `refresh_etl_mvs()`
- Views helper: `v_etl_latest_metrics`, `v_etl_recent_alerts`
- Índices necesarios

#### Migración desde Instalación Existente

Si ya tienes una instalación existente del ETL, ejecuta el script de migración después del setup:

```bash
psql $KPIS_PG_DSN -f data/db/etl_migration.sql
```

Este script:
- Agrega columnas faltantes (ej: `dry_run`)
- Crea índices adicionales para mejor performance
- Crea o actualiza views helper
- Crea materialized views si no existen
- Refresca vistas con datos existentes

**Nota**: Ejecuta primero `etl_setup.sql`, luego `etl_migration.sql` si tienes datos existentes.

### Backup y Restore

Scripts para backup y restore de tablas del ETL:

**Backup**:
```bash
export KPIS_PG_DSN="postgresql://user:pass@host:5432/db"
export BACKUP_DIR="./backups"  # opcional
export KEEP_BACKUPS=7  # opcional, número de backups a retener
./data/db/etl_backup.sh
```

El script crea backups comprimidos en `BACKUP_DIR` con formato `etl_backup_YYYYMMDD_HHMMSS.sql.gz`.

**Restore**:
```bash
export KPIS_PG_DSN="postgresql://user:pass@host:5432/db"
./data/db/etl_restore.sh backups/etl_backup_20250115_120000.sql.gz
```

**Nota**: El restore requiere confirmación y reemplazará datos existentes. Los materialized views se refrescan automáticamente después del restore.

### Checklist de Deployment

Para deployment en producción, sigue el checklist completo:

**Ver**: `data/airflow/dags/DEPLOYMENT_CHECKLIST.md`

Incluye:
- Pre-deployment (BD, variables, dependencias)
- Primera ejecución y validación
- Configuración de observabilidad
- Monitoreo continuo
- Plan de rollback

## Configuración

### Variables de Entorno

- `KPIS_PG_DSN`: Connection string PostgreSQL (usado por `plugins.db.get_conn()`)
- `SLACK_WEBHOOK`: URL webhook de Slack (fallback si no hay provider)
- `SLACK_CONN_ID`: ID de conexión Airflow para Slack provider (default: "slack_default")
- `MLFLOW_TRACKING_URI`: URI del servidor MLflow
- `ETL_POOL`: Nombre del pool de Airflow (opcional, para limitar concurrencia)

### Dependencias Opcionales

- `polars`: Acelera transformación (fallback a Python si no está)
- `pydantic`: Validación de esquemas (opcional, no bloquea si falta)
- `great_expectations`: Validación avanzada (opcional, solo requerido si `enforce_ge=True`)
- `mlflow`: Tracking de experimentos (opcional)
- `airflow.providers.slack`: Notificaciones nativas (fallback a webhook si no está)

## Uso

### Ejecución Normal

```bash
# Trigger desde UI o CLI
airflow dags trigger etl_improved \
  --conf '{"batch_size": 1000, "run_label": "daily_prod"}'
```

### Dry-run (Testing)

```bash
airflow dags trigger etl_improved \
  --conf '{"dry_run": true, "batch_size": 100}'
```

### Ejecución con Great Expectations Obligatorio

```bash
airflow dags trigger etl_improved \
  --conf '{"enforce_ge": true, "batch_size": 500}'
```

## Estructura de Tareas

1. **extract**: Extrae registros determinísticos (idempotentes)
2. **transform**: Enriquece y calcula fingerprints (usa Polars si disponible)
3. **chunk**: Divide en chunks para paralelización
4. **validate**: Validación básica (expandida por chunk)
5. **ge_validate**: Validación Great Expectations opcional (expandida)
6. **load**: Upsert idempotente a Postgres (expandida, con retries)
7. **finalize**: Verifica ratio y persiste métricas

## Tablas Creadas

- `{schema}.{table_name}`: Tabla principal con eventos
- `{schema}.{audit_table_name}`: Log de corridas
- `{schema}.etl_improved_metrics`: Métricas históricas
- `public.etl_improved_alerts`: Alertas generadas (por consumer)

## Monitoreo

### Dashboard Next.js

Accede a `/etl` en la app Next.js para ver:
- Métricas más recientes
- Histórico con filtros
- Gráfico de ratio histórico
- Alertas recientes

### API Endpoints

- `GET /api/metrics/latest`: Última métrica
- `GET /api/metrics/history?limit=30&start=...&end=...&run_label=...&dry_run=...&format=csv`: Histórico con filtros
- `GET /api/alerts/recent`: Últimas 50 alertas
- `GET /api/etl/health`: Healthcheck del ETL (conectividad, tablas, última corrida, vistas)
- `GET /api/etl/metrics`: Métricas en formato Prometheus (text/plain) para scraping

### Grafana

Usa las materialized views:
- `mv_etl_metrics_daily`: Agregaciones diarias
- `mv_etl_alerts_daily`: Alertas por día/tipo

Refrescadas automáticamente por `etl_consumer` tras cada corrida.

### Prometheus

El endpoint `/api/etl/metrics` exporta métricas en formato Prometheus.

**Configuración ServiceMonitor (Kubernetes):**

Usa el ServiceMonitor en `observability/servicemonitors/etl-metrics.yaml`:

```bash
kubectl apply -f observability/servicemonitors/etl-metrics.yaml
```

**Configuración manual (Prometheus raw config):**

Ver ejemplo en `observability/prometheus/etl-scrape-example.yaml`.

**Métricas exportadas:**

- Gauges de última corrida: `etl_latest_*` (total_rows, expected_rows, ratio, num_chunks, run_age_seconds, dry_run)
- Métricas diarias: `etl_daily_*{day="YYYY-MM-DD"}` (runs, total_rows, ratio_avg, low_ratio_count)
- Alertas 24h: `etl_alerts_24h_count{kind="..."}`
- Estadísticas globales: `etl_total_runs_all_time`, `etl_low_ratio_runs_all_time`, `etl_avg_ratio_all_time`

## DAG Consumidor

`etl_consumer` se dispara automáticamente cuando `etl_improved` completa (via Dataset).

Funciones:
- Resume métricas más recientes
- Detecta ratios bajos y caídas de tendencia
- Envía alertas a Slack
- Persiste eventos de alerta
- Refresca materialized views

## DAG Downstream (Ejemplo)

`etl_downstream_example` es un ejemplo de cómo crear pipelines que se ejecutan automáticamente cuando el ETL completa.

**Schedule**: Triggered por Dataset (`postgres://etl_improved/etl_improved_events`)

**Funciones**:
- Lee métricas más recientes del ETL
- Realiza análisis de eventos (agregaciones, estadísticas)
- Genera reportes basados en métricas y análisis
- Limpieza opcional de datos temporales

**Parámetros**:
- `analysis_type` (default: "daily_summary"): Tipo de análisis a realizar
- `top_n` (default: 10): Número de resultados a retornar

**Uso como plantilla**: Este DAG puede ser copiado y modificado para crear pipelines downstream personalizados que se ejecuten automáticamente cuando el ETL completa.

## DAG de Mantenimiento

`etl_maintenance` ejecuta limpieza semanal de datos antiguos para mantener el tamaño de la BD bajo control.

**Schedule**: `@weekly` (ejecuta cada semana)

**Parámetros**:
- `retention_days_metrics` (default: 90): Días a retener en `etl_improved_metrics`
- `retention_days_audit` (default: 90): Días a retener en `etl_improved_audit`
- `retention_days_alerts` (default: 180): Días a retener en `etl_improved_alerts`
- `retention_days_events` (default: 365): Días a retener en `etl_improved_events`

**Tareas**:
1. `clean_old_metrics`: Elimina métricas antiguas
2. `clean_old_audit`: Elimina registros de auditoría antiguos
3. `clean_old_alerts`: Elimina alertas antiguas
4. `clean_old_events`: Elimina eventos antiguos
5. `refresh_mvs`: Refresca materialized views tras limpieza
6. `vacuum_analyze`: Ejecuta VACUUM ANALYZE para reclaimar espacio

**Uso**:

```bash
# Ejecutar manualmente con retention personalizado
airflow dags trigger etl_maintenance \
  --conf '{"retention_days_metrics": 60, "retention_days_events": 180}'
```

## Troubleshooting

### Error: "plugins.db.get_conn not available"
- Verifica que `KPIS_PG_DSN` esté configurado
- Verifica que el plugin `plugins.db` esté en PYTHONPATH

### Error: "Great Expectations validation failed"
- Revisa logs de `ge_validate` para detalles
- Desactiva `enforce_ge` si GE no es requerido

### Ratio < 1.0
- Revisa logs de `extract` y `transform`
- Verifica que `batch_size` coincida con datos reales
- Ajusta `min_acceptance_ratio` si es aceptable un ratio menor

### SLA Miss
- Revisa `load` task logs
- Verifica performance de BD
- Ajusta `chunk_size` si hay mucha carga

