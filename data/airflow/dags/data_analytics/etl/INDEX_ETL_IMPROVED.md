# ETL Mejorado - Índice Ejecutivo

> **Versión**: 2.5 | **Última actualización**: 2025-01-15 | **Estado**: Producción Ready ✅

> **Mejoras en v2.5**:
> - ✅ **Anti-patterns Completos**: 10 anti-patterns comunes con ejemplos de código ❌ vs ✅, cubriendo validación, SQL injection, rate limiting, logging seguro, timeouts, chunks, circuit breakers y DQ
> - ✅ **Guía de Migración Detallada**: Proceso paso a paso para migrar DAGs legacy con checklist de evaluación, migración incremental (6 pasos), plantilla completa de código y testing post-migración
> - ✅ **Escalabilidad Avanzada**: Guías detalladas para HPA en Kubernetes, escalado vertical con tuning de memoria, particionamiento automático de DB, índices estratégicos y connection pooling optimizado
> - ✅ **Plugins Completados**: Creados etl_config.py, etl_callbacks.py, etl_tracing.py, etl_notifications.py con funcionalidad completa

> **Mejoras en v2.4**: 
> - ✅ **Seguridad avanzada**: Validación completa de parámetros DAG con Param, whitelists para operaciones críticas, logging seguro sin exponer secrets, prevención SQL injection con psycopg2.sql, validación de endpoints y URLs
> - ✅ **Escalabilidad detallada**: Guías completas de horizontal/vertical scaling con Kubernetes HPA, auto-scaling basado en métricas, optimización de DB con índices estratégicos, particionamiento automático, materialized views, connection pooling
> - ✅ **Optimización de costos**: Estrategias detalladas con cálculos de ROI, tuning inteligente de chunks, materialized views para pre-cálculo, limpieza proactiva con estimación de ahorro, rate limiting basado en costo de APIs, monitoreo de costos mensuales
> - ✅ **Ejemplos prácticos completos**: Código funcional para alto volumen (checkpointing), baja frecuencia (batching), escalado dinámico, estimación de costos
> - ✅ Sección Quick Start para nuevos desarrolladores y operaciones
> - ✅ Documentación completa de DAGs adicionales (financieros, outreach, KPIs)
> - ✅ Mejores prácticas avanzadas con ejemplos de código prácticos
> - ✅ Troubleshooting avanzado con guías paso a paso detalladas
> - ✅ Métricas clave y SLAs por tipo de DAG para monitoreo
> - ✅ Referencias cruzadas a documentación relacionada
> - ✅ Observabilidad mejorada: Prometheus, Grafana, ELK Stack integrados
> - ✅ ServiceMonitors para todos los componentes (Airflow, Kestra, Camunda, Flowable)
> - ✅ Dashboards de Grafana para monitoreo de automatizaciones
> - ✅ Alertas avanzadas de Prometheus para detección proactiva de fallos
> - ✅ Recolección centralizada de logs con Fluent Bit y ELK
> - ✅ Mejoras en troubleshooting y documentación de monitoreo

> **Mejoras en v2.3**: 
> - ✅ Mejoras de seguridad en `etl_maintenance.py` (whitelist de tablas, SQL seguro, validación de parámetros)
> - ✅ Documentación de mejoras recientes de Kestra flows y DAGs
> - ✅ Actualización de características mejoradas en todos los DAGs principales

## Tabla de Contenidos

