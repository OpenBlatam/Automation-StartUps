# Mejores Prácticas - approval_cleanup

## Guía de Uso de los Plugins Modulares

Esta guía explica cómo usar correctamente los plugins modulares creados para el DAG `approval_cleanup`.

## 📚 Plugins Disponibles

### 1. approval_cleanup_config.py

**Propósito**: Centralizar toda la configuración

```python
from data.airflow.plugins.approval_cleanup_config import (
    APPROVALS_DB_CONN,
    BATCH_SIZE,
    QUERY_TIMEOUT_SECONDS,
    get_config,
    ENABLE_QUERY_OPTIMIZATION,
)

# Obtener configuración completa
config = get_config()
print(config['retention']['max_years'])

# Usar constantes directamente
hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
```

### 2. approval_cleanup_ops.py

**Propósito**: Operaciones de base de datos y procesamiento

```python
from data.airflow.plugins.approval_cleanup_ops import (
    get_pg_hook,
    execute_query_with_timeout,
    process_batch,
    calculate_optimal_batch_size,
    track_performance,
)

# Obtener hook (con cache)
pg_hook = get_pg_hook()

# Ejecutar query con timeout
result = execute_query_with_timeout(
    pg_hook,
    "SELECT * FROM table WHERE id = %s",
    parameters=(123,),
    timeout_seconds=30,
    operation_name="get_record"
)

# Procesar en lotes
def process_items(batch):
    return {'processed': len(batch)}

results = process_batch(
    items=[1, 2, 3, 4, 5],
    batch_size=2,
    processor=process_items,
    operation_name="batch_operation"
)

# Calcular batch size óptimo
optimal_size = calculate_optimal_batch_size(
    estimated_count=10000,
    operation_name="archive_requests",
    pg_hook=pg_hook
)

# Track performance
track_performance(
    operation_name="archive_requests",
    duration_ms=1500.0,
    records_processed=500,
    batch_size=100,
    pg_hook=pg_hook
)
```

### 3. approval_cleanup_queries.py

**Propósito**: Queries SQL reutilizables

```python
from data.airflow.plugins.approval_cleanup_queries import (
    check_table_exists,
    create_archive_table,
    get_old_requests_to_archive,
    archive_requests_batch,
    get_expired_notifications,
    delete_notifications_batch,
    get_database_size,
    get_table_sizes,
    get_request_counts,
    insert_cleanup_history,
)

# Verificar tabla
exists = check_table_exists('approval_requests_archive')

# Crear tabla de archivo
create_archive_table()

# Obtener requests antiguos
old_requests = get_old_requests_to_archive(
    retention_years=1,
    batch_size=1000
)

# Archivar en lotes
result = archive_requests_batch(
    request_ids=[1, 2, 3],
    dry_run=False
)

# Obtener tamaño de base de datos
db_size = get_database_size()
print(f"Database size: {db_size['size_pretty']}")

# Obtener tamaños de tablas
table_sizes = get_table_sizes()
for table in table_sizes:
    print(f"{table['table']}: {table['size_pretty']}")

# Insertar historial
history_id = insert_cleanup_history({
    'archived_count': 100,
    'deleted_count': 50,
    'database_size_bytes': 1024 * 1024 * 1024,
})
```

### 4. approval_cleanup_analytics.py

**Propósito**: Análisis y métricas avanzadas

```python
from data.airflow.plugins.approval_cleanup_analytics import (
    detect_anomaly,
    analyze_table_sizes,
    analyze_trends,
    predict_capacity_need,
    calculate_percentiles,
)

# Detectar anomalías
anomaly = detect_anomaly(
    value=5000,
    metric_name='archived_count',
    pg_hook=pg_hook
)
if anomaly['is_anomaly']:
    print(f"Anomaly detected! Z-score: {anomaly['z_score']}")

# Analizar tamaños de tablas
table_analysis = analyze_table_sizes()
print(f"Total size: {table_analysis['total_size_gb']} GB")

# Analizar tendencias
history = get_cleanup_history(days=30)
trends = analyze_trends(history, days=30)
print(f"Archived trend: {trends['archived_trend']}")

# Predecir capacidad
prediction = predict_capacity_need(days_ahead=30)
if prediction['prediction_available']:
    print(f"Predicted size in 30 days: {prediction['predicted_size_gb']} GB")

# Calcular percentiles
values = [100, 200, 300, 400, 500]
percentiles = calculate_percentiles(values)
print(f"p95: {percentiles['p95']}")
```

### 5. approval_cleanup_utils.py

**Propósito**: Utilidades generales

