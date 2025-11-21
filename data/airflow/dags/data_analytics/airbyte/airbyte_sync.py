"""
DAG para orquestar sincronizaciones de datos con Airbyte.

Este DAG demuestra cómo usar Airflow para orquestar sincronizaciones de Airbyte,
combinando la potencia de Airbyte (600+ conectores) con la orquestación avanzada
de Airflow para flujos de datos complejos.

Ejemplos de uso:
1. Sincronizar datos de Stripe a PostgreSQL
2. Sincronizar datos de HubSpot a Snowflake
3. Ejecutar múltiples sincronizaciones en paralelo
4. Trigger sincronizaciones basadas en eventos (webhooks)
"""

from datetime import datetime, timedelta
from typing import Any
import logging
import json

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.models import Variable
from airflow.exceptions import AirflowException

# Configuración
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# Variables de entorno (configurar en Airflow Variables o secrets)
# AIRBYTE_API_URL: URL del servidor API de Airbyte (ej: http://airbyte-server.integration.svc.cluster.local:8000)
# AIRBYTE_API_USERNAME: Usuario de Airbyte
# AIRBYTE_API_PASSWORD: Password de Airbyte (almacenar en External Secrets)

logger = logging.getLogger(__name__)


def get_airbyte_api_url() -> str:
    """Obtiene la URL de la API de Airbyte desde variables o configuración."""
    api_url = Variable.get("AIRBYTE_API_URL", default_var="http://airbyte-server.integration.svc.cluster.local:8000")
    return api_url.rstrip("/")


def get_airbyte_credentials() -> tuple[str, str]:
    """Obtiene credenciales de Airbyte desde secrets."""
    username = Variable.get("AIRBYTE_API_USERNAME", default_var="airbyte")
    password = Variable.get("AIRBYTE_API_PASSWORD", default_var="password")
    return username, password


