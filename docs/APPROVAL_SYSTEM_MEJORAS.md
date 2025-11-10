# 🚀 Mejoras Recomendadas - Sistema de Aprobaciones

> **Versión**: 1.0 | **Última actualización**: 2024

Guía de mejoras específicas para el sistema de aprobaciones (`approval_cleanup.py`).

## 📋 Tabla de Contenidos

- [Problemas Identificados](#-problemas-identificados)
- [Mejoras Prioritarias](#-mejoras-prioritarias)
- [Plan de Refactorización](#-plan-de-refactorización)
- [Optimizaciones de Performance](#-optimizaciones-de-performance)
- [Mejoras de Código](#-mejoras-de-código)
- [Mejoras de Documentación](#-mejoras-de-documentación)

---

## ⚠️ Problemas Identificados

### 1. Tamaño del Archivo

- **Problema**: 32,609 líneas en un solo archivo
- **Impacto**: 
  - Dificultad para mantener
  - Tiempo de carga lento en Airflow
  - Imposibilidad de reutilizar código
- **Prioridad**: 🔴 Alta

### 2. Variables de Entorno Excesivas

- **Problema**: 100+ variables de entorno hardcodeadas
- **Impacto**:
  - Dificultad para gestionar configuración
  - Riesgo de inconsistencias
  - Código difícil de mantener
- **Prioridad**: 🔴 Alta

### 3. Funciones Auxiliares en el DAG

- **Problema**: Funciones auxiliares mezcladas con la lógica del DAG
- **Impacto**:
  - Código no reutilizable
  - Dificultad para testear
  - Violación de principios SOLID
- **Prioridad**: 🟡 Media

### 4. Falta de Organización

- **Problema**: Tareas no agrupadas lógicamente
- **Impacto**:
  - Dificultad para entender el flujo
  - Imposible navegar eficientemente
- **Prioridad**: 🟡 Media

---

## 🎯 Mejoras Prioritarias

### Prioridad 1: Migrar a Plugins Modulares

**Objetivo**: Reducir el DAG principal usando plugins modulares existentes.

**Pasos**:

1. **Verificar plugins disponibles**:
```bash
python data/airflow/scripts/validate_approval_cleanup.py
```

2. **Usar versión simplificada**:
```python
# En lugar de approval_cleanup.py (32,609 líneas)
# Usar approval_cleanup_simplified_example.py (~400 líneas)

from data.airflow.plugins.approval_cleanup_config import get_config
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook
from data.airflow.plugins.approval_cleanup_queries import get_old_requests_to_archive
```

3. **Beneficios**:
   - ✅ 97% reducción en líneas de código
   - ✅ Código reutilizable
   - ✅ Mejor mantenibilidad
   - ✅ Más fácil de testear

### Prioridad 2: Centralizar Configuración

**Objetivo**: Mover todas las variables de entorno a `approval_cleanup_config.py`.

**Antes**:
```python
# ❌ 100+ líneas de variables de entorno
ENABLE_FEATURE_X = os.getenv("APPROVAL_CLEANUP_FEATURE_X", "true").lower() == "true"
ENABLE_FEATURE_Y = os.getenv("APPROVAL_CLEANUP_FEATURE_Y", "false").lower() == "true"
# ... 100+ más
```

**Después**:
```python
# ✅ Configuración centralizada
from data.airflow.plugins.approval_cleanup_config import get_config

config = get_config()
enable_feature_x = config['features']['feature_x']
enable_feature_y = config['features']['feature_y']
```

### Prioridad 3: Agrupar Tareas con Task Groups

**Objetivo**: Organizar tareas en grupos lógicos.

**Antes**:
```python
# ❌ 150+ tareas sin organización
task1 = tarea1()
task2 = tarea2()
# ... 150+ más
```

**Después**:
```python
# ✅ Tareas agrupadas
@task_group(group_id='cleanup_operations')
def cleanup_operations():
    archive = archive_old_requests()
    notifications = cleanup_notifications()
    return [archive, notifications]

@task_group(group_id='optimization')
def optimization():
    indexes = optimize_indexes()
    vacuum = vacuum_tables()
    return [indexes, vacuum]
```

---

## 📋 Plan de Refactorización

### Fase 1: Preparación (1-2 días)

- [x] Verificar plugins modulares existentes
- [x] Documentar funciones actuales
- [ ] Crear backup del DAG original
- [ ] Establecer entorno de pruebas

### Fase 2: Migración Gradual (1 semana)

- [ ] Migrar funciones de configuración
- [ ] Migrar funciones de operaciones DB
- [ ] Migrar funciones de queries SQL
- [ ] Migrar funciones de análisis
- [ ] Migrar funciones de utilidades

### Fase 3: Simplificación del DAG (2-3 días)

- [ ] Reemplazar código con llamadas a plugins
- [ ] Agrupar tareas en task groups
- [ ] Eliminar código duplicado
- [ ] Optimizar flujo de ejecución

### Fase 4: Testing y Validación (2-3 días)

- [ ] Ejecutar tests unitarios
- [ ] Ejecutar tests de integración
- [ ] Validar en entorno de staging
- [ ] Comparar resultados con versión original

### Fase 5: Deployment (1 día)

- [ ] Deploy a producción
- [ ] Monitorear ejecución
- [ ] Verificar métricas
- [ ] Documentar cambios

---

## ⚡ Optimizaciones de Performance

### 1. Lazy Loading de Configuración

**Problema**: Carga todas las configuraciones al inicio.

**Solución**:
```python
# ❌ Carga todo al inicio
config = get_config()  # Carga 100+ variables

# ✅ Carga solo cuando se necesita
@lru_cache(maxsize=1)
def get_config_section(section: str):
    config = get_config()
    return config.get(section, {})
```

### 2. Connection Pooling

**Problema**: Crea nuevas conexiones para cada query.

**Solución**:
```python
# ✅ Usar connection pooling
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook

# El plugin ya implementa pooling
pg_hook = get_pg_hook()  # Reutiliza conexiones
```

### 3. Query Caching

**Problema**: Ejecuta las mismas queries repetidamente.

**Solución**:
```python
# ✅ Cache de queries frecuentes
from data.airflow.plugins.approval_cleanup_ops import execute_query_with_cache

result = execute_query_with_cache(
    pg_hook,
    "SELECT * FROM config",
    ttl_seconds=300
)
```

### 4. Batch Processing Optimizado

**Problema**: Procesa registros uno por uno.

**Solución**:
```python
# ✅ Procesamiento en lotes adaptativo
from data.airflow.plugins.approval_cleanup_ops import process_batch_adaptive

results = process_batch_adaptive(
    records,
    process_func=process_record,
    initial_batch_size=1000
)
```

---

## 🔧 Mejoras de Código

### 1. Eliminar Código Duplicado

**Problema**: Funciones similares repetidas múltiples veces.

**Solución**: Identificar y consolidar funciones duplicadas usando plugins.

### 2. Mejorar Manejo de Errores

**Antes**:
```python
# ❌ Manejo básico
try:
    result = execute_query(sql)
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

**Después**:
```python
# ✅ Manejo estructurado con retry
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def execute_query_with_retry(sql):
    return execute_query(sql)
```

### 3. Agregar Type Hints

**Antes**:
```python
# ❌ Sin type hints
def process_data(data):
    return process(data)
```

**Después**:
```python
# ✅ Con type hints
from typing import List, Dict, Any

def process_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    return process(data)
```

### 4. Documentación de Funciones

**Antes**:
```python
# ❌ Sin documentación
def archive_requests(requests):
    # archiva requests
    pass
```

**Después**:
```python
# ✅ Con documentación completa
def archive_requests(requests: List[Dict[str, Any]]) -> int:
    """
    Archiva solicitudes antiguas en la tabla de archivo.
    
    Args:
        requests: Lista de solicitudes a archivar
        
    Returns:
        Número de solicitudes archivadas
        
    Raises:
        AirflowFailException: Si falla el archivado
    """
    # Implementación
    pass
```

---

## 📚 Mejoras de Documentación

### 1. Documentar Variables de Entorno

Crear archivo `APPROVAL_CLEANUP_ENV_VARS.md` con todas las variables:

```markdown
# Variables de Entorno - Approval Cleanup

## Configuración Principal

| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `APPROVAL_CLEANUP_RETENTION_YEARS` | Años de retención | 2 | `3` |
| `APPROVAL_CLEANUP_BATCH_SIZE` | Tamaño de lote | 1000 | `2000` |
```

### 2. Diagramas de Flujo

Crear diagramas Mermaid para visualizar:
- Flujo del DAG
- Arquitectura de plugins
- Flujo de datos

### 3. Ejemplos de Uso

Agregar más ejemplos prácticos:
- Casos de uso comunes
- Configuraciones típicas
- Troubleshooting específico

---

## 📊 Métricas de Éxito

### Antes de Mejoras

- Líneas de código: 32,609
- Tiempo de carga: ~30 segundos
- Variables de entorno: 100+
- Funciones auxiliares: 200+
- Testabilidad: Baja

### Después de Mejoras

- Líneas de código: ~400 (97% reducción)
- Tiempo de carga: < 2 segundos (93% mejora)
- Variables centralizadas: 1 archivo
- Funciones en plugins: Reutilizables
- Testabilidad: Alta

---

## 🛠️ Herramientas Disponibles

### Scripts de Análisis

```bash
# Analizar complejidad
python data/airflow/scripts/analyze_approval_cleanup.py

# Validar plugins
python data/airflow/scripts/validate_approval_cleanup.py

# Generar reporte de migración
python data/airflow/scripts/migrate_approval_cleanup.py
```

### Scripts de Refactorización

```bash
# Extraer funciones a plugins
python data/airflow/scripts/extract_to_plugin.py

# Verificar código duplicado
python data/airflow/scripts/find_duplicates.py
```

---

## 📖 Referencias

- [`docs/APPROVAL_SYSTEM.md`](./APPROVAL_SYSTEM.md) - Documentación técnica
- [`data/airflow/README_APPROVAL_CLEANUP.md`](../data/airflow/README_APPROVAL_CLEANUP.md) - Guía completa
- [`data/airflow/dags/approval_cleanup_REFACTORING.md`](../data/airflow/dags/approval_cleanup_REFACTORING.md) - Plan de refactorización

---

**Versión**: 1.0 | **Estado**: Propuesta  
**Mantenido por**: platform-team  
**Última actualización**: 2024

