# Arquitecturas y Ejemplos Avanzados de Airbyte

Este documento contiene diagramas de arquitectura y ejemplos avanzados de integración de Airbyte con la plataforma.

## 🏗️ Arquitecturas Comunes

### 1. Pipeline Completo: Stripe → S3 → Databricks → Snowflake

```
┌─────────────┐
│   Stripe    │  (Source)
│   API       │
└──────┬──────┘
       │ Airbyte Sync
       ▼
┌─────────────┐
│     S3      │  (Data Lake)
│  Parquet    │  biz-datalake-dev/airbyte/stripe/
└──────┬──────┘
       │
       │ Spark/Athena Query
       ▼
┌─────────────┐
│ Databricks  │  (Transform)
│   Jobs      │  (Ya configurado en tu plataforma)
└──────┬──────┘
       │
       │ Transformed Data
       ▼
┌─────────────┐
│  Snowflake  │  (Analytics)
│  Warehouse  │  (Para dashboards y BI)
└─────────────┘
```

**Implementación**:

```python
# data/airflow/dags/stripe_datalake_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync

with DAG(
    dag_id="stripe_datalake_pipeline",
    schedule_interval=timedelta(hours=6),
    ...
) as dag:
    
    # 1. Sync Stripe a S3 (Airbyte)
    sync_to_s3 = PythonOperator(
        task_id="sync_stripe_to_s3",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_S3_CONNECTION_ID"),
        },
    )
    
    # 2. Procesar con Databricks
    process_databricks = DatabricksRunNowOperator(
        task_id="process_stripe_data",
        job_id=Variable.get("DATABRICKS_STRIPE_JOB_ID"),
        notebook_params={
            "s3_path": "s3://biz-datalake-dev/airbyte/stripe/",
            "output_path": "s3://biz-datalake-dev/processed/stripe/",
        },
    )
    
    # 3. Cargar a Snowflake (si aplica)
    load_to_snowflake = PythonOperator(
        task_id="load_to_snowflake",
        python_callable=load_processed_data_to_snowflake,
    )
    
    sync_to_s3 >> process_databricks >> load_to_snowflake
```

### 2. Multi-Source Consolidation: CRM + Payments → Analytics

```
┌──────────┐      ┌──────────┐      ┌──────────┐
│  Stripe  │      │ HubSpot  │      │PostgreSQL│
│  (API)   │      │   (API)  │      │  (DB)    │
└────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                 │
     │ Airbyte         │ Airbyte         │ Airbyte
     │                 │                 │
     ▼                 ▼                 ▼
┌─────────────────────────────────────────────┐
│         PostgreSQL Analytics                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │stripe_raw│  │hubspot_  │  │etl_      │ │
│  │          │  │raw       │  │processed │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────┘
                    │
                    │ Transform
                    ▼
┌─────────────────────────────────────────────┐
│              Snowflake                      │
│         (Data Warehouse)                    │
│  ┌──────────────────────────────────────┐  │
│  │  Unified Analytics Tables            │  │
│  │  - customers_unified                 │  │
│  │  - revenue_analytics                 │  │
│  │  - sales_pipeline                    │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                    │
                    │ BI Tools
                    ▼
        ┌───────────────────────┐
        │  Grafana / Tableau   │
        │      Dashboards       │
        └───────────────────────┘
```

**Implementación**:

```python
# data/airflow/dags/multi_source_analytics.py
with DAG("multi_source_analytics", ...) as dag:
    
    # Sync múltiples fuentes en paralelo
    stripe_sync = PythonOperator(
        task_id="sync_stripe",
        python_callable=trigger_airbyte_sync,
        op_kwargs={"connection_id": Variable.get("AIRBYTE_STRIPE_PG_CONNECTION_ID")},
    )
    
    hubspot_sync = PythonOperator(
        task_id="sync_hubspot",
        python_callable=trigger_airbyte_sync,
        op_kwargs={"connection_id": Variable.get("AIRBYTE_HUBSPOT_PG_CONNECTION_ID")},
    )
    
    pg_sync = PythonOperator(
        task_id="sync_postgres",
        python_callable=trigger_airbyte_sync,
        op_kwargs={"connection_id": Variable.get("AIRBYTE_PG_PG_CONNECTION_ID")},
    )
    
    # Esperar a que todas completen
    all_syncs = [stripe_sync, hubspot_sync, pg_sync]
    
    # Transformar y consolidar
    transform = PythonOperator(
        task_id="transform_and_consolidate",
        python_callable=transform_unified_data,
    )
    
    # Cargar a Snowflake
    load_snowflake = PythonOperator(
        task_id="load_to_snowflake",
        python_callable=load_to_snowflake,
    )
    
    all_syncs >> transform >> load_snowflake
```

