"""
Helpers y funciones de conveniencia para ads reporting.

Incluye:
- Helpers de fecha
- Helpers de transformación
- Helpers de validación
- Helpers de formato
- Helpers de cálculo
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


def normalize_date(date_input: Any) -> str:
    """
    Normaliza una fecha a formato YYYY-MM-DD.
    
    Args:
        date_input: Puede ser string, datetime, o None
        
    Returns:
        String en formato YYYY-MM-DD
        
    Raises:
        ValueError: Si la fecha no puede ser parseada
    """
    if date_input is None:
        return datetime.now().strftime("%Y-%m-%d")
    
    if isinstance(date_input, str):
        try:
            # Intentar parsear varios formatos
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    dt = datetime.strptime(date_input, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            raise ValueError(f"Formato de fecha no reconocido: {date_input}")
        except Exception as e:
            raise ValueError(f"Error parseando fecha: {str(e)}")
    
    if isinstance(date_input, datetime):
        return date_input.strftime("%Y-%m-%d")
    
    if isinstance(date_input, timedelta):
        return (datetime.now() + date_input).strftime("%Y-%m-%d")
    
    raise ValueError(f"Tipo de fecha no soportado: {type(date_input)}")


def get_date_range(
    days_back: int = 7,
    date_start: Optional[str] = None,
    date_stop: Optional[str] = None
) -> Tuple[str, str]:
    """
    Obtiene un rango de fechas.
    
    Args:
        days_back: Días hacia atrás desde hoy (si date_start no se proporciona)
        date_start: Fecha inicio (opcional)
        date_stop: Fecha fin (opcional)
        
    Returns:
        Tuple (date_start, date_stop) en formato YYYY-MM-DD
    """
    if date_stop is None:
        date_stop = datetime.now().strftime("%Y-%m-%d")
    else:
        date_stop = normalize_date(date_stop)
    
    if date_start is None:
        date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    else:
        date_start = normalize_date(date_start)
    
    return (date_start, date_stop)


def calculate_ctr(clicks: int, impressions: int) -> float:
    """Calcula CTR (Click-Through Rate)."""
    if impressions == 0:
        return 0.0
    return (clicks / impressions) * 100


def calculate_cpc(spend: float, clicks: int) -> float:
    """Calcula CPC (Cost Per Click)."""
    if clicks == 0:
        return 0.0
    return spend / clicks


def calculate_cpa(spend: float, conversions: float) -> float:
    """Calcula CPA (Cost Per Acquisition)."""
    if conversions == 0:
        return 0.0
    return spend / conversions


def calculate_roas(revenue: float, spend: float) -> float:
    """Calcula ROAS (Return on Ad Spend)."""
    if spend == 0:
        return 0.0
    return revenue / spend


def calculate_conversion_rate(conversions: float, clicks: int) -> float:
    """Calcula tasa de conversión."""
    if clicks == 0:
        return 0.0
    return (conversions / clicks) * 100


def round_decimal(value: float, decimals: int = 2) -> float:
    """Redondea un valor a N decimales."""
    return float(Decimal(str(value)).quantize(
        Decimal('0.' + '0' * decimals),
        rounding=ROUND_HALF_UP
    ))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """División segura con valor por defecto si denominador es 0."""
    if denominator == 0:
        return default
    return numerator / denominator


def format_currency(amount: float, currency: str = "USD") -> str:
    """Formatea un monto como moneda."""
    return f"{currency} {amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Formatea un valor como porcentaje."""
    return f"{value:.{decimals}f}%"


