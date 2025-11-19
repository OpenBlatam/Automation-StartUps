"""
Funciones de análisis avanzadas para datos de ads.

Incluye:
- Análisis de tendencias
- Comparaciones temporales
- Detección de cambios significativos
- Análisis de segmentación
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import statistics
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False


@dataclass
class TrendAnalysis:
    """Análisis de tendencias."""
    metric: str
    current_value: float
    previous_value: float
    change_percent: float
    trend: str  # "up", "down", "stable"
    significance: str  # "significant", "moderate", "minor"


@dataclass
class ComparisonResult:
    """Resultado de comparación."""
    metric: str
    baseline_value: float
    comparison_value: float
    difference: float
    difference_percent: float
    is_significant: bool


def analyze_trends(
    current_data: List[Dict[str, Any]],
    previous_data: List[Dict[str, Any]],
    metric: str = "spend"
) -> List[TrendAnalysis]:
    """
    Analiza tendencias entre dos períodos.
    
    Args:
        current_data: Datos del período actual
        previous_data: Datos del período anterior
        metric: Métrica a analizar
        
    Returns:
        Lista de análisis de tendencias
    """
    from ads_reporting.processors import CampaignProcessor
    
    processor = CampaignProcessor()
    
    # Calcular métricas agregadas
    current_metrics = processor.calculate_metrics(current_data)
    previous_metrics = processor.calculate_metrics(previous_data)
    
    trends = []
    metrics_to_analyze = [
        ("spend", "total_spend"),
        ("conversions", "total_conversions"),
        ("impressions", "total_impressions"),
        ("clicks", "total_clicks"),
        ("ctr", "avg_ctr"),
        ("roas", "roas"),
    ]
    
    for metric_name, metric_attr in metrics_to_analyze:
        current_val = getattr(current_metrics, metric_attr, 0)
        previous_val = getattr(previous_metrics, metric_attr, 0)
        
        if previous_val == 0:
            change_percent = 100.0 if current_val > 0 else 0.0
        else:
            change_percent = ((current_val - previous_val) / previous_val) * 100
        
        # Determinar tendencia
        if abs(change_percent) < 1.0:
            trend = "stable"
            significance = "minor"
        elif abs(change_percent) < 10.0:
            trend = "up" if change_percent > 0 else "down"
            significance = "moderate"
        else:
            trend = "up" if change_percent > 0 else "down"
            significance = "significant"
        
        trends.append(TrendAnalysis(
            metric=metric_name,
            current_value=current_val,
            previous_value=previous_val,
            change_percent=change_percent,
            trend=trend,
            significance=significance
        ))
    
    return trends


def compare_periods(
    period1_data: List[Dict[str, Any]],
    period2_data: List[Dict[str, Any]],
    metric: str = "spend"
) -> Dict[str, ComparisonResult]:
    """
    Compara dos períodos de datos.
    
    Args:
        period1_data: Datos del período 1 (baseline)
        period2_data: Datos del período 2 (comparación)
        metric: Métrica principal a comparar
        
    Returns:
        Diccionario con comparaciones por métrica
    """
    from ads_reporting.processors import CampaignProcessor
    
    processor = CampaignProcessor()
    
    metrics1 = processor.calculate_metrics(period1_data)
    metrics2 = processor.calculate_metrics(period2_data)
    
    comparisons = {}
    
    metrics_to_compare = {
        "spend": ("total_spend", "total_spend"),
        "conversions": ("total_conversions", "total_conversions"),
        "ctr": ("avg_ctr", "avg_ctr"),
        "cpc": ("avg_cpc", "avg_cpc"),
        "cpa": ("avg_cpa", "avg_cpa"),
        "roas": ("roas", "roas"),
    }
    
    for metric_name, (attr1, attr2) in metrics_to_compare.items():
        baseline = getattr(metrics1, attr1, 0)
        comparison = getattr(metrics2, attr2, 0)
        
        difference = comparison - baseline
        
        if baseline == 0:
            diff_percent = 0.0 if comparison == 0 else 100.0
        else:
            diff_percent = (difference / baseline) * 100
        
        # Determinar si es significativo (>10% cambio)
        is_significant = abs(diff_percent) > 10.0
        
        comparisons[metric_name] = ComparisonResult(
            metric=metric_name,
            baseline_value=baseline,
            comparison_value=comparison,
            difference=difference,
            difference_percent=diff_percent,
            is_significant=is_significant
        )
    
    return comparisons


def detect_significant_changes(
    data: List[Dict[str, Any]],
    field: str,
    threshold_percent: float = 20.0
) -> List[Dict[str, Any]]:
    """
    Detecta cambios significativos en un campo.
    
    Args:
        data: Lista de datos
        field: Campo a analizar
        threshold_percent: Umbral de cambio significativo
        
    Returns:
        Lista de registros con cambios significativos
    """
    if len(data) < 2 or not STATS_AVAILABLE:
        return []
    
    values = [float(r.get(field, 0) or 0) for r in data]
    
    if not values:
        return []
    
    mean = statistics.mean(values)
    if mean == 0:
        return []
    
    # Detectar valores que están fuera del umbral
    threshold_value = mean * (threshold_percent / 100)
    
    significant_changes = []
    for i, record in enumerate(data):
        value = float(record.get(field, 0) or 0)
        if abs(value - mean) > threshold_value:
            significant_changes.append({
                **record,
                "change_from_mean": value - mean,
                "change_percent": ((value - mean) / mean * 100) if mean > 0 else 0
            })
    
    return significant_changes


def segment_analysis(
    data: List[Dict[str, Any]],
    segment_field: str,
    metrics: List[str] = None
) -> Dict[str, Dict[str, float]]:
    """
    Analiza datos por segmento.
    
    Args:
        data: Lista de datos
        segment_field: Campo para segmentar (ej: "campaign_id", "audience_type")
        metrics: Métricas a calcular por segmento
        
    Returns:
        Diccionario con métricas por segmento
    """
    if metrics is None:
        metrics = ["spend", "conversions", "roas", "ctr"]
    
    segments = {}
    
    for record in data:
        segment_key = record.get(segment_field, "unknown")
        
        if segment_key not in segments:
            segments[segment_key] = {
                "count": 0,
                **{m: 0.0 for m in metrics}
            }
        
        segments[segment_key]["count"] += 1
        
        for metric in metrics:
            value = float(record.get(metric, 0) or 0)
            segments[segment_key][metric] += value
    
    # Calcular promedios
    for segment_key, segment_data in segments.items():
        count = segment_data["count"]
        if count > 0:
            for metric in metrics:
                if metric in ["ctr", "roas", "cpc", "cpa"]:
                    # Estas son ratios, mantener como están o calcular promedio
                    segment_data[metric] = segment_data[metric] / count if count > 1 else segment_data[metric]
    
    return segments


def calculate_lift(
    test_group: List[Dict[str, Any]],
    control_group: List[Dict[str, Any]],
    metric: str = "conversions"
) -> Dict[str, float]:
    """
    Calcula el lift entre grupo de prueba y control.
    
    Args:
        test_group: Datos del grupo de prueba
        control_group: Datos del grupo de control
        metric: Métrica a analizar
        
    Returns:
        Diccionario con lift y métricas relacionadas
    """
    from ads_reporting.helpers import safe_divide
    
    test_total = sum(float(r.get(metric, 0) or 0) for r in test_group)
    control_total = sum(float(r.get(metric, 0) or 0) for r in control_group)
    
    if control_total == 0:
        return {
            "lift_percent": 0.0,
            "test_value": test_total,
            "control_value": control_total,
            "absolute_lift": test_total
        }
    
    lift_percent = ((test_total - control_total) / control_total) * 100
    
    return {
        "lift_percent": lift_percent,
        "test_value": test_total,
        "control_value": control_total,
        "absolute_lift": test_total - control_total
    }


def find_top_performers(
    data: List[Dict[str, Any]],
    metric: str = "roas",
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Encuentra los top performers por métrica.
    
    Args:
        data: Lista de datos
        metric: Métrica para ranking
        top_n: Número de top performers a retornar
        
    Returns:
        Lista de top performers
    """
    sorted_data = sorted(
        data,
        key=lambda x: float(x.get(metric, 0) or 0),
        reverse=True
    )
    
    return sorted_data[:top_n]


def find_bottom_performers(
    data: List[Dict[str, Any]],
    metric: str = "cpa",
    bottom_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Encuentra los peores performers por métrica.
    
    Args:
        data: Lista de datos
        metric: Métrica para ranking (más bajo es mejor)
        bottom_n: Número de bottom performers a retornar
        
    Returns:
        Lista de bottom performers
    """
    sorted_data = sorted(
        data,
        key=lambda x: float(x.get(metric, float('inf')) or float('inf'))
    )
    
    return sorted_data[:bottom_n]

