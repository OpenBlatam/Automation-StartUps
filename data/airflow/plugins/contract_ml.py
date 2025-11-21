"""
Módulo de Machine Learning para Contratos
Predicción de tiempo de firma, probabilidad de renovación, etc.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import numpy as np

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def predict_contract_signature_time(
    contract_type: str,
    signers_count: int,
    department: str = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Predice el tiempo esperado para firmar un contrato basado en datos históricos.
    
    Args:
        contract_type: Tipo de contrato
        signers_count: Número de firmantes
        department: Departamento (opcional)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con predicción y confianza
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener datos históricos
    query = """
        SELECT 
            AVG(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as avg_days,
            STDDEV(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as stddev_days,
            COUNT(*) as sample_size
        FROM contracts
        WHERE status = 'fully_signed'
          AND contract_type = %s
          AND signed_date IS NOT NULL
          AND created_at >= NOW() - INTERVAL '6 months'
    """
    
    result = hook.get_first(query, parameters=(contract_type,))
    
    if not result or not result[0]:
        # Fallback a promedio general
        fallback_query = """
            SELECT AVG(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400)
            FROM contracts
            WHERE status = 'fully_signed' AND signed_date IS NOT NULL
        """
        fallback_result = hook.get_first(fallback_query)
        avg_days = float(fallback_result[0]) if fallback_result and fallback_result[0] else 7.0
        stddev_days = 2.0
        sample_size = 0
    else:
        avg_days = float(result[0]) if result[0] else 7.0
        stddev_days = float(result[1]) if result[1] else 2.0
        sample_size = result[2] or 0
    
    # Ajustar por número de firmantes (más firmantes = más tiempo)
    signer_multiplier = 1.0 + (signers_count - 1) * 0.3
    predicted_days = avg_days * signer_multiplier
    
    # Calcular confianza basada en tamaño de muestra
    confidence = min(0.95, 0.5 + (sample_size / 100.0) * 0.45)
    
    return {
        "predicted_days": round(predicted_days, 1),
        "confidence": round(confidence, 2),
        "avg_historical_days": round(avg_days, 1),
        "stddev_days": round(stddev_days, 1),
        "sample_size": sample_size,
        "signers_count": signers_count,
        "factors": {
            "contract_type": contract_type,
            "signers_multiplier": round(signer_multiplier, 2)
        }
    }


def predict_contract_renewal_probability(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Predice la probabilidad de renovación de un contrato.
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con probabilidad y factores
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener datos del contrato
    query = """
        SELECT 
            contract_type, auto_renew, expiration_date, signed_date,
            primary_party_type, 
            COUNT(DISTINCT ce.id) as events_count
        FROM contracts c
        LEFT JOIN contract_events ce ON c.contract_id = ce.contract_id
        WHERE c.contract_id = %s
        GROUP BY c.contract_id, contract_type, auto_renew, expiration_date,
                 signed_date, primary_party_type
    """
    
    contract = hook.get_first(query, parameters=(contract_id,))
    
    if not contract:
        return {"error": "Contract not found"}
    
    contract_type = contract[0]
    auto_renew = contract[1]
    expiration_date = contract[2]
    signed_date = contract[3]
    primary_party_type = contract[4]
    events_count = contract[5] or 0
    
    # Calcular probabilidad base
    probability = 0.5  # Base 50%
    
    # Factor: auto_renew
    if auto_renew:
        probability += 0.3
    
    # Factor: tipo de contrato
    renewal_probabilities = {
        "employment": 0.8,
        "service": 0.6,
        "vendor": 0.7,
        "client": 0.75,
        "lease": 0.9,
        "nda": 0.3
    }
    type_prob = renewal_probabilities.get(contract_type, 0.5)
    probability = (probability + type_prob) / 2
    
    # Factor: tiempo desde firma (contratos más recientes tienen más probabilidad)
    if signed_date:
        days_since_signed = (datetime.now().date() - signed_date).days
        if days_since_signed < 365:
            probability += 0.1
        elif days_since_signed > 1095:  # Más de 3 años
            probability -= 0.1
    
    # Factor: eventos (más interacción = más probabilidad)
    if events_count > 5:
        probability += 0.05
    
    # Asegurar rango [0, 1]
    probability = max(0.0, min(1.0, probability))
    
    return {
        "contract_id": contract_id,
        "renewal_probability": round(probability, 2),
        "confidence": "high" if probability > 0.7 or probability < 0.3 else "medium",
        "factors": {
            "auto_renew": auto_renew,
            "contract_type": contract_type,
            "type_base_probability": round(type_prob, 2),
            "events_count": events_count,
            "primary_party_type": primary_party_type
        },
        "recommendation": "high" if probability > 0.7 else "medium" if probability > 0.5 else "low"
    }


def detect_contract_anomalies(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Detecta anomalías en un contrato (tiempo de firma, eventos, etc.).
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con anomalías detectadas
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener datos del contrato
    query = """
        SELECT 
            contract_type, status, created_at, signed_date,
            expiration_date, 
            EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400 as days_to_sign
        FROM contracts
        WHERE contract_id = %s
    """
    
    contract = hook.get_first(query, parameters=(contract_id,))
    
    if not contract:
        return {"error": "Contract not found"}
    
    anomalies = []
    
    # Anomalía: Tiempo de firma muy largo
    if contract[5] and contract[5] > 30:  # Más de 30 días
        anomalies.append({
            "type": "long_signature_time",
            "severity": "high",
            "description": f"Contrato tardó {contract[5]:.1f} días en firmarse (promedio: 7 días)",
            "value": contract[5]
        })
    
    # Anomalía: Estado pendiente por mucho tiempo
    if contract[1] in ("pending_signature", "partially_signed"):
        days_since_creation = (datetime.now().date() - contract[2].date()).days if contract[2] else 0
        if days_since_creation > 14:
            anomalies.append({
                "type": "stale_pending",
                "severity": "medium",
                "description": f"Contrato pendiente por {days_since_creation} días",
                "value": days_since_creation
            })
    
    # Anomalía: Contrato sin fecha de expiración pero firmado
    if contract[1] == "fully_signed" and not contract[4]:
        anomalies.append({
            "type": "missing_expiration",
            "severity": "medium",
            "description": "Contrato firmado sin fecha de expiración",
            "value": None
        })
    
    # Anomalía: Fecha de expiración en el pasado pero no marcado como expirado
    if contract[4] and contract[4] < datetime.now().date() and contract[1] != "expired":
        anomalies.append({
            "type": "expired_not_marked",
            "severity": "high",
            "description": f"Contrato expiró el {contract[4]} pero no está marcado como expirado",
            "value": contract[4].isoformat()
        })
    
    return {
        "contract_id": contract_id,
        "anomalies_detected": len(anomalies),
        "anomalies": anomalies,
        "has_anomalies": len(anomalies) > 0
    }


def get_contract_health_score(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Calcula un score de salud para un contrato (0-100).
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con score y factores
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener datos del contrato
    query = """
        SELECT 
            status, created_at, signed_date, expiration_date,
            contract_type, auto_renew,
            (SELECT COUNT(*) FROM contract_events WHERE contract_id = %s) as events_count,
            (SELECT COUNT(*) FROM contract_signers WHERE contract_id = %s) as signers_count,
            (SELECT COUNT(*) FROM contract_versions WHERE contract_id = %s AND is_current = true) as has_version
        FROM contracts
        WHERE contract_id = %s
    """
    
    contract = hook.get_first(query, parameters=(contract_id, contract_id, contract_id, contract_id))
    
    if not contract:
        return {"error": "Contract not found"}
    
    score = 100.0
    factors = []
    
    # Factor: Estado
    status_scores = {
        "fully_signed": 30,
        "partially_signed": 20,
        "pending_signature": 10,
        "draft": 5,
        "expired": 0,
        "cancelled": 0
    }
    status_score = status_scores.get(contract[0], 10)
    score = min(score, status_score * 3)  # Máximo 30 puntos
    factors.append({"factor": "status", "score": status_score, "max": 30})
    
    # Factor: Tiempo de firma razonable
    if contract[2] and contract[1]:
        days_to_sign = (contract[2] - contract[1]).days if contract[1] else 0
        if days_to_sign <= 7:
            score += 20
            factors.append({"factor": "fast_signature", "score": 20, "max": 20})
        elif days_to_sign <= 14:
            score += 10
            factors.append({"factor": "acceptable_signature", "score": 10, "max": 20})
        else:
            factors.append({"factor": "slow_signature", "score": 0, "max": 20})
    
    # Factor: Tiene versión almacenada
    if contract[8] and contract[8] > 0:
        score += 20
        factors.append({"factor": "has_version", "score": 20, "max": 20})
    else:
        factors.append({"factor": "missing_version", "score": 0, "max": 20})
    
    # Factor: Tiene eventos registrados
    if contract[6] and contract[6] >= 3:
        score += 15
        factors.append({"factor": "good_audit_trail", "score": 15, "max": 15})
    elif contract[6] and contract[6] > 0:
        score += 10
        factors.append({"factor": "basic_audit_trail", "score": 10, "max": 15})
    else:
        factors.append({"factor": "no_audit_trail", "score": 0, "max": 15})
    
    # Factor: Auto-renew configurado si aplica
    if contract[5] and contract[3]:  # auto_renew y expiration_date
        score += 15
        factors.append({"factor": "auto_renew_enabled", "score": 15, "max": 15})
    else:
        factors.append({"factor": "no_auto_renew", "score": 0, "max": 15})
    
    # Asegurar rango [0, 100]
    score = max(0.0, min(100.0, score))
    
    # Determinar nivel de salud
    if score >= 80:
        health_level = "excellent"
    elif score >= 60:
        health_level = "good"
    elif score >= 40:
        health_level = "fair"
    else:
        health_level = "poor"
    
    return {
        "contract_id": contract_id,
        "health_score": round(score, 1),
        "health_level": health_level,
        "factors": factors,
        "max_score": 100.0
    }

