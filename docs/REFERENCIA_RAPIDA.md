# 📖 Referencia Rápida

> **Versión**: 1.0 | **Última actualización**: 2024

Referencia rápida de comandos, APIs y configuraciones comunes.

## 📋 Tabla de Contenidos

- [Comandos de Airflow](#-comandos-de-airflow)
- [Comandos de Kubernetes](#-comandos-de-kubernetes)
- [Comandos de Base de Datos](#-comandos-de-base-de-datos)
- [Variables de Entorno](#-variables-de-entorno)
- [APIs y Endpoints](#-apis-y-endpoints)
- [Plugins Disponibles](#-plugins-disponibles)

---

## ✈️ Comandos de Airflow

### DAGs

```bash
# Listar DAGs
airflow dags list

# Ver detalles de un DAG
airflow dags show <dag-id>

# Ver estado de un DAG
airflow dags state <dag-id> <execution-date>

# Pausar DAG
airflow dags pause <dag-id>

# Despausar DAG
airflow dags unpause <dag-id>

# Trigger DAG
airflow dags trigger <dag-id>

# Trigger con configuración
airflow dags trigger <dag-id> --conf '{"key": "value"}'

# Ver import errors
airflow dags list-import-errors
```

### Tareas

```bash
# Ver estado de tarea
airflow tasks state <dag-id> <task-id> <execution-date>

# Ejecutar tarea
airflow tasks test <dag-id> <task-id> <execution-date>

# Ver logs de tarea
airflow tasks logs <dag-id> <task-id> <execution-date>

# Limpiar tarea
airflow tasks clear <dag-id> --task-regex <task-pattern>
```

### Conexiones

```bash
# Listar conexiones
airflow connections list

# Agregar conexión
airflow connections add <conn-id> \
  --conn-type <type> \
  --conn-host <host> \
  --conn-login <user> \
  --conn-password <password>

# Eliminar conexión
airflow connections delete <conn-id>
```

### Variables

```bash
# Listar variables
airflow variables list

# Obtener variable
airflow variables get <key>

# Establecer variable
airflow variables set <key> <value>

# Eliminar variable
airflow variables delete <key>
```

---

## ☸️ Comandos de Kubernetes

### Pods

```bash
# Listar pods
kubectl get pods -n <namespace>

# Ver detalles de pod
kubectl describe pod <pod-name> -n <namespace>

# Ver logs de pod
kubectl logs <pod-name> -n <namespace>

# Ver logs con seguimiento
kubectl logs -f <pod-name> -n <namespace>

# Ejecutar shell en pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Eliminar pod
kubectl delete pod <pod-name> -n <namespace>
```

### Deployments

```bash
# Listar deployments
kubectl get deployments -n <namespace>

# Ver detalles
kubectl describe deployment <deployment-name> -n <namespace>

# Escalar deployment
kubectl scale deployment <deployment-name> --replicas=5 -n <namespace>

# Ver historial de rollout
kubectl rollout history deployment/<deployment-name> -n <namespace>

# Rollback
kubectl rollout undo deployment/<deployment-name> -n <namespace>
```

### Services

```bash
# Listar services
kubectl get svc -n <namespace>

# Port-forward
kubectl port-forward -n <namespace> service/<service-name> <local-port>:<service-port>

# Ver endpoints
kubectl get endpoints -n <namespace>
```

### ConfigMaps y Secrets

```bash
# Listar configmaps
kubectl get configmaps -n <namespace>

# Ver configmap
kubectl get configmap <name> -n <namespace> -o yaml

# Crear configmap desde archivo
kubectl create configmap <name> --from-file=<file> -n <namespace>

# Listar secrets
kubectl get secrets -n <namespace>

# Ver secret (decodificado)
kubectl get secret <name> -n <namespace> -o jsonpath='{.data.<key>}' | base64 -d
```

### Eventos y Debugging

```bash
# Ver eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Ver recursos de pods
kubectl top pods -n <namespace>

# Ver recursos de nodes
kubectl top nodes

# Ver todos los recursos
kubectl get all -n <namespace>
```

---

## 🗄️ Comandos de Base de Datos

### PostgreSQL

```bash
# Conectar a PostgreSQL
psql -h <host> -U <user> -d <database>

# Backup
pg_dump -h <host> -U <user> -d <database> > backup.sql

# Restore
psql -h <host> -U <user> -d <database> < backup.sql

# Ver tamaño de base de datos
psql -h <host> -U <user> -d <database> -c "SELECT pg_size_pretty(pg_database_size('database_name'));"

# Ver conexiones activas
psql -h <host> -U <user> -d <database> -c "SELECT count(*) FROM pg_stat_activity;"

# Ver queries lentas
psql -h <host> -U <user> -d <database> -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Vacuum
psql -h <host> -U <user> -d <database> -c "VACUUM ANALYZE tabla;"

# Reindex
psql -h <host> -U <user> -d <database> -c "REINDEX TABLE tabla;"
```

---

## 🔧 Variables de Entorno

### Airflow

```bash
# Connection ID para approvals
APPROVALS_DB_CONN_ID=approvals_db

# Directorio de reportes
APPROVAL_CLEANUP_REPORT_DIR=/tmp/approval_cleanup_reports
```

### Approval Cleanup

```bash
# Retención
APPROVAL_CLEANUP_RETENTION_YEARS=2
APPROVAL_CLEANUP_NOTIFICATION_RETENTION_MONTHS=12

# Procesamiento
APPROVAL_CLEANUP_BATCH_SIZE=1000
APPROVAL_CLEANUP_MAX_WORKERS=4

# Features
APPROVAL_CLEANUP_ANALYTICS_ENABLED=true
APPROVAL_CLEANUP_PROMETHEUS_ENABLED=true
APPROVAL_CLEANUP_S3_EXPORT_ENABLED=false
```

### Kubernetes

```bash
# Namespace
NAMESPACE=airflow

# Cluster
KUBECONFIG=~/.kube/config
```

---

## 🌐 APIs y Endpoints

### Airflow API

```bash
# Health check
curl http://localhost:8080/health

# Listar DAGs
curl -X GET "http://localhost:8080/api/v1/dags" \
  -H "Authorization: Basic <base64(user:pass)>"

# Trigger DAG
curl -X POST "http://localhost:8080/api/v1/dags/<dag-id>/dagRuns" \
  -H "Authorization: Basic <base64(user:pass)>" \
  -H "Content-Type: application/json" \
  -d '{"conf": {"key": "value"}}'
```

### Prometheus API

```bash
# Query
curl 'http://localhost:9090/api/v1/query?query=up'

# Range query
curl 'http://localhost:9090/api/v1/query_range?query=up&start=2024-01-01T00:00:00Z&end=2024-01-01T23:59:59Z&step=1h'
```

### Grafana API

```bash
# Listar dashboards
curl -X GET "http://localhost:3000/api/dashboards/home" \
  -H "Authorization: Bearer <token>"

# Obtener dashboard
curl -X GET "http://localhost:3000/api/dashboards/uid/<uid>" \
  -H "Authorization: Bearer <token>"
```

---

## 🔌 Plugins Disponibles

### Approval Cleanup Plugins

```python
# Configuración
from data.airflow.plugins.approval_cleanup_config import get_config
config = get_config()

# Operaciones
from data.airflow.plugins.approval_cleanup_ops import (
    get_pg_hook,
    execute_query_with_timeout,
    process_batch,
)

# Queries
from data.airflow.plugins.approval_cleanup_queries import (
    get_old_requests_to_archive,
    archive_requests_batch,
    get_expired_notifications,
    delete_notifications_batch,
)

# Analytics
from data.airflow.plugins.approval_cleanup_analytics import (
    detect_anomaly,
    calculate_percentiles,
    analyze_trends,
)

# Utilidades
from data.airflow.plugins.approval_cleanup_utils import (
    log_with_context,
    validate_params,
    export_to_multiple_formats,
)
```

### ETL Plugins

```python
# Callbacks
from data.airflow.plugins.etl_callbacks import (
    on_task_failure,
    sla_miss_callback,
)

# Notificaciones
from data.airflow.plugins.etl_notifications import notify_slack

# Configuración
from data.airflow.plugins.etl_config_constants import (
    DEFAULT_RETRIES,
    DEFAULT_RETRY_DELAY,
)

# Utilidades
from data.airflow.plugins.etl_utils import (
    validate_data,
    transform_data,
)
```

---

## 📊 URLs Comunes

### Desarrollo Local

```bash
# Airflow UI
http://localhost:8080

# Grafana
http://localhost:3000

# Prometheus
http://localhost:9090

# Kestra
http://localhost:8080
```

### Producción (ejemplos)

```bash
# Airflow
https://airflow.example.com

# Grafana
https://grafana.example.com

# Prometheus
https://prometheus.example.com

# Kestra
https://kestra.example.com
```

---

## 🔑 Conexiones Comunes

### PostgreSQL

```python
# Connection ID: postgres_default
# Tipo: postgres
# Host: localhost (dev) / <host> (prod)
# Port: 5432
# Schema: <database_name>
```

### AWS S3

```python
# Connection ID: aws_default
# Tipo: aws
# Extra: {"region_name": "us-east-1"}
```

### Slack

```python
# Connection ID: slack_default
# Tipo: http
# Host: https://hooks.slack.com
# Extra: {"webhook_token": "<token>"}
```

---

## 📚 Referencias Rápidas

### Documentación

- [`docs/QUICK_START.md`](./QUICK_START.md) - Guía rápida
- [`docs/DESARROLLO.md`](./DESARROLLO.md) - Guía de desarrollo
- [`docs/TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) - Troubleshooting

### Comandos Útiles

```bash
# Ver tamaño de archivo
wc -l <file>

# Buscar en logs
kubectl logs -n <namespace> | grep <pattern>

# Ver última ejecución de DAG
airflow dags list-runs -d <dag-id> --no-backfill

# Port-forward múltiple
kubectl port-forward -n airflow service/airflow-webserver 8080:8080 &
kubectl port-forward -n observability service/prometheus-grafana 3000:80 &
```

---

**Versión**: 1.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

