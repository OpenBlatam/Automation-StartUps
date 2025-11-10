"""
DAG para Operaciones Masivas de Contratos
Incluye bulk creation, bulk send, bulk status check
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from data.airflow.plugins.contract_integrations import (
    create_contract_from_template,
    send_contract_for_signature,
    check_contract_signature_status
)

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


@dag(
    dag_id="contract_bulk_operations",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger only
    catchup=False,
    default_args={
        "owner": "legal-hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Contract Bulk Operations - Operaciones Masivas
    
    DAG para ejecutar operaciones masivas sobre contratos:
    - ✅ Creación masiva desde CSV/JSON
    - ✅ Envío masivo para firma
    - ✅ Verificación masiva de estado
    - ✅ Actualización masiva de datos
    
    **Uso:**
    - Disparar manualmente con parámetros de operación
    - Cargar datos desde archivo o parámetros
    """,
    description="Operaciones masivas sobre contratos",
    tags=["contracts", "legal", "bulk", "automation"],
    dagrun_timeout=timedelta(hours=2),
    max_active_runs=1,
)
def contract_bulk_operations() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="bulk_create_contracts", pool=CONTRACT_POOL)
    def bulk_create_contracts() -> Dict[str, Any]:
        """Crea múltiples contratos desde datos proporcionados"""
        ctx = get_current_context()
        params = ctx.get("params", {})
        
        contracts_data = params.get("contracts_data", [])
        template_id = params.get("template_id", "")
        
        if not contracts_data:
            return {"error": "No contracts_data provided", "created": 0}
        
        if Stats:
            try:
                Stats.incr("contracts.bulk.create.start", 1)
            except Exception:
                pass
        
        results = {
            "total": len(contracts_data),
            "created": 0,
            "failed": 0,
            "errors": []
        }
        
        for contract_data in contracts_data:
            try:
                result = create_contract_from_template(
                    template_id=template_id or contract_data.get("template_id"),
                    primary_party_email=contract_data["primary_party_email"],
                    primary_party_name=contract_data["primary_party_name"],
                    contract_variables=contract_data.get("contract_variables", {}),
                    additional_signers=contract_data.get("additional_signers")
                )
                results["created"] += 1
                logger.info(f"Contrato creado: {result['contract_id']}")
            except Exception as e:
                results["failed"] += 1
                error_msg = f"Error creando contrato para {contract_data.get('primary_party_email', 'unknown')}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        if Stats:
            try:
                Stats.incr("contracts.bulk.create.success", 1)
                Stats.incr("contracts.bulk.create.count", results["created"])
            except Exception:
                pass
        
        return results

    @task(task_id="bulk_send_for_signature", pool=CONTRACT_POOL)
    def bulk_send_for_signature() -> Dict[str, Any]:
        """Envía múltiples contratos para firma"""
        ctx = get_current_context()
        params = ctx.get("params", {})
        
        contract_ids = params.get("contract_ids", [])
        esignature_provider = params.get("esignature_provider", "docusign")
        
        if not contract_ids:
            return {"error": "No contract_ids provided", "sent": 0}
        
        if Stats:
            try:
                Stats.incr("contracts.bulk.send.start", 1)
            except Exception:
                pass
        
        results = {
            "total": len(contract_ids),
            "sent": 0,
            "failed": 0,
            "errors": []
        }
        
        for contract_id in contract_ids:
            try:
                send_contract_for_signature(
                    contract_id=contract_id,
                    esignature_provider=esignature_provider
                )
                results["sent"] += 1
                logger.info(f"Contrato enviado: {contract_id}")
            except Exception as e:
                results["failed"] += 1
                error_msg = f"Error enviando contrato {contract_id}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        if Stats:
            try:
                Stats.incr("contracts.bulk.send.success", 1)
                Stats.incr("contracts.bulk.send.count", results["sent"])
            except Exception:
                pass
        
        return results

    @task(task_id="bulk_check_status", pool=CONTRACT_POOL)
    def bulk_check_status() -> Dict[str, Any]:
        """Verifica estado de múltiples contratos"""
        ctx = get_current_context()
        params = ctx.get("params", {})
        
        contract_ids = params.get("contract_ids", [])
        
        if not contract_ids:
            # Si no se proporcionan, buscar contratos pendientes
            if not POSTGRES_AVAILABLE:
                return {"error": "Database not available"}
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            query = """
                SELECT contract_id
                FROM contracts
                WHERE status IN ('pending_signature', 'partially_signed')
                LIMIT 100
            """
            contract_ids = [row[0] for row in hook.get_records(query)]
        
        if Stats:
            try:
                Stats.incr("contracts.bulk.check.start", 1)
            except Exception:
                pass
        
        results = {
            "total": len(contract_ids),
            "checked": 0,
            "signed": 0,
            "pending": 0,
            "errors": []
        }
        
        for contract_id in contract_ids:
            try:
                status_result = check_contract_signature_status(contract_id=contract_id)
                results["checked"] += 1
                
                if status_result.get("status") == "fully_signed":
                    results["signed"] += 1
                else:
                    results["pending"] += 1
                
                logger.info(f"Estado verificado: {contract_id} - {status_result.get('status')}")
            except Exception as e:
                error_msg = f"Error verificando {contract_id}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        if Stats:
            try:
                Stats.incr("contracts.bulk.check.success", 1)
                Stats.incr("contracts.bulk.check.checked", results["checked"])
            except Exception:
                pass
        
        return results

    # Define task flow - ejecutar según parámetros
    ctx = get_current_context()
    params = ctx.get("params", {})
    operation = params.get("operation", "check")  # create, send, check
    
    if operation == "create":
        bulk_create_contracts()
    elif operation == "send":
        bulk_send_for_signature()
    else:
        bulk_check_status()
    
    return None


dag = contract_bulk_operations()

