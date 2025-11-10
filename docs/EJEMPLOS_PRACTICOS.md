# 💡 Ejemplos Prácticos

> **Versión**: 1.0 | **Última actualización**: 2024

Ejemplos prácticos y casos de uso comunes de la plataforma.

## 📋 Tabla de Contenidos

- [Ejemplos de Airflow](#-ejemplos-de-airflow)
- [Ejemplos de Kestra](#-ejemplos-de-kestra)
- [Ejemplos de Integraciones](#-ejemplos-de-integraciones)
- [Ejemplos de Monitoreo](#-ejemplos-de-monitoreo)
- [Casos de Uso Completos](#-casos-de-uso-completos)

---

## ✈️ Ejemplos de Airflow

### Ejemplo 1: DAG Simple de ETL

```python
"""
DAG simple para extraer, transformar y cargar datos.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task

@dag(
    dag_id="etl_simple",
    description="ETL simple de ejemplo",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["etl", "ejemplo"],
)
def etl_simple():
    
    @task
    def extract():
        """Extrae datos de la fuente."""
        # Tu lógica de extracción aquí
        return {"records": 100, "status": "success"}
    
    @task
    def transform(extract_result):
        """Transforma los datos."""
        records = extract_result["records"]
        # Tu lógica de transformación aquí
        return {"transformed": records, "status": "success"}
    
    @task
    def load(transform_result):
        """Carga los datos al destino."""
        # Tu lógica de carga aquí
        return {"loaded": transform_result["transformed"], "status": "success"}
    
    # Flujo
    data = extract()
    transformed = transform(data)
    load(transformed)

etl_simple()
```

### Ejemplo 2: DAG con Retry y Notificaciones

```python
"""
DAG con manejo de errores y notificaciones.
"""
from __future__ import annotations
from datetime import timedelta
import logging
import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)

@dag(
    dag_id="etl_with_notifications",
    description="ETL con notificaciones y retry",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": lambda context: notify_slack(
            context,
            message=f"❌ DAG {context['dag'].dag_id} falló"
        ),
    },
    tags=["etl", "notifications"],
)
def etl_with_notifications():
    
    @task(retries=3, retry_delay=timedelta(minutes=2))
    def process_data():
        """Procesa datos con retry."""
        try:
            # Tu lógica aquí
            pg_hook = PostgresHook(postgres_conn_id="postgres_default")
            result = pg_hook.get_records("SELECT COUNT(*) FROM tabla")
            logger.info(f"Procesados {result[0][0]} registros")
            return {"status": "success", "count": result[0][0]}
        except Exception as e:
            logger.error(f"Error procesando datos: {e}")
            raise
    
    @task
    def notify_success(process_result):
        """Notifica éxito."""
        notify_slack(
            context=None,
            message=f"✅ Procesados {process_result['count']} registros exitosamente"
        )
        return process_result
    
    result = process_data()
    notify_success(result)

etl_with_notifications()
```

### Ejemplo 3: DAG con Task Groups

```python
"""
DAG organizado con task groups.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task, task_group

@dag(
    dag_id="etl_with_groups",
    description="ETL con task groups",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["etl", "groups"],
)
def etl_with_groups():
    
    @task_group(group_id="extraction")
    def extraction_group():
        """Grupo de tareas de extracción."""
        
        @task
        def extract_from_api():
            return {"source": "api", "records": 100}
        
        @task
        def extract_from_db():
            return {"source": "db", "records": 200}
        
        return [extract_from_api(), extract_from_db()]
    
    @task_group(group_id="transformation")
    def transformation_group(extracted_data):
        """Grupo de tareas de transformación."""
        
        @task
        def validate_data(data):
            return {"validated": True, "data": data}
        
        @task
        def clean_data(validated_data):
            return {"cleaned": True, "data": validated_data}
        
        validated = validate_data(extracted_data)
        return clean_data(validated)
    
    @task
    def load_data(transformed_data):
        """Carga datos transformados."""
        return {"loaded": True, "data": transformed_data}
    
    # Flujo
    extracted = extraction_group()
    transformed = transformation_group(extracted)
    load_data(transformed)

etl_with_groups()
```

### Ejemplo 4: DAG con Parámetros Dinámicos

```python
"""
DAG que acepta parámetros dinámicos.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param

@dag(
    dag_id="etl_with_params",
    description="ETL con parámetros dinámicos",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    params={
        "source_table": Param("tabla_default", type="string"),
        "batch_size": Param(1000, type="integer", minimum=100, maximum=10000),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["etl", "params"],
)
def etl_with_params():
    
    @task
    def process_with_params(**context):
        """Procesa con parámetros del DAG."""
        params = context["params"]
        source_table = params.get("source_table", "tabla_default")
        batch_size = params.get("batch_size", 1000)
        dry_run = params.get("dry_run", False)
        
        if dry_run:
            return {"status": "dry_run", "would_process": batch_size}
        
        # Tu lógica aquí usando source_table y batch_size
        return {"status": "success", "processed": batch_size}
    
    process_with_params()

etl_with_params()

# Ejecutar con parámetros:
# airflow dags trigger etl_with_params --conf '{"source_table": "mi_tabla", "batch_size": 2000}'
```

### Ejemplo 5: DAG usando Plugins de Approval Cleanup

```python
"""
Ejemplo de uso de plugins modulares de approval_cleanup.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.approval_cleanup_config import get_config
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook, execute_query_with_timeout
from data.airflow.plugins.approval_cleanup_queries import get_old_requests_to_archive
from data.airflow.plugins.approval_cleanup_utils import log_with_context

@dag(
    dag_id="cleanup_using_plugins",
    description="Limpieza usando plugins modulares",
    schedule_interval="@weekly",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["cleanup", "plugins"],
)
def cleanup_using_plugins():
    
    @task
    def archive_old_requests(**context):
        """Archiva solicitudes antiguas usando plugins."""
        config = get_config()
        pg_hook = get_pg_hook()
        
        log_with_context('info', 'Iniciando archivado...', extra={
            'task_id': context['task_instance'].task_id
        })
        
        retention_years = config['retention']['years']
        old_requests = get_old_requests_to_archive(
            pg_hook,
            retention_years=retention_years,
            limit=config['processing']['batch_size']
        )
        
        log_with_context('info', f'Encontradas {len(old_requests)} solicitudes antiguas')
        
        return {"archived": len(old_requests), "status": "success"}
    
    archive_old_requests()

cleanup_using_plugins()
```

---

## 🎯 Ejemplos de Kestra

### Ejemplo 1: Workflow Simple

```yaml
id: ejemplo-simple
namespace: company
description: Workflow simple de ejemplo

tasks:
  - id: hello
    type: io.kestra.plugin.scripts.python.Script
    script: |
      print("Hello from Kestra!")
      return {"message": "Hello World"}

  - id: process
    type: io.kestra.plugin.scripts.python.Script
    script: |
      import json
      data = {{ outputs.hello }}
      print(f"Received: {data}")
```

### Ejemplo 2: Workflow con HTTP Request

```yaml
id: fetch-and-process
namespace: company
description: Obtener datos de API y procesarlos

tasks:
  - id: fetch-data
    type: io.kestra.plugin.fs.http.Download
    uri: https://api.example.com/data
    outputFile: /tmp/data.json

  - id: process-data
    type: io.kestra.plugin.scripts.python.Script
    script: |
      import json
      with open('/tmp/data.json') as f:
          data = json.load(f)
      
      # Procesar datos
      processed = [item for item in data if item['status'] == 'active']
      
      with open('/tmp/processed.json', 'w') as f:
          json.dump(processed, f)

  - id: load-to-db
    type: io.kestra.plugin.jdbc.postgresql.CopyIn
    connectionString: "jdbc:postgresql://db:5432/mydb"
    from: /tmp/processed.json
    table: processed_data

triggers:
  - id: schedule
    type: io.kestra.core.models.triggers.types.Schedule
    cron: "0 8 * * *"  # Diario a las 8 AM
```

### Ejemplo 3: Workflow con Paralelismo

```yaml
id: parallel-processing
namespace: company
description: Procesamiento paralelo de múltiples fuentes

tasks:
  - id: parallel-extract
    type: io.kestra.core.tasks.flows.Parallel
    tasks:
      - id: extract-source-1
        type: io.kestra.plugin.fs.http.Download
        uri: https://api.example.com/source1
        outputFile: /tmp/source1.json
      
      - id: extract-source-2
        type: io.kestra.plugin.fs.http.Download
        uri: https://api.example.com/source2
        outputFile: /tmp/source2.json
      
      - id: extract-source-3
        type: io.kestra.plugin.fs.http.Download
        uri: https://api.example.com/source3
        outputFile: /tmp/source3.json

  - id: merge-data
    type: io.kestra.plugin.scripts.python.Script
    script: |
      import json
      import glob
      
      all_data = []
      for file in glob.glob('/tmp/source*.json'):
          with open(file) as f:
              all_data.extend(json.load(f))
      
      with open('/tmp/merged.json', 'w') as f:
          json.dump(all_data, f)
```

---

## 🔗 Ejemplos de Integraciones

### Ejemplo 1: Integración con HubSpot

```python
"""
Integración con HubSpot para sincronizar leads.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task
import requests

@dag(
    dag_id="hubspot_sync",
    description="Sincronizar leads desde HubSpot",
    schedule_interval="@hourly",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["integration", "hubspot"],
)
def hubspot_sync():
    
    @task
    def fetch_hubspot_leads(**context):
        """Obtiene leads de HubSpot."""
        api_key = context["dag_run"].conf.get("hubspot_api_key")
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    @task
    def process_leads(leads_data):
        """Procesa leads obtenidos."""
        # Tu lógica de procesamiento aquí
        return {"processed": len(leads_data.get("results", []))}
    
    leads = fetch_hubspot_leads()
    process_leads(leads)

hubspot_sync()
```

### Ejemplo 2: Integración con S3

```python
"""
Integración con S3 para cargar/descargar archivos.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

@dag(
    dag_id="s3_integration",
    description="Integración con S3",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["integration", "s3"],
)
def s3_integration():
    
    @task
    def upload_to_s3():
        """Sube archivo a S3."""
        s3_hook = S3Hook(aws_conn_id="aws_default")
        s3_hook.load_file(
            filename="/tmp/data.csv",
            key="data/processed/data.csv",
            bucket_name="my-bucket",
            replace=True
        )
        return {"status": "uploaded"}
    
    @task
    def download_from_s3():
        """Descarga archivo de S3."""
        s3_hook = S3Hook(aws_conn_id="aws_default")
        s3_hook.download_file(
            key="data/raw/input.csv",
            bucket_name="my-bucket",
            local_path="/tmp/input.csv"
        )
        return {"status": "downloaded"}
    
    upload_to_s3()
    download_from_s3()

s3_integration()
```

---

## 📊 Ejemplos de Monitoreo

### Ejemplo 1: Métricas Personalizadas

```python
"""
Enviar métricas personalizadas a Prometheus.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task
from prometheus_client import Counter, Histogram, push_to_gateway

# Definir métricas
PROCESSED_RECORDS = Counter('processed_records_total', 'Total records processed')
PROCESSING_TIME = Histogram('processing_time_seconds', 'Processing time')

@dag(
    dag_id="metrics_example",
    description="Ejemplo de métricas personalizadas",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["monitoring", "metrics"],
)
def metrics_example():
    
    @task
    def process_with_metrics():
        """Procesa datos y registra métricas."""
        import time
        
        start_time = time.time()
        
        # Simular procesamiento
        records_processed = 100
        time.sleep(1)
        
        processing_time = time.time() - start_time
        
        # Registrar métricas
        PROCESSED_RECORDS.inc(records_processed)
        PROCESSING_TIME.observe(processing_time)
        
        # Enviar a Pushgateway
        push_to_gateway(
            gateway='prometheus-pushgateway:9091',
            job='airflow_dag',
            registry=None
        )
        
        return {"records": records_processed, "time": processing_time}
    
    process_with_metrics()

metrics_example()
```

### Ejemplo 2: Alertas Personalizadas

```python
"""
Configurar alertas personalizadas.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.etl_notifications import notify_slack

@dag(
    dag_id="alerts_example",
    description="Ejemplo de alertas personalizadas",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    default_args={
        "on_failure_callback": lambda context: notify_slack(
            context,
            message=f"❌ DAG {context['dag'].dag_id} falló en tarea {context['task_instance'].task_id}"
        ),
        "on_success_callback": lambda context: notify_slack(
            context,
            message=f"✅ DAG {context['dag'].dag_id} completó exitosamente"
        ),
    },
    tags=["monitoring", "alerts"],
)
def alerts_example():
    
    @task
    def check_threshold(value):
        """Verifica si un valor excede un umbral."""
        threshold = 1000
        if value > threshold:
            notify_slack(
                context=None,
                message=f"⚠️ Valor {value} excede umbral {threshold}"
            )
        return {"value": value, "threshold_exceeded": value > threshold}
    
    check_threshold(1500)

alerts_example()
```

---

## 🎬 Casos de Uso Completos

### Caso de Uso 1: Pipeline de Onboarding de Clientes

```python
"""
Pipeline completo de onboarding de clientes.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task, task_group
from airflow.providers.postgres.hooks.postgres import PostgresHook
from data.airflow.plugins.etl_notifications import notify_slack

@dag(
    dag_id="customer_onboarding",
    description="Pipeline completo de onboarding",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["onboarding", "customer"],
)
def customer_onboarding():
    
    @task_group(group_id="validation")
    def validation_group():
        """Validación de datos de cliente."""
        
        @task
        def validate_email():
            return {"email_valid": True}
        
        @task
        def validate_phone():
            return {"phone_valid": True}
        
        return [validate_email(), validate_phone()]
    
    @task_group(group_id="processing")
    def processing_group(validation_results):
        """Procesamiento de datos."""
        
        @task
        def create_account():
            return {"account_id": "acc_123"}
        
        @task
        def send_welcome_email(account_id):
            return {"email_sent": True}
        
        account = create_account()
        return send_welcome_email(account)
    
    @task
    def finalize(processing_result):
        """Finaliza el proceso."""
        notify_slack(
            context=None,
            message="✅ Onboarding completado exitosamente"
        )
        return {"status": "completed"}
    
    # Flujo
    validated = validation_group()
    processed = processing_group(validated)
    finalize(processed)

customer_onboarding()
```

### Caso de Uso 2: ETL de Ventas con Reportes

```python
"""
ETL de ventas con generación de reportes.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd

@dag(
    dag_id="sales_etl_reporting",
    description="ETL de ventas con reportes",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["etl", "sales", "reporting"],
)
def sales_etl_reporting():
    
    @task
    def extract_sales_data():
        """Extrae datos de ventas."""
        pg_hook = PostgresHook(postgres_conn_id="sales_db")
        sql = """
            SELECT 
                date,
                product_id,
                quantity,
                revenue
            FROM sales
            WHERE date >= CURRENT_DATE - INTERVAL '1 day'
        """
        df = pd.read_sql(sql, pg_hook.get_conn())
        return df.to_dict('records')
    
    @task
    def transform_sales_data(sales_data):
        """Transforma datos de ventas."""
        df = pd.DataFrame(sales_data)
        
        # Agregaciones
        daily_summary = df.groupby('date').agg({
            'quantity': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        return daily_summary.to_dict('records')
    
    @task
    def load_to_warehouse(transformed_data):
        """Carga a data warehouse."""
        pg_hook = PostgresHook(postgres_conn_id="warehouse_db")
        conn = pg_hook.get_conn()
        
        df = pd.DataFrame(transformed_data)
        df.to_sql('sales_daily_summary', conn, if_exists='append', index=False)
        
        return {"loaded": len(transformed_data)}
    
    @task
    def generate_report(load_result):
        """Genera reporte."""
        # Generar reporte HTML, PDF, etc.
        return {"report_generated": True}
    
    # Flujo
    sales_data = extract_sales_data()
    transformed = transform_sales_data(sales_data)
    loaded = load_to_warehouse(transformed)
    generate_report(loaded)

sales_etl_reporting()
```

---

## 📚 Referencias

- [`docs/DESARROLLO.md`](./DESARROLLO.md) - Guía de desarrollo
- [`docs/ARQUITECTURA.md`](./ARQUITECTURA.md) - Arquitectura del sistema
- [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) - Guía ETL completa

---

**Versión**: 1.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

