# Scripts de MLflow

Scripts utilitarios para automatizar tareas comunes de MLflow.

## Scripts Disponibles

### `cleanup_old_runs.py`

Limpia automáticamente runs antiguos de MLflow según políticas de retención configurables.

#### Uso Básico

```bash
# Limpiar todos los experimentos (dry-run primero)
python cleanup_old_runs.py --dry-run

# Limpiar con retención de 90 días
python cleanup_old_runs.py --retention-days 90 --delete-failed

# Limpiar experimento específico
python cleanup_old_runs.py --experiment "mi-experimento" --retention-days 60

# Mantener al menos 20 runs por experimento
python cleanup_old_runs.py --min-runs-to-keep 20
```

#### Opciones

- `--tracking-uri`: URI del servidor MLflow (default: `MLFLOW_TRACKING_URI` env var)
- `--experiment`: Nombre o ID del experimento específico (opcional)
- `--retention-days`: Días de retención (default: 90)
- `--delete-failed`: Eliminar también runs fallidos
- `--min-runs-to-keep`: Mínimo de runs a mantener (default: 10)
- `--delete-artifacts`: También eliminar artefactos de S3
- `--dry-run`: Solo mostrar qué se eliminaría sin hacer cambios

#### Ejemplo con Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mlflow-cleanup
  namespace: ml
spec:
  schedule: "0 2 * * *"  # 2 AM diario
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: python:3.10
            command:
            - /bin/sh
            - -c
            - |
              pip install mlflow boto3
              python /scripts/cleanup_old_runs.py \
                --tracking-uri http://mlflow.ml.svc.cluster.local \
                --retention-days 90 \
                --delete-failed \
                --min-runs-to-keep 10
            env:
            - name: MLFLOW_TRACKING_URI
              value: "http://mlflow.ml.svc.cluster.local"
            volumeMounts:
            - name: scripts
              mountPath: /scripts
          volumes:
          - name: scripts
            configMap:
              name: mlflow-scripts
          restartPolicy: OnFailure
```

#### Ejemplo con Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

def cleanup_mlflow():
    subprocess.run([
        "python", "/path/to/cleanup_old_runs.py",
        "--tracking-uri", "http://mlflow.example.com",
        "--retention-days", "90",
        "--delete-failed",
        "--min-runs-to-keep", "10"
    ])

dag = DAG(
    'mlflow_cleanup',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_runs',
    python_callable=cleanup_mlflow,
    dag=dag
)
```

#### `export_experiments.py`

Exporta experimentos de MLflow a JSON o CSV para backup o migración.

##### Uso

```bash
# Exportar todos los experimentos a JSON
python export_experiments.py --output-dir ./exports

# Exportar experimento específico a CSV
python export_experiments.py --experiment "mi-experimento" --format csv

# Exportar a ambos formatos
python export_experiments.py --format both
```

##### Opciones

- `--tracking-uri`: URI del servidor MLflow
- `--experiment`: Nombre o ID del experimento (opcional)
- `--output-dir`: Directorio de salida (default: ./mlflow_exports)
- `--format`: Formato de exportación (json | csv | both)

## Instalación

```bash
# Instalar dependencias
pip install mlflow boto3 pandas

# Hacer ejecutables
chmod +x cleanup_old_runs.py
chmod +x export_experiments.py
```

## Seguridad

- El script requiere permisos de lectura/escritura en MLflow
- Para eliminar artefactos de S3, necesita permisos `s3:DeleteObject`
- Usa Service Account con permisos mínimos necesarios en Kubernetes

## Troubleshooting

### Error: "MLflow no está instalado"
```bash
pip install mlflow
```

### Error: "No se pudo conectar a MLflow"
- Verifica que `MLFLOW_TRACKING_URI` esté configurado correctamente
- Verifica conectividad de red desde donde ejecutas el script
- Verifica que el servidor MLflow esté corriendo

### Error: "Permission denied"
- Verifica permisos del usuario/Service Account
- Para S3, verifica IAM roles/policies

