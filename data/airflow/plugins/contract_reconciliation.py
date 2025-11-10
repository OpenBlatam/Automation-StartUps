"""
Módulo de Reconciliación de Contratos
Verifica consistencia entre BD y proveedores de firma electrónica
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from data.airflow.plugins.contract_integrations import (
    get_esignature_client,
    check_contract_signature_status
)

logger = logging.getLogger("airflow.task")


def reconcile_contracts(
    contract_ids: List[str] = None,
    days_back: int = 7,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Reconciliación de contratos entre BD y proveedores de firma.
    
    Args:
        contract_ids: Lista de contract IDs a reconciliar (None = todos los pendientes)
        days_back: Días hacia atrás para buscar contratos
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con resultados de reconciliación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Construir query
    if contract_ids:
        placeholders = ','.join(['%s'] * len(contract_ids))
        where_clause = f"c.contract_id IN ({placeholders})"
        params = tuple(contract_ids)
    else:
        where_clause = """
            c.status IN ('pending_signature', 'partially_signed')
            AND c.created_at >= %s
            AND c.esignature_provider IS NOT NULL
            AND c.esignature_provider != 'manual'
        """
        params = (datetime.now() - timedelta(days=days_back),)
    
    query = f"""
        SELECT 
            c.contract_id,
            c.status as db_status,
            c.esignature_provider,
            c.esignature_envelope_id,
            c.esignature_document_id,
            c.updated_at
        FROM contracts c
        WHERE {where_clause}
    """
    
    contracts = hook.get_records(query, parameters=params)
    
    results = {
        "total_checked": 0,
        "synced": 0,
        "out_of_sync": 0,
        "errors": 0,
        "discrepancies": []
    }
    
    for row in contracts:
        contract_id = row[0]
        db_status = row[1]
        provider = row[2]
        envelope_id = row[3]
        document_id = row[4]
        last_updated = row[5]
        
        results["total_checked"] += 1
        
        try:
            # Verificar estado en el proveedor
            status_result = check_contract_signature_status(contract_id=contract_id)
            provider_status = status_result.get("status")
            
            # Comparar estados
            if db_status == provider_status:
                results["synced"] += 1
            else:
                results["out_of_sync"] += 1
                results["discrepancies"].append({
                    "contract_id": contract_id,
                    "db_status": db_status,
                    "provider_status": provider_status,
                    "provider": provider,
                    "last_updated": last_updated.isoformat() if last_updated else None
                })
                
                logger.warning(
                    f"Discrepancia encontrada",
                    extra={
                        "contract_id": contract_id,
                        "db_status": db_status,
                        "provider_status": provider_status
                    }
                )
        except Exception as e:
            results["errors"] += 1
            logger.error(f"Error reconciliando contrato {contract_id}: {e}")
    
    logger.info(
        f"Reconciliación completada",
        extra={
            "total": results["total_checked"],
            "synced": results["synced"],
            "out_of_sync": results["out_of_sync"]
        }
    )
    
    return results


def verify_contract_integrity(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Verifica la integridad de un contrato (versiones, firmantes, eventos).
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con resultados de verificación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    checks = {
        "contract_exists": False,
        "has_signers": False,
        "versions_consistent": False,
        "events_consistent": False,
        "issues": []
    }
    
    # Verificar que el contrato existe
    contract_query = "SELECT contract_id FROM contracts WHERE contract_id = %s"
    contract = hook.get_first(contract_query, parameters=(contract_id,))
    
    if not contract:
        checks["issues"].append("Contrato no existe en BD")
        return checks
    
    checks["contract_exists"] = True
    
    # Verificar firmantes
    signers_query = "SELECT COUNT(*) FROM contract_signers WHERE contract_id = %s"
    signers_count = hook.get_first(signers_query, parameters=(contract_id,))[0] or 0
    
    if signers_count == 0:
        checks["issues"].append("No hay firmantes configurados")
    else:
        checks["has_signers"] = True
    
    # Verificar versiones
    versions_query = """
        SELECT COUNT(*) as total,
               COUNT(CASE WHEN is_current = true THEN 1 END) as current_count
        FROM contract_versions
        WHERE contract_id = %s
    """
    versions_result = hook.get_first(versions_query, parameters=(contract_id,))
    
    if versions_result:
        total_versions = versions_result[0] or 0
        current_versions = versions_result[1] or 0
        
        if total_versions > 0:
            if current_versions != 1:
                checks["issues"].append(f"Versiones inconsistentes: {current_versions} marcadas como actuales")
            else:
                checks["versions_consistent"] = True
    
    # Verificar eventos
    events_query = "SELECT COUNT(*) FROM contract_events WHERE contract_id = %s"
    events_count = hook.get_first(events_query, parameters=(contract_id,))[0] or 0
    
    if events_count == 0:
        checks["issues"].append("No hay eventos registrados")
    else:
        checks["events_consistent"] = True
    
    checks["is_valid"] = (
        checks["contract_exists"] and
        checks["has_signers"] and
        checks["versions_consistent"] and
        len(checks["issues"]) == 0
    )
    
    return checks


def audit_contract_chain(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Audita la cadena completa de un contrato (creación -> firma -> almacenamiento).
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con auditoría completa
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    audit = {
        "contract_id": contract_id,
        "audit_date": datetime.now().isoformat(),
        "chain_events": [],
        "gaps": [],
        "is_complete": False
    }
    
    # Obtener todos los eventos ordenados
    events_query = """
        SELECT event_type, event_description, event_timestamp, event_actor_email
        FROM contract_events
        WHERE contract_id = %s
        ORDER BY event_timestamp ASC
    """
    events = hook.get_records(events_query, parameters=(contract_id,))
    
    expected_events = ["created", "sent_for_signature", "signed"]
    found_events = []
    
    for event in events:
        event_type = event[0]
        audit["chain_events"].append({
            "type": event_type,
            "description": event[1],
            "timestamp": event[2].isoformat() if event[2] else None,
            "actor": event[3]
        })
        found_events.append(event_type)
    
    # Verificar eventos esperados
    for expected in expected_events:
        if expected not in found_events:
            audit["gaps"].append(f"Evento esperado no encontrado: {expected}")
    
    # Verificar que hay versión firmada si está completamente firmado
    contract_query = "SELECT status FROM contracts WHERE contract_id = %s"
    contract_status = hook.get_first(contract_query, parameters=(contract_id,))
    
    if contract_status and contract_status[0] == "fully_signed":
        versions_query = """
            SELECT COUNT(*) FROM contract_versions
            WHERE contract_id = %s AND is_current = true
        """
        has_version = hook.get_first(versions_query, parameters=(contract_id,))[0] or 0
        
        if has_version == 0:
            audit["gaps"].append("Contrato firmado pero no hay versión almacenada")
    
    audit["is_complete"] = len(audit["gaps"]) == 0
    
    return audit

