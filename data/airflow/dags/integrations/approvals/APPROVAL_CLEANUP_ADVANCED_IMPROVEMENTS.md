# Mejoras Avanzadas para Approval Cleanup DAG

## 🚀 Nuevas Funcionalidades Implementadas

### 1. Sistema de Detección de Anomalías

**Funcionalidad**: `_detect_anomaly()`
- Detecta valores anómalos usando Z-score basado en historial
- Configurable mediante `APPROVAL_CLEANUP_ANOMALY_Z_SCORE` (default: 2.5)
- Analiza métricas históricas de las últimas N ejecuciones
- Identifica anomalías en:
  - `archived_count`
  - `deleted_count`
  - `notifications_deleted`
  - `database_size_bytes`

**Ejemplo de uso**:
```python
anomaly = _detect_anomaly(
    value=5000,  # Valor actual
    metric_name='archived_count',
    pg_hook=pg_hook
)

if anomaly['is_anomaly']:
    logger.warning(
        f"Anomaly detected: z_score={anomaly['z_score']}, "
        f"mean={anomaly['mean']}, std={anomaly['std']}"
    )
```

### 2. Cálculo de Percentiles

**Funcionalidad**: `_calculate_percentiles()`
- Calcula percentiles (p50, p95, p99) de una lista de valores
- Útil para análisis de performance y duración de tareas
- Retorna: min, max, avg, p50, p95, p99

**Ejemplo de uso**:
```python
durations = [100, 150, 200, 250, 300, 350, 400]
stats = _calculate_percentiles(durations)
# {'p50': 250, 'p95': 400, 'p99': 400, 'min': 100, 'max': 400, 'avg': 250}
```

### 3. Auto-tuning de Batch Sizes

**Funcionalidad**: `_get_optimal_batch_size()`
- Calcula batch size óptimo basado en performance histórico
- Analiza throughput de diferentes batch sizes
- Ajusta automáticamente para máxima eficiencia
- Configurable mediante `APPROVAL_CLEANUP_BATCH_ADAPTIVE` (default: true)

**Ejemplo de uso**:
```python
optimal_size = _get_optimal_batch_size(
    operation_name='archive_old_requests',
    estimated_count=10000,
    pg_hook=pg_hook
)
# Puede retornar valores entre BATCH_SIZE_MIN (100) y BATCH_SIZE_MAX (10000)
```

### 4. Sistema de Checkpoints

**Funcionalidades**: `_save_checkpoint()`, `_load_checkpoint()`
- Guarda estado de procesamiento por lotes
- Permite reanudar operaciones interrumpidas
- Almacena datos en tabla `approval_cleanup_checkpoints`
- Útil para batch processing robusto

**Ejemplo de uso**:
```python
# Guardar checkpoint
checkpoint_data = {
    'offset': 5000,
    'processed_count': 5000,
    'last_batch_ids': [1001, 1002, ...]
}
_save_checkpoint('archive_old_requests', checkpoint_data, pg_hook)

# Cargar checkpoint
checkpoint = _load_checkpoint('archive_old_requests', pg_hook)
if checkpoint:
    offset = checkpoint['offset']
    # Continuar desde offset
```

### 5. Performance Tracking Avanzado

**Funcionalidad**: `_track_performance()`
- Registra métricas de performance para cada operación
- Almacena: duration_ms, records_processed, batch_size, throughput_per_sec
- Se usa para auto-tuning de batch sizes
- Limpia automáticamente datos antiguos

**Tabla creada**: `approval_cleanup_performance`
```sql
CREATE TABLE approval_cleanup_performance (
    id BIGSERIAL PRIMARY KEY,
    operation_name VARCHAR(255) NOT NULL,
    duration_ms FLOAT NOT NULL,
    records_processed INTEGER NOT NULL,
    batch_size INTEGER NOT NULL,
    throughput_per_sec FLOAT,
    cleanup_date TIMESTAMPTZ DEFAULT NOW()
);
```

## 📊 Variables de Entorno

### Configuración de Anomalías
```bash
APPROVAL_CLEANUP_ANOMALY_Z_SCORE=2.5  # Threshold Z-score para detectar anomalías
```

### Configuración de Performance
```bash
APPROVAL_CLEANUP_PERF_HISTORY_WINDOW=20  # Número de ejecuciones históricas a considerar
APPROVAL_CLEANUP_BATCH_ADAPTIVE=true  # Habilitar auto-tuning de batch sizes
```

