"""
Sistema de Alertas Inteligentes
Detección proactiva de problemas y alertas automáticas
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


def detect_contract_issues(
    postgres_conn_id: str = "postgres_default"
) -> List[Dict[str, Any]]:
    """
    Detecta problemas y anomalías en contratos.
    
    Args:
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Lista de problemas detectados
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    issues = []
    
    # Contratos pendientes por mucho tiempo
    stale_query = """
        SELECT contract_id, title, created_at, status
        FROM contracts
        WHERE status IN ('pending_signature', 'partially_signed')
          AND created_at < NOW() - INTERVAL '30 days'
        ORDER BY created_at ASC
        LIMIT 50
    """
    
    stale_contracts = hook.get_records(stale_query)
    for row in stale_contracts:
        issues.append({
            "contract_id": row[0],
            "issue_type": "stale_pending",
            "severity": "high",
            "title": f"Contrato pendiente por más de 30 días",
            "description": f"El contrato '{row[1]}' está pendiente desde {row[2]}",
            "contract_title": row[1],
            "created_at": row[2].isoformat() if hasattr(row[2], 'isoformat') else str(row[2])
        })
    
    # Contratos expirados pero no marcados
    expired_not_marked_query = """
        SELECT contract_id, title, expiration_date, status
        FROM contracts
        WHERE expiration_date < CURRENT_DATE
          AND status != 'expired'
          AND status != 'terminated'
        ORDER BY expiration_date ASC
        LIMIT 50
    """
    
    expired_contracts = hook.get_records(expired_not_marked_query)
    for row in expired_contracts:
        issues.append({
            "contract_id": row[0],
            "issue_type": "expired_not_marked",
            "severity": "high",
            "title": f"Contrato expirado no marcado",
            "description": f"El contrato '{row[1]}' expiró el {row[2]} pero no está marcado como expirado",
            "contract_title": row[1],
            "expiration_date": row[2].isoformat() if hasattr(row[2], 'isoformat') else str(row[2])
        })
    
    # Contratos sin revisión legal cuando se requiere
    no_legal_review_query = """
        SELECT contract_id, title, requires_legal_review, legal_reviewed
        FROM contracts
        WHERE requires_legal_review = true
          AND legal_reviewed = false
          AND status IN ('draft', 'pending_signature')
        LIMIT 50
    """
    
    no_review_contracts = hook.get_records(no_legal_review_query)
    for row in no_review_contracts:
        issues.append({
            "contract_id": row[0],
            "issue_type": "missing_legal_review",
            "severity": "medium",
            "title": f"Falta revisión legal",
            "description": f"El contrato '{row[1]}' requiere revisión legal pero no ha sido revisado",
            "contract_title": row[1]
        })
    
    # Contratos sin versión almacenada después de firma
    no_version_query = """
        SELECT c.contract_id, c.title, c.signed_date
        FROM contracts c
        WHERE c.status = 'fully_signed'
          AND c.signed_date IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM contract_versions cv 
              WHERE cv.contract_id = c.contract_id
          )
        LIMIT 50
    """
    
    no_version_contracts = hook.get_records(no_version_query)
    for row in no_version_contracts:
        issues.append({
            "contract_id": row[0],
            "issue_type": "missing_signed_version",
            "severity": "high",
            "title": f"Versión firmada no almacenada",
            "description": f"El contrato '{row[1]}' fue firmado el {row[2]} pero no tiene versión almacenada",
            "contract_title": row[1],
            "signed_date": row[2].isoformat() if hasattr(row[2], 'isoformat') else str(row[2])
        })
    
    return issues


def send_intelligent_alerts(
    issues: List[Dict[str, Any]] = None,
    notification_channels: List[str] = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Envía alertas inteligentes basadas en problemas detectados.
    
    Args:
        issues: Lista de problemas (si None, detecta automáticamente)
        notification_channels: Canales ['email', 'slack'] (opcional)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con resultado de alertas enviadas
    """
    if issues is None:
        issues = detect_contract_issues(postgres_conn_id)
    
    notification_channels = notification_channels or ["slack"]
    
    results = {
        "issues_detected": len(issues),
        "alerts_sent": 0,
        "errors": []
    }
    
    # Agrupar por severidad
    high_severity = [i for i in issues if i.get("severity") == "high"]
    medium_severity = [i for i in issues if i.get("severity") == "medium"]
    low_severity = [i for i in issues if i.get("severity") == "low"]
    
    # Enviar alertas
    if "slack" in notification_channels:
        try:
            from data.airflow.plugins.contract_notifications import send_slack_notification
            
            if high_severity:
                send_slack_notification(
                    message=f"🚨 {len(high_severity)} problemas de alta severidad detectados",
                    color="danger",
                    details={
                        "issues": high_severity[:10]  # Limitar a 10
                    }
                )
                results["alerts_sent"] += 1
            
            if medium_severity:
                send_slack_notification(
                    message=f"⚠️ {len(medium_severity)} problemas de severidad media detectados",
                    color="warning",
                    details={
                        "issues": medium_severity[:10]
                    }
                )
                results["alerts_sent"] += 1
        except Exception as e:
            results["errors"].append(f"Error enviando Slack: {e}")
    
    if "email" in notification_channels:
        try:
            # TODO: Implementar envío por email
            logger.info("Email notifications not yet implemented")
        except Exception as e:
            results["errors"].append(f"Error enviando email: {e}")
    
    return results


def get_contract_health_dashboard(
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Obtiene dashboard de salud del sistema de contratos.
    
    Args:
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con métricas de salud
    """
    issues = detect_contract_issues(postgres_conn_id)
    
    # Agrupar por tipo
    issues_by_type = {}
    for issue in issues:
        issue_type = issue.get("issue_type", "unknown")
        issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
    
    # Calcular health score
    total_issues = len(issues)
    high_severity_count = len([i for i in issues if i.get("severity") == "high"])
    medium_severity_count = len([i for i in issues if i.get("severity") == "medium"])
    
    # Score base 100, penalizar por problemas
    health_score = 100.0
    health_score -= high_severity_count * 10
    health_score -= medium_severity_count * 5
    health_score = max(0.0, health_score)
    
    return {
        "health_score": round(health_score, 1),
        "health_status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
        "total_issues": total_issues,
        "high_severity_issues": high_severity_count,
        "medium_severity_issues": medium_severity_count,
        "issues_by_type": issues_by_type,
        "generated_at": datetime.now().isoformat()
    }

