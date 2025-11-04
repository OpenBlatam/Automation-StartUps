# DAG de Limpieza de Aprobaciones - Mejoras

Este documento describe las mejoras implementadas en el DAG `approval_cleanup.py`.

## 🚀 Mejoras Implementadas

### 1. **Manejo Robusto de Conexiones**

- ✅ **Retry con exponential backoff**: Uso de `tenacity` para reintentos automáticos
- ✅ **Validación de conexión**: Test de conexión antes de usar el hook
- ✅ **Manejo de errores mejorado**: Excepciones más descriptivas

**Código**:
```python
def _get_pg_hook() -> PostgresHook:
    """Obtiene hook de PostgreSQL con validación y retry."""
    # Retry automático con exponential backoff
    # Validación de conexión antes de retornar
```

### 2. **Transacciones Atómicas**

- ✅ **Transacciones explícitas**: Todas las operaciones críticas usan transacciones
- ✅ **Rollback automático**: En caso de error, se revierten todos los cambios
- ✅ **Atomicidad garantizada**: Archive y delete en la misma transacción

**Beneficios**:
- No quedan datos en estado inconsistente
- Rollback automático en caso de error
- Mejor integridad de datos

### 3. **Batch Processing**

- ✅ **Procesamiento en batches**: Para grandes volúmenes, procesa en lotes de 10,000
- ✅ **Evita locks prolongados**: Reduce tiempo de bloqueo de tablas
- ✅ **Mejor logging**: Logs de progreso por batch

**Implementación**:
```python
BATCH_SIZE = 10000
# Procesa en batches para evitar locks prolongados
```

### 4. **Seguridad SQL Mejorada**

- ✅ **Validación de tablas**: Verifica existencia antes de operar
- ✅ **Nombres seguros**: Uso de comillas para nombres de tablas/vistas
- ✅ **Validación de parámetros**: Verifica tipos y rangos antes de usar

**Ejemplo**:
```python
# Verificar que tabla existe
check_sql = """
    SELECT EXISTS (...)
"""
exists = pg_hook.get_first(check_sql, parameters=(table,))

# Usar formato seguro
sql = f'ANALYZE "{table}";'
```

### 5. **Gestión de Recursos**

- ✅ **Pools de recursos**: Uso de `etl_pool` para tareas pesadas
- ✅ **Configuración de ejecución**: `MaxWorkers: 1` para VACUUM (secuencial)
- ✅ **Priorización**: Tareas críticas tienen acceso garantizado a recursos

### 6. **Reportes Mejorados**

- ✅ **Métricas adicionales**: 
  - Total approved/rejected/auto-approved
  - Tiempo promedio de procesamiento
  - Tamaños de tablas
- ✅ **Notificaciones enriquecidas**: Slack con más detalles
- ✅ **Estadísticas de tablas**: Tamaños y uso de espacio

### 7. **Manejo de Materialized Views**

- ✅ **Fallback inteligente**: Si CONCURRENTLY falla, intenta sin CONCURRENTLY
- ✅ **Validación de existencia**: Verifica que la vista existe antes de refrescar
- ✅ **Manejo de errores**: Continúa con otras vistas aunque una falle

### 8. **Optimización de Queries**

- ✅ **CTEs para eficiencia**: Uso de Common Table Expressions
- ✅ **Índices verificados**: Verifica existencia antes de crear
- ✅ **Queries optimizadas**: Eliminación de subqueries redundantes

## 📊 Nuevas Métricas

### Estadísticas Adicionales

1. **Por Estado**:
   - Total approved
   - Total rejected
   - Total auto-approved
   - Total pending

2. **Performance**:
   - Tiempo promedio de procesamiento (horas)
   - Solicitudes antiguas pendientes

3. **Storage**:
   - Tamaño de cada tabla
   - Tamaño total del esquema

### Reporte de Slack Mejorado

```
🧹 Approval Cleanup Report - 2025-01-15

*Archive:*
• Archived: 1,234
• Deleted: 1,234

*Notifications:*
• Deleted: 567
• Remaining: 89

*Stale Requests:*
• Found: 12

*Optimization:*
• Tables analyzed: 6
• Views refreshed: 3
• Tables vacuumed: 3

*Current Stats:*
• Total pending: 45
• Total completed: 12,345
• Total approved: 10,000
• Total rejected: 2,000
• Total auto-approved: 345
• Old pending (>90 days): 12
• Avg processing time: 24.5 hours

*Table Sizes:*
• approval_requests: 1.2 GB
• approval_history: 500 MB
• approval_chains: 200 MB
```

## 🔧 Configuración

### Parámetros del DAG

- `archive_retention_years`: 1-10 años (default: 1)
- `notification_retention_months`: 1-24 meses (default: 6)
- `dry_run`: true/false (default: false)
- `notify_on_completion`: true/false (default: true)

### Uso

**Ejecución Normal**:
```bash
# Trigger manual desde UI con parámetros por defecto
# O esperar schedule (domingos 2 AM)
```

**Dry Run**:
```bash
# Trigger con dry_run=true para ver qué se haría sin ejecutar
```

**Retención Personalizada**:
```bash
# Trigger con archive_retention_years=2, notification_retention_months=12
```

## ⚠️ Troubleshooting

### Error: "Cannot connect to database"

- Verificar que `APPROVALS_DB_CONN_ID` esté configurado
- Verificar conectividad de red
- Verificar credenciales en External Secrets

### Error: "Transaction failed during archive"

- Verificar espacio en disco
- Verificar permisos en tabla de archivo
- Verificar locks en tablas

### VACUUM muy lento

- Es normal para tablas grandes
- Considerar ejecutar en horarios de bajo uso
- Verificar si hay otros procesos bloqueando

### Materialized View refresh falla

- Verificar que tiene índice único (para CONCURRENTLY)
- El DAG intenta automáticamente sin CONCURRENTLY si falla

## 📈 Performance

### Optimizaciones

1. **Batch Processing**: Reduce tiempo de locks
2. **Transacciones**: Garantiza atomicidad sin overhead adicional
3. **Validación previa**: Evita operaciones innecesarias
4. **Pools de recursos**: Controla concurrencia

### Benchmarks Esperados

- **Archivo**: ~10,000 registros/segundo
- **Notificaciones**: ~50,000 registros/segundo
- **ANALYZE**: ~1-5 segundos por tabla
- **VACUUM**: Depende del tamaño (1-30 minutos)

## 🔐 Seguridad

- ✅ Todas las queries usan parámetros o validación
- ✅ Nombres de tablas validados contra whitelist
- ✅ Transacciones para atomicidad
- ✅ Rollback automático en errores

## 📚 Referencias

- **Esquema de aprobaciones**: `data/db/approvals_schema.sql`
- **Sistema de aprobaciones**: `workflow/APPROVALS_SYSTEM.md`
- **DAG de monitoreo**: `data/airflow/dags/approval_monitoring.py`

---

**Última actualización**: 2025-01-15  
**Versión**: 2.0

