from __future__ import annotations

from datetime import timedelta
import logging
import json
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    dag_id="customer_onboarding_webhook",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger only
    catchup=False,
    default_args={
        "owner": "sales-operations",
        "retries": 0,
        "retry_delay": timedelta(minutes=1),
        "depends_on_past": False,
    },
    doc_md="""
    ### Customer Onboarding Webhook Handler
    
    Maneja webhooks externos para actualizar el estado del onboarding de clientes.
    
    Soporta:
    - Actualización de estado de verificación de identidad
    - Confirmación de códigos OTP
    - Eventos de servicios externos (KYC providers, etc.)
    - Actualización de datos del cliente
    """,
    params={
        "event_type": "string",
        "customer_email": "string",
        "payload": "object",
    },
    tags=["onboarding", "webhook", "customer"],
    max_active_runs=10,
)
def customer_onboarding_webhook() -> None:
    @task(task_id="process_webhook")
    def process_webhook() -> Dict[str, Any]:
        """Procesar webhook y actualizar estado."""
        context = get_current_context()
        params = context.get("params", {})
        
        event_type = params.get("event_type")
        customer_email = params.get("customer_email")
        payload = params.get("payload", {})
        
        logger.info(
            "Processing webhook",
            extra={
                "event_type": event_type,
                "customer_email": customer_email
            }
        )
        
        try:
            pg_hook = PostgresHook(postgres_conn_id="postgres_default")
            
            if event_type == "identity_verification_confirmed":
                # Confirmar verificación de identidad
                verification_code = payload.get("verification_code")
                
                # Buscar verificación pendiente
                check_sql = """
                    SELECT id, verification_code, expires_at
                    FROM customer_identity_verifications
                    WHERE customer_email = %s
                      AND verification_type = %s
                      AND verification_status = 'pending'
                      AND verification_code = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                
                verification_method = payload.get("verification_method", "email")
                result = pg_hook.get_first(
                    check_sql,
                    parameters=(customer_email, verification_method, verification_code)
                )
                
                if result:
                    verification_id, stored_code, expires_at = result
                    
                    # Verificar que no haya expirado
                    from datetime import datetime, timezone
                    if expires_at and expires_at > datetime.now(timezone.utc):
                        # Actualizar verificación
                        update_sql = """
                            UPDATE customer_identity_verifications
                            SET verification_status = 'verified',
                                verified_at = NOW(),
                                updated_at = NOW()
                            WHERE id = %s
                        """
                        pg_hook.run(update_sql, parameters=(verification_id,))
                        
                        # Actualizar estado del onboarding
                        onboarding_sql = """
                            UPDATE customer_onboarding
                            SET identity_verified = TRUE,
                                identity_verification_status = 'verified',
                                identity_verified_at = NOW(),
                                status = 'activating_services',
                                updated_at = NOW()
                            WHERE customer_email = %s
                        """
                        pg_hook.run(onboarding_sql, parameters=(customer_email,))
                        
                        # Registrar evento
                        event_sql = """
                            INSERT INTO customer_onboarding_events
                            (customer_email, event_type, event_details)
                            VALUES (%s, 'identity_verified', %s::jsonb)
                        """
                        pg_hook.run(event_sql, parameters=(
                            customer_email,
                            json.dumps({
                                "method": verification_method,
                                "verified_at": datetime.now(timezone.utc).isoformat(),
                                "source": "webhook"
                            })
                        ))
                        
                        logger.info("Identity verification confirmed", extra={
                            "customer_email": customer_email,
                            "verification_id": verification_id
                        })
                    else:
                        logger.warning("Verification code expired", extra={
                            "customer_email": customer_email
                        })
            
            elif event_type == "kyc_provider_result":
                # Resultado de proveedor KYC externo
                kyc_status = payload.get("status")  # verified, rejected, pending
                provider = payload.get("provider")
                provider_response = payload.get("response", {})
                
                # Actualizar verificación
                insert_sql = """
                    INSERT INTO customer_identity_verifications
                    (customer_email, verification_type, verification_provider,
                     verification_status, provider_response, verified_at)
                    VALUES (%s, 'kyc', %s, %s, %s::jsonb, %s)
                    ON CONFLICT DO NOTHING
                """
                
                verified_at = None
                if kyc_status == "verified":
                    from datetime import datetime, timezone
                    verified_at = datetime.now(timezone.utc)
                
                pg_hook.run(insert_sql, parameters=(
                    customer_email,
                    provider,
                    kyc_status,
                    json.dumps(provider_response),
                    verified_at
                ))
                
                # Actualizar estado del onboarding
                if kyc_status == "verified":
                    onboarding_sql = """
                        UPDATE customer_onboarding
                        SET identity_verified = TRUE,
                            identity_verification_status = 'verified',
                            identity_verified_at = NOW(),
                            status = 'activating_services',
                            updated_at = NOW()
                        WHERE customer_email = %s
                    """
                    pg_hook.run(onboarding_sql, parameters=(customer_email,))
                
                elif kyc_status == "rejected":
                    onboarding_sql = """
                        UPDATE customer_onboarding
                        SET identity_verification_status = 'rejected',
                            status = 'rejected',
                            updated_at = NOW()
                        WHERE customer_email = %s
                    """
                    pg_hook.run(onboarding_sql, parameters=(customer_email,))
            
            elif event_type == "service_activated":
                # Servicio activado externamente
                service_name = payload.get("service_name")
                account_id = payload.get("account_id")
                account_data = payload.get("account_data", {})
                
                # Actualizar cuenta
                update_sql = """
                    UPDATE customer_accounts
                    SET account_status = 'active',
                        account_id = %s,
                        activated_at = NOW(),
                        updated_at = NOW(),
                        metadata = %s::jsonb
                    WHERE customer_email = %s
                      AND service_name = %s
                """
                
                pg_hook.run(update_sql, parameters=(
                    account_id,
                    json.dumps(account_data),
                    customer_email,
                    service_name
                ))
                
                logger.info("Service activation confirmed", extra={
                    "customer_email": customer_email,
                    "service_name": service_name
                })
            
            elif event_type == "customer_data_updated":
                # Actualizar datos del cliente
                update_fields = payload.get("data", {})
                
                if update_fields:
                    set_clauses = []
                    params = []
                    
                    for field, value in update_fields.items():
                        if field in ["company_name", "phone", "country", "timezone"]:
                            set_clauses.append(f"{field} = %s")
                            params.append(value)
                    
                    if set_clauses:
                        params.append(customer_email)
                        update_sql = f"""
                            UPDATE customer_onboarding
                            SET {', '.join(set_clauses)}, updated_at = NOW()
                            WHERE customer_email = %s
                        """
                        pg_hook.run(update_sql, parameters=tuple(params))
            
            # Registrar evento del webhook
            event_sql = """
                INSERT INTO customer_onboarding_events
                (customer_email, event_type, event_details, metadata)
                VALUES (%s, %s, %s::jsonb, %s::jsonb)
            """
            
            pg_hook.run(event_sql, parameters=(
                customer_email,
                f"webhook_{event_type}",
                json.dumps(payload),
                json.dumps({"source": "webhook", "received_at": pendulum.now().isoformat()})
            ))
            
            return {
                "status": "success",
                "event_type": event_type,
                "customer_email": customer_email
            }
            
        except Exception as e:
            logger.error("Webhook processing failed", exc_info=True, extra={
                "event_type": event_type,
                "customer_email": customer_email
            })
            raise
    
    process_webhook()


customer_onboarding_webhook_dag = customer_onboarding_webhook()





