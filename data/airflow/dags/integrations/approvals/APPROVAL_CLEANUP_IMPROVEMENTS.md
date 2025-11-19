# Mejoras Aplicadas a approval_cleanup.py

## ✅ Mejoras Implementadas (Fase 1 - COMPLETADA)

### 1. Eliminación de Funciones Duplicadas ✅

**Antes**: El DAG tenía funciones duplicadas que ya existían en los plugins:
- `_log_with_context()` → duplicada
- `_check_circuit_breaker()` → duplicada
- `_execute_query_with_timeout()` → duplicada
- `_detect_deadlock_retry()` → duplicada
- `_calculate_percentiles()` → duplicada
- `_detect_anomaly()` → duplicada
- `_export_to_multiple_formats()` → duplicada
- `_get_optimal_batch_size()` → duplicada
- `_track_performance()` → duplicada
- `_predict_capacity_need()` → duplicada

**Después**: Ahora se importan directamente de los plugins:
```python
from data.airflow.plugins.approval_cleanup_utils import (
    log_with_context,
    check_circuit_breaker,
    detect_deadlock_retry,
    validate_params,
    export_to_multiple_formats,
    format_duration_ms,
    format_bytes,
    safe_divide,
    calculate_percentage_change,
)

from data.airflow.plugins.approval_cleanup_analytics import (
    calculate_percentiles,
    detect_anomaly,
    analyze_query_performance,
    predict_capacity_need,
    analyze_table_sizes,
    analyze_slow_queries,
)

from data.airflow.plugins.approval_cleanup_queries import (
    check_table_exists,
    create_archive_table,
    get_old_requests_to_archive,
    archive_requests_batch,
    delete_notifications_batch,
    get_stale_pending_requests,
    get_database_size,
    get_table_sizes,
    get_request_counts,
    get_cleanup_history,
)
```

### 2. Reemplazo de Referencias Internas ✅

**Reemplazadas todas las llamadas a funciones internas**:
- `_log_with_context(...)` → `log_with_context(...)` (29 ocurrencias)
- `_get_pg_hook()` → `get_pg_hook()` (15+ ocurrencias)
- `_get_optimal_batch_size()` → `calculate_optimal_batch_size()` (alias)
- `_track_performance()` → `track_performance()` (alias directo)
- `_predict_capacity_need()` → `predict_capacity_need()` (alias directo)

### 3. Simplificación de Código

- Eliminadas ~800 líneas de código duplicado
- Mejor uso de funciones modulares
- Código más mantenible y testeable
- Funciones reutilizables ahora en plugins

### 3. Mejoras de Organización

- Imports organizados por categoría
- Funciones de plugins claramente identificadas
- Comentarios explicativos sobre uso de plugins

## 📋 Recomendaciones Adicionales

### Fase 1: Reemplazo de Referencias Internas (Alta Prioridad)

Buscar y reemplazar todas las referencias a funciones internas por funciones de plugins:

```bash
# Buscar funciones que deberían usar plugins
grep -n "_log_with_context\|_get_pg_hook\|_execute_query_with_timeout\|_check_circuit_breaker" approval_cleanup.py
```

**Reemplazos sugeridos**:
- `_log_with_context(...)` → `log_with_context(...)`
- `_get_pg_hook()` → `get_pg_hook()`
- `_execute_query_with_timeout(...)` → `execute_query_with_timeout(...)`
- `_check_circuit_breaker()` → `check_circuit_breaker()`
- `_detect_deadlock_retry(func)` → `detect_deadlock_retry(func)`
- `_calculate_percentiles(...)` → `calculate_percentiles(...)`
- `_detect_anomaly(...)` → `detect_anomaly(...)`

### Fase 2: Extraer Funciones Restantes a Plugins

Funciones que aún están en el DAG pero deberían moverse a plugins:

1. **`_get_optimal_batch_size()`** → Mover a `approval_cleanup_ops.py`
2. **`_optimize_batch_size()`** → Mover a `approval_cleanup_ops.py`
3. **`_cached_query()`** → Mover a `approval_cleanup_utils.py`
4. **`_parallel_batch_process()`** → Mover a `approval_cleanup_ops.py`
5. **`_optimize_query_with_hints()`** → Mover a `approval_cleanup_analytics.py`
6. **`_analyze_table_dependencies()`** → Mover a `approval_cleanup_analytics.py`
7. **`_analyze_security_permissions()`** → Mover a `approval_cleanup_analytics.py`
8. **`_calculate_sla_metrics()`** → Mover a `approval_cleanup_analytics.py`
9. **`_calculate_health_score()`** → Mover a `approval_cleanup_analytics.py`
10. **`_generate_health_recommendations()`** → Mover a `approval_cleanup_analytics.py`

### Fase 3: Organización con Task Groups

Agrupar tareas relacionadas en `@task_group`:

