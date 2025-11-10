# 🔧 Guía de Operación y Mantenimiento

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Guía completa para operar y mantener la plataforma en producción.

## 📋 Tabla de Contenidos

- [Monitoreo](#-monitoreo)
- [Alertas](#-alertas)
- [Mantenimiento Rutinario](#-mantenimiento-rutinario)
- [Backup y Recuperación](#-backup-y-recuperación)
- [Escalamiento](#-escalamiento)
- [Actualizaciones](#-actualizaciones)
- [Incident Management](#-incident-management)
- [Performance Tuning](#-performance-tuning)
- [Health Checks](#-health-checks)

---

## 📊 Monitoreo

### Dashboards Principales

#### Grafana

Acceder a Grafana:
```bash
# Port-forward
kubectl port-forward -n observability service/prometheus-grafana 3000:80

# Acceder en navegador
http://localhost:3000
# Usuario: admin / Contraseña: (ver secret)
```

**Dashboards clave**:
- **Sistema**: CPU, memoria, disco, red
- **Kubernetes**: Pods, nodes, recursos
- **Aplicación**: Request rate, latency, errors
- **KPIs**: Métricas de negocio en tiempo real
- **Airflow**: Estado de DAGs y tareas

#### Prometheus

Acceder a Prometheus:
```bash
kubectl port-forward -n observability service/prometheus 9090:9090
```

**Queries útiles**:
```promql
# Rate de requests
rate(http_requests_total[5m])

# Latencia p95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# CPU usage
100 - (avg(rate(container_cpu_usage_seconds_total[5m])) * 100)
```

### Logs

#### Loki

Acceder a logs:
```bash
# Ver logs de un pod
kubectl logs -f <pod-name> -n <namespace>

# Ver logs de todos los pods de un deployment
kubectl logs -f -l app=<app-name> -n <namespace>

# Ver logs con filtro
kubectl logs -f <pod-name> -n <namespace> | grep ERROR
```

#### Logs de Airflow

```bash
# Ver logs de un DAG run
airflow dags show <dag-id>

# Ver logs de una tarea
airflow tasks logs <dag-id> <task-id> <execution-date>

# Ver logs en Kubernetes
kubectl logs -f -n airflow <airflow-worker-pod> | grep <dag-id>
```

---

## 🚨 Alertas

### Configuración de Alertas

Las alertas están configuradas en `observability/prometheus/alertrules.yaml`.

**Alertas principales**:
- **Alto uso de CPU**: > 80% por más de 5 minutos
- **Alto uso de memoria**: > 85% por más de 5 minutos
- **Errores altos**: > 5% de error rate por más de 5 minutos
- **Latencia alta**: p95 > 1 segundo por más de 10 minutos
- **DAGs fallidos**: DAGs con estado FAILED

### Canales de Notificación

- **Slack**: `#alerts-platform` channel
- **Email**: `platform-alerts@company.com`
- **PagerDuty**: Para incidentes críticos (P1/P2)

### Responder a Alertas

1. **Identificar**: Verificar qué componente está alertando
2. **Investigar**: Revisar logs y métricas
3. **Mitigar**: Aplicar solución temporal si es necesario
4. **Resolver**: Implementar solución permanente
5. **Documentar**: Registrar en runbook

---

## 🔄 Mantenimiento Rutinario

### Tareas Diarias

```bash
# Verificar estado de pods
kubectl get pods -A | grep -v Running

# Verificar DAGs fallidos
airflow dags list-import-errors

# Verificar espacio en disco
kubectl top nodes

# Verificar alertas activas
# Acceder a Prometheus Alertmanager
```

### Tareas Semanales

```bash
# Revisar logs de errores
kubectl logs -n airflow --since=7d | grep ERROR | wc -l

# Revisar performance de queries lentas
# Verificar en PostgreSQL: pg_stat_statements

# Limpiar logs antiguos
# Verificar retención en Loki

# Revisar costos
# Verificar en cloud provider dashboard
```

### Tareas Mensuales

- **Actualización de dependencias**: Revisar y actualizar
- **Review de seguridad**: Revisar vulnerabilidades
- **Optimización**: Analizar performance y optimizar
- **Backup verification**: Verificar que los backups funcionan
- **Capacity planning**: Revisar uso y planear escalamiento

---

## 💾 Backup y Recuperación

### Backup de Base de Datos

#### PostgreSQL

```bash
# Backup manual
pg_dump -h <host> -U <user> -d <database> > backup_$(date +%Y%m%d).sql

# Restore
psql -h <host> -U <user> -d <database> < backup_20240101.sql
```

#### Backup Automático

Los backups están configurados con Velero:
- **Ubicación**: `backup/velero/values.yaml`
- **Frecuencia**: Diario a las 2 AM UTC
- **Retención**: 30 días

```bash
# Verificar backups
velero backup get

# Crear backup manual
velero backup create backup-manual --include-namespaces airflow,data

# Restore
velero restore create restore-from-backup --from-backup backup-manual
```

### Backup de Configuraciones

```bash
# Backup de secrets
kubectl get secrets -A -o yaml > secrets_backup_$(date +%Y%m%d).yaml

# Backup de configmaps
kubectl get configmaps -A -o yaml > configmaps_backup_$(date +%Y%m%d).yaml
```

### Disaster Recovery

**Plan de recuperación**:
1. Identificar componentes afectados
2. Restaurar desde backup más reciente
3. Verificar integridad de datos
4. Re-activar servicios
5. Monitorear para asegurar estabilidad

---

## 📈 Escalamiento

### Escalamiento Manual

#### Horizontal (Pods)

```bash
# Escalar deployment
kubectl scale deployment <deployment-name> --replicas=5 -n <namespace>

# Escalar StatefulSet
kubectl scale statefulset <statefulset-name> --replicas=3 -n <namespace>
```

#### Vertical (Recursos)

```bash
# Editar deployment
kubectl edit deployment <deployment-name> -n <namespace>

# Modificar resources:
# resources:
#   requests:
#     memory: "2Gi"
#     cpu: "1000m"
#   limits:
#     memory: "4Gi"
#     cpu: "2000m"
```

### Auto-scaling (HPA)

Los HPA están configurados en `kubernetes/workers/`.

```bash
# Ver HPA
kubectl get hpa -n <namespace>

# Ver detalles
kubectl describe hpa <hpa-name> -n <namespace>
```

### Escalamiento de Base de Datos

#### PostgreSQL

```bash
# Escalar read replicas
# Editar configuración en Terraform o Helm

# Vertical scaling
# Cambiar instance type en cloud provider
```

Ver [`docs/ESCALABILIDAD.md`](./ESCALABILIDAD.md) para más detalles.

---

## 🔄 Actualizaciones

### Actualización de Aplicaciones

#### Airflow

```bash
# 1. Backup
velero backup create airflow-backup-$(date +%Y%m%d)

# 2. Actualizar Helm chart
helm upgrade airflow apache-airflow/airflow \
  --namespace airflow \
  --values data/airflow/values.yaml \
  --version <new-version>

# 3. Verificar
kubectl get pods -n airflow
airflow version
```

#### Kubernetes

```bash
# Actualizar cluster (EKS)
aws eks update-cluster-version --name <cluster-name> --kubernetes-version <version>

# Actualizar node groups
aws eks update-nodegroup-version --cluster-name <cluster-name> --nodegroup-name <nodegroup-name>
```

### Actualización de Dependencias

```bash
# Python
pip install --upgrade -r requirements.txt

# Verificar vulnerabilidades
pip-audit

# Actualizar imágenes Docker
docker pull <image>:<new-tag>
```

### Rollback

```bash
# Rollback de Helm release
helm rollback <release-name> <revision> -n <namespace>

# Rollback de deployment
kubectl rollout undo deployment/<deployment-name> -n <namespace>

# Ver historial
kubectl rollout history deployment/<deployment-name> -n <namespace>
```

---

## 🚑 Incident Management

### Clasificación de Incidentes

- **P1 - Crítico**: Sistema completamente caído
- **P2 - Alto**: Funcionalidad principal afectada
- **P3 - Medio**: Funcionalidad secundaria afectada
- **P4 - Bajo**: Impacto mínimo

### Proceso de Resolución

1. **Detectar**: Alertas, monitoreo, reportes
2. **Evaluar**: Clasificar severidad
3. **Comunicar**: Notificar stakeholders
4. **Investigar**: Identificar root cause
5. **Mitigar**: Aplicar solución temporal
6. **Resolver**: Implementar solución permanente
7. **Post-mortem**: Documentar y aprender

### Comandos Útiles Durante Incidentes

```bash
# Ver estado completo
kubectl get all -A

# Ver eventos recientes
kubectl get events -A --sort-by='.lastTimestamp' | tail -20

# Ver logs de errores
kubectl logs -n <namespace> --since=10m | grep -i error

# Reiniciar pod problemático
kubectl delete pod <pod-name> -n <namespace>

# Escalar para manejar carga
kubectl scale deployment <deployment> --replicas=10 -n <namespace>
```

---

## ⚡ Performance Tuning

### Optimización de Base de Datos

#### PostgreSQL

```sql
-- Ver queries lentas
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Analizar tabla
ANALYZE tabla;

-- Vacuum
VACUUM ANALYZE tabla;

-- Reindex
REINDEX TABLE tabla;
```

#### Índices

```sql
-- Crear índice
CREATE INDEX idx_tabla_fecha ON tabla(fecha);

-- Ver índices no usados
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

### Optimización de Aplicaciones

#### Airflow

```python
# Configurar parallelism
[core]
parallelism = 32
dag_concurrency = 16
max_active_runs_per_dag = 2

# Optimizar pool
[celery]
worker_concurrency = 16
```

#### Kubernetes

```yaml
# Resource requests/limits apropiados
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Caching

```python
# Usar Redis para cache
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.set('key', 'value', ex=3600)  # TTL 1 hora
value = r.get('key')
```

---

## 🏥 Health Checks

### Health Checks Automáticos

Los health checks están configurados en los deployments:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Health Checks Manuales

#### Verificar Salud del Cluster

```bash
# Nodes
kubectl get nodes

# Pods
kubectl get pods -A | grep -v Running

# Services
kubectl get svc -A
```

#### Verificar Salud de Base de Datos

```bash
# PostgreSQL
psql -h <host> -U <user> -d <database> -c "SELECT 1"

# Verificar conexiones
psql -h <host> -U <user> -d <database> -c "SELECT count(*) FROM pg_stat_activity;"
```

#### Scripts de Health Check

```bash
# Ejecutar health check script
./scripts/health-check.sh

# Health check de Airflow
python scripts/airflow_health_check.py
```

---

## 📚 Runbooks

### Runbook: DAG Fallido

1. Identificar DAG fallido en Airflow UI
2. Revisar logs de la tarea fallida
3. Identificar causa raíz
4. Si es temporal: Retry manual
5. Si es permanente: Corregir código y redeploy
6. Monitorear siguiente ejecución

### Runbook: Base de Datos Lenta

1. Verificar métricas de CPU/memoria
2. Identificar queries lentas
3. Verificar locks
4. Si es query: Optimizar o crear índice
5. Si es locks: Identificar y resolver
6. Si es recursos: Escalar base de datos

### Runbook: Pod en CrashLoopBackOff

1. Ver logs del pod
2. Identificar error en logs
3. Verificar configuración (secrets, configmaps)
4. Verificar recursos (CPU/memoria)
5. Corregir problema y reiniciar
6. Monitorear para asegurar estabilidad

---

## 📖 Recursos Adicionales

- [Kubernetes Operations](https://kubernetes.io/docs/tasks/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/current/admin.html)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Airflow Operations Guide](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/index.html)

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