### 3. Real-time CDC: PostgreSQL → PostgreSQL (Multi-región)

```
┌─────────────────────────────────┐
│  PostgreSQL (Primary)          │
│  - Production Database         │
│  - WAL Logs Enabled            │
│  - Logical Replication Slot    │
└────────────┬────────────────────┘
             │
             │ CDC (Logical Replication)
             │
             ▼
┌─────────────────────────────────┐
│      Airbyte Worker             │
│  - Reads from WAL               │
│  - Transforms if needed         │
└────────────┬────────────────────┘
             │
             │ Sync
             ▼
┌─────────────────────────────────┐
│  PostgreSQL (Replica)          │
│  - Analytics Database           │
│  - Read-only for BI tools       │
│  - Different Region             │
└─────────────────────────────────┘
```

**Implementación**:

```python
# data/airflow/dags/postgres_cdc_replication.py
with DAG("postgres_cdc_replication", ...) as dag:
    
    # CDC sync es continuo, solo verificamos que esté corriendo
    check_cdc_health = PythonOperator(
        task_id="check_cdc_health",
        python_callable=check_postgres_cdc_status,
    )
    
    # Verificar lag de replicación
    check_replication_lag = PythonOperator(
        task_id="check_replication_lag",
        python_callable=check_replication_lag,
        op_kwargs={"max_lag_seconds": 300},  # 5 minutos máximo
    )
    
    check_cdc_health >> check_replication_lag
```

## 📊 Casos de Uso Avanzados

### Caso 1: ETL Completo con Validación

```python
# data/airflow/dags/stripe_etl_with_validation.py
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync, validate_sync_results
from airflow.operators.python import PythonOperator
from airflow.providers.great_expectations.operators.great_expectations import GreatExpectationsOperator

with DAG("stripe_etl_validated", ...) as dag:
    
    # 1. Sync desde Stripe
    sync = PythonOperator(
        task_id="sync_stripe",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_PG_CONNECTION_ID"),
            "validate_connection": True,
        },
    )
    
    # 2. Validar que se sincronizaron datos
    validate_records = PythonOperator(
        task_id="validate_min_records",
        python_callable=validate_sync_results,
        op_kwargs={"min_records": 100},
    )
    
    # 3. Validar calidad de datos con Great Expectations
    validate_quality = GreatExpectationsOperator(
        task_id="validate_data_quality",
        data_context_root_dir="/opt/airflow/gx",
        checkpoint_name="stripe_post_sync_checkpoint",
        fail_task_on_validation_failure=True,
    )
    
    # 4. Transformar datos
    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_stripe_data,
    )
    
    # 5. Cargar a destino final
    load = PythonOperator(
        task_id="load_to_warehouse",
        python_callable=load_to_warehouse,
    )
    
    sync >> validate_records >> validate_quality >> transform >> load
```

### Caso 2: Sincronización Condicional Basada en Eventos

```python
# data/airflow/dags/event_driven_airbyte_sync.py
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor

def should_sync(**context):
    """Determina si debe sincronizar basado en eventos"""
    # Verificar si hay nuevos datos en source
    # Ejemplo: Verificar timestamp de última actualización
    last_sync = context['ti'].xcom_pull(key='last_sync_time')
    current_time = datetime.now()
    
    # Solo sync si han pasado más de 6 horas
    if (current_time - last_sync).total_seconds() > 21600:
        return True
    
    # O verificar si hay eventos nuevos
    # (ej: mensajes en Kafka, webhooks, etc.)
    return False

with DAG("event_driven_sync", schedule_interval=None, ...) as dag:
    
    # Esperar evento (ej: webhook de Stripe)
    wait_for_event = ExternalTaskSensor(
        task_id="wait_for_stripe_webhook",
        external_dag_id="stripe_webhook_processor",
        external_task_id="process_webhook",
        timeout=3600,
    )
    
    # Decidir si sync
    check_condition = PythonOperator(
        task_id="check_sync_condition",
        python_callable=should_sync,
    )
    
    # Sync si condición se cumple
    sync = PythonOperator(
        task_id="sync_if_needed",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_PG_CONNECTION_ID"),
        },
        trigger_rule="one_success",  # Ejecutar si condición es True
    )
    
    wait_for_event >> check_condition >> sync
```

### Caso 3: Pipeline con Retry y Fallback

