# Integración Airbyte con Airflow

Este documento describe cómo usar Airbyte junto con Airflow para orquestar sincronizaciones de datos.

## Resumen

Airbyte proporciona más de 600 conectores listos para sincronizar datos entre fuentes y destinos. Airflow orquesta cuándo y cómo ejecutar estas sincronizaciones, permitiendo:

- **Flujos complejos**: Orquestar múltiples sincronizaciones con dependencias
- **Transformaciones**: Ejecutar transformaciones entre sincronizaciones
- **Validación**: Verificar calidad de datos después de sincronizar
- **Alertas**: Notificaciones personalizadas en caso de fallos
- **Scheduling avanzado**: Horarios complejos basados en eventos o condiciones

## Configuración

### 1. Variables de Airflow

Configurar las siguientes variables en Airflow (UI → Admin → Variables o External Secrets):

```python
# URL de la API de Airbyte
AIRBYTE_API_URL = "http://airbyte-server.integration.svc.cluster.local:8000"

# Credenciales de Airbyte
AIRBYTE_API_USERNAME = "airbyte"
AIRBYTE_API_PASSWORD = "<password>"  # Usar External Secrets

# IDs de conexiones en Airbyte (obtener desde la UI de Airbyte)
AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID = "<connection-id>"
AIRBYTE_HUBSPOT_CONNECTION_ID = "<connection-id>"
AIRBYTE_SALESFORCE_CONNECTION_ID = "<connection-id>"
```

### 2. Obtener Connection IDs

1. Acceder a la UI de Airbyte: `https://airbyte.example.com`
2. Crear/editar una conexión (Source → Destination)
3. Copiar el Connection ID desde la URL o desde la API:
   ```bash
   curl -u username:password \
     http://airbyte-server:8000/api/v1/connections/list
   ```

## Uso de los DAGs

### DAG: `airbyte_stripe_to_postgres`

Sincroniza datos de Stripe hacia PostgreSQL cada 6 horas.

**Configuración**:
- Crear conexión en Airbyte: Stripe → PostgreSQL
- Configurar variable `AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID`

### DAG: `airbyte_multi_source_sync`

Ejecuta múltiples sincronizaciones en paralelo (Stripe, HubSpot, Salesforce).

**Configuración**:
- Crear conexiones en Airbyte para cada fuente
- Configurar variables `AIRBYTE_STRIPE_CONNECTION_ID`, `AIRBYTE_HUBSPOT_CONNECTION_ID`, etc.

### DAG: `airbyte_event_driven_sync`

Triggea sincronizaciones basadas en eventos o manualmente.

**Uso manual**:
1. Trigger DAG manualmente desde Airflow UI
2. Proporcionar configuración JSON:
   ```json
   {
     "connection_id": "abc-123-def-456"
   }
   ```

**Uso desde webhook**:
- Integrar con un endpoint que reciba eventos y trigger el DAG con `connection_id` en la configuración

## Ejemplos Avanzados

### 1. Sincronización seguida de transformación

```python
from airflow.operators.python import PythonOperator

def transform_data(**context):
    # Transformar datos después de la sincronización
    # Por ejemplo, limpieza, agregaciones, etc.
    pass

# En el DAG
stripe_sync >> transform_data_task
```

### 2. Validación con Great Expectations

```python
from airflow.providers.great_expectations.operators.great_expectations import GreatExpectationsOperator

# Después de sincronizar, validar datos
validate_task = GreatExpectationsOperator(
    task_id="validate_synced_data",
    data_context_root_dir="/opt/airflow/gx",
    checkpoint_name="stripe_postgres_checkpoint",
)
```

### 3. Notificaciones personalizadas

```python
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email

def notify_on_success(**context):
    # Enviar notificación cuando sincronización complete
    send_email(
        to=["data-team@example.com"],
        subject="Airbyte sync succeeded",
        html_content=f"Sync {context['ti'].xcom_pull(key='airbyte_job_id')} completed successfully"
    )
```

## Conectores Comunes

Airbyte incluye conectores para:

- **Sales & CRM**: Stripe, HubSpot, Salesforce, Zendesk
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Data Warehouses**: Snowflake, BigQuery, Redshift, Databricks
- **APIs**: REST APIs, GraphQL, Google Sheets
- **Cloud Storage**: S3, GCS, Azure Blob Storage
- **Analytics**: Google Analytics, Mixpanel, Amplitude

Ver lista completa: https://docs.airbyte.com/integrations/

## Mejores Prácticas

1. **Usar Airbyte para ETL simple**: Para extracción y carga de datos (EL)
2. **Usar Airflow para orquestación**: Para flujos complejos con múltiples pasos
3. **Monitoreo**: Usar ServiceMonitors de Prometheus para métricas
4. **Retries**: Configurar retries en Airflow para manejar fallos temporales
5. **Timeouts**: Ajustar timeouts según el tamaño de datos a sincronizar
6. **Paralelización**: Ejecutar sincronizaciones independientes en paralelo
7. **Secrets**: Usar External Secrets para credenciales sensibles

## Troubleshooting

### Error: "Connection refused"

- Verificar que el servicio de Airbyte esté corriendo: `kubectl get pods -n integration -l app=airbyte`
- Verificar la URL de la API en variables de Airflow

### Error: "Authentication failed"

- Verificar credenciales en External Secrets
- Verificar variables `AIRBYTE_API_USERNAME` y `AIRBYTE_API_PASSWORD`

### Error: "Job timed out"

- Aumentar `timeout_minutes` en `wait_for_job_completion()`
- Verificar recursos de workers de Airbyte

### Job se queda en "pending"

- Verificar que haya workers disponibles: `kubectl get pods -n integration -l app=airbyte,component=worker`
- Verificar recursos (CPU/memoria) disponibles en el cluster

## Mejoras Implementadas

### Hook Mejorado

El `AirbyteHook` ahora incluye:
- ✅ Retries automáticos con exponential backoff
- ✅ Validación de respuestas de API
- ✅ Logging estructurado y detallado
- ✅ Métodos adicionales: `get_connection_info()`, `list_connections()`

### Validación Post-Sync

Nueva función `validate_sync_results()` para validar que las sincronizaciones hayan transferido datos:
- Valida número mínimo de registros
- Guarda estadísticas en XCom
- Permite detección temprana de problemas

### Seguridad

- **NetworkPolicies**: Control granular de tráfico de red (`security/networkpolicies/airbyte.yaml`)
- **External Secrets**: Gestión automática de credenciales (`security/secrets/externalsecrets-airbyte.yaml`)

### Ejemplos Avanzados

Ver `airbyte_advanced_examples.py` para:
- Reset de conexiones
- Sincronizaciones en cadena
- Sincronizaciones condicionales
- Notificaciones personalizadas

**Ver detalles completos**: `kubernetes/integration/IMPROVEMENTS_AIRBYTE.md`

## Referencias

- [Documentación oficial de Airbyte](https://docs.airbyte.com/)
- [Airbyte Helm Chart](https://github.com/airbytehq/airbyte-helm-charts)
- [Lista de conectores](https://docs.airbyte.com/integrations/)
- [Airflow HTTP Provider](https://airflow.apache.org/docs/apache-airflow-providers-http/stable/index.html)
- **Mejoras implementadas**: `kubernetes/integration/IMPROVEMENTS_AIRBYTE.md`

