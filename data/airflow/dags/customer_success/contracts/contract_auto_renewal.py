"""
DAG de Renovación Automática de Contratos
Identifica contratos que requieren renovación y los renueva automáticamente
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from data.airflow.plugins.contract_integrations import renew_contract

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


@dag(
    dag_id="contract_auto_renewal",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=timedelta(hours=24),  # Ejecutar diariamente
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
    ### Contract Auto Renewal - Renovación Automática de Contratos
    
    DAG que se ejecuta diariamente para:
    - ✅ Identificar contratos con auto_renew=true que están próximos a expirar
    - ✅ Renovar automáticamente contratos elegibles
    - ✅ Enviar nuevos contratos para firma
    - ✅ Notificar a las partes involucradas
    
    **Funcionalidad:**
    - Busca contratos firmados con auto_renew=true
    - Identifica contratos que expiran en los próximos 30 días
    - Renueva contratos creando nuevas versiones
    - Envía nuevos contratos para firma
    """,
    description="Renovación automática de contratos configurados",
    tags=["contracts", "legal", "automation", "renewal"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
)
def contract_auto_renewal() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="find_contracts_to_renew", pool=CONTRACT_POOL)
    def find_contracts_to_renew() -> List[Dict[str, Any]]:
        """Encuentra contratos elegibles para renovación automática."""
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL hook no disponible")
        
        if Stats:
            try:
                Stats.incr("contracts.renewal.find_to_renew.start", 1)
            except Exception:
                pass
        
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        # Buscar contratos firmados con auto_renew que expiran pronto
        query = """
            SELECT contract_id, expiration_date, template_id, primary_party_email,
                   primary_party_name, contract_type
            FROM contracts
            WHERE status = 'fully_signed'
              AND auto_renew = true
              AND expiration_date IS NOT NULL
              AND expiration_date >= CURRENT_DATE
              AND expiration_date <= CURRENT_DATE + INTERVAL '30 days'
              AND contract_id NOT IN (
                  SELECT DISTINCT jsonb_extract_path_text(contract_variables, 'renewal_of')
                  FROM contracts
                  WHERE contract_variables::text LIKE '%renewal_of%'
              )
            ORDER BY expiration_date ASC
            LIMIT 50
        """
        
        contracts = hook.get_records(query)
        
        result = []
        for row in contracts:
            expiration_date = row[1]
            days_until_expiration = (expiration_date - pendulum.now().date()).days
            
            result.append({
                "contract_id": row[0],
                "expiration_date": expiration_date.isoformat() if hasattr(expiration_date, 'isoformat') else str(expiration_date),
                "days_until_expiration": days_until_expiration,
                "template_id": row[2],
                "primary_party_email": row[3],
                "primary_party_name": row[4],
                "contract_type": row[5]
            })
        
        logger.info(
            f"Contratos elegibles para renovación encontrados",
            extra={"contracts_count": len(result)},
        )
        
        if Stats:
            try:
                Stats.incr("contracts.renewal.find_to_renew.success", 1)
                Stats.incr("contracts.renewal.find_to_renew.count", len(result))
            except Exception:
                pass
        
        return result

    @task(task_id="renew_contracts", pool=CONTRACT_POOL)
    def renew_contracts(contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Renueva los contratos elegibles."""
        if Stats:
            try:
                Stats.incr("contracts.renewal.renew.start", 1)
            except Exception:
                pass
        
        results = {
            "total": len(contracts),
            "renewed": 0,
            "failed": 0,
            "errors": []
        }
        
        for contract in contracts:
            contract_id = contract["contract_id"]
            try:
                renewal_result = renew_contract(
                    contract_id=contract_id,
                    new_start_date=None,  # Usará fecha de expiración actual
                    new_expiration_days=None  # Usará default de la plantilla
                )
                
                results["renewed"] += 1
                
                logger.info(
                    f"Contrato renovado automáticamente",
                    extra={
                        "original_contract_id": contract_id,
                        "new_contract_id": renewal_result.get("new_contract_id")
                    },
                )
                
            except Exception as e:
                error_msg = f"Error renovando contrato {contract_id}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["failed"] += 1
        
        logger.info(
            f"Renovación de contratos completada",
            extra=results,
        )
        
        if Stats:
            try:
                Stats.incr("contracts.renewal.renew.success", 1)
                Stats.incr("contracts.renewal.renew.count", results["renewed"])
                Stats.incr("contracts.renewal.renew.failed", results["failed"])
            except Exception:
                pass
        
        return results

    # Define task flow
    contracts = find_contracts_to_renew()
    results = renew_contracts(contracts)
    
    return None


dag = contract_auto_renewal()

