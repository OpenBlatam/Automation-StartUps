# Employee Onboarding (Airflow + Camunda)

## Overview
This DAG (`employee_onboarding`) automates new-hire onboarding:
- Create accounts (IdP/email/workspace)
- Assign onboarding tasks/tickets
- Send welcome email and documentation
- Track progress and notify (Slack)

Camunda process (`workflow/camunda/onboarding_employee.bpmn`) can trigger this DAG via API for human-in-the-loop steps.

## Configuration
Set these environment variables (Helm `values.yaml` → `workers.env`):
- `ONBOARDING_POOL` (optional, default `etl_pool`)
- `IDP_API_URL` (e.g., `https://idp.example.com/api`)
- `WORKSPACE_API_URL` (e.g., `https://workspace.example.com`)
- `ISSUE_TRACKER_URL` (e.g., `https://jira.example.com`)
- `ISSUE_TRACKER_PROJECT` (e.g., `ONB`)
- `ONBOARDING_DOCS_BASE_URL` (e.g., `https://docs.example.com/onboarding`)
- `ONBOARDING_EMAIL_FROM` (e.g., `hr@example.com`)
- Slack/email notification envs are shared with other DAGs (see `data/INTEGRATIONS.md`).

Store credentials (tokens, SMTP) in your Secret manager and expose to the cluster as `Secret`s (External Secrets recommended).

## Triggering
Manual trigger with params (example):
```json
{
  "employee_email": "ana.romero@example.com",
  "full_name": "Ana Romero",
  "start_date": "2025-11-04",
  "manager_email": "marta.garcia@example.com",
  "department": "Engineering",
  "role": "Data Engineer",
  "location": "Madrid",
  "send_welcome": true,
  "create_issue_tracker_tasks": true,
  "idempotency_key": "ana.romero@example.com:2025-11-04",
  "idempotency_ttl_hours": 24,
  "hris_lookup": true
}
```

## Extending Integrations
Replace stubs in `plugins/onboarding_integrations.py` with real provider calls:
- IdP/Email: Okta/Entra/Google/M365
- Issue tracker: Jira/Linear/Asana
- Email: Airflow `EmailOperator` or external API (SES/SendGrid)
- Persist progress: DB table or metrics (Prometheus)

### Lightweight persistence (default)
El DAG guarda un historial de progreso por empleado usando Airflow Variables con la clave `onboarding_runs:<email>` (lista JSON). Ideal para demo/staging. Para producción, sustituir por DB/Metrics.

## Camunda Notes
Service tasks use Zeebe job types:
- `create-accounts`, `assign-onboarding-tasks`, `send-onboarding-docs`, `track-progress`
Map them to workers that call the Airflow REST API or trigger the DAG directly.

## Quick progress panel (CLI)
Puede consultar el historial guardado en Variables con un CLI simple:

```bash
python scripts/onboarding_runs_cli.py ana.romero@example.com \
  --airflow https://airflow.example.com \
  --token $AIRFLOW_TOKEN
```
Devuelve una lista JSON con eventos de progreso por empleado.
