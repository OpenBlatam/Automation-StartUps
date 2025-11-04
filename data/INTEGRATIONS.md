# Integraciones de Analítica

Este documento describe cómo integrar Databricks, Snowflake y Airbyte con los componentes de datos/ML de la plataforma (Airflow, Data Lake y MLflow/KServe).

## Notificaciones de Airflow (Slack/Email)

- Variables de entorno consumidas por `data/airflow/dags` y `plugins`:
  - `ENABLE_SLACK` ("true"/"false"), `SLACK_WEBHOOK_URL`
  - `ENABLE_EMAIL` ("true"/"false"), `ALERT_EMAILS` (lista separada por comas)
- Inyección por Helm values: ver `data/airflow/values.yaml` (`workers.env`)
- Secret (External Secrets): `security/secrets/externalsecrets-airflow-notify.yaml` crea el `Secret` `airflow-secrets` con las claves `slack-webhook-url` y `alert-emails` a partir de AWS Secrets Manager.

## Databricks

- Orquestación (Airflow): use `airflow.providers.databricks.operators.databricks` para jobs/notebooks.
- Credenciales: gestione tokens en Secrets Manager/Key Vault y expóngalos con External Secrets en `data` (ver `security/secrets/externalsecrets-aws.yaml` o `externalsecrets-azure.yaml`).
- Red: permita egress hacia endpoints de Databricks (ajuste NetworkPolicies si aplica) y configure rutas/VPC peering si es necesario.
- Data Lake: monte S3/ADLS como fuente/target para ETL y features.

Ejemplo (Airflow):
```python
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
run_job = DatabricksRunNowOperator(
    task_id="run_dbx_job",
    job_id=12345,
)
```

## Snowflake

- Conectividad (Airflow): `airflow.providers.snowflake.hooks.snowflake` o conexiones `AIRFLOW_CONN_SNOWFLAKE`.
- Cargas: optimice con `COPY INTO` desde el data lake (S3/ADLS) con particiones por fecha.
- Credenciales: almacénelas en Secrets Manager/Key Vault y expóngalas con External Secrets.

Ejemplo (COPY):
```sql
COPY INTO mydb.public.events
FROM 's3://biz-datalake-dev/events/date=2025-10-30/'
CREDENTIALS=(aws_key_id='${AWS_KEY}' aws_secret_key='${AWS_SECRET}')
FILE_FORMAT=(TYPE=JSON);
```

## Airbyte

Airbyte es una plataforma open-source de integración de datos con más de 600 conectores listos para sincronizar datos entre fuentes y destinos (ELT). Se integra perfectamente con Airflow para orquestar sincronizaciones complejas.

### Ventajas

- **600+ conectores**: Fuentes y destinos pre-configurados (Stripe, HubSpot, PostgreSQL, Snowflake, etc.)
- **Open-source**: Sin costos de licencia por conectores
- **Extensible**: Fácil crear conectores personalizados
- **UI intuitiva**: Configuración de conexiones sin código
- **CDC (Change Data Capture)**: Sincronización incremental automática

### Desventajas

- **Enfoque en ELT**: Mejor para extracción/carga que para transformaciones complejas
- **Orquestación limitada**: Requiere Airflow/Temporal para flujos complejos con dependencias

### Despliegue

Airbyte se despliega en Kubernetes usando el Helm chart oficial:

```bash
# Aplicar manifests
kubectl apply -f kubernetes/integration/airbyte.yaml

# Aplicar Ingress
kubectl apply -f kubernetes/ingress/airbyte-ingress.yaml

# Verificar estado
kubectl get pods -n integration -l app=airbyte
```

**Archivos principales**:
- `kubernetes/integration/airbyte.yaml`: Helm chart y configuración
- `kubernetes/ingress/airbyte-ingress.yaml`: Ingress para UI y API
- `observability/servicemonitors/airbyte.yaml`: Métricas Prometheus

### Configuración

1. **Acceder a la UI**: `https://airbyte.example.com` (configurar en `airbyte-ingress.yaml`)
2. **Crear conexiones**: Configurar Sources y Destinations desde la UI
3. **Credenciales**: Gestionar con External Secrets (ver `security/secrets/`)

### Integración con Airflow

Airflow orquesta sincronizaciones de Airbyte usando la API REST:

**Ejemplo (DAG incluido en `data/airflow/dags/airbyte_sync.py`)**:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync

with DAG("airbyte_stripe_to_postgres", ...) as dag:
    sync_task = PythonOperator(
        task_id="sync_stripe",
        python_callable=trigger_airbyte_sync,
        op_kwargs={"connection_id": "abc-123"},
    )
```

**Variables de Airflow requeridas**:
- `AIRBYTE_API_URL`: URL del servidor (ej: `http://airbyte-server.integration.svc.cluster.local:8000`)
- `AIRBYTE_API_USERNAME`: Usuario de Airbyte
- `AIRBYTE_API_PASSWORD`: Password (usar External Secrets)
- `AIRBYTE_*_CONNECTION_ID`: IDs de conexiones específicas

