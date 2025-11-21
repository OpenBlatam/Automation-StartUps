# Arquitectura de Escalabilidad

Esta documentación describe la arquitectura de escalabilidad de la plataforma, incluyendo workers para procesamiento en segundo plano, orquestación con Docker y Kubernetes, y observabilidad completa.

## 📋 Tabla de Contenidos

1. [Workers](#workers)
2. [Infraestructura de Orquestación](#infraestructura-de-orquestación)
3. [Observabilidad](#observabilidad)

---

## Workers

Los workers procesan tareas en segundo plano de forma asíncrona, desacoplando el procesamiento pesado de las aplicaciones principales.

### Tipos de Workers

#### 1. Workers de Python (Celery)

**Uso**: Procesamiento de pipelines de datos, ETL, tareas pesadas.

**Implementación**: Airflow con CeleryExecutor

**Configuración actual** (`data/airflow/values.yaml`):
- Executor: `CeleryExecutor`
- Workers: 2 réplicas (configurable)
- Concurrencia por worker: 16 tareas
- Paralelismo total: 64 tareas

**Ubicación**:
- `data/airflow/docker-compose.yml` - Configuración local
- `data/airflow/values.yaml` - Configuración Kubernetes (Helm)

**Pools de tareas**:
- `etl_pool`: 24 slots para tareas ETL
- `dq_pool`: 8 slots para validación y calidad de datos

#### 2. Workers de Python (Camunda External Tasks)

**Uso**: Procesamiento de tareas BPMN, integración con procesos de negocio.

**Implementación**: Workers Python que consumen tareas externas de Camunda

**Ejemplos**:
- `workflow/camunda/worker/zeebe_worker.py` - Worker para Zeebe (Camunda Cloud)
- `workflow/camunda/worker/python/worker.py` - Worker para Camunda Self-Hosted

**Configuración**:
```python
# Ejemplo de worker
client = ExternalTaskClient(base_url="http://camunda:8080")
client.subscribe("process-order", handle_task)
```

#### 3. Workers de Node.js (Futuro)

**Uso**: Tareas ligeras, webhooks, procesamiento de eventos.

**Arquitectura propuesta**:
- Queue: Redis o RabbitMQ
- Framework: Bull o Agenda.js
- Ejecución: Pods en Kubernetes

**Ejemplo de implementación**:
```javascript
// workers/nodejs/example-worker.js
const Queue = require('bull');
const redis = { host: 'redis', port: 6379 };

const workQueue = new Queue('background-jobs', { redis });

workQueue.process(async (job) => {
  // Procesar tarea
  return { processed: true };
});
```

### Despliegue de Workers en Kubernetes

#### Airflow Celery Workers

Los workers de Airflow se despliegan como un Deployment con auto-escalado:

```yaml
# Ya configurado en data/airflow/values.yaml
workers:
  replicas: 2  # Réplicas iniciales
  # HPA se configura por separado (ver sección HPA)
```

#### Workers personalizados (Camunda, Node.js)

Ejemplo de Deployment para un worker personalizado:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: camunda-worker
  namespace: workflows
spec:
  replicas: 2
  selector:
    matchLabels:
      app: camunda-worker
  template:
    metadata:
      labels:
        app: camunda-worker
    spec:
      containers:
      - name: worker
        image: camunda-worker:latest
        env:
        - name: CAMUNDA_REST_URL
          value: "http://camunda-platform:8080"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

---

## Infraestructura de Orquestación

### Docker + Kubernetes

La plataforma utiliza **Docker** para containerización y **Kubernetes (K8s)** para orquestación y auto-escalado.

### Auto-escalado de Workers

#### Horizontal Pod Autoscaler (HPA)

El auto-escalado se basa en métricas reales de carga (CPU, memoria, métricas personalizadas).

**Ejemplo de HPA para Workers de Airflow**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: airflow-worker-hpa
  namespace: data
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: airflow-worker  # Nombre del deployment de workers
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: celery_queue_length  # Métrica personalizada
        target:
          type: AverageValue
          averageValue: "10"  # Escalar si hay >10 tareas en cola por pod
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Esperar 5 min antes de reducir
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
```

**Ejemplo de HPA para Workers de Camunda**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: camunda-worker-hpa
  namespace: workflows
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: camunda-worker
  minReplicas: 1
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
```

### Métricas Personalizadas para Auto-escalado

Para escalar basado en la longitud de colas de tareas, necesitas exponer métricas personalizadas:

**Para Celery (Airflow)**:

```python
# plugins/celery_metrics.py
from prometheus_client import Gauge
from airflow.executors.celery_executor import CeleryExecutor

queue_length = Gauge('celery_queue_length', 'Number of tasks in queue')

def update_queue_metrics():
    executor = CeleryExecutor()
    queues = executor.queues
    total = sum(len(queue) for queue in queues.values())
    queue_length.set(total)
```

**Exponer métricas en el worker**:

```python
# En el código del worker
from prometheus_client import start_http_server, Counter

tasks_processed = Counter('worker_tasks_processed_total', 'Total processed tasks')

@worker.task
def handle_task(data):
    tasks_processed.inc()
    # ... procesar tarea
```

### Configuración de Recursos

**Requests y Limits recomendados**:

```yaml
resources:
  requests:
    cpu: 200m      # Mínimo garantizado
    memory: 512Mi
  limits:
    cpu: 2000m      # Máximo permitido
    memory: 2Gi     # OOMKilled si excede
```

**Ajustes por tipo de worker**:
- Workers ligeros (webhooks, eventos): `cpu: 100m, memory: 256Mi`
- Workers ETL: `cpu: 500m-2000m, memory: 1Gi-4Gi`
- Workers ML: `cpu: 2000m+, memory: 4Gi+`

---

## Observabilidad

La stack de observabilidad proporciona visibilidad completa sobre qué está pasando, dónde fallan los flujos y por qué.

### Stack: Prometheus + Grafana + Loki

#### Prometheus

**Rol**: Recolección y almacenamiento de métricas.

**Configuración**: `observability/prometheus/values.yaml`

**Características**:
- Métricas de aplicaciones (endpoints `/metrics`)
- Métricas de Kubernetes (kube-state-metrics)
- ServiceMonitors para descubrimiento automático
- Retención: 15 días (configurable)

**Métricas clave para Workers**:
- `celery_queue_length`: Tareas pendientes en cola
- `worker_tasks_processed_total`: Total de tareas procesadas
- `worker_task_duration_seconds`: Duración de tareas
- `worker_task_failures_total`: Tareas fallidas

#### Grafana

**Rol**: Visualización y dashboards.

**Configuración**: Incluido en `kube-prometheus-stack`

**Dashboards existentes**:
- `api_http.json`: Métricas HTTP
- `kpi.json`: KPIs de negocio
- `etl_improved.json`: Métricas ETL

**Dashboards recomendados para Workers**:
- Queue depth over time
- Worker throughput (tasks/sec)
- Task duration percentiles (p50, p95, p99)
- Failure rate
- Worker resource utilization (CPU, memory)

#### Loki

**Rol**: Agregación y consulta de logs.

**Configuración**: `observability/loki/values.yaml`

**Características**:
- Logs de todas las aplicaciones y workers
- Consultas con LogQL (similar a PromQL)
- Integración con Grafana
- Retención configurable

**Configuración de logs estructurados en Workers**:

```python
# Python workers
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)

# Logs estructurados
logger.info("Task processed", extra={
    "task_id": task_id,
    "duration_ms": duration,
    "queue": "etl_pool"
})
```

**Query de logs en Grafana**:

```logql
# Logs de workers de Airflow
{namespace="data", container="airflow-worker"} |= "ERROR"

# Tareas fallidas
{namespace="data"} | json | status="failed"

# Tareas por cola
{namespace="data"} | json | queue="etl_pool" | count_over_time(1m)
```

### Monitoreo de Flujos

#### Identificación de Fallos

**Logs estructurados con contexto**:

```python
logger.error("Task failed", extra={
    "task_id": task.id,
    "dag_id": task.dag_id,
    "execution_date": task.execution_date.isoformat(),
    "error_type": type(e).__name__,
    "error_message": str(e),
    "retry_count": task.retry_count,
    "queue": task.queue
})
```

**Alertas en Prometheus**:

```yaml
# observability/prometheus/alertrules.yaml
- alert: HighWorkerFailureRate
  expr: rate(worker_task_failures_total[5m]) > 0.1
  for: 5m
  annotations:
    summary: "High worker failure rate detected"
    description: "{{ $value }} failures per second in {{ $labels.queue }}"

- alert: WorkerQueueBacklog
  expr: celery_queue_length > 100
  for: 10m
  annotations:
    summary: "Worker queue backlog too high"
    description: "{{ $value }} tasks waiting in queue"
```

#### Métricas de Performance

**Dashboards recomendados**:

1. **Worker Performance**:
   - Throughput (tareas/segundo)
   - Latencia (p50, p95, p99)
   - Utilización de recursos
   - Queue depth

2. **Flujo End-to-End**:
   - Tiempo de ejecución por flujo
   - Tasa de éxito/fallo
   - Retrasos en procesamiento
   - Dependencias entre tareas

3. **Recursos**:
   - CPU/Memoria por worker
   - Costo por namespace (OpenCost)
   - Utilización de pools

### Integración Completa

**Flujo de observabilidad**:

1. **Aplicaciones/Workers** → Exponen métricas en `/metrics` y logs estructurados
2. **Prometheus** → Scrapea métricas cada 30s (configurable)
3. **Loki** → Recolecta logs via Fluent Bit/Fluentd (DaemonSet)
4. **Grafana** → Visualiza métricas y logs en dashboards unificados
5. **Alertmanager** → Envía alertas (Slack, email, PagerDuty)

**Configuración de ServiceMonitor para Workers**:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: airflow-worker
  namespace: data
spec:
  selector:
    matchLabels:
      app: airflow-worker
  endpoints:
  - port: metrics  # Puerto donde el worker expone /metrics
    path: /metrics
    interval: 30s
```

---

## Mejores Prácticas

### Workers

1. **Idempotencia**: Las tareas deben ser idempotentes (poder ejecutarse múltiples veces sin efectos secundarios)
2. **Timeouts**: Configurar timeouts apropiados para evitar tareas colgadas
3. **Retries**: Implementar lógica de reintento con backoff exponencial
4. **Logs estructurados**: Usar JSON logs con contexto relevante
5. **Métricas**: Exponer métricas clave (throughput, latencia, errores)

### Auto-escalado

1. **Métricas reales**: Escalar basado en métricas de negocio (queue depth, throughput) además de CPU/memoria
2. **Ventanas de estabilización**: Configurar `stabilizationWindowSeconds` para evitar oscilaciones
3. **Límites razonables**: `minReplicas` y `maxReplicas` según capacidad y costo
4. **Resource limits**: Definir límites para evitar que un pod consuma todos los recursos

### Observabilidad

1. **Logs estructurados**: Siempre usar JSON logs con campos estándar
2. **Métricas relevantes**: Exponer métricas que realmente importan para el negocio
3. **Alertas accionables**: Configurar alertas solo para situaciones que requieren acción
4. **Dashboards ágiles**: Crear dashboards que muestren métricas clave en un vistazo

---

## Referencias

- [Observabilidad - README](../observability/README.md)
- [Airflow Workers](../data/airflow/values.yaml)
- [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)
- [Loki LogQL](https://grafana.com/docs/loki/latest/logql/)