- [Visión General](#visión-general)
- [DAGs Principales](#dags-principales)
  - [etl_example](#etl_example-mejorado)
  - [etl_improved](#etl_improved)
  - [etl_maintenance](#etl_maintenance)
  - [employee_onboarding](#employee_onboarding)
- [Workflows de Kestra](#workflows-de-kestra)
- [Plugins Mejorados](#plugins-mejorados)
- [Arquitectura de Observabilidad](#arquitectura-de-observabilidad)
- [Flujo de Datos](#flujo-de-datos-etl_example)
- [Configuración](#configuración)
- [Patrones de Diseño](#patrones-de-diseño)
- [Optimizaciones](#optimizaciones)
- [Casos de Uso](#casos-de-uso)
- [Comparación de DAGs](#comparación-de-dags)
- [Performance Benchmarks](#performance-benchmarks)
- [Seguridad y Compliance](#seguridad-y-compliance)
- [Disaster Recovery](#disaster-recovery)
- [Testing Strategy](#testing-strategy)
- [Versionado y Changelog](#versionado-y-changelog)
- [Checklist de Implementación](#checklist-de-implementación)
- [Checklist de Deployment](#checklist-de-deployment)
- [Monitoreo Proactivo](#monitoreo-proactivo)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Comandos Útiles](#comandos-útiles)
- [Referencias](#referencias)
- [Anti-patterns Comunes](#anti-patterns-comunes-y-cómo-evitarlos)
- [Guía de Migración](#guía-completa-de-migración-desde-dags-legacy)
- [Escalabilidad Avanzada](#escalabilidad-avanzada---guías-detalladas)

## Visión General

Sistema ETL enterprise-grade con observabilidad completa, validación robusta, rate limiting, circuit breakers y debugging avanzado. Diseñado para producción con alto throughput y resiliencia.

## DAGs Principales

### `etl_example` (Mejorado)
- **Archivo**: `data/airflow/dags/etl_example.py`
- **Schedule**: Triggered por Dataset (`dataset://source_ready`)
- **Características mejoradas**:
  - ✅ Validación de schema con `etl_validation`
  - ✅ Rate limiting para APIs externas (`@rate_limit`)
  - ✅ Circuit breaker con TTL configurable y auto-reset
  - ✅ Detección de anomalías de volumen (basado en 20 ejecuciones históricas)
  - ✅ Health check con diagnóstico de ambiente
  - ✅ Logging estructurado con correlación (`log_with_context`)
  - ✅ Métricas de performance (p50, p95, p99) y throughput (`rows_per_sec`)
  - ✅ Debugging avanzado (`debug_context`, `diagnose_task_environment`)
  - ✅ Idempotencia con TTL configurable por parámetro o ENV
  - ✅ Chunking adaptativo con límite `MAX_CHUNKS` y optimización automática
  - ✅ DQ checks configurable vía ENV/Variables con validación de null_rate
  - ✅ Validación de checksum para detectar cambios en datos
  - ✅ Notificaciones Slack en anomalías y resúmenes de ejecución
  - ✅ Dry run mode para testing sin efectos secundarios
  - ✅ Métricas de duración end-to-end del DAG
  - ✅ Dataset lineage completo (inlets/outlets en todas las tareas)

### `etl_improved`
- **Archivo**: `data/airflow/dags/etl_improved.py`
- **Schedule**: `@daily`
- **Función**: Pipeline ETL principal (extract → transform → validate → load)
- Características: Idempotencia, chunking paralelo, validación opcional con Great Expectations

### `employee_onboarding`
- **Archivo**: `data/airflow/dags/employee_onboarding.py`
- **Función**: Automatización de onboarding de empleados
- Características: Validación robusta, idempotencia con TTL, logging estructurado, integración HRIS/IdP

### `kpi_reports_monthly` (Mejorado)
- **Archivo**: `data/airflow/dags/kpi_reports_monthly.py`
- **Schedule**: `0 9 1 * *` (Día 1 del mes, 09:00 UTC)
- **Función**: Reportes mensuales de KPIs con comparaciones MoM
- **Características**:
  - ✅ Idempotencia por mes para evitar regeneraciones
  - ✅ Detección de anomalías en revenue y leads (basado en últimos 12 meses)
  - ✅ Métricas completas en Stats (`kpi_reports.*`)
  - ✅ Logging estructurado con contexto completo
  - ✅ Upload opcional a S3 con manejo de errores
  - ✅ Notificaciones Slack con resumen estructurado
  - ✅ Validación de ventanas temporales (backfill limitado)

### `etl_maintenance` (Mejorado v2.2)
- **Archivo**: `data/airflow/dags/etl_maintenance.py`
- **Schedule**: `@weekly`
- **Función**: Limpieza automatizada de datos antiguos y mantenimiento de base de datos
- **Características mejoradas**:
  - ✅ Retención configurable por tabla con validación de rangos (7-1095 días)
  - ✅ Constantes centralizadas para valores por defecto (`DEFAULT_RETENTION_*`)
  - ✅ Whitelist de tablas para VACUUM (`ALLOWED_TABLES`) - seguridad
  - ✅ SQL seguro usando `psycopg2.sql.SQL` y `Identifier` (previene SQL injection)
  - ✅ Validación de parámetros con límites razonables (`_validate_retention_days()`)
  - ✅ Logging estructurado con `get_task_logger`
  - ✅ Callbacks de error (`on_task_failure`) en todas las tareas
  - ✅ Notificaciones Slack en éxito/fallo del DAG
  - ✅ Timeouts configurables por tipo de tarea
  - ✅ VACUUM ANALYZE para optimización de tablas (whitelist security)
  - ✅ Refresh de materialized views
  - ✅ Manejo robusto de errores con contexto completo

### `etl_downstream_example`
- **Archivo**: `data/airflow/dags/etl_downstream_example.py`
- **Schedule**: Triggered por Dataset de `etl_improved` (`postgres://etl_improved/etl_improved_events`)
- **Función**: Ejemplo de DAG downstream que procesa datos del ETL
- **Características**:
  - ✅ Demuestra consumo del Dataset del ETL
  - ✅ Lee métricas del ETL más recientes
  - ✅ Realiza análisis de eventos (agregaciones, estadísticas)
  - ✅ Genera reportes basados en métricas y análisis
  - ✅ Limpieza opcional de datos temporales
  - ✅ Parámetros configurables (analysis_type, top_n)
  - ✅ Logging estructurado y métricas

**Uso como plantilla**: Este DAG sirve como ejemplo para crear pipelines downstream que se ejecuten automáticamente cuando el ETL completa, ideal para:
- Reportes automatizados
- Análisis de datos
- Sincronización con otros sistemas
- Alertas basadas en datos procesados

## Workflows de Kestra

### `whatsapp_ticket_to_sheet_doc`
- **Archivo**: `workflow/kestra/flows/whatsapp_ticket_to_sheet_doc.yaml`
- **Trigger**: Webhook (WhatsApp)
- **Función**: Procesa fotos de tickets/recibos vía WhatsApp, extrae datos con IA, valida schema, agrega a Google Sheets y genera documentos
- **Características**:
  - ✅ Verificación HMAC de firmas WhatsApp (opcional)
  - ✅ Extracción inteligente con OpenAI GPT-4o-mini
  - ✅ Validación robusta de esquema y tipos de datos
  - ✅ Normalización de datos (fechas, números, moneda)
  - ✅ Validación de estructura de items
  - ✅ Manejo de errores de API de OpenAI
  - ✅ Logging estructurado con contexto
  - ✅ Integración con Google Sheets con User-Agent y metadata
  - ✅ Generación de documentos (Markdown/PDF)
  - ✅ Notificaciones a Slack con formato enriquecido (blocks)
  - ✅ Retry automático con backoff exponencial
  - ✅ Timeouts configurables por tarea
  - ✅ Verificación HMAC opcional para seguridad webhook

### `leads_manychats_to_hubspot`
- **Archivo**: `workflow/kestra/flows/leads_manychats_to_hubspot.yaml`
- **Función**: Sincronización de leads desde ManyChats a HubSpot

### `hubspot_update_estado_interes`
- **Archivos**: 
  - `data/airflow/dags/hubspot_update_estado_interes.py` (DAG de Airflow)
  - `workflow/kestra/flows/hubspot_update_estado_interes.yaml` (Workflow de Kestra)
- **Función**: Actualiza la propiedad 'estado_interés' de un contacto en HubSpot
- **Parámetros requeridos**:
  - `hubspot_contact_id`: ID del contacto en HubSpot
  - `nuevo_estado`: Nuevo valor para la propiedad 'estado_interés'
- **Retorno**: 'Éxito' si tiene éxito, o 'CÓDIGO_ERROR: mensaje' si falla
- **Uso**: Ejecución manual o programada desde Airflow UI, o por webhook desde Kestra

### `bpm_rpa_example`
- **Archivo**: `workflow/kestra/flows/bpm_rpa_example.yaml`
- **Función**: Ejemplo de integración BPM con RPA (OpenRPA)

## Plugins Mejorados

### `etl_validation.py`
**Validación robusta de schemas y datos**

Funciones principales:
- `validate_payload_schema(payload, strict=False)` → `(is_valid, errors)`
- `validate_and_raise(payload, strict=False)` → Falla con mensajes estructurados
- `validate_rows_range(rows, min_rows, max_rows)` → Validación de rangos con contexto

**Ejemplo**:
```python
from data.airflow.plugins.etl_validation import validate_and_raise

@task
def validate_data(payload: ExtractPayload):
    validate_and_raise(payload, strict=False)
    return payload
```

### `etl_rate_limit.py`
**Rate limiting para APIs externas**

Decorador `@rate_limit()` que:
- Limita llamadas por ventana de tiempo
- Usa Airflow Variables para tracking persistente
- Registra métricas automáticas (`rate_limit.{task}.hits`)
- Espera automáticamente si se excede el límite

**Ejemplo**:
```python
from data.airflow.plugins.etl_rate_limit import rate_limit

@rate_limit(max_calls=10, window_seconds=60, variable_key="api_calls")
def call_external_api(data: dict):
    return requests.post(api_url, json=data)
```

### `etl_logging.py`
**Logging estructurado con correlación**

Funciones:
- `log_with_context(logger, level, message, **context)` → Log con campos estructurados
- `get_task_logger(dag_id)` → Logger por tarea con correlación automática
- `log_task_duration(task_id, duration_ms)` → Context manager para duraciones

**Ejemplo**:
```python
from data.airflow.plugins.etl_logging import log_with_context, get_task_logger

logger = get_task_logger("etl_example")
log_with_context(logger, logging.INFO, "Processing chunk",
                 task_id="transform", dag_run_id=run_id, chunk=1, rows=1000)
```

### `etl_debug.py`
**Helpers de debugging y diagnóstico**

Funciones:
- `debug_context(task_id)` → Context manager que captura excepciones con stack traces
- `log_payload_summary(payload, max_items=10)` → Resumen estructurado de payloads
- `diagnose_task_environment(logger)` → Diagnóstico completo del ambiente (env vars, configs, system state)

**Ejemplo**:
```python
from data.airflow.plugins.etl_debug import debug_context, diagnose_task_environment

with debug_context("my_task"):
    process_data()
    
# Diagnóstico completo
diag = diagnose_task_environment(logger)
logger.info("Environment", extra=diag)
```

### `etl_performance.py`
**Tracking detallado de performance**

Clases y funciones:
- `PerformanceTracker(name)` → Calcula min, max, mean, p50, p95, p99
- `track_performance(name)` → Context manager para tracking automático

**Ejemplo**:
```python
from data.airflow.plugins.etl_performance import track_performance, PerformanceTracker

with track_performance("db_query"):
    results = query_database()

tracker = PerformanceTracker("my_operation")
tracker.record(100)  # ms
tracker.record(150)
stats = tracker.get_stats()  # {min, max, mean, p50, p95, p99}
```

## Flujo de Datos (etl_example)

### Diagrama de Flujo Principal

```
┌─────────────────┐
                    │  validate_window │ ◄─── Parámetros: since, until
└────────┬────────┘
                             │ ✅ Validación temporal
         ▼
┌─────────────────┐
                    │   health_check   │ ◄─── Verifica: MLflow, Pool, CB
└────────┬────────┘
                             │ ✅ Health OK
                             ▼
┌─────────────────┐
                    │     branch       │ ◄─── Circuit Breaker Check
└────────┬────────┘
                   ✅│       │❌
                     │       └───► [SKIP] → DAG finaliza
                     ▼
              ┌─────────────────┐
              │     extract      │ ◄─── Anomalía de volumen
              │                  │      • Detección automática
              │                  │      • Notificación Slack si detecta
              └────────┬─────────┘
                       │ ✅ Datos extraídos
                       ▼
              ┌─────────────────┐
              │   make_chunks    │ ◄─── Chunking adaptativo
              │                  │      • Calcula chunk_size óptimo
              │                  │      • Respeta MAX_CHUNKS
              └────────┬─────────┘
                       │ ✅ Chunks listos
                       ▼
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌─────────┐  ┌─────────┐  ┌─────────┐
  │transform │  │transform │  │transform │ ◄─── Paralelo (expand)
  │ chunk_1  │  │ chunk_2  │  │ chunk_N  │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │            │              │
       └────────────┼──────────────┘
                    │ ✅ Transformación completa
                    ▼
              ┌─────────────────┐
              │    validated     │ ◄─── Validación de schema
              │                  │      • validate_and_raise()
              └────────┬─────────┘
                       │ ✅ Schema válido
                       ▼
              ┌─────────────────┐
              │     dq_check     │ ◄─── Data Quality
              │                  │      • min_rows, max_rows
              │                  │      • null_rate
              └────────┬─────────┘
                       │ ✅ DQ OK
                       ▼
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌─────────┐  ┌─────────┐  ┌─────────┐
  │  load   │  │  load   │  │  load   │ ◄─── Paralelo + Rate Limit
  │ chunk_1 │  │ chunk_2 │  │ chunk_N │      • Idempotencia por chunk
  └────┬────┘  └────┬────┘  └────┬────┘      • Rate limiting MLflow
       │            │              │
       └────────────┼──────────────┘
                    │ ✅ Load completo
                    ▼
              ┌─────────────────┐
              │ notify_summary  │ ◄─── Resumen a Slack
              │                  │      • Métricas finales
              │                  │      • Duración total
              └─────────────────┘
```

### Flujo Detallado con Decisiones

```python
# Pseudocódigo del flujo completo

def etl_example_dag():
    # 1. VALIDACIÓN INICIAL
    window = validate_window(since, until)
    if not window.valid:
        raise AirflowFailException("Invalid time window")
    
    # 2. HEALTH CHECK
    health = health_check()
    if not health.mlflow_ready:
        raise AirflowFailException("MLflow not available")
    if not health.pool_available:
        raise AirflowFailException("ETL pool exhausted")
    
    # 3. CIRCUIT BREAKER
    if circuit_breaker_is_open():
        logger.warning("Circuit breaker open, skipping execution")
        return  # Early exit
    
    # 4. EXTRACCIÓN CON ANOMALÍA DETECTION
    raw_data = extract(rows)
    volume_check = check_volume_anomaly(raw_data.rows)
    if volume_check.is_anomaly:
        notify_slack("⚠️ Volume anomaly detected")
    
    # 5. CHUNKING ADAPTATIVO
    chunks = make_chunks(
        data=raw_data,
        max_chunks=MAX_CHUNKS,
        base_chunk_size=chunk_rows
    )
    logger.info(f"Created {len(chunks)} chunks")
    
    # 6. TRANSFORMACIÓN PARALELA
    transformed_chunks = transform.expand(chunk=chunks)
    
    # 7. VALIDACIÓN DE SCHEMA
    for chunk in transformed_chunks:
        validate_and_raise(chunk, strict=False)
    
    # 8. DATA QUALITY CHECK
    total_rows = sum(len(c.rows) for c in transformed_chunks)
    dq_result = dq_check(total_rows, min_rows, max_rows)
    if not dq_result.ok:
        raise AirflowFailException(f"DQ failed: {dq_result.reason}")
    
    # 9. LOAD PARALELO CON IDEMPOTENCIA
    loaded_chunks = load.expand(chunk=transformed_chunks)
    
    # 10. NOTIFICACIÓN FINAL
    notify_summary(
        rows_processed=total_rows,
        duration_ms=total_duration,
        chunks=len(chunks)
    )
```

### Flujo de Circuit Breaker

```
┌──────────────────────────────────────────────────────┐
│              CIRCUIT BREAKER FLOW                    │
└──────────────────────────────────────────────────────┘

        [Inicio DAG]
             │
             ▼
    ┌────────────────┐
    │ ¿CB abierto?   │
    └────┬───────┬───┘
         │SÍ     │NO
         │       │
         ▼       ▼
    ┌───────┐ ┌──────────┐
    │ SKIP  │ │ Continuar │
    │       │ │           │
    │       │ │           │
    └───────┘ └─────┬─────┘
                    │
                    ▼
            ┌───────────────┐
            │ Ejecutar tarea│
            └───────┬───────┘
                    │
            ┌───────┴───────┐
            │               │
            ▼               ▼
       ┌────────┐    ┌────────┐
       │ ÉXITO   │    │ FALLO  │
       └────┬────┘    └───┬────┘
            │            │
            │            ▼
            │    ┌──────────────┐
            │    │ Registrar    │
            │    │ fallo en CB  │
            │    └───────┬──────┘
            │            │
            │            ▼
            │    ┌──────────────┐
            │    │ ¿Fallo >=    │
            │    │ threshold?   │
            │    └────┬───────┬─┘
            │         │SÍ     │NO
            │         │       │
            │         ▼       │
            │    ┌────────┐  │
            │    │Abrir CB│  │
            │    └────────┘  │
            │                │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ ¿CB abierto >   │
            │ reset_time?    │
            └────┬─────────┬──┘
                 │SÍ       │NO
                 │         │
                 ▼         │
            ┌─────────┐   │
            │Auto-reset│   │
            └─────────┘   │
                          │
                          ▼
                   [Fin DAG]
```

### Flujo de Idempotencia

```
┌──────────────────────────────────────────────────────┐
│            IDEMPOTENCY FLOW (en load task)           │
└──────────────────────────────────────────────────────┘

    [Chunk recibido]
         │
         ▼
┌────────────────────┐
│ Generar lock_key   │ ◄─── hash(chunk_data + dag_run_id)
│ basado en checksum │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ ¿Lock existe?     │
└────┬───────────┬───┘
     │SÍ         │NO
     │           │
     ▼           ▼
┌─────────┐ ┌──────────────┐
│¿allow_  │ │ Crear lock   │
│overwrite?│ │ con TTL      │
└──┬────┬──┘ └──────┬───────┘
   │NO  │SÍ         │
   │    │           │
   ▼    ▼           ▼
┌─────┐ ┌───────┐ ┌────────────┐
│SKIP │ │DELETE │ │ CONTINUAR  │
│     │ │lock   │ │            │
└─────┘ └───┬───┘ └─────┬──────┘
            │           │
            └─────┬─────┘
                  │
                  ▼
         ┌──────────────┐
         │ Procesar     │
         │ chunk        │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │ Actualizar   │
         │ lock TTL     │
         └──────────────┘
```

## Configuración

### Variables de Entorno

```bash
# Core
export ETL_POOL="etl_pool"
export MAX_ACTIVE_TASKS=32
export CHUNK_PARALLELISM=16
export MAX_CHUNKS=100

# Rate Limiting
export IDEMP_TTL_SECONDS=3600  # 1 hora default

# Data Quality (override de params DAG)
export DQ_MIN_ROWS=1
export DQ_MAX_ROWS=1000000

# Circuit Breaker (control manual)
export ETL_EXAMPLE_CIRCUIT_OPEN=1  # Para abrir manualmente
```

### Parámetros del DAG (etl_example)

- `rows`: Número de filas a procesar
- `run_name`: Identificador de ejecución
- `chunk_rows`: Tamaño de chunk (default: 1000)
- `since` / `until`: Ventana temporal (ISO 8601)
- `idempotency_ttl_minutes`: TTL para locks (default: 60)
- `dry_run`: Modo dry-run (no escribe a DB)

## Patrones de Diseño

### Patrón 1: Validación en Capas

```python
@task
def layered_validation(payload: ExtractPayload) -> ExtractPayload:
    # Capa 1: Schema básico
    validate_and_raise(payload, strict=False)
    
    # Capa 2: Rangos
    rows = payload.get("rows", 0)
    validate_rows_range(rows, min_rows=100, max_rows=1000000)
    
    # Capa 3: Reglas de negocio
    if payload.get("status") not in ["active", "pending"]:
        raise AirflowFailException(f"Invalid status: {payload.get('status')}")
    
    return payload
```

### Patrón 2: Rate Limiting con Retry Inteligente

```python
from data.airflow.plugins.etl_rate_limit import rate_limit

@rate_limit(max_calls=10, window_seconds=60)
def api_call_with_backoff():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
    raise AirflowException("API call failed after retries")
```

### Patrón 3: Circuit Breaker con Auto-Recovery

```python
def check_and_reset_circuit_breaker():
    cb_data = Variable.get("cb:failures:etl_example", default_var=None)
    if cb_data:
        data = json.loads(cb_data)
        failures = data.get("count", 0)
        last_failure = data.get("last_failure_ts", 0)
        now = pendulum.now("UTC").int_timestamp
        
        # Auto-reset después de 1 hora
        if (now - last_failure) > 3600 and failures > 0:
            Variable.delete("cb:failures:etl_example")
            logger.info("Circuit breaker auto-reset")
```

### Patrón 4: Idempotencia con Deduplicación

```python
def idempotent_load(data: list, key_func: callable, ttl_hours: int = 24):
    """Load con idempotencia basada en clave derivada de datos."""
    processed = []
    for item in data:
        item_key = key_func(item)
        lock_key = f"idemp:load:{hashlib.sha256(item_key.encode()).hexdigest()}"
        
        if _idemp_should_skip(lock_key):
            logger.debug(f"Skipping duplicate: {item_key}")
            continue
        
        _idemp_set(lock_key, ttl_hours * 3600)
        processed.append(item)
        # Insert into DB
    return processed
```

## Optimizaciones

### Chunking Adaptativo

```python
def adaptive_chunking(total_rows: int, base_chunk_size: int, max_parallel: int) -> int:
    """
    Calcula tamaño óptimo de chunk basado en volumen y paralelismo.
    """
    ideal_chunks = min(max_parallel, max(1, total_rows // base_chunk_size))
    if ideal_chunks == 0:
        ideal_chunks = 1
    
    chunk_size = max(1, total_rows // ideal_chunks)
    # Redondear a múltiplo de 1000 para eficiencia
    chunk_size = ((chunk_size + 999) // 1000) * 1000
    return min(chunk_size, total_rows)
```

### Batch Processing con Rate Limiting

```python
@rate_limit(max_calls=100, window_seconds=60, variable_key="batch_api")
def batch_api_call(items: list, batch_size: int = 50) -> list:
    """Procesa items en batches respetando rate limits."""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_result = process_batch(batch)  # Protegido por rate limit
        results.extend(batch_result)
    return results
```

## Checklist de Implementación

### Para Nuevos DAGs

- [ ] Usar `get_task_logger()` para logging estructurado
- [ ] Validar inputs con `validate_and_raise()` o `validate_payload_schema()`
- [ ] Agregar `@rate_limit()` a todas las llamadas a APIs externas
- [ ] Incluir `start_span()` para tracing (preparado para OpenTelemetry)
- [ ] Medir performance con `track_performance()` en código crítico
- [ ] Implementar idempotencia con TTL si procesa datos duplicables
- [ ] Configurar circuit breaker si el DAG depende de servicios externos inestables
- [ ] Agregar `debug_context()` para captura automática de errores
- [ ] Incluir health check si el DAG tiene dependencias externas

### Para Migración de DAGs Existentes

- [ ] Reemplazar `logger.info()` con `log_with_context()`
- [ ] Reemplazar validaciones manuales con `validate_and_raise()`
- [ ] Agregar `@rate_limit()` a funciones que llamen APIs
- [ ] Agregar `track_performance()` alrededor de operaciones lentas
- [ ] Envolver bloques críticos con `debug_context()`

## Métricas y KPIs

### Métricas de Performance

| Métrica | Descripción | Target | Alerta |
|---------|-------------|--------|--------|
| `etl_example.transform.duration_ms` | Tiempo de transform por chunk | < 3000ms | > 8000ms |
| `etl_example.load.duration_ms` | Tiempo de load por chunk | < 2000ms | > 5000ms |
| `etl_example.total_duration_ms` | Duración end-to-end del DAG | < 15min | > 30min |
| `etl_example.throughput.rows_per_sec` | Filas procesadas por segundo | > 1000 | < 500 |
| `etl_example.throughput.ms_per_1k_rows` | Milisegundos por 1000 filas | < 1000ms | > 2000ms |
| `etl_example.rows_processed` | Total de filas procesadas | N/A | N/A |

### Métricas de Calidad de Datos

| Métrica | Descripción | Target | Alerta |
|---------|-------------|--------|--------|
| `etl_example.validate.success` | Validaciones exitosas | > 95% | < 90% |
| `etl_example.validate.failure` | Validaciones fallidas | < 5% | > 10% |
| `etl_example.dq.deviation_pct` | Desviación de volumen esperado | ±10% | ±20% |
| `etl_example.dq.min_rows` | Filas mínimas validadas | > 0 | = 0 |
| `etl_example.dq.max_rows` | Filas máximas validadas | < threshold | > 2x threshold |

### Métricas Operacionales

| Métrica | Descripción | Target | Alerta |
|---------|-------------|--------|--------|
| `rate_limit.{task}.hits` | Límites de rate alcanzados | < 5/hora | > 10/hora |
| `etl_example.runs.success` | Ejecuciones exitosas | > 98% | < 95% |
| `etl_example.runs.failure` | Ejecuciones fallidas | < 2% | > 5% |
| `circuit_breaker.{service}.open` | Circuit breakers abiertos | 0 | > 0 |
| `anomaly.{type}.detected` | Anomalías detectadas | < 1/día | > 5/día |

### KPIs del Sistema

- **SLA de Ejecución**: 99% de corridas completan en < 30 min
- **Throughput**: > 10,000 filas/minuto en transform
- **Disponibilidad**: > 99.5% uptime
- **Tiempo de Recuperación (MTTR)**: < 15 min para errores comunes
- **Tasa de Éxito**: > 98% de corridas sin fallos críticos

### Dashboards Recomendados

1. **Performance Dashboard**
   - Gráfico de líneas: p50, p95, p99 por tarea
   - Heatmap de duración por hora del día
   - Distribución de tiempos (histograma)

2. **Quality Dashboard**
   - Tasa de validación exitosa (gauge)
   - Trend de desviaciones de volumen
   - Top errores de validación (tabla)

3. **Operational Dashboard**
   - Estado de circuit breakers (mapa de calor)
   - Rate limit hits por servicio
   - Alertas activas (lista temporal)

## Monitoreo Proactivo

### Métricas Clave

- **Performance**: `etl_example.perf.{task}.{p50|p95|p99}_ms`
- **Rate Limits**: `rate_limit.{task}.hits`
- **Validaciones**: `etl_example.validate.{success|failure}`
- **DQ**: `etl_example.dq.{min|max}_rows`, `etl_example.dq.deviation_pct`
- **Circuit Breaker**: `cb:failures:etl_example` (Variable)

### Alertas Recomendadas

1. **Rate Limit Hits**: `rate_limit.{task}.hits > 5` en 1 hora → Alertar a equipo
2. **Performance Degradation**: `p95_ms > 2x p50_ms` → Investigar outliers
3. **Circuit Breaker Open**: Alerta inmediata cuando se abre
4. **Validation Failures**: `validate.failure` > 10% del total → Revisar schema
5. **Volume Anomalies**: Cuando `_check_volume_anomaly` detecta desviación > 20%

## Troubleshooting

### Rate Limit Exceeded

```python
# Verificar estado actual
from airflow.models import Variable
state = Variable.get("rate_limit:mlflow_api", default_var=None)
if state:
    import json
    data = json.loads(state)
    print(f"Calls: {data.get('count')}, Window start: {data.get('window_start')}")

# Ver métricas
from airflow.stats import Stats
hits = Stats.gauge("rate_limit.mlflow_api.hits")
print(f"Total hits: {hits}")
```

### Circuit Breaker Abierto

```bash
# Ver estado
airflow variables get cb:failures:etl_example | jq

# Reset manual
airflow variables delete cb:failures:etl_example

# Reset desde código
from airflow.models import Variable
Variable.delete("cb:failures:etl_example")
```

### Performance Issues

```python
from data.airflow.plugins.etl_debug import diagnose_task_environment
from data.airflow.plugins.etl_performance import PerformanceTracker

# Diagnóstico completo
diag = diagnose_task_environment(logger)
logger.info("Environment diagnostics", extra=diag)

# Análisis de performance
tracker = PerformanceTracker("diagnostic")
# ... registrar operaciones ...
stats = tracker.get_stats()
logger.info(f"P95: {stats['p95_ms']}ms, P99: {stats['p99_ms']}ms")
```

### Debugging de Validaciones

```python
from data.airflow.plugins.etl_validation import validate_payload_schema

# Obtener errores detallados sin fallar
is_valid, errors = validate_payload_schema(payload, strict=False)
if not is_valid:
    logger.error(f"Validation errors: {errors}")
    # Analizar cada error individualmente
```

## FAQ

### ¿Cuándo usar rate limiting?
- Cuando llamas a APIs externas con límites conocidos (Stripe, HubSpot, etc.)
- Para prevenir throttling y costos imprevistos
- Cuando múltiples DAGs comparten la misma API

### ¿Cuándo usar circuit breaker?
- Cuando un servicio externo falla frecuentemente y quieres evitar cascading failures
- Para control manual de ejecución (ej: mantenimiento programado)
- Cuando quieres limitar intentos fallidos automáticamente

### ¿Cómo elegir TTL de idempotencia?
- **Corto (1-6h)**: Datos frecuentes que pueden cambiar (ej: métricas en tiempo real)
- **Medio (12-24h)**: Procesos diarios estándar (ej: ETL nocturno)
- **Largo (48h+)**: Para procesos semanales o backfills únicos

### ¿Cómo interpretar percentiles de performance?
- **p50 (mediana)**: Lo que típicamente esperas
- **p95**: Detecta outliers, objetivo común para SLA
- **p99**: Peaks extremos, investigar si es consistente

### ¿Cuándo usar validación estricta vs flexible?
- **strict=False**: Permite campos adicionales (útil para evolución de schema)
- **strict=True**: Falla en campos inesperados (útil para debugging de integraciones)

## Comandos Útiles

```bash
# Circuit breaker
airflow variables get cb:failures:etl_example | jq
airflow variables delete cb:failures:etl_example

# Rate limits
airflow variables get rate_limit:mlflow_api | jq

# Health check manual
airflow tasks test etl_example health_check $(date +%Y-%m-%d)

# Dry run con parámetros
airflow dags trigger etl_example --conf '{
  "dry_run": true,
  "rows": 1000,
  "chunk_rows": 500
}'

# Ver métricas de Stats
airflow tasks test etl_example health_check $(date +%Y-%m-%d) --task-params '{}' | grep "Stats"
```

## Referencias

- **Plugins**: `data/airflow/plugins/`
  - `etl_validation.py` - Validación robusta
  - `etl_rate_limit.py` - Rate limiting
  - `etl_logging.py` - Logging estructurado
  - `etl_debug.py` - Debugging
  - `etl_performance.py` - Performance tracking
- **DAGs**: `data/airflow/dags/`
  - `etl_example.py` - DAG mejorado completo
  - `employee_onboarding.py` - Ejemplo de uso de plugins
- **Tests**: `data/airflow/dags/tests/`
- **Documentación**: `README_ETL_IMPROVED.md`
- **Dashboard**: `web/kpis-next/app/etl/page.tsx` (si existe)
- **Grafana**: `observability/grafana/dashboards/etl_improved.json` (si existe)

## Testing y Calidad

### Estructura de Tests

```
data/airflow/
├── dags/tests/
│   ├── test_dag_import.py      # Verifica importación de DAGs
│   ├── test_etl_example.py     # Tests unitarios ETL
│   ├── test_dq_helper.py       # Tests de data quality
│   ├── test_etl_utils.py       # Tests de utilidades
│   ├── test_dq_config.py       # Tests de configuración DQ
│   └── test_smoke.py            # Smoke tests básicos
└── plugins/tests/
    ├── test_etl_config.py      # Tests de validación de params
    └── test_etl_ops.py         # Tests de operaciones ETL
```

### Ejecutar Tests

```bash
# Todos los tests
pytest data/airflow/dags/tests -v

# Tests específicos
pytest data/airflow/dags/tests/test_etl_example.py -v

# Con cobertura
pytest data/airflow/dags/tests --cov=data.airflow --cov-report=html

# Tests de plugins
pytest data/airflow/plugins/tests -v
```

### Ejemplo de Test Unitario

```python
import pytest
from data.airflow.plugins.etl_validation import validate_payload_schema

def test_validate_payload_schema_valid():
    payload = {"rows": 100, "transformed": False}
    is_valid, errors = validate_payload_schema(payload, strict=False)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_payload_schema_missing_rows():
    payload = {"transformed": False}
    is_valid, errors = validate_payload_schema(payload, strict=False)
    assert is_valid is False
    assert "Missing required field: rows" in errors
```

### Test de Integración con Airflow

```python
from airflow.models import DagBag
import pytest

def test_etl_example_dag_loaded():
    """Verifica que el DAG se carga correctamente."""
    dagbag = DagBag()
    dag = dagbag.get_dag(dag_id="etl_example")
    assert dag is not None
    assert len(dag.tasks) > 0

def test_etl_example_has_required_tasks():
    """Verifica que el DAG tiene las tareas esperadas."""
    dagbag = DagBag()
    dag = dagbag.get_dag(dag_id="etl_example")
    expected_tasks = {"extract", "transform", "validate", "load"}
    actual_tasks = {task.task_id for task in dag.tasks}
    assert expected_tasks.issubset(actual_tasks)
```

## Casos de Uso Específicos

### Caso 1: Migración de Legacy ETL

**Problema**: DAG antiguo sin validaciones ni rate limiting

**Solución paso a paso**:

1. **Agregar logging estructurado**:
```python
# Antes
logger.info(f"Processing {len(data)} rows")

# Después
from data.airflow.plugins.etl_logging import log_with_context, get_task_logger
logger = get_task_logger("my_dag")
log_with_context(logger, logging.INFO, "Processing rows",
                 task_id="extract", rows=len(data), dag_run_id=run_id)
```

2. **Agregar validación**:
```python
# Antes
data = extract_data()

# Después
from data.airflow.plugins.etl_validation import validate_and_raise
data = extract_data()
validate_and_raise(data, strict=False)
```

3. **Agregar rate limiting**:
```python
# Antes
def call_api():
    return requests.post(api_url, json=data)

# Después
from data.airflow.plugins.etl_rate_limit import rate_limit

@rate_limit(max_calls=10, window_seconds=60)
def call_api():
    return requests.post(api_url, json=data)
```

### Caso 2: Optimización de Performance

**Problema**: DAG lento, no sabemos dónde está el cuello de botella

**Solución**:

```python
from data.airflow.plugins.etl_performance import track_performance
from data.airflow.plugins.etl_debug import diagnose_task_environment

@task
def optimized_extract():
    # 1. Diagnóstico inicial
    diag = diagnose_task_environment(logger)
    logger.info("Environment", extra=diag)
    
    # 2. Medir cada operación
    with track_performance("db_query"):
        raw_data = query_database()
    
    with track_performance("transform"):
        transformed = transform_data(raw_data)
    
    with track_performance("validation"):
        validated = validate_data(transformed)
    
    # 3. Revisar métricas en Stats
    # Buscar en Grafana: etl_example.perf.db_query.p95_ms
    return validated
```

### Caso 3: Manejo de APIs con Rate Limits Estrictos

**Problema**: API externa limita a 5 calls/minuto, múltiples DAGs la usan

**Solución**:

```python
from data.airflow.plugins.etl_rate_limit import rate_limit

# Usar la misma variable_key para compartir el rate limit
@rate_limit(max_calls=5, window_seconds=60, variable_key="strict_api")
def call_strict_api(data):
    response = requests.post("https://api.example.com", json=data)
    response.raise_for_status()
    return response.json()

# Todos los DAGs que usen variable_key="strict_api" compartirán el límite
```

### Caso 4: Detección Temprana de Problemas de Datos

**Problema**: Queremos detectar cambios en volumen de datos antes de procesar

**Solución** (ya implementado en `etl_example`):

```python
from data.airflow.plugins.etl_metrics import record_extract_start, record_extract_success
from airflow.models import Variable

def _check_volume_anomaly(expected_rows: int, tolerance_pct: float = 20.0):
    """Compara volumen actual con histórico de 7 días."""
    # Obtener histórico
    historical = Variable.get("etl_example:volume_history", default_var="[]")
    history = json.loads(historical)
    
    if len(history) >= 7:
        avg_historical = sum(history[-7:]) / 7
        deviation = abs(expected_rows - avg_historical) / avg_historical * 100
        
        if deviation > tolerance_pct:
            logger.warning(f"Volume anomaly detected: {deviation:.1f}% deviation")
            notify_slack(f"⚠️ Volume anomaly: {expected_rows} rows (expected ~{avg_historical:.0f})")
    
    # Guardar en histórico
    history.append(expected_rows)
    Variable.set("etl_example:volume_history", json.dumps(history[-30:]))  # Últimos 30 días
```

## Arquitectura y Deployment

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    Airflow Scheduler                     │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼──────┐ ┌────▼──────────┐
│  etl_example │ │etl_improved│ │employee_      │
│              │ │            │ │onboarding     │
└───────┬──────┘ └────┬───────┘ └────┬──────────┘
        │             │              │
        └─────────────┼──────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼─────┐ ┌────▼─────┐ ┌────▼─────┐
│  Plugins    │ │PostgreSQL│ │External   │
│  - validation│ │          │ │APIs       │
│  - rate_limit│ │          │ │           │
│  - logging  │ │          │ │           │
│  - debug    │ │          │ │           │
│  - perf     │ │          │ │           │
└─────────────┘ └──────────┘ └───────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │   Observability Stack      │
        │  - Stats (Prometheus)      │
        │  - Grafana Dashboards      │
        │  - MLflow (experiments)    │
        │  - Slack Notifications     │
        └────────────────────────────┘
```

### Deployment Checklist

#### Pre-Deployment

- [ ] Todos los tests pasan (`pytest data/airflow/dags/tests -v`)
- [ ] DAGs se importan correctamente (`airflow dags list`)
- [ ] Variables de entorno configuradas
- [ ] Connections configuradas en Airflow UI
- [ ] Rate limits configurados según límites de APIs
- [ ] Circuit breakers configurados si aplica
- [ ] Notificaciones Slack configuradas

#### Deployment

1. **Backup de configuración actual**:
```bash
# Exportar Variables
airflow variables export /tmp/airflow_vars_backup.json

# Exportar Connections (si necesario)
airflow connections export /tmp/airflow_conns_backup.json
```

2. **Verificar sintaxis**:
```bash
# Validar DAGs
airflow dags list-import-errors

# Test individual
airflow tasks test etl_example validate_window 2024-01-01
```

3. **Deploy incremental**:
```bash
# 1. Deploy plugins primero
# 2. Deploy DAGs mejorados
# 3. Monitorear primeras ejecuciones
```

#### Post-Deployment

- [ ] Verificar métricas en Grafana
- [ ] Verificar logs estructurados
- [ ] Probar circuit breaker (si aplica)
- [ ] Verificar rate limiting funcionando
- [ ] Probar notificaciones Slack

## Integración con Otros Sistemas

### Integración con MLflow

```python
from data.airflow.plugins.etl_ops import log_with_mlflow

@task
def track_experiment(payload: ExtractPayload):
    # Logging automático con rate limiting
    log_with_mlflow(
        experiment_name="etl_pipeline",
        run_name=f"run_{dag_run_id}",
        metrics={
            "rows_processed": payload.get("rows", 0),
            "duration_ms": duration,
        },
        params={
            "chunk_size": chunk_rows,
            "source": "api",
        }
    )
```

### Integración con Prometheus/Stats

```python
from airflow.stats import Stats

# Métricas personalizadas
Stats.increment("custom.metric.name")
Stats.gauge("custom.gauge", value=100)
Stats.timing("custom.timing", duration_ms=150)
```

### Integración con Grafana

**Query ejemplo para dashboard**:
```promql
# Rate limit hits
rate(rate_limit_mlflow_api_hits[5m])

# Performance P95
etl_example_perf_extract_p95_ms

# Validation failures
rate(etl_example_validate_failure[5m])
```

### Integración con Slack

```python
from data.airflow.plugins.etl_notifications import notify_slack

@task
def notify_completion(status: str, rows: int):
    message = f"✅ ETL completed: {rows} rows processed"
    if status == "failed":
        message = f"❌ ETL failed: {rows} rows processed"
    
    notify_slack(
        message=message,
        webhook_url=Variable.get("slack_webhook_url"),
        attachments=[{
            "color": "good" if status == "success" else "danger",
            "fields": [
                {"title": "Rows", "value": str(rows), "short": True},
                {"title": "Status", "value": status, "short": True},
            ]
        }]
    )
```

## Seguridad

### Validación de Inputs

```python
import re
from airflow.exceptions import AirflowFailException

def sanitize_input(user_input: str, max_length: int = 200) -> str:
    """Sanitiza inputs del usuario para prevenir inyección."""
    # Remover caracteres peligrosos
    sanitized = re.sub(r'[<>"\';]', '', user_input)
    # Limitar longitud
    sanitized = sanitized[:max_length].strip()
    
    if not sanitized:
        raise AirflowFailException("Input sanitization resulted in empty string")
    
    return sanitized
```

### Manejo Seguro de Secrets

```python
from airflow.hooks.base import BaseHook
from airflow.models import Variable

def get_secret_safely(conn_id: str, key: str) -> str:
    """Obtiene secretos de forma segura desde Airflow Connections."""
    try:
        conn = BaseHook.get_connection(conn_id)
        secret = getattr(conn, key, None)
        if not secret:
            raise AirflowFailException(f"Secret {key} not found in {conn_id}")
        return secret
    except Exception as e:
        logger.error(f"Failed to get secret {key} from {conn_id}: {e}")
        raise AirflowFailException(f"Secret retrieval failed: {e}")
```

### Prevención de SQL Injection

```python
from airflow.providers.postgres.hooks.postgres import PostgresHook

# ✅ CORRECTO: Prepared statements
hook = PostgresHook(postgres_conn_id="postgres_default")
sql = "INSERT INTO table (col1, col2) VALUES (%s, %s)"
hook.run(sql, parameters=(value1, value2))

# ❌ INCORRECTO: String interpolation
sql = f"INSERT INTO table (col1) VALUES ('{user_input}')"  # VULNERABLE
```

## Troubleshooting Avanzado

### Debugging de Rate Limits

```python
from airflow.models import Variable
import json
import time

def debug_rate_limit(task_name: str):
    """Diagnostica problemas de rate limiting."""
    key = f"rate_limit:{task_name}"
    state = Variable.get(key, default_var=None)
    
    if not state:
        logger.info(f"No rate limit state found for {task_name}")
        return
    
    data = json.loads(state)
    now = int(time.time())
    window_start = data.get("window_start", 0)
    count = data.get("count", 0)
    max_calls = data.get("max_calls", 0)
    window_seconds = data.get("window_seconds", 0)
    
    window_age = now - window_start
    calls_remaining = max(0, max_calls - count)
    time_until_reset = max(0, window_seconds - window_age)
    
    logger.info(f"Rate limit state for {task_name}:", extra={
        "count": count,
        "max_calls": max_calls,
        "window_age_sec": window_age,
        "window_total_sec": window_seconds,
        "calls_remaining": calls_remaining,
        "time_until_reset_sec": time_until_reset,
        "is_throttled": count >= max_calls,
    })
```

### Análisis de Performance Degradado

```python
from data.airflow.plugins.etl_performance import PerformanceTracker
from data.airflow.plugins.etl_debug import diagnose_task_environment

@task
def diagnose_performance_issue():
    """Diagnóstico completo de problemas de performance."""
    # 1. Diagnóstico de ambiente
    diag = diagnose_task_environment(logger)
    logger.info("Environment diagnostics", extra=diag)
    
    # 2. Comparar con baseline
    baseline_p95 = Variable.get("baseline:p95_ms", default_var="0")
    current_stats = PerformanceTracker("current").get_stats()
    current_p95 = current_stats.get("p95_ms", 0)
    
    if current_p95 > float(baseline_p95) * 2:
        logger.warning(f"Performance degraded: {current_p95}ms vs baseline {baseline_p95}ms")
        
        # Investigar causas
        # - Revisar métricas de DB
        # - Revisar carga del sistema
        # - Revisar cambios recientes
    
    return diag
```

### Resolución de Circuit Breaker

```python
def analyze_and_reset_circuit_breaker(dag_id: str, auto_reset: bool = False):
    """Análisis detallado y reset del circuit breaker."""
    cb_key = f"cb:failures:{dag_id}"
    cb_data = Variable.get(cb_key, default_var=None)
    
    if not cb_data:
        logger.info(f"Circuit breaker inactive for {dag_id}")
        return
    
    data = json.loads(cb_data)
    failures = data.get("count", 0)
    last_failure_ts = data.get("last_failure_ts", 0)
    now_ts = pendulum.now("UTC").int_timestamp
    age = now_ts - last_failure_ts
    
    logger.info(f"Circuit breaker analysis for {dag_id}:", extra={
        "failure_count": failures,
        "last_failure_age_sec": age,
        "last_failure_time": pendulum.from_timestamp(last_failure_ts).isoformat(),
        "status": "OPEN" if age < 1800 else "CLOSED",
        "auto_reset_in_sec": max(0, 1800 - age),
    })
    
    # Auto-reset si edad > 1 hora
    if auto_reset and age > 3600:
        Variable.delete(cb_key)
        logger.info(f"Circuit breaker auto-reset for {dag_id}")
```

## Mejores Prácticas de Código

### Naming Conventions

```python
# ✅ Bueno: Nombres descriptivos
def validate_payload_schema(payload: Dict[str, Any]) -> tuple[bool, List[str]]:
    pass

# ❌ Malo: Nombres genéricos
def validate(data):
    pass
```

### Type Hints

```python
# ✅ Bueno: Type hints completos
from typing import Dict, Any, List, Optional

def process_data(
    payload: ExtractPayload,
    chunk_size: int = 1000,
    dry_run: bool = False
) -> Dict[str, Any]:
    pass

# ❌ Malo: Sin type hints
def process_data(payload, chunk_size=1000, dry_run=False):
    pass
```

### Error Handling

```python
# ✅ Bueno: Manejo específico de errores
try:
    result = call_external_api(data)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        logger.warning("Rate limited, will retry")
        raise  # Re-raise para retry de Airflow
    else:
        logger.error(f"API error: {e}")
        raise AirflowFailException(f"API call failed: {e}")
except Exception as e:
    logger.exception("Unexpected error")
    raise AirflowFailException(f"Unexpected error: {e}")

# ❌ Malo: Catching genérico sin contexto
try:
    result = call_external_api(data)
except:
    pass  # Silencia errores
```

## Mejores Prácticas

### Desarrollo de DAGs

1. **Siempre usar validación de datos**
   ```python
   from data.airflow.plugins.etl_validation import validate_payload_schema
   validated = validate_payload_schema(payload, expected_schema)
   ```

2. **Implementar idempotencia para tareas críticas**
   ```python
   lock_key = f"idemp:{dag_id}:{unique_key}"
   if _check_idempotency_with_ttl(lock_key, ttl_hours):
       logger.warning("Skipping duplicate run")
       return
   _set_idempotency_with_ttl(lock_key, ttl_hours)
   ```

3. **Usar logging estructurado**
   ```python
   logger.info("processing data", extra={
       "rows": rows,
       "duration_ms": duration_ms,
       "dag_run_id": run_id
   })
   ```

4. **Agregar timeouts a todas las tareas**
   ```python
   @task(execution_timeout=timedelta(minutes=10))
   def my_task():
       ...
   ```

5. **Configurar retries apropiados**
   - Tareas I/O: 2-3 retries con exponential backoff
   - Validación/DQ: 0 retries (fail fast)

6. **Validar parámetros con límites razonables**
   ```python
   def _validate_retention_days(days: int, param_name: str) -> int:
       """Validate retention days parameter is within reasonable bounds."""
       MIN_RETENTION_DAYS = 7
       MAX_RETENTION_DAYS = 1095
       if not isinstance(days, (int, float)) or days < MIN_RETENTION_DAYS:
           raise AirflowFailException(
               f"Invalid {param_name}: {days} (minimum: {MIN_RETENTION_DAYS} days)"
           )
       if days > MAX_RETENTION_DAYS:
           raise AirflowFailException(
               f"Invalid {param_name}: {days} (maximum: {MAX_RETENTION_DAYS} days)"
           )
       return int(days)
   ```

7. **Usar whitelists para operaciones críticas**
   ```python
   # Para VACUUM, DROP, o cualquier operación destructiva
   ALLOWED_TABLES = {"table1", "table2", "table3"}
   if table not in ALLOWED_TABLES:
       raise ValueError(f"Table {table} not allowed for VACUUM")
   ```

8. **Prevenir SQL Injection con psycopg2.sql**
   ```python
   from psycopg2.sql import SQL, Identifier
   
   # ✅ Seguro
   cur.execute(SQL("VACUUM ANALYZE public.{}").format(Identifier(table)))
   
   # ❌ Inseguro
   cur.execute(f"VACUUM ANALYZE public.{table}")
   ```
   - Transformaciones: 1-2 retries

6. **Usar circuit breakers para servicios externos**
   ```python
   if _cb_is_open(dag_id, threshold=5, reset_minutes=15):
       raise AirflowFailException("Circuit breaker is open")
   ```

### Operaciones

1. **Monitorear métricas clave diariamente**
   - Tasa de éxito de DAGs
   - Duración promedio de tareas
   - Alertas activas
   - Circuit breakers abiertos

2. **Configurar alertas proactivas**
   - SLA misses
   - Anomalías de volumen
   - Rate limit hits frecuentes
   - Circuit breaker activaciones

3. **Revisar logs estructurados para debugging**
   - Buscar por `dag_run_id` para correlación
   - Filtrar por `component` para tareas específicas
   - Revisar `duration_ms` para performance issues

4. **Mantener documentación actualizada**
   - Parámetros de DAGs
   - Variables de entorno
   - Configuración de integraciones

### Configuración

1. **Centralizar configuración en `etl_config_constants.py`**
   - Facilita ajustes sin modificar DAGs
   - Permite override vía env vars

2. **Usar environment-specific configs**
   - `environments/dev.yaml`, `stg.yaml`, `prod.yaml`
   - Resolución automática de URLs y credenciales

3. **Validar parámetros al inicio**
   - Usar Airflow Param con tipos
   - Validar rangos y formatos
   - Proporcionar defaults sensibles

## Ejemplos de Uso Completos

### Ejemplo 1: ETL con Validación y Anomalía Detection

```python
@task(task_id="extract")
def extract() -> Dict[str, Any]:
    ctx = get_current_context()
    rows = ctx["params"].get("rows", 1000)
    
    # Health check
    if not _check_environment_ready():
        raise AirflowFailException("Environment not ready")
    
    # Extract with rate limiting
    with rate_limit("extract_api", max_calls=100, window_seconds=60):
        data = fetch_data(rows)
    
    # Anomaly detection
    if _check_volume_anomaly("extract", rows):
        notify_slack(f":warning: Volume anomaly detected: {rows} rows")
    
    return data
```

### Ejemplo 2: Onboarding con Validaciones

```python
# Trigger con parámetros
airflow dags trigger employee_onboarding --conf '{
  "employee_email": "new.employee@company.com",
  "full_name": "New Employee",
  "start_date": "2024-12-01",
  "manager_email": "manager@company.com",
  "department": "Engineering",
  "send_welcome": true,
  "create_issue_tracker_tasks": true,
  "hris_lookup": true
}'
```

### Ejemplo 3: KPI Report Manual

```python
# El reporte mensual se ejecuta automáticamente el día 1
# Para forzar ejecución manual:
airflow dags trigger kpi_reports_monthly --conf '{
  "since": "2024-11-01",
  "until": "2024-11-30"
}'
```

## Escalabilidad

### Estrategias de Escalado

1. **Horizontal Scaling**
   - Ajustar `MAX_ACTIVE_TASKS` y `CHUNK_PARALLELISM` dinámicamente
   - Configurar múltiples workers en Kubernetes
   - Distribuir carga entre pools de Airflow

2. **Vertical Scaling**
   - Ajustar tamaño de chunks basado en memoria disponible
   - Optimizar queries para reducir uso de memoria
   - Usar streaming para datasets grandes

3. **Auto-scaling**
   - Kubernetes HPA basado en métricas de CPU/memoria
   - Ajustar workers según carga del sistema
   - Monitorear métricas de throughput

### Optimización de Base de Datos

```sql
-- Índices estratégicos
CREATE INDEX CONCURRENTLY idx_events_created_at 
ON etl_improved_events(created_at);

-- Particionamiento por fecha
CREATE TABLE etl_events_2024_01 PARTITION OF etl_improved_events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Materialized views para agregaciones
CREATE MATERIALIZED VIEW mv_daily_metrics AS
SELECT date_trunc('day', created_at) as day,
       COUNT(*) as total_events,
       SUM(amount) as total_amount
FROM etl_improved_events
GROUP BY day;
```

### Límites y Consideraciones

- **Máximo chunks**: `MAX_CHUNKS` (default: 100)
- **Pool slots**: Configurar según capacidad
- **Memory per task**: Monitorear uso
- **DB connections**: Limitar pool de PostgreSQL

## Optimización de Costos

### Estrategias de Reducción de Costos

#### 1. Tuning de Chunks (Balance Overhead vs Paralelismo)

```python
def optimize_chunk_size(total_rows: int, cost_per_chunk: float) -> int:
    """
    Calcula chunk size óptimo balanceando overhead y paralelismo.
    
    Costos a considerar:
    - Overhead de orquestación por chunk
    - Costo de procesamiento por fila
    - Costo de infraestructura (CPU/memoria)
    """
    # Costo base por chunk (orquestación, task creation)
    BASE_COST_PER_CHUNK = 0.01  # $0.01 por chunk
    COST_PER_ROW = 0.00001  # $0.00001 por fila procesada
    
    # Calcular costo total para diferentes tamaños de chunk
    optimal_chunk_size = 10_000
    min_total_cost = float('inf')
    
    for chunk_size in [1_000, 5_000, 10_000, 50_000, 100_000]:
        num_chunks = (total_rows + chunk_size - 1) // chunk_size
        chunk_cost = num_chunks * BASE_COST_PER_CHUNK
        row_cost = total_rows * COST_PER_ROW
        total_cost = chunk_cost + row_cost
        
        if total_cost < min_total_cost:
            min_total_cost = total_cost
            optimal_chunk_size = chunk_size
    
    return optimal_chunk_size
```

**Guía de Tamaños de Chunk**:
- **Chunks pequeños (1K-10K)**: Mayor paralelismo, más overhead
  - Usar cuando: Procesamiento rápido, alta latencia de red
  - Costo: Alto overhead de orquestación
  
- **Chunks medianos (10K-50K)**: Balance óptimo
  - Usar cuando: Caso general, procesamiento moderado
  - Costo: Balanceado
  
- **Chunks grandes (50K-100K)**: Menor overhead, menor paralelismo
  - Usar cuando: Procesamiento pesado, I/O bound
  - Costo: Bajo overhead, pero puede causar timeouts

#### 2. Materialized Views (Pre-cálculo de Agregaciones)

```sql
-- Ejemplo: Materialized view para métricas costosas
CREATE MATERIALIZED VIEW mv_revenue_daily AS
SELECT 
    date_trunc('day', created_at) as day,
    SUM(amount) as total_revenue,
    COUNT(*) as transaction_count,
    AVG(amount) as avg_transaction,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY amount) as p95_amount
FROM transactions
WHERE created_at >= CURRENT_DATE - INTERVAL '365 days'
GROUP BY day;

-- Refresh solo cuando necesario (no cada hora)
-- Refresh programado en etl_maintenance DAG
CREATE INDEX ON mv_revenue_daily (day);

-- Ahorro de costos: Una query a MV en lugar de full table scan
-- Antes: SELECT SUM(amount) FROM transactions WHERE ... (scan 1M+ filas)
-- Después: SELECT total_revenue FROM mv_revenue_daily WHERE day = ... (scan 365 filas)
-- Ahorro: ~99.96% menos I/O
```

#### 3. Limpieza Proactiva de Datos

```python
# Configuración de retención por tipo de dato
RETENTION_POLICIES = {
    'metrics': {
        'days': 90,  # 3 meses
        'rationale': 'Métricas históricas suficientes para análisis'
    },
    'audit': {
        'days': 90,  # 3 meses
        'rationale': 'Cumplimiento regulatorio mínimo'
    },
    'alerts': {
        'days': 180,  # 6 meses
        'rationale': 'Historial para análisis de patrones'
    },
    'events': {
        'days': 365,  # 1 año
        'rationale': 'Análisis anuales y reportes'
    },
    'temp': {
        'days': 7,  # 1 semana
        'rationale': 'Datos temporales de procesamiento'
    }
}

# Implementación en etl_maintenance.py
def cleanup_old_data(table_name: str, retention_days: int):
    """Elimina datos antiguos para reducir costos de almacenamiento."""
    cutoff_date = pendulum.now("UTC").subtract(days=retention_days)
    
    # Contar antes de eliminar (para logging)
    count_before = count_rows_older_than(table_name, cutoff_date)
    
    # Eliminar
    delete_older_than(table_name, cutoff_date)
    
    # Contar después
    count_after = count_rows_older_than(table_name, cutoff_date)
    
    logger.info(f"Cleanup {table_name}: removed {count_before - count_after} rows")
    
    # Calcular ahorro estimado (asumiendo ~1KB por fila)
    saved_bytes = (count_before - count_after) * 1024
    saved_gb = saved_bytes / (1024 ** 3)
    # Asumiendo $0.023/GB/mes (AWS RDS PostgreSQL)
    monthly_savings = saved_gb * 0.023
    
    logger.info(f"Estimated monthly savings: ${monthly_savings:.2f}")
```

#### 4. Rate Limiting Inteligente (Control de Costos de API)

```python
# Configuración de rate limits por costo
API_COSTS = {
    'openai_api': {
        'max_calls': 100,  # Límite bajo para API cara
        'window_seconds': 60,
        'cost_per_call': 0.002,  # $0.002 por llamada
        'rationale': 'OpenAI es costoso, limitar para controlar gastos'
    },
    'hubspot_api': {
        'max_calls': 1000,  # Límite alto para API gratuita/barata
        'window_seconds': 60,
        'cost_per_call': 0.0,
        'rationale': 'API gratuita, mayor throughput permitido'
    },
    'stripe_api': {
        'max_calls': 500,
        'window_seconds': 60,
        'cost_per_call': 0.0001,
        'rationale': 'API moderadamente costosa'
    }
}

@rate_limit(
    max_calls=API_COSTS['openai_api']['max_calls'],
    window_seconds=API_COSTS['openai_api']['window_seconds'],
    variable_key="openai_api"
)
def call_openai_api(prompt: str):
    """Llamada protegida por rate limiting basado en costo."""
    # Implementación
    pass

# Tracking de costos
def track_api_cost(api_name: str, calls: int):
    """Registra costo de llamadas a API."""
    cost_per_call = API_COSTS[api_name]['cost_per_call']
    total_cost = calls * cost_per_call
    
    Stats.gauge(f"api_costs.{api_name}.total_usd", total_cost)
    Stats.incr(f"api_costs.{api_name}.calls", calls)
```

#### 5. Optimización de Queries SQL

```python
# Antes: Query ineficiente
def inefficient_query():
    """Query que escanea toda la tabla."""
    sql = """
        SELECT * 
        FROM transactions 
        WHERE status = 'completed'
        ORDER BY created_at DESC
    """
    # Escanea todas las filas, luego filtra

# Después: Query optimizada
def optimized_query():
    """Query que usa índice y limita resultados."""
    sql = """
        SELECT id, amount, created_at 
        FROM transactions 
        WHERE status = 'completed'
          AND created_at >= NOW() - INTERVAL '30 days'  -- Filtro temporal
        ORDER BY created_at DESC
        LIMIT 1000  -- Solo lo necesario
    """
    # Usa índice en (status, created_at)
    # Filtro temporal reduce datos escaneados
    # LIMIT evita transferir datos innecesarios

# Análisis de queries costosas
def analyze_expensive_queries():
    """Identifica queries que consumen más recursos."""
    sql = """
        SELECT 
            query,
            calls,
            total_exec_time,
            mean_exec_time,
            (total_exec_time / SUM(total_exec_time) OVER ()) * 100 as pct_total
        FROM pg_stat_statements
        ORDER BY total_exec_time DESC
        LIMIT 10
    """
    # Usar para identificar queries a optimizar
```

#### 6. Almacenamiento Eficiente

```sql
-- Usar tipos de datos apropiados (reducir tamaño)
-- Antes: VARCHAR(255) para todos los campos
-- Después: Tipos específicos
CREATE TABLE optimized_table (
    id BIGSERIAL,  -- 8 bytes vs INT (4 bytes) para IDs grandes
    status VARCHAR(20),  -- Solo lo necesario, no VARCHAR(255)
    amount DECIMAL(10, 2),  -- Decimal en lugar de FLOAT para precisión
    metadata JSONB,  -- JSONB comprimido vs JSON sin comprimir
    created_at TIMESTAMPTZ  -- Con timezone para precisión
);

-- Compresión en PostgreSQL
ALTER TABLE large_table SET (
    fillfactor = 90,  -- Dejar espacio para updates
    autovacuum_vacuum_scale_factor = 0.05  -- Vacuum más frecuente
);

-- Particionamiento para reducir tamaño de índices
-- Índices más pequeños = menos memoria = menos costo
```

#### 7. Spot Instances y Auto-scaling

```yaml
# Kubernetes: Usar spot instances para workers
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-worker
spec:
  template:
    spec:
      nodeSelector:
        instance-type: spot  # Usar spot instances (50-90% más barato)
      tolerations:
      - key: instance-type
        operator: Equal
        value: spot
        effect: NoSchedule
```

#### 8. Monitoreo de Costos

```python
# Métricas de costo a trackear
COST_METRICS = {
    "compute_cost_per_hour": "Costo de instancias EC2/K8s",
    "storage_cost_per_gb_month": "Costo de almacenamiento DB",
    "api_calls_cost": "Costo acumulado de llamadas a APIs",
    "data_transfer_cost": "Costo de transferencia de datos",
    "total_monthly_cost": "Costo total estimado mensual",
}

def estimate_monthly_cost():
    """Estima costo mensual del ETL."""
    # Compute: workers * cost_per_hour * hours_per_month
    compute_cost = 4 * 0.10 * 730  # 4 workers, $0.10/hr, 730 hrs/mes = $292
    
    # Storage: gb_stored * cost_per_gb
    storage_cost = 500 * 0.023  # 500GB, $0.023/GB/mes = $11.50
    
    # API calls: calls * cost_per_call
    api_cost = 100000 * 0.002  # 100K calls, $0.002/call = $200
    
    total = compute_cost + storage_cost + api_cost
    logger.info(f"Estimated monthly cost: ${total:.2f}")
    return total
```

### Comparación de Costos por Estrategia

| Estrategia | Ahorro Estimado | Esfuerzo | Impacto |
|------------|-----------------|----------|--------|
| Limpieza proactiva | 20-30% | Bajo | Alto |
| Materialized views | 15-25% | Medio | Alto |
| Optimización de queries | 10-20% | Medio | Medio |
| Tuning de chunks | 5-15% | Bajo | Medio |
| Rate limiting | 10-30% (APIs) | Bajo | Alto |
| Spot instances | 50-90% (compute) | Alto | Alto |
| Particionamiento | 5-10% | Alto | Medio |

## Guía Rápida de Referencia

### Comandos Airflow Comunes

```bash
# Listar DAGs
airflow dags list

# Ver detalles de DAG
airflow dags show etl_example

# Trigger DAG con conf
airflow dags trigger etl_example --conf '{"rows": 5000}'

# Ver logs de última corrida
airflow tasks logs etl_example extract $(date +%Y-%m-%d)

# Test task
airflow tasks test etl_example extract $(date +%Y-%m-%d)

# Listar variables
airflow variables list

# Ver variable específica
airflow variables get rate_limit:mlflow_api

# Ver conexiones
airflow connections list
```

### Variables Importantes

- `rate_limit:{service}`: Estado de rate limiting
- `cb:failures:{dag_id}`: Circuit breaker state
- `idemp:{dag_id}:{key}`: Idempotency locks
- `onboarding_start_ts:{dag_id}:{run_id}`: Timestamps de inicio
- `kpi_monthly_complete:{dag_id}:{month}`: Reportes completados

### Logs Estructurados - Buscar Por

- `dag_run_id`: Correlación completa de una ejecución
- `component`: Filtro por tipo de tarea
- `duration_ms`: Performance issues
- `error`: Errores específicos
- `employee_email`: Tracking de onboarding específico

### Health Checks

```bash
# API Health
curl http://your-app/api/etl/health

# DAG Health (via task test)
airflow tasks test etl_example health_check $(date +%Y-%m-%d)
```

### Troubleshooting Común

| Problema | Solución |
|----------|----------|
| Rate limit exceeded | Verificar `rate_limit:{service}` variable, esperar ventana |
| Circuit breaker open | Revisar logs, esperar reset window, o reset manual |
| Idempotency lock hit | Verificar si es duplicado intencional, usar `allow_overwrite=true` |
| Validation failures | Revisar schema esperado vs datos reales en logs |
| Timeout errors | Revisar volumen de datos, ajustar timeouts o chunk size |

## Inventario Completo de DAGs

### ETL Core (8 DAGs)
- **`etl_example`** - Pipeline ETL principal mejorado (triggered por Dataset)
- **`etl_improved`** - Pipeline ETL alternativo (`@daily`)
- **`etl_consumer`** - Consumidor post-ETL con alertas
- **`etl_maintenance`** - Mantenimiento semanal (`@weekly`)
- **`post_etl_consumer`** - Consumidor adicional post-ETL
- **`post_etl_report`** - Reportes post-ETL
- **`source_producer`** - Productor de datos fuente
- **`etl_downstream_example`** - Ejemplo de downstream processing

### KPIs y Reportes (8 DAGs)
- **`kpi_aggregate_daily`** - Agregación diaria de KPIs
- **`kpi_reports`** - Reportes base de KPIs
- **`kpi_reports_weekly`** - Reportes semanales
- **`kpi_reports_monthly`** - Reportes mensuales con comparación MoM
- **`kpi_refresh_materialized`** - Refresh de vistas materializadas
- **`refresh_kpi_materialized`** - Refresh alternativo
- **`kpi_dq_health_checks`** - Health checks de calidad de datos
- **`kpi_query_performance`** - Monitoreo de performance de queries

### Financiero (13 DAGs) - Ver `INDEX_FINANCIAL.md`
- **Facturación**: `invoice_generate`, `credit_notes`
- **Pagos**: `payment_reminders`, `invoice_mark_paid`, `payment_partial`
- **Conciliación**: `bank_reconcile`, `stripe_reconcile`
- **Reportes**: `financial_reports`, `financial_export`, `export_accounting`, `financial_summary`
- **Alertas**: `invoice_alerts`, `invoice_deduplication`, `invoice_audit`

### Marketing y Leads (6 DAGs)
- **`leads_sync_hubspot`** - Sincronización bidireccional con HubSpot
- **`hubspot_update_estado_interes`** - Actualización de propiedad 'estado_interés' de contactos HubSpot
- **`lead_nurturing`** - Automatización de nutrición de leads
- **`outreach_multichannel`** - Campañas multi-canal (email, SMS, WhatsApp)
- **`outreach_dlq_retry`** - Retry automático de mensajes fallidos
- **`outreach_unsubscribe_sync`** - Sincronización de unsubscribes

### Operaciones (1 DAG)
- **`employee_onboarding`** - Onboarding automatizado de empleados

### Utilidades y Tests
- **`etl_config_constants.py`** - Constantes de configuración
- **`etl_optimizations.py`** - Utilidades de optimización
- **`etl_utils.py`** - Utilidades generales ETL
- **Tests**: `test_etl_example.py`, `test_etl_utils.py`, `test_dq_helper.py`

**Total: 35+ DAGs en producción**

## Integración Entre Sistemas

### Flujo ETL → Financiero

```python
# Ejemplo: Después de procesar ventas, generar facturas
@task
def generate_invoices_from_sales(payload: ExtractPayload):
    """Trigger invoice_generate desde datos ETL."""
    sales = payload.get("sales_data", [])
    for sale in sales:
        trigger_dag_run(
            dag_id="invoice_generate",
            conf={
                "sales": [{
                    "id": sale.get("id"),
                    "amount": sale.get("total"),
                    "currency": sale.get("currency", "USD"),
                    "description": sale.get("product_name")
                }]
            },
            replace_microseconds=False
        )
    return payload
```

### Flujo Marketing → ETL

```python
# Ejemplo: Leads de HubSpot → ETL para análisis
@task
def sync_leads_to_etl():
    """Sincronizar leads para procesamiento ETL."""
    from data.airflow.plugins.db import get_conn
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO leads_etl (ext_id, email, score, created_at)
                SELECT ext_id, email, score, created_at
                FROM leads
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
            conn.commit()
    
    # Trigger ETL para procesar nuevos leads
    trigger_dag_run(dag_id="etl_example", conf={"source": "leads"})
```

### Pipeline Completo: Lead → ETL → Invoice

```
leads_sync_hubspot (Hourly)
    ↓
etl_example (Process leads)
    ↓
kpi_aggregate_daily (Update metrics)
    ↓
outreach_multichannel (If lead qualified)
    ↓
[If converted] → invoice_generate (Create invoice)
    ↓
payment_reminders (If not paid)
```

## Casos de Uso Avanzados

### Caso 1: ETL con Retry Inteligente

```python
from airflow.models import Variable
from airflow.exceptions import AirflowFailException

def smart_retry_with_backoff(max_retries: int = 3):
    """Decorator para retry con backoff exponencial."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = 2 ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed, waiting {wait_time}s")
                    time.sleep(wait_time)
        return wrapper
    return decorator

@smart_retry_with_backoff(max_retries=3)
@task
def unreliable_external_api():
    return call_external_api()
```

### Caso 2: Chunking Dinámico Basado en Performance

```python
from data.airflow.plugins.etl_performance import PerformanceTracker

def adaptive_chunk_size(total_rows: int, base_size: int = 1000) -> int:
    """Calcula chunk size óptimo basado en performance histórica."""
    tracker = PerformanceTracker("transform")
    historical_stats = Variable.get("perf:transform:stats", default_var="{}")
    
    if historical_stats:
        stats = json.loads(historical_stats)
        avg_time = stats.get("mean_ms", 1000)
        
        # Si promedio < 500ms, aumentar chunk size
        if avg_time < 500:
            return min(base_size * 2, total_rows)
        # Si promedio > 2000ms, reducir chunk size
        elif avg_time > 2000:
            return max(base_size // 2, 100)
    
    return base_size
```

### Caso 3: Validación Multi-Capa con Great Expectations

```python
from great_expectations.core import ExpectationSuite

@task
def multi_layer_validation(payload: ExtractPayload):
    """Validación en múltiples capas."""
    # Capa 1: Schema básico
    validate_and_raise(payload, strict=False)
    
    # Capa 2: Reglas de negocio
    rows = payload.get("rows", 0)
    if rows < 100:
        raise AirflowFailException(f"Too few rows: {rows}")
    
    # Capa 3: Great Expectations (si disponible)
    try:
        import great_expectations as ge
        df = pd.DataFrame(payload.get("data", []))
        suite = ExpectationSuite("sales_expectations")
        results = df.validate(expectation_suite=suite)
        
        if not results.success:
            logger.warning(f"GE validation warnings: {results.statistics}")
    except ImportError:
        logger.debug("Great Expectations not available")
    
    return payload
```

## Métricas de Negocio

### KPIs Operacionales

```python
# Métricas a trackear en todos los DAGs
BUSINESS_METRICS = {
    "etl_example": {
        "rows_processed": "etl_example.rows.processed",
        "processing_time": "etl_example.duration.total_ms",
        "success_rate": "etl_example.success.rate",
        "cost_per_row": "etl_example.cost.per_row",
    },
    "invoice_generate": {
        "invoices_created": "financial.invoices.created",
        "total_revenue": "financial.revenue.total",
        "avg_invoice_amount": "financial.invoice.avg_amount",
    },
    "employee_onboarding": {
        "onboarding_time": "hr.onboarding.duration_ms",
        "success_rate": "hr.onboarding.success_rate",
        "accounts_created": "hr.accounts.created",
    }
}
```

### Dashboard Consolidado

```python
# Query para dashboard unificado
SELECT 
    dag_id,
    DATE(execution_date) as date,
    COUNT(*) as total_runs,
    SUM(CASE WHEN state = 'success' THEN 1 ELSE 0 END) as success_count,
    AVG(duration) as avg_duration_ms
FROM dag_run
WHERE execution_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY dag_id, DATE(execution_date)
ORDER BY date DESC, dag_id;
```

## Monitoreo Proactivo Avanzado

### Alertas Inteligentes

```python
def intelligent_alerting(dag_id: str, metrics: dict):
    """Alertas basadas en tendencias y thresholds."""
    # 1. Comparar con baseline histórico
    baseline = Variable.get(f"baseline:{dag_id}", default_var="{}")
    if baseline:
        base_dict = json.loads(baseline)
        for metric, value in metrics.items():
            baseline_value = base_dict.get(metric, 0)
            if baseline_value > 0:
                deviation = abs(value - baseline_value) / baseline_value
                if deviation > 0.3:  # 30% desviación
                    notify_slack(
                        f"⚠️ {dag_id}: {metric} deviated {deviation*100:.1f}% "
                        f"from baseline ({value} vs {baseline_value})"
                    )
    
    # 2. Actualizar baseline (rolling average)
    if baseline:
        base_dict = json.loads(baseline)
        for metric, value in metrics.items():
            current_base = base_dict.get(metric, value)
            base_dict[metric] = (current_base * 0.9) + (value * 0.1)  # EMA
    else:
        base_dict = metrics
    
    Variable.set(f"baseline:{dag_id}", json.dumps(base_dict))
```

## Optimización de Recursos

### Resource Pools Estratégicos

```python
# Configurar pools según prioridad
AIRFLOW_POOLS = {
    "critical": {
        "slots": 10,
        "description": "DAGs críticos de negocio"
    },
    "etl_pool": {
        "slots": 20,
        "description": "ETL pipelines estándar"
    },
    "batch": {
        "slots": 5,
        "description": "Procesamiento batch pesado"
    },
    "reporting": {
        "slots": 3,
        "description": "Reportes y analytics"
    }
}
```

### Auto-scaling de Chunks

```python
def auto_scale_chunks(
    total_rows: int,
    available_memory_mb: int = 2048,
    target_duration_ms: int = 5000
) -> int:
    """Calcula chunks óptimos basado en recursos disponibles."""
    # Estimar memoria por fila (MB)
    memory_per_row_mb = 0.001  # Ajustar según datos reales
    
    # Máximo rows que caben en memoria
    max_rows_in_memory = int(available_memory_mb * 0.8 / memory_per_row_mb)
    
    # Chunks necesarios para durar ~target_duration_ms
    # Asumiendo ~100 rows/ms de throughput
    throughput_per_ms = 100
    rows_per_chunk_ideal = int(target_duration_ms * throughput_per_ms)
    
    # Balancear memoria y throughput
    chunk_size = min(max_rows_in_memory, rows_per_chunk_ideal)
    
    # Redondear a múltiplo de 100
    chunk_size = ((chunk_size + 99) // 100) * 100
    
    return max(100, min(chunk_size, total_rows))
```

## Troubleshooting Avanzado

### Diagnóstico Completo de DAG

```python
def diagnose_dag_execution(dag_id: str, run_id: str):
    """Diagnóstico completo de una ejecución de DAG."""
    from airflow.models import DagRun, TaskInstance
    
    dag_run = DagRun.find(dag_id=dag_id, run_id=run_id)
    if not dag_run:
        return None
    
    tasks = TaskInstance.find(dag_id=dag_id, run_id=run_id)
    
    diagnosis = {
        "dag_run": {
            "state": dag_run.state,
            "start_date": dag_run.start_date.isoformat() if dag_run.start_date else None,
            "end_date": dag_run.end_date.isoformat() if dag_run.end_date else None,
            "duration": (dag_run.end_date - dag_run.start_date).total_seconds() if dag_run.end_date and dag_run.start_date else None,
        },
        "tasks": []
    }
    
    for task in tasks:
        task_diag = {
            "task_id": task.task_id,
            "state": task.state,
            "duration": task.duration if task.duration else None,
            "try_number": task.try_number,
            "log_url": task.log_url if hasattr(task, 'log_url') else None,
        }
        diagnosis["tasks"].append(task_diag)
    
    return diagnosis
```

### Análisis de Bottlenecks

```python
def analyze_bottlenecks(dag_id: str, days: int = 7):
    """Analiza cuellos de botella en un DAG."""
    query = f"""
    SELECT 
        task_id,
        AVG(duration) as avg_duration,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration) as p95_duration,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration) as p99_duration,
        COUNT(*) as executions,
        SUM(CASE WHEN state = 'failed' THEN 1 ELSE 0 END) as failures
    FROM task_instance
    WHERE dag_id = '{dag_id}'
    AND execution_date >= CURRENT_DATE - INTERVAL '{days} days'
    AND state IN ('success', 'failed')
    GROUP BY task_id
    ORDER BY avg_duration DESC
    """
    
    # Identificar tareas lentas (p95 > 2x promedio)
    # Identificar tareas con alta tasa de fallo (>5%)
    # Identificar tareas con alta variabilidad (p99 >> p95)
```

## ⚠️ Anti-patterns Comunes y Cómo Evitarlos

### Anti-pattern 1: Sin Validación de Parámetros

**❌ Malo:**
```python
@task
def my_task():
    rows = context["params"]["rows"]  # Sin validación
    process_data(rows)  # Puede fallar silenciosamente
```

**✅ Bueno:**
```python
@task
def my_task():
    params = validate_params(context["params"])  # Valida tipos, rangos
    rows = params["rows"]  # Ya validado
    process_data(rows)
```

### Anti-pattern 2: Catching Genérico Sin Contexto

**❌ Malo:**
```python
try:
    result = call_api()
except:  # Catching genérico
    pass  # Silencia errores
```

**✅ Bueno:**
```python
try:
    result = call_api()
except requests.exceptions.RequestException as e:
    logger.error("API call failed", extra={
        "url": url,
        "status_code": getattr(e.response, 'status_code', None),
        "error": str(e)
    }, exc_info=True)
    raise AirflowFailException(f"API call failed: {e}") from e
```

### Anti-pattern 3: Sin Idempotencia

**❌ Malo:**
```python
@task
def load():
    # Siempre ejecuta, puede duplicar datos
    insert_to_db(data)
```

**✅ Bueno:**
```python
@task
def load():
    lock_key = f"idemp:{dag_id}:{run_id}:{checksum}"
    if _idemp_should_skip(lock_key):
        logger.info("Skipping duplicate load")
        return
    _idemp_set(lock_key, ttl_seconds=86400)
    insert_to_db(data)
```

### Anti-pattern 4: SQL Injection Vulnerable

**❌ Malo:**
```python
cur.execute(f"SELECT * FROM {table_name} WHERE id = '{user_id}'")
```

**✅ Bueno:**
```python
from psycopg2.sql import SQL, Identifier, Literal

# Para nombres de tablas/columnas
cur.execute(SQL("SELECT * FROM {} WHERE id = {}").format(
    Identifier(table_name),
    Literal(user_id)
))

# O usando parámetros preparados
cur.execute("SELECT * FROM %s WHERE id = %s", (table_name, user_id))
```

### Anti-pattern 5: Sin Rate Limiting en APIs

**❌ Malo:**
```python
for item in items:
    api_call(item)  # Puede exceder límites de API
```

**✅ Bueno:**
```python
@rate_limit(max_calls=20, window_seconds=60)
def api_call_safe(item):
    return api_call(item)

for item in items:
    api_call_safe(item)
```

### Anti-pattern 6: Logging Inseguro (Exponer Secrets)

**❌ Malo:**
```python
logger.info(f"API key: {api_key}")  # Expone secretos
logger.debug(f"Password: {password}")
```

**✅ Bueno:**
```python
# En etl_notifications.py se sanitiza automáticamente
notify_slack("Error", extra_context={
    "api_key": api_key  # Se redacta automáticamente
})

# En código manual
logger.info("API call", extra={
    "api_key": "***REDACTED***" if api_key else None
})
```

### Anti-pattern 7: Sin Timeout en Tareas

**❌ Malo:**
```python
@task  # Sin timeout
def long_running_task():
    # Puede ejecutarse indefinidamente
    process_huge_dataset()
```

**✅ Bueno:**
```python
@task(execution_timeout=timedelta(minutes=30))
def long_running_task():
    process_huge_dataset()
```

### Anti-pattern 8: Chunks Demasiado Grandes o Pequeños

**❌ Malo:**
```python
chunks = [data[i:i+10] for i in range(0, len(data), 10)]  # Chunks muy pequeños
# O
chunks = [data]  # Un chunk gigante
```

**✅ Bueno:**
```python
# Usar chunking adaptativo
chunk_size = _adaptive_chunk_size(
    total_rows=len(data),
    max_chunks=MAX_CHUNKS,
    base_chunk_size=100_000
)
chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
```

### Anti-pattern 9: Sin Circuit Breaker

**❌ Malo:**
```python
@task(retries=10)  # Reintentos infinitos
def call_unreliable_api():
    api.call()  # Puede fallar repetidamente
```

**✅ Bueno:**
```python
@task(retries=3)
def call_unreliable_api():
    if _cb_is_open(dag_id, threshold=5, reset_minutes=15):
        raise AirflowFailException("Circuit breaker open")
    api.call()
```

### Anti-pattern 10: Sin Validación de DQ

**❌ Malo:**
```python
@task
def load():
    insert_all(data)  # Sin verificar calidad
```

**✅ Bueno:**
```python
@task
def dq_check(payload):
    rows = payload["rows"]
    min_rows = get_config_value("DQ_MIN_ROWS", 1)
    max_rows = get_config_value("DQ_MAX_ROWS", 10_000_000)
    validate_rows_range(rows, min_rows, max_rows)
    return payload

dq_checked = dq_check(transformed)
load(dq_checked)
```

## 🚀 Guía Completa de Migración desde DAGs Legacy

### Paso 1: Evaluación del DAG Existente

**Checklist de Evaluación:**
- [ ] ¿Tiene validación de parámetros?
- [ ] ¿Implementa idempotencia?
- [ ] ¿Tiene manejo de errores robusto?
- [ ] ¿Usa logging estructurado?
- [ ] ¿Tiene métricas y observabilidad?
- [ ] ¿Tiene timeouts configurados?
- [ ] ¿Maneja rate limiting?
- [ ] ¿Valida calidad de datos?

### Paso 2: Migración Incremental

#### 2.1 Agregar Validación de Parámetros

**Antes:**
```python
@dag
def legacy_etl():
    @task
    def extract():
        rows = context["params"]["rows"]  # Sin validación
        return {"rows": rows}
```

**Después:**
```python
from data.airflow.plugins.etl_config import validate_params

@dag
def legacy_etl():
    @task
    def extract():
        params = validate_params(context["params"])  # Validado
        rows = params["rows"]
        return {"rows": rows}
```

#### 2.2 Agregar Logging Estructurado

**Antes:**
```python
logger.info(f"Processing {rows} rows")
```

**Después:**
```python
from data.airflow.plugins.etl_logging import log_with_context

log_with_context(
    logger,
    logging.INFO,
    "Processing rows",
    task_id="extract",
    dag_run_id=run_id,
    rows=rows
)
```

#### 2.3 Agregar Idempotencia

**Antes:**
```python
@task
def load(data):
    insert_to_db(data)  # Siempre ejecuta
```

**Después:**
```python
from airflow.models import Variable
import hashlib
import json

@task
def load(data):
    # Generar checksum del payload
    checksum = hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()
    
    lock_key = f"idemp:{dag_id}:{checksum}"
    
    # Verificar idempotencia
    if Variable.get(lock_key, default_var=None):
        logger.warning("Duplicate load, skipping")
        return
    
    # Ejecutar y setear lock
    Variable.set(lock_key, str(pendulum.now().int_timestamp))
    insert_to_db(data)
```

#### 2.4 Agregar Rate Limiting

**Antes:**
```python
@task
def call_api():
    response = requests.get("https://api.example.com/data")
    return response.json()
```

**Después:**
```python
from data.airflow.plugins.etl_rate_limit import rate_limit

@task
@rate_limit(max_calls=10, window_seconds=60)
def call_api():
    response = requests.get("https://api.example.com/data")
    return response.json()
```

#### 2.5 Agregar Validación de DQ

**Antes:**
```python
@task
def transform(data):
    return process(data)
```

**Después:**
```python
from data.airflow.plugins.etl_validation import (
    validate_payload_schema,
    validate_rows_range
)

@task
def transform(data):
    # Validar schema
    is_valid, errors = validate_payload_schema(data)
    if not is_valid:
        raise AirflowFailException(f"Schema validation failed: {errors}")
    
    # Validar rangos
    rows = data.get("rows", 0)
    validate_rows_range(rows, min_rows=1, max_rows=1_000_000)
    
    return process(data)
```

#### 2.6 Agregar Circuit Breaker

**Antes:**
```python
@task(retries=10)
def call_unreliable_service():
    service.call()
```

**Después:**
```python
from data.airflow.dags.etl_example import _cb_is_open, _cb_record_failure

@task(retries=3)
def call_unreliable_service():
    dag_id = context.get("dag").dag_id
    
    # Verificar circuit breaker
    if _cb_is_open(dag_id, threshold=5, reset_minutes=15):
        raise AirflowFailException("Circuit breaker is open")
    
    try:
        service.call()
    except Exception as e:
        _cb_record_failure(dag_id)
        raise
```

### Paso 3: Migración Completa - Plantilla

```python
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException

# Importar plugins mejorados
from data.airflow.plugins.etl_config import validate_params
from data.airflow.plugins.etl_logging import get_task_logger, log_with_context
from data.airflow.plugins.etl_validation import validate_payload_schema
from data.airflow.plugins.etl_rate_limit import rate_limit
from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_tracing import start_span
from data.airflow.plugins.etl_notifications import notify_slack

logger = get_task_logger()

@dag(
    dag_id="migrated_etl",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "on_failure_callback": on_task_failure,
    },
)
def migrated_etl():
    @task(
        execution_timeout=timedelta(minutes=10),
        on_failure_callback=on_task_failure,
    )
    def extract() -> Dict[str, Any]:
        """Extract with validation and logging."""
        ctx = get_current_context()
        params = validate_params(ctx["params"])
        
        with start_span("migrated_etl.extract"):
            log_with_context(
                logger,
                logging.INFO,
                "Starting extraction",
                task_id="extract",
                dag_run_id=ctx.get("run_id"),
                rows=params["rows"]
            )
            
            # Your extraction logic here
            data = fetch_data(params["rows"])
            
            log_with_context(
                logger,
                logging.INFO,
                "Extraction completed",
                task_id="extract",
                rows=len(data)
            )
            
            return {"data": data, "rows": len(data)}
    
    @task(
        execution_timeout=timedelta(minutes=15),
        on_failure_callback=on_task_failure,
    )
    @rate_limit(max_calls=20, window_seconds=60)
    def transform(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Transform with validation."""
        # Validate schema
        is_valid, errors = validate_payload_schema(payload)
        if not is_valid:
            raise AirflowFailException(f"Validation failed: {errors}")
        
        with start_span("migrated_etl.transform"):
            data = payload["data"]
            transformed = process_data(data)
            
            return {"data": transformed, "rows": len(transformed), "transformed": True}
    
    @task(
        execution_timeout=timedelta(minutes=5),
        on_failure_callback=on_task_failure,
    )
    def load(payload: Dict[str, Any]) -> None:
        """Load with idempotency."""
        ctx = get_current_context()
        dag_id = ctx.get("dag").dag_id
        run_id = ctx.get("run_id")
        
        # Idempotency check
        from airflow.models import Variable
        lock_key = f"idemp:{dag_id}:{run_id}"
        
        if Variable.get(lock_key, default_var=None):
            logger.warning("Duplicate load, skipping", extra={"lock_key": lock_key})
            return
        
        Variable.set(lock_key, str(pendulum.now().int_timestamp))
        
        try:
            with start_span("migrated_etl.load"):
                insert_to_db(payload["data"])
                notify_slack(f":white_check_mark: migrated_etl completed")
        finally:
            # Optionally clean up lock after successful load
            pass
    
    extracted = extract()
    transformed = transform(extracted)
    load(transformed)

dag = migrated_etl()
```

### Paso 4: Testing Post-Migración

1. **Ejecutar en modo dry_run:**
   ```bash
   airflow dags trigger migrated_etl --conf '{"dry_run": true}'
   ```

2. **Verificar métricas:**
   ```bash
   # Verificar que se registren métricas
   airflow dags test migrated_etl
   ```

3. **Validar logs estructurados:**
   ```bash
   # Buscar logs con estructura
   grep "dag_run_id" airflow-logs/migrated_etl/extract/*.log
   ```

4. **Probar idempotencia:**
   ```bash
   # Trigger dos veces con mismo payload
   airflow dags trigger migrated_etl --conf '{"rows": 1000}'
   airflow dags trigger migrated_etl --conf '{"rows": 1000}'
   # Segunda ejecución debe saltarse load
   ```

## 🔧 Escalabilidad Avanzada - Guías Detalladas

### Escalado Horizontal con Kubernetes HPA

**Configurar HPA para Airflow Workers:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: airflow-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: airflow-worker
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
```

**Monitoreo de Auto-scaling:**

```python
# Métricas para trigger de scaling
from airflow.stats import Stats

# Registrar métricas de carga
Stats.gauge("airflow.worker.queue_length", queue_length)
Stats.gauge("airflow.worker.active_tasks", active_tasks)
Stats.gauge("airflow.worker.pool_utilization", pool_utilization)
```

### Escalado Vertical - Optimización de Memoria

**Tuning de Chunks Dinámicos:**

```python
def calculate_optimal_chunk_size(
    available_memory_mb: int,
    row_size_bytes: int,
    parallelism_target: int
) -> int:
    """
    Calcula chunk size óptimo basado en memoria disponible.
    
    Args:
        available_memory_mb: Memoria disponible por worker (MB)
        row_size_bytes: Tamaño promedio de fila en bytes
        parallelism_target: Paralelismo deseado
        
    Returns:
        Chunk size óptimo en número de filas
    """
    # Reserver 30% de memoria para overhead del sistema
    usable_memory_mb = available_memory_mb * 0.7
    
    # Memoria por chunk = memoria disponible / paralelismo
    memory_per_chunk_mb = usable_memory_mb / parallelism_target
    memory_per_chunk_bytes = memory_per_chunk_mb * 1024 * 1024
    
    # Chunk size = memoria disponible / tamaño de fila
    chunk_size = int(memory_per_chunk_bytes / row_size_bytes)
    
    # Limitar entre 1K y 1M filas
    return max(1_000, min(chunk_size, 1_000_000))
```

### Optimización de Base de Datos - Particionamiento

**Particionamiento Automático por Mes:**

```sql
-- Tabla particionada
CREATE TABLE etl_events (
    id BIGSERIAL,
    event_type VARCHAR(50),
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Crear particiones automáticamente
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    start_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    end_date := start_date + INTERVAL '1 month';
    partition_name := 'etl_events_' || TO_CHAR(start_date, 'YYYY_MM');
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF etl_events
         FOR VALUES FROM %L TO %L',
        partition_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;

-- Ejecutar mensualmente (via DAG)
SELECT create_monthly_partition();
```

**Índices Estratégicos:**

```sql
-- Índice compuesto para queries comunes
CREATE INDEX CONCURRENTLY idx_events_type_created 
ON etl_events(event_type, created_at DESC);

-- Índice GIN para búsquedas en JSONB
CREATE INDEX CONCURRENTLY idx_events_payload_gin 
ON etl_events USING GIN (payload);

-- Índice parcial para datos recientes
CREATE INDEX CONCURRENTLY idx_events_recent 
ON etl_events(created_at DESC) 
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';
```

### Connection Pooling Optimizado

```python
from psycopg2 import pool
import os

# Pool global por worker
_db_pool = None

def get_db_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,  # Ajustar según carga
            dsn=os.getenv("DATABASE_URL"),
            options="-c statement_timeout=30000"  # 30s timeout
        )
    return _db_pool

@task
def db_operation():
    conn = get_db_pool().getconn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM table")
        return cur.fetchall()
    finally:
        get_db_pool().putconn(conn)
```

## 📚 Referencia Rápida - Cheat Sheet

### Comandos Esenciales

```bash
# === VERIFICACIÓN ===
# Listar DAGs
airflow dags list | grep etl

# Ver detalles de DAG
airflow dags show etl_example

# Ver últimas ejecuciones
airflow dags list-runs etl_example --state failed --limit 5

# === EJECUCIÓN ===
# Trigger DAG con parámetros
airflow dags trigger etl_example --conf '{
  "rows": 5000,
  "chunk_rows": 1000,
  "dry_run": false
}'

# Test de tarea individual
airflow tasks test etl_example health_check $(date +%Y-%m-%d)

# === MONITOREO ===
# Ver logs de tarea
airflow tasks logs etl_example extract $(date +%Y-%m-%d) | tail -50

# Ver estado de circuit breaker
airflow variables get cb:failures:etl_example | jq

# Ver rate limit actual
airflow variables get rate_limit:mlflow_api | jq

# === CONFIGURACIÓN ===
# Setear variables
airflow variables set ETL_POOL "etl_pool"
airflow variables set MAX_CHUNKS 100

# Listar variables
airflow variables list | grep -E "ETL|rate_limit|cb:"

# === TROUBLESHOOTING ===
# Health check manual
airflow tasks test etl_example health_check $(date +%Y-%m-%d)

# Ver errores de importación
airflow dags list-import-errors

# Reset circuit breaker (después de resolver problema)
airflow variables delete cb:failures:etl_example
```

### Variables Clave

| Variable | Tipo | Descripción | Ejemplo |
|----------|------|-------------|---------|
| `ETL_POOL` | String | Pool de Airflow para tareas ETL | `etl_pool` |
| `MAX_CHUNKS` | Int | Máximo número de chunks paralelos | `100` |
| `DQ_MIN_ROWS` | Int | Mínimo de filas esperadas | `1` |
| `DQ_MAX_ROWS` | Int | Máximo de filas esperadas | `1000000` |
| `rate_limit:{service}` | JSON | Estado de rate limiting | `{"count": 5, "window_start": 123456}` |
| `cb:failures:{dag_id}` | JSON | Estado del circuit breaker | `{"count": 3, "last_failure_ts": 123456}` |
| `idemp:{dag_id}:{key}` | String | Lock de idempotencia | `idemp:etl_example:abc123` |

### Parámetros de DAG Comunes

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `rows` | int | `1000` | Número de filas a procesar |
| `chunk_rows` | int | `1000` | Tamaño de chunk |
| `since` | string | - | Ventana temporal inicio (ISO 8601) |
| `until` | string | - | Ventana temporal fin (ISO 8601) |
| `idempotency_ttl_minutes` | int | `60` | TTL para locks de idempotencia |
| `dry_run` | bool | `false` | Modo dry-run (no escribe a DB) |
| `run_name` | string | - | Identificador de ejecución |

### Código Snippets Rápidos

#### Rate Limiting
```python
from data.airflow.plugins.etl_rate_limit import rate_limit

@rate_limit(max_calls=10, window_seconds=60)
def call_api():
    return requests.post(api_url, json=data)
```

#### Validación
```python
from data.airflow.plugins.etl_validation import validate_and_raise

validate_and_raise(payload, strict=False)
```

#### Logging Estructurado
```python
from data.airflow.plugins.etl_logging import log_with_context

log_with_context(logger, logging.INFO, "Processing",
                 task_id="extract", rows=1000, dag_run_id=run_id)
```

#### Performance Tracking
```python
from data.airflow.plugins.etl_performance import track_performance

with track_performance("db_query"):
    results = query_database()
```

#### Circuit Breaker Check
```python
if _cb_is_open("etl_example", threshold=5):
    raise AirflowFailException("Circuit breaker is open")
```

#### Idempotencia
```python
lock_key = f"idemp:{dag_id}:{checksum}"
if _idemp_should_skip(lock_key):
    return  # Skip
_idemp_set(lock_key, ttl_seconds=3600)
```

### Métricas Importantes

```python
# Performance
Stats.gauge("etl_example.perf.transform.p95_ms")
Stats.gauge("etl_example.perf.load.p99_ms")
Stats.timing("etl_example.total_duration_ms", duration)

# Rate Limiting
Stats.increment("rate_limit.mlflow_api.hits")

# Validaciones
Stats.increment("etl_example.validate.success")
Stats.increment("etl_example.validate.failure")

# DQ
Stats.gauge("etl_example.dq.min_rows", rows)
Stats.gauge("etl_example.dq.deviation_pct", deviation)
```

### Troubleshooting Rápido

| Problema | Comando de Diagnóstico | Solución |
|----------|----------------------|----------|
| Rate limit | `airflow variables get rate_limit:mlflow_api \| jq` | Esperar reset o aumentar límite |
| Circuit breaker | `airflow variables get cb:failures:etl_example \| jq` | Reset manual si problema resuelto |
| Performance | `airflow tasks logs etl_example transform $(date +%Y-%m-%d)` | Revisar logs para cuellos de botella |
| Validación falla | `airflow tasks test etl_example validated $(date +%Y-%m-%d)` | Revisar schema y tipos de datos |
| Health check falla | `airflow tasks test etl_example health_check $(date +%Y-%m-%d)` | Verificar MLflow, pool, conexiones |

### Enlaces Rápidos

- 📖 [Quick Start](#quick-start-guía-rápida-de-inicio) - Empezar en 5 minutos
- 🔍 [Troubleshooting](#troubleshooting) - Resolver problemas comunes
- 📊 [Métricas y KPIs](#métricas-y-kpis) - Monitoreo y alertas
- 🏗️ [Arquitectura](#arquitectura-rápida) - Diagramas y diseño
- 💡 [FAQ](#faq) - Preguntas frecuentes
- 📋 [Checklist](#checklist-de-implementación) - Guía de implementación

---

**Última actualización**: 2025-01 - Sistema ETL enterprise-grade con 35+ DAGs, plugins mejorados, circuit breakers, rate limiting, observabilidad avanzada, integración con sistemas financieros y marketing, y automatizaciones de negocio listas para producción.

**Mejoras en esta versión del documento**:
- ✅ Guía rápida de inicio (Quick Start) completa
- ✅ Diagramas de flujo detallados (circuit breaker, idempotency, rate limiting)
- ✅ Troubleshooting expandido con casos reales y soluciones paso a paso
- ✅ Referencia rápida (Cheat Sheet) para uso diario
- ✅ Estructura mejorada con navegación más clara
- ✅ Ejemplos de código más completos y comentados
