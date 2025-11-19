"""
Funciones de optimización y recomendaciones.

Incluye:
- Recomendaciones de optimización
- Análisis de oportunidades
- Sugerencias de mejora
- Detección de ineficiencias
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OptimizationRecommendation:
    """Recomendación de optimización."""
    type: str
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    impact: str
    action: str
    estimated_improvement: Optional[str] = None


def analyze_campaign_efficiency(
    data: List[Dict[str, Any]]
) -> List[OptimizationRecommendation]:
    """
    Analiza eficiencia de campañas y genera recomendaciones.
    
    Args:
        data: Lista de datos de campañas
        
    Returns:
        Lista de recomendaciones de optimización
    """
    recommendations = []
    
    if not data:
        return recommendations
    
    from ads_reporting.processors import CampaignProcessor
    processor = CampaignProcessor()
    metrics = processor.calculate_metrics(data)
    
    # Analizar CTR
    if metrics.avg_ctr < 1.0:
        recommendations.append(OptimizationRecommendation(
            type="ctr_low",
            priority="high",
            title="CTR Bajo",
            description=f"CTR promedio es {metrics.avg_ctr:.2f}%, está por debajo del promedio de la industria (1-2%)",
            impact="Bajo engagement y posible desperdicio de presupuesto en impresiones",
            action="Revisar creativos, headlines y targeting. Considerar A/B testing",
            estimated_improvement="Mejora esperada: +0.5-1% CTR"
        ))
    
    # Analizar CPA
    avg_cpa = metrics.avg_cpa
    if avg_cpa > 50:  # Asumiendo CPA objetivo < $50
        recommendations.append(OptimizationRecommendation(
            type="cpa_high",
            priority="high",
            title="CPA Alto",
            description=f"CPA promedio es ${avg_cpa:.2f}, puede estar por encima del objetivo",
            impact="Bajo retorno de inversión y posible pérdida en conversiones",
            action="Optimizar landing pages, mejorar targeting, ajustar pujas",
            estimated_improvement="Reducción esperada: 10-20% CPA"
        ))
    
    # Analizar ROAS
    if metrics.roas < 2.0:
        recommendations.append(OptimizationRecommendation(
            type="roas_low",
            priority="high",
            title="ROAS Bajo",
            description=f"ROAS es {metrics.roas:.2f}, idealmente debería ser > 2.0",
            impact="Bajo retorno sobre inversión publicitaria",
            action="Pausar bajo performers, incrementar presupuesto en top performers, optimizar audiences",
            estimated_improvement="Mejora esperada: +0.5-1.0 ROAS"
        ))
    
    # Analizar conversiones
    conversion_rate = metrics.conversion_rate
    if conversion_rate < 2.0:
        recommendations.append(OptimizationRecommendation(
            type="conversion_rate_low",
            priority="medium",
            title="Tasa de Conversión Baja",
            description=f"Tasa de conversión es {conversion_rate:.2f}%, por debajo del ideal (2-5%)",
            impact="Bajo número de conversiones a pesar de clics",
            action="Optimizar landing pages, mejorar UX, revisar funnel de conversión",
            estimated_improvement="Mejora esperada: +1-2% tasa de conversión"
        ))
    
    # Detectar campañas con muchos clics pero sin conversiones
    campaigns_without_conversions = [
        r for r in data
        if r.get("clicks", 0) > 100 and r.get("conversions", 0) == 0
    ]
    
    if len(campaigns_without_conversions) > len(data) * 0.2:  # Más del 20%
        recommendations.append(OptimizationRecommendation(
            type="no_conversions",
            priority="high",
            title="Campañas sin Conversiones",
            description=f"{len(campaigns_without_conversions)} campañas tienen >100 clics pero 0 conversiones",
            impact="Desperdicio significativo de presupuesto",
            action="Pausar o optimizar estas campañas. Revisar targeting y landing pages",
            estimated_improvement="Ahorro: redirigir presupuesto a campañas que convierten"
        ))
    
    return recommendations


def suggest_budget_reallocation(
    data: List[Dict[str, Any]],
    current_total_budget: float
) -> Dict[str, Any]:
    """
    Sugiere reasignación de presupuesto basada en rendimiento.
    
    Args:
        data: Lista de datos de campañas
        current_total_budget: Presupuesto total actual
        
    Returns:
        Diccionario con sugerencias de reasignación
    """
    if not data:
        return {"suggestions": []}
    
    from ads_reporting.analytics import find_top_performers, find_bottom_performers
    
    # Identificar top y bottom performers
    top_performers = find_top_performers(data, metric="roas", top_n=5)
    bottom_performers = find_bottom_performers(data, metric="cpa", bottom_n=5)
    
    suggestions = []
    
    # Calcular presupuesto actual por campaña
    total_current_spend = sum(r.get("spend", 0) or 0 for r in data)
    
    if total_current_spend == 0:
        total_current_spend = current_total_budget
    
    for bottom in bottom_performers:
        campaign_id = bottom.get("campaign_id", "")
        current_spend = bottom.get("spend", 0) or 0
        roas = bottom.get("roas", 0) or 0
        cpa = bottom.get("cpa", 0) or 0
        
        if roas < 1.5 or cpa > 100:
            suggestions.append({
                "campaign_id": campaign_id,
                "campaign_name": bottom.get("campaign_name", ""),
                "action": "pausar_o_reducir",
                "current_spend": current_spend,
                "suggested_spend": current_spend * 0.2,  # Reducir a 20%
                "reason": f"ROAS bajo ({roas:.2f}) o CPA alto (${cpa:.2f})",
                "budget_to_reallocate": current_spend * 0.8
            })
    
    for top in top_performers:
        campaign_id = top.get("campaign_id", "")
        current_spend = top.get("spend", 0) or 0
        roas = top.get("roas", 0) or 0
        
        if roas > 3.0:
            suggestions.append({
                "campaign_id": campaign_id,
                "campaign_name": top.get("campaign_name", ""),
                "action": "incrementar",
                "current_spend": current_spend,
                "suggested_spend": current_spend * 1.5,  # Incrementar 50%
                "reason": f"ROAS alto ({roas:.2f}), buen rendimiento",
                "additional_budget_needed": current_spend * 0.5
            })
    
    # Calcular ahorro potencial
    total_to_reallocate = sum(
        s.get("budget_to_reallocate", 0) for s in suggestions
        if s.get("action") == "pausar_o_reducir"
    )
    
    total_needed = sum(
        s.get("additional_budget_needed", 0) for s in suggestions
        if s.get("action") == "incrementar"
    )
    
    return {
        "suggestions": suggestions,
        "total_budget_to_reallocate": total_to_reallocate,
        "total_budget_needed": total_needed,
        "net_impact": total_to_reallocate - total_needed,
        "recommendation": "reducir" if total_to_reallocate > total_needed else "aumentar"
    }


def detect_waste(
    data: List[Dict[str, Any]],
    thresholds: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Detecta desperdicio de presupuesto.
    
    Args:
        data: Lista de datos de campañas
        thresholds: Umbrales personalizados
        
    Returns:
        Diccionario con análisis de desperdicio
    """
    if thresholds is None:
        thresholds = {
            "min_ctr": 0.5,
            "max_cpa": 100.0,
            "min_roas": 1.0,
            "min_clicks_for_conversion": 50
        }
    
    waste_campaigns = []
    
    for record in data:
        issues = []
        
        ctr = record.get("ctr", 0) or 0
        cpa = record.get("cpa", 0) or 0
        roas = record.get("roas", 0) or 0
        clicks = record.get("clicks", 0) or 0
        conversions = record.get("conversions", 0) or 0
        spend = record.get("spend", 0) or 0
        
        if ctr < thresholds["min_ctr"]:
            issues.append(f"CTR bajo ({ctr:.2f}%)")
        
        if cpa > thresholds["max_cpa"]:
            issues.append(f"CPA alto (${cpa:.2f})")
        
        if roas < thresholds["min_roas"]:
            issues.append(f"ROAS bajo ({roas:.2f})")
        
        if clicks >= thresholds["min_clicks_for_conversion"] and conversions == 0:
            issues.append(f"{clicks} clics sin conversiones")
        
        if issues:
            waste_campaigns.append({
                "campaign_id": record.get("campaign_id", ""),
                "campaign_name": record.get("campaign_name", ""),
                "spend": spend,
                "issues": issues,
                "waste_score": len(issues) * spend / 100  # Score basado en número de issues y spend
            })
    
    total_waste = sum(w.get("spend", 0) for w in waste_campaigns)
    
    return {
        "waste_campaigns": waste_campaigns,
        "total_waste_potential": total_waste,
        "waste_percentage": (total_waste / sum(r.get("spend", 1) or 1 for r in data) * 100) if data else 0,
        "recommendation": "revisar" if total_waste > 0 else "ninguna"
    }


