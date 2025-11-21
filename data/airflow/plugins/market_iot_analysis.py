"""
Análisis de Mercado con IoT

Análisis de datos de dispositivos IoT para investigación de mercado:
- Análisis de datos de sensores
- Análisis de dispositivos conectados
- Análisis de patrones de uso
- Análisis de datos de movilidad
- Análisis de datos ambientales
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IoTDataPoint:
    """Punto de datos IoT."""
    device_id: str
    device_type: str  # 'sensor', 'wearable', 'smart_device'
    metric_name: str
    value: float
    timestamp: datetime
    location: Optional[str]


class IoTMarketAnalyzer:
    """Analizador de mercado con datos IoT."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_iot_data(
        self,
        industry: str,
        iot_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza datos IoT.
        
        Args:
            industry: Industria
            iot_data: Datos de dispositivos IoT
            
        Returns:
            Análisis de datos IoT
        """
        logger.info(f"Analyzing IoT data for {industry} - {len(iot_data)} data points")
        
        # Análisis de dispositivos
        device_analysis = self._analyze_devices(iot_data, industry)
        
        # Análisis de patrones de uso
        usage_patterns = self._analyze_usage_patterns(iot_data, industry)
        
        # Análisis de datos de sensores
        sensor_analysis = self._analyze_sensors(iot_data, industry)
        
        # Análisis de movilidad
        mobility_analysis = self._analyze_mobility(iot_data, industry)
        
        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "total_data_points": len(iot_data),
            "device_analysis": device_analysis,
            "usage_patterns": usage_patterns,
            "sensor_analysis": sensor_analysis,
            "mobility_analysis": mobility_analysis,
            "insights": self._generate_iot_insights(device_analysis, usage_patterns)
        }
    
    def _analyze_devices(
        self,
        iot_data: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """Analiza dispositivos IoT."""
        device_types = {}
        for data_point in iot_data:
            device_type = data_point.get("device_type", "unknown")
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        return {
            "total_devices": len(set(d.get("device_id") for d in iot_data)),
            "device_types": device_types,
            "active_devices": len(set(d.get("device_id") for d in iot_data if d.get("active", True)))
        }
    
    def _analyze_usage_patterns(
        self,
        iot_data: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """Analiza patrones de uso."""
        # Agrupar por hora del día
        hourly_usage = {}
        for data_point in iot_data:
            hour = datetime.fromisoformat(data_point.get("timestamp", datetime.utcnow().isoformat())).hour
            hourly_usage[hour] = hourly_usage.get(hour, 0) + 1
        
        peak_hour = max(hourly_usage.items(), key=lambda x: x[1])[0] if hourly_usage else 0
        
        return {
            "hourly_usage": hourly_usage,
            "peak_usage_hour": peak_hour,
            "usage_trend": "increasing" if len(iot_data) > 1000 else "stable"
        }
    
    def _analyze_sensors(
        self,
        iot_data: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """Analiza datos de sensores."""
        sensor_data = [d for d in iot_data if d.get("device_type") == "sensor"]
        
        if sensor_data:
            values = [d.get("value", 0) for d in sensor_data]
            avg_value = sum(values) / len(values) if values else 0
            
            return {
                "total_sensors": len(set(d.get("device_id") for d in sensor_data)),
                "average_value": avg_value,
                "data_quality": "high" if len(sensor_data) > 100 else "medium"
            }
        
        return {"total_sensors": 0, "average_value": 0, "data_quality": "unknown"}
    
    def _analyze_mobility(
        self,
        iot_data: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """Analiza datos de movilidad."""
        locations = [d.get("location") for d in iot_data if d.get("location")]
        unique_locations = len(set(locations))
        
        return {
            "unique_locations": unique_locations,
            "mobility_pattern": "high" if unique_locations > 10 else "medium" if unique_locations > 5 else "low",
            "geographic_coverage": "wide" if unique_locations > 20 else "limited"
        }
    
    def _generate_iot_insights(
        self,
        device_analysis: Dict[str, Any],
        usage_patterns: Dict[str, Any]
    ) -> List[str]:
        """Genera insights de IoT."""
        insights = [
            f"Total devices analyzed: {device_analysis.get('total_devices', 0)}",
            f"Peak usage hour: {usage_patterns.get('peak_usage_hour', 0)}:00",
            f"Usage trend: {usage_patterns.get('usage_trend', 'unknown')}"
        ]
        
        return insights






