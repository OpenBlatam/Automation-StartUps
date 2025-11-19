# 📚 Mejores Prácticas para DAGs

Guía de mejores prácticas para desarrollar y mantener DAGs en este proyecto.

## 🗂️ Organización de Archivos

### Ubicación de Nuevos DAGs
1. **Identifica el área principal**: Sales, HR, Finance, Product, Customer Success, Data, Operations, o Integrations
2. **Selecciona la subcarpeta funcional**: Si existe una subcarpeta que coincida con tu funcionalidad, úsala
3. **Crea una nueva subcarpeta si es necesario**: Si la funcionalidad es nueva y merece su propia categoría
4. **Mantén nombres descriptivos**: `funcionalidad_accion.py` (ej: `invoice_generate.py`)

### Convención de Nombres
- **Formato**: `snake_case` para archivos Python
- **Descriptivo**: El nombre debe indicar claramente qué hace el DAG
- **Específico**: Evita nombres genéricos como `process.py` o `main.py`
- **Ejemplos buenos**:
  - ✅ `invoice_generate.py`
  - ✅ `lead_qualification.py`
  - ✅ `stripe_invoice_sync_quickbooks.py`
- **Ejemplos malos**:
  - ❌ `dag1.py`
  - ❌ `process.py`
  - ❌ `main.py`

## 📝 Documentación

### README por DAG Complejo
Si tu DAG tiene más de 200 líneas o lógica compleja, crea un README:
- Ubicación: Mismo directorio que el DAG
- Nombre: `README_[nombre_dag].md`
- Contenido mínimo:
  - Descripción del propósito
  - Parámetros de configuración
  - Dependencias
  - Ejemplos de uso

### Comentarios en Código
- **Docstrings**: Cada función debe tener docstring
- **Comentarios inline**: Explica el "por qué", no el "qué"
- **Type hints**: Usa type hints para mejorar la legibilidad

## 🔧 Estructura de DAGs

### Template Básico
```python
from airflow.decorators import dag, task
from datetime import datetime, timedelta
import pendulum

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='example_dag',
    default_args=default_args,
    description='Descripción clara del propósito',
    schedule_interval='@daily',
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=['area', 'funcionalidad'],
)
def example_dag():
    @task
    def extract():
        """Extrae datos de la fuente"""
        pass
    
    @task
    def transform(data):
        """Transforma los datos"""
        pass
    
    @task
    def load(data):
        """Carga los datos al destino"""
        pass
    
    data = extract()
    transformed = transform(data)
    load(transformed)

example_dag()
```

## 🏷️ Tags y Categorización

### Tags Recomendados
Usa tags para facilitar la búsqueda en Airflow UI:
- **Área**: `sales`, `finance`, `hr`, `product`, `customer-success`, `data`, `operations`, `integrations`
- **Funcionalidad**: `etl`, `reporting`, `sync`, `automation`, `monitoring`
- **Frecuencia**: `daily`, `weekly`, `monthly`, `on-demand`
- **Prioridad**: `critical`, `high`, `medium`, `low`

Ejemplo:
```python
tags=['sales', 'leads', 'daily', 'high']
```

## ⚙️ Configuración y Variables

### Variables de Airflow
- Usa Airflow Variables para configuración sensible
- Prefijo por área: `SALES_`, `FINANCE_`, `HR_`, etc.
- Ejemplo: `SALES_CRM_API_KEY`, `FINANCE_QUICKBOOKS_CLIENT_ID`

### Conexiones
- Nombres descriptivos: `postgres_default`, `s3_default`
- Documenta conexiones en el README del DAG

## 🔄 Dependencias y Orden de Ejecución

### Task Dependencies
- Usa el operador `>>` o `set_downstream()` explícitamente
- Evita dependencias circulares
- Documenta dependencias complejas

### DAG Dependencies
- Si un DAG depende de otro, documenta esto claramente
- Usa `ExternalTaskSensor` cuando sea apropiado

## 🚨 Manejo de Errores

### Retries
- **Críticos**: 3-5 retries con delay exponencial
- **Importantes**: 2-3 retries
- **Operacionales**: 1-2 retries

### Notificaciones
- **Críticos**: Email + Slack/PagerDuty
- **Importantes**: Email
- **Operacionales**: Logs solamente

### Logging
```python
import logging
logger = logging.getLogger(__name__)

@task
def process_data():
    logger.info("Iniciando procesamiento")
    try:
        # código
        logger.info("Procesamiento completado")
    except Exception as e:
        logger.error(f"Error en procesamiento: {str(e)}")
        raise
```

## 📊 Monitoreo y Métricas

### Métricas Clave
- Tiempo de ejecución
- Tasa de éxito/fallo
- Volumen de datos procesados
- Costo de ejecución (si aplica)

### Alertas
- Configura alertas para DAGs críticos
- Monitorea tendencias (ej: tiempo de ejecución aumentando)

## 🧪 Testing

### Tests Unitarios
- Crea tests para lógica compleja
- Ubicación: `tests/` o junto al DAG
- Nombres: `test_[nombre_dag].py`

### Tests de Integración
- Prueba flujos completos en ambiente de desarrollo
- Valida datos de salida

## 🔐 Seguridad

### Credenciales
- ❌ NUNCA hardcodees credenciales
- ✅ Usa Airflow Variables o Connections
- ✅ Usa secretos de Kubernetes si aplica

### Permisos
- Limita acceso a DAGs sensibles
- Usa roles y permisos de Airflow apropiadamente

## 📈 Performance

### Optimizaciones
- Usa `@task` decorator para paralelización
- Implementa caching cuando sea apropiado
- Optimiza queries de base de datos
- Usa `batch_size` apropiado para procesamiento masivo

### Recursos
- Especifica recursos necesarios (CPU, memoria)
- Monitorea uso de recursos

## 🔄 Versionado

### Cambios Importantes
- Documenta cambios breaking en README
- Usa versionado semántico si es necesario
- Comunica cambios a usuarios afectados

## 📋 Checklist Pre-Deploy

Antes de hacer deploy de un nuevo DAG:

- [ ] DAG está en la carpeta correcta
- [ ] Nombre sigue convenciones
- [ ] Tags están configurados
- [ ] Documentación básica incluida
- [ ] Variables y conexiones documentadas
- [ ] Manejo de errores implementado
- [ ] Logging apropiado
- [ ] Tests creados (si aplica)
- [ ] Sin credenciales hardcodeadas
- [ ] Schedule configurado correctamente
- [ ] Dependencias documentadas
- [ ] Notificaciones configuradas (si crítico)

## 🆘 Troubleshooting

### Problemas Comunes

1. **DAG no aparece en UI**
   - Verifica sintaxis Python
   - Revisa logs de Airflow
   - Verifica imports

2. **Task falla consistentemente**
   - Revisa logs del task
   - Verifica conexiones
   - Valida datos de entrada

3. **Performance lenta**
   - Revisa queries
   - Verifica recursos asignados
   - Considera paralelización

## 📚 Recursos Adicionales

- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- READMEs específicos en cada área
- Documentación en `_documentation/`

