"""
Ejemplos avanzados de integración Airbyte con Airflow.

Incluye:
- Sincronizaciones condicionales
- Reset de conexiones
- Validación con Great Expectations
- Notificaciones personalizadas
- Sincronizaciones en cadena con dependencias
"""

from datetime import datetime, timedelta
from typing import Any
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.exceptions import AirflowException
from airflow.utils.email import send_email

from data.airflow.dags.airbyte_sync import (
    AirbyteHook,
    get_airbyte_api_url,
    get_airbyte_credentials,
    check_airbyte_health,
    trigger_airbyte_sync,
)

logger = logging.getLogger(__name__)

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def reset_airbyte_connection(
    connection_id: str,
    task_instance: Any,
    **context: Any
) -> str:
    """
    Resetea una conexión de Airbyte (limpia datos en destino).
    
    Útil antes de hacer un full refresh o cuando hay problemas de datos.
    """
    api_url = get_airbyte_api_url()
    username, password = get_airbyte_credentials()
    
    hook = AirbyteHook(api_url, username, password)
    
    logger.info(f"Resetting Airbyte connection {connection_id}")
    
    job_info = hook.trigger_sync(connection_id, job_type="reset")
    job_id = job_info.get("jobId") or job_info.get("id")
    
    if not job_id:
        raise AirflowException(f"No job ID returned from reset: {job_info}")
    
    # Esperar a que complete
    final_status = hook.wait_for_job_completion(job_id, timeout_minutes=60)
    
    logger.info(f"Reset completed for connection {connection_id}")
    task_instance.xcom_push(key="reset_job_id", value=job_id)
    
    return job_id


def conditional_sync(
    connection_id: str,
    condition_check: Any,
    task_instance: Any,
    **context: Any
) -> str:
    """
    Ejecuta sincronización solo si se cumple una condición.
    
    Args:
        connection_id: ID de la conexión
        condition_check: Función que retorna True/False
    """
    # Ejemplo: Solo sincronizar si hay nuevos datos
    should_sync = condition_check()
    
    if not should_sync:
        logger.info(f"Skipping sync for {connection_id}: condition not met")
        return "skipped"
    
    return trigger_airbyte_sync(connection_id, task_instance, **context)


def notify_sync_completion(
    task_instance: Any,
    success: bool = True,
    **context: Any
) -> None:
    """Envía notificación personalizada al completar sincronización."""
    job_id = task_instance.xcom_pull(key="airbyte_job_id")
    connection_id = task_instance.xcom_pull(key="airbyte_connection_id")
    records = task_instance.xcom_pull(key="airbyte_records") or 0
    
    if success:
        subject = f"✅ Airbyte Sync Completed: {connection_id}"
        body = f"""
        Airbyte synchronization completed successfully!
        
        Job ID: {job_id}
        Connection: {connection_id}
        Records synced: {records}
        
        View in Airbyte: https://airbyte.example.com/connections/{connection_id}
        """
    else:
        subject = f"❌ Airbyte Sync Failed: {connection_id}"
        body = f"""
        Airbyte synchronization failed!
        
        Job ID: {job_id}
        Connection: {connection_id}
        
        Check logs for details.
        """
    
    # Enviar email (requiere configuración SMTP)
    try:
        send_email(
            to=Variable.get("ALERT_EMAILS", default_var="").split(","),
            subject=subject,
            html_content=body,
        )
        logger.info(f"Notification sent for sync {job_id}")
    except Exception as e:
        logger.warning(f"Failed to send notification: {e}")


def validate_with_great_expectations(
    task_instance: Any,
    **context: Any
) -> None:
    """
    Valida datos sincronizados usando Great Expectations.
    
    Requiere configuración de Great Expectations en el proyecto.
    """
    job_id = task_instance.xcom_pull(key="airbyte_job_id")
    connection_id = task_instance.xcom_pull(key="airbyte_connection_id")
    
    logger.info(f"Validating data for sync {job_id} with Great Expectations")
    
    # Aquí iría la lógica de validación con Great Expectations
    # Ejemplo:
    # from airflow.providers.great_expectations.operators.great_expectations import GreatExpectationsOperator
    # 
    # validate_task = GreatExpectationsOperator(
    #     task_id="validate_data",
    #     data_context_root_dir="/opt/airflow/gx",
    #     checkpoint_name="post_sync_checkpoint",
    #     ...
    # )
    
    logger.info(f"Validation completed for sync {job_id}")


# DAG: Sincronización con reset previo
with DAG(
    dag_id="airbyte_reset_and_sync",
    description="Resetea conexión y luego sincroniza (full refresh)",
    default_args=default_args,
    schedule_interval=None,  # Manual trigger
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["airbyte", "reset", "full-refresh"],
) as reset_dag:
    
    health_check = PythonOperator(
        task_id="check_airbyte_health",
        python_callable=check_airbyte_health,
    )
    
    # Reset connection
    reset_task = PythonOperator(
        task_id="reset_connection",
        python_callable=reset_airbyte_connection,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID", default_var="changeme"),
        },
    )
    
    # Sync after reset
    sync_task = PythonOperator(
        task_id="sync_after_reset",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID", default_var="changeme"),
        },
    )
    
    # Notify
    notify_task = PythonOperator(
        task_id="notify_completion",
        python_callable=notify_sync_completion,
        op_kwargs={"success": True},
    )
    
    health_check >> reset_task >> sync_task >> notify_task


# DAG: Múltiples sincronizaciones en cadena
with DAG(
    dag_id="airbyte_chained_syncs",
    description="Sincroniza múltiples fuentes en cadena (una después de otra)",
    default_args=default_args,
    schedule_interval=timedelta(hours=12),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["airbyte", "chained", "sequential"],
) as chained_dag:
    
    health_check = PythonOperator(
        task_id="check_airbyte_health",
        python_callable=check_airbyte_health,
    )
    
    # Primero: Stripe
    stripe_sync = PythonOperator(
        task_id="sync_stripe",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_CONNECTION_ID", default_var="changeme"),
        },
    )
    
    # Segundo: HubSpot (después de Stripe)
    hubspot_sync = PythonOperator(
        task_id="sync_hubspot",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_HUBSPOT_CONNECTION_ID", default_var="changeme"),
        },
    )
    
    # Tercero: Salesforce (después de HubSpot)
    salesforce_sync = PythonOperator(
        task_id="sync_salesforce",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_SALESFORCE_CONNECTION_ID", default_var="changeme"),
        },
    )
    
    # Validación final
    validate_all = PythonOperator(
        task_id="validate_all_syncs",
        python_callable=validate_with_great_expectations,
    )
    
    health_check >> stripe_sync >> hubspot_sync >> salesforce_sync >> validate_all


# DAG: Sincronización condicional basada en eventos
with DAG(
    dag_id="airbyte_conditional_sync",
    description="Sincroniza solo si se cumplen condiciones específicas",
    default_args=default_args,
    schedule_interval=timedelta(hours=6),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["airbyte", "conditional", "event-driven"],
) as conditional_dag:
    
    def check_if_new_data():
        """Ejemplo: Verificar si hay nuevos datos para sincronizar."""
        # Aquí iría lógica para verificar (ej: consultar API, verificar timestamps, etc.)
        # Por ahora retornamos True siempre
        return True
    
    health_check = PythonOperator(
        task_id="check_airbyte_health",
        python_callable=check_airbyte_health,
    )
    
    conditional_sync_task = PythonOperator(
        task_id="conditional_sync",
        python_callable=conditional_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID", default_var="changeme"),
            "condition_check": check_if_new_data,
        },
    )
    
    health_check >> conditional_sync_task





