# Entrenamiento

Coloque sus notebooks/scripts de entrenamiento aquí.

Recomendado:
- Use MLflow para el tracking de experimentos (vea `ml/mlflow/values.yaml`).
- Guarde artefactos en el data lake (S3/ADLS) y registre el modelo para servirlo con KServe.

Ejemplo (Python):

```python
import mlflow
mlflow.set_tracking_uri("http://mlflow.example.com")
mlflow.set_experiment("demo")
with mlflow.start_run():
    mlflow.log_param("lr", 0.01)
    mlflow.log_metric("acc", 0.99)
    mlflow.sklearn.log_model(model, "model")
```
