# Airflow - Operación y Notificaciones

## Variables y notificaciones

- Slack
  - `ENABLE_SLACK`: "true"/"false" (default: true)
  - `SLACK_WEBHOOK_URL`: Webhook entrante
- Email
  - `ENABLE_EMAIL`: "true"/"false" (default: false)
  - `ALERT_EMAILS`: lista separada por comas
- Operación ETL
  - `ETL_POOL`: nombre del pool usado por tareas (default: `etl_pool`)
  - `MAX_ACTIVE_TASKS`: límite de tareas activas del DAG (default: 32)

Estos valores se inyectan vía Helm en `values.yaml` (`workers.env`). Los secretos se montan con External Secret `airflow-secrets` (ver `security/secrets/externalsecrets-airflow-notify.yaml`).

## Pool de ETL

- Pool: `etl_pool` (configurado en `values.yaml`)
- Ajuste `slots` según capacidad de workers.

## DAG de ejemplo: `etl_example`

- Trigger por dataset: `dataset://source_ready`
- Params (con schema):
  - `rows` (int, 1..10e6)
  - `run_name` (string)
  - `chunk_rows` (int, opcional)

### Ejecutar con parámetros (UI o CLI)

UI: Trigger DAG y establezca params JSON, por ejemplo:
```json
{
  "rows": 500000,
  "run_name": "ad_hoc_run",
  "chunk_rows": 100000
}
```

CLI (ejemplo):
```bash
airflow dags trigger etl_example \
  --conf '{"rows": 500000, "run_name": "ad_hoc_run", "chunk_rows": 100000}'
```

## Desarrollo local (variables rápidas)

```bash
export ENABLE_SLACK=true
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export ENABLE_EMAIL=false
export ALERT_EMAILS="ops@example.com, data@example.com"
export ETL_POOL=etl_pool
export MAX_ACTIVE_TASKS=32
```

Reinicie los workers/webserver para aplicar cambios.
