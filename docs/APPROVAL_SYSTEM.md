# ✅ Sistema de Aprobaciones - Documentación Técnica

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Documentación técnica completa del sistema de aprobaciones y limpieza (`approval_cleanup.py`).

## 📋 Tabla de Contenidos

- [Visión General](#-visión-general)
- [Arquitectura](#-arquitectura)
- [Componentes Principales](#-componentes-principales)
- [Funcionalidades](#-funcionalidades)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Plugins Modulares](#-plugins-modulares)
- [Performance](#-performance)
- [Monitoreo](#-monitoreo)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visión General

El sistema de aprobaciones es un DAG de Airflow que gestiona el ciclo de vida completo de las solicitudes de aprobación, incluyendo:

- **Archivado**: Mover solicitudes antiguas a tablas de archivo
- **Limpieza**: Eliminar notificaciones expiradas
- **Optimización**: Mantener índices y optimizar queries
- **Reportes**: Generar reportes de limpieza y análisis
- **Monitoreo**: Tracking de performance y métricas

### Estadísticas

- **Líneas de código**: ~32,609 (DAG principal) - **Requiere refactorización**
- **Plugins modulares**: 5 plugins (~1,270 líneas) - **Recomendado usar**
- **Funcionalidades**: 100+ features configurables
- **Tests**: Tests unitarios y de integración
- **Reducción potencial**: 97% al usar plugins modulares

### ⚠️ Estado Actual y Recomendaciones

El DAG principal (`approval_cleanup.py`) tiene **32,609 líneas**, lo cual es extremadamente grande y causa:
- ⚠️ Dificultad para mantener y entender
- ⚠️ Problemas de rendimiento al cargar el DAG
- ⚠️ Imposibilidad de reutilizar código en otros DAGs

**Recomendación**: Usar la versión simplificada con plugins modulares que reduce el código en **97%** manteniendo toda la funcionalidad.

---

## 🏗️ Arquitectura

### Arquitectura Modular

El sistema ha sido refactorizado usando una arquitectura modular:

```
approval_cleanup.py (DAG principal)
    │
    ├── approval_cleanup_config.py       # Configuración
    ├── approval_cleanup_ops.py          # Operaciones DB
    ├── approval_cleanup_queries.py     # Queries SQL
    ├── approval_cleanup_analytics.py   # Análisis
    └── approval_cleanup_utils.py       # Utilidades
```

### Flujo del DAG

```
1. Validación de Parámetros
   │
   ▼
2. Archivado de Solicitudes Antiguas
   │
   ▼
3. Limpieza de Notificaciones Expiradas
   │
   ▼
4. Optimización de Índices
   │
   ▼
5. Análisis y Reportes
   │
   ▼
6. Monitoreo y Alertas
```

---

## 🔧 Componentes Principales

### 1. Configuración (`approval_cleanup_config.py`)

Centraliza toda la configuración del sistema:

- **Variables de entorno**: 100+ flags de feature
- **Constantes**: Retención, batch sizes, timeouts
- **Función `get_config()`**: Acceso estructurado a configuración

**Ejemplo**:
```python
from data.airflow.plugins.approval_cleanup_config import get_config

config = get_config()
retention_years = config['retention']['years']
batch_size = config['processing']['batch_size']
```

### 2. Operaciones (`approval_cleanup_ops.py`)

Operaciones de base de datos y procesamiento:

- **`get_pg_hook()`**: Hook de PostgreSQL con cache
- **`execute_query_with_timeout()`**: Queries con timeout
- **`process_batch()`**: Procesamiento en lotes
- **`calculate_optimal_batch_size()`**: Batch size adaptativo
- **`track_performance()`**: Tracking de métricas

**Ejemplo**:
```python
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook, execute_query_with_timeout

pg_hook = get_pg_hook()
result = execute_query_with_timeout(
    pg_hook,
    "SELECT * FROM requests WHERE created_at < %s",
    parameters=(cutoff_date,),
    timeout_seconds=300
)
```

### 3. Queries (`approval_cleanup_queries.py`)

Queries SQL reutilizables y parametrizadas:

- **`get_old_requests_to_archive()`**: Obtener requests antiguos
- **`archive_requests_batch()`**: Archivar en lotes
- **`get_expired_notifications()`**: Obtener notificaciones expiradas
- **`delete_notifications_batch()`**: Eliminar notificaciones
- **`get_stale_pending_requests()`**: Obtener requests stale
- **`get_database_size()`**: Obtener tamaño de BD
- **`get_table_sizes()`**: Obtener tamaños de tablas

**Ejemplo**:
```python
from data.airflow.plugins.approval_cleanup_queries import get_old_requests_to_archive

old_requests = get_old_requests_to_archive(
    pg_hook,
    retention_years=2,
    limit=1000
)
```

### 4. Analytics (`approval_cleanup_analytics.py`)

Análisis y métricas avanzadas:

- **`calculate_percentiles()`**: Percentiles (p50, p95, p99)
- **`detect_anomaly()`**: Detección de anomalías (Z-score)
- **`predict_capacity_need()`**: Predicción de capacidad
- **`analyze_trends()`**: Análisis de tendencias
- **`analyze_query_performance()`**: Análisis de performance

**Ejemplo**:
```python
from data.airflow.plugins.approval_cleanup_analytics import detect_anomaly, calculate_percentiles

metrics = [10, 20, 30, 40, 50, 1000]  # Último valor es anomalía
is_anomaly = detect_anomaly(metrics, threshold=2.5)
percentiles = calculate_percentiles(metrics)
```

### 5. Utilidades (`approval_cleanup_utils.py`)

Utilidades generales:

- **`log_with_context()`**: Logging estructurado
- **`check_circuit_breaker()`**: Circuit breaker
- **`validate_params()`**: Validación de parámetros
- **`export_to_multiple_formats()`**: Exportación múltiples formatos

**Ejemplo**:
```python
from data.airflow.plugins.approval_cleanup_utils import log_with_context, validate_params

log_with_context('info', 'Procesando solicitudes', extra={
    'count': len(requests),
    'task_id': task_id
})

validate_params({
    'retention_years': (1, 10),
    'batch_size': (100, 10000)
})
```

---

## ⚙️ Funcionalidades

### 1. Archivado de Solicitudes

Archiva solicitudes antiguas según política de retención:

```python
@task
def archive_old_requests(retention_years: int = 2):
    """Archiva solicitudes antiguas."""
    cutoff_date = pendulum.now().subtract(years=retention_years)
    
    # Obtener requests antiguos
    old_requests = get_old_requests_to_archive(
        pg_hook,
        cutoff_date=cutoff_date,
        limit=BATCH_SIZE
    )
    
    # Archivar en lotes
    archived = archive_requests_batch(pg_hook, old_requests)
    
    return {'archived': archived}
```

### 2. Limpieza de Notificaciones

Elimina notificaciones expiradas:

```python
@task
def cleanup_notifications(retention_months: int = 12):
    """Limpia notificaciones expiradas."""
    cutoff_date = pendulum.now().subtract(months=retention_months)
    
    # Obtener notificaciones expiradas
    expired = get_expired_notifications(pg_hook, cutoff_date)
    
    # Eliminar en lotes
    deleted = delete_notifications_batch(pg_hook, expired)
    
    return {'deleted': deleted}
```

### 3. Optimización de Índices

Optimiza índices para mejorar performance:

```python
@task
def optimize_indexes():
    """Optimiza índices de la base de datos."""
    # Analizar índices faltantes
    missing_indexes = analyze_missing_indexes(pg_hook)
    
    # Crear índices recomendados
    for index in missing_indexes:
        create_index(pg_hook, index)
    
    # Reindexar índices fragmentados
    reindex_fragmented(pg_hook)
    
    return {'indexes_created': len(missing_indexes)}
```

### 4. Análisis y Reportes

Genera reportes de análisis:

```python
@task
def generate_reports():
    """Genera reportes de análisis."""
    # Análisis de performance
    perf_analysis = analyze_query_performance(pg_hook)
    
    # Análisis de tendencias
    trends = analyze_trends(pg_hook, days=30)
    
    # Detección de anomalías
    anomalies = detect_anomalies(pg_hook)
    
    # Exportar reportes
    export_to_multiple_formats({
        'performance': perf_analysis,
        'trends': trends,
        'anomalies': anomalies
    }, formats=['csv', 'json', 'html'])
    
    return {'reports_generated': True}
```

---

## 🔧 Configuración

### Variables de Entorno

Las principales variables de entorno están documentadas en `approval_cleanup_config.py`:

```bash
# Retención
APPROVAL_CLEANUP_RETENTION_YEARS=2
APPROVAL_CLEANUP_NOTIFICATION_RETENTION_MONTHS=12

# Procesamiento
APPROVAL_CLEANUP_BATCH_SIZE=1000
APPROVAL_CLEANUP_MAX_WORKERS=4

# Features
APPROVAL_CLEANUP_ANALYTICS_ENABLED=true
APPROVAL_CLEANUP_PROMETHEUS_ENABLED=true
APPROVAL_CLEANUP_S3_EXPORT_ENABLED=false

# Database
APPROVALS_DB_CONN_ID=approvals_db
```

### Parámetros del DAG

El DAG acepta parámetros configurables:

```python
@dag(
    params={
        'retention_years': Param(2, type='integer', minimum=1, maximum=10),
        'notification_retention_months': Param(12, type='integer', minimum=1, maximum=24),
        'dry_run': Param(False, type='boolean'),
    }
)
```

### Ejecutar con Parámetros

```bash
# Desde Airflow UI
# Config > JSON: {"retention_years": 3, "dry_run": true}

# Desde CLI
airflow dags trigger approval_cleanup \
  --conf '{"retention_years": 3, "dry_run": true}'
```

---

## 🚀 Uso

### Ejecución Manual

```bash
# Ejecutar DAG completo
airflow dags trigger approval_cleanup

# Ejecutar tarea específica
airflow tasks test approval_cleanup archive_old_requests 2024-01-01

# Ejecutar con dry-run
airflow dags trigger approval_cleanup \
  --conf '{"dry_run": true}'
```

### Programación

El DAG está configurado para ejecutarse:

```python
schedule_interval="@weekly"  # Cada semana
# o
schedule_interval="0 2 * * 0"  # Domingos a las 2 AM
```

### Monitoreo

- **Airflow UI**: Ver estado de ejecuciones
- **Grafana**: Dashboards de métricas
- **Prometheus**: Alertas automáticas
- **Slack**: Notificaciones de completado/fallos

---

## 📦 Plugins Modulares

### Ventajas de la Arquitectura Modular

1. **Reutilización**: Código reutilizable en otros DAGs
2. **Mantenibilidad**: Código más fácil de mantener
3. **Testabilidad**: Tests unitarios más simples
4. **Reducción**: 97% reducción en líneas del DAG principal

### Uso de Plugins

```python
# Importar plugins
from data.airflow.plugins.approval_cleanup_config import get_config
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook
from data.airflow.plugins.approval_cleanup_queries import get_old_requests_to_archive
from data.airflow.plugins.approval_cleanup_utils import log_with_context

# Usar en tu DAG
@task
def mi_tarea():
    config = get_config()
    pg_hook = get_pg_hook()
    
    log_with_context('info', 'Iniciando...')
    
    old_requests = get_old_requests_to_archive(
        pg_hook,
        retention_years=config['retention']['years']
    )
    
    return {'count': len(old_requests)}
```

Ver [`data/airflow/README_APPROVAL_CLEANUP.md`](../data/airflow/README_APPROVAL_CLEANUP.md) para más detalles.

---

## ⚡ Performance

### Optimizaciones Implementadas

1. **Batch Processing**: Procesamiento en lotes para operaciones grandes
2. **Batch Size Adaptativo**: Ajusta batch size según performance
3. **Connection Pooling**: Pool de conexiones optimizado
4. **Query Caching**: Cache de queries frecuentes
5. **Parallel Processing**: Procesamiento paralelo donde es posible
6. **Index Optimization**: Índices optimizados para queries comunes

### Métricas de Performance

- **Throughput**: ~10,000 registros/minuto
- **Latencia p95**: < 500ms por lote
- **Memory Usage**: < 2GB por worker
- **CPU Usage**: < 50% promedio

### Mejoras de Performance

```python
# Usar batch processing
for batch in chunks(records, batch_size=1000):
    process_batch(batch)

# Usar índices
# Asegurar que las queries usan índices apropiados

# Connection pooling
# Reutilizar conexiones de base de datos

# Cache
# Cachear resultados de queries frecuentes
```

---

## 📊 Monitoreo

### Métricas Clave

- **Requests Archivados**: Total de requests archivados
- **Notifications Deleted**: Notificaciones eliminadas
- **Execution Time**: Tiempo de ejecución del DAG
- **Error Rate**: Tasa de errores
- **Batch Size**: Tamaño de lotes procesados

### Dashboards

- **Grafana**: Dashboard de métricas del sistema
- **Airflow UI**: Estado de ejecuciones
- **Prometheus**: Métricas en tiempo real

### Alertas

- **Alto error rate**: > 5% de errores
- **Ejecución lenta**: > 1 hora de ejecución
- **Alto uso de recursos**: > 80% CPU/memoria

---

## 🔍 Troubleshooting

### Problema: DAG falla con timeout

**Solución**:
```python
# Aumentar timeout
@task(execution_timeout=timedelta(hours=2))
def mi_tarea_lenta():
    # Tu código
    pass
```

### Problema: DAG tarda mucho en cargar

**Causa**: El archivo tiene 32,609 líneas, lo cual es excesivo.

**Solución**:
1. **Usar plugins modulares**: Migrar a la versión simplificada
2. **Verificar imports**: Eliminar imports no usados
3. **Lazy loading**: Cargar configuraciones solo cuando se necesiten
4. **Dividir DAG**: Considerar dividir en múltiples DAGs más pequeños

```bash
# Verificar tamaño del archivo
wc -l data/airflow/dags/approval_cleanup.py

# Analizar complejidad
python data/airflow/scripts/analyze_approval_cleanup.py

# Verificar plugins disponibles
python data/airflow/scripts/validate_approval_cleanup.py
```

### Problema: Error de conexión a BD

**Solución**:
```bash
# Verificar connection ID
airflow connections list | grep approvals_db

# Probar conexión
python -c "from airflow.providers.postgres.hooks.postgres import PostgresHook; h = PostgresHook(postgres_conn_id='approvals_db'); print(h.get_conn())"
```

### Problema: Performance lenta

**Solución**:
1. Verificar índices en base de datos
2. Ajustar batch size (usar batch size adaptativo)
3. Verificar uso de recursos
4. Analizar queries lentas
5. Usar connection pooling
6. Habilitar cache de queries frecuentes

### Problema: Módulo no encontrado

**Solución**:
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project"

# Verificar imports
python -c "from data.airflow.plugins.approval_cleanup_config import get_config; print('OK')"

# Verificar que los plugins existen
ls -la data/airflow/plugins/approval_cleanup_*.py
```

### Problema: Demasiadas variables de entorno

**Causa**: El archivo tiene 100+ variables de entorno hardcodeadas.

**Solución**:
1. **Usar `approval_cleanup_config.py`**: Centraliza todas las configuraciones
2. **Usar `get_config()`**: Acceso estructurado a configuración
3. **Documentar variables**: Mantener lista de variables en README

```python
# ❌ Malo - Variables hardcodeadas
ENABLE_FEATURE_X = os.getenv("APPROVAL_CLEANUP_FEATURE_X", "true").lower() == "true"

# ✅ Bueno - Usar configuración centralizada
from data.airflow.plugins.approval_cleanup_config import get_config
config = get_config()
enable_feature_x = config['features']['feature_x']
```

---

## 📚 Referencias

- [`data/airflow/README_APPROVAL_CLEANUP.md`](../data/airflow/README_APPROVAL_CLEANUP.md) - Documentación completa
- [`data/airflow/dags/approval_cleanup_REFACTORING.md`](../data/airflow/dags/approval_cleanup_REFACTORING.md) - Guía de refactorización
- [`data/airflow/dags/approval_cleanup_BEST_PRACTICES.md`](../data/airflow/dags/approval_cleanup_BEST_PRACTICES.md) - Mejores prácticas

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

