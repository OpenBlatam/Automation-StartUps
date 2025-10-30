# Documentación de Plataforma

- Inicio rápido: ver `README.md`
- Infraestructura (IaC): `infra/terraform/` (AWS) y `infra/terraform/azure/` (Azure)
- Kubernetes base: `kubernetes/`
- Integraciones de Analítica: `data/INTEGRATIONS.md`
- MLOps: `ml/` (MLflow, KServe, Kubeflow)
- Workflows/BPM: `workflow/kestra/` y `workflow/flowable/`
- RPA: `rpa/OPENRPA.md`
- Observabilidad: `observability/` (Prometheus/Grafana/ELK, KPIs)
- Seguridad: `security/` (RBAC, Gatekeeper, External Secrets)
- Entornos: `environments/` (dev/stg/prod)

## Growth / Outreach

Nuevo DAG de Airflow: `outreach_multichannel`

Parámetros clave al disparar:
- `leads_csv_url`: URL/ruta CSV con columnas: email, first_name, last_name, company, linkedin_url (opcional)
- `email_webhook_url`: webhook para envío de emails (Zapier/Make/Lemlist/Sendgrid Function)
- `linkedin_webhook_url`: webhook para programar acción de LinkedIn (PhantomBuster/Make)
- `email_from`, `email_subject_template`, `email_body_template`, `linkedin_delay_days`
- `max_parallel_leads`: paralelismo sugerido; controla el ritmo junto al pool `outreach_pool` en Airflow UI
- Follow-up: `followup_delay_days`, `email2_subject_template`, `email2_body_template`
- Operación: `suppression_csv_url`, `business_hours_start_utc`, `business_hours_end_utc`
- Flags: `enable_linkedin` (bool), `enable_followup` (bool), `dry_run` (bool)
- Engagement: `engagement_check_url`, `engagement_timeout_seconds`, `skip_linkedin_if_opened`, `skip_followup_if_replied`

Ejemplo (CLI):

```bash
airflow dags trigger outreach_multichannel \
  --conf '{
    "leads_csv_url": "https://tu-bucket/leads.csv",
    "email_webhook_url": "https://hooks.zapier.com/xxx",
    "linkedin_webhook_url": "https://hook.integromat.com/yyy",
    "email_from": "growth@tu-dominio.com",
    "email_subject_template": "{{first_name}}, idea para {{company}}",
    "email_body_template": "Hola {{first_name}}...",
    "linkedin_delay_days": 2,
    "max_parallel_leads": 16
  }'
```

Notas avanzadas:
- Deduplicación por `email` y normalización a minúsculas; se descartan filas sin `@`.
- Reintentos con backoff (2s, 4s) para webhooks; logs sin exponer PII completa.
- Usa el pool `outreach_pool` para limitar concurrencia efectiva (configurable en Airflow UI).
- Ventana horaria: si está fuera de `business_hours_*`, el email inicial se programa al siguiente inicio de ventana (vía `run_at` en webhook).
- Follow-up email: se encola con `run_at` = ahora + `followup_delay_days`. Asegúrate que tu webhook soporte scheduling.
- Idempotencia: se añade `X-Idempotency-Key` por lead y paso por día para evitar duplicados en webhooks.
- `dry_run=true`: simula respuestas 200 sin ejecutar llamadas externas para pruebas de orquestación.
- Engagement: si configuras `engagement_check_url` (GET ?email=...), el DAG aplica branching: puede omitir LinkedIn si `opened=true` y omitir follow-up si `replied=true` según flags.
