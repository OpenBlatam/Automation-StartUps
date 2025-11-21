"""
Sistema de Workflow de Aprobación para Contratos
Gestión de aprobaciones antes de enviar para firma
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


class ApprovalStatus(Enum):
    """Estados de aprobación"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


def request_approval(
    contract_id: str,
    approvers: List[Dict[str, str]],
    approval_notes: str = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Solicita aprobación para un contrato.
    
    Args:
        contract_id: ID del contrato
        approvers: Lista de aprobadores [{"email": "...", "name": "...", "role": "..."}]
        approval_notes: Notas sobre la solicitud
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de la solicitud de aprobación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Verificar que el contrato existe
    contract_query = "SELECT contract_id, status FROM contracts WHERE contract_id = %s"
    contract = hook.get_first(contract_query, parameters=(contract_id,))
    
    if not contract:
        raise ValueError(f"Contrato {contract_id} no encontrado")
    
    # Crear solicitud de aprobación
    approval_id = f"APPROVAL-{contract_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    insert_query = """
        INSERT INTO contract_approvals (
            approval_id, contract_id, approval_status, approval_notes,
            requested_at, requested_by
        ) VALUES (%s, %s, %s, %s, NOW(), %s)
    """
    
    hook.run(
        insert_query,
        parameters=(
            approval_id,
            contract_id,
            ApprovalStatus.PENDING.value,
            approval_notes,
            "system"  # TODO: obtener de contexto
        )
    )
    
    # Crear registros de aprobadores
    for idx, approver in enumerate(approvers):
        approver_query = """
            INSERT INTO contract_approvers (
                approval_id, approver_email, approver_name, approver_role,
                approval_order, approval_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        
        hook.run(
            approver_query,
            parameters=(
                approval_id,
                approver["email"],
                approver["name"],
                approver.get("role", "approver"),
                idx + 1,
                ApprovalStatus.PENDING.value
            )
        )
    
    # Actualizar metadata del contrato
    hook.run(
        """
        UPDATE contracts
        SET metadata = COALESCE(metadata, '{}'::jsonb) || 
            jsonb_build_object('approval_id', %s, 'approval_status', 'pending')
        WHERE contract_id = %s
        """,
        parameters=(approval_id, contract_id)
    )
    
    logger.info(
        f"Aprobación solicitada para contrato {contract_id}",
        extra={"approval_id": approval_id, "approvers_count": len(approvers)}
    )
    
    return {
        "approval_id": approval_id,
        "contract_id": contract_id,
        "status": ApprovalStatus.PENDING.value,
        "approvers": approvers,
        "requested_at": datetime.now().isoformat()
    }


def approve_contract(
    approval_id: str,
    approver_email: str,
    approval_notes: str = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Aprueba un contrato (un aprobador).
    
    Args:
        approval_id: ID de la aprobación
        approver_email: Email del aprobador
        approval_notes: Notas de aprobación
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de la aprobación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Actualizar estado del aprobador
    update_query = """
        UPDATE contract_approvers
        SET approval_status = %s,
            approval_notes = %s,
            approved_at = NOW()
        WHERE approval_id = %s AND approver_email = %s
        RETURNING approval_order
    """
    
    result = hook.get_first(
        update_query,
        parameters=(
            ApprovalStatus.APPROVED.value,
            approval_notes,
            approval_id,
            approver_email
        )
    )
    
    if not result:
        raise ValueError(f"Aprobador {approver_email} no encontrado en {approval_id}")
    
    # Verificar si todos los aprobadores han aprobado
    check_query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN approval_status = 'approved' THEN 1 END) as approved
        FROM contract_approvers
        WHERE approval_id = %s
    """
    
    counts = hook.get_first(check_query, parameters=(approval_id,))
    total = counts[0]
    approved = counts[1]
    
    # Si todos han aprobado, actualizar estado general
    if approved == total:
        hook.run(
            """
            UPDATE contract_approvals
            SET approval_status = %s,
                approved_at = NOW()
            WHERE approval_id = %s
            """,
            parameters=(ApprovalStatus.APPROVED.value, approval_id)
        )
        
        # Actualizar metadata del contrato
        contract_query = """
            SELECT contract_id FROM contract_approvals WHERE approval_id = %s
        """
        contract_id = hook.get_first(contract_query, parameters=(approval_id,))[0]
        
        hook.run(
            """
            UPDATE contracts
            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                jsonb_build_object('approval_status', 'approved', 'approved_at', NOW())
            WHERE contract_id = %s
            """,
            parameters=(contract_id,)
        )
        
        logger.info(f"Todos los aprobadores han aprobado {approval_id}")
    
    return {
        "approval_id": approval_id,
        "approver_email": approver_email,
        "status": ApprovalStatus.APPROVED.value,
        "all_approved": approved == total,
        "approved_count": approved,
        "total_count": total,
        "approved_at": datetime.now().isoformat()
    }


def reject_approval(
    approval_id: str,
    approver_email: str,
    rejection_notes: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Rechaza una aprobación.
    
    Args:
        approval_id: ID de la aprobación
        approver_email: Email del aprobador
        rejection_notes: Motivo del rechazo
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información del rechazo
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Actualizar estado del aprobador
    hook.run(
        """
        UPDATE contract_approvers
        SET approval_status = %s,
            approval_notes = %s,
            rejected_at = NOW()
        WHERE approval_id = %s AND approver_email = %s
        """,
        parameters=(
            ApprovalStatus.REJECTED.value,
            rejection_notes,
            approval_id,
            approver_email
        )
    )
    
    # Rechazar aprobación completa
    hook.run(
        """
        UPDATE contract_approvals
        SET approval_status = %s,
            rejected_at = NOW()
        WHERE approval_id = %s
        """,
        parameters=(ApprovalStatus.REJECTED.value, approval_id)
    )
    
    # Actualizar metadata del contrato
    contract_query = """
        SELECT contract_id FROM contract_approvals WHERE approval_id = %s
    """
    contract_id = hook.get_first(contract_query, parameters=(approval_id,))[0]
    
    hook.run(
        """
        UPDATE contracts
        SET metadata = COALESCE(metadata, '{}'::jsonb) || 
            jsonb_build_object('approval_status', 'rejected', 'rejected_at', NOW())
        WHERE contract_id = %s
        """,
        parameters=(contract_id,)
    )
    
    logger.info(f"Aprobación rechazada: {approval_id}")
    
    return {
        "approval_id": approval_id,
        "approver_email": approver_email,
        "status": ApprovalStatus.REJECTED.value,
        "rejected_at": datetime.now().isoformat()
    }


def get_approval_status(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Optional[Dict[str, Any]]:
    """
    Obtiene el estado de aprobación de un contrato.
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con estado de aprobación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    query = """
        SELECT 
            a.approval_id,
            a.approval_status,
            a.approval_notes,
            a.requested_at,
            a.approved_at,
            a.rejected_at,
            COUNT(ap.approver_email) as total_approvers,
            COUNT(CASE WHEN ap.approval_status = 'approved' THEN 1 END) as approved_count,
            COUNT(CASE WHEN ap.approval_status = 'pending' THEN 1 END) as pending_count
        FROM contract_approvals a
        LEFT JOIN contract_approvers ap ON a.approval_id = ap.approval_id
        WHERE a.contract_id = %s
        GROUP BY a.approval_id, a.approval_status, a.approval_notes,
                 a.requested_at, a.approved_at, a.rejected_at
        ORDER BY a.requested_at DESC
        LIMIT 1
    """
    
    approval = hook.get_first(query, parameters=(contract_id,))
    
    if not approval:
        return None
    
    # Obtener aprobadores
    approvers_query = """
        SELECT approver_email, approver_name, approver_role,
               approval_order, approval_status, approved_at, rejected_at
        FROM contract_approvers
        WHERE approval_id = %s
        ORDER BY approval_order
    """
    
    approvers = hook.get_records(approvers_query, parameters=(approval[0],))
    
    return {
        "approval_id": approval[0],
        "status": approval[1],
        "notes": approval[2],
        "requested_at": approval[3].isoformat() if approval[3] else None,
        "approved_at": approval[4].isoformat() if approval[4] else None,
        "rejected_at": approval[5].isoformat() if approval[5] else None,
        "total_approvers": approval[6] or 0,
        "approved_count": approval[7] or 0,
        "pending_count": approval[8] or 0,
        "approvers": [
            {
                "email": a[0],
                "name": a[1],
                "role": a[2],
                "order": a[3],
                "status": a[4],
                "approved_at": a[5].isoformat() if a[5] else None,
                "rejected_at": a[6].isoformat() if a[6] else None
            }
            for a in approvers
        ]
    }

