"""
Módulo de Compliance y GDPR para Contratos
Incluye funciones de privacidad, retención y eliminación de datos
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

logger = logging.getLogger("airflow.task")


def check_contract_retention_policy(
    contract_id: str,
    retention_years: int = 7,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Verifica si un contrato cumple con la política de retención.
    
    Args:
        contract_id: ID del contrato
        retention_years: Años de retención requeridos
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de retención
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    query = """
        SELECT signed_date, expiration_date, created_at
        FROM contracts
        WHERE contract_id = %s
    """
    contract = hook.get_first(query, parameters=(contract_id,))
    
    if not contract:
        return {"error": "Contract not found"}
    
    signed_date = contract[0]
    expiration_date = contract[1]
    created_at = contract[2]
    
    # Calcular fecha de retención (años después de expiración o firma)
    reference_date = expiration_date or signed_date or created_at
    if not reference_date:
        return {"error": "No reference date available"}
    
    retention_date = reference_date + timedelta(days=retention_years * 365)
    
    is_expired = retention_date < datetime.now().date()
    
    return {
        "contract_id": contract_id,
        "reference_date": reference_date.isoformat(),
        "retention_date": retention_date.isoformat(),
        "retention_years": retention_years,
        "is_expired": is_expired,
        "days_until_expiration": (retention_date - datetime.now().date()).days if not is_expired else 0,
        "can_be_deleted": is_expired
    }


def anonymize_contract_data(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Anonimiza datos de un contrato para cumplir con GDPR.
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de anonimización
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Anonimizar datos personales
    update_query = """
        UPDATE contracts
        SET 
            primary_party_email = 'ANONYMIZED-' || contract_id,
            primary_party_name = 'ANONYMIZED',
            primary_party_id = NULL,
            description = 'Data anonymized for GDPR compliance',
            updated_at = NOW()
        WHERE contract_id = %s
    """
    
    hook.run(update_query, parameters=(contract_id,))
    
    # Anonimizar firmantes
    signers_update = """
        UPDATE contract_signers
        SET 
            signer_email = 'ANONYMIZED-' || contract_id || '-' || signer_order,
            signer_name = 'ANONYMIZED',
            updated_at = NOW()
        WHERE contract_id = %s
    """
    
    hook.run(signers_update, parameters=(contract_id,))
    
    # Registrar evento
    event_query = """
        INSERT INTO contract_events (
            contract_id, event_type, event_description, event_data
        ) VALUES (%s, %s, %s, %s)
    """
    hook.run(
        event_query,
        parameters=(
            contract_id,
            "anonymized",
            "Datos anonimizados para cumplimiento GDPR",
            '{"anonymized_at": "' + datetime.now().isoformat() + '"}'
        )
    )
    
    logger.info(f"Contrato {contract_id} anonimizado para GDPR")
    
    return {
        "contract_id": contract_id,
        "anonymized_at": datetime.now().isoformat(),
        "status": "anonymized"
    }


def delete_contract_data(
    contract_id: str,
    soft_delete: bool = True,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Elimina datos de un contrato (soft delete por defecto).
    
    Args:
        contract_id: ID del contrato
        soft_delete: Si True, marca como eliminado; si False, elimina físicamente
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de eliminación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    if soft_delete:
        # Soft delete: marcar como eliminado
        update_query = """
            UPDATE contracts
            SET status = 'cancelled',
                metadata = COALESCE(metadata, '{}'::jsonb) || 
                    jsonb_build_object('deleted_at', NOW(), 'deleted_reason', 'GDPR'),
                updated_at = NOW()
            WHERE contract_id = %s
        """
        hook.run(update_query, parameters=(contract_id,))
        
        # Registrar evento
        event_query = """
            INSERT INTO contract_events (
                contract_id, event_type, event_description, event_data
            ) VALUES (%s, %s, %s, %s)
        """
        hook.run(
            event_query,
            parameters=(
                contract_id,
                "soft_deleted",
                "Contrato marcado como eliminado (soft delete)",
                '{"deleted_at": "' + datetime.now().isoformat() + '", "reason": "GDPR"}'
            )
        )
        
        logger.info(f"Contrato {contract_id} marcado como eliminado (soft delete)")
        
        return {
            "contract_id": contract_id,
            "deleted_at": datetime.now().isoformat(),
            "delete_type": "soft",
            "status": "deleted"
        }
    else:
        # Hard delete: eliminar físicamente (usar con precaución)
        # Primero eliminar dependencias
        hook.run("DELETE FROM contract_events WHERE contract_id = %s", parameters=(contract_id,))
        hook.run("DELETE FROM contract_renewal_reminders WHERE contract_id = %s", parameters=(contract_id,))
        hook.run("DELETE FROM contract_versions WHERE contract_id = %s", parameters=(contract_id,))
        hook.run("DELETE FROM contract_signers WHERE contract_id = %s", parameters=(contract_id,))
        hook.run("DELETE FROM contracts WHERE contract_id = %s", parameters=(contract_id,))
        
        logger.warning(f"Contrato {contract_id} eliminado físicamente (hard delete)")
        
        return {
            "contract_id": contract_id,
            "deleted_at": datetime.now().isoformat(),
            "delete_type": "hard",
            "status": "permanently_deleted"
        }


def get_contracts_for_gdpr_cleanup(
    retention_years: int = 7,
    postgres_conn_id: str = "postgres_default"
) -> List[Dict[str, Any]]:
    """
    Obtiene contratos que pueden ser eliminados según política de retención.
    
    Args:
        retention_years: Años de retención
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Lista de contratos elegibles para eliminación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    cutoff_date = datetime.now().date() - timedelta(days=retention_years * 365)
    
    query = """
        SELECT contract_id, title, expiration_date, signed_date, created_at,
               primary_party_email, status
        FROM contracts
        WHERE status IN ('fully_signed', 'expired', 'terminated')
          AND (
              (expiration_date IS NOT NULL AND expiration_date < %s) OR
              (signed_date IS NOT NULL AND signed_date < %s) OR
              (expiration_date IS NULL AND signed_date IS NULL AND created_at < %s)
          )
          AND metadata->>'deleted_at' IS NULL
        ORDER BY expiration_date DESC NULLS LAST, signed_date DESC NULLS LAST
        LIMIT 100
    """
    
    contracts = hook.get_records(query, parameters=(cutoff_date, cutoff_date, cutoff_date))
    
    result = []
    for row in contracts:
        result.append({
            "contract_id": row[0],
            "title": row[1],
            "expiration_date": row[2].isoformat() if row[2] else None,
            "signed_date": row[3].isoformat() if row[3] else None,
            "created_at": row[4].isoformat() if row[4] else None,
            "primary_party_email": row[5],
            "status": row[6]
        })
    
    return result


