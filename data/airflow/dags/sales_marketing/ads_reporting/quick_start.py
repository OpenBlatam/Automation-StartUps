"""
Funciones de inicio rápido para casos de uso comunes.

Proporciona funciones de alto nivel que encapsulan flujos completos
para facilitar el uso del sistema.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ads_reporting.facebook_client import FacebookAdsClient, FacebookAdsConfig
from ads_reporting.extractors import FacebookExtractor
from ads_reporting.storage import get_storage
from ads_reporting.integration import extract_and_store
from ads_reporting.reporting import format_report_summary, export_to_csv
from ads_reporting.helpers import get_date_range

logger = logging.getLogger(__name__)


def quick_extract_facebook(
    days_back: int = 7,
    table_name: str = "facebook_ads_performance",
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Extracción rápida de Facebook Ads.
    
    Args:
        days_back: Días hacia atrás desde hoy
        table_name: Nombre de tabla para almacenar
        use_cache: Si usar caché
        
    Returns:
        Diccionario con resultados
    """
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
    )
    
    date_start, date_stop = get_date_range(days_back=days_back)
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        storage = get_storage("postgres")
        
        result = extract_and_store(
            client, extractor, storage,
            date_start, date_stop,
            table_name=table_name,
            use_cache=use_cache,
            validate=True,
            process=True
        )
    
    return result


def quick_report_facebook(
    days_back: int = 7,
    format_type: str = "text"
) -> str:
    """
    Genera reporte rápido de Facebook Ads.
    
    Args:
        days_back: Días hacia atrás desde hoy
        format_type: Tipo de formato (text, markdown, html)
        
    Returns:
        String con reporte formateado
    """
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
    )
    
    date_start, date_stop = get_date_range(days_back=days_back)
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        data = extractor.extract_campaign_performance(date_start, date_stop)
        
        from ads_reporting.integration import generate_performance_report
        report = generate_performance_report(data, date_start, date_stop)
        
        return format_report_summary(report.get("summary", {}), format_type=format_type)


def quick_export_facebook(
    days_back: int = 7,
    filepath: Optional[str] = None,
    format_type: str = "csv"
) -> str:
    """
    Extrae y exporta datos de Facebook Ads rápidamente.
    
    Args:
        days_back: Días hacia atrás desde hoy
        filepath: Ruta del archivo (auto-genera si None)
        format_type: Tipo de exportación (csv, json)
        
    Returns:
        Ruta del archivo o string con datos
    """
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
    )
    
    date_start, date_stop = get_date_range(days_back=days_back)
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        data = extractor.extract_campaign_performance(date_start, date_stop)
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"facebook_ads_{timestamp}.{format_type}"
        
        if format_type == "csv":
            return export_to_csv(data, filepath=filepath)
        elif format_type == "json":
            from ads_reporting.reporting import export_to_json
            return export_to_json(data, filepath=filepath)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")


def quick_compare_periods(
    period1_days: int = 7,
    period2_days: int = 7,
    period2_offset: int = 7
) -> Dict[str, Any]:
    """
    Compara dos períodos de datos rápidamente.
    
    Args:
        period1_days: Días del período 1
        period2_days: Días del período 2
        period2_offset: Offset en días para período 2 (desde hoy)
        
    Returns:
        Diccionario con comparación
    """
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
    )
    
    # Período 1 (más reciente)
    date_start1, date_stop1 = get_date_range(days_back=period1_days)
    
    # Período 2 (anterior)
    date_start2 = (datetime.now() - timedelta(days=period2_offset + period2_days)).strftime("%Y-%m-%d")
    date_stop2 = (datetime.now() - timedelta(days=period2_offset)).strftime("%Y-%m-%d")
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        
        data1 = extractor.extract_campaign_performance(date_start1, date_stop1)
        data2 = extractor.extract_campaign_performance(date_start2, date_stop2)
        
        from ads_reporting.analytics import compare_periods
        comparison = compare_periods(data1, data2)
        
        return {
            "period1": {"start": date_start1, "stop": date_stop1, "data_count": len(data1)},
            "period2": {"start": date_start2, "stop": date_stop2, "data_count": len(data2)},
            "comparison": comparison
        }


def quick_optimize_campaigns(
    days_back: int = 30
) -> Dict[str, Any]:
    """
    Análisis rápido de optimización de campañas.
    
    Args:
        days_back: Días hacia atrás para análisis
        
    Returns:
        Diccionario con recomendaciones y análisis
    """
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
    )
    
    date_start, date_stop = get_date_range(days_back=days_back)
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        data = extractor.extract_campaign_performance(date_start, date_stop)
        
        from ads_reporting.optimization import (
            analyze_campaign_efficiency,
            suggest_budget_reallocation,
            detect_waste
        )
        
        # Calcular presupuesto total actual
        total_spend = sum(r.get("spend", 0) or 0 for r in data)
        
        recommendations = analyze_campaign_efficiency(data)
        budget_suggestions = suggest_budget_reallocation(data, total_spend)
        waste_analysis = detect_waste(data)
        
        return {
            "period": {"start": date_start, "stop": date_stop},
            "total_campaigns": len(data),
            "total_spend": total_spend,
            "recommendations": [
                {
                    "priority": r.priority,
                    "title": r.title,
                    "description": r.description,
                    "action": r.action
                }
                for r in recommendations
            ],
            "budget_suggestions": budget_suggestions,
            "waste_analysis": waste_analysis
        }