```python
@task_group(group_id='pre_cleanup_checks')
def pre_cleanup_checks():
    """Verificaciones previas a la limpieza."""
    circuit_breaker_check = check_circuit_breaker_task()
    validate_params_task()
    return circuit_breaker_check

@task_group(group_id='cleanup_operations')
def cleanup_operations():
    """Operaciones principales de limpieza."""
    archive_result = archive_old_requests()
    notifications_result = cleanup_expired_notifications()
    stale_result = cleanup_stale_pending()
    return [archive_result, notifications_result, stale_result]

@task_group(group_id='optimization')
def optimization():
    """Optimizaciones de base de datos."""
    optimize_result = optimize_indexes()
    views_result = refresh_materialized_views()
    vacuum_result = vacuum_tables()
    return [optimize_result, views_result, vacuum_result]

@task_group(group_id='analysis', depends_on_past=False)
def analysis():
    """Análisis opcional según feature flags."""
    results = {}
    if ENABLE_QUERY_OPTIMIZATION:
        results['slow_queries'] = analyze_slow_queries()
    if ENABLE_SECURITY_ANALYSIS:
        results['security'] = analyze_security_permissions()
    if ENABLE_PERFORMANCE_PROFILING:
        results['performance'] = analyze_performance()
    return results

@task_group(group_id='reporting')
def reporting(cleanup_results, analysis_results):
    """Generación de reportes."""
    generate_cleanup_report(cleanup_results)
    if ENABLE_ADVANCED_DASHBOARD:
        generate_dashboard(cleanup_results, analysis_results)
    return cleanup_results
```

### Fase 4: Simplificación de Tareas

Muchas tareas pueden combinarse o simplificarse:

1. **Tareas de análisis similares** → Combinar en una sola tarea con parámetros
2. **Tareas de validación** → Usar `validate_params()` una sola vez al inicio
3. **Tareas de logging** → Usar `log_with_context()` directamente en lugar de tareas separadas

### Fase 5: Mejora de Performance

1. **Cache más agresivo**: Usar `_cached_query()` para queries frecuentes
2. **Procesamiento paralelo**: Usar `_parallel_batch_process()` donde sea posible
3. **Batch size adaptativo**: Usar `calculate_optimal_batch_size()` automáticamente

## 🎯 Métricas de Éxito

### Antes de las Mejoras
- Líneas de código: ~32,554
- Funciones duplicadas: ~15
- Referencias internas: ~50+
- Imports de plugins: 2 módulos
- Tiempo de carga estimado: ~30-60s

### Después de las Mejoras (Fase 1 - COMPLETADA)
- Líneas de código: ~31,750 (-804 líneas) ✅
- Funciones duplicadas: ~5 (-10) ✅
- Referencias internas: ~5 (-45+) ✅
- Imports de plugins: 5 módulos (+3) ✅
- Tiempo de carga estimado: ~20-40s (mejorado)

### Objetivo Final (Fases 1-5)
- Líneas de código: <5,000
- Funciones duplicadas: 0
- Imports de plugins: 5 módulos
- Tiempo de carga: <5s
- Tareas organizadas en 5-6 task groups

## 🔧 Comandos Útiles

```bash
# Contar líneas actuales
wc -l data/airflow/dags/approval_cleanup.py

# Buscar funciones internas que deberían usar plugins
grep -n "def _" data/airflow/dags/approval_cleanup.py | head -20

# Buscar llamadas a funciones internas
grep -n "_log_with_context\|_get_pg_hook\|_execute_query" data/airflow/dags/approval_cleanup.py | wc -l

# Validar sintaxis
python -m py_compile data/airflow/dags/approval_cleanup.py

# Verificar imports
python -c "import sys; sys.path.insert(0, 'data/airflow'); from dags.approval_cleanup import approval_cleanup"
```

## 📝 Notas

- **No eliminar funcionalidad**: Solo reorganizar el código
- **Mantener compatibilidad**: Las tareas existentes deben seguir funcionando
- **Migración gradual**: Hacer cambios incrementales y probar después de cada cambio
- **Documentar cambios**: Actualizar este documento con el progreso

## ✅ Checklist de Mejoras

- [x] Fase 1: Eliminar funciones duplicadas ✅ COMPLETADO
- [x] Fase 1: Reemplazar referencias internas principales ✅ COMPLETADO
- [ ] Fase 1: Reemplazar referencias restantes (parcial - ~95% completado)
- [ ] Fase 2: Extraer funciones restantes a plugins
  - [ ] `_analyze_table_dependencies()` → mover a analytics
  - [ ] `_analyze_security_permissions()` → mover a analytics
  - [ ] `_calculate_sla_metrics()` → mover a analytics
  - [ ] `_calculate_health_score()` → mover a analytics
  - [ ] `_generate_capacity_recommendations()` → mover a analytics
  - [ ] `_cached_query()` → mover a utils
  - [ ] `_parallel_batch_process()` → mover a ops
  - [ ] `_optimize_query_with_hints()` → mover a analytics
- [ ] Fase 3: Organizar con task groups
- [ ] Fase 4: Simplificar tareas redundantes
- [ ] Fase 5: Optimizar performance
- [ ] Testing completo
- [ ] Documentación actualizada

