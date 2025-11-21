"""
Dashboard de Métricas en Tiempo Real para Contratos
Genera datos para visualización de dashboards
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from data.airflow.plugins.contract_integrations import get_contract_analytics
from data.airflow.plugins.contract_ml import (
    predict_contract_signature_time,
    predict_contract_renewal_probability,
    get_contract_health_score
)

logger = logging.getLogger("airflow.task")


def get_dashboard_metrics(
    days_back: int = 30,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Obtiene métricas completas para dashboard.
    
    Args:
        days_back: Días hacia atrás para análisis
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con todas las métricas del dashboard
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    # Analytics básicos
    analytics = get_contract_analytics(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    # Métricas por tipo de contrato
    type_metrics_query = """
        SELECT 
            contract_type,
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'fully_signed' THEN 1 END) as signed,
            AVG(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as avg_days_to_sign
        FROM contracts
        WHERE created_at >= %s
        GROUP BY contract_type
    """
    type_metrics = {}
    for row in hook.get_records(type_metrics_query, parameters=(start_date,)):
        type_metrics[row[0]] = {
            "total": row[1] or 0,
            "signed": row[2] or 0,
            "avg_days_to_sign": round(float(row[3]), 1) if row[3] else 0.0
        }
    
    # Contratos por estado
    status_distribution_query = """
        SELECT 
            status,
            COUNT(*) as count
        FROM contracts
        WHERE created_at >= %s
        GROUP BY status
    """
    status_distribution = {}
    for row in hook.get_records(status_distribution_query, parameters=(start_date,)):
        status_distribution[row[0]] = row[1] or 0
    
    # Tendencias diarias (últimos 30 días)
    daily_trends_query = """
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as created,
            COUNT(CASE WHEN status = 'fully_signed' THEN 1 END) as signed
        FROM contracts
        WHERE created_at >= %s
        GROUP BY DATE(created_at)
        ORDER BY date
    """
    daily_trends = []
    for row in hook.get_records(daily_trends_query, parameters=(start_date,)):
        daily_trends.append({
            "date": row[0].isoformat() if row[0] else None,
            "created": row[1] or 0,
            "signed": row[2] or 0
        })
    
    # Contratos próximos a expirar
    expiring_query = """
        SELECT COUNT(*)
        FROM contracts
        WHERE status = 'fully_signed'
          AND expiration_date IS NOT NULL
          AND expiration_date <= CURRENT_DATE + INTERVAL '30 days'
          AND expiration_date > CURRENT_DATE
    """
    expiring_count = hook.get_first(expiring_query)[0] or 0
    
    # Contratos pendientes antiguos
    stale_query = """
        SELECT COUNT(*)
        FROM contracts
        WHERE status IN ('pending_signature', 'partially_signed')
          AND created_at < NOW() - INTERVAL '7 days'
    """
    stale_count = hook.get_first(stale_query)[0] or 0
    
    # Top firmantes (más contratos)
    top_signers_query = """
        SELECT 
            signer_email,
            COUNT(DISTINCT contract_id) as contract_count
        FROM contract_signers
        WHERE signature_status = 'signed'
        GROUP BY signer_email
        ORDER BY contract_count DESC
        LIMIT 10
    """
    top_signers = []
    for row in hook.get_records(top_signers_query):
        top_signers.append({
            "email": row[0],
            "contract_count": row[1] or 0
        })
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days_back
        },
        "summary": analytics,
        "by_type": type_metrics,
        "by_status": status_distribution,
        "daily_trends": daily_trends,
        "alerts": {
            "expiring_soon": expiring_count,
            "stale_pending": stale_count
        },
        "top_signers": top_signers,
        "generated_at": datetime.now().isoformat()
    }


def get_contract_detailed_view(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Obtiene vista detallada de un contrato para dashboard.
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con vista detallada completa
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener contrato
    contract_query = """
        SELECT 
            contract_id, title, contract_type, status, primary_party_name,
            primary_party_email, start_date, expiration_date, signed_date,
            created_at, esignature_provider, esignature_url, auto_renew
        FROM contracts
        WHERE contract_id = %s
    """
    contract = hook.get_first(contract_query, parameters=(contract_id,))
    
    if not contract:
        return {"error": "Contract not found"}
    
    # Obtener firmantes
    signers_query = """
        SELECT signer_email, signer_name, signer_role, signature_status,
               signature_sent_at, signature_signed_at, signer_order
        FROM contract_signers
        WHERE contract_id = %s
        ORDER BY signer_order
    """
    signers = hook.get_records(signers_query, parameters=(contract_id,))
    
    # Obtener eventos
    events_query = """
        SELECT event_type, event_description, event_timestamp, event_actor_email
        FROM contract_events
        WHERE contract_id = %s
        ORDER BY event_timestamp DESC
        LIMIT 20
    """
    events = hook.get_records(events_query, parameters=(contract_id,))
    
    # Obtener versiones
    versions_query = """
        SELECT version_number, signed_at, is_current, signed_document_hash
        FROM contract_versions
        WHERE contract_id = %s
        ORDER BY version_number DESC
    """
    versions = hook.get_records(versions_query, parameters=(contract_id,))
    
    # Obtener métricas ML
    try:
        health_score = get_contract_health_score(contract_id, postgres_conn_id)
        renewal_prob = predict_contract_renewal_probability(contract_id, postgres_conn_id)
    except Exception as e:
        logger.warning(f"Error obteniendo métricas ML: {e}")
        health_score = {}
        renewal_prob = {}
    
    return {
        "contract": {
            "contract_id": contract[0],
            "title": contract[1],
            "contract_type": contract[2],
            "status": contract[3],
            "primary_party_name": contract[4],
            "primary_party_email": contract[5],
            "start_date": contract[6].isoformat() if contract[6] else None,
            "expiration_date": contract[7].isoformat() if contract[7] else None,
            "signed_date": contract[8].isoformat() if contract[8] else None,
            "created_at": contract[9].isoformat() if contract[9] else None,
            "esignature_provider": contract[10],
            "esignature_url": contract[11],
            "auto_renew": contract[12]
        },
        "signers": [
            {
                "email": s[0],
                "name": s[1],
                "role": s[2],
                "status": s[3],
                "sent_at": s[4].isoformat() if s[4] else None,
                "signed_at": s[5].isoformat() if s[5] else None,
                "order": s[6]
            }
            for s in signers
        ],
        "events": [
            {
                "type": e[0],
                "description": e[1],
                "timestamp": e[2].isoformat() if e[2] else None,
                "actor": e[3]
            }
            for e in events
        ],
        "versions": [
            {
                "version_number": v[0],
                "signed_at": v[1].isoformat() if v[1] else None,
                "is_current": v[2],
                "document_hash": v[3]
            }
            for v in versions
        ],
        "metrics": {
            "health_score": health_score,
            "renewal_probability": renewal_prob
        }
    }

