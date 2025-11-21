"""
Sistema de Auditoría Avanzado para Contratos
Tracking completo de cambios, acceso y modificaciones
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


def log_audit_event(
    contract_id: str,
    event_type: str,
    event_description: str,
    actor_email: str = None,
    actor_role: str = None,
    event_data: Dict[str, Any] = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Registra un evento de auditoría.
    
    Args:
        contract_id: ID del contrato
        event_type: Tipo de evento
        event_description: Descripción del evento
        actor_email: Email del actor
        actor_role: Rol del actor
        event_data: Datos adicionales del evento
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información del evento registrado
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    import json
    
    # Insertar evento
    insert_query = """
        INSERT INTO contract_events (
            contract_id, event_type, event_description,
            event_actor_email, event_actor_role, event_data, event_timestamp
        ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
        RETURNING id
    """
    
    event_data_json = json.dumps(event_data) if event_data else "{}"
    
    result = hook.get_first(
        insert_query,
        parameters=(
            contract_id,
            event_type,
            event_description,
            actor_email,
            actor_role,
            event_data_json
        )
    )
    
    event_id = result[0] if result else None
    
    logger.info(
        f"Evento de auditoría registrado",
        extra={
            "contract_id": contract_id,
            "event_type": event_type,
            "event_id": event_id
        }
    )
    
    return {
        "event_id": event_id,
        "contract_id": contract_id,
        "event_type": event_type,
        "event_description": event_description,
        "actor_email": actor_email,
        "actor_role": actor_role,
        "timestamp": datetime.now().isoformat()
    }


def get_contract_audit_trail(
    contract_id: str,
    start_date: datetime = None,
    end_date: datetime = None,
    event_type: str = None,
    postgres_conn_id: str = "postgres_default"
) -> List[Dict[str, Any]]:
    """
    Obtiene el trail completo de auditoría de un contrato.
    
    Args:
        contract_id: ID del contrato
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
        event_type: Filtrar por tipo (opcional)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Lista de eventos de auditoría
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    where_clauses = ["contract_id = %s"]
    params = [contract_id]
    
    if start_date:
        where_clauses.append("event_timestamp >= %s")
        params.append(start_date)
    
    if end_date:
        where_clauses.append("event_timestamp <= %s")
        params.append(end_date)
    
    if event_type:
        where_clauses.append("event_type = %s")
        params.append(event_type)
    
    query = f"""
        SELECT 
            id, event_type, event_description, event_actor_email,
            event_actor_role, event_data, event_timestamp
        FROM contract_events
        WHERE {' AND '.join(where_clauses)}
        ORDER BY event_timestamp ASC
    """
    
    events = hook.get_records(query, parameters=tuple(params))
    
    import json
    
    return [
        {
            "event_id": row[0],
            "event_type": row[1],
            "event_description": row[2],
            "actor_email": row[3],
            "actor_role": row[4],
            "event_data": json.loads(row[5]) if row[5] else {},
            "timestamp": row[6].isoformat() if row[6] else None
        }
        for row in events
    ]


def get_user_activity_report(
    user_email: str,
    start_date: datetime = None,
    end_date: datetime = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Obtiene reporte de actividad de un usuario.
    
    Args:
        user_email: Email del usuario
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con reporte de actividad
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    where_clauses = ["event_actor_email = %s"]
    params = [user_email]
    
    if start_date:
        where_clauses.append("event_timestamp >= %s")
        params.append(start_date)
    
    if end_date:
        where_clauses.append("event_timestamp <= %s")
        params.append(end_date)
    
    # Estadísticas de actividad
    stats_query = f"""
        SELECT 
            COUNT(*) as total_events,
            COUNT(DISTINCT contract_id) as contracts_accessed,
            COUNT(DISTINCT event_type) as event_types_count,
            MIN(event_timestamp) as first_activity,
            MAX(event_timestamp) as last_activity
        FROM contract_events
        WHERE {' AND '.join(where_clauses)}
    """
    
    stats = hook.get_first(stats_query, parameters=tuple(params))
    
    # Eventos por tipo
    type_query = f"""
        SELECT 
            event_type,
            COUNT(*) as count
        FROM contract_events
        WHERE {' AND '.join(where_clauses)}
        GROUP BY event_type
        ORDER BY count DESC
    """
    
    events_by_type = {}
    for row in hook.get_records(type_query, parameters=tuple(params)):
        events_by_type[row[0]] = row[1]
    
    # Contratos más accedidos
    contracts_query = f"""
        SELECT 
            contract_id,
            COUNT(*) as access_count
        FROM contract_events
        WHERE {' AND '.join(where_clauses)}
        GROUP BY contract_id
        ORDER BY access_count DESC
        LIMIT 10
    """
    
    top_contracts = []
    for row in hook.get_records(contracts_query, parameters=tuple(params)):
        top_contracts.append({
            "contract_id": row[0],
            "access_count": row[1]
        })
    
    return {
        "user_email": user_email,
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "statistics": {
            "total_events": stats[0] or 0,
            "contracts_accessed": stats[1] or 0,
            "event_types_count": stats[2] or 0,
            "first_activity": stats[3].isoformat() if stats[3] else None,
            "last_activity": stats[4].isoformat() if stats[4] else None
        },
        "events_by_type": events_by_type,
        "top_contracts": top_contracts,
        "generated_at": datetime.now().isoformat()
    }


def get_compliance_report(
    start_date: datetime = None,
    end_date: datetime = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Genera reporte de compliance y auditoría.
    
    Args:
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con reporte de compliance
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    where_clauses = []
    params = []
    
    if start_date:
        where_clauses.append("created_at >= %s")
        params.append(start_date)
    
    if end_date:
        where_clauses.append("created_at <= %s")
        params.append(end_date)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Contratos sin eventos de auditoría
    no_audit_query = f"""
        SELECT COUNT(*)
        FROM contracts c
        WHERE {where_sql}
          AND NOT EXISTS (
              SELECT 1 FROM contract_events ce WHERE ce.contract_id = c.contract_id
          )
    """
    
    no_audit_count = hook.get_first(no_audit_query, parameters=tuple(params))[0] or 0
    
    # Contratos sin revisión legal cuando se requiere
    no_legal_review_query = f"""
        SELECT COUNT(*)
        FROM contracts
        WHERE {where_sql}
          AND requires_legal_review = true
          AND legal_reviewed = false
    """
    
    no_legal_review_count = hook.get_first(no_legal_review_query, parameters=tuple(params))[0] or 0
    
    # Eventos de auditoría totales
    total_events_query = f"""
        SELECT COUNT(*)
        FROM contract_events ce
        JOIN contracts c ON ce.contract_id = c.contract_id
        WHERE {where_sql.replace('created_at', 'ce.event_timestamp')}
    """
    
    total_events = hook.get_first(total_events_query, parameters=tuple(params))[0] or 0
    
    return {
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "compliance_metrics": {
            "contracts_without_audit": no_audit_count,
            "contracts_without_legal_review": no_legal_review_count,
            "total_audit_events": total_events,
            "compliance_score": calculate_compliance_score(
                no_audit_count,
                no_legal_review_count,
                total_events
            )
        },
        "generated_at": datetime.now().isoformat()
    }


def calculate_compliance_score(
    no_audit_count: int,
    no_legal_review_count: int,
    total_events: int
) -> float:
    """Calcula score de compliance (0-100)"""
    # Score base
    score = 100.0
    
    # Penalizar contratos sin auditoría
    if no_audit_count > 0:
        score -= min(30, no_audit_count * 2)
    
    # Penalizar contratos sin revisión legal
    if no_legal_review_count > 0:
        score -= min(40, no_legal_review_count * 3)
    
    # Bonus por eventos de auditoría
    if total_events > 100:
        score += min(10, (total_events - 100) / 10)
    
    return max(0.0, min(100.0, score))

