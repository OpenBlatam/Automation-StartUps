# Integración MLflow - Airflow

> **Versión**: 1.0 | **Última actualización**: 2025-01-15 | **Estado**: Producción Ready ✅

Guía completa para integrar MLflow con Airflow DAGs, incluyendo mejores prácticas, troubleshooting y ejemplos avanzados.

## 📋 Tabla de Contenidos

- [Configuración](#configuración)
- [Integración Básica](#integración-básica)
- [Integración Avanzada](#integración-avanzada)
- [Rate Limiting](#rate-limiting)
- [Mejores Prácticas](#mejores-prácticas)
- [Troubleshooting](#troubleshooting)
- [Métricas y Observabilidad](#métricas-y-observabilidad)

## Configuración

### 1. Variables de Entorno en Airflow

```bash
# Resolver MLflow URI desde environments/*.yaml
export MLFLOW_TRACKING_URI="http://mlflow.ml.svc.cluster.local:5000"

# O configurar via Airflow Variable
airflow variables set MLFLOW_TRACKING_URI "http://mlflow.ml.svc.cluster.local:5000"
```

### 2. Resolución Automática desde environments/*.yaml

El plugin `etl_example.py` incluye función `_resolve_mlflow_uri_from_env()` que resuelve automáticamente:

```python
def _resolve_mlflow_uri_from_env() -> str | None:
    """Resolve MLflow URI from environments/<env>.yaml"""
    env = os.getenv("ENV", "dev")
    env_file = f"environments/{env}.yaml"
    # Busca línea: mlflow: mlflow.example.com
    # Retorna: https://mlflow.example.com
```

**Formato en environments/*.yaml:**
```yaml
# environments/dev.yaml
domains:
  mlflow: mlflow-dev.example.com

# environments/prod.yaml
domains:
  mlflow: mlflow.example.com
```

### 3. Verificación de Conectividad

```python
# En Airflow task
import mlflow
import os

tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
if tracking_uri:
    mlflow.set_tracking_uri(tracking_uri)
    try:
        experiments = mlflow.search_experiments(max_results=1)
        logger.info(f"MLflow conectado: {tracking_uri}")
    except Exception as e:
        logger.error(f"MLflow no disponible: {e}")
```

## Integración Básica

### Ejemplo 1: Logging Simple desde DAG

```python
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
import mlflow
import os

@dag(dag_id="simple_mlflow_example")
def simple_mlflow_dag():
    @task
    def log_to_mlflow():
        ctx = get_current_context()
        
        # Configurar tracking URI
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        
        # Crear/establecer experimento
        experiment_name = "simple_experiment"
        mlflow.set_experiment(experiment_name)
        
        # Iniciar run
        run_name = f"run_{ctx['run_id']}"
        with mlflow.start_run(run_name=run_name):
            # Log parámetros
            mlflow.log_param("dag_id", ctx['dag'].dag_id)
            mlflow.log_param("run_id", ctx['run_id'])
            
            # Log métricas
            mlflow.log_metric("rows_processed", 1000)
            mlflow.log_metric("duration_ms", 5000)
            
            # Tags
            mlflow.set_tag("environment", os.getenv("ENV", "dev"))
            mlflow.set_tag("source", "airflow")
    
    log_to_mlflow()

dag = simple_mlflow_dag()
```

### Ejemplo 2: Usando Plugin etl_ops.log_with_mlflow

```python
from data.airflow.plugins.etl_ops import log_with_mlflow
from data.airflow.plugins.etl_types import ExtractPayload

@task
def load(payload: ExtractPayload) -> None:
    ctx = get_current_context()
    
    # Log con rate limiting automático (20 calls/min)
    log_with_mlflow(
        payload=payload,
        run_name=ctx['params'].get('run_name', 'default'),
        tags={
            'dag_id': ctx['dag'].dag_id,
            'run_id': ctx['run_id'],
            'chunk': str(ctx.get('map_index', '')),
        }
    )
```

## Integración Avanzada

### Ejemplo 1: Tracking de Model Training Pipeline

```python
from airflow.decorators import dag, task
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

@dag(dag_id="ml_training_pipeline")
def training_pipeline():
    @task
    def load_data():
        # Cargar datos
        data = pd.read_csv("/data/training.csv")
        return data
    
    @task
    def train_model(data: pd.DataFrame):
        ctx = get_current_context()
        
        # Configurar MLflow
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("model_training")
        
        # Preparar datos
        X = data.drop('target', axis=1)
        y = data['target']
        
        # Iniciar run
        run_name = f"training_{ctx['run_id']}"
        with mlflow.start_run(run_name=run_name):
            # Parámetros del modelo
            n_estimators = 100
            max_depth = 10
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("max_depth", max_depth)
            mlflow.log_param("algorithm", "RandomForest")
            
            # Entrenar
            model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42
            )
            model.fit(X, y)
            
            # Evaluar
            train_score = model.score(X, y)
            mlflow.log_metric("train_accuracy", train_score)
            
            # Registrar modelo
            mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name="churn_prediction_model"
            )
            
            # Artifacts
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': model.feature_importances_
            })
            feature_importance.to_csv("/tmp/feature_importance.csv", index=False)
            mlflow.log_artifact("/tmp/feature_importance.csv")
            
            return mlflow.active_run().info.run_id
    
    data = load_data()
    run_id = train_model(data)

dag = training_pipeline()
```

### Ejemplo 2: Tracking de ETL con Métricas de Calidad

```python
from data.airflow.plugins.etl_ops import log_with_mlflow
from data.airflow.plugins.etl_validation import validate_payload_schema

@task
def transform_and_track(payload: ExtractPayload) -> ExtractPayload:
    ctx = get_current_context()
    
    # Validar y transformar
    validate_payload_schema(payload)
    transformed = apply_transform(payload)
    
    # Calcular métricas de calidad
    rows = transformed.get("rows", 0)
    null_rate = transformed.get("null_rate", 0.0)
    checksum = transformed.get("checksum", 0)
    
    # Log a MLflow con contexto completo
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI") or _resolve_mlflow_uri_from_env()
    if tracking_uri:
        import mlflow
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("etl_quality_tracking")
        
        with mlflow.start_run(run_name=f"etl_{ctx['run_id']}"):
            # Parámetros
            mlflow.log_param("dag_id", ctx['dag'].dag_id)
            mlflow.log_param("run_id", ctx['run_id'])
            mlflow.log_param("transformed", "true")
            
            # Métricas
            mlflow.log_metric("rows_processed", float(rows))
            mlflow.log_metric("null_rate", float(null_rate))
            mlflow.log_metric("checksum", float(checksum))
            
            # Tags
            mlflow.set_tag("environment", os.getenv("ENV", "dev"))
            mlflow.set_tag("component", "etl")
    
    return transformed
```

### Ejemplo 3: Comparación de Runs con MLflow

```python
@task
def compare_experiments():
    """Comparar resultados de diferentes runs de MLflow"""
    import mlflow
    from mlflow.tracking import MlflowClient
    
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()
    
    # Buscar runs del último experimento
    experiment = mlflow.get_experiment_by_name("model_training")
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=10,
        order_by=["metrics.train_accuracy DESC"]
    )
    
    # Análisis
    best_run = runs.iloc[0]
    logger.info(f"Mejor run: {best_run['run_id']}")
    logger.info(f"Accuracy: {best_run['metrics.train_accuracy']}")
    
    return {
        "best_run_id": best_run['run_id'],
        "best_accuracy": best_run['metrics.train_accuracy']
    }
```

## Rate Limiting

### Configuración en etl_ops.py

El plugin `etl_ops.log_with_mlflow()` incluye rate limiting automático:

```python
@rate_limit(max_calls=20, window_seconds=60, variable_key="mlflow_api")
def _mlflow_log_internal(...):
    # Máximo 20 llamadas por minuto
    # Espera automática si se excede
```

### Monitoreo de Rate Limits

```bash
# Ver estado del rate limit
airflow variables get rate_limit:mlflow_api | jq

# Reset manual si es necesario
airflow variables delete rate_limit:mlflow_api
```

### Métricas de Rate Limiting

```python
from airflow.stats import Stats

# Verificar hits de rate limit
rate_limit_hits = Stats.gauge("rate_limit.mlflow_api.hits")
if rate_limit_hits > 10:
    logger.warning(f"Rate limit frecuente: {rate_limit_hits} hits")
```

## Mejores Prácticas

### 1. Usar Experimentos Organizados

```python
# ✅ Bueno: Experimentos por componente/proyecto
mlflow.set_experiment("etl_quality")
mlflow.set_experiment("model_training")
mlflow.set_experiment("lead_scoring")

# ❌ Malo: Un solo experimento para todo
mlflow.set_experiment("all")
```

### 2. Tags Consistentes

```python
# Tags recomendados
mlflow.set_tag("dag_id", ctx['dag'].dag_id)
mlflow.set_tag("environment", os.getenv("ENV", "dev"))
mlflow.set_tag("team", "data-engineering")
mlflow.set_tag("component", "etl")
mlflow.set_tag("version", "1.0")
```

### 3. Manejo de Errores

```python
try:
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("experiment_name")
    with mlflow.start_run():
        # Tu código aquí
        pass
except Exception as e:
    # No fallar el DAG si MLflow no está disponible
    logger.warning(f"MLflow logging skipped: {e}")
    # Continuar sin MLflow
```

### 4. Logging Selectivo

```python
# Solo loguear si está habilitado
mlflow_enabled = bool(ctx['params'].get('mlflow_enable', False))

if mlflow_enabled and _MLFLOW_AVAILABLE:
    log_with_mlflow(...)
else:
    logger.debug("MLflow logging disabled")
```

### 5. Limpiar Runs Antiguos

```python
# Desde DAG de mantenimiento
@task
def cleanup_old_runs():
    from mlflow.tracking import MlflowClient
    
    client = MlflowClient()
    
    # Buscar runs antiguos (>90 días)
    cutoff_date = (pendulum.now() - timedelta(days=90)).timestamp()
    
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"start_time < {cutoff_date}",
        max_results=1000
    )
    
    # Eliminar
    for run in runs:
        client.delete_run(run.info.run_id)
        logger.info(f"Deleted old run: {run.info.run_id}")
```

## Troubleshooting

### Problema 1: MLflow no disponible

**Síntoma:**
```
Error: Connection refused to MLflow tracking URI
```

**Solución:**
```bash
# 1. Verificar que MLflow está corriendo
kubectl get pods -n ml -l app=mlflow

# 2. Verificar Service
kubectl get svc -n ml mlflow

# 3. Verificar conectividad desde Airflow pod
kubectl exec -n airflow deployment/airflow-worker -- \
  curl -v http://mlflow.ml.svc.cluster.local:5000/health

# 4. Verificar DNS
kubectl exec -n airflow deployment/airflow-worker -- \
  nslookup mlflow.ml.svc.cluster.local
```

### Problema 2: Rate Limit Excedido

**Síntoma:**
```
Rate limit exceeded, waiting 30s
```

**Solución:**
```python
# Aumentar límite en etl_ops.py
@rate_limit(max_calls=50, window_seconds=60)  # De 20 a 50
```

O distribuir llamadas:
```python
# Usar delay entre llamadas
import time

for chunk in chunks:
    log_with_mlflow(chunk)
    time.sleep(1)  # 1 segundo entre llamadas
```

### Problema 3: Timeouts en Upload de Artefactos

**Síntoma:**
```
Timeout uploading artifact to S3
```

**Solución:**
```yaml
# En ml/mlflow/values.yaml
mlflow:
  extraEnv:
    - name: MLFLOW_ARTIFACT_UPLOAD_TIMEOUT
      value: "600"  # Aumentar a 10 minutos
```

### Problema 4: PostgreSQL Connection Pool Exhausted

**Síntoma:**
```
QueuePool limit of size 20 overflow 10 reached
```

**Solución:**
```yaml
# Aumentar pool en ml/mlflow/values.yaml
backendStore:
  postgres:
    poolSize: 40
    maxOverflow: 80
```

## Métricas y Observabilidad

### Métricas de Prometheus

MLflow expone métricas en `/metrics`:

- `mlflow_http_requests_total`: Total de requests HTTP
- `mlflow_http_request_duration_seconds`: Latencia de requests
- `mlflow_experiments_created_total`: Experimentos creados
- `mlflow_runs_logged_total`: Runs logueados
- `mlflow_artifact_upload_failed_total`: Fallos en upload

### Queries de Prometheus Útiles

```promql
# Tasa de errores 5xx
rate(mlflow_http_requests_total{status=~"5.."}[5m]) 
/ rate(mlflow_http_requests_total[5m])

# Latencia p95
histogram_quantile(0.95, 
  rate(mlflow_http_request_duration_seconds_bucket[5m])
)

# Runs por minuto
rate(mlflow_runs_logged_total[5m])
```

### Alertas Configuradas

Ver `observability/prometheus/alertrules.yaml`:
- `MLflowServerDown`: Servidor caído
- `MLflowHighErrorRate`: >5% errores 5xx
- `MLflowHighLatency`: Latencia p95 > 2s
- `MLflowPostgresConnectionPoolExhausted`: Pool >90% usado

## Referencias

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Airflow MLflow Integration](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/operators.html)
- [Prometheus MLflow Metrics](../observability/prometheus/alertrules.yaml)

