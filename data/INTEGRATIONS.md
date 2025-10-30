# Integraciones de Analítica

Este documento describe cómo integrar Databricks y Snowflake con los componentes de datos/ML de la plataforma (Airflow, Data Lake y MLflow/KServe).

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

## Buenas prácticas

- Versionado como código: conserve operadores/consultas en el repo y parametrice vía `environments/*.yaml`.
- Reutilización de credenciales: use External Secrets y evite duplicación de secretos por equipo.
- Observabilidad: registre métricas de pipelines en Prometheus y logs en ELK; considere OpenTelemetry.
- Seguridad: aplique NetworkPolicies mínimas necesarias; valide con Gatekeeper antes de producción.
