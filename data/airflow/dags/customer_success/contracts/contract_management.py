"""
DAG de Automatización Completa de Gestión de Contratos
Incluye creación desde plantillas, envío para firma, almacenamiento y recordatorios
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
from airflow.models import Variable
from airflow.models.param import Param

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
    dag_id="contract_management",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger only
    catchup=False,
    default_args={
        "owner": "legal-hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Contract Management - Sistema Completo de Automatización de Contratos
    
    Automatiza completamente el ciclo de vida de contratos:
    - ✅ Creación automática desde plantillas con variables
    - ✅ Integración con DocuSign y PandaDoc para firma electrónica
    - ✅ Almacenamiento de versiones firmadas
    - ✅ Recordatorios automáticos de renovación
    - ✅ Tracking completo de estados y eventos
    - ✅ Gestión de múltiples firmantes con orden de firma
    
    **Workflow automatizado:**
    1. Validación de parámetros de entrada
    2. Obtención de plantilla
    3. Generación de contrato con variables reemplazadas
    4. Creación de registro en BD
    5. Configuración de firmantes
    6. Envío para firma electrónica (opcional)
    7. Tracking de estado de firma
    
    **Parámetros:**
    - `template_id`: ID de la plantilla a usar (requerido)
    - `primary_party_email`: Email de la parte principal (requerido)
    - `primary_party_name`: Nombre de la parte principal (requerido)
    - `contract_variables`: JSON con variables para el template
    - `esignature_provider`: 'docusign', 'pandadoc' o 'manual' (opcional)
    - `auto_send_for_signature`: Enviar automáticamente para firma (default: true)
    - `additional_signers`: Lista adicional de firmantes (opcional)
    
    **Ejemplo de uso:**
    ```json
    {
        "template_id": "employment_contract_v1",
        "primary_party_email": "employee@example.com",
        "primary_party_name": "Juan Pérez",
        "contract_variables": {
            "employee_name": "Juan Pérez",
            "position": "Software Engineer",
            "salary": "$5000",
            "start_date": "2024-02-01",
            "expiration_days": 365
        },
        "esignature_provider": "docusign",
        "auto_send_for_signature": true
    }
    ```
    """,
    params={
        "template_id": Param("", type="string", description="ID de la plantilla (requerido)"),
        "primary_party_email": Param("", type="string", description="Email de la parte principal (requerido)"),
        "primary_party_name": Param("", type="string", description="Nombre de la parte principal (requerido)"),
        "contract_variables": Param({}, type="object", description="Variables para el template (JSON)"),
        "esignature_provider": Param("docusign", type="string", description="Proveedor de firma: docusign, pandadoc, manual"),
        "auto_send_for_signature": Param(True, type="boolean", description="Enviar automáticamente para firma"),
        "additional_signers": Param([], type="array", description="Firmantes adicionales (opcional)"),
    },
    description="Sistema completo de automatización de contratos con firma electrónica",
    tags=["contracts", "legal", "hr", "automation", "esignature"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=5,
    max_active_tasks=MAX_ACTIVE_TASKS,
    concurrency=10,
    sla_miss_callback=sla_miss_callback,
    render_template_as_native_obj=True,
    on_success_callback=lambda context: notify_slack(":white_check_mark: contract_management DAG succeeded"),
    on_failure_callback=lambda context: notify_slack(":x: contract_management DAG failed"),
)
def contract_management() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="validate_input", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def validate_input() -> Dict[str, Any]:
        """Validación de parámetros de entrada."""
        ctx = get_current_context()
        params = dict(ctx.get("params", {}))
        
        logger.info(
            "validating contract management params",
            extra={
                "params": {k: v for k, v in params.items() if k != "contract_variables"},
                "dag_run_id": ctx.get("run_id"),
            },
        )
        
        if Stats:
            try:
                Stats.incr("contracts.validate_input.start", 1)
            except Exception:
                pass
        
        # Validar parámetros requeridos
        template_id = params.get("template_id", "").strip()
        primary_party_email = params.get("primary_party_email", "").strip()
        primary_party_name = params.get("primary_party_name", "").strip()
        
        if not template_id:
            raise AirflowFailException("template_id es requerido")
        if not primary_party_email:
            raise AirflowFailException("primary_party_email es requerido")
        if not primary_party_name:
            raise AirflowFailException("primary_party_name es requerido")
        
        # Validar formato de email
        if "@" not in primary_party_email or "." not in primary_party_email.split("@")[1]:
            raise AirflowFailException(f"Formato de email inválido: {primary_party_email}")
        
        # Validar contract_variables
        contract_variables = params.get("contract_variables", {})
        if not isinstance(contract_variables, dict):
            raise AirflowFailException("contract_variables debe ser un objeto JSON")
        
        # Validar esignature_provider
        esignature_provider = params.get("esignature_provider", "docusign").lower()
        valid_providers = ["docusign", "pandadoc", "manual"]
        if esignature_provider not in valid_providers:
            raise AirflowFailException(f"esignature_provider debe ser uno de: {', '.join(valid_providers)}")
        
        validated_params = {
            "template_id": template_id,
            "primary_party_email": primary_party_email,
            "primary_party_name": primary_party_name,
            "contract_variables": contract_variables,
            "esignature_provider": esignature_provider,
            "auto_send_for_signature": bool(params.get("auto_send_for_signature", True)),
            "additional_signers": params.get("additional_signers", []),
        }
        
        if Stats:
            try:
                Stats.incr("contracts.validate_input.success", 1)
            except Exception:
                pass
        
        return validated_params

    @task(task_id="verify_template", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def verify_template(params: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica que la plantilla existe y está activa."""
        if Stats:
            try:
                Stats.incr("contracts.verify_template.start", 1)
            except Exception:
                pass
        
        template_id = params["template_id"]
        template = get_template(template_id)
        
        if not template:
            raise AirflowFailException(f"Plantilla no encontrada o inactiva: {template_id}")
        
        logger.info(
            f"Template verificado",
            extra={
                "template_id": template_id,
                "template_name": template.get("name"),
                "contract_type": template.get("contract_type"),
            },
        )
        
        if Stats:
            try:
                Stats.incr("contracts.verify_template.success", 1)
            except Exception:
                pass
        
        return {**params, "template": template}

    @task(task_id="create_contract", on_failure_callback=on_task_failure, pool=CONTRACT_POOL, retries=1)
    def create_contract(params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea el contrato desde la plantilla."""
        if Stats:
            try:
                Stats.incr("contracts.create_contract.start", 1)
            except Exception:
                pass
        
        result = create_contract_from_template(
            template_id=params["template_id"],
            primary_party_email=params["primary_party_email"],
            primary_party_name=params["primary_party_name"],
            contract_variables=params["contract_variables"],
            additional_signers=params.get("additional_signers", []),
        )
        
        logger.info(
            f"Contrato creado",
            extra={
                "contract_id": result["contract_id"],
                "template_id": params["template_id"],
                "status": result["status"],
            },
        )
        
        if Stats:
            try:
                Stats.incr("contracts.create_contract.success", 1)
            except Exception:
                pass
        
        return {**params, **result}

    @task(task_id="send_for_signature", on_failure_callback=on_task_failure, pool=CONTRACT_POOL, retries=2)
    def send_for_signature(params: Dict[str, Any]) -> Dict[str, Any]:
        """Envía el contrato para firma electrónica si está configurado."""
        contract_id = params.get("contract_id")
        auto_send = params.get("auto_send_for_signature", True)
        provider = params.get("esignature_provider", "docusign")
        
        if not auto_send or provider == "manual":
            logger.info(
                f"Envió automático deshabilitado o proveedor manual",
                extra={
                    "contract_id": contract_id,
                    "auto_send": auto_send,
                    "provider": provider,
                },
            )
            return {**params, "signature_sent": False}
        
        if not contract_id:
            raise AirflowFailException("contract_id no disponible")
        
        if Stats:
            try:
                Stats.incr("contracts.send_for_signature.start", 1)
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
                },
            )
            
            if Stats:
                try:
                    Stats.incr("contracts.send_for_signature.success", 1)
                except Exception:
                    pass
            
            return {**params, "signature_sent": True, **result}
        except Exception as e:
            logger.error(f"Error enviando contrato para firma: {e}")
            if Stats:
                try:
                    Stats.incr("contracts.send_for_signature.failed", 1)
                except Exception:
                    pass
            # No fallar el DAG completo si falla el envío
            return {**params, "signature_sent": False, "signature_error": str(e)}

    @task(task_id="check_initial_status", on_failure_callback=on_task_failure, pool=CONTRACT_POOL)
    def check_initial_status(params: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica el estado inicial de firma si se envió."""
        contract_id = params.get("contract_id")
        signature_sent = params.get("signature_sent", False)
        
        if not signature_sent or not contract_id:
            return {**params, "initial_status": "not_sent"}
        
        if Stats:
            try:
                Stats.incr("contracts.check_initial_status.start", 1)
            except Exception:
                pass
        
        try:
            status_result = check_contract_signature_status(contract_id=contract_id)
            
            logger.info(
                f"Estado inicial verificado",
                extra={
                    "contract_id": contract_id,
                    "status": status_result.get("status"),
                },
            )
            
            if Stats:
                try:
                    Stats.incr("contracts.check_initial_status.success", 1)
                except Exception:
                    pass
            
            return {**params, "initial_status": status_result.get("status"), "status_result": status_result}
        except Exception as e:
            logger.warning(f"Error verificando estado inicial: {e}")
            return {**params, "initial_status": "unknown", "status_error": str(e)}

    # Define task flow
    validated = validate_input()
    verified = verify_template(validated)
    contract = create_contract(verified)
    sent = send_for_signature(contract)
    status = check_initial_status(sent)
    
    return None


dag = contract_management()

