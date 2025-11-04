"""
Procesadores modulares de datos para transformaciones avanzadas.

Incluye:
- Normalización de datos entre plataformas
- Cálculo de métricas derivadas
- Agregaciones y agrupaciones
- Análisis de rendimiento
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento calculadas."""
    date_start: str
    date_stop: str
    total_impressions: int
    total_clicks: int
    total_spend: float
    total_conversions: float
    total_revenue: float
    avg_ctr: float
    avg_cpc: float
    avg_cpa: float
    roas: float
    conversion_rate: float


class BaseProcessor(ABC):
    """Procesador base para transformaciones de datos."""
    
    @abstractmethod
    def normalize(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normaliza datos a formato estándar."""
        pass
    
    @abstractmethod
    def calculate_metrics(self, data: List[Dict[str, Any]]) -> PerformanceMetrics:
        """Calcula métricas agregadas."""
        pass


class CampaignProcessor(BaseProcessor):
    """Procesador para datos de campañas."""
    
    def normalize(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza datos de campañas a formato estándar.
        
        Args:
            data: Lista de datos de campañas (pueden ser de diferentes plataformas)
            
        Returns:
            Lista de datos normalizados
        """
        normalized = []
        
        for record in data:
            try:
                normalized_record = {
                    "date_start": record.get("date_start", ""),
                    "date_stop": record.get("date_stop", ""),
                    "platform": record.get("platform", "unknown"),
                    "campaign_id": str(record.get("campaign_id", "")),
                    "campaign_name": str(record.get("campaign_name", "") or ""),
                    "ad_group_id": str(record.get("ad_group_id") or record.get("adset_id", "")),
                    "ad_group_name": str(record.get("ad_group_name") or record.get("adset_name", "") or ""),
                    "ad_id": str(record.get("ad_id", "")),
                    "ad_name": str(record.get("ad_name", "") or ""),
                    "impressions": int(record.get("impressions", 0) or 0),
                    "clicks": int(record.get("clicks", 0) or 0),
                    "spend": float(record.get("spend", 0) or 0),
                    "conversions": float(record.get("conversions", 0) or 0),
                    "revenue": float(record.get("revenue") or (record.get("spend", 0) * record.get("roas", 0)) or 0),
                }
                
                # Calcular métricas derivadas si no existen
                impressions = normalized_record["impressions"]
                clicks = normalized_record["clicks"]
                spend = normalized_record["spend"]
                conversions = normalized_record["conversions"]
                revenue = normalized_record["revenue"]
                
                normalized_record["ctr"] = (
                    float(record.get("ctr", 0)) or
                    (clicks / impressions * 100 if impressions > 0 else 0.0)
                )
                normalized_record["cpc"] = (
                    float(record.get("cpc") or record.get("avg_cpc", 0)) or
                    (spend / clicks if clicks > 0 else 0.0)
                )
                normalized_record["cpa"] = (
                    float(record.get("cpa") or record.get("cost_per_conversion", 0)) or
                    (spend / conversions if conversions > 0 else 0.0)
                )
                normalized_record["roas"] = (
                    float(record.get("roas", 0)) or
                    (revenue / spend if spend > 0 else 0.0)
                )
                normalized_record["conversion_rate"] = (
                    float(record.get("conversion_rate", 0)) or
                    (conversions / clicks * 100 if clicks > 0 else 0.0)
                )
                
                normalized.append(normalized_record)
                
            except Exception as e:
                logger.warning(f"Error normalizando registro: {str(e)}")
                continue
        
        return normalized
    
    def calculate_metrics(self, data: List[Dict[str, Any]]) -> PerformanceMetrics:
        """
        Calcula métricas agregadas de rendimiento.
        
        Args:
            data: Lista de datos de campañas (normalizados)
            
        Returns:
            PerformanceMetrics con métricas agregadas
        """
        if not data:
            return PerformanceMetrics(
                date_start="",
                date_stop="",
                total_impressions=0,
                total_clicks=0,
                total_spend=0.0,
                total_conversions=0.0,
                total_revenue=0.0,
                avg_ctr=0.0,
                avg_cpc=0.0,
                avg_cpa=0.0,
                roas=0.0,
                conversion_rate=0.0
            )
        
        # Obtener fechas del primer registro
        date_start = data[0].get("date_start", "")
        date_stop = data[0].get("date_stop", "")
        
        # Agregar métricas
        total_impressions = sum(r.get("impressions", 0) for r in data)
        total_clicks = sum(r.get("clicks", 0) for r in data)
        total_spend = sum(r.get("spend", 0) for r in data)
        total_conversions = sum(r.get("conversions", 0) for r in data)
        total_revenue = sum(r.get("revenue", 0) for r in data)
        
        # Calcular promedios
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0.0
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0.0
        roas = (total_revenue / total_spend) if total_spend > 0 else 0.0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0
        
        return PerformanceMetrics(
            date_start=date_start,
            date_stop=date_stop,
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            total_spend=total_spend,
            total_conversions=total_conversions,
            total_revenue=total_revenue,
            avg_ctr=avg_ctr,
            avg_cpc=avg_cpc,
            avg_cpa=avg_cpa,
            roas=roas,
            conversion_rate=conversion_rate
        )
    
    def group_by_campaign(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa datos por campaña.
        
        Args:
            data: Lista de datos de campañas
            
        Returns:
            Diccionario agrupado por campaign_id
        """
        grouped = {}
        for record in data:
            campaign_id = record.get("campaign_id", "unknown")
            if campaign_id not in grouped:
                grouped[campaign_id] = []
            grouped[campaign_id].append(record)
        return grouped
    
    def group_by_date(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa datos por fecha.
        
        Args:
            data: Lista de datos de campañas
            
        Returns:
            Diccionario agrupado por date_start
        """
        grouped = {}
        for record in data:
            date = record.get("date_start", "unknown")
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(record)
        return grouped
    
    def filter_by_performance(
        self,
        data: List[Dict[str, Any]],
        min_ctr: Optional[float] = None,
        max_cpc: Optional[float] = None,
        min_conversions: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Filtra datos por criterios de rendimiento.
        
        Args:
            data: Lista de datos
            min_ctr: CTR mínimo (opcional)
            max_cpc: CPC máximo (opcional)
            min_conversions: Conversiones mínimas (opcional)
            
        Returns:
            Lista filtrada
        """
        filtered = []
        
        for record in data:
            if min_ctr is not None and record.get("ctr", 0) < min_ctr:
                continue
            if max_cpc is not None and record.get("cpc", 0) > max_cpc:
                continue
            if min_conversions is not None and record.get("conversions", 0) < min_conversions:
                continue
            
            filtered.append(record)
        
        return filtered


class AudienceProcessor(BaseProcessor):
    """Procesador para datos de audiencias."""
    
    def normalize(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normaliza datos de audiencias."""
        normalized = []
        for record in data:
            try:
                normalized.append({
                    "audience_type": str(record.get("audience_type", "unknown")),
                    "spend": float(record.get("spend", 0) or 0),
                    "conversions": float(record.get("conversions", 0) or 0),
                    "revenue": float(record.get("revenue", 0) or 0),
                    "cpa": float(record.get("cpa", 0) or 0),
                    "conversion_value": float(record.get("conversion_value") or record.get("revenue", 0) / max(record.get("conversions", 1), 1) or 0),
                })
            except Exception as e:
                logger.warning(f"Error normalizando audiencia: {str(e)}")
                continue
        return normalized
    
    def calculate_metrics(self, data: List[Dict[str, Any]]) -> PerformanceMetrics:
        """Calcula métricas agregadas de audiencias."""
        if not data:
            return PerformanceMetrics(
                date_start="", date_stop="",
                total_impressions=0, total_clicks=0,
                total_spend=0.0, total_conversions=0.0, total_revenue=0.0,
                avg_ctr=0.0, avg_cpc=0.0, avg_cpa=0.0, roas=0.0, conversion_rate=0.0
            )
        
        total_spend = sum(r.get("spend", 0) for r in data)
        total_conversions = sum(r.get("conversions", 0) for r in data)
        total_revenue = sum(r.get("revenue", 0) for r in data)
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0.0
        roas = (total_revenue / total_spend) if total_spend > 0 else 0.0
        
        return PerformanceMetrics(
            date_start="", date_stop="",
            total_impressions=0, total_clicks=0,
            total_spend=total_spend,
            total_conversions=total_conversions,
            total_revenue=total_revenue,
            avg_ctr=0.0, avg_cpc=0.0,
            avg_cpa=avg_cpa,
            roas=roas,
            conversion_rate=0.0
        )
    
    def identify_underperformers(
        self,
        data: List[Dict[str, Any]],
        threshold_percent: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        Identifica audiencias con rendimiento inferior.
        
        Args:
            data: Lista de datos de audiencias
            threshold_percent: Porcentaje sobre el promedio para considerar inferior
            
        Returns:
            Lista de audiencias bajo rendimiento
        """
        if not data:
            return []
        
        # Calcular promedio de CPA
        total_spend = sum(r.get("spend", 0) for r in data)
        total_conversions = sum(r.get("conversions", 0) for r in data)
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0.0
        
        threshold_cpa = avg_cpa * (1 + threshold_percent / 100)
        
        underperformers = [
            r for r in data
            if r.get("cpa", 0) > threshold_cpa or r.get("conversions", 0) == 0
        ]
        
        return underperformers


class GeographicProcessor(BaseProcessor):
    """Procesador para datos geográficos."""
    
    def normalize(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normaliza datos geográficos."""
        normalized = []
        for record in data:
            try:
                normalized.append({
                    "country": str(record.get("country") or record.get("geographic_location", "unknown")),
                    "region": str(record.get("region", "")),
                    "impressions": int(record.get("impressions", 0) or 0),
                    "clicks": int(record.get("clicks", 0) or 0),
                    "conversions": float(record.get("conversions", 0) or 0),
                    "spend": float(record.get("spend", 0) or 0),
                    "cpa": float(record.get("cpa", 0) or 0),
                })
            except Exception as e:
                logger.warning(f"Error normalizando geografía: {str(e)}")
                continue
        return normalized
    
    def calculate_metrics(self, data: List[Dict[str, Any]]) -> PerformanceMetrics:
        """Calcula métricas agregadas geográficas."""
        # Similar a CampaignProcessor pero enfocado en geografía
        processor = CampaignProcessor()
        return processor.calculate_metrics(data)
    
    def get_top_locations(
        self,
        data: List[Dict[str, Any]],
        top_n: int = 10,
        sort_by: str = "conversions"
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las mejores ubicaciones.
        
        Args:
            data: Lista de datos geográficos
            top_n: Número de ubicaciones a retornar
            sort_by: Campo para ordenar (conversions, cpa, spend)
            
        Returns:
            Lista de top ubicaciones
        """
        sorted_data = sorted(
            data,
            key=lambda x: x.get(sort_by, 0),
            reverse=(sort_by != "cpa")
        )
        return sorted_data[:top_n]


def get_processor(processor_type: str) -> BaseProcessor:
    """
    Factory function para obtener procesadores.
    
    Args:
        processor_type: Tipo de procesador ("campaign", "audience", "geographic")
        
    Returns:
        Instancia del procesador
    """
    if processor_type == "campaign":
        return CampaignProcessor()
    elif processor_type == "audience":
        return AudienceProcessor()
    elif processor_type == "geographic":
        return GeographicProcessor()
    else:
        raise ValueError(f"Tipo de procesador no soportado: {processor_type}")

