"""
DAG de Reconciliación Periódica de Contratos
Verifica consistencia entre BD y proveedores de firma
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.contract_reconciliation import (
    reconcile_contracts,
    verify_contract_integrity
)

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


@dag(
    dag_id="contract_reconciliation",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=timedelta(hours=12),  # Ejecutar cada 12 horas
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
    ### Contract Reconciliation - Reconciliación Periódica
    
    DAG que se ejecuta cada 12 horas para:
    - ✅ Verificar consistencia entre BD y proveedores
    - ✅ Identificar contratos desincronizados
    - ✅ Verificar integridad de datos
    - ✅ Reportar discrepancias
    
    **Funcionalidad:**
    - Compara estado en BD vs proveedores
    - Identifica contratos que necesitan actualización
    - Verifica integridad de versiones y eventos
    """,
    description="Reconciliación periódica de contratos",
    tags=["contracts", "legal", "reconciliation", "monitoring"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
)
def contract_reconciliation() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="reconcile_with_providers", pool=CONTRACT_POOL)
    def reconcile_with_providers() -> dict:
        """Reconcilia contratos con proveedores de firma"""
        if Stats:
            try:
                Stats.incr("contracts.reconciliation.start", 1)
            except Exception:
                pass
        
        results = reconcile_contracts(days_back=7)
        
        if results["out_of_sync"] > 0:
            logger.warning(
                f"Contratos desincronizados encontrados",
                extra={
                    "out_of_sync": results["out_of_sync"],
                    "discrepancies": results["discrepancies"]
                }
            )
        
        if Stats:
            try:
                Stats.incr("contracts.reconciliation.completed", 1)
                Stats.gauge("contracts.reconciliation.out_of_sync", results["out_of_sync"])
            except Exception:
                pass
        
        return results

    @task(task_id="verify_integrity", pool=CONTRACT_POOL)
    def verify_integrity(reconciliation_results: dict) -> dict:
        """Verifica integridad de contratos con problemas"""
        if Stats:
            try:
                Stats.incr("contracts.reconciliation.verify.start", 1)
            except Exception:
                pass
        
        discrepancies = reconciliation_results.get("discrepancies", [])
        
        integrity_results = {
            "checked": 0,
            "valid": 0,
            "invalid": 0,
            "issues": []
        }
        
        for discrepancy in discrepancies[:10]:  # Limitar a 10 para no sobrecargar
            contract_id = discrepancy["contract_id"]
            integrity_results["checked"] += 1
            
            try:
                checks = verify_contract_integrity(contract_id=contract_id)
                
                if checks["is_valid"]:
                    integrity_results["valid"] += 1
                else:
                    integrity_results["invalid"] += 1
                    integrity_results["issues"].append({
                        "contract_id": contract_id,
                        "issues": checks["issues"]
                    })
            except Exception as e:
                logger.error(f"Error verificando integridad de {contract_id}: {e}")
        
        if Stats:
            try:
                Stats.incr("contracts.reconciliation.verify.completed", 1)
                Stats.gauge("contracts.reconciliation.invalid", integrity_results["invalid"])
            except Exception:
                pass
        
        return integrity_results

    # Define task flow
    reconciliation = reconcile_with_providers()
    integrity = verify_integrity(reconciliation)
    
    return None


dag = contract_reconciliation()

