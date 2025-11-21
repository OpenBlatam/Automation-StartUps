# Observabilidad

Esta carpeta contiene la configuración de la stack de observabilidad de la plataforma: métricas (Prometheus), visualización (Grafana), logging (Loki) y costos (OpenCost).

## Estructura

```
observability/
├── prometheus/           # Prometheus para métricas
│   ├── values.yaml
│   └── alertrules.yaml
├── grafana/              # Grafana para dashboards
│   ├── dashboards/
│   │   ├── api_http.json
│   │   ├── kpi.json
│   │   └── README.md
│   └── datasources/
│       └── postgres.yaml
├── loki/                 # Loki para logging
│   └── values.yaml
├── elastic/              # ELK Stack para logging (alternativa)
│   └── values.yaml
├── opencost/             # Análisis de costos
│   └── values.yaml
└── servicemonitors/       # ServiceMonitors para Prometheus
    ├── healthz.yaml
    └── kpis-api.yaml
```

## Componentes

### Prometheus

Sistema de monitoreo y alertas basado en time-series database.

**Ubicación**: `observability/prometheus/`

**Características**:
- Recolección de métricas de aplicaciones y Kubernetes
- Alertas configurables (Alertmanager)
- ServiceDiscovery automático de pods
- Retención configurable de datos
- Integración con Grafana

**Instalación**:

```bash
# Con Helmfile (recomendado)
helmfile apply

# O manualmente
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace observability \
  --create-namespace \
  -f observability/prometheus/values.yaml
```

**Uso**:

```bash
# Port-forward para acceso local
kubectl port-forward -n observability service/prometheus-operated 9090:9090

# Acceder a UI: http://localhost:9090
```

**Alertas**: Ver `observability/prometheus/alertrules.yaml`

### Grafana

Plataforma de visualización y dashboards.

**Ubicación**: `observability/grafana/`

**Características**:
- Dashboards predefinidos para KPIs y métricas
- Datasources: Prometheus, PostgreSQL, Elasticsearch
- Alertas visuales
- Anotaciones de eventos

**Instalación**:

Grafana se instala como parte del `kube-prometheus-stack`:

```bash
# Acceder a Grafana (credenciales por defecto: admin/admin)
kubectl port-forward -n observability service/prometheus-grafana 3000:80

# UI: http://localhost:3000
```

**Dashboards**:

- `api_http.json`: Métricas HTTP de APIs (requests, latencia, errores)
- `kpi.json`: KPIs de negocio (ingresos, leads, conversión)

**Importar Dashboards**:

```bash
# Desde UI: Configuration → Dashboards → Import
# O con ConfigMap (se importan automáticamente)
kubectl apply -f observability/grafana/dashboards/
```

**Datasources**:

- Prometheus: Automático (parte de kube-prometheus-stack)
- Loki: Automático (parte de loki-stack)
- PostgreSQL: Ver `observability/grafana/datasources/postgres.yaml`

### Loki

Sistema de agregación y consulta de logs, diseñado para trabajar junto con Prometheus y Grafana.

**Ubicación**: `observability/loki/`

**Características**:
- Agregación centralizada de logs de todas las aplicaciones
- Consultas con LogQL (similar a PromQL)
- Integración nativa con Grafana
- Alto rendimiento y bajo costo
- Retención configurable

**Instalación**:

```bash
# Con Helmfile (recomendado)
helmfile apply

# O manualmente
helm install loki grafana/loki-stack \
  --namespace observability \
  --create-namespace \
  -f observability/loki/values.yaml
```

**Componentes**:
- **Loki**: Almacenamiento y procesamiento de logs
- **Promtail**: Recolector de logs (DaemonSet) que envía logs a Loki

**Acceso a Logs**:

Los logs se consultan directamente desde Grafana (Loki está configurado como datasource):

```bash
# Acceder a Grafana
kubectl port-forward -n observability service/prometheus-grafana 3000:80
# UI: http://localhost:3000
# Navegar a: Explore → Seleccionar datasource "Loki"
```

**Query de Logs (LogQL)**:

```logql
# Logs de todos los pods en un namespace
{namespace="data", container="airflow-worker"}

# Filtrar por nivel de log
{namespace="data"} |= "ERROR"

# Logs estructurados JSON
{namespace="data"} | json | status="failed"

# Agregaciones
{namespace="data"} | json | count_over_time(1m)
```

**Configuración de Logs Estructurados**:

Para aprovechar al máximo Loki, usa logs estructurados en JSON:

```python
# Python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)

# Logs con contexto
logger.info("Task processed", extra={
    "task_id": task_id,
    "duration_ms": duration,
    "queue": "etl_pool"
})
```

**Retención**:

Configurar retención en `values.yaml`:
- Por defecto: 30 días
- Para producción: Usar almacenamiento persistente (S3, GCS) y configurar políticas de lifecycle

### Elasticsearch / ELK Stack (Alternativa)

Stack de logging alternativo: Elasticsearch, Logstash, Kibana.

**Nota**: Loki es la solución principal. ELK se mantiene como alternativa si se requiere funcionalidad avanzada de Elasticsearch.

**Ubicación**: `observability/elastic/`

**Características**:
- Agregación centralizada de logs
- Búsqueda y análisis de logs
- Visualización en Kibana
- Retención configurable

**Instalación**:

```bash
helm install elasticsearch elastic/elasticsearch \
  --namespace observability \
  --create-namespace \
  -f observability/elastic/values.yaml

helm install kibana elastic/kibana \
  --namespace observability \
  -f observability/elastic/values.yaml
```

**Recolección de Logs**:

Usa Fluent Bit o Fluentd como DaemonSet:

