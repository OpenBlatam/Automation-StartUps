# ✅ Mejores Prácticas

> **Versión**: 1.0 | **Última actualización**: 2024

Mejores prácticas y patrones recomendados para desarrollar en la plataforma.

## 📋 Tabla de Contenidos

- [Principios Generales](#-principios-generales)
- [Mejores Prácticas de Airflow](#-mejores-prácticas-de-airflow)
- [Mejores Prácticas de Código](#-mejores-prácticas-de-código)
- [Mejores Prácticas de Performance](#-mejores-prácticas-de-performance)
- [Mejores Prácticas de Seguridad](#-mejores-prácticas-de-seguridad)
- [Anti-Patrones](#-anti-patrones)

---

## 🎯 Principios Generales

### 1. Modularidad

✅ **Bueno**: Código dividido en módulos reutilizables
```python
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook
```

❌ **Malo**: Código duplicado en cada DAG
```python
def get_pg_hook():
    return PostgresHook(postgres_conn_id="approvals_db")
# Repetido en cada DAG
```

### 2. Idempotencia

✅ **Bueno**: Tareas idempotentes
```python
@task
def cargar_datos():
    # Verificar si ya existe
    if datos_ya_existen():
        return {"status": "skipped"}
    # Cargar datos
    return {"status": "loaded"}
```

❌ **Malo**: Siempre inserta sin verificar
```python
@task
def cargar_datos():
    # Siempre inserta, puede duplicar
    insertar_datos()
```

### 3. Manejo de Errores

✅ **Bueno**: Manejo robusto de errores
```python
@task(retries=3, retry_delay=timedelta(minutes=5))
def procesar():
    try:
        # Lógica
        return result
    except TransientError as e:
        logger.warning(f"Error temporal: {e}")
        raise  # Retry automático
    except PermanentError as e:
        logger.error(f"Error permanente: {e}")
        raise AirflowFailException(e)  # Falla inmediatamente
```

❌ **Malo**: Sin manejo de errores
```python
@task
def procesar():
    # Sin try/except, cualquier error falla el DAG
    resultado = operacion_riesgosa()
```

---

## ✈️ Mejores Prácticas de Airflow

### 1. Configuración del DAG

✅ **Bueno**: Configuración completa y clara
```python
@dag(
    dag_id="mi_dag",
    description="Descripción clara del propósito",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,  # Importante para evitar backfills no deseados
    tags=["etl", "datos"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": on_task_failure,
    },
)
```

❌ **Malo**: Configuración incompleta
```python
@dag(
    dag_id="mi_dag",
    # Falta descripción, tags, default_args
)
```

### 2. Nombres Descriptivos

✅ **Bueno**: Nombres claros y descriptivos
```python
@task
def extraer_datos_de_api_hubspot():
    """Extrae datos de la API de HubSpot."""
    pass

@task
def transformar_datos_de_clientes():
    """Transforma datos de clientes."""
    pass
```

❌ **Malo**: Nombres genéricos
```python
@task
def task1():
    pass

@task
def process():
    pass
```

### 3. Uso de Task Groups

✅ **Bueno**: Organizar tareas en grupos
```python
@task_group(group_id="extraction")
def extraction_group():
    api_data = extract_from_api()
    db_data = extract_from_db()
    return [api_data, db_data]
```

❌ **Malo**: Todas las tareas al mismo nivel
```python
# 50+ tareas sin organización
task1 = extract1()
task2 = extract2()
# ... 50+ más
```

### 4. Documentación

✅ **Bueno**: Documentación completa
```python
@task
def procesar_datos(
    datos: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Procesa los datos según la configuración.
    
    Args:
        datos: Lista de diccionarios con los datos a procesar
        config: Configuración opcional para el procesamiento
        
    Returns:
        Diccionario con resultados del procesamiento
        
    Raises:
        ValueError: Si los datos son inválidos
        AirflowFailException: Si el procesamiento falla
    """
    pass
```

❌ **Malo**: Sin documentación
```python
@task
def procesar(datos):
    # Sin docstring, sin type hints
    pass
```

---

## 💻 Mejores Prácticas de Código

### 1. Type Hints

✅ **Bueno**: Type hints completos
```python
from typing import List, Dict, Any, Optional

def procesar_datos(
    datos: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    pass
```

❌ **Malo**: Sin type hints
```python
def procesar_datos(datos, config=None):
    pass
```

### 2. Logging Estructurado

✅ **Bueno**: Logging con contexto
```python
from data.airflow.plugins.approval_cleanup_utils import log_with_context

log_with_context('info', 'Procesando datos', extra={
    'task_id': context['task_instance'].task_id,
    'record_count': len(records),
    'duration_ms': duration
})
```

❌ **Malo**: Print statements
```python
print(f"Processing {len(records)} records")  # No usar print
```

### 3. Configuración Centralizada

✅ **Bueno**: Configuración en plugins
```python
from data.airflow.plugins.approval_cleanup_config import get_config

config = get_config()
batch_size = config['processing']['batch_size']
```

❌ **Malo**: Valores hardcodeados
```python
batch_size = 1000  # Hardcodeado
```

### 4. Validación de Parámetros

✅ **Bueno**: Validar parámetros
```python
from data.airflow.plugins.approval_cleanup_utils import validate_params

@dag(
    params={
        "batch_size": Param(1000, type="integer", minimum=100, maximum=10000),
    }
)
def mi_dag():
    @task
    def procesar(**context):
        params = context["params"]
        validate_params({
            'batch_size': (100, 10000)
        })
        batch_size = params['batch_size']
```

❌ **Malo**: Sin validación
```python
@task
def procesar(**context):
    batch_size = context["params"].get("batch_size", 1000)
    # Sin validar que está en rango válido
```

---

## ⚡ Mejores Prácticas de Performance

### 1. Procesamiento en Lotes

✅ **Bueno**: Procesar en lotes
```python
def procesar_registros(registros: List[Dict]) -> None:
    batch_size = 1000
    for i in range(0, len(registros), batch_size):
        batch = registros[i:i + batch_size]
        procesar_lote(batch)
```

❌ **Malo**: Uno por uno
```python
def procesar_registros(registros: List[Dict]) -> None:
    for registro in registros:
        procesar(registro)  # Muy lento
```

### 2. Connection Pooling

✅ **Bueno**: Reutilizar conexiones
```python
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook

# El plugin maneja connection pooling
pg_hook = get_pg_hook()  # Reutiliza conexiones
```

❌ **Malo**: Nueva conexión por query
```python
def ejecutar_query(sql):
    hook = PostgresHook(postgres_conn_id="db")  # Nueva conexión cada vez
    return hook.get_records(sql)
```

### 3. Caching

✅ **Bueno**: Cachear resultados costosos
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_config():
    # Carga configuración una vez
    return load_config()
```

❌ **Malo**: Cargar cada vez
```python
def get_config():
    # Carga desde archivo cada vez
    return load_config()
```

### 4. Timeouts Apropiados

✅ **Bueno**: Timeouts configurados
```python
@task(execution_timeout=timedelta(hours=2))
def tarea_larga():
    # Tarea que puede tardar
    pass
```

❌ **Malo**: Sin timeout
```python
@task
def tarea_larga():
    # Puede colgar indefinidamente
    pass
```

---

## 🔒 Mejores Prácticas de Seguridad

### 1. Secrets Management

✅ **Bueno**: Usar Airflow Connections
```python
from airflow.providers.postgres.hooks.postgres import PostgresHook

hook = PostgresHook(postgres_conn_id="my_db")  # Secret en Airflow
```

❌ **Malo**: Credenciales en código
```python
password = "my_secret_password"  # ❌ NUNCA hacer esto
```

### 2. Validación de Inputs

✅ **Bueno**: Validar inputs
```python
def procesar_datos(datos: List[Dict]) -> None:
    if not datos:
        raise ValueError("Datos no pueden estar vacíos")
    if not isinstance(datos, list):
        raise TypeError("Datos debe ser una lista")
    # Procesar
```

❌ **Malo**: Sin validación
```python
def procesar_datos(datos):
    # Asume que datos es válido
    for item in datos:
        procesar(item)
```

### 3. Queries Parametrizadas

✅ **Bueno**: Queries parametrizadas
```python
sql = "SELECT * FROM tabla WHERE id = %s"
hook.get_records(sql, parameters=(user_id,))
```

❌ **Malo**: String formatting (SQL injection)
```python
sql = f"SELECT * FROM tabla WHERE id = {user_id}"  # ❌ Vulnerable
```

---

## 🚫 Anti-Patrones

### 1. Variables Globales

❌ **Malo**:
```python
# Variables globales
BATCH_SIZE = 1000
CONFIG = load_config()

@task
def procesar():
    global BATCH_SIZE  # ❌ Evitar
    BATCH_SIZE = 2000
```

✅ **Bueno**:
```python
@task
def procesar():
    config = get_config()
    batch_size = config['batch_size']
    # Usar localmente
```

### 2. Efectos Secundarios en Tareas

❌ **Malo**:
```python
@task
def procesar():
    # Modifica estado global
    global_counter += 1
    # Escribe a archivos del sistema
    open('/tmp/data.txt', 'w').write('data')
```

✅ **Bueno**:
```python
@task
def procesar():
    # Retorna resultado, no modifica estado
    result = compute()
    return result
```

### 3. Dependencias Circulares

❌ **Malo**:
```python
task1 = tarea1(task2)  # task1 depende de task2
task2 = tarea2(task1)  # task2 depende de task1 (circular!)
```

✅ **Bueno**:
```python
# Diseñar flujo lineal o en árbol
data = extract()
transformed = transform(data)
loaded = load(transformed)
```

### 4. Código Duplicado

❌ **Malo**:
```python
# Misma función en múltiples DAGs
def get_pg_hook():
    return PostgresHook(postgres_conn_id="db")
```

✅ **Bueno**:
```python
# En plugin reutilizable
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook
```

---

## 📚 Referencias

- [`docs/DESARROLLO.md`](./DESARROLLO.md) - Guía de desarrollo completa
- [`docs/EJEMPLOS_PRACTICOS.md`](./EJEMPLOS_PRACTICOS.md) - Ejemplos prácticos
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

---

**Versión**: 1.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