### Límites de Batch Size
```python
BATCH_SIZE_MIN = 100      # Tamaño mínimo de batch
BATCH_SIZE_MAX = 10000    # Tamaño máximo de batch
```

## 🔧 Integración en el DAG

### Ejemplo: Usar detección de anomalías en archive_old_requests

```python
@task(task_id='archive_old_requests')
def archive_old_requests(archive_info: Dict[str, Any]) -> Dict[str, Any]:
    # ... código existente ...
    
    archived_count = len(all_archived_ids)
    
    # Detectar anomalías
    anomaly = _detect_anomaly(
        value=archived_count,
        metric_name='archived_count',
        pg_hook=pg_hook
    )
    
    if anomaly['is_anomaly']:
        _log_with_context(
            'warning',
            f'Anomaly detected in archived_count',
            anomaly=anomaly,
            archived_count=archived_count
        )
        
        # Opcional: Enviar alerta
        if anomaly['z_score'] > 3.0:  # Crítico
            notify_slack(
                f"🚨 Critical anomaly detected: "
                f"archived_count={archived_count} "
                f"(z_score={anomaly['z_score']})"
            )
    
    # Track performance
    duration_ms = (perf_counter() - start_time) * 1000
    _track_performance(
        operation_name='archive_old_requests',
        duration_ms=duration_ms,
        records_processed=archived_count,
        batch_size=optimal_batch_size,
        pg_hook=pg_hook
    )
    
    return {'archived_count': archived_count, 'anomaly': anomaly}
```

### Ejemplo: Usar auto-tuning de batch size

```python
# Calcular batch size óptimo antes de procesar
estimated_count = pg_hook.get_first(count_sql)[0]
optimal_batch_size = _get_optimal_batch_size(
    operation_name='archive_old_requests',
    estimated_count=estimated_count,
    pg_hook=pg_hook
)

# Usar batch size óptimo en lugar de BATCH_SIZE fijo
use_batching = estimated_count > optimal_batch_size
```

### Ejemplo: Usar checkpoints para batch processing robusto

```python
# Cargar checkpoint al inicio
checkpoint = _load_checkpoint('archive_old_requests', pg_hook)
start_offset = checkpoint['offset'] if checkpoint else 0

# Procesar en lotes
for batch in batches:
    # ... procesar batch ...
    
    # Guardar checkpoint después de cada lote
    _save_checkpoint(
        'archive_old_requests',
        {
            'offset': current_offset,
            'processed_count': processed_count,
            'last_batch_ids': batch_ids
        },
        pg_hook
    )
```

## 📈 Métricas y Monitoreo

### Métricas de Performance
- `approval_cleanup.performance.{operation}.duration_ms`
- `approval_cleanup.performance.{operation}.throughput_per_sec`
- `approval_cleanup.performance.{operation}.batch_size`

### Métricas de Anomalías
- `approval_cleanup.anomaly.detected` - Contador de anomalías detectadas
- `approval_cleanup.anomaly.z_score` - Z-score promedio de anomalías

### Alertas Recomendadas

1. **Anomalía Crítica** (z_score > 3.0):
   ```
   approval_cleanup_anomaly_z_score > 3.0
   ```

2. **Performance Degradada**:
   ```
   approval_cleanup_performance_duration_ms > p95_historical * 2
   ```

3. **Throughput Bajo**:
   ```
   approval_cleanup_performance_throughput_per_sec < threshold
   ```

## 🎯 Beneficios

1. **Detección Proactiva**: Identifica problemas antes de que se vuelvan críticos
2. **Auto-Optimización**: Ajusta automáticamente parámetros para mejor performance
3. **Resiliencia**: Checkpoints permiten reanudar operaciones interrumpidas
4. **Observabilidad**: Tracking detallado de performance para análisis futuro
5. **Eficiencia**: Batch sizes optimizados reducen tiempo de ejecución

## 🔄 Próximos Pasos

Para integrar estas mejoras en el DAG existente:

1. Agregar las funciones helper al inicio del DAG (después de `_detect_deadlock_retry`)
2. Integrar `_detect_anomaly()` en tareas críticas
3. Usar `_get_optimal_batch_size()` en operaciones de batch
4. Implementar `_track_performance()` después de cada operación importante
5. Considerar usar checkpoints para operaciones muy largas

## 📚 Referencias

- Z-score: https://en.wikipedia.org/wiki/Standard_score
- Percentiles: https://en.wikipedia.org/wiki/Percentile
- Auto-tuning: https://en.wikipedia.org/wiki/Automatic_optimization