def optimize_ad_schedule(
    data: List[Dict[str, Any]],
    day_field: str = "day_of_week",
    hour_field: str = "hour"
) -> Dict[str, Any]:
    """
    Optimiza horarios de anuncios basado en rendimiento.
    
    Args:
        data: Lista de datos con información de día/hora
        day_field: Campo con día de la semana
        hour_field: Campo con hora del día
        
    Returns:
        Diccionario con recomendaciones de horarios
    """
    if not data:
        return {"recommendations": []}
    
    from ads_reporting.analytics import segment_analysis
    
    # Analizar por día
    day_analysis = segment_analysis(
        [r for r in data if day_field in r],
        segment_field=day_field,
        metrics=["spend", "conversions", "roas", "cpa"]
    )
    
    # Analizar por hora
    hour_analysis = {}
    if hour_field:
        hour_analysis = segment_analysis(
            [r for r in data if hour_field in r],
            segment_field=hour_field,
            metrics=["spend", "conversions", "roas", "cpa"]
        )
    
    # Encontrar mejores y peores horarios
    best_days = sorted(
        day_analysis.items(),
        key=lambda x: x[1].get("roas", 0),
        reverse=True
    )[:3]
    
    worst_days = sorted(
        day_analysis.items(),
        key=lambda x: x[1].get("roas", 0)
    )[:3]
    
    recommendations = []
    
    # Recomendar días para incrementar presupuesto
    for day, metrics in best_days:
        recommendations.append({
            "type": "increase_budget",
            "time_period": f"Día: {day}",
            "reason": f"ROAS alto ({metrics.get('roas', 0):.2f}), buen rendimiento",
            "current_spend": metrics.get("spend", 0),
            "suggested_increase": "30-50%"
        })
    
    # Recomendar días para reducir o pausar
    for day, metrics in worst_days:
        if metrics.get("roas", 0) < 1.0:
            recommendations.append({
                "type": "reduce_budget",
                "time_period": f"Día: {day}",
                "reason": f"ROAS bajo ({metrics.get('roas', 0):.2f}), bajo rendimiento",
                "current_spend": metrics.get("spend", 0),
                "suggested_reduction": "50-70%"
            })
    
    return {
        "recommendations": recommendations,
        "best_days": [d[0] for d in best_days],
        "worst_days": [d[0] for d in worst_days],
        "day_analysis": day_analysis,
        "hour_analysis": hour_analysis
    }

