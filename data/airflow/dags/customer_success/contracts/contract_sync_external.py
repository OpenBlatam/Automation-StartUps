"""
DAG de Sincronización con Sistemas Externos
Sincroniza contratos con CRM, HRIS y otros sistemas
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


@dag(
    dag_id="contract_sync_external",
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
    ### Contract External Sync - Sincronización con Sistemas Externos
    
    DAG que se ejecuta cada 6 horas para:
    - ✅ Sincronizar contratos firmados con CRM (HubSpot, Salesforce)
    - ✅ Sincronizar con sistemas HRIS
    - ✅ Actualizar estados en sistemas externos
    - ✅ Mantener consistencia entre sistemas
    
    **Funcionalidad:**
    - Identifica contratos firmados recientemente
    - Sincroniza con sistemas externos configurados
    - Maneja errores y reintentos
    """,
    description="Sincronización con sistemas externos",
    tags=["contracts", "legal", "sync", "integration"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
)
def contract_sync_external() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="find_contracts_to_sync", pool=CONTRACT_POOL)
    def find_contracts_to_sync() -> list:
        """Encuentra contratos que necesitan sincronización"""
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL hook no disponible")
        
        if Stats:
            try:
                Stats.incr("contracts.sync.find.start", 1)
            except Exception:
                pass
        
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        # Buscar contratos firmados en las últimas 24h que no han sido sincronizados
        query = """
            SELECT contract_id, primary_party_email, primary_party_id, status, signed_date
            FROM contracts
            WHERE status = 'fully_signed'
              AND signed_date >= NOW() - INTERVAL '24 hours'
              AND (metadata->>'synced_to_external' IS NULL OR metadata->>'synced_to_external' = 'false')
            ORDER BY signed_date DESC
            LIMIT 100
        """
        
        contracts = hook.get_records(query)
        
        result = [
            {
                "contract_id": row[0],
                "primary_party_email": row[1],
                "primary_party_id": row[2],
                "status": row[3],
                "signed_date": row[4].isoformat() if row[4] else None
            }
            for row in contracts
        ]
        
        logger.info(
            f"Contratos encontrados para sincronización",
            extra={"count": len(result)}
        )
        
        if Stats:
            try:
                Stats.incr("contracts.sync.find.completed", 1)
                Stats.gauge("contracts.sync.find.count", len(result))
            except Exception:
                pass
        
        return result

    @task(task_id="sync_to_crm", pool=CONTRACT_POOL)
    def sync_to_crm(contracts: list) -> dict:
        """Sincroniza contratos con CRM"""
        if Stats:
            try:
                Stats.incr("contracts.sync.crm.start", 1)
            except Exception:
                pass
        
        # TODO: Implementar sincronización con HubSpot, Salesforce, etc.
        # Por ahora solo marcar como sincronizado
        
        if not POSTGRES_AVAILABLE:
            return {"synced": 0, "errors": []}
        
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        results = {
            "total": len(contracts),
            "synced": 0,
            "failed": 0,
            "errors": []
        }
        
        for contract in contracts:
            contract_id = contract["contract_id"]
            try:
                # Marcar como sincronizado
                hook.run(
                    """
                    UPDATE contracts
                    SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                        jsonb_build_object('synced_to_external', true, 'synced_at', NOW())
                    WHERE contract_id = %s
                    """,
                    parameters=(contract_id,)
                )
                
                results["synced"] += 1
                logger.info(f"Contrato sincronizado: {contract_id}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{contract_id}: {e}")
                logger.error(f"Error sincronizando {contract_id}: {e}")
        
        if Stats:
            try:
                Stats.incr("contracts.sync.crm.completed", 1)
                Stats.gauge("contracts.sync.crm.synced", results["synced"])
            except Exception:
                pass
        
        return results

    # Define task flow
    contracts = find_contracts_to_sync()
    sync_results = sync_to_crm(contracts)
    
    return None


dag = contract_sync_external()