class AirbyteHook:
    """
    Hook mejorado para interactuar con la API de Airbyte.
    
    Incluye:
    - Manejo robusto de errores y retries
    - Validación de respuestas
    - Métricas y logging estructurado
    - Soporte para diferentes tipos de jobs
    """
    
    def __init__(self, api_url: str, username: str, password: str, max_retries: int = 3):
        self.api_url = api_url.rstrip("/")
        self.http_hook = HttpHook(http_conn_id=None, method="POST")
        self.auth = (username, password)
        self.max_retries = max_retries
    
    def trigger_sync(
        self, 
        connection_id: str, 
        job_type: str = "sync",
        retry_on_failure: bool = True
    ) -> dict[str, Any]:
        """
        Triggea una sincronización en Airbyte con retries y validación.
        
        Args:
            connection_id: ID de la conexión en Airbyte
            job_type: Tipo de job ("sync", "reset", "sync_clear")
            retry_on_failure: Si debe reintentar en caso de fallo
            
        Returns:
            Información del job de sincronización con jobId
            
        Raises:
            AirflowException: Si falla después de todos los retries
        """
        url = f"{self.api_url}/api/v1/jobs"
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "connectionId": connection_id,
            "jobType": job_type,
        }
        
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Triggering Airbyte {job_type} for connection {connection_id} "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                
                response = self.http_hook.run(
                    endpoint=url,
                    data=json.dumps(payload),
                    headers=headers,
                    extra_options={
                        "auth": self.auth,
                        "timeout": 30,
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Validar respuesta
                if "jobId" not in result and "id" not in result:
                    raise ValueError(f"Invalid response from Airbyte API: {result}")
                
                job_id = result.get("jobId") or result.get("id")
                logger.info(
                    f"Successfully triggered Airbyte job {job_id} "
                    f"for connection {connection_id}"
                )
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed: {e}",
                    exc_info=True
                )
                
                if not retry_on_failure or attempt == self.max_retries:
                    break
                
                # Exponential backoff
                import time
                time.sleep(2 ** attempt)
        
        error_msg = (
            f"Failed to trigger Airbyte {job_type} for connection {connection_id} "
            f"after {self.max_retries} attempts: {last_exception}"
        )
        logger.error(error_msg)
        raise AirflowException(error_msg)
    
    def get_job_status(self, job_id: str) -> dict[str, Any]:
        """
        Obtiene el estado de un job de sincronización.
        
        Args:
            job_id: ID del job
            
        Returns:
            Estado del job con información detallada
            
        Raises:
            AirflowException: Si no se puede obtener el estado
        """
        url = f"{self.api_url}/api/v1/jobs/{job_id}"
        headers = {"Accept": "application/json"}
        
        try:
            response = self.http_hook.run(
                endpoint=url,
                headers=headers,
                method="GET",
                extra_options={
                    "auth": self.auth,
                    "timeout": 30,
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error al obtener estado del job {job_id}: {e}")
            raise AirflowException(f"Failed to get job status for {job_id}: {e}")
    
    def get_connection_info(self, connection_id: str) -> dict[str, Any]:
        """
        Obtiene información de una conexión.
        
        Args:
            connection_id: ID de la conexión
            
        Returns:
            Información de la conexión (source, destination, config, etc.)
        """
        url = f"{self.api_url}/api/v1/connections/get"
        headers = {"Content-Type": "application/json"}
        
        payload = {"connectionId": connection_id}
        
        try:
            response = self.http_hook.run(
                endpoint=url,
                data=json.dumps(payload),
                headers=headers,
                method="POST",
                extra_options={
                    "auth": self.auth,
                    "timeout": 30,
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error al obtener información de conexión {connection_id}: {e}")
            raise AirflowException(f"Failed to get connection info: {e}")
    
    def list_connections(self) -> list[dict[str, Any]]:
        """
        Lista todas las conexiones disponibles.
        
        Returns:
            Lista de conexiones con sus IDs y nombres
        """
        url = f"{self.api_url}/api/v1/connections/list"
        headers = {"Accept": "application/json"}
        
        try:
            response = self.http_hook.run(
                endpoint=url,
                headers=headers,
                method="POST",
                extra_options={
                    "auth": self.auth,
                    "timeout": 30,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Error al listar conexiones: {e}")
            raise AirflowException(f"Failed to list connections: {e}")
    
    def wait_for_job_completion(
        self, 
        job_id: str, 
        timeout_minutes: int = 60,
        check_interval: int = 30
    ) -> dict[str, Any]:
        """
        Espera a que un job de sincronización complete con mejor logging y validación.
        
        Args:
            job_id: ID del job
            timeout_minutes: Tiempo máximo de espera en minutos
            check_interval: Intervalo entre checks en segundos
            
        Returns:
            Estado final del job con estadísticas
            
        Raises:
            AirflowException: Si el job falla o excede el timeout
        """
        import time
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        last_status = None
        
        logger.info(
            f"Waiting for Airbyte job {job_id} to complete "
            f"(timeout: {timeout_minutes} minutes)"
        )
        
        while True:
            try:
                status = self.get_job_status(job_id)
                job_status = status.get("status", "unknown")
                
                # Log solo si cambió el estado
                if job_status != last_status:
                    logger.info(
                        f"Job {job_id} status changed: {last_status} → {job_status}"
                    )
                    last_status = job_status
                
                # Estados finales
                if job_status == "succeeded":
                    elapsed_minutes = (time.time() - start_time) / 60
                    logger.info(
                        f"Job {job_id} completed successfully in {elapsed_minutes:.2f} minutes"
                    )
                    
                    # Extraer estadísticas si están disponibles
                    stats = status.get("stats", {})
                    if stats:
                        logger.info(
                            f"Job {job_id} stats: "
                            f"records={stats.get('records', 'N/A')}, "
                            f"bytes={stats.get('bytes', 'N/A')}"
                        )
                    
                    return status
                    
                elif job_status == "failed":
                    error_msg = status.get("error") or status.get("failureReason", "Unknown error")
                    elapsed_minutes = (time.time() - start_time) / 60
                    
                    logger.error(
                        f"Job {job_id} failed after {elapsed_minutes:.2f} minutes: {error_msg}"
                    )
                    raise AirflowException(
                        f"Airbyte job {job_id} failed: {error_msg}"
                    )
                    
                elif job_status in ["pending", "running", "incomplete"]:
                    elapsed = time.time() - start_time
                    if elapsed > timeout_seconds:
                        elapsed_minutes = elapsed / 60
                        raise AirflowException(
                            f"Airbyte job {job_id} timed out after "
                            f"{elapsed_minutes:.2f} minutes (status: {job_status})"
                        )
                    
                    # Log progreso cada 2 minutos
                    if int(elapsed) % 120 == 0:
                        elapsed_minutes = elapsed / 60
                        logger.info(
                            f"Job {job_id} still running "
                            f"({elapsed_minutes:.1f}/{timeout_minutes} minutes elapsed)"
                        )
                    
                    time.sleep(check_interval)
                    
                elif job_status == "cancelled":
                    raise AirflowException(f"Airbyte job {job_id} was cancelled")
                    
                else:
                    raise AirflowException(
                        f"Unknown or unexpected job status '{job_status}' for job {job_id}"
                    )
                    
            except AirflowException:
                raise
            except Exception as e:
                logger.warning(f"Error checking job status (will retry): {e}")
                time.sleep(check_interval)


def trigger_airbyte_sync(
    connection_id: str,
    task_instance: Any,
    timeout_minutes: int = 120,
    validate_connection: bool = True,
    **context: Any
) -> str:
    """
    Triggea una sincronización de Airbyte y espera a que complete.
    
    Args:
        connection_id: ID de la conexión en Airbyte
        task_instance: Instancia de la tarea (Airflow)
        timeout_minutes: Tiempo máximo de espera (default: 120)
        validate_connection: Si debe validar que la conexión existe antes de sync
        
    Returns:
        Job ID de la sincronización
        
    Raises:
        AirflowException: Si falla la sincronización o validación
    """
    api_url = get_airbyte_api_url()
    username, password = get_airbyte_credentials()
    
    hook = AirbyteHook(api_url, username, password)
    
    # Validar conexión si está habilitado
    if validate_connection:
        try:
            conn_info = hook.get_connection_info(connection_id)
            logger.info(
                f"Validated connection {connection_id}: "
                f"source={conn_info.get('sourceId')}, "
                f"destination={conn_info.get('destinationId')}"
            )
        except Exception as e:
            logger.error(f"Connection {connection_id} validation failed: {e}")
            raise AirflowException(f"Invalid Airbyte connection {connection_id}: {e}")
    
    logger.info(f"Triggering Airbyte sync for connection {connection_id}")
    
    try:
        job_info = hook.trigger_sync(connection_id)
        job_id = job_info.get("jobId") or job_info.get("id")
        
        if not job_id:
            raise AirflowException(f"No job ID returned from Airbyte: {job_info}")
        
        logger.info(f"Started Airbyte job {job_id} for connection {connection_id}")
        
        # Guardar información en XCom para referencia
        task_instance.xcom_push(key="airbyte_job_id", value=job_id)
        task_instance.xcom_push(key="airbyte_connection_id", value=connection_id)
        task_instance.xcom_push(key="airbyte_start_time", value=datetime.now().isoformat())
        
        # Esperar a que complete
        final_status = hook.wait_for_job_completion(job_id, timeout_minutes=timeout_minutes)
        
        # Guardar estadísticas finales
        stats = final_status.get("stats", {})
        task_instance.xcom_push(key="airbyte_records", value=stats.get("records", 0))
        task_instance.xcom_push(key="airbyte_bytes", value=stats.get("bytes", 0))
        task_instance.xcom_push(key="airbyte_end_time", value=datetime.now().isoformat())
        
        logger.info(
            f"Airbyte sync {job_id} completed successfully. "
            f"Records: {stats.get('records', 'N/A')}, "
            f"Bytes: {stats.get('bytes', 'N/A')}"
        )
        
        return job_id
        
    except AirflowException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Airbyte sync: {e}", exc_info=True)
        raise AirflowException(f"Failed to complete Airbyte sync: {e}")


def check_airbyte_health(**context: Any) -> None:
    """Verifica que el servicio de Airbyte esté disponible."""
    api_url = get_airbyte_api_url()
    username, password = get_airbyte_credentials()
    
    hook = HttpHook(http_conn_id=None, method="GET")
    
    try:
        response = hook.run(
            endpoint=f"{api_url}/api/v1/health",
            extra_options={
                "auth": (username, password),
                "timeout": 10,
            }
        )
        response.raise_for_status()
        logger.info("Airbyte service is healthy")
    except Exception as e:
        logger.error(f"Airbyte health check failed: {e}")
        raise AirflowException(f"Airbyte service is not available: {e}")


def validate_sync_results(
    task_instance: Any,
    min_records: int = 0,
    **context: Any
) -> None:
    """
    Valida los resultados de una sincronización de Airbyte.
    
    Args:
        task_instance: Instancia de la tarea (Airflow)
        min_records: Número mínimo de registros esperados
        
    Raises:
        AirflowException: Si la validación falla
    """
    job_id = task_instance.xcom_pull(key="airbyte_job_id", task_ids="sync_stripe_to_postgres")
    records = task_instance.xcom_pull(key="airbyte_records", task_ids="sync_stripe_to_postgres") or 0
    
    if not job_id:
        raise AirflowException("No job ID found in XCom. Sync may not have completed.")
    
    logger.info(f"Validating sync results for job {job_id}: {records} records")
    
    if records < min_records:
        raise AirflowException(
            f"Sync validation failed: Expected at least {min_records} records, "
            f"but got {records}"
        )
    
    logger.info(f"Sync validation passed: {records} records >= {min_records} minimum")


# DAG: Sincronización de Stripe a PostgreSQL
with DAG(
    dag_id="airbyte_stripe_to_postgres",
    description="Sincroniza datos de Stripe hacia PostgreSQL usando Airbyte",
    default_args=default_args,
    schedule_interval=timedelta(hours=6),  # Cada 6 horas
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["airbyte", "stripe", "postgres", "data-sync"],
) as stripe_dag:
    
    # Health check
    health_check = PythonOperator(
        task_id="check_airbyte_health",
        python_callable=check_airbyte_health,
    )
    
    # Sincronización Stripe -> PostgreSQL
    # Nota: Reemplazar CONNECTION_ID con el ID real de tu conexión en Airbyte
    stripe_sync = PythonOperator(
        task_id="sync_stripe_to_postgres",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID", default_var="changeme"),
            "timeout_minutes": 180,  # 3 horas para sincronizaciones grandes
            "validate_connection": True,
        },
    )
    
    # Validación post-sync (opcional)
    validate_sync = PythonOperator(
        task_id="validate_sync_results",
        python_callable=validate_sync_results,
        op_kwargs={
            "min_records": 1,  # Validar que al menos se sincronizó 1 registro
        },
    )
    
    health_check >> stripe_sync >> validate_sync


# DAG: Sincronización de múltiples fuentes en paralelo
with DAG(
    dag_id="airbyte_multi_source_sync",
    description="Sincroniza datos de múltiples fuentes usando Airbyte en paralelo",
    default_args=default_args,
    schedule_interval=timedelta(hours=12),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["airbyte", "multi-source", "data-sync"],
) as multi_source_dag:
    
    health_check = PythonOperator(
        task_id="check_airbyte_health",
        python_callable=check_airbyte_health,
    )
    
    # Múltiples sincronizaciones en paralelo
    # Ejemplo: sincronizar Stripe, HubSpot, y Salesforce simultáneamente
    
    stripe_sync = PythonOperator(
        task_id="sync_stripe",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_CONNECTION_ID", default_var="changeme"),
        },
    )
    
    hubspot_sync = PythonOperator(
        task_id="sync_hubspot",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_HUBSPOT_CONNECTION_ID", default_var="changeme"),
        },
    )
    
    salesforce_sync = PythonOperator(
        task_id="sync_salesforce",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_SALESFORCE_CONNECTION_ID", default_var="changeme"),
        },
    )
    
    # Todas las sincronizaciones se ejecutan en paralelo después del health check
    health_check >> [stripe_sync, hubspot_sync, salesforce_sync]


# DAG: Sincronización condicional basada en eventos
with DAG(
    dag_id="airbyte_event_driven_sync",
    description="Triggea sincronizaciones de Airbyte basadas en eventos",
    default_args=default_args,
    schedule_interval=None,  # Trigger manual o por webhook
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["airbyte", "event-driven", "webhook"],
) as event_driven_dag:
    
    health_check = PythonOperator(
        task_id="check_airbyte_health",
        python_callable=check_airbyte_health,
    )
    
    # Esta tarea puede ser triggerada manualmente con parámetros
    # o por un webhook que recibe el connection_id como parámetro
    dynamic_sync = PythonOperator(
        task_id="sync_from_event",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": "{{ dag_run.conf.get('connection_id', 'changeme') }}",
        },
    )
    
    health_check >> dynamic_sync

