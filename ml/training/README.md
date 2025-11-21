# Training - Scripts y Pipelines de Entrenamiento

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Guía completa para entrenamiento de modelos de machine learning con MLflow, Kubeflow y KServe.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Setup Inicial](#setup-inicial)
- [Integración con MLflow](#integración-con-mlflow)
- [Ejemplos de Entrenamiento](#ejemplos-de-entrenamiento)
- [Pipelines con Kubeflow](#pipelines-con-kubeflow)
- [Integración con Airflow](#integración-con-airflow)
- [Best Practices](#best-practices)
- [Referencias](#referencias)

## Descripción

Este directorio contiene scripts, notebooks y pipelines para entrenar modelos de machine learning.

**Recomendaciones**:
- ✅ Usar MLflow para tracking de experimentos (ver [`ml/mlflow/README.md`](../mlflow/README.md))
- ✅ Guardar artefactos en el data lake (S3/ADLS)
- ✅ Registrar modelos para servir con KServe (ver [`ml/kserve/README.md`](../kserve/README.md))
- ✅ Usar pipelines reproducibles (Kubeflow o Airflow)

## Setup Inicial

### Configurar Variables de Entorno

```bash
# MLflow Tracking URI
export MLFLOW_TRACKING_URI=http://mlflow.example.com

# O desde código
import mlflow
mlflow.set_tracking_uri("http://mlflow.example.com")
```

### Estructura de Proyecto Recomendada

```
training/
├── notebooks/          # Jupyter notebooks para exploración
├── scripts/            # Scripts de entrenamiento Python
├── pipelines/          # Pipelines de Kubeflow/Airflow
├── requirements.txt    # Dependencias Python
└── config/            # Configuraciones por experimento
```

### Instalar Dependencias

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Dependencias básicas recomendadas
pip install mlflow scikit-learn pandas numpy matplotlib
```

## Integración con MLflow

### Ejemplo Básico

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Configurar tracking
mlflow.set_tracking_uri("http://mlflow.example.com")
mlflow.set_experiment("iris-classification")

with mlflow.start_run():
    # Cargar datos
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Parámetros
    n_estimators = 100
    max_depth = 10
    
    # Entrenar modelo
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluar
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, test_pred)
    
    # Logging
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_metric("train_accuracy", train_acc)
    mlflow.log_metric("test_accuracy", test_acc)
    
    # Registrar modelo
    mlflow.sklearn.log_model(model, "model")
    
    print(f"✅ Run ID: {mlflow.active_run().info.run_id}")
    print(f"📊 Test Accuracy: {test_acc:.4f}")
```

### Tracking Avanzado

```python
import mlflow
import pandas as pd
import numpy as np
from pathlib import Path

with mlflow.start_run():
    # Log parámetros como dict
    params = {
        "learning_rate": 0.01,
        "batch_size": 32,
        "epochs": 100
    }
    mlflow.log_params(params)
    
    # Log múltiples métricas
    for epoch in range(100):
        train_loss = np.random.uniform(0.1, 0.5)
        val_loss = np.random.uniform(0.15, 0.6)
        mlflow.log_metrics({
            "train_loss": train_loss,
            "val_loss": val_loss
        }, step=epoch)
    
    # Log artefactos (archivos)
    artifact_path = Path("artifacts")
    artifact_path.mkdir(exist_ok=True)
    
    # Guardar gráfico
    import matplotlib.pyplot as plt
    plt.plot([1, 2, 3, 4])
    plt.savefig(artifact_path / "training_curve.png")
    mlflow.log_artifact(artifact_path / "training_curve.png")
    
    # Guardar datos
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    df.to_csv(artifact_path / "training_data.csv", index=False)
    mlflow.log_artifact(artifact_path / "training_data.csv")
    
    # Log dataset
    mlflow.log_input(
        mlflow.data.from_pandas(df),
        context="training"
    )
```

### Model Registry

```python
from mlflow.tracking import MlflowClient

# Registrar modelo después del entrenamiento
run_id = mlflow.active_run().info.run_id
model_uri = f"runs:/{run_id}/model"
model_name = "iris-classifier"

mlflow.register_model(model_uri, model_name)

# Promover a Production
client = MlflowClient()
latest_version = client.get_latest_versions(model_name)[0]
client.transition_model_version_stage(
    name=model_name,
    version=latest_version.version,
    stage="Production"
)
```

## Ejemplos de Entrenamiento

### Scikit-learn

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

mlflow.set_experiment("gb-classifier")

with mlflow.start_run():
    # Hyperparameters
    n_estimators = 200
    learning_rate = 0.1
    max_depth = 5
    
    model = GradientBoostingClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth
    )
    
    # Cross-validation
    X, y = load_iris(return_X_y=True)
    cv_scores = cross_val_score(model, X, y, cv=5)
    
    mlflow.log_params({
        "n_estimators": n_estimators,
        "learning_rate": learning_rate,
        "max_depth": max_depth
    })
    
    mlflow.log_metric("cv_mean", cv_scores.mean())
    mlflow.log_metric("cv_std", cv_scores.std())
    
    # Entrenar modelo final
    model.fit(X, y)
    mlflow.sklearn.log_model(model, "model")
```

### TensorFlow/Keras

```python
import mlflow
import mlflow.keras
import tensorflow as tf
from tensorflow import keras

mlflow.set_experiment("keras-classifier")

with mlflow.start_run():
    # Modelo
    model = keras.Sequential([
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(10, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Datos
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
    x_train = x_train / 255.0
    x_test = x_test / 255.0
    
    # Callback de MLflow
    mlflow_callback = mlflow.keras.MLflowCallback()
    
    # Entrenar
    history = model.fit(
        x_train, y_train,
        epochs=10,
        validation_data=(x_test, y_test),
        callbacks=[mlflow_callback]
    )
    
    # Log adicional
    mlflow.log_metric("final_accuracy", history.history['accuracy'][-1])
    mlflow.keras.log_model(model, "model")
```

### PyTorch

```python
import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn

mlflow.set_experiment("pytorch-classifier")

class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

with mlflow.start_run():
    model = SimpleNet()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Datos y entrenamiento
    # ... código de entrenamiento ...
    
    mlflow.log_params({
        "learning_rate": 0.001,
        "batch_size": 64,
        "epochs": 10
    })
    
    mlflow.pytorch.log_model(model, "model")
```

### XGBoost

```python
import mlflow
import mlflow.xgboost
import xgboost as xgb

mlflow.set_experiment("xgboost-classifier")

with mlflow.start_run():
    # Datos
    X, y = load_iris(return_X_y=True)
    dtrain = xgb.DMatrix(X, label=y)
    
    # Parámetros
    params = {
        "objective": "multi:softprob",
        "num_class": 3,
        "max_depth": 6,
        "eta": 0.1,
        "eval_metric": "mlogloss"
    }
    
    # Entrenar
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=100
    )
    
    mlflow.log_params(params)
    mlflow.xgboost.log_model(model, "model")
```

## Pipelines con Kubeflow

Ver [`ml/kubeflow/README.md`](../kubeflow/README.md) para configuración completa de Kubeflow.

**Ejemplo de Pipeline**:

```python
from kfp import dsl
from kfp import compiler

@dsl.pipeline(
    name="ml-training-pipeline",
    description="Pipeline de entrenamiento con MLflow"
)
def training_pipeline():
    # Tarea de carga de datos
    load_data = dsl.ContainerOp(
        name="load-data",
        image="python:3.9",
        command=["python", "load_data.py"],
        file_outputs={"data": "/data/output.txt"}
    )
    
    # Tarea de entrenamiento
    train = dsl.ContainerOp(
        name="train-model",
        image="mlflow:latest",
        command=["python", "train.py"],
        arguments=["--data", load_data.outputs["data"]]
    )
    
    # Tarea de evaluación
    evaluate = dsl.ContainerOp(
        name="evaluate-model",
        image="mlflow:latest",
        command=["python", "evaluate.py"],
        arguments=["--model", train.outputs["model"]]
    )

# Compilar pipeline
compiler.Compiler().compile(training_pipeline, "pipeline.yaml")
```

## Integración con Airflow

Ver [`data/airflow/README.md`](../../data/airflow/README.md) para configuración completa.

**Ejemplo de DAG**:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import mlflow

def train_model(**context):
    mlflow.set_tracking_uri("http://mlflow.ml.svc.cluster.local")
    mlflow.set_experiment(f"airflow-{context['dag_run'].run_id}")
    
    with mlflow.start_run():
        # Cargar datos
        # ... código de carga ...
        
        # Entrenar
        # ... código de entrenamiento ...
        
        # Evaluar
        accuracy = 0.95
        mlflow.log_metric("accuracy", accuracy)
        
        # Registrar modelo
        mlflow.sklearn.log_model(model, "model")
        
        return {"run_id": mlflow.active_run().info.run_id}

default_args = {
    "owner": "ml-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

dag = DAG(
    "ml_training",
    default_args=default_args,
    description="Training pipeline con MLflow",
    schedule_interval="@daily"
)

train_task = PythonOperator(
    task_id="train_model",
    python_callable=train_model,
    dag=dag
)
```

## Best Practices

### ✅ DO (Hacer)

1. **Siempre usar MLflow para tracking**:
   ```python
   mlflow.set_experiment("nombre-descriptivo")
   with mlflow.start_run():
       # código de entrenamiento
   ```

2. **Logging completo de parámetros y métricas**:
   ```python
   mlflow.log_params({"lr": 0.01, "batch_size": 32})
   mlflow.log_metrics({"train_loss": 0.5, "val_loss": 0.6})
   ```

3. **Registrar modelos con versiones**:
   ```python
   mlflow.register_model(model_uri, "model-name")
   ```

4. **Guardar artefactos importantes**:
   ```python
   mlflow.log_artifact("training_curve.png")
   mlflow.log_artifact("feature_importance.csv")
   ```

5. **Usar tags para organización**:
   ```python
   mlflow.set_tag("team", "ml-team")
   mlflow.set_tag("project", "customer-churn")
   ```

### ❌ DON'T (Evitar)

1. **No hardcodear rutas o configuraciones**
2. **No ignorar métricas de validación**
3. **No entrenar sin validación cruzada para modelos pequeños**
4. **No olvidar documentar hiperparámetros**
5. **No commitear modelos grandes al repositorio**

### Estructura de Proyecto

```
training/
├── notebooks/
│   ├── 01-exploration.ipynb
│   ├── 02-feature-engineering.ipynb
│   └── 03-model-training.ipynb
├── scripts/
│   ├── train.py
│   ├── evaluate.py
│   └── deploy.py
├── config/
│   ├── config.yaml
│   └── hyperparameters.yaml
├── requirements.txt
└── README.md
```

## Referencias

### MLflow

- [MLflow Documentation](../mlflow/README.md)
- [MLflow Python API](https://mlflow.org/docs/latest/python_api/index.html)

### Kubeflow

- [Kubeflow Documentation](../kubeflow/README.md)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)

### KServe

- [KServe Documentation](../kserve/README.md)
- [KServe Examples](https://github.com/kserve/kserve/tree/master/docs/samples)

### Airflow

- [Airflow Documentation](../../data/airflow/README.md)
- [Airflow + MLflow Integration](https://mlflow.org/docs/latest/tracking.html#airflow-integration)

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: ML Engineering Team  
**Última actualización**: 2024