def normalize_platform_data(
    data: Dict[str, Any],
    platform: str
) -> Dict[str, Any]:
    """
    Normaliza datos de diferentes plataformas a formato estándar.
    
    Args:
        data: Datos de cualquier plataforma
        platform: Nombre de la plataforma (facebook, tiktok, google)
        
    Returns:
        Datos normalizados
    """
    normalized = {
        "platform": platform,
        "date_start": data.get("date_start", ""),
        "date_stop": data.get("date_stop", ""),
    }
    
    # Mapeo de campos comunes
    field_mapping = {
        "facebook": {
            "campaign_id": "campaign_id",
            "adset_id": "adset_id",
            "ad_id": "ad_id",
        },
        "tiktok": {
            "campaign_id": "campaign_id",
            "ad_group_id": "ad_group_id",
            "ad_id": "ad_id",
        },
        "google": {
            "campaign_id": "campaign_id",
            "ad_group_id": "ad_group_id",
            "ad_id": "ad_id",
        }
    }
    
    mapping = field_mapping.get(platform, {})
    for standard_field, platform_field in mapping.items():
        normalized[standard_field] = data.get(platform_field, "")
    
    # Campos comunes
    normalized.update({
        "impressions": int(data.get("impressions", 0) or 0),
        "clicks": int(data.get("clicks", 0) or 0),
        "spend": float(data.get("spend", 0) or 0),
        "conversions": float(data.get("conversions", 0) or 0),
    })
    
    # Calcular métricas si no existen
    impressions = normalized["impressions"]
    clicks = normalized["clicks"]
    spend = normalized["spend"]
    conversions = normalized["conversions"]
    
    normalized["ctr"] = round_decimal(calculate_ctr(clicks, impressions), 4)
    normalized["cpc"] = round_decimal(calculate_cpc(spend, clicks), 4)
    normalized["cpa"] = round_decimal(calculate_cpa(spend, conversions), 2)
    normalized["conversion_rate"] = round_decimal(
        calculate_conversion_rate(conversions, clicks), 4
    )
    
    # Revenue/ROAS
    revenue = float(data.get("revenue") or (data.get("spend", 0) * data.get("roas", 0)) or 0)
    normalized["revenue"] = round_decimal(revenue, 2)
    normalized["roas"] = round_decimal(calculate_roas(revenue, spend), 4)
    
    return normalized