```python
from data.airflow.plugins.approval_cleanup_utils import (
    log_with_context,
    check_circuit_breaker,
    validate_params,
    format_duration_ms,
    format_bytes,
    safe_divide,
    calculate_percentage_change,
)

# Logging estructurado
log_with_context(
    'info',
    'Processing batch',
    batch_num=1,
    total_batches=10,
    items_processed=100
)

# Verificar circuit breaker
cb_status = check_circuit_breaker()
if cb_status['active']:
    raise AirflowFailException("Circuit breaker is active!")

# Validar parámetros
params = {
    'archive_retention_years': 2,
    'notification_retention_months': 6,
    'dry_run': False
}
validate_params(params)

# Formatear duración
duration_str = format_duration_ms(125000)  # "2m 5.0s"

# Formatear bytes
size_str = format_bytes(1024 * 1024 * 5)  # "5.00 MB"

# División segura
result = safe_divide(10, 0, default=0)  # 0 en lugar de error

# Calcular cambio porcentual
change = calculate_percentage_change(100, 150)  # 50.0 (aumento del 50%)
```

## 🎯 Patrones de Uso Recomendados

### Patrón 1: Task con Validación y Logging

```python
@task(task_id='my_task', on_failure_callback=on_task_failure)
def my_task() -> Dict[str, Any]:
    """Ejemplo de tarea usando plugins."""
    # Validar parámetros
    context = get_current_context()
    params = context.get('params', {})
    validate_params(params)
    
    # Logging estructurado
    log_with_context('info', 'Starting task', task='my_task')
    
    try:
        # Obtener hook
        pg_hook = get_pg_hook()
        
        # Ejecutar operación
        result = execute_query_with_timeout(
            pg_hook,
            "SELECT COUNT(*) FROM table",
            timeout_seconds=30,
            operation_name="count_records"
        )
        
        # Logging de éxito
        log_with_context('info', 'Task completed', count=result[0][0])
        
        return {'success': True, 'count': result[0][0]}
        
    except Exception as e:
        log_with_context('error', f'Task failed: {e}', error=str(e))
        raise
```

### Patrón 2: Procesamiento en Lotes con Performance Tracking

```python
@task(task_id='process_batch_task')
def process_batch_task() -> Dict[str, Any]:
    """Procesar datos en lotes con tracking."""
    from time import perf_counter
    
    pg_hook = get_pg_hook()
    
    # Obtener datos
    items = get_old_requests_to_archive(
        retention_years=1,
        batch_size=1000,
        pg_hook=pg_hook
    )
    
    if not items:
        return {'processed': 0}
    
    # Calcular batch size óptimo
    optimal_batch_size = calculate_optimal_batch_size(
        estimated_count=len(items),
        operation_name="process_requests",
        pg_hook=pg_hook
    )
    
    # Procesar en lotes
    start_time = perf_counter()
    result = process_batch(
        items=items,
        batch_size=optimal_batch_size,
        processor=lambda batch: archive_requests_batch([r[0] for r in batch]),
        operation_name="archive_requests"
    )
    duration_ms = (perf_counter() - start_time) * 1000
    
    # Track performance
    track_performance(
        operation_name="archive_requests",
        duration_ms=duration_ms,
        records_processed=result['processed'],
        batch_size=optimal_batch_size,
        pg_hook=pg_hook
    )
    
    return result
```

### Patrón 3: Análisis con Detección de Anomalías

```python
@task(task_id='analyze_and_alert')
def analyze_and_alert(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analizar resultados y alertar si hay anomalías."""
    pg_hook = get_pg_hook()
    
    archived_count = results.get('archived', 0)
    
    # Detectar anomalías
    anomaly = detect_anomaly(
        value=archived_count,
        metric_name='archived_count',
        pg_hook=pg_hook
    )
    
    if anomaly['is_anomaly']:
        # Enviar alerta
        log_with_context(
            'warning',
            f'Anomaly detected in archived count',
            z_score=anomaly['z_score'],
            threshold=anomaly['threshold'],
            mean=anomaly['mean'],
            std=anomaly['std']
        )
        
        # Notificar
        notify_slack(
            f"⚠️ Anomaly detected: {archived_count} archived "
            f"(Z-score: {anomaly['z_score']:.2f})"
        )
    
    return {
        'anomaly_detected': anomaly['is_anomaly'],
        'anomaly_details': anomaly
    }
```

### Patrón 4: Circuit Breaker Pattern

```python
@task(task_id='safe_operation')
def safe_operation() -> Dict[str, Any]:
    """Operación con circuit breaker."""
    # Verificar circuit breaker
    cb_status = check_circuit_breaker()
    
    if cb_status['active']:
        raise AirflowFailException(
            f"Circuit breaker is ACTIVE: {cb_status['reason']}. "
            f"Too many failures ({cb_status['failure_count']}) in last "
            f"{CIRCUIT_BREAKER_CHECK_WINDOW_HOURS} hours."
        )
    
    # Continuar con operación normal
    # ...
```

