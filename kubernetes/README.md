# Kubernetes Manifests

Esta carpeta contiene todos los manifiestos de Kubernetes (YAML) para desplegar componentes de la plataforma en el cluster.

## Estructura

```
kubernetes/
├── namespaces.yaml           # Namespaces base
├── ingress/                  # Configuración de Ingress
│   └── nginx-ingress.yaml
├── integration/             # Servicios de integración
│   ├── healthz.yaml         # Health check endpoint
│   ├── healthz-hpa.yaml     # Horizontal Pod Autoscaler
│   ├── healthz-pdb.yaml     # Pod Disruption Budget
│   └── kpis-api.yaml        # API de KPIs
├── kafka/                   # Configuración de Kafka
│   ├── strimzi-kafka.yaml   # Operador Strimzi
│   ├── connect/             # Kafka Connect
│   │   ├── deployment.yaml
│   │   └── s3-sink.json
│   └── topics/              # Definición de tópicos
│       └── orders.yaml
└── overlays/                # Kustomize overlays por entorno
    ├── dev/
    ├── stg/
    └── prod/
```

## Componentes

### Namespaces

`namespaces.yaml` define los namespaces principales:

- `data`: Airflow y pipelines de datos
- `integration`: APIs y servicios de integración
- `workflows`: Orquestadores (Camunda, Flowable, Kestra)
- `ml`: MLOps (MLflow, KServe, Kubeflow)
- `observability`: Prometheus, Grafana, ELK
- `security`: Cert-manager, OAuth2-proxy, External Secrets
- `backup`: Velero

Aplicar:

```bash
kubectl apply -f kubernetes/namespaces.yaml
```

### Ingress

Configuración del controlador NGINX Ingress:

- LoadBalancer para exponer servicios
- Integración con cert-manager para TLS
- Anotaciones para rate limiting y autenticación

Ver: `kubernetes/ingress/nginx-ingress.yaml`

### Integration Services

#### Healthz

Endpoint de health check básico para validar conectividad del cluster:

```bash
kubectl apply -f kubernetes/integration/healthz.yaml
kubectl apply -f kubernetes/integration/healthz-hpa.yaml
kubectl apply -f kubernetes/integration/healthz-pdb.yaml
```

#### KPIs API

API de KPIs que expone métricas del negocio:

```bash
kubectl apply -f kubernetes/integration/kpis-api.yaml
```

### Kafka

#### Strimzi Operator

Operador de Kafka para Kubernetes:

```bash
kubectl apply -f kubernetes/kafka/strimzi-kafka.yaml
```

#### Kafka Connect

Conectores para integraciones (ej: S3 sink):

```bash
kubectl apply -f kubernetes/kafka/connect/deployment.yaml
```

#### Tópicos

Definición de tópicos de Kafka:

```bash
kubectl apply -f kubernetes/kafka/topics/orders.yaml
```

### Overlays (Kustomize)

Los overlays permiten personalizar la configuración por entorno:

```bash
# Desarrollo
kubectl apply -k kubernetes/overlays/dev

# Staging
kubectl apply -k kubernetes/overlays/stg

# Producción
kubectl apply -k kubernetes/overlays/prod
```

Cada overlay puede:
- Cambiar hosts de Ingress
- Ajustar recursos (CPU/memoria)
- Aplicar labels específicos por entorno
- Referenciar configuraciones de `environments/{env}.yaml`

## Uso con Makefile

El Makefile proporciona comandos convenientes:

```bash
# Aplicar namespaces
make k8s-namespaces

# Aplicar Ingress
make k8s-ingress

# Aplicar servicios de integración
make k8s-integration

# Aplicar Kafka
make k8s-kafka

# Aplicar tópicos de Kafka
make k8s-kafka-topics

# Aplicar overlay por entorno
make kustomize-dev
make kustomize-stg
make kustomize-prod

# Validar overlays
make kustomize-validate-dev
```

## Buenas Prácticas

### Labels

Usa labels consistentes según [Kubernetes Recommended Labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/):

```yaml
metadata:
  labels:
    app.kubernetes.io/name: kpis-api
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: platform
    app.kubernetes.io/managed-by: kustomize
    app.kubernetes.io/environment: dev
```

### Resource Requests/Limits

Siempre define requests y limits:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

Gatekeeper puede forzar esto (ver `security/policies/gatekeeper/limits.yaml`).

### Health Checks

Incluye probes de readiness y liveness:

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

### Security Context

Ejecuta contenedores como usuario no-root cuando sea posible:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
```

### Secrets

Nunca hardcodees secrets en manifiestos:

- Usa **Secrets** de Kubernetes (inyectados por External Secrets)
- Usa **ConfigMaps** para configuración no sensible
- Referencia desde External Secrets Operator

## Validación

### Dry-run

Antes de aplicar, valida los manifiestos:

```bash
# Validar sintaxis
kubectl apply --dry-run=client -f kubernetes/integration/kpis-api.yaml

# Validar con Kustomize
kubectl kustomize kubernetes/overlays/dev --dry-run=client
```

### Linting

Usa herramientas de linting:

```bash
# kubeval
kubeval kubernetes/integration/*.yaml

# kube-linter
kube-linter lint kubernetes/integration/

# kubectl
kubectl apply --dry-run=server -f kubernetes/
```

## Orden de Aplicación

1. **Namespaces**: Primero crear los namespaces
2. **CRDs**: Instalar Custom Resource Definitions (Strimzi, cert-manager, etc.)
3. **Operadores**: Instalar operadores (Strimzi, External Secrets)
4. **Configuración Base**: Secrets, ConfigMaps, RBAC
5. **Aplicaciones**: Deployments, Services, Ingress
6. **Overlays**: Aplicar personalizaciones por entorno

## Troubleshooting

### Ver recursos

```bash
# Ver todos los recursos en un namespace
kubectl get all -n integration

# Ver eventos
kubectl get events -n integration --sort-by='.lastTimestamp'

# Describir un recurso
kubectl describe deployment kpis-api -n integration
```

### Logs

```bash
# Logs de un pod
kubectl logs -n integration deployment/kpis-api

# Logs de múltiples pods (ej: StatefulSet)
kubectl logs -n data statefulset/airflow-scheduler --all-containers
```

### Debugging

```bash
# Ejecutar shell en un pod
kubectl exec -it -n integration deployment/kpis-api -- /bin/sh

# Port-forward para acceso local
kubectl port-forward -n integration service/kpis-api 8080:8080
```

## Referencias

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)


