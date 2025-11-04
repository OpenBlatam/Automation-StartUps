# Integration Services

Esta carpeta contiene servicios de integración y APIs auxiliares que conectan diferentes componentes de la plataforma.

## Estructura

```
integration/
├── healthz.yaml          # Health check endpoint básico
├── healthz-hpa.yaml      # Horizontal Pod Autoscaler para healthz
├── healthz-pdb.yaml      # Pod Disruption Budget para healthz
├── kpis-api.yaml         # API de KPIs
├── airbyte.yaml          # Airbyte - Plataforma de integración de datos (ELT)
└── README_AIRBYTE.md     # Documentación detallada de Airbyte
```

## Servicios

### Healthz

Endpoint básico de health check para validar conectividad del cluster y servicios.

**Archivo**: `healthz.yaml`

**Características**:
- Endpoint `/health` que responde 200 OK
- Liveness y readiness probes
- HPA para auto-escalado
- PDB para alta disponibilidad

**Despliegue**:

```bash
# Aplicar healthz
kubectl apply -f kubernetes/integration/healthz.yaml

# Aplicar HPA
kubectl apply -f kubernetes/integration/healthz-hpa.yaml

# Aplicar PDB
kubectl apply -f kubernetes/integration/healthz-pdb.yaml

# Verificar
kubectl get pods -n integration -l app=healthz
```

**Uso**:

```bash
# Port-forward para pruebas
kubectl port-forward -n integration service/healthz 8080:8080

# Probar endpoint
curl http://localhost:8080/health

# Respuesta:
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

### KPIs API

API REST que expone métricas y KPIs del negocio desde PostgreSQL.

**Archivo**: `kpis-api.yaml`

**Características**:
- Endpoint `/api/kpi/summary` con métricas agregadas
- Dashboard HTML en `/`
- Métricas Prometheus en `/metrics`
- Health check en `/health`

**Documentación completa**: Ver `web/kpis/README.md`

**Despliegue**:

```bash
# Aplicar KPIs API
kubectl apply -f kubernetes/integration/kpis-api.yaml

# Configurar secretos de base de datos
kubectl create secret generic kpis-db-credentials \
  --from-literal=KPIS_PG_HOST=postgres.example.com \
  --from-literal=KPIS_PG_DB=analytics \
  --from-literal=KPIS_PG_USER=analytics \
  --from-literal=KPIS_PG_PASSWORD=password \
  -n integration

# Verificar
kubectl get pods -n integration -l app=kpis-api
```

**Uso**:

```bash
# Port-forward
kubectl port-forward -n integration service/kpis-api 3001:3001

# Obtener KPIs
curl http://localhost:3001/api/kpi/summary

# Ver dashboard
open http://localhost:3001
```

## Integración

### Desde Ingress

Expón los servicios mediante Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: integration-services
  namespace: integration
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: integration-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: healthz
            port:
              number: 80
      - path: /kpis
        pathType: Prefix
        backend:
          service:
            name: kpis-api
            port:
              number: 80
```

### Monitoreo

Configurar ServiceMonitors para Prometheus:

```yaml
# ServiceMonitor para KPIs API (ya existe)
# observability/servicemonitors/kpis-api.yaml

# ServiceMonitor para healthz (crear si necesario)
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: healthz
  namespace: integration
spec:
  selector:
    matchLabels:
      app: healthz
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

## Auto-escalado

### Healthz HPA

El HPA escala healthz basado en CPU y requests:

```yaml
# healthz-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: healthz-hpa
  namespace: integration
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: healthz
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### KPIs API HPA

Similar para KPIs API si se requiere alto throughput.

## Alta Disponibilidad

### Pod Disruption Budget

El PDB garantiza disponibilidad mínima durante mantenimientos:

```yaml
# healthz-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: healthz-pdb
  namespace: integration
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: healthz
```

## Troubleshooting

### Ver logs

```bash
# Logs de healthz
kubectl logs -n integration deployment/healthz

# Logs de KPIs API
kubectl logs -n integration deployment/kpis-api

# Logs de múltiples pods
kubectl logs -n integration -l app=kpis-api --all-containers
```

### Verificar estado

```bash
# Ver pods
kubectl get pods -n integration

# Ver servicios
kubectl get svc -n integration

# Ver HPA
kubectl get hpa -n integration

# Ver PDB
kubectl get pdb -n integration
```

### Debugging

```bash
# Ejecutar shell en pod
kubectl exec -it -n integration deployment/kpis-api -- /bin/sh

# Ver variables de entorno
kubectl exec -n integration deployment/kpis-api -- env

# Probar conectividad interna
kubectl exec -n integration deployment/kpis-api -- \
  curl http://healthz.integration.svc.cluster.local/health
```

### Airbyte

Plataforma open-source de integración de datos con 600+ conectores para sincronizar datos entre fuentes y destinos.

**Archivo**: `airbyte.yaml`

**Características**:
- 600+ conectores pre-configurados (Stripe, HubSpot, PostgreSQL, Snowflake, etc.)
- UI intuitiva para configurar conexiones
- API REST para orquestación programática
- Integración con Airflow para flujos complejos
- Auto-escalado de workers según carga
- Métricas Prometheus integradas

**Despliegue**:

```bash
# Aplicar Airbyte
kubectl apply -f kubernetes/integration/airbyte.yaml

# Aplicar Ingress
kubectl apply -f kubernetes/ingress/airbyte-ingress.yaml

# Verificar
kubectl get pods -n integration -l app=airbyte
```

**Documentación completa**: Ver `README_AIRBYTE.md` y `data/airflow/dags/README_AIRBYTE.md`

**Mejoras recientes**: Ver `IMPROVEMENTS_AIRBYTE.md` para detalles de mejoras implementadas

**Uso**:

```bash
# Acceder a la UI
open https://airbyte.example.com

# Trigger sincronización desde Airflow
# Ver: data/airflow/dags/airbyte_sync.py
```

## Referencias

- **KPIs API**: `web/kpis/README.md`
- **Airbyte**: `README_AIRBYTE.md`
- **Health Checks**: [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- **HPA**: `kubernetes/workers/README.md`

