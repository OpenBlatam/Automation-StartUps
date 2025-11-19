"""
MLflow Cleanup DAG - Limpieza automática de runs antiguos

Ejecuta el script de limpieza de MLflow para mantener el sistema optimizado.
Elimina runs antiguos según políticas de retención configuradas.

Schedule: @weekly (domingos a las 2 AM)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.models import Variable
from airflow.utils.context import get_current_context
from airflow.operators.bash import BashOperator
import pendulum

logger = logging.getLogger(__name__)


def _get_env_var(key: str, default: str = "") -> str:
    """Obtiene variable de entorno o Airflow Variable."""
    return os.getenv(key) or Variable.get(key, default_var=default)


@dag(
    dag_id="mlflow_cleanup",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 2 * * 0",  # Domingos a las 2 AM
    catchup=False,
    default_args={
        "owner": "ml-team",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### MLflow Cleanup - Limpieza Automática
    
    Limpia runs antiguos de MLflow automáticamente para optimizar almacenamiento.
    
    **Funcionalidades:**
    - Elimina runs más antiguos que el período de retención
    - Respeta mínimo de runs a mantener por experimento
    - Opcionalmente elimina artefactos de S3
    - Logging completo de operaciones
    
    **Parámetros:**
    - `retention_days`: Días de retención (default: 90)
    - `delete_failed`: Eliminar runs fallidos (default: true)
    - `min_runs_to_keep`: Mínimo de runs a mantener (default: 10)
    - `delete_artifacts`: También eliminar artefactos de S3 (default: false)
    - `experiment`: Experimento específico o vacío para todos
    - `dry_run`: Solo simular sin eliminar (default: false)
    
    **Requisitos:**
    - Script cleanup_old_runs.py disponible en PATH
    - MLFLOW_TRACKING_URI configurado
    - Permisos de lectura/escritura en MLflow
    """,
    params={
        "retention_days": 90,
        "delete_failed": True,
        "min_runs_to_keep": 10,
        "delete_artifacts": False,
        "experiment": "",  # Vacío = todos los experimentos
        "dry_run": False,
    },
    tags=["ml", "mlflow", "cleanup", "maintenance"],
)
def mlflow_cleanup() -> None:
    """
    DAG de limpieza automática de MLflow.
    """
    
    @task(task_id="cleanup_runs")
    def cleanup_runs(**kwargs) -> dict:
        """Ejecuta script de limpieza."""
        ctx = get_current_context()
        params = ctx["params"]
        
        tracking_uri = _get_env_var("MLFLOW_TRACKING_URI", "http://mlflow.ml.svc.cluster.local")
        retention_days = int(params.get("retention_days", 90))
        delete_failed = bool(params.get("delete_failed", True))
        min_runs = int(params.get("min_runs_to_keep", 10))
        delete_artifacts = bool(params.get("delete_artifacts", False))
        experiment = str(params.get("experiment", "")).strip()
        dry_run = bool(params.get("dry_run", False))
        
        logger.info(
            f"Starting MLflow cleanup",
            extra={
                "tracking_uri": tracking_uri,
                "retention_days": retention_days,
                "delete_failed": delete_failed,
                "min_runs_to_keep": min_runs,
                "experiment": experiment or "all",
                "dry_run": dry_run,
            },
        )
        
        # Construir comando
        script_path = os.path.join(
            os.path.dirname(__file__),
            "../../ml/mlflow/scripts/cleanup_old_runs.py"
        )
        
        if not os.path.exists(script_path):
            # Intentar ruta alternativa
            script_path = "ml/mlflow/scripts/cleanup_old_runs.py"
            if not os.path.exists(script_path):
                raise AirflowFailException(
                    f"Cleanup script not found at {script_path}. "
                    "Ensure ml/mlflow/scripts/cleanup_old_runs.py exists."
                )
        
        cmd_parts = [
            "python",
            script_path,
            "--tracking-uri", tracking_uri,
            "--retention-days", str(retention_days),
            "--min-runs-to-keep", str(min_runs),
        ]
        
        if delete_failed:
            cmd_parts.append("--delete-failed")
        
        if delete_artifacts:
            cmd_parts.append("--delete-artifacts")
        
        if experiment:
            cmd_parts.extend(["--experiment", experiment])
        
        if dry_run:
            cmd_parts.append("--dry-run")
        
        cmd = " ".join(cmd_parts)
        
        logger.info(f"Executing: {cmd}")
        
        import subprocess
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            logger.error(f"Cleanup failed: {result.stderr}")
            raise AirflowFailException(f"Cleanup script failed: {result.stderr}")
        
        logger.info(f"Cleanup completed: {result.stdout}")
        
        # Parsear resultados si es posible
        return {
            "success": True,
            "output": result.stdout,
            "retention_days": retention_days,
            "dry_run": dry_run,
        }
    
    @task(task_id="notify_cleanup")
    def notify_cleanup(cleanup_result: dict) -> None:
        """Notifica resultados de limpieza."""
        from data.airflow.plugins.etl_notifications import notify_slack
        
        retention_days = cleanup_result.get("retention_days", 90)
        dry_run = cleanup_result.get("dry_run", False)
        success = cleanup_result.get("success", False)
        
        if success:
            prefix = "🔍 DRY RUN: " if dry_run else "✅ "
            message = (
                f"{prefix}Limpieza de MLflow completada\n"
                f"Retention: {retention_days} días\n"
                f"Ver logs para detalles"
            )
        else:
            message = (
                f"❌ Error en limpieza de MLflow\n"
                f"Ver logs para detalles"
            )
        
        try:
            notify_slack(message, dag_id="mlflow_cleanup")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
    
    # Pipeline
    result = cleanup_runs()
    notify_cleanup(result)
    
    return None


# Ejecutar DAG
mlflow_cleanup()