def merge_campaign_data(
    data_list: List[List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    Combina múltiples listas de datos de campañas.
    
    Args:
        data_list: Lista de listas de datos
        
    Returns:
        Lista combinada y normalizada
    """
    merged = []
    seen = set()
    
    for data in data_list:
        for record in data:
            # Crear clave única basada en identificadores
            key = (
                record.get("platform", "unknown"),
                record.get("campaign_id", ""),
                record.get("ad_id", ""),
                record.get("date_start", "")
            )
            
            if key not in seen:
                seen.add(key)
                merged.append(record)
    
    return merged


def filter_by_date_range(
    data: List[Dict[str, Any]],
    date_start: str,
    date_stop: str
) -> List[Dict[str, Any]]:
    """
    Filtra datos por rango de fechas.
    
    Args:
        data: Lista de datos
        date_start: Fecha inicio (YYYY-MM-DD)
        date_stop: Fecha fin (YYYY-MM-DD)
        
    Returns:
        Lista filtrada
    """
    start = datetime.strptime(date_start, "%Y-%m-%d")
    stop = datetime.strptime(date_stop, "%Y-%m-%d")
    
    filtered = []
    for record in data:
        record_date_str = record.get("date_start", "")
        if not record_date_str:
            continue
        
        try:
            record_date = datetime.strptime(record_date_str, "%Y-%m-%d")
            if start <= record_date <= stop:
                filtered.append(record)
        except ValueError:
            logger.warning(f"Fecha inválida en registro: {record_date_str}")
            continue
    
    return filtered


def aggregate_by_field(
    data: List[Dict[str, Any]],
    field: str,
    metrics: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    Agrega datos por un campo específico.
    
    Args:
        data: Lista de datos
        field: Campo por el cual agregar
        metrics: Lista de métricas a sumar
        
    Returns:
        Diccionario agrupado por campo
    """
    aggregated = {}
    
    for record in data:
        key = record.get(field, "unknown")
        
        if key not in aggregated:
            aggregated[key] = {field: key}
            for metric in metrics:
                aggregated[key][metric] = 0
        
        for metric in metrics:
            aggregated[key][metric] += float(record.get(metric, 0) or 0)
    
    return aggregated


def calculate_performance_score(
    record: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calcula un score de rendimiento combinado.
    
    Args:
        record: Datos de una campaña/anuncio
        weights: Pesos para cada métrica (opcional)
        
    Returns:
        Score de rendimiento (0-100)
    """
    if weights is None:
        weights = {
            "ctr": 0.3,
            "conversion_rate": 0.4,
            "roas": 0.3
        }
    
    ctr = record.get("ctr", 0) or 0
    conversion_rate = record.get("conversion_rate", 0) or 0
    roas = record.get("roas", 0) or 0
    
    # Normalizar valores (asumiendo rangos típicos)
    ctr_score = min(ctr / 5.0 * 100, 100)  # CTR máximo esperado ~5%
    conversion_score = min(conversion_rate / 10.0 * 100, 100)  # Conversión máxima ~10%
    roas_score = min(roas / 5.0 * 100, 100)  # ROAS máximo esperado ~5
    
    # Calcular score ponderado
    score = (
        ctr_score * weights.get("ctr", 0.33) +
        conversion_score * weights.get("conversion_rate", 0.33) +
        roas_score * weights.get("roas", 0.33)
    )
    
    return round_decimal(score, 2)


def detect_anomalies(
    data: List[Dict[str, Any]],
    field: str,
    threshold_std: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Detecta anomalías usando desviación estándar.
    
    Args:
        data: Lista de datos
        field: Campo a analizar
        threshold_std: Umbral en desviaciones estándar
        
    Returns:
        Lista de registros que son anomalías
    """
    if not data:
        return []
    
    # Calcular media y desviación estándar
    values = [float(r.get(field, 0) or 0) for r in data]
    
    if not values:
        return []
    
    import statistics
    try:
        mean = statistics.mean(values)
        if len(values) > 1:
            std = statistics.stdev(values)
        else:
            std = 0
        
        if std == 0:
            return []
        
        threshold_low = mean - (threshold_std * std)
        threshold_high = mean + (threshold_std * std)
        
        anomalies = []
        for record in data:
            value = float(record.get(field, 0) or 0)
            if value < threshold_low or value > threshold_high:
                anomalies.append(record)
        
        return anomalies
    except Exception as e:
        logger.warning(f"Error detectando anomalías: {str(e)}")
        return []


def calculate_mom_growth(
    current: float,
    previous: float
) -> float:
    """
    Calcula crecimiento mes a mes (MoM).
    
    Args:
        current: Valor actual
        previous: Valor anterior
        
    Returns:
        Porcentaje de crecimiento
    """
    if previous == 0:
        return 0.0 if current == 0 else 100.0
    
    return ((current - previous) / previous) * 100


def calculate_yoy_growth(
    current: float,
    previous: float
) -> float:
    """
    Calcula crecimiento año a año (YoY).
    
    Args:
        current: Valor actual
        previous: Valor del año anterior
        
    Returns:
        Porcentaje de crecimiento
    """
    return calculate_mom_growth(current, previous)


def format_large_number(num: float) -> str:
    """
    Formatea números grandes con K, M, B.
    
    Args:
        num: Número a formatear
        
    Returns:
        String formateado (ej: "1.5M", "2.3K")
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return f"{num:.0f}"


def validate_campaign_performance(
    record: Dict[str, Any],
    strict: bool = False
) -> tuple[bool, List[str]]:
    """
    Valida un registro de rendimiento de campaña.
    
    Args:
        record: Registro a validar
        strict: Si usar validación estricta
        
    Returns:
        Tuple (is_valid, errors)
    """
    errors = []
    
    # Campos requeridos
    required_fields = ["campaign_id", "impressions", "clicks", "spend"]
    for field in required_fields:
        if field not in record or record[field] is None:
            errors.append(f"Campo requerido '{field}' faltante")
    
    if errors and strict:
        return (False, errors)
    
    # Validar valores no negativos
    numeric_fields = ["impressions", "clicks", "spend", "conversions"]
    for field in numeric_fields:
        if field in record:
            value = record.get(field, 0)
            try:
                if float(value) < 0:
                    errors.append(f"Campo '{field}' no puede ser negativo")
            except (ValueError, TypeError):
                if strict:
                    errors.append(f"Campo '{field}' debe ser numérico")
    
    # Validar consistencia básica
    impressions = record.get("impressions", 0) or 0
    clicks = record.get("clicks", 0) or 0
    
    if clicks > impressions:
        errors.append("Clics no pueden ser mayores que impresiones")
    
    # Validar CTR si está presente
    if "ctr" in record and impressions > 0:
        calculated_ctr = (clicks / impressions * 100) if impressions > 0 else 0
        reported_ctr = float(record.get("ctr", 0) or 0)
        
        if abs(reported_ctr - calculated_ctr) > 5.0:  # Tolerancia 5%
            errors.append(f"CTR inconsistente: reportado {reported_ctr:.2f}%, calculado {calculated_ctr:.2f}%")
    
    return (len(errors) == 0, errors)


def enrich_with_calculations(
    record: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enriquece un registro con cálculos automáticos.
    
    Args:
        record: Registro a enriquecer
        
    Returns:
        Registro enriquecido
    """
    enriched = record.copy()
    
    impressions = float(enriched.get("impressions", 0) or 0)
    clicks = float(enriched.get("clicks", 0) or 0)
    spend = float(enriched.get("spend", 0) or 0)
    conversions = float(enriched.get("conversions", 0) or 0)
    revenue = float(enriched.get("revenue", 0) or 0)
    
    # Calcular métricas si no existen
    if "ctr" not in enriched or enriched.get("ctr") is None:
        enriched["ctr"] = calculate_ctr(clicks, impressions)
    
    if "cpc" not in enriched or enriched.get("cpc") is None:
        enriched["cpc"] = calculate_cpc(spend, clicks)
    
    if "cpa" not in enriched or enriched.get("cpa") is None:
        enriched["cpa"] = calculate_cpa(spend, conversions)
    
    if "roas" not in enriched or enriched.get("roas") is None:
        enriched["roas"] = calculate_roas(revenue, spend)
    
    if "conversion_rate" not in enriched or enriched.get("conversion_rate") is None:
        enriched["conversion_rate"] = calculate_conversion_rate(conversions, clicks)
    
    # Calcular CPM si hay impresiones
    if impressions > 0:
        enriched["cpm"] = (spend / impressions) * 1000
    
    return enriched


def create_summary_dict(
    data: List[Dict[str, Any]],
    include_details: bool = False
) -> Dict[str, Any]:
    """
    Crea diccionario resumen de datos.
    
    Args:
        data: Lista de datos
        include_details: Si incluir detalles por campaña
        
    Returns:
        Diccionario con resumen
    """
    if not data:
        return {
            "total_records": 0,
            "total_campaigns": 0,
            "summary": {}
        }
    
    from ads_reporting.processors import CampaignProcessor
    
    processor = CampaignProcessor()
    metrics = processor.calculate_metrics(data)
    
    summary = {
        "total_records": len(data),
        "total_campaigns": len(processor.group_by_campaign(data)),
        "summary": {
            "total_impressions": metrics.total_impressions,
            "total_clicks": metrics.total_clicks,
            "total_spend": metrics.total_spend,
            "total_conversions": metrics.total_conversions,
            "total_revenue": metrics.total_revenue,
            "avg_ctr": metrics.avg_ctr,
            "avg_cpc": metrics.avg_cpc,
            "avg_cpa": metrics.avg_cpa,
            "roas": metrics.roas,
            "conversion_rate": metrics.conversion_rate
        }
    }
    
    if include_details:
        summary["by_campaign"] = {
            campaign_id: {
                "records": len(campaign_data),
                "spend": sum(r.get("spend", 0) or 0 for r in campaign_data),
                "conversions": sum(r.get("conversions", 0) or 0 for r in campaign_data)
            }
            for campaign_id, campaign_data in processor.group_by_campaign(data).items()
        }
    
    return summary