## ⚠️ Anti-Patrones a Evitar

### ❌ No hacer: Funciones auxiliares dentro del DAG

```python
# ❌ MAL
@dag(...)
def my_dag():
    def _helper_function():  # NO hacer esto
        return "something"
    
    @task
    def my_task():
        return _helper_function()
```

**✅ Hacer**: Usar plugins

```python
# ✅ BIEN
from data.airflow.plugins.approval_cleanup_utils import helper_function

@dag(...)
def my_dag():
    @task
    def my_task():
        return helper_function()
```

### ❌ No hacer: Queries SQL hardcodeadas en tareas

```python
# ❌ MAL
@task
def my_task():
    sql = "SELECT * FROM table WHERE id = 123"  # Hardcoded
    return pg_hook.get_records(sql)
```

**✅ Hacer**: Usar funciones de queries

```python
# ✅ BIEN
from data.airflow.plugins.approval_cleanup_queries import get_old_requests_to_archive

@task
def my_task():
    return get_old_requests_to_archive(retention_years=1)
```

### ❌ No hacer: Configuración hardcodeada

```python
# ❌ MAL
@task
def my_task():
    batch_size = 1000  # Hardcoded
    timeout = 30  # Hardcoded
```

**✅ Hacer**: Usar configuración centralizada

```python
# ✅ BIEN
from data.airflow.plugins.approval_cleanup_config import BATCH_SIZE, QUERY_TIMEOUT_SECONDS

@task
def my_task():
    batch_size = BATCH_SIZE
    timeout = QUERY_TIMEOUT_SECONDS
```

## 🧪 Testing

### Ejemplo de Test para una Tarea

```python
from unittest.mock import Mock, patch
from data.airflow.plugins.approval_cleanup_queries import get_old_requests_to_archive

@patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
def test_get_old_requests(mock_get_hook):
    """Test obtener requests antiguos."""
    mock_hook = Mock()
    mock_get_hook.return_value = mock_hook
    mock_hook.get_records.return_value = [(1, 'completed', '2024-01-01')]
    
    result = get_old_requests_to_archive(retention_years=1)
    
    assert len(result) == 1
    assert result[0][0] == 1
```

## 📊 Monitoreo y Observabilidad

### Logging Estructurado

Siempre usar `log_with_context` para logging estructurado:

```python
log_with_context(
    'info',
    'Processing completed',
    items_processed=100,
    duration_ms=1500,
    batch_size=50
)
```

### Performance Tracking

Siempre trackear performance de operaciones importantes:

```python
from time import perf_counter

start_time = perf_counter()
# ... operación ...
duration_ms = (perf_counter() - start_time) * 1000

track_performance(
    operation_name="my_operation",
    duration_ms=duration_ms,
    records_processed=count,
    batch_size=batch_size
)
```

## 🔒 Seguridad

### Validación de Parámetros

Siempre validar parámetros del DAG:

```python
@task
def my_task():
    context = get_current_context()
    params = context.get('params', {})
    validate_params(params)  # Valida y lanza excepción si es inválido
    # ...
```

### Queries Parametrizadas

Siempre usar parámetros en queries SQL:

```python
# ✅ BIEN
execute_query_with_timeout(
    pg_hook,
    "SELECT * FROM table WHERE id = %s",
    parameters=(user_id,),  # Parametrizado
    timeout_seconds=30
)

# ❌ MAL
execute_query_with_timeout(
    pg_hook,
    f"SELECT * FROM table WHERE id = {user_id}",  # SQL injection risk
    timeout_seconds=30
)
```

## 📈 Optimización

### Batch Size Adaptativo

Usar batch size adaptativo basado en historial:

```python
optimal_batch_size = calculate_optimal_batch_size(
    estimated_count=estimated_count,
    operation_name="operation_name",
    pg_hook=pg_hook
)
```

### Timeouts Configurables

Siempre usar timeouts para queries:

```python
result = execute_query_with_timeout(
    pg_hook,
    sql,
    timeout_seconds=QUERY_TIMEOUT_SECONDS,
    operation_name="operation_name"
)
```

## 🎓 Resumen

1. **Usa plugins** en lugar de funciones auxiliares en el DAG
2. **Valida parámetros** antes de usar
3. **Usa logging estructurado** con `log_with_context`
4. **Trackea performance** de operaciones importantes
5. **Detecta anomalías** para alertas proactivas
6. **Usa circuit breaker** para operaciones críticas
7. **Testea plugins** independientemente
8. **Documenta** tus tareas y funciones

Sigue estos patrones para mantener código limpio, mantenible y escalable.
