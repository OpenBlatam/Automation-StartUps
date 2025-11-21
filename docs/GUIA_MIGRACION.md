# 🔄 Guía de Migración

> **Versión**: 1.0 | **Última actualización**: 2024

Guía paso a paso para migrar código existente a la nueva arquitectura modular.

## 📋 Tabla de Contenidos

- [Migración de approval_cleanup.py](#-migración-de-approval_cleanuppy)
- [Migración de DAGs Legacy](#-migración-de-dags-legacy)
- [Migración de Configuración](#-migración-de-configuración)
- [Migración de Funciones](#-migración-de-funciones)
- [Checklist de Migración](#-checklist-de-migración)

---

## 🔄 Migración de approval_cleanup.py

### Paso 1: Análisis del DAG Actual

```bash
# Analizar el DAG actual
python data/airflow/scripts/analyze_approval_cleanup.py approval_cleanup.py

# Verificar plugins disponibles
python data/airflow/scripts/validate_approval_cleanup.py

# Generar reporte de migración
python data/airflow/scripts/migrate_approval_cleanup.py approval_cleanup.py
```

### Paso 2: Backup del DAG Original

```bash
# Crear backup
cp data/airflow/dags/approval_cleanup.py data/airflow/dags/approval_cleanup_legacy.py

# Verificar backup
ls -lh data/airflow/dags/approval_cleanup*.py
```

### Paso 3: Crear Versión Simplificada

```python
# Crear nuevo archivo: approval_cleanup_v2.py
"""
Versión simplificada usando plugins modulares.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task, task_group
from data.airflow.plugins.approval_cleanup_config import get_config
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook
from data.airflow.plugins.approval_cleanup_queries import (
    get_old_requests_to_archive,
    archive_requests_batch,
    get_expired_notifications,
    delete_notifications_batch,
)
from data.airflow.plugins.approval_cleanup_utils import log_with_context

@dag(
    dag_id="approval_cleanup_v2",
    description="Limpieza de aprobaciones (versión simplificada)",
    schedule_interval="@weekly",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    params={
        "retention_years": 2,
        "notification_retention_months": 12,
        "dry_run": False,
    },
    tags=["cleanup", "approvals", "v2"],
)
def approval_cleanup_v2():
    
    @task_group(group_id="cleanup_operations")
    def cleanup_operations(**context):
        """Operaciones de limpieza."""
        
        @task
        def archive_old_requests(**ctx):
            """Archiva solicitudes antiguas."""
            config = get_config()
            params = ctx["dag_run"].conf or {}
            retention_years = params.get("retention_years", config['retention']['years'])
            
            pg_hook = get_pg_hook()
            old_requests = get_old_requests_to_archive(
                pg_hook,
                retention_years=retention_years,
                limit=config['processing']['batch_size']
            )
            
            if old_requests and not params.get("dry_run", False):
                archived = archive_requests_batch(pg_hook, old_requests)
                log_with_context('info', f'Archivadas {archived} solicitudes')
                return {"archived": archived}
            
            return {"archived": 0, "dry_run": True}
        
        @task
        def cleanup_notifications(**ctx):
            """Limpia notificaciones expiradas."""
            config = get_config()
            params = ctx["dag_run"].conf or {}
            retention_months = params.get("notification_retention_months", 12)
            
            pg_hook = get_pg_hook()
            expired = get_expired_notifications(pg_hook, retention_months)
            
            if expired and not params.get("dry_run", False):
                deleted = delete_notifications_batch(pg_hook, expired)
                log_with_context('info', f'Eliminadas {deleted} notificaciones')
                return {"deleted": deleted}
            
            return {"deleted": 0, "dry_run": True}
        
        return {
            "archive": archive_old_requests(),
            "notifications": cleanup_notifications(),
        }
    
    cleanup_operations()

approval_cleanup_v2()
```

### Paso 4: Testing en Staging

```bash
# Probar en staging
airflow dags test approval_cleanup_v2 2024-01-01

# Probar con dry-run
airflow dags trigger approval_cleanup_v2 \
  --conf '{"retention_years": 2, "dry_run": true}'

# Comparar resultados
# Ejecutar ambas versiones y comparar outputs
```

### Paso 5: Migración Gradual

```bash
# Opción 1: Deshabilitar versión antigua
airflow dags pause approval_cleanup

# Opción 2: Renombrar versiones
mv approval_cleanup.py approval_cleanup_legacy.py
mv approval_cleanup_v2.py approval_cleanup.py

# Opción 3: Ejecutar ambas en paralelo temporalmente
# Monitorear ambas versiones durante 1-2 semanas
```

---

## 🔄 Migración de DAGs Legacy

### Patrón 1: Migrar Funciones Auxiliares

**Antes**:
```python
# ❌ Funciones auxiliares en el DAG
def _get_pg_hook():
    return PostgresHook(postgres_conn_id="approvals_db")

def _execute_query(sql, params=None):
    hook = _get_pg_hook()
    return hook.get_records(sql, parameters=params)

@task
def my_task():
    result = _execute_query("SELECT * FROM tabla")
    return result
```

**Después**:
```python
# ✅ Usar plugins modulares
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook, execute_query_with_timeout

@task
def my_task():
    pg_hook = get_pg_hook()
    result = execute_query_with_timeout(
        pg_hook,
        "SELECT * FROM tabla"
    )
    return result
```

### Patrón 2: Migrar Configuración

**Antes**:
```python
# ❌ Variables hardcodeadas
BATCH_SIZE = 1000
RETENTION_YEARS = 2
TIMEOUT = 300

@task
def my_task():
    # Usar variables directamente
    process_batch(BATCH_SIZE)
```

**Después**:
```python
# ✅ Configuración centralizada
from data.airflow.plugins.approval_cleanup_config import get_config

@task
def my_task():
    config = get_config()
    batch_size = config['processing']['batch_size']
    process_batch(batch_size)
```

### Patrón 3: Migrar Logging

**Antes**:
```python
# ❌ Logging básico
import logging
logger = logging.getLogger(__name__)

@task
def my_task():
    logger.info("Procesando...")
```

**Después**:
```python
# ✅ Logging estructurado
from data.airflow.plugins.approval_cleanup_utils import log_with_context

@task
def my_task(**context):
    log_with_context('info', 'Procesando...', extra={
        'task_id': context['task_instance'].task_id,
        'dag_id': context['dag'].dag_id
    })
```

---

## 🔄 Migración de Configuración

### Migrar Variables de Entorno

**Antes** (en el DAG):
```python
# ❌ 100+ variables en el DAG
ENABLE_FEATURE_X = os.getenv("APPROVAL_CLEANUP_FEATURE_X", "true").lower() == "true"
ENABLE_FEATURE_Y = os.getenv("APPROVAL_CLEANUP_FEATURE_Y", "false").lower() == "true"
# ... 100+ más
```

**Después** (en `approval_cleanup_config.py`):
```python
# ✅ Configuración centralizada
def get_config():
    return {
        'features': {
            'feature_x': os.getenv("APPROVAL_CLEANUP_FEATURE_X", "true").lower() == "true",
            'feature_y': os.getenv("APPROVAL_CLEANUP_FEATURE_Y", "false").lower() == "true",
        },
        # ... más configuraciones
    }
```

**Uso en el DAG**:
```python
from data.airflow.plugins.approval_cleanup_config import get_config

config = get_config()
if config['features']['feature_x']:
    # Usar feature X
    pass
```

---

## 🔄 Migración de Funciones

### Paso 1: Identificar Funciones a Migrar

```python
# Script para identificar funciones auxiliares
import ast
import sys

def find_helper_functions(file_path):
    """Encuentra funciones auxiliares en el archivo."""
    with open(file_path) as f:
        tree = ast.parse(f.read())
    
    helper_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('_'):
                helper_functions.append({
                    'name': node.name,
                    'lines': node.lineno,
                    'params': len(node.args.args)
                })
    
    return helper_functions

if __name__ == "__main__":
    functions = find_helper_functions(sys.argv[1])
    for func in functions:
        print(f"{func['name']}: {func['lines']} líneas, {func['params']} parámetros")
```

### Paso 2: Extraer a Plugin Apropiado

**Ejemplo: Extraer función de query**

**Antes** (en el DAG):
```python
def _get_old_requests(retention_years):
    """Obtiene solicitudes antiguas."""
    hook = PostgresHook(postgres_conn_id="approvals_db")
    sql = f"""
        SELECT * FROM requests
        WHERE created_at < NOW() - INTERVAL '{retention_years} years'
    """
    return hook.get_records(sql)
```

**Después** (en `approval_cleanup_queries.py`):
```python
def get_old_requests_to_archive(
    pg_hook: PostgresHook,
    retention_years: int = 2,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Obtiene solicitudes antiguas para archivar.
    
    Args:
        pg_hook: Hook de PostgreSQL
        retention_years: Años de retención
        limit: Límite de registros
        
    Returns:
        Lista de solicitudes antiguas
    """
    sql = """
        SELECT * FROM requests
        WHERE created_at < NOW() - INTERVAL %s
        LIMIT %s
    """
    records = pg_hook.get_records(sql, parameters=(f"{retention_years} years", limit))
    return [dict(row) for row in records]
```

**Uso en el DAG**:
```python
from data.airflow.plugins.approval_cleanup_queries import get_old_requests_to_archive

@task
def archive_task():
    pg_hook = get_pg_hook()
    old_requests = get_old_requests_to_archive(pg_hook, retention_years=2)
    return old_requests
```

---

## ✅ Checklist de Migración

### Pre-Migración

- [ ] Analizar DAG actual
- [ ] Identificar funciones auxiliares
- [ ] Identificar variables de configuración
- [ ] Crear backup del DAG original
- [ ] Verificar que plugins existen
- [ ] Documentar dependencias

### Migración

- [ ] Extraer funciones a plugins apropiados
- [ ] Migrar configuración a `approval_cleanup_config.py`
- [ ] Reemplazar código con llamadas a plugins
- [ ] Agrupar tareas en task groups
- [ ] Actualizar imports
- [ ] Eliminar código duplicado

### Testing

- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Validar en staging
- [ ] Comparar resultados con versión original
- [ ] Verificar performance
- [ ] Verificar logs

### Deployment

- [ ] Deploy a staging
- [ ] Monitorear ejecución
- [ ] Verificar métricas
- [ ] Deploy a producción
- [ ] Mantener versión legacy como backup
- [ ] Documentar cambios

### Post-Migración

- [ ] Eliminar versión legacy después de validación
- [ ] Actualizar documentación
- [ ] Notificar al equipo
- [ ] Registrar lecciones aprendidas

---

## 🛠️ Herramientas de Migración

### Script de Análisis

```bash
# Analizar complejidad
python data/airflow/scripts/analyze_approval_cleanup.py <dag_file>

# Encontrar funciones duplicadas
python data/airflow/scripts/find_duplicates.py <dag_file>

# Generar reporte de migración
python data/airflow/scripts/migrate_approval_cleanup.py <dag_file>
```

### Script de Validación

```bash
# Validar plugins
python data/airflow/scripts/validate_approval_cleanup.py

# Validar sintaxis
python -m py_compile <dag_file>

# Validar imports
python -c "import <dag_module>"
```

---

## 📚 Referencias

- [`docs/APPROVAL_SYSTEM_MEJORAS.md`](./APPROVAL_SYSTEM_MEJORAS.md) - Guía de mejoras
- [`docs/APPROVAL_SYSTEM.md`](./APPROVAL_SYSTEM.md) - Documentación técnica
- [`data/airflow/README_APPROVAL_CLEANUP.md`](../data/airflow/README_APPROVAL_CLEANUP.md) - Guía completa

---

**Versión**: 1.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

