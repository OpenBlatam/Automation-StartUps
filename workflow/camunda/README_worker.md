# Zeebe Worker for Employee Onboarding

A lightweight worker that consumes BPMN job types and triggers the Airflow DAG `employee_onboarding`.

## Job Types handled
- `create-accounts`: triggers the Airflow DAG once with process variables.
- `assign-onboarding-tasks`, `send-onboarding-docs`, `track-progress`: acknowledged (no-op) – the DAG manages these steps.

## Env Vars
- `ZEEBE_ADDRESS`: Zeebe gateway address, e.g., `zeebe-gateway:26500` or `x.y.z.cloud.camunda.io:443`.
- `AIRFLOW_BASE_URL`: Airflow base URL, e.g., `https://airflow.example.com`.
- `AIRFLOW_TOKEN`: Bearer token to call Airflow REST API.
- `ONBOARDING_DAG_ID`: Defaults to `employee_onboarding`.

## Run locally
```bash
pip install pyzeebe requests
export ZEEBE_ADDRESS=zeebe-gateway:26500
export AIRFLOW_BASE_URL=https://airflow.example.com
export AIRFLOW_TOKEN=... # optional if not required
python workflow/camunda/worker/zeebe_worker.py
```

## Notes
- In producción, ejecute el worker en Kubernetes como Deployment con un ServiceAccount.
- Endurecer con reintentos, timeouts y logs estructurados; añada métricas/OTel si es necesario.