### Casos de Uso

1. **Sincronización periódica**: Stripe → PostgreSQL cada 6 horas
2. **Múltiples fuentes en paralelo**: Stripe, HubSpot, Salesforce simultáneamente
3. **Event-driven**: Trigger sincronización desde webhook o evento
4. **CDC incremental**: Sincronizar solo cambios (PostgreSQL CDC, MongoDB oplog, etc.)

Ver `data/airflow/dags/README_AIRBYTE.md` para ejemplos completos.

### Conectores Comunes

**Top 10 Más Útiles** (ver `kubernetes/integration/AIRBYTE_TOP_CONNECTORS.md`):
1. **PostgreSQL** - Database (Source & Destination)
2. **Stripe** - Payment Processing (Source)
3. **HubSpot** - CRM (Source)
4. **Snowflake** - Data Warehouse (Destination)
5. **Google Sheets** - Spreadsheet (Source)
6. **MySQL** - Database (Source & Destination)
7. **Salesforce** - CRM (Source)
8. **Amazon S3** - Object Storage (Destination)
9. **MongoDB** - NoSQL Database (Source & Destination)
10. **REST API** - Generic API (Source)

**Categorías completas**:
- **Sales/CRM**: Stripe, HubSpot, Salesforce, Zendesk
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Data Warehouses**: Snowflake, BigQuery, Redshift, Databricks
- **Cloud Storage**: S3, GCS, Azure Blob
- **APIs**: REST APIs, Google Sheets, Jira

Lista completa: https://docs.airbyte.com/integrations/

### Buenas Prácticas

- **ELT vs ETL**: Usar Airbyte para EL (Extract/Load), Airflow para Transform
- **Orquestación**: Airflow para flujos complejos, Airbyte para sincronizaciones simples
- **Monitoreo**: Métricas en Prometheus, logs en Loki/ELK
- **Secrets**: External Secrets para credenciales, nunca hardcodeadas
- **Paralelización**: Ejecutar sincronizaciones independientes en paralelo desde Airflow

## Framework de Sincronización Unificada

Framework completo para sincronizar datos entre CRM, ERP, hojas de cálculo y bases de datos.

### Características

- **Sincronización bidireccional**: Sincroniza datos en ambas direcciones entre sistemas
- **Múltiples conectores**: HubSpot, QuickBooks, Google Sheets, PostgreSQL, etc.
- **Validación robusta**: Validación de datos antes y después de sincronización
- **Circuit breaker**: Protección contra fallos en cascada
- **Resolución de conflictos**: Múltiples estrategias (source_wins, target_wins, latest, manual)
- **Auditoría completa**: Tracking completo de todas las sincronizaciones
- **Monitoreo**: Métricas y alertas en tiempo real

### Ubicación

- **Framework**: `data/integrations/`
- **DAG de Airflow**: `data/airflow/dags/data_sync_unified.py`
- **Workflow Kestra**: `workflow/kestra/flows/sheets_sync_unified.yaml`
- **Esquema de BD**: `data/integrations/sync_schema.sql`
- **Documentación**: `data/integrations/README.md`

### Uso Rápido

**Desde Airflow**:
```python
# Trigger DAG data_sync_unified con parámetros:
{
  "source_type": "hubspot",
  "target_type": "quickbooks",
  "direction": "bidirectional",
  "batch_size": 50,
  "dry_run": false
}
```

**Desde Kestra**:
```yaml
# Ejecutar workflow sheets_sync_unified
inputs:
  source_type: "google_sheets"
  target_type: "hubspot"
  direction: "source_to_target"
```

### Conectores Disponibles

- **HubSpot**: Contactos, deals, companies
- **QuickBooks**: Items, customers, invoices
- **Google Sheets**: Lectura y escritura de hojas
- **PostgreSQL/MySQL**: Sincronización con bases de datos

### Configuración de Credenciales

**Variables de entorno requeridas**:
- `HUBSPOT_API_TOKEN`: Token de API de HubSpot
- `QUICKBOOKS_ACCESS_TOKEN`: Access token de QuickBooks
- `QUICKBOOKS_REALM_ID`: Realm ID de QuickBooks
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: JSON de service account de Google
- `GOOGLE_SHEETS_SPREADSHEET_ID`: ID del spreadsheet

Ver `data/integrations/README.md` para documentación completa.

## Buenas prácticas

- Versionado como código: conserve operadores/consultas en el repo y parametrice vía `environments/*.yaml`.
- Reutilización de credenciales: use External Secrets y evite duplicación de secretos por equipo.
- Observabilidad: registre métricas de pipelines en Prometheus y logs en ELK; considere OpenTelemetry.
- Seguridad: aplique NetworkPolicies mínimas necesarias; valide con Gatekeeper antes de producción.
- Sincronización: use el framework unificado (`data/integrations/`) para sincronizaciones entre sistemas en lugar de scripts ad-hoc.