```bash
# Fluent Bit (recomendado, más ligero)
helm install fluent-bit fluent/fluent-bit \
  --namespace observability
```

**Acceso a Kibana**:

```bash
kubectl port-forward -n observability service/kibana-kibana 5601:5601
# UI: http://localhost:5601
```

### OpenCost

Análisis de costos en tiempo real de recursos de Kubernetes.

**Ubicación**: `observability/opencost/`

**Características**:
- Costos por namespace, pod, servicio
- Integración con AWS/Azure billing
- Exportación a Prometheus
- Dashboard de costos

**Instalación**:

```bash
helm install opencost opencost/opencost \
  --namespace observability \
  --create-namespace \
  -f observability/opencost/values.yaml
```

**Acceso**:

```bash
kubectl port-forward -n observability service/opencost 9003:9003
# UI: http://localhost:9003
```

**Métricas en Prometheus**:

OpenCost expone métricas que puedes visualizar en Grafana.

## ServiceMonitors

Los ServiceMonitors permiten que Prometheus descubra y scrape métricas de servicios.

**Ubicación**: `observability/servicemonitors/`

**Archivos**:
- `healthz.yaml`: ServiceMonitor para el endpoint de health check
- `kpis-api.yaml`: ServiceMonitor para la API de KPIs

**Aplicar**:

```bash
kubectl apply -f observability/servicemonitors/
```

**Ejemplo de ServiceMonitor**:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kpis-api
  namespace: integration
spec:
  selector:
    matchLabels:
      app: kpis-api
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

## Configuración de Alertas

### Prometheus AlertRules

Las reglas de alerta están en `observability/prometheus/alertrules.yaml`:

```yaml
groups:
  - name: platform
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
```

### Alertmanager

Alertmanager envía notificaciones (email, Slack, PagerDuty):

```bash
# Configurar en values.yaml de Prometheus
alertmanager:
  config:
    global:
      slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    route:
      receiver: 'slack-notifications'
```

## Dashboards de Grafana

### Dashboard de KPIs

**Archivo**: `observability/grafana/dashboards/kpi.json`

**Métricas mostradas**:
- Ingresos (última hora, últimas 24h)
- Ingresos por hora (últimas 24h)
- Pagos y leads recientes
- Leads por prioridad (hoy)
- Conversión 7 días (leads → pagos)
- Salud de servicios (tasa 5xx, reinicios)

**Datasource**: PostgreSQL (ver `observability/grafana/datasources/postgres.yaml`)

### Dashboard de APIs HTTP

**Archivo**: `observability/grafana/dashboards/api_http.json`

**Métricas mostradas**:
- Requests por segundo
- Latencia (p50, p95, p99)
- Tasa de errores (4xx, 5xx)
- Throughput

**Datasource**: Prometheus

## Integración con Aplicaciones

### Exportar Métricas desde Apps

Para que Prometheus scrape tus aplicaciones:

1. **Exponer endpoint `/metrics`**:

```python
# Python (Prometheus client)
from prometheus_client import Counter, generate_latest

requests_total = Counter('http_requests_total', 'Total HTTP requests')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

2. **Crear ServiceMonitor**:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: http
      path: /metrics
```

### Enviar Logs a Loki

**Recomendado**: Los logs se recolectan automáticamente por Promtail (DaemonSet) y se envían a Loki. Solo necesitas configurar logs estructurados en tus aplicaciones:

```python
# Python logging estructurado
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

logger.info("Application started", extra={"app": "kpis-api", "version": "1.0.0"})
```

**Cómo funciona**:
1. Tu aplicación escribe logs a stdout/stderr (formato JSON recomendado)
2. Promtail (DaemonSet en cada nodo) recolecta logs de `/var/log/pods/`
3. Promtail enriquece logs con metadatos de Kubernetes (namespace, pod, container, labels)
4. Logs se envían a Loki para almacenamiento y consulta

**Ver logs en Grafana**:
- Navegar a: Explore → Seleccionar datasource "Loki"
- Query: `{namespace="integration", app="kpis-api"}`

### Enviar Logs a Elasticsearch (Alternativa)

Si usas ELK en lugar de Loki, los logs se recolectan por Fluent Bit y se envían a Elasticsearch. Ver sección "Elasticsearch / ELK Stack" arriba.

## Retención de Datos

### Prometheus

Configurar retención en `values.yaml`:

```yaml
prometheus:
  retention: 30d  # Retener 30 días
  retentionSize: 50GB  # O por tamaño
```

Para retención a largo plazo, usa **Thanos** o **Cortex**.

### Elasticsearch

Configurar ILM (Index Lifecycle Management) en Kibana:

1. Políticas de ILM: logs > 30 días → cold, > 90 días → delete
2. Aplicar a índices: `logstash-*`

## Troubleshooting

### Prometheus no scrapea métricas

```bash
# Verificar ServiceMonitor
kubectl get servicemonitor -A

# Ver targets en Prometheus UI
# Status → Targets

# Verificar que el servicio expone /metrics
curl http://service-name.namespace.svc.cluster.local/metrics
```

### Grafana no muestra datos

```bash
# Verificar datasources
kubectl get datasource -n observability

# Verificar conexión a Prometheus
# En Grafana UI: Configuration → Data Sources → Test
```

### Logs no aparecen en Kibana

```bash
# Verificar Fluent Bit
kubectl get pods -n observability -l app=fluent-bit

# Ver logs de Fluent Bit
kubectl logs -n observability -l app=fluent-bit

# Verificar índices en Elasticsearch
curl http://elasticsearch.observability.svc:9200/_cat/indices
```

## Referencias

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)
- [OpenCost Documentation](https://www.opencost.io/docs)

