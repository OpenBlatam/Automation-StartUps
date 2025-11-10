# 👨‍💻 Guía de Desarrollo

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Guía completa para desarrolladores que trabajan en la plataforma.

## 📋 Tabla de Contenidos

- [Configuración del Entorno](#-configuración-del-entorno)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Crear un Nuevo DAG de Airflow](#-crear-un-nuevo-dag-de-airflow)
- [Crear un Nuevo Workflow en Kestra](#-crear-un-nuevo-workflow-en-kestra)
- [Crear un Nuevo Worker](#-crear-un-nuevo-worker)
- [Testing](#-testing)
- [Code Review](#-code-review)
- [Mejores Prácticas](#-mejores-prácticas)
- [Debugging](#-debugging)
- [Troubleshooting Común](#-troubleshooting-común)

---

## 🚀 Configuración del Entorno

### Requisitos Previos

- Python 3.11+
- Docker y Docker Compose
- Kubernetes CLI (kubectl)
- Helm 3.13+
- Terraform 1.6+
- Git

### Setup Inicial

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd IA

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r data/airflow/requirements.txt

# 4. Configurar variables de entorno
cp data/airflow/ENV_EXAMPLE .env
# Editar .env con tus configuraciones

# 5. Iniciar servicios locales (opcional)
cd data/airflow
docker-compose up -d
```

### Configuración de IDE

#### VS Code

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

#### PyCharm

1. Configurar Python interpreter: `File > Settings > Project > Python Interpreter`
2. Habilitar Ruff: `File > Settings > Tools > Ruff`
3. Configurar Black: `File > Settings > Tools > Black`

---

## 📁 Estructura del Proyecto

```
IA/
├── data/
│   ├── airflow/
│   │   ├── dags/           # DAGs de Airflow
│   │   ├── plugins/        # Plugins y utilidades
│   │   ├── scripts/         # Scripts de utilidad
│   │   └── tests/          # Tests unitarios
│   ├── db/                 # Schemas de base de datos
│   └── integrations/       # Integraciones externas
├── workflow/
│   ├── kestra/             # Workflows de Kestra
│   ├── flowable/           # Procesos BPMN Flowable
│   └── camunda/            # Procesos BPMN Camunda
├── ml/                     # Machine Learning
├── infra/                  # Infraestructura (Terraform, Ansible)
├── kubernetes/             # Manifiestos de Kubernetes
├── observability/          # Observabilidad (Prometheus, Grafana)
├── security/                # Seguridad (Vault, OPA)
└── docs/                   # Documentación
```

---

## ✈️ Crear un Nuevo DAG de Airflow

### Plantilla Básica

```python
"""
DAG para [descripción del propósito].
"""
from __future__ import annotations

from datetime import timedelta
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

# Configuración del DAG
@dag(
    dag_id="mi_nuevo_dag",
    description="Descripción del DAG",
    schedule_interval="@daily",  # o cron expression
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["etl", "datos"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": on_task_failure,
    },
)
def mi_dag():
    """Definición del DAG."""
    
    @task
    def extraer_datos():
        """Extrae datos de la fuente."""
        logger.info("Extrayendo datos...")
        # Tu lógica aquí
        return {"status": "success", "count": 100}
    
    @task
    def transformar_datos(extraccion_result):
        """Transforma los datos."""
        logger.info(f"Transformando {extraccion_result['count']} registros...")
        # Tu lógica aquí
        return {"status": "success"}
    
    @task
    def cargar_datos(transformacion_result):
        """Carga los datos al destino."""
        logger.info("Cargando datos...")
        # Tu lógica aquí
        return {"status": "success"}
    
    # Flujo del DAG
    datos_extraidos = extraer_datos()
    datos_transformados = transformar_datos(datos_extraidos)
    cargar_datos(datos_transformados)

# Instanciar el DAG
mi_dag()
```

### Mejores Prácticas

1. **Usar plugins existentes**: Reutilizar código de `data/airflow/plugins/`
2. **Configuración centralizada**: Usar `etl_config_constants.py` para constantes
3. **Manejo de errores**: Implementar retry logic y logging
4. **Idempotencia**: Asegurar que las tareas sean idempotentes
5. **Documentación**: Documentar cada tarea y parámetros

### Ejemplo con Plugins

```python
from data.airflow.plugins.approval_cleanup_config import get_config
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook, execute_query_with_timeout
from data.airflow.plugins.approval_cleanup_utils import log_with_context

@task
def mi_tarea():
    """Tarea usando plugins."""
    config = get_config()
    pg_hook = get_pg_hook()
    
    log_with_context('info', 'Iniciando tarea...')
    
    result = execute_query_with_timeout(
        pg_hook,
        "SELECT * FROM tabla WHERE fecha > %s",
        parameters=(pendulum.now().subtract(days=1),)
    )
    
    return {"count": len(result)}
```

Ver [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) para más ejemplos.

---

## 🎯 Crear un Nuevo Workflow en Kestra

### Estructura Básica

```yaml
id: mi-workflow
namespace: company
description: Descripción del workflow

tasks:
  - id: extraer
    type: io.kestra.plugin.fs.http.Download
    uri: https://api.example.com/data
    outputFile: /tmp/data.json

  - id: transformar
    type: io.kestra.plugin.scripts.python.Script
    script: |
      import json
      with open('/tmp/data.json') as f:
          data = json.load(f)
      # Transformación aquí
      with open('/tmp/transformed.json', 'w') as f:
          json.dump(data, f)

  - id: cargar
    type: io.kestra.plugin.jdbc.postgresql.CopyIn
    connectionString: "jdbc:postgresql://db:5432/mydb"
    from: /tmp/transformed.json
    table: mi_tabla

triggers:
  - id: schedule
    type: io.kestra.core.models.triggers.types.Schedule
    cron: "0 8 * * *"  # Diario a las 8 AM
```

### Características Avanzadas

- **Error Handling**: Manejo de errores con `onFailure`
- **Parallel Execution**: Tareas paralelas con `parallel`
- **Conditional Logic**: Flujos condicionales con `if`
- **Variables**: Variables dinámicas con `{{ variables.var_name }}`

Ver [`workflow/kestra/README.md`](../workflow/kestra/README.md) para más ejemplos.

---

## 🔧 Crear un Nuevo Worker

### Worker de Python (Camunda)

```python
"""
Worker para procesar tareas externas de Camunda.
"""
import os
import logging
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

logger = logging.getLogger(__name__)

# Configuración
CAMUNDA_URL = os.getenv("CAMUNDA_URL", "http://camunda:8080/engine-rest")
TOPIC_NAME = "mi-topic"

def process_task(task: ExternalTask) -> TaskResult:
    """Procesa una tarea externa."""
    try:
        # Obtener variables
        variables = task.get_variables()
        data = variables.get("data")
        
        logger.info(f"Procesando tarea {task.get_task_id()} con datos: {data}")
        
        # Tu lógica aquí
        result = process_data(data)
        
        return task.complete({
            "result": result,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error procesando tarea: {e}")
        return task.failure(
            error_message=str(e),
            error_details=str(e),
            max_retries=3,
            retry_timeout=5000
        )

if __name__ == "__main__":
    # Configurar worker
    worker = ExternalTaskWorker(
        worker_id="mi-worker",
        base_url=CAMUNDA_URL,
        config={
            "maxTasks": 1,
            "lockDuration": 10000,
            "asyncResponseTimeout": 5000
        }
    )
    
    # Suscribirse al topic
    worker.subscribe(TOPIC_NAME, process_task)
```

Ver [`workflow/camunda/README_worker.md`](../workflow/camunda/README_worker.md) para más detalles.

---

## 🧪 Testing

### Tests Unitarios

```python
"""
Tests unitarios para mi módulo.
"""
import pytest
from unittest.mock import Mock, patch
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook

def test_get_pg_hook():
    """Test para obtener hook de PostgreSQL."""
    with patch('data.airflow.plugins.approval_cleanup_ops.PostgresHook') as mock_hook:
        hook = get_pg_hook()
        assert hook is not None
        mock_hook.assert_called_once()

def test_execute_query():
    """Test para ejecutar query."""
    # Tu test aquí
    pass
```

### Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests específicos
pytest tests/test_approval_cleanup_ops.py

# Con cobertura
pytest --cov=data.airflow.plugins --cov-report=html

# Tests en paralelo
pytest -n auto
```

### Tests de Integración

```python
"""
Tests de integración con base de datos real.
"""
import pytest
from airflow.providers.postgres.hooks.postgres import PostgresHook

@pytest.fixture
def pg_hook():
    """Fixture para hook de PostgreSQL."""
    return PostgresHook(postgres_conn_id="test_db")

def test_integration_query(pg_hook):
    """Test de integración con BD."""
    result = pg_hook.get_records("SELECT 1")
    assert result == [(1,)]
```

---

## 📝 Code Review

### Checklist de Code Review

- [ ] **Funcionalidad**: ¿El código hace lo que se espera?
- [ ] **Testing**: ¿Hay tests adecuados?
- [ ] **Documentación**: ¿Está documentado el código?
- [ ] **Performance**: ¿Hay problemas de performance?
- [ ] **Seguridad**: ¿Hay vulnerabilidades de seguridad?
- [ ] **Estilo**: ¿Sigue las convenciones del proyecto?
- [ ] **Error Handling**: ¿Maneja errores correctamente?
- [ ] **Logging**: ¿Tiene logging apropiado?

### Convenciones de Código

#### Python

- **PEP 8**: Seguir guía de estilo PEP 8
- **Type Hints**: Usar type hints donde sea posible
- **Docstrings**: Documentar funciones y clases
- **Line Length**: Máximo 100 caracteres

```python
def procesar_datos(
    datos: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Procesa los datos según la configuración.
    
    Args:
        datos: Lista de diccionarios con los datos
        config: Configuración opcional
        
    Returns:
        Diccionario con resultados del procesamiento
        
    Raises:
        ValueError: Si los datos son inválidos
    """
    # Implementación
    pass
```

#### YAML (Kestra)

- **Indentación**: 2 espacios
- **Comentarios**: Explicar secciones complejas
- **Nombres**: Usar nombres descriptivos

---

## ✅ Mejores Prácticas

### 1. Manejo de Errores

```python
# ✅ Bueno
try:
    result = process_data(data)
    logger.info(f"Procesado exitosamente: {result}")
except ValueError as e:
    logger.error(f"Error de validación: {e}")
    raise
except Exception as e:
    logger.exception(f"Error inesperado: {e}")
    raise AirflowFailException(f"Error procesando datos: {e}")

# ❌ Malo
result = process_data(data)  # Sin manejo de errores
```

### 2. Logging

```python
# ✅ Bueno
logger.info("Iniciando procesamiento", extra={
    "task_id": task_id,
    "record_count": len(records)
})

# ❌ Malo
print(f"Processing {len(records)} records")  # No usar print
```

### 3. Configuración

```python
# ✅ Bueno - Usar variables de entorno
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))

# ❌ Malo - Hardcodear valores
BATCH_SIZE = 1000
```

### 4. Idempotencia

```python
# ✅ Bueno - Idempotente
@task
def cargar_datos():
    """Carga datos de forma idempotente."""
    # Verificar si ya existe
    if datos_ya_existen():
        logger.info("Datos ya cargados, saltando...")
        return
    
    # Cargar datos
    cargar()

# ❌ Malo - No idempotente
@task
def cargar_datos():
    """Carga datos (siempre inserta)."""
    insertar_datos()  # Puede duplicar
```

### 5. Performance

```python
# ✅ Bueno - Procesamiento en lotes
def procesar_registros(registros: List[Dict]) -> None:
    """Procesa registros en lotes."""
    batch_size = 1000
    for i in range(0, len(registros), batch_size):
        batch = registros[i:i + batch_size]
        procesar_lote(batch)

# ❌ Malo - Procesamiento uno por uno
def procesar_registros(registros: List[Dict]) -> None:
    """Procesa registros uno por uno."""
    for registro in registros:
        procesar(registro)  # Muy lento
```

---

## 🐛 Debugging

### Debugging Local

```bash
# Ejecutar DAG localmente
airflow dags test mi_dag 2024-01-01

# Ejecutar tarea específica
airflow tasks test mi_dag mi_tarea 2024-01-01

# Con Python debugger
python -m pdb -c continue script.py
```

### Debugging en Kubernetes

```bash
# Ver logs de un pod
kubectl logs -f <pod-name> -n <namespace>

# Ejecutar shell en pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Ver eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

### Debugging con Logs

```python
# Logging estructurado
logger.info("Procesando datos", extra={
    "task_id": task_id,
    "record_count": len(records),
    "duration_ms": duration
})

# Logging con niveles
logger.debug("Detalles de depuración")
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error")
logger.exception("Excepción con traceback")
```

---

## 🔍 Troubleshooting Común

### Error: "Module not found"

```bash
# Verificar que el módulo está en PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project"

# Verificar imports
python -c "from data.airflow.plugins.approval_cleanup_config import get_config; print('OK')"
```

### Error: "Database connection failed"

```bash
# Verificar connection ID en Airflow
airflow connections list | grep <connection_id>

# Probar conexión
python -c "from airflow.providers.postgres.hooks.postgres import PostgresHook; h = PostgresHook(postgres_conn_id='<id>'); print(h.get_conn())"
```

### Error: "Task timeout"

```python
# Aumentar timeout en la tarea
@task(
    execution_timeout=timedelta(hours=2)  # Aumentar timeout
)
def mi_tarea_lenta():
    # Tu código
    pass
```

---

## 📚 Recursos Adicionales

- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Kestra Documentation](https://kestra.io/docs/)
- [Camunda External Task Pattern](https://docs.camunda.org/manual/latest/user-guide/process-engine/external-tasks/)

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

