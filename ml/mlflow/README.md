# MLflow - Model Tracking y Registry

> **Versión**: 2.1 | **Última actualización**: 2025-01 | **Estado**: Producción Ready ✅

MLflow es una plataforma open-source para gestionar el ciclo de vida de machine learning, incluyendo tracking de experimentos, empaquetado de modelos y registro de modelos.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Características Principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Configuración](#configuración)
- [Instalación](#instalación)
- [Uso](#uso)
- [Integraciones](#integraciones)
- [Monitoreo](#monitoreo)
- [Seguridad](#seguridad)
- [Backups](#backups)
- [Troubleshooting](#troubleshooting)
- [Referencias](#referencias)

## Descripción

MLflow proporciona:

- **Tracking**: Registro de parámetros, métricas y artefactos de experimentos
- **Projects**: Empaquetado de código ML en formato reproducible
- **Models**: Formato estándar para empaquetar modelos
- **Model Registry**: Almacén centralizado para gestionar modelos

## Características Principales

### ✅ Configuración Production-Ready

El archivo `values.yaml` incluye:

- ✅ **Backend Store**: PostgreSQL con connection pooling optimizado
- ✅ **Artifact Store**: S3/ADLS con soporte multi-cloud
- ✅ **High Availability**: Replicas, Pod Disruption Budget, Health Checks
- ✅ **Autoscaling**: HPA configurado (2-10 replicas)
- ✅ **Monitoring**: ServiceMonitor para Prometheus
- ✅ **Security**: Security contexts, Network Policies, TLS
- ✅ **Resource Management**: Requests/Limits configurados
- ✅ **Cleanup Automático**: Eliminación de runs/experimentos antiguos

### Recursos y Performance

```yaml
mlflow:
  workers: 2
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi
```

### Connection Pooling

```yaml
backendStore:
  postgres:
    poolSize: 20
    maxOverflow: 40
    poolRecycle: 3600
    poolPrePing: true
```

## Arquitectura

```
┌─────────────────────────────────────────┐
│         MLflow UI (Ingress)              │
│         http://mlflow.example.com        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      MLflow Server (PodSet)              │
│  ┌──────────┐  ┌──────────┐            │
│  │ Worker 1 │  │ Worker 2 │            │
│  └────┬─────┘  └────┬─────┘            │
└───────┼─────────────┼──────────────────┘
        │             │
        ▼             ▼
┌─────────────────────────────────────────┐
│      PostgreSQL (Backend Store)          │
│      Metadatos, parámetros, métricas     │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│      S3/ADLS (Artifact Store)            │
│      Modelos, artefactos, datos          │
└─────────────────────────────────────────┘
```

## Configuración

### Variables Principales

#### Backend Store (PostgreSQL)

```yaml
backendStore:
  postgres:
    enabled: true
    host: postgres.ml.svc.cluster.local
    port: 5432
    database: mlflow
    username: mlflow
    passwordFromSecret:
      enabled: true
      name: mlflow-postgres-secret
      key: password
    poolSize: 20
    maxOverflow: 40
    sslMode: prefer
    cleanupRunsEnabled: true
    cleanupRunsDays: 90
```

#### Artifact Store (S3/ADLS)

```yaml
artifactStore:
  s3:
    enabled: true
    bucket: biz-datalake-dev
    path: mlflow/artifacts
    # Usar IRSA en producción (AWS) o Workload Identity (Azure)
```

#### Ingress con TLS

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: mlflow.example.com
      paths:
        - path: /
  tls:
    - secretName: mlflow-tls
      hosts:
        - mlflow.example.com
```

## Instalación

### Estructura de Archivos

```
ml/mlflow/
├── values.yaml          # Configuración base (producción-ready)
├── values-dev.yaml      # Override para desarrollo
├── values-prod.yaml     # Override para producción (máxima seguridad)
├── scripts/
│   ├── health-check.sh              # Script de verificación de salud
│   └── setup-external-secrets.sh    # Configuración de External Secrets
└── README.md            # Esta documentación
```

### Instalación por Entorno

#### Desarrollo

```bash
# Instalar con override de desarrollo
helm install mlflow mlflow/mlflow \
  --namespace ml \
  --create-namespace \
  -f ml/mlflow/values.yaml \
  -f ml/mlflow/values-dev.yaml

# O con Helmfile
helmfile apply --file helmfile-dev.yaml
```

#### Producción

```bash
# Instalar con override de producción
helm install mlflow mlflow/mlflow \
  --namespace ml \
  --create-namespace \
  -f ml/mlflow/values.yaml \
  -f ml/mlflow/values-prod.yaml

# Verificar External Secrets primero
ml/mlflow/scripts/setup-external-secrets.sh

# O con Helmfile
helmfile apply --file helmfile-prod.yaml
```

### Con Helmfile (Recomendado)

```bash
# Aplicar configuración base
helmfile apply

# Con override específico
helmfile apply --file helmfile-dev.yaml
```

### Con Helm Directo

```bash
# Añadir repositorio
helm repo add mlflow https://community-charts.github.io/charts
helm repo update

# Instalar MLflow (desarrollo)
helm install mlflow mlflow/mlflow \
  --namespace ml \
  --create-namespace \
  -f ml/mlflow/values.yaml \
  -f ml/mlflow/values-dev.yaml

# Verificar
kubectl get pods -n ml
kubectl get ingress -n ml
```

### Verificar Instalación

#### Health Check Automático

```bash
# Usar script de health check
MLFLOW_NAMESPACE=ml ml/mlflow/scripts/health-check.sh

# O manualmente
kubectl get pods -n ml -l app=mlflow
kubectl get svc -n ml
kubectl get ingress -n ml mlflow
curl http://mlflow.example.com/health
```

#### Verificación de Componentes

```bash
# Ver pods
kubectl get pods -n ml -l app=mlflow

# Ver servicios
kubectl get svc -n ml

# Ver ingress
kubectl get ingress -n ml mlflow

# Ver External Secrets (si aplica)
kubectl get externalsecrets -n ml

# Ver secrets sincronizados
kubectl get secrets -n ml | grep mlflow

# Test de conectividad
curl -k https://mlflow.example.com/health
```

## Uso

### Acceder al UI

```bash
# Obtener la URL del Ingress
kubectl get ingress -n ml mlflow -o jsonpath='{.spec.rules[0].host}'

# O con port-forward (desarrollo)
kubectl port-forward -n ml service/mlflow 5000:5000
# Abrir http://localhost:5000
```

### Configurar Tracking URI

**Desde Python**:

```python
import mlflow

# Opción 1: Configurar directamente
mlflow.set_tracking_uri("http://mlflow.example.com")

# Opción 2: Variable de entorno
# export MLFLOW_TRACKING_URI=http://mlflow.example.com
```

**Desde Airflow DAGs**:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
import mlflow

def train_model():
    mlflow.set_tracking_uri("http://mlflow.ml.svc.cluster.local")
    mlflow.set_experiment("my_experiment")
    # ... código de entrenamiento

dag = DAG('ml_training', ...)
train_task = PythonOperator(
    task_id='train', 
    python_callable=train_model, 
    dag=dag
)
```

### Ejemplo Básico de Tracking

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Configurar tracking
mlflow.set_tracking_uri("http://mlflow.example.com")
mlflow.set_experiment("iris-classification")

with mlflow.start_run():
    # Cargar datos
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Parámetros del modelo
    n_estimators = 100
    max_depth = 10
    
    # Entrenar modelo
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Calcular métricas
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    
    # Registrar parámetros
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    
    # Registrar métricas
    mlflow.log_metric("train_accuracy", train_accuracy)
    mlflow.log_metric("test_accuracy", test_accuracy)
    
    # Registrar modelo
    mlflow.sklearn.log_model(model, "model")
    
    print(f"Run ID: {mlflow.active_run().info.run_id}")
```

### Model Registry

**Registrar modelo desde código**:

```python
# Obtener run_id del run actual
run_id = mlflow.active_run().info.run_id
model_uri = f"runs:/{run_id}/model"

# Registrar modelo
model_name = "iris-classifier"
mlflow.register_model(model_uri, model_name)

print(f"Modelo '{model_name}' registrado exitosamente")
```

**Registrar desde UI**:
1. Ir a Experiments → Seleccionar run
2. Click en "Register Model"
3. Ingresar nombre del modelo o seleccionar uno existente

**Promover modelo a Production**:

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
model_name = "iris-classifier"

# Obtener versión más reciente
latest_version = client.get_latest_versions(model_name)[0]

# Promover a Production
client.transition_model_version_stage(
    name=model_name,
    version=latest_version.version,
    stage="Production"
)
```

### Servir Modelo Localmente

```bash
# Servir modelo desde registry
mlflow models serve -m "models:/iris-classifier/1" -p 5001

# Hacer predicción
curl -X POST http://localhost:5001/invocations \
  -H 'Content-Type: application/json' \
  -d '{"inputs": [[5.1, 3.5, 1.4, 0.2]]}'
```

## Integraciones

### Integración con Airflow

Ver [`data/airflow/README.md`](../../data/airflow/README.md) para configuración completa.

**Ejemplo en DAG**:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import mlflow

def train_with_mlflow(**context):
    mlflow.set_tracking_uri("http://mlflow.ml.svc.cluster.local")
    mlflow.set_experiment(f"airflow-{context['dag_run'].run_id}")
    
    with mlflow.start_run():
        # ... entrenar modelo
        mlflow.log_metric("accuracy", 0.95)
        mlflow.sklearn.log_model(model, "model")

dag = DAG('mlflow_training', ...)
train = PythonOperator(
    task_id='train',
    python_callable=train_with_mlflow,
    dag=dag
)
```

### Integración con KServe

Ver [`ml/kserve/README.md`](../kserve/README.md) para servir modelos con KServe.

**Ejemplo**:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: iris-classifier
  namespace: ml
spec:
  predictor:
    sklearn:
      storageUri: s3://biz-datalake-dev/mlflow/artifacts/12345/model
```

### Integración con S3/ADLS

**S3 (AWS)**:

```bash
# Variables de entorno (o IRSA)
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_REGION=us-east-1
```

**ADLS (Azure)**:

```bash
# Variables de entorno (o Managed Identity)
export AZURE_STORAGE_ACCOUNT_NAME=xxx
export AZURE_STORAGE_ACCESS_KEY=xxx
# O usar Managed Identity si está configurado
```

## Monitoreo

### Métricas de Prometheus

MLflow expone métricas en el endpoint `/metrics`:

```bash
# Ver métricas
curl http://mlflow.example.com/metrics
```

**Métricas disponibles**:
- `mlflow_http_requests_total`: Total de requests HTTP
- `mlflow_http_request_duration_seconds`: Duración de requests
- `mlflow_runs_total`: Total de runs registrados
- `mlflow_experiments_total`: Total de experimentos

### ServiceMonitor

El ServiceMonitor está configurado en `values.yaml`:

```yaml
serviceMonitor:
  enabled: true
  interval: 30s
  scrapeTimeout: 10s
```

**Verificar**:

```bash
kubectl get servicemonitor -n ml mlflow
```

### Grafana Dashboard

Importar dashboard desde `observability/grafana/dashboards/mlflow.json` (si existe) o crear uno nuevo usando las métricas de Prometheus.

### Logs

```bash
# Ver logs de MLflow
kubectl logs -n ml deployment/mlflow -f

# Ver logs de todos los pods
kubectl logs -n ml -l app=mlflow -f

# Filtrar por nivel
kubectl logs -n ml deployment/mlflow | grep ERROR
```

## Seguridad

### Autenticación

MLflow no incluye autenticación por defecto. Opciones:

1. **OAuth2-proxy**: Ver [`security/oauth2-proxy/`](../../security/oauth2-proxy/)
2. **Ingress con auth**: Configurar en annotations del Ingress
3. **VPN/Private network**: Acceso solo interno

### HTTPS/TLS

Configurado en `values.yaml` con cert-manager:

```yaml
ingress:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  tls:
    - secretName: mlflow-tls
      hosts:
        - mlflow.example.com
```

### Network Policies

```yaml
networkPolicy:
  enabled: true
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: data
      ports:
        - protocol: TCP
          port: 5000
```

### Secrets Management

**External Secrets Operator** (Recomendado):

```yaml
# Ver security/secrets/externalsecrets-*.yaml
backendStore:
  postgres:
    passwordFromSecret:
      enabled: true
      name: mlflow-postgres-secret
      key: password
```

## Backups

### Backup de Base de Datos

```bash
# Backup de PostgreSQL
kubectl exec -n ml postgres-pod -- \
  pg_dump -U mlflow mlflow > mlflow_backup_$(date +%Y%m%d).sql

# Restaurar
kubectl exec -i -n ml postgres-pod -- \
  psql -U mlflow mlflow < mlflow_backup_20240115.sql
```

### Backup de Artefactos

Los artefactos en S3/ADLS deben tener versioning y backups habilitados (ver `infra/terraform`).

**S3**:

```bash
# Habilitar versioning
aws s3api put-bucket-versioning \
  --bucket biz-datalake-dev \
  --versioning-configuration Status=Enabled

# Configurar lifecycle policies en Terraform
```

### Backup Automático con Velero

Si Velero está configurado, los PVCs se pueden hacer backup automáticamente. Sin embargo, los artefactos en S3 no necesitan backup ya que están en el data lake.

## Troubleshooting

### Error de Conexión a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
kubectl get pods -n ml -l app=postgresql

# Verificar credenciales
kubectl get secret -n ml mlflow-postgres-secret -o yaml

# Test de conexión
kubectl exec -n ml deployment/mlflow -- \
  python -c "import psycopg2; psycopg2.connect('postgresql://mlflow:xxx@postgres.ml.svc.cluster.local:5432/mlflow')"
```

### Error de S3/Artifact Store

```bash
# Verificar credenciales AWS
kubectl exec -n ml deployment/mlflow -- env | grep AWS

# Verificar permisos del bucket
aws s3 ls s3://biz-datalake-dev/mlflow/

# Test de acceso
kubectl exec -n ml deployment/mlflow -- \
  aws s3 ls s3://biz-datalake-dev/mlflow/artifacts/
```

### UI no Carga

```bash
# Verificar Ingress
kubectl get ingress -n ml mlflow
kubectl describe ingress -n ml mlflow

# Verificar servicios
kubectl get svc -n ml mlflow

# Verificar pods
kubectl get pods -n ml -l app=mlflow

# Port-forward para debug
kubectl port-forward -n ml service/mlflow 5000:5000
# Probar http://localhost:5000
```

### Performance Lento

1. **Aumentar workers**:
   ```yaml
   mlflow:
     workers: 4
   ```

2. **Aumentar connection pool**:
   ```yaml
   backendStore:
     postgres:
       poolSize: 40
       maxOverflow: 80
   ```

3. **Verificar recursos**:
   ```bash
   kubectl top pods -n ml -l app=mlflow
   ```

### Pods en CrashLoopBackOff

```bash
# Ver logs
kubectl logs -n ml deployment/mlflow --previous

# Ver eventos
kubectl get events -n ml --sort-by='.lastTimestamp'

# Verificar configuración
kubectl describe deployment -n ml mlflow
```

## Referencias

### Documentación Oficial

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow Python API](https://mlflow.org/docs/latest/python_api/index.html)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)

### Charts y Deployment

- [MLflow Helm Chart](https://github.com/community-charts/charts/tree/main/charts/mlflow)

### Integraciones

- [MLflow + Airflow](https://mlflow.org/docs/latest/tracking.html#airflow-integration)
- [MLflow + KServe](../kserve/README.md)

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: ML Engineering Team  
**Última actualización**: 2024
