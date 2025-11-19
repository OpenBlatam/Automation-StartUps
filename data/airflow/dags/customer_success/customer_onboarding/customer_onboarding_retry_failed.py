from __future__ import annotations

from datetime import timedelta
import logging
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    dag_id="customer_onboarding_retry_failed",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "sales-operations",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    doc_md="""
    ### Customer Onboarding Retry Failed
    
    Reintenta automáticamente onboardings que fallaron o servicios que no se activaron.
    Revisa onboardings en estado 'failed' o servicios con 'account_status = failed'
    y los reintenta según criterios configurados.
    """,
    tags=["onboarding", "retry", "customer"],
)
def customer_onboarding_retry_failed() -> None:
    @task(task_id="identify_failed_onboardings")
    def identify_failed_onboardings() -> list:
        """Identificar onboardings fallidos que pueden reintentarse."""
        try:
            pg_hook = PostgresHook(postgres_conn_id="postgres_default")
            
            # Onboardings en estado failed que no sean muy antiguos (últimos 7 días)
            sql = """
                SELECT 
                    customer_email,
                    status,
                    onboarding_started_at,
                    identity_verification_status,
                    id
                FROM customer_onboarding
                WHERE status = 'failed'
                  AND onboarding_started_at >= NOW() - INTERVAL '7 days'
                ORDER BY onboarding_started_at DESC
                LIMIT 50
            """
            
            results = pg_hook.get_records(sql)
            failed_onboardings = [
                {
                    "customer_email": row[0],
                    "status": row[1],
                    "started_at": row[2].isoformat() if row[2] else None,
                    "identity_status": row[3],
                    "onboarding_id": row[4]
                }
                for row in results
            ]
            
            logger.info(f"Found {len(failed_onboardings)} failed onboardings to retry")
            return failed_onboardings
            
        except Exception as e:
            logger.error("Failed to identify failed onboardings", exc_info=True)
            return []
    
    @task(task_id="identify_failed_services")
    def identify_failed_services() -> list:
        """Identificar servicios que fallaron al activarse."""
        try:
            pg_hook = PostgresHook(postgres_conn_id="postgres_default")
            
            # Servicios con estado failed
            sql = """
                SELECT 
                    ca.customer_email,
                    ca.service_name,
                    ca.account_status,
                    ca.error_message,
                    ca.activation_requested_at,
                    co.status as onboarding_status,
                    co.identity_verified
                FROM customer_accounts ca
                JOIN customer_onboarding co ON ca.customer_email = co.customer_email
                WHERE ca.account_status = 'failed'
                  AND ca.activation_requested_at >= NOW() - INTERVAL '7 days'
                  AND co.status != 'rejected'
                  AND co.identity_verified = TRUE
                ORDER BY ca.activation_requested_at DESC
                LIMIT 100
            """
            
            results = pg_hook.get_records(sql)
            failed_services = [
                {
                    "customer_email": row[0],
                    "service_name": row[1],
                    "account_status": row[2],
                    "error_message": row[3],
                    "requested_at": row[4].isoformat() if row[4] else None,
                    "onboarding_status": row[5],
                    "identity_verified": row[6]
                }
                for row in results
            ]
            
            logger.info(f"Found {len(failed_services)} failed services to retry")
            return failed_services
            
        except Exception as e:
            logger.error("Failed to identify failed services", exc_info=True)
            return []
    
    @task(task_id="retry_failed_services")
    def retry_failed_services(failed_services: list) -> Dict[str, Any]:
        """Reintentar activación de servicios fallidos."""
        from data.airflow.plugins.customer_onboarding_integrations import activate_customer_accounts
        
        retried = 0
        succeeded = 0
        failed = 0
        
        for service_info in failed_services[:20]:  # Limitar a 20 por ejecución
            try:
                customer_email = service_info["customer_email"]
                service_name = service_info["service_name"]
                
                logger.info(f"Retrying service activation", extra={
                    "customer_email": customer_email,
                    "service_name": service_name
                })
                
                # Obtener datos del cliente
                pg_hook = PostgresHook(postgres_conn_id="postgres_default")
                customer_sql = """
                    SELECT 
                        customer_email, first_name, last_name, company_name,
                        service_plan, service_tier, services_to_activate
                    FROM customer_onboarding
                    WHERE customer_email = %s
                    LIMIT 1
                """
                customer_data = pg_hook.get_first(customer_sql, parameters=(customer_email,))
                
                if customer_data:
                    payload = {
                        "customer_email": customer_data[0],
                        "first_name": customer_data[1],
                        "last_name": customer_data[2],
                        "company_name": customer_data[3],
                        "service_plan": customer_data[4],
                        "service_tier": customer_data[5],
                        "services_to_activate": [service_name],
                        "identity_verified": service_info["identity_verified"]
                    }
                    
                    result = activate_customer_accounts(payload)
                    
                    if service_name in result.get("accounts_activated", []):
                        succeeded += 1
                        logger.info(f"Service retry succeeded", extra={
                            "customer_email": customer_email,
                            "service_name": service_name
                        })
                    else:
                        failed += 1
                    
                    retried += 1
                
            except Exception as e:
                logger.error(f"Failed to retry service", exc_info=True, extra={
                    "customer_email": service_info.get("customer_email"),
                    "service_name": service_info.get("service_name")
                })
                failed += 1
        
        return {
            "retried": retried,
            "succeeded": succeeded,
            "failed": failed
        }
    
    @task(task_id="notify_results")
    def notify_results(retry_results: Dict[str, Any]) -> None:
        """Notificar resultados de los reintentos."""
        try:
            message = f"""
🔄 *Customer Onboarding Retry Results*

*Services Retried:*
• Total: {retry_results['retried']}
• Succeeded: {retry_results['succeeded']}
• Failed: {retry_results['failed']}
"""
            notify_slack(message)
        except Exception as e:
            logger.warning(f"Failed to send notification: {e}")
    
    # Pipeline
    failed_services = identify_failed_services()
    retry_results = retry_failed_services(failed_services)
    notify_results(retry_results)


customer_onboarding_retry_failed_dag = customer_onboarding_retry_failed()

