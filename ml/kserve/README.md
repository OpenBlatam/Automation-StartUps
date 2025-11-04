# KServe - Model Serving

KServe proporciona una plataforma de alto nivel para servir modelos de machine learning en Kubernetes con autoscaling automático y soporte para múltiples frameworks.

## Descripción

KServe (anteriormente KFServing) es una abstracción sobre Knative Serving y Istio que simplifica el despliegue y serving de modelos ML en Kubernetes. Soporta múltiples frameworks como TensorFlow, PyTorch, Scikit-learn, XGBoost, etc.

## Estructura

```
kserve/
└── model.yaml    # Ejemplo de InferenceService
```

## Archivo model.yaml

Este archivo define un `InferenceService` de ejemplo usando Scikit-learn:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
  namespace: ml
spec:
  predictor:
    sklearn:
      storageUri: gs://kfserving-examples/models/sklearn/1.0/model
      resources:
        requests:
          cpu: 100m
          memory: 256Mi
        limits:
          cpu: 500m
          memory: 512Mi
```

## Instalación

### Prerrequisitos

- Kubernetes cluster 1.23+
- Knative Serving instalado
- Istio o Kourier como Ingress

### Instalar KServe

```bash
# Instalar operador de KServe
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.13.0/kserve.yaml

# Verificar instalación
kubectl get pods -n kserve-system
```

## Uso

### Desplegar un Modelo

```bash
# Aplicar el InferenceService
kubectl apply -f ml/kserve/model.yaml

# Verificar estado
kubectl get inferenceservice sklearn-iris -n ml

# Ver detalles
kubectl describe inferenceservice sklearn-iris -n ml
```

### Hacer Predicciones

Una vez desplegado, el servicio expone un endpoint:

```bash
# Obtener la URL del servicio
SERVICE_HOST=$(kubectl get inferenceservice sklearn-iris -n ml -o jsonpath='{.status.url}' | cut -d "/" -f 3)

# Hacer una predicción
curl -v -H "Host: ${SERVICE_HOST}" \
  http://${INGRESS_HOST}/v1/models/sklearn-iris:predict \
  -d @- <<EOF
{
  "instances": [[5.1, 3.5, 1.4, 0.2]]
}
EOF
```

### Usar con Python

```python
import requests
import json

url = "http://sklearn-iris.ml.svc.cluster.local/v1/models/sklearn-iris:predict"
data = {"instances": [[5.1, 3.5, 1.4, 0.2]]}

response = requests.post(url, json=data)
print(response.json())
```

## Frameworks Soportados

### TensorFlow

```yaml
spec:
  predictor:
    tensorflow:
      storageUri: s3://bucket/models/tensorflow/
      resources:
        requests:
          cpu: 100m
          memory: 512Mi
```

### PyTorch

```yaml
spec:
  predictor:
    pytorch:
      storageUri: s3://bucket/models/pytorch/
      modelClassName: MyModel
```

### XGBoost

```yaml
spec:
  predictor:
    xgboost:
      storageUri: s3://bucket/models/xgboost/
```

### Scikit-learn

```yaml
spec:
  predictor:
    sklearn:
      storageUri: s3://bucket/models/sklearn/
```

### ONNX

```yaml
spec:
  predictor:
    onnx:
      storageUri: s3://bucket/models/onnx/
```

## Almacenamiento de Modelos

Los modelos pueden almacenarse en:

- **S3**: `s3://bucket/path/to/model`
- **GCS**: `gs://bucket/path/to/model`
- **Azure Blob**: `https://account.blob.core.windows.net/container/path`
- **HTTP/HTTPS**: URLs públicas
- **PVC**: Volúmenes persistentes de Kubernetes

### Credenciales para Storage

Para S3/GCS/Azure, configura secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: s3-credentials
  namespace: ml
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: YOUR_KEY
  AWS_SECRET_ACCESS_KEY: YOUR_SECRET
```

Y referencia en el InferenceService:

```yaml
spec:
  predictor:
    sklearn:
      storageUri: s3://bucket/models/
      s3:
        secretName: s3-credentials
```

## Autoscaling

KServe soporta autoscaling basado en métricas:

```yaml
metadata:
  annotations:
    autoscaling.knative.dev/minScale: "1"
    autoscaling.knative.dev/maxScale: "10"
    autoscaling.knative.dev/target: "10"
spec:
  predictor:
    sklearn:
      # ... configuración del modelo
```

## Canary Deployments

Despliega múltiples versiones con tráfico dividido:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
spec:
  predictor:
    canaryTrafficPercent: 10
    sklearn:
      storageUri: s3://bucket/models/v2/
    canary:
      sklearn:
        storageUri: s3://bucket/models/v1/
```

## Monitoreo

### Métricas Prometheus

KServe expone métricas de Prometheus:

- `kserve_predictor_latency`: Latencia de predicciones
- `kserve_predictor_requests`: Número de requests
- `kserve_predictor_errors`: Errores

### ServiceMonitor

Crea un ServiceMonitor para Prometheus:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: sklearn-iris
  namespace: ml
spec:
  selector:
    matchLabels:
      serving.kserve.io/inferenceservice: sklearn-iris
  endpoints:
    - port: http
      interval: 30s
```

## Integración con MLflow

Para servir modelos entrenados con MLflow:

```yaml
spec:
  predictor:
    sklearn:
      storageUri: s3://mlflow-bucket/models/12345/artifacts/model
      # MLflow guarda modelos en formato compatible
```

## Troubleshooting

### Ver Logs

```bash
# Ver logs del predictor
kubectl logs -n ml deployment/sklearn-iris-predictor-default

# Ver eventos
kubectl get events -n ml --sort-by='.lastTimestamp'
```

### Verificar Estado

```bash
# Ver estado del InferenceService
kubectl get inferenceservice sklearn-iris -n ml -o yaml

# Ver pods
kubectl get pods -n ml -l serving.kserve.io/inferenceservice=sklearn-iris
```

### Debugging

```bash
# Describir el servicio
kubectl describe inferenceservice sklearn-iris -n ml

# Port-forward para pruebas locales
kubectl port-forward -n ml service/sklearn-iris-predictor-default 8080:80
```

## Referencias

- [KServe Documentation](https://kserve.github.io/website/)
- [KServe GitHub](https://github.com/kserve/kserve)
- [KServe Examples](https://github.com/kserve/kserve/tree/master/docs/samples)