```python
# data/airflow/dags/resilient_airbyte_sync.py
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

def sync_with_fallback(**context):
    """Sync con fallback a método alternativo"""
    try:
        # Intentar sync principal
        return trigger_airbyte_sync(
            connection_id=Variable.get("AIRBYTE_STRIPE_PG_CONNECTION_ID"),
            task_instance=context['ti'],
        )
    except Exception as e:
        logger.warning(f"Primary sync failed: {e}, trying fallback")
        # Fallback: Sync desde backup o método alternativo
        return sync_from_backup(context['ti'])

with DAG("resilient_sync", ...) as dag:
    
    # Sync principal
    primary_sync = PythonOperator(
        task_id="primary_sync",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_PG_CONNECTION_ID"),
        },
        retries=3,
        retry_delay=timedelta(minutes=10),
    )
    
    # Fallback si falla
    fallback_sync = PythonOperator(
        task_id="fallback_sync",
        python_callable=sync_with_fallback,
        trigger_rule=TriggerRule.ALL_FAILED,  # Solo si primary falla
    )
    
    # Validación final
    validate = PythonOperator(
        task_id="validate_sync",
        python_callable=validate_sync_results,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )
    
    primary_sync >> fallback_sync >> validate
```

## 🔄 Patterns de Integración

### Pattern 1: Fan-out (Una fuente, múltiples destinos)

```
      ┌─────────┐
      │ Stripe  │
      └────┬────┘
           │
           │ Airbyte
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
┌─────┐ ┌─────┐ ┌─────┐
│  S3 │ │  PG │ │  SF │
└─────┘ └─────┘ └─────┘
```

**Uso**: Mismo dato en diferentes formatos para diferentes propósitos.

### Pattern 2: Fan-in (Múltiples fuentes, un destino)

```
┌─────┐ ┌─────┐ ┌─────┐
│ S1  │ │ S2  │ │ S3  │
└──┬──┘ └──┬──┘ └──┬──┘
   │       │       │
   └───┬───┴───┬───┘
       │       │
       ▼       ▼
    ┌───────────┐
    │ Snowflake │
    └───────────┘
```

**Uso**: Consolidar datos de múltiples fuentes en un data warehouse.

### Pattern 3: Pipeline en Cadena

```
S1 → D1 → Transform → D2 → Analytics
```

**Uso**: Procesar datos en etapas con transformaciones intermedias.

## 📈 Performance Tuning

### Optimización de Sincronizaciones Grandes

```python
# Para sincronizaciones muy grandes, usar configuración específica
def optimized_sync(**context):
    hook = AirbyteHook(
        api_url=get_airbyte_api_url(),
        username=get_airbyte_credentials()[0],
        password=get_airbyte_credentials()[1],
        max_retries=5,  # Más retries para syncs grandes
    )
    
    # Trigger sync con configuración especial
    job_info = hook.trigger_sync(
        connection_id=Variable.get("AIRBYTE_LARGE_SYNC_CONNECTION_ID"),
        retry_on_failure=True,
    )
    
    # Wait con timeout más largo
    return hook.wait_for_job_completion(
        job_id=job_info.get("jobId"),
        timeout_minutes=720,  # 12 horas para syncs muy grandes
        check_interval=60,  # Verificar cada minuto
    )
```

### Parallelización de Sincronizaciones

```python
# Ejecutar múltiples syncs en paralelo
with DAG("parallel_syncs", ...) as dag:
    
    syncs = []
    for source in ["stripe", "hubspot", "salesforce"]:
        sync = PythonOperator(
            task_id=f"sync_{source}",
            python_callable=trigger_airbyte_sync,
            op_kwargs={
                "connection_id": Variable.get(f"AIRBYTE_{source.upper()}_CONNECTION_ID"),
            },
        )
        syncs.append(sync)
    
    # Todas en paralelo
    # No hay dependencias entre ellas
```

## 🔐 Seguridad en Integraciones

### Uso de External Secrets

```python
# Todas las credenciales vienen de External Secrets
# No hardcodear nunca en código

# En Airflow Variables (referencias a secrets):
AIRBYTE_API_URL = "http://airbyte-server.integration.svc.cluster.local:8000"
AIRBYTE_API_USERNAME = "airbyte"  # No sensible
AIRBYTE_API_PASSWORD = "{{ from_secret:airbyte/api-password }}"  # Desde External Secrets
```

### Network Isolation

```yaml
# Ya configurado en security/networkpolicies/airbyte.yaml
# Solo permite comunicación necesaria
```

---

**Última actualización**: 2025-01-15  
**Versión**: 1.0

