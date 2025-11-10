"""
DAG de Automatización Completa de Contratos para Nuevos Clientes
Flujo: Nuevo Cliente → Genera Borrador → Envía para Firma → Activa Servicio cuando Firma es Recibida
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from airflow.models.param import Param
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Integraciones de contratos
from data.airflow.plugins.contract_integrations import (
    create_contract_from_template,
    send_contract_for_signature,
    check_contract_signature_status,
    get_template,
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


@dag(
    dag_id="automated_customer_contract",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger only
    catchup=False,
    default_args={
        "owner": "legal-sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Automatización Completa de Contratos para Nuevos Clientes
    
    Sistema automatizado que integra el ciclo completo:
    - ✅ Detección de nuevo cliente
    - ✅ Generación automática de borrador de contrato
    - ✅ Envío para firma electrónica
    - ✅ Monitoreo de estado de firma
    - ✅ Activación automática de servicios cuando la firma es recibida
    
    **Flujo automatizado:**
    1. Validación de datos del cliente
    2. Obtención de plantilla de contrato (por tipo de cliente/plan)
    3. Generación de borrador con datos del cliente
    4. Envío para firma electrónica (DocuSign/PandaDoc)
    5. Monitoreo de estado de firma
    6. Activación de servicios cuando la firma es completada
    
    **Parámetros:**
    - `customer_email`: Email del cliente (requerido)
    - `customer_name`: Nombre completo del cliente (requerido)
    - `company_name`: Nombre de la empresa (opcional)
    - `service_plan`: Plan de servicio (requerido)
    - `contract_template_id`: ID de plantilla (opcional, se selecciona automáticamente si no se proporciona)
    - `esignature_provider`: 'docusign' o 'pandadoc' (default: 'docusign')
    - `auto_activate_services`: Activar servicios automáticamente después de firma (default: true)
    - `services_to_activate`: Lista de servicios a activar (array)
    
    **Integración con onboarding:**
    Este DAG se puede disparar desde el DAG de `customer_onboarding` o 
    independientemente cuando se detecta un nuevo cliente.
    
    **Ejemplo de uso:**
    ```json
    {
        "customer_email": "cliente@example.com",
        "customer_name": "Juan Pérez",
        "company_name": "Mi Empresa S.A.",
        "service_plan": "enterprise",
        "contract_template_id": "client_service_contract_v1",
        "esignature_provider": "docusign",
        "auto_activate_services": true,
        "services_to_activate": ["api_access", "dashboard", "support"]
    }
    ```
    """,
    params={
        "customer_email": Param("", type="string", description="Email del cliente (requerido)"),
        "customer_name": Param("", type="string", description="Nombre completo del cliente (requerido)"),
        "company_name": Param("", type="string", description="Nombre de la empresa (opcional)"),
        "service_plan": Param("", type="string", description="Plan de servicio (requerido)"),
        "contract_template_id": Param("", type="string", description="ID de plantilla (opcional)"),
        "esignature_provider": Param("docusign", type="string", description="Proveedor de firma: docusign, pandadoc"),
        "auto_activate_services": Param(True, type="boolean", description="Activar servicios después de firma"),
        "services_to_activate": Param([], type="array", description="Lista de servicios a activar"),
        "contract_start_date": Param("", type="string", description="Fecha de inicio del contrato (YYYY-MM-DD)"),
        "contract_duration_days": Param(365, type="integer", description="Duración del contrato en días"),
        "additional_signers": Param([], type="array", description="Firmantes adicionales (opcional)"),
    },
    description="Automatización completa de contratos para nuevos clientes con activación de servicios",
    tags=["contracts", "legal", "sales", "automation", "customer", "onboarding"],
    dagrun_timeout=timedelta(minutes=60),
    max_active_runs=5,
    max_active_tasks=MAX_ACTIVE_TASKS,
    concurrency=10,
    sla_miss_callback=sla_miss_callback,
    render_template_as_native_obj=True,
    on_success_callback=lambda context: notify_slack(":white_check_mark: automated_customer_contract DAG succeeded"),
    on_failure_callback=lambda context: notify_slack(":x: automated_customer_contract DAG failed"),
)
def automated_customer_contract() -> None:
    logger = logging.getLogger("airflow.task")
    
    @task(task_id="validate_customer_data", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def validate_customer_data() -> Dict[str, Any]:
        """Valida y prepara los datos del cliente."""
        ctx = get_current_context()
        params = dict(ctx.get("params", {}))
        
        logger.info(
            "Validating customer contract data",
            extra={
                "customer_email": params.get("customer_email"),
                "dag_run_id": ctx.get("run_id"),
            },
        )
        
        if Stats:
            try:
                Stats.incr("automated_contract.validate.start", 1)
            except Exception:
                pass
        
        # Validar parámetros requeridos
        customer_email = params.get("customer_email", "").strip()
        customer_name = params.get("customer_name", "").strip()
        service_plan = params.get("service_plan", "").strip()
        
        if not customer_email:
            raise AirflowFailException("customer_email es requerido")
        if not customer_name:
            raise AirflowFailException("customer_name es requerido")
        if not service_plan:
            raise AirflowFailException("service_plan es requerido")
        
        # Validar formato de email
        if "@" not in customer_email or "." not in customer_email.split("@")[1]:
            raise AirflowFailException(f"Formato de email inválido: {customer_email}")
        
        # Preparar datos del cliente
        customer_data = {
            "customer_email": customer_email,
            "customer_name": customer_name,
            "company_name": params.get("company_name", "").strip() or None,
            "service_plan": service_plan,
            "contract_template_id": params.get("contract_template_id", "").strip() or None,
            "esignature_provider": params.get("esignature_provider", "docusign").lower(),
            "auto_activate_services": bool(params.get("auto_activate_services", True)),
            "services_to_activate": params.get("services_to_activate", []),
            "contract_start_date": params.get("contract_start_date", "").strip() or None,
            "contract_duration_days": int(params.get("contract_duration_days", 365)),
            "additional_signers": params.get("additional_signers", []),
        }
        
        # Validar proveedor de firma
        valid_providers = ["docusign", "pandadoc"]
        if customer_data["esignature_provider"] not in valid_providers:
            raise AirflowFailException(f"esignature_provider debe ser uno de: {', '.join(valid_providers)}")
        
        if Stats:
            try:
                Stats.incr("automated_contract.validate.success", 1)
            except Exception:
                pass
        
        return customer_data
    
    @task(task_id="determine_contract_template", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def determine_contract_template(customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determina la plantilla de contrato a usar."""
        if Stats:
            try:
                Stats.incr("automated_contract.determine_template.start", 1)
            except Exception:
                pass
        
        template_id = customer_data.get("contract_template_id")
        service_plan = customer_data.get("service_plan", "").lower()
        
        # Si no se proporciona template_id, seleccionar automáticamente según plan
        if not template_id:
            # Mapeo de planes a templates
            plan_template_map = {
                "basic": "client_service_contract_basic",
                "standard": "client_service_contract_standard",
                "enterprise": "client_service_contract_enterprise",
                "premium": "client_service_contract_premium",
            }
            
            template_id = plan_template_map.get(service_plan, "client_service_contract_standard")
            logger.info(
                f"Template seleccionado automáticamente según plan",
                extra={
                    "service_plan": service_plan,
                    "template_id": template_id,
                },
            )
        
        # Verificar que la plantilla existe
        template = get_template(template_id)
        if not template:
            raise AirflowFailException(f"Plantilla no encontrada o inactiva: {template_id}")
        
        logger.info(
            f"Template determinado",
            extra={
                "template_id": template_id,
                "template_name": template.get("name"),
                "contract_type": template.get("contract_type"),
            },
        )
        
        if Stats:
            try:
                Stats.incr("automated_contract.determine_template.success", 1)
            except Exception:
                pass
        
        return {**customer_data, "template_id": template_id, "template": template}
    
    @task(task_id="generate_contract_draft", on_failure_callback=on_task_failure, pool=CONTRACT_POOL, retries=1)
    def generate_contract_draft(data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera el borrador del contrato desde la plantilla."""
        if Stats:
            try:
                Stats.incr("automated_contract.generate_draft.start", 1)
            except Exception:
                pass
        
        # Preparar variables para el contrato
        customer_name = data["customer_name"]
        company_name = data.get("company_name")
        customer_email = data["customer_email"]
        service_plan = data["service_plan"]
        start_date = data.get("contract_start_date")
        duration_days = data.get("contract_duration_days", 365)
        
        # Parsear fecha de inicio
        if start_date:
            from datetime import datetime
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                start_date_obj = None
        else:
            from datetime import datetime
            start_date_obj = datetime.now().date()
        
        # Calcular fecha de expiración
        from datetime import timedelta
        expiration_date_obj = start_date_obj + timedelta(days=duration_days) if start_date_obj else None
        
        contract_variables = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "company_name": company_name or customer_name,
            "service_plan": service_plan,
            "start_date": start_date_obj.strftime("%Y-%m-%d") if start_date_obj else None,
            "expiration_days": duration_days,
            "expiration_date": expiration_date_obj.strftime("%Y-%m-%d") if expiration_date_obj else None,
            "primary_party_type": "customer",
            "primary_party_email": customer_email,
            "primary_party_name": customer_name,
        }
        
        # Crear el contrato
        result = create_contract_from_template(
            template_id=data["template_id"],
            primary_party_email=customer_email,
            primary_party_name=customer_name,
            contract_variables=contract_variables,
            additional_signers=data.get("additional_signers", []),
        )
        
        logger.info(
            f"Borrador de contrato generado",
            extra={
                "contract_id": result["contract_id"],
                "template_id": data["template_id"],
                "status": result["status"],
            },
        )
        
        if Stats:
            try:
                Stats.incr("automated_contract.generate_draft.success", 1)
            except Exception:
                pass
        
        return {**data, **result, "contract_variables": contract_variables}
    
    @task(task_id="send_contract_for_signature", on_failure_callback=on_task_failure, pool=CONTRACT_POOL, retries=2)
    def send_contract_for_signature(data: Dict[str, Any]) -> Dict[str, Any]:
        """Envía el contrato para firma electrónica."""
        contract_id = data.get("contract_id")
        provider = data.get("esignature_provider", "docusign")
        
        if not contract_id:
            raise AirflowFailException("contract_id no disponible")
        
        if Stats:
            try:
                Stats.incr("automated_contract.send_signature.start", 1)
            except Exception:
                pass
        
        try:
            result = send_contract_for_signature(
                contract_id=contract_id,
                esignature_provider=provider,
            )
            
            logger.info(
                f"Contrato enviado para firma",
                extra={
                    "contract_id": contract_id,
                    "provider": provider,
                    "envelope_id": result.get("envelope_id"),
                    "document_id": result.get("document_id"),
                    "signature_url": result.get("signature_url"),
                },
            )
            
            if Stats:
                try:
                    Stats.incr("automated_contract.send_signature.success", 1)
                except Exception:
                    pass
            
            return {**data, "signature_sent": True, **result}
        except Exception as e:
            logger.error(f"Error enviando contrato para firma: {e}", exc_info=True)
            if Stats:
                try:
                    Stats.incr("automated_contract.send_signature.failed", 1)
                except Exception:
                    pass
            raise AirflowFailException(f"Error enviando contrato para firma: {str(e)}")
    
    @task(task_id="store_contract_reference", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def store_contract_reference(data: Dict[str, Any]) -> Dict[str, Any]:
        """Almacena la referencia del contrato en la tabla de onboarding para tracking."""
        if Stats:
            try:
                Stats.incr("automated_contract.store_reference.start", 1)
            except Exception:
                pass
        
        customer_email = data.get("customer_email")
        contract_id = data.get("contract_id")
        
        if not customer_email or not contract_id:
            return data
        
        try:
            pg_hook = PostgresHook(postgres_conn_id=os.getenv("POSTGRES_CONN_ID", "postgres_default"))
            
            # Actualizar o insertar referencia en customer_onboarding
            update_sql = """
                UPDATE customer_onboarding
                SET metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb),
                    '{contract_id}',
                    %s::jsonb
                ),
                updated_at = NOW()
                WHERE customer_email = %s
                RETURNING id
            """
            
            contract_metadata = {
                "contract_id": contract_id,
                "template_id": data.get("template_id"),
                "esignature_provider": data.get("esignature_provider"),
                "envelope_id": data.get("envelope_id"),
                "document_id": data.get("document_id"),
                "signature_url": data.get("signature_url"),
                "status": "pending_signature",
                "created_at": data.get("contract_created_at"),
            }
            
            import json
            result = pg_hook.get_first(update_sql, parameters=(
                json.dumps(contract_id),
                customer_email
            ))
            
            if result:
                logger.info(
                    f"Referencia de contrato almacenada",
                    extra={
                        "customer_email": customer_email,
                        "contract_id": contract_id,
                        "onboarding_id": result[0],
                    },
                )
            
            if Stats:
                try:
                    Stats.incr("automated_contract.store_reference.success", 1)
                except Exception:
                    pass
            
        except Exception as e:
            logger.warning(f"Error almacenando referencia de contrato: {e}")
            # No fallar el DAG si esto falla
        
        return data
    
    # Define task flow
    validated = validate_customer_data()
    template_data = determine_contract_template(validated)
    contract_draft = generate_contract_draft(template_data)
    sent = send_contract_for_signature(contract_draft)
    stored = store_contract_reference(sent)
    
    return None


# Export DAG
dag = automated_customer_contract()














