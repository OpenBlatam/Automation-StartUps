"""
DAG de Limpieza GDPR de Contratos
Elimina o anonimiza contratos según políticas de retención
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.contract_compliance import (
    get_contracts_for_gdpr_cleanup,
    check_contract_retention_policy,
    anonymize_contract_data,
    delete_contract_data
)

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


@dag(
    dag_id="contract_gdpr_cleanup",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=timedelta(days=30),  # Ejecutar mensualmente
    catchup=False,
    default_args={
        "owner": "legal-compliance",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Contract GDPR Cleanup - Limpieza de Datos para GDPR
    
    DAG que se ejecuta mensualmente para:
    - ✅ Identificar contratos que exceden política de retención
    - ✅ Anonimizar o eliminar datos según configuración
    - ✅ Cumplir con regulaciones GDPR
    - ✅ Reportar acciones tomadas
    
    **Configuración:**
    - `retention_years`: Años de retención (default: 7)
    - `action`: 'anonymize' o 'delete' (default: 'anonymize')
    - `soft_delete`: Si es delete, usar soft delete (default: true)
    """,
    description="Limpieza automática de contratos para cumplimiento GDPR",
    tags=["contracts", "legal", "gdpr", "compliance", "privacy"],
    dagrun_timeout=timedelta(hours=2),
    max_active_runs=1,
)
def contract_gdpr_cleanup() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="find_contracts_for_cleanup", pool=CONTRACT_POOL)
    def find_contracts_for_cleanup() -> dict:
        """Encuentra contratos que necesitan limpieza"""
        ctx = get_current_context()
        params = ctx.get("params", {})
        retention_years = params.get("retention_years", 7)
        
        if Stats:
            try:
                Stats.incr("contracts.gdpr.find.start", 1)
            except Exception:
                pass
        
        contracts = get_contracts_for_gdpr_cleanup(retention_years=retention_years)
        
        logger.info(
            f"Contratos encontrados para limpieza GDPR",
            extra={"count": len(contracts)}
        )
        
        if Stats:
            try:
                Stats.incr("contracts.gdpr.find.completed", 1)
                Stats.gauge("contracts.gdpr.find.count", len(contracts))
            except Exception:
                pass
        
        return {
            "contracts": contracts,
            "retention_years": retention_years,
            "count": len(contracts)
        }

    @task(task_id="process_cleanup", pool=CONTRACT_POOL)
    def process_cleanup(contracts_data: dict) -> dict:
        """Procesa limpieza de contratos"""
        ctx = get_current_context()
        params = ctx.get("params", {})
        
        action = params.get("action", "anonymize")  # 'anonymize' o 'delete'
        soft_delete = params.get("soft_delete", True)
        contracts = contracts_data["contracts"]
        
        if Stats:
            try:
                Stats.incr("contracts.gdpr.process.start", 1)
            except Exception:
                pass
        
        results = {
            "total": len(contracts),
            "processed": 0,
            "anonymized": 0,
            "deleted": 0,
            "failed": 0,
            "errors": []
        }
        
        for contract in contracts[:50]:  # Limitar a 50 por ejecución
            contract_id = contract["contract_id"]
            
            try:
                if action == "anonymize":
                    anonymize_contract_data(contract_id=contract_id)
                    results["anonymized"] += 1
                    logger.info(f"Contrato anonimizado: {contract_id}")
                elif action == "delete":
                    delete_contract_data(
                        contract_id=contract_id,
                        soft_delete=soft_delete
                    )
                    results["deleted"] += 1
                    logger.info(f"Contrato eliminado: {contract_id}")
                
                results["processed"] += 1
            except Exception as e:
                results["failed"] += 1
                error_msg = f"Error procesando {contract_id}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        logger.info(
            f"Limpieza GDPR completada",
            extra=results
        )
        
        if Stats:
            try:
                Stats.incr("contracts.gdpr.process.completed", 1)
                Stats.gauge("contracts.gdpr.process.processed", results["processed"])
            except Exception:
                pass
        
        return results

    # Define task flow
    contracts = find_contracts_for_cleanup()
    results = process_cleanup(contracts)
    
    return None


dag = contract_gdpr_cleanup()

