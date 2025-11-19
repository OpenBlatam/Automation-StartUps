"""
DAG de Monitoreo Periódico de Estado de Contratos
Verifica el estado de contratos pendientes de firma y actualiza la BD
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from data.airflow.plugins.contract_integrations import check_contract_signature_status

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


@dag(
    dag_id="contract_status_monitor",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=timedelta(hours=6),  # Ejecutar cada 6 horas
    catchup=False,
    default_args={
        "owner": "legal-hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Contract Status Monitor - Monitoreo Periódico de Estado
    
    DAG que se ejecuta cada 6 horas para:
    - ✅ Verificar estado de contratos pendientes de firma
    - ✅ Actualizar estado en base de datos
    - ✅ Descargar y almacenar documentos firmados
    - ✅ Notificar cambios de estado
    
    **Funcionalidad:**
    - Busca contratos con status 'pending_signature' o 'partially_signed'
    - Verifica estado en DocuSign/PandaDoc
    - Actualiza estado en BD
    - Descarga documentos firmados si están completos
    """,
    description="Monitoreo periódico del estado de firma de contratos",
    tags=["contracts", "legal", "monitoring", "automation"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
)
def contract_status_monitor() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="find_pending_contracts", pool=CONTRACT_POOL)
    def find_pending_contracts() -> List[Dict[str, Any]]:
        """Encuentra contratos pendientes de firma."""
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL hook no disponible")
        
        if Stats:
            try:
                Stats.incr("contracts.monitor.find_pending.start", 1)
            except Exception:
                pass
        
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        # Buscar contratos pendientes con integración de firma electrónica
        query = """
            SELECT DISTINCT contract_id, esignature_provider, esignature_envelope_id, esignature_document_id
            FROM contracts
            WHERE status IN ('pending_signature', 'partially_signed')
              AND esignature_provider IS NOT NULL
              AND esignature_provider != 'manual'
              AND (esignature_envelope_id IS NOT NULL OR esignature_document_id IS NOT NULL)
            ORDER BY created_at DESC
            LIMIT 100
        """
        
        contracts = hook.get_records(query)
        
        result = []
        for row in contracts:
            result.append({
                "contract_id": row[0],
                "provider": row[1],
                "envelope_id": row[2],
                "document_id": row[3]
            })
        
        logger.info(
            f"Contratos pendientes encontrados",
            extra={"contracts_count": len(result)},
        )
        
        if Stats:
            try:
                Stats.incr("contracts.monitor.find_pending.success", 1)
                Stats.incr("contracts.monitor.find_pending.count", len(result))
            except Exception:
                pass
        
        return result

    @task(task_id="check_contract_statuses", pool=CONTRACT_POOL)
    def check_contract_statuses(contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verifica el estado de cada contrato."""
        if Stats:
            try:
                Stats.incr("contracts.monitor.check_status.start", 1)
            except Exception:
                pass
        
        results = {
            "checked": 0,
            "signed": 0,
            "errors": []
        }
        
        for contract in contracts:
            contract_id = contract["contract_id"]
            try:
                status_result = check_contract_signature_status(contract_id=contract_id)
                
                results["checked"] += 1
                
                if status_result.get("status") == "fully_signed":
                    results["signed"] += 1
                    
                    logger.info(
                        f"Contrato completamente firmado",
                        extra={
                            "contract_id": contract_id,
                            "status": status_result.get("status")
                        },
                    )
                
            except Exception as e:
                error_msg = f"Error verificando {contract_id}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        logger.info(
            f"Estado de contratos verificado",
            extra=results,
        )
        
        if Stats:
            try:
                Stats.incr("contracts.monitor.check_status.success", 1)
                Stats.incr("contracts.monitor.check_status.checked", results["checked"])
                Stats.incr("contracts.monitor.check_status.signed", results["signed"])
            except Exception:
                pass
        
        return results

    # Define task flow
    contracts = find_pending_contracts()
    results = check_contract_statuses(contracts)
    
    return None


dag = contract_status_monitor()

