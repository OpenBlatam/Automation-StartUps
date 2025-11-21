"""
Estadísticas Avanzadas y Analytics para Contratos
Métricas detalladas, tendencias, comparativas y predicciones
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


def get_detailed_contract_statistics(
    start_date: str = None,
    end_date: str = None,
    contract_type: str = None,
    department: str = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Obtiene estadísticas detalladas de contratos.
    
    Args:
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
        contract_type: Filtrar por tipo
        department: Filtrar por departamento
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con estadísticas detalladas
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Construir filtros
    where_clauses = []
    params = []
    
    if start_date:
        where_clauses.append("created_at >= %s")
        params.append(start_date)
    
    if end_date:
        where_clauses.append("created_at <= %s")
        params.append(end_date + " 23:59:59")
    
    if contract_type:
        where_clauses.append("contract_type = %s")
        params.append(contract_type)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Estadísticas generales
    stats_query = f"""
        SELECT 
            COUNT(*) as total_contracts,
            COUNT(CASE WHEN status = 'fully_signed' THEN 1 END) as signed_contracts,
            COUNT(CASE WHEN status = 'pending_signature' THEN 1 END) as pending_contracts,
            COUNT(CASE WHEN status = 'expired' THEN 1 END) as expired_contracts,
            COUNT(CASE WHEN auto_renew = true THEN 1 END) as auto_renew_contracts,
            AVG(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as avg_days_to_sign,
            MIN(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as min_days_to_sign,
            MAX(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as max_days_to_sign,
            COUNT(CASE WHEN expiration_date < CURRENT_DATE AND status = 'fully_signed' THEN 1 END) as expired_but_active
        FROM contracts
        WHERE {where_sql}
    """
    
    stats = hook.get_first(stats_query, parameters=tuple(params))
    
    # Estadísticas por tipo
    type_query = f"""
        SELECT 
            contract_type,
            COUNT(*) as count,
            COUNT(CASE WHEN status = 'fully_signed' THEN 1 END) as signed_count,
            AVG(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as avg_days
        FROM contracts
        WHERE {where_sql}
        GROUP BY contract_type
        ORDER BY count DESC
    """
    
    type_stats = {}
    for row in hook.get_records(type_query, parameters=tuple(params)):
        type_stats[row[0]] = {
            "total": row[1],
            "signed": row[2],
            "avg_days_to_sign": round(float(row[3]), 1) if row[3] else 0.0
        }
    
    # Estadísticas por estado
    status_query = f"""
        SELECT 
            status,
            COUNT(*) as count
        FROM contracts
        WHERE {where_sql}
        GROUP BY status
        ORDER BY count DESC
    """
    
    status_stats = {}
    for row in hook.get_records(status_query, parameters=tuple(params)):
        status_stats[row[0]] = row[1]
    
    # Tendencias mensuales
    monthly_query = f"""
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            COUNT(*) as created,
            COUNT(CASE WHEN status = 'fully_signed' THEN 1 END) as signed
        FROM contracts
        WHERE {where_sql}
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY month DESC
        LIMIT 12
    """
    
    monthly_trends = []
    for row in hook.get_records(monthly_query, parameters=tuple(params)):
        monthly_trends.append({
            "month": row[0].isoformat() if hasattr(row[0], 'isoformat') else str(row[0]),
            "created": row[1],
            "signed": row[2]
        })
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "general": {
            "total_contracts": stats[0] or 0,
            "signed_contracts": stats[1] or 0,
            "pending_contracts": stats[2] or 0,
            "expired_contracts": stats[3] or 0,
            "auto_renew_contracts": stats[4] or 0,
            "signature_rate": round((stats[1] / stats[0] * 100) if stats[0] > 0 else 0, 2),
            "avg_days_to_sign": round(float(stats[5]), 1) if stats[5] else 0.0,
            "min_days_to_sign": round(float(stats[6]), 1) if stats[6] else 0.0,
            "max_days_to_sign": round(float(stats[7]), 1) if stats[7] else 0.0,
            "expired_but_active": stats[8] or 0
        },
        "by_type": type_stats,
        "by_status": status_stats,
        "monthly_trends": monthly_trends,
        "generated_at": datetime.now().isoformat()
    }


def get_contract_performance_metrics(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Obtiene métricas de rendimiento de un contrato específico.
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con métricas de rendimiento
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    query = """
        SELECT 
            created_at,
            signed_date,
            expiration_date,
            status,
            (SELECT COUNT(*) FROM contract_events WHERE contract_id = %s) as events_count,
            (SELECT COUNT(*) FROM contract_signers WHERE contract_id = %s) as signers_count,
            (SELECT COUNT(*) FROM contract_signers WHERE contract_id = %s AND signature_status = 'signed') as signed_signers_count,
            (SELECT MAX(signature_signed_at) FROM contract_signers WHERE contract_id = %s) as last_signature_date
        FROM contracts
        WHERE contract_id = %s
    """
    
    result = hook.get_first(
        query,
        parameters=(contract_id, contract_id, contract_id, contract_id, contract_id)
    )
    
    if not result:
        raise ValueError(f"Contrato {contract_id} no encontrado")
    
    created_at = result[0]
    signed_date = result[1]
    expiration_date = result[2]
    status = result[3]
    events_count = result[4] or 0
    signers_count = result[5] or 0
    signed_signers_count = result[6] or 0
    last_signature_date = result[7]
    
    # Calcular métricas
    metrics = {
        "contract_id": contract_id,
        "status": status,
        "signature_progress": round((signed_signers_count / signers_count * 100) if signers_count > 0 else 0, 2),
        "events_count": events_count,
        "signers_count": signers_count,
        "signed_signers_count": signed_signers_count
    }
    
    # Tiempo de firma
    if signed_date and created_at:
        days_to_sign = (signed_date - created_at).days
        metrics["days_to_sign"] = days_to_sign
        metrics["is_fast_signature"] = days_to_sign <= 7
    
    # Tiempo hasta expiración
    if expiration_date:
        days_until_expiration = (expiration_date - datetime.now().date()).days
        metrics["days_until_expiration"] = days_until_expiration
        metrics["is_expiring_soon"] = 0 <= days_until_expiration <= 30
    
    # Última actividad
    if last_signature_date:
        metrics["last_activity_date"] = last_signature_date.isoformat()
        days_since_activity = (datetime.now().date() - last_signature_date.date()).days
        metrics["days_since_last_activity"] = days_since_activity
    
    return metrics


def compare_periods_statistics(
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Compara estadísticas entre dos períodos.
    
    Args:
        period1_start: Inicio del período 1
        period1_end: Fin del período 1
        period2_start: Inicio del período 2
        period2_end: Fin del período 2
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con comparación
    """
    stats1 = get_detailed_contract_statistics(
        start_date=period1_start,
        end_date=period1_end,
        postgres_conn_id=postgres_conn_id
    )
    
    stats2 = get_detailed_contract_statistics(
        start_date=period2_start,
        end_date=period2_end,
        postgres_conn_id=postgres_conn_id
    )
    
    gen1 = stats1["general"]
    gen2 = stats2["general"]
    
    comparison = {
        "period1": {
            "start": period1_start,
            "end": period1_end,
            "stats": gen1
        },
        "period2": {
            "start": period2_start,
            "end": period2_end,
            "stats": gen2
        },
        "changes": {
            "total_contracts_change": gen2["total_contracts"] - gen1["total_contracts"],
            "total_contracts_change_pct": round(
                ((gen2["total_contracts"] - gen1["total_contracts"]) / gen1["total_contracts"] * 100)
                if gen1["total_contracts"] > 0 else 0,
                2
            ),
            "signature_rate_change": gen2["signature_rate"] - gen1["signature_rate"],
            "avg_days_change": gen2["avg_days_to_sign"] - gen1["avg_days_to_sign"]
        }
    }
    
    return comparison

