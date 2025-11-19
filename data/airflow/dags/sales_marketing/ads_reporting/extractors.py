"""
Extractores modulares de datos para cada plataforma.

Separa la lógica de extracción de datos de la lógica de almacenamiento.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ads_reporting.base_client import BaseAdsClient
from ads_reporting.facebook_client import FacebookAdsClient
from ads_reporting.tiktok_client import TikTokAdsClient
from ads_reporting.google_client import GoogleAdsClient

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Extractor base para datos de ads."""
    
    def __init__(self, client: BaseAdsClient):
        """
        Inicializa el extractor.
        
        Args:
            client: Cliente de la API
        """
        self.client = client
    
    @abstractmethod
    def extract_campaign_performance(
        self,
        date_start: str,
        date_stop: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Extrae datos de rendimiento de campañas.
        
        Args:
            date_start: Fecha inicio (YYYY-MM-DD)
            date_stop: Fecha fin (YYYY-MM-DD)
            **kwargs: Parámetros adicionales específicos de la plataforma
            
        Returns:
            Lista de datos de campañas
        """
        pass
    
    @abstractmethod
    def extract_audience_performance(
        self,
        date_start: str,
        date_stop: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extrae datos de rendimiento por audiencia.
        
        Args:
            date_start: Fecha inicio
            date_stop: Fecha fin
            **kwargs: Parámetros adicionales
            
        Returns:
            Diccionario con datos de audiencias
        """
        pass


class FacebookExtractor(BaseExtractor):
    """Extractor para Facebook Ads."""
    
    def __init__(self, client: FacebookAdsClient):
        """Inicializa el extractor de Facebook."""
        super().__init__(client)
        self.client: FacebookAdsClient = client
    
    def extract_campaign_performance(
        self,
        date_start: str,
        date_stop: str,
        level: str = "ad",
        breakdowns: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Extrae datos de rendimiento de campañas de Facebook."""
        with self.client._track_operation("extract_campaign_performance"):
            fields = [
                "campaign_id", "campaign_name",
                "adset_id", "adset_name",
                "ad_id", "ad_name",
                "impressions", "clicks",
                "ctr", "cpc",
                "actions", "spend",
                "action_values"
            ]
            
            params = {
                'time_range': {
                    'since': date_start,
                    'until': date_stop
                },
                'level': level,
                'limit': 1000
            }
            
            if breakdowns:
                params['breakdowns'] = breakdowns
            
            insights = self.client.get_insights(fields, params, use_sdk=True)
            
            # Procesar y normalizar datos
            results = []
            for insight in insights:
                processed = self._process_insight(insight, date_start, date_stop)
                if processed:
                    results.append(processed)
            
            return results
    
    def _process_insight(
        self,
        insight: Dict[str, Any],
        date_start: str,
        date_stop: str
    ) -> Optional[Dict[str, Any]]:
        """Procesa un insight individual."""
        try:
            # Calcular métricas
            impressions = int(insight.get("impressions", 0) or 0)
            clicks = int(insight.get("clicks", 0) or 0)
            ctr = float(insight.get("ctr", 0) or 0)
            cpc = float(insight.get("cpc", 0) or 0)
            spend = float(insight.get("spend", 0) or 0)
            
            # Procesar conversiones
            actions = insight.get("actions", []) or []
            conversions = sum(
                float(action.get("value", 0) or 0)
                for action in actions
                if isinstance(action, dict) and 
                action.get("action_type") in ["purchase", "complete_registration", "lead"]
            )
            
            # Calcular ROAS
            action_values = insight.get("action_values", []) or []
            revenue = sum(
                float(av.get("value", 0) or 0)
                for av in action_values
                if isinstance(av, dict) and av.get("action_type") == "purchase"
            )
            roas = (revenue / spend) if spend > 0 else 0.0
            
            return {
                "date_start": date_start,
                "date_stop": date_stop,
                "campaign_id": str(insight.get("campaign_id", "") or ""),
                "campaign_name": str(insight.get("campaign_name", "") or ""),
                "adset_id": str(insight.get("adset_id", "") or ""),
                "adset_name": str(insight.get("adset_name", "") or ""),
                "ad_id": str(insight.get("ad_id", "") or ""),
                "ad_name": str(insight.get("ad_name", "") or ""),
                "impressions": impressions,
                "clicks": clicks,
                "ctr": ctr,
                "cpc": cpc,
                "conversions": conversions,
                "roas": roas,
                "spend": spend,
                "platform": "facebook"
            }
        except Exception as e:
            logger.warning(f"Error procesando insight: {str(e)}")
            return None
    
    def extract_audience_performance(
        self,
        date_start: str,
        date_stop: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Extrae datos de rendimiento por audiencia."""
        with self.client._track_operation("extract_audience_performance"):
            # Obtener datos con breakdown por audiencia
            campaign_data = self.extract_campaign_performance(
                date_start, date_stop,
                breakdowns=["audience_type"]
            )
            
            # Agrupar por audiencia
            audience_stats = {}
            for data in campaign_data:
                audience_type = data.get("audience_type", "unknown")
                if audience_type not in audience_stats:
                    audience_stats[audience_type] = {
                        "spend": 0,
                        "conversions": 0,
                        "revenue": 0
                    }
                
                audience_stats[audience_type]["spend"] += data.get("spend", 0)
                audience_stats[audience_type]["conversions"] += data.get("conversions", 0)
                audience_stats[audience_type]["revenue"] += (
                    data.get("spend", 0) * data.get("roas", 0)
                )
            
            # Calcular métricas por audiencia
            audiences = []
            total_spend = sum(s["spend"] for s in audience_stats.values())
            total_conversions = sum(s["conversions"] for s in audience_stats.values())
            avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            
            for audience_type, stats in audience_stats.items():
                conversions = stats["conversions"]
                spend = stats["spend"]
                cpa = (spend / conversions) if conversions > 0 else 0
                
                audiences.append({
                    "audience_type": audience_type,
                    "spend": spend,
                    "conversions": conversions,
                    "revenue": stats["revenue"],
                    "cpa": cpa,
                    "cpa_vs_avg": ((cpa - avg_cpa) / avg_cpa * 100) if avg_cpa > 0 else 0
                })
            
            return {
                "date_start": date_start,
                "date_stop": date_stop,
                "average_cpa": avg_cpa,
                "audiences": audiences
            }


class TikTokExtractor(BaseExtractor):
    """Extractor para TikTok Ads."""
    
    def __init__(self, client: TikTokAdsClient):
        """Inicializa el extractor de TikTok."""
        super().__init__(client)
        self.client: TikTokAdsClient = client
    
    def extract_campaign_performance(
        self,
        date_start: str,
        date_stop: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Extrae datos de rendimiento de campañas de TikTok."""
        with self.client._track_operation("extract_campaign_performance"):
            dimensions = ["campaign_id", "adgroup_id", "ad_id", "stat_time_day"]
            metrics = [
                "impressions", "reach", "clicks",
                "ctr", "cpc", "cpi",
                "conversion", "conversion_rate", "spend",
                "ad_format"
            ]
            
            params = {
                "data_level": "AUCTION_AD",
                "start_date": date_start,
                "end_date": date_stop,
                "page_size": 1000
            }
            
            response = self.client.get_report(dimensions, metrics, params)
            data_list = response.get("data", {}).get("list", [])
            
            results = []
            for item in data_list:
                processed = self._process_report_item(item, date_start, date_stop)
                if processed:
                    results.append(processed)
            
            return results
    
    def _process_report_item(
        self,
        item: Dict[str, Any],
        date_start: str,
        date_stop: str
    ) -> Optional[Dict[str, Any]]:
        """Procesa un item del reporte de TikTok."""
        try:
            metrics_data = item.get("metrics", {})
            
            return {
                "date_start": date_start,
                "date_stop": date_stop,
                "campaign_id": str(item.get("campaign_id", "")),
                "campaign_name": item.get("campaign_name", ""),
                "ad_group_id": str(item.get("adgroup_id", "")),
                "ad_group_name": item.get("adgroup_name", ""),
                "ad_id": str(item.get("ad_id", "")),
                "ad_name": item.get("ad_name", ""),
                "ad_format": item.get("ad_format", "unknown"),
                "impressions": int(metrics_data.get("impressions", 0)),
                "reach": int(metrics_data.get("reach", 0)),
                "clicks": int(metrics_data.get("clicks", 0)),
                "ctr": float(metrics_data.get("ctr", 0)),
                "cpc": float(metrics_data.get("cpc", 0)),
                "cpi": float(metrics_data.get("cpi", 0)) if metrics_data.get("cpi") else None,
                "conversions": float(metrics_data.get("conversion", 0)),
                "conversion_rate": float(metrics_data.get("conversion_rate", 0)),
                "spend": float(metrics_data.get("spend", 0)),
                "platform": "tiktok"
            }
        except Exception as e:
            logger.warning(f"Error procesando item de TikTok: {str(e)}")
            return None
    
    def extract_audience_performance(
        self,
        date_start: str,
        date_stop: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Extrae datos de rendimiento por audiencia de TikTok."""
        # TikTok tiene estructura diferente, implementar según necesidades
        return {
            "date_start": date_start,
            "date_stop": date_stop,
            "audiences": [],
            "message": "Not implemented for TikTok"
        }

