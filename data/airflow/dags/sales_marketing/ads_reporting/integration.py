"""
Integraciones y helpers para usar en DAGs de Airflow.

Proporciona funciones de alto nivel que combinan múltiples módulos.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ads_reporting.base_client import BaseAdsClient
from ads_reporting.extractors import BaseExtractor
from ads_reporting.storage import BaseStorage
from ads_reporting.processors import CampaignProcessor
from ads_reporting.analytics import (
    analyze_trends,
    compare_periods,
    segment_analysis,
    find_top_performers,
    calculate_lift,
)
from ads_reporting.validators import validate_campaign_data
from ads_reporting.cache import get_cache
from ads_reporting.config import get_config

logger = logging.getLogger(__name__)

try:
    from ads_reporting_utils import (
        check_api_credentials,
        check_database_connection,
        validate_date_range,
        check_data_quality_campaigns,
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False


def extract_and_store(
    client: BaseAdsClient,
    extractor: BaseExtractor,
    storage: BaseStorage,
    date_start: str,
    date_stop: str,
    table_name: str = "ads_performance",
    use_cache: bool = True,
    validate: bool = True,
    process: bool = True
) -> Dict[str, Any]:
    """
    Función de alto nivel que extrae, valida, procesa y almacena datos.
    
    Args:
        client: Cliente de la API
        extractor: Extractor de datos
        storage: Almacenador de datos
        date_start: Fecha inicio
        date_stop: Fecha fin
        table_name: Nombre de tabla
        use_cache: Si usar caché
        validate: Si validar datos
        process: Si procesar datos
        
    Returns:
        Diccionario con resultados de la operación
    """
    global_config = get_config()
    results = {
        "extracted": 0,
        "validated": False,
        "processed": False,
        "saved": 0,
        "errors": 0,
        "from_cache": False
    }
    
    # Caché
    cache = None
    if use_cache and global_config.cache_enabled:
        cache = get_cache()
        cached_data = cache.get(
            client.config.platform,
            "campaign_performance",
            {"date_start": date_start, "date_stop": date_stop}
        )
        if cached_data is not None:
            results["from_cache"] = True
            data = cached_data
        else:
            # Extracción
            data = extractor.extract_campaign_performance(date_start, date_stop)
            cache.set(
                client.config.platform,
                "campaign_performance",
                {"date_start": date_start, "date_stop": date_stop},
                data
            )
    else:
        # Extracción sin caché
        data = extractor.extract_campaign_performance(date_start, date_stop)
    
    results["extracted"] = len(data)
    
    if not data:
        return results
    
    # Validación
    if validate:
        validation_result = validate_campaign_data(
            data,
            strict=global_config.strict_validation
        )
        results["validated"] = validation_result.valid
        if not validation_result.valid and global_config.strict_validation:
            raise ValueError(f"Validación falló: {validation_result.errors}")
    
    # Procesamiento
    processed_data = data
    if process:
        processor = CampaignProcessor()
        processed_data = processor.normalize(data)
        metrics = processor.calculate_metrics(processed_data)
        results["processed"] = True
        results["metrics"] = {
            "total_impressions": metrics.total_impressions,
            "total_clicks": metrics.total_clicks,
            "total_spend": metrics.total_spend,
            "avg_ctr": metrics.avg_ctr,
            "roas": metrics.roas
        }
    
    # Data quality (si está habilitado)
    if global_config.enable_dq_checks and UTILS_AVAILABLE:
        dq_check = check_data_quality_campaigns(processed_data, client.config.platform)
        results["dq_passed"] = dq_check.passed
        if dq_check.issues:
            results["dq_issues"] = dq_check.issues
    
    # Almacenamiento
    storage_result = storage.save_campaign_performance(processed_data, table_name)
    results["saved"] = storage_result.get("saved", 0)
    results["errors"] = storage_result.get("errors", 0)
    
    return results


def compare_platforms(
    extractors: Dict[str, BaseExtractor],
    date_start: str,
    date_stop: str
) -> Dict[str, Any]:
    """
    Compara rendimiento entre múltiples plataformas.
    
    Args:
        extractors: Diccionario de extractores por plataforma
        date_start: Fecha inicio
        date_stop: Fecha fin
        
    Returns:
        Diccionario con comparación de plataformas
    """
    comparison = {
        "date_start": date_start,
        "date_stop": date_stop,
        "platforms": {}
    }
    
    processor = CampaignProcessor()
    
    for platform, extractor in extractors.items():
        try:
            data = extractor.extract_campaign_performance(date_start, date_stop)
            normalized = processor.normalize(data)
            metrics = processor.calculate_metrics(normalized)
            
            comparison["platforms"][platform] = {
                "total_records": len(normalized),
                "total_spend": metrics.total_spend,
                "total_conversions": metrics.total_conversions,
                "avg_ctr": metrics.avg_ctr,
                "avg_cpc": metrics.avg_cpc,
                "avg_cpa": metrics.avg_cpa,
                "roas": metrics.roas
            }
        except Exception as e:
            logger.error(f"Error extrayendo datos de {platform}: {str(e)}")
            comparison["platforms"][platform] = {"error": str(e)}
    
    # Calcular rankings
    if len(comparison["platforms"]) > 1:
        # Ranking por ROAS
        platforms_by_roas = sorted(
            [(p, d.get("roas", 0)) for p, d in comparison["platforms"].items() if "error" not in d],
            key=lambda x: x[1],
            reverse=True
        )
        comparison["rankings"] = {
            "by_roas": [p for p, _ in platforms_by_roas],
            "by_cpa": sorted(
                [(p, d.get("avg_cpa", float('inf'))) for p, d in comparison["platforms"].items() if "error" not in d],
                key=lambda x: x[1]
            )[:1][0][0] if platforms_by_roas else None
        }
    
    return comparison


def optimize_campaign_budget(
    data: List[Dict[str, Any]],
    total_budget: float,
    min_budget: float = 10.0
) -> Dict[str, Any]:
    """
    Optimiza distribución de presupuesto entre campañas.
    
    Args:
        data: Lista de datos de campañas
        total_budget: Presupuesto total disponible
        min_budget: Presupuesto mínimo por campaña
        
    Returns:
        Diccionario con distribución optimizada
    """
    from ads_reporting.helpers import safe_divide
    
    if not data:
        return {"allocations": {}, "total_allocated": 0.0}
    
    # Calcular score de rendimiento para cada campaña
    scores = []
    for record in data:
        roas = float(record.get("roas", 0) or 0)
        ctr = float(record.get("ctr", 0) or 0)
        conversion_rate = float(record.get("conversion_rate", 0) or 0)
        
        # Score combinado
        score = (roas * 0.5) + (ctr * 0.3) + (conversion_rate * 0.2)
        
        scores.append({
            "campaign_id": record.get("campaign_id", ""),
            "campaign_name": record.get("campaign_name", ""),
            "current_spend": float(record.get("spend", 0) or 0),
            "score": score,
            "roas": roas
        })
    
    # Ordenar por score
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Distribuir presupuesto proporcionalmente
    total_score = sum(s["score"] for s in scores)
    
    allocations = {}
    allocated = 0.0
    
    for i, score_data in enumerate(scores):
        if total_score > 0:
            proportion = score_data["score"] / total_score
            allocation = total_budget * proportion
        else:
            allocation = total_budget / len(scores)
        
        # Asegurar mínimo
        allocation = max(allocation, min_budget)
        
        # Asegurar que no exceda el total
        if allocated + allocation > total_budget:
            allocation = total_budget - allocated
        
        if allocation > 0:
            allocations[score_data["campaign_id"]] = {
                "campaign_name": score_data["campaign_name"],
                "current_spend": score_data["current_spend"],
                "recommended_budget": allocation,
                "change": allocation - score_data["current_spend"],
                "change_percent": ((allocation - score_data["current_spend"]) / score_data["current_spend"] * 100) if score_data["current_spend"] > 0 else 0
            }
            allocated += allocation
    
    return {
        "allocations": allocations,
        "total_allocated": allocated,
        "remaining_budget": total_budget - allocated
    }


def generate_performance_report(
    data: List[Dict[str, Any]],
    date_start: str,
    date_stop: str
) -> Dict[str, Any]:
    """
    Genera un reporte completo de rendimiento.
    
    Args:
        data: Lista de datos de campañas
        date_start: Fecha inicio
        date_stop: Fecha fin
        
    Returns:
        Diccionario con reporte completo
    """
    processor = CampaignProcessor()
    
    # Normalizar y calcular métricas
    normalized = processor.normalize(data)
    metrics = processor.calculate_metrics(normalized)
    
    # Agrupar por campaña
    by_campaign = processor.group_by_campaign(normalized)
    
    # Top performers
    top_performers = processor.filter_by_performance(
        normalized,
        min_ctr=1.0,
        max_cpc=10.0
    )
    
    # Agrupar por fecha
    by_date = processor.group_by_date(normalized)
    
    # Calcular crecimiento diario
    daily_growth = []
    dates = sorted(by_date.keys())
    for i in range(1, len(dates)):
        prev_metrics = processor.calculate_metrics(by_date[dates[i-1]])
        curr_metrics = processor.calculate_metrics(by_date[dates[i]])
        
        growth = {
            "date": dates[i],
            "spend_growth": ((curr_metrics.total_spend - prev_metrics.total_spend) / prev_metrics.total_spend * 100) if prev_metrics.total_spend > 0 else 0,
            "conversions_growth": ((curr_metrics.total_conversions - prev_metrics.total_conversions) / prev_metrics.total_conversions * 100) if prev_metrics.total_conversions > 0 else 0
        }
        daily_growth.append(growth)
    
    return {
        "period": {
            "start": date_start,
            "stop": date_stop,
            "days": (datetime.strptime(date_stop, "%Y-%m-%d") - datetime.strptime(date_start, "%Y-%m-%d")).days + 1
        },
        "summary": {
            "total_records": len(normalized),
            "total_campaigns": len(by_campaign),
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
        },
        "top_performers": {
            "count": len(top_performers),
            "campaigns": top_performers[:10]
        },
        "daily_growth": daily_growth,
        "by_campaign": {
            campaign_id: processor.calculate_metrics(campaign_data)
            for campaign_id, campaign_data in list(by_campaign.items())[:10]
        },
        "top_performers_details": find_top_performers(normalized, "roas", 10)
    }

