"""
DAG para Detectar Firmas de Contratos y Activar Servicios Automáticamente
Monitorea contratos pendientes de firma y activa servicios cuando se recibe la firma
"""

from __future__ import annotations

from datetime import timedelta, datetime
import logging
import os
import json
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Integraciones de contratos
from data.airflow.plugins.contract_integrations import (
    check_contract_signature_status,
)

# Callbacks y notificaciones
from data.airflow.plugins.etl_callbacks import on_task_failure, sla_miss_callback
from data.airflow.plugins.etl_notifications import notify_slack

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore


CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")
MAX_ACTIVE_TASKS = int(os.getenv("MAX_ACTIVE_TASKS", "32"))


def activate_customer_services(
    customer_email: str,
    services_to_activate: List[str],
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Activa servicios para un cliente después de que el contrato es firmado.
    
    Args:
        customer_email: Email del cliente
        services_to_activate: Lista de servicios a activar
        contract_id: ID del contrato firmado
        postgres_conn_id: Connection ID de Airflow para PostgreSQL
        
    Returns:
        Dict con información de servicios activados
    """
    logger = logging.getLogger("airflow.task")
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    activated_services = []
    failed_services = []
    
    for service in services_to_activate:
        try:
            # Activar servicio según tipo
            if service == "api_access":
                # Crear API key para el cliente
                api_key_result = pg_hook.get_first("""
                    SELECT api_key FROM customer_api_keys 
                    WHERE customer_email = %s AND is_active = true
                    LIMIT 1
                """, parameters=(customer_email,))
                
                if not api_key_result:
                    # Generar nuevo API key
                    import secrets
                    api_key = f"sk_{secrets.token_urlsafe(32)}"
                    pg_hook.run("""
                        INSERT INTO customer_api_keys (customer_email, api_key, is_active, created_at)
                        VALUES (%s, %s, true, NOW())
                        ON CONFLICT (customer_email) DO UPDATE SET
                            api_key = EXCLUDED.api_key,
                            is_active = true,
                            updated_at = NOW()
                    """, parameters=(customer_email, api_key))
                    logger.info(f"API key generado para {customer_email}")
            
            elif service == "dashboard":
                # Activar acceso al dashboard
                pg_hook.run("""
                    UPDATE customer_onboarding
                    SET metadata = jsonb_set(
                        COALESCE(metadata, '{}'::jsonb),
                        '{dashboard_access}',
                        'true'::jsonb
                    ),
                    updated_at = NOW()
                    WHERE customer_email = %s
                """, parameters=(customer_email,))
                logger.info(f"Acceso al dashboard activado para {customer_email}")
            
            elif service == "support":
                # Crear cuenta de soporte
                pg_hook.run("""
                    UPDATE customer_onboarding
                    SET metadata = jsonb_set(
                        COALESCE(metadata, '{}'::jsonb),
                        '{support_access}',
                        'true'::jsonb
                    ),
                    updated_at = NOW()
                    WHERE customer_email = %s
                """, parameters=(customer_email,))
                logger.info(f"Cuenta de soporte activada para {customer_email}")
            
            # Registrar en tabla de servicios activados (si existe)
            try:
                pg_hook.run("""
                    INSERT INTO customer_services (customer_email, service_name, contract_id, activated_at, status)
                    VALUES (%s, %s, %s, NOW(), 'active')
                    ON CONFLICT (customer_email, service_name) DO UPDATE SET
                        contract_id = EXCLUDED.contract_id,
                        activated_at = NOW(),
                        status = 'active',
                        updated_at = NOW()
                """, parameters=(customer_email, service, contract_id))
            except Exception:
                # Si la tabla no existe, continuar sin error
                pass
            
            activated_services.append(service)
            
        except Exception as e:
            logger.error(f"Error activando servicio {service} para {customer_email}: {e}")
            failed_services.append({"service": service, "error": str(e)})
    
    # Registrar evento de activación
    try:
        pg_hook.run("""
            INSERT INTO customer_onboarding_events (customer_email, event_type, event_details)
            VALUES (%s, 'services_activated', %s::jsonb)
        """, parameters=(
            customer_email,
            json.dumps({
                "contract_id": contract_id,
                "activated_services": activated_services,
                "failed_services": failed_services,
                "total_activated": len(activated_services),
                "total_failed": len(failed_services),
            })
        ))
    except Exception:
        pass
    
    return {
        "customer_email": customer_email,
        "contract_id": contract_id,
        "activated_services": activated_services,
        "failed_services": failed_services,
        "success": len(failed_services) == 0,
    }


@dag(
    dag_id="contract_signature_activation",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="*/15 * * * *",  # Cada 15 minutos
    catchup=False,
    default_args={
        "owner": "legal-sales",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Activación Automática de Servicios tras Firma de Contrato
    
    DAG que monitorea contratos pendientes de firma y activa servicios automáticamente
    cuando se detecta que un contrato ha sido firmado.
    
    **Funcionalidades:**
    - ✅ Monitoreo periódico de contratos con estado 'pending_signature'
    - ✅ Verificación de estado de firma con proveedores (DocuSign/PandaDoc)
    - ✅ Detección automática de firmas completadas
    - ✅ Activación automática de servicios configurados
    - ✅ Actualización de estado en base de datos
    - ✅ Notificaciones de activación
    
    **Flujo:**
    1. Buscar contratos con estado 'pending_signature' o 'partially_signed'
    2. Verificar estado actual con proveedor de firma
    3. Si el contrato está 'fully_signed', activar servicios
    4. Actualizar estado del contrato y registrar evento
    
    **Servicios que se pueden activar:**
    - api_access: Genera API keys para el cliente
    - dashboard: Activa acceso al dashboard
    - support: Crea cuenta de soporte
    - Otros servicios personalizados según configuración
    """,
    description="Monitorea firmas de contratos y activa servicios automáticamente",
    tags=["contracts", "legal", "sales", "automation", "activation"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
    max_active_tasks=MAX_ACTIVE_TASKS,
    concurrency=5,
    sla_miss_callback=sla_miss_callback,
    render_template_as_native_obj=True,
    on_success_callback=lambda context: notify_slack(":white_check_mark: contract_signature_activation DAG succeeded"),
    on_failure_callback=lambda context: notify_slack(":x: contract_signature_activation DAG failed"),
)
def contract_signature_activation() -> None:
    logger = logging.getLogger("airflow.task")
    
    @task(task_id="find_pending_contracts", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def find_pending_contracts() -> Dict[str, Any]:
        """Busca contratos pendientes de firma."""
        if Stats:
            try:
                Stats.incr("contract_activation.find_pending.start", 1)
            except Exception:
                pass
        
        pg_hook = PostgresHook(postgres_conn_id=os.getenv("POSTGRES_CONN_ID", "postgres_default"))
        
        # Buscar contratos pendientes de firma
        query = """
            SELECT 
                c.contract_id,
                c.primary_party_email,
                c.primary_party_name,
                c.esignature_provider,
                c.esignature_envelope_id,
                c.esignature_document_id,
                c.status,
                c.metadata,
                co.metadata as onboarding_metadata
            FROM contracts c
            LEFT JOIN customer_onboarding co ON c.primary_party_email = co.customer_email
            WHERE c.status IN ('pending_signature', 'partially_signed')
              AND c.esignature_provider IS NOT NULL
              AND c.esignature_provider != 'manual'
              AND c.created_at > NOW() - INTERVAL '30 days'
            ORDER BY c.created_at DESC
            LIMIT 50
        """
        
        results = pg_hook.get_records(query)
        
        pending_contracts = []
        for row in results:
            pending_contracts.append({
                "contract_id": row[0],
                "customer_email": row[1],
                "customer_name": row[2],
                "esignature_provider": row[3],
                "envelope_id": row[4],
                "document_id": row[5],
                "status": row[6],
                "contract_metadata": row[7] if isinstance(row[7], dict) else json.loads(row[7] or '{}'),
                "onboarding_metadata": row[8] if isinstance(row[8], dict) else json.loads(row[8] or '{}'),
            })
        
        logger.info(
            f"Contratos pendientes encontrados",
            extra={
                "count": len(pending_contracts),
            },
        )
        
        if Stats:
            try:
                Stats.incr("contract_activation.find_pending.success", 1)
                Stats.incr("contract_activation.find_pending.count", len(pending_contracts))
            except Exception:
                pass
        
        return {"pending_contracts": pending_contracts}
    
    @task(task_id="check_contract_signatures", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def check_contract_signatures(data: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica el estado de firma de cada contrato."""
        if Stats:
            try:
                Stats.incr("contract_activation.check_signatures.start", 1)
            except Exception:
                pass
        
        pending_contracts = data.get("pending_contracts", [])
        signed_contracts = []
        
        for contract in pending_contracts:
            contract_id = contract["contract_id"]
            try:
                # Verificar estado con el proveedor
                status_result = check_contract_signature_status(contract_id=contract_id)
                current_status = status_result.get("status")
                
                logger.info(
                    f"Estado de contrato verificado",
                    extra={
                        "contract_id": contract_id,
                        "status": current_status,
                    },
                )
                
                # Si está completamente firmado, agregar a la lista
                if current_status == "fully_signed":
                    signed_contracts.append({
                        **contract,
                        "signature_status_result": status_result,
                        "signed_date": status_result.get("signed_date"),
                    })
                    
            except Exception as e:
                logger.warning(
                    f"Error verificando estado de contrato {contract_id}: {e}",
                    extra={"contract_id": contract_id},
                )
                # Continuar con el siguiente contrato
        
        logger.info(
            f"Contratos firmados detectados",
            extra={
                "count": len(signed_contracts),
            },
        )
        
        if Stats:
            try:
                Stats.incr("contract_activation.check_signatures.success", 1)
                Stats.incr("contract_activation.check_signatures.signed_count", len(signed_contracts))
            except Exception:
                pass
        
        return {"signed_contracts": signed_contracts}
    
    @task(task_id="activate_services_for_signed_contracts", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def activate_services_for_signed_contracts(data: Dict[str, Any]) -> Dict[str, Any]:
        """Activa servicios para contratos que han sido firmados."""
        if Stats:
            try:
                Stats.incr("contract_activation.activate_services.start", 1)
            except Exception:
                pass
        
        signed_contracts = data.get("signed_contracts", [])
        activation_results = []
        
        for contract in signed_contracts:
            contract_id = contract["contract_id"]
            customer_email = contract["customer_email"]
            
            # Obtener servicios a activar desde metadata
            onboarding_metadata = contract.get("onboarding_metadata", {})
            contract_metadata = contract.get("contract_metadata", {})
            
            # Buscar servicios a activar en diferentes lugares
            services_to_activate = (
                onboarding_metadata.get("services_to_activate") or
                contract_metadata.get("services_to_activate") or
                ["api_access", "dashboard", "support"]  # Default
            )
            
            # Verificar si auto_activate está habilitado
            auto_activate = onboarding_metadata.get("auto_activate_services", True)
            
            if not auto_activate:
                logger.info(
                    f"Auto-activación deshabilitada para {customer_email}",
                    extra={"contract_id": contract_id},
                )
                continue
            
            try:
                # Activar servicios
                result = activate_customer_services(
                    customer_email=customer_email,
                    services_to_activate=services_to_activate,
                    contract_id=contract_id,
                )
                
                # Actualizar estado del contrato a fully_signed
                pg_hook = PostgresHook(postgres_conn_id=os.getenv("POSTGRES_CONN_ID", "postgres_default"))
                
                signed_date = contract.get("signed_date")
                if signed_date:
                    from datetime import datetime
                    if isinstance(signed_date, str):
                        signed_date = datetime.fromisoformat(signed_date.replace('Z', '+00:00'))
                
                pg_hook.run("""
                    UPDATE contracts
                    SET status = 'fully_signed',
                        signed_date = %s,
                        updated_at = NOW()
                    WHERE contract_id = %s
                """, parameters=(signed_date or datetime.utcnow(), contract_id))
                
                # Registrar evento
                pg_hook.run("""
                    INSERT INTO contract_events (contract_id, event_type, event_description, event_data)
                    VALUES (%s, 'services_activated', %s, %s::jsonb)
                """, parameters=(
                    contract_id,
                    f"Servicios activados para {customer_email}",
                    json.dumps(result),
                ))
                
                activation_results.append({
                    "contract_id": contract_id,
                    "customer_email": customer_email,
                    "success": result["success"],
                    "activated_services": result["activated_services"],
                    "failed_services": result["failed_services"],
                })
                
                logger.info(
                    f"Servicios activados para contrato firmado",
                    extra={
                        "contract_id": contract_id,
                        "customer_email": customer_email,
                        "activated_services": result["activated_services"],
                    },
                )
                
                # Notificar
                if result["success"]:
                    notify_slack(
                        f":white_check_mark: Servicios activados para {customer_email} "
                        f"tras firma de contrato {contract_id}"
                    )
                
            except Exception as e:
                logger.error(
                    f"Error activando servicios para {customer_email}: {e}",
                    exc_info=True,
                    extra={"contract_id": contract_id},
                )
                activation_results.append({
                    "contract_id": contract_id,
                    "customer_email": customer_email,
                    "success": False,
                    "error": str(e),
                })
        
        if Stats:
            try:
                Stats.incr("contract_activation.activate_services.success", 1)
                Stats.incr("contract_activation.activate_services.activated", len(activation_results))
            except Exception:
                pass
        
        return {"activation_results": activation_results}
    
    # Define task flow
    pending = find_pending_contracts()
    checked = check_contract_signatures(pending)
    activated = activate_services_for_signed_contracts(checked)
    
    return None


# Export DAG
dag = contract_signature_activation()

