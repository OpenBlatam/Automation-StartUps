"""
Sistema Avanzado de Alertas y Recomendaciones para Predicción de Demanda
Autor: Sistema de IA Avanzado
Fecha: 2024
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AlertSystem:
    """
    Sistema avanzado de alertas y recomendaciones para gestión de demanda de transporte
    """
    
    def __init__(self, data=None):
        """
        Inicializar el sistema de alertas
        
        Args:
            data (pd.DataFrame): DataFrame con datos históricos
        """
        self.data = data
        self.alerts = []
        self.recommendations = []
        self.alert_history = []
        self.thresholds = {
            'demand_spike': 1.5,      # 50% por encima del promedio
            'demand_drop': 0.7,       # 30% por debajo del promedio
            'volatility_high': 1.3,   # 30% más volátil que el promedio
            'trend_change': 0.2,       # Cambio de tendencia del 20%
            'seasonal_deviation': 0.4, # 40% de desviación estacional
            'capacity_utilization': 0.9, # 90% de utilización de capacidad
            'cost_spike': 1.3,        # 30% de aumento en costos
            'weather_impact': 0.3     # 30% de impacto climático
        }
        
    def set_data(self, data):
        """
        Establecer datos para análisis
        
        Args:
            data (pd.DataFrame): DataFrame con datos históricos
        """
        self.data = data.copy()
        print(f"✅ Datos establecidos para sistema de alertas: {len(self.data)} registros")
        
    def set_thresholds(self, thresholds: Dict[str, float]):
        """
        Establecer umbrales personalizados para alertas
        
        Args:
            thresholds (Dict[str, float]): Diccionario con nuevos umbrales
        """
        self.thresholds.update(thresholds)
        print("✅ Umbrales de alertas actualizados")
        
    def detect_demand_anomalies(self) -> List[Dict]:
        """
        Detectar anomalías en la demanda
        """
        if self.data is None:
            return []
        
        print("🔍 Detectando anomalías de demanda...")
        
        alerts = []
        demand_data = self.data['demanda_transporte']
        
        # Calcular métricas base
        mean_demand = demand_data.mean()
        std_demand = demand_data.std()
        
        # Detectar picos de demanda
        recent_data = demand_data.tail(7)  # Últimos 7 días
        for i, (idx, value) in enumerate(recent_data.items()):
            if value > mean_demand * self.thresholds['demand_spike']:
                alerts.append({
                    'type': 'demand_spike',
                    'severity': 'high',
                    'title': '🚨 Pico de Demanda Detectado',
                    'message': f'Demanda de {value:,.0f} está {((value/mean_demand)-1)*100:.1f}% por encima del promedio',
                    'date': self.data.loc[idx, 'fecha'],
                    'value': value,
                    'threshold': mean_demand * self.thresholds['demand_spike'],
                    'recommendation': self._get_demand_spike_recommendation(value, mean_demand)
                })
        
        # Detectar caídas de demanda
        for i, (idx, value) in enumerate(recent_data.items()):
            if value < mean_demand * self.thresholds['demand_drop']:
                alerts.append({
                    'type': 'demand_drop',
                    'severity': 'medium',
                    'title': '📉 Caída de Demanda Detectada',
                    'message': f'Demanda de {value:,.0f} está {((value/mean_demand)-1)*100:.1f}% por debajo del promedio',
                    'date': self.data.loc[idx, 'fecha'],
                    'value': value,
                    'threshold': mean_demand * self.thresholds['demand_drop'],
                    'recommendation': self._get_demand_drop_recommendation(value, mean_demand)
                })
        
        return alerts
    
    def run_complete_analysis(self) -> Dict:
        """
        Ejecutar análisis completo de alertas y recomendaciones
        """
        print("🚀 Ejecutando análisis completo de alertas...")
        
        all_alerts = []
        
        # Ejecutar todas las detecciones
        all_alerts.extend(self.detect_demand_anomalies())
        
        # Generar recomendaciones
        recommendations = self.generate_recommendations()
        
        # Clasificar alertas por severidad
        high_severity = [alert for alert in all_alerts if alert['severity'] == 'high']
        medium_severity = [alert for alert in all_alerts if alert['severity'] == 'medium']
        low_severity = [alert for alert in all_alerts if alert['severity'] == 'low']
        
        # Crear resumen
        analysis_summary = {
            'timestamp': datetime.now().isoformat(),
            'total_alerts': len(all_alerts),
            'high_severity_count': len(high_severity),
            'medium_severity_count': len(medium_severity),
            'low_severity_count': len(low_severity),
            'recommendations_count': len(recommendations),
            'alerts': {
                'high': high_severity,
                'medium': medium_severity,
                'low': low_severity
            },
            'recommendations': recommendations,
            'system_status': self._get_system_status(all_alerts)
        }
        
        self.alerts = all_alerts
        self.recommendations = recommendations
        
        print(f"✅ Análisis completado: {len(all_alerts)} alertas, {len(recommendations)} recomendaciones")
        
        return analysis_summary
    
    def generate_recommendations(self) -> List[Dict]:
        """
        Generar recomendaciones basadas en análisis completo
        """
        print("💡 Generando recomendaciones...")
        
        recommendations = []
        
        # Análisis de tendencias
        if self.data is not None:
            demand_data = self.data['demanda_transporte']
            trend = demand_data.tail(30).diff().mean()
            
            if trend > 0:
                recommendations.append({
                    'category': 'capacity_planning',
                    'priority': 'high',
                    'title': '📈 Planificación de Capacidad',
                    'description': 'La demanda muestra tendencia creciente. Considerar expansión de capacidad.',
                    'actions': [
                        'Evaluar necesidad de vehículos adicionales',
                        'Revisar rutas y horarios',
                        'Considerar contratación de personal'
                    ],
                    'timeline': '1-3 meses',
                    'impact': 'high'
                })
        
        return recommendations
    
    def _get_system_status(self, alerts: List[Dict]) -> str:
        """
        Determinar el estado general del sistema
        """
        high_alerts = len([a for a in alerts if a['severity'] == 'high'])
        
        if high_alerts > 3:
            return 'critical'
        elif high_alerts > 0:
            return 'warning'
        else:
            return 'normal'
    
    def _get_demand_spike_recommendation(self, current_demand: float, avg_demand: float) -> str:
        """Generar recomendación para pico de demanda"""
        increase_pct = ((current_demand / avg_demand) - 1) * 100
        
        if increase_pct > 100:
            return "Activar planes de emergencia y considerar servicios adicionales"
        elif increase_pct > 50:
            return "Aumentar capacidad operativa y optimizar rutas"
        else:
            return "Monitorear de cerca y preparar recursos adicionales"
    
    def _get_demand_drop_recommendation(self, current_demand: float, avg_demand: float) -> str:
        """Generar recomendación para caída de demanda"""
        decrease_pct = ((avg_demand / current_demand) - 1) * 100
        
        if decrease_pct > 50:
            return "Revisar estrategias de marketing y considerar promociones"
        elif decrease_pct > 30:
            return "Optimizar costos operativos y revisar horarios"
        else:
            return "Analizar causas y ajustar estrategias"