def export_contract_data_for_subject(
    primary_party_email: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Exporta todos los datos de un sujeto para solicitudes GDPR (derecho de acceso).
    
    Args:
        primary_party_email: Email del sujeto
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con todos los datos del sujeto
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener todos los contratos
    contracts_query = """
        SELECT contract_id, title, contract_type, status, start_date,
               expiration_date, signed_date, created_at, contract_variables
        FROM contracts
        WHERE primary_party_email = %s
        ORDER BY created_at DESC
    """
    contracts = hook.get_records(contracts_query, parameters=(primary_party_email,))
    
    result = {
        "subject_email": primary_party_email,
        "export_date": datetime.now().isoformat(),
        "contracts": []
    }
    
    for row in contracts:
        contract_id = row[0]
        
        # Obtener firmantes
        signers_query = """
            SELECT signer_email, signer_name, signer_role, signature_status,
                   signature_signed_at
            FROM contract_signers
            WHERE contract_id = %s
        """
        signers = hook.get_records(signers_query, parameters=(contract_id,))
        
        # Obtener eventos
        events_query = """
            SELECT event_type, event_description, event_timestamp
            FROM contract_events
            WHERE contract_id = %s
            ORDER BY event_timestamp
        """
        events = hook.get_records(events_query, parameters=(contract_id,))
        
        contract_data = {
            "contract_id": row[0],
            "title": row[1],
            "contract_type": row[2],
            "status": row[3],
            "start_date": row[4].isoformat() if row[4] else None,
            "expiration_date": row[5].isoformat() if row[5] else None,
            "signed_date": row[6].isoformat() if row[6] else None,
            "created_at": row[7].isoformat() if row[7] else None,
            "contract_variables": row[8] if isinstance(row[8], dict) else {},
            "signers": [
                {
                    "email": s[0],
                    "name": s[1],
                    "role": s[2],
                    "status": s[3],
                    "signed_at": s[4].isoformat() if s[4] else None
                }
                for s in signers
            ],
            "events": [
                {
                    "type": e[0],
                    "description": e[1],
                    "timestamp": e[2].isoformat() if e[2] else None
                }
                for e in events
            ]
        }
        
        result["contracts"].append(contract_data)
    
    result["total_contracts"] = len(result["contracts"])
    
    return result

