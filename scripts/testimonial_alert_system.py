#!/usr/bin/env python3
"""
Sistema de Alertas para Testimonios
Detecta problemas, oportunidades y genera alertas proactivas
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"


@dataclass
class Alert:
    """Alerta generada"""
    level: AlertLevel
    title: str
    message: str
    action_required: bool
    recommendation: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AlertSystem:
    """Sistema de alertas y notificaciones"""
    
    def __init__(self):
        """Inicializa el sistema de alertas"""
        self.alerts: List[Alert] = []
    
    def analyze_and_alert(
        self,
        post_data: Dict[str, Any],
        platform: str,
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[Alert]:
        """
        Analiza los datos y genera alertas
        
        Args:
            post_data: Datos de la publicación
            platform: Plataforma objetivo
            historical_data: Datos históricos para comparación
        
        Returns:
            Lista de alertas generadas
        """
        alerts = []
        
        # Alerta: Score bajo
        if "engagement_prediction" in post_data:
            pred = post_data["engagement_prediction"]
            score = pred.get("predicted_score", 0)
            
            if score < 40:
                alerts.append(Alert(
                    level=AlertLevel.CRITICAL,
                    title="Score de Engagement Bajo",
                    message=f"El score predicho es {score}/100, lo cual es muy bajo.",
                    action_required=True,
                    recommendation="Revisa el contenido y considera usar optimizaciones sugeridas."
                ))
            elif score < 60:
                alerts.append(Alert(
                    level=AlertLevel.WARNING,
                    title="Score de Engagement Mejorable",
                    message=f"El score predicho es {score}/100. Hay margen de mejora.",
                    action_required=False,
                    recommendation="Considera aplicar las optimizaciones sugeridas."
                ))
            elif score >= 80:
                alerts.append(Alert(
                    level=AlertLevel.SUCCESS,
                    title="Excelente Score de Engagement",
                    message=f"El score predicho es {score}/100. ¡Excelente trabajo!",
                    action_required=False
                ))
        
        # Alerta: Comparación con benchmarks
        if "analytics_report" in post_data and "benchmark_comparison" in post_data["analytics_report"]:
            bench = post_data["analytics_report"]["benchmark_comparison"]
            percentile = bench.get("percentile", 50)
            
            if percentile < 25:
                alerts.append(Alert(
                    level=AlertLevel.CRITICAL,
                    title="Rendimiento por Debajo del Promedio",
                    message=f"Estás en el percentil {percentile}% de la industria.",
                    action_required=True,
                    recommendation=f"Potencial de mejora: +{bench.get('improvement_potential', 0)}%"
                ))
            elif percentile >= 90:
                alerts.append(Alert(
                    level=AlertLevel.SUCCESS,
                    title="Rendimiento Excepcional",
                    message=f"Estás en el percentil {percentile}% - Top 10% de la industria!",
                    action_required=False
                ))
        
        # Alerta: Longitud no óptima
        length = post_data.get("length", 0)
        optimal_lengths = {
            'instagram': 200, 'linkedin': 300, 'facebook': 250,
            'twitter': 200, 'tiktok': 150
        }
        optimal = optimal_lengths.get(platform, 200)
        
        if length < optimal * 0.7:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="Contenido Muy Corto",
                message=f"Longitud actual: {length} caracteres. Óptimo: ~{optimal} caracteres.",
                action_required=False,
                recommendation="Considera expandir el contenido para mejor engagement."
            ))
        elif length > optimal * 1.5:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="Contenido Muy Largo",
                message=f"Longitud actual: {length} caracteres. Óptimo: ~{optimal} caracteres.",
                action_required=False,
                recommendation="Considera acortar el contenido para mantener atención."
            ))
        
        # Alerta: Hashtags insuficientes
        hashtags_count = len(post_data.get("hashtags", []))
        optimal_counts = {
            'instagram': 10, 'linkedin': 5, 'facebook': 5,
            'twitter': 3, 'tiktok': 5
        }
        optimal_count = optimal_counts.get(platform, 5)
        
        if hashtags_count < optimal_count * 0.5:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="Hashtags Insuficientes",
                message=f"Tienes {hashtags_count} hashtags. Óptimo: {optimal_count}.",
                action_required=False,
                recommendation="Agrega más hashtags relevantes para aumentar alcance."
            ))
        
        # Alerta: Sin CTA
        if not post_data.get("call_to_action"):
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="Falta Llamada a la Acción",
                message="No se detectó una llamada a la acción en el contenido.",
                action_required=False,
                recommendation="Agrega un CTA para guiar a la audiencia hacia una acción."
            ))
        
        # Alerta: Sin números/métricas
        import re
        content = post_data.get("post_content", "")
        if not re.search(r'\d+', content):
            alerts.append(Alert(
                level=AlertLevel.INFO,
                title="Sin Números o Métricas",
                message="El contenido no incluye números o porcentajes específicos.",
                action_required=False,
                recommendation="Agrega números concretos para mayor credibilidad."
            ))
        
        # Alerta: Comparación con histórico
        if historical_data and len(historical_data) >= 5:
            recent_avg = sum(
                p.get('engagement_rate', 0) for p in historical_data[-5:]
            ) / 5
            
            if "engagement_prediction" in post_data:
                current_pred = post_data["engagement_prediction"].get("predicted_engagement_rate", 0)
                
                if current_pred < recent_avg * 0.8:
                    alerts.append(Alert(
                        level=AlertLevel.WARNING,
                        title="Predicción por Debajo del Promedio Histórico",
                        message=f"Predicción: {current_pred:.2f}% vs Promedio reciente: {recent_avg:.2f}%",
                        action_required=False,
                        recommendation="Revisa qué factores están afectando negativamente."
                    ))
        
        self.alerts = alerts
        return alerts
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de las alertas"""
        if not self.alerts:
            return {"total": 0, "by_level": {}}
        
        by_level = {}
        for level in AlertLevel:
            by_level[level.value] = len([a for a in self.alerts if a.level == level])
        
        critical_count = by_level.get("critical", 0)
        warning_count = by_level.get("warning", 0)
        
        return {
            "total": len(self.alerts),
            "by_level": by_level,
            "requires_attention": critical_count > 0 or warning_count > 0,
            "critical_count": critical_count,
            "warning_count": warning_count
        }
    
    def format_alerts_for_display(self) -> str:
        """Formatea las alertas para mostrar en consola"""
        if not self.alerts:
            return "✅ No hay alertas. Todo se ve bien!"
        
        lines = []
        lines.append("\n" + "="*60)
        lines.append("🚨 ALERTAS Y RECOMENDACIONES")
        lines.append("="*60)
        
        # Agrupar por nivel
        for level in [AlertLevel.CRITICAL, AlertLevel.WARNING, AlertLevel.INFO, AlertLevel.SUCCESS]:
            level_alerts = [a for a in self.alerts if a.level == level]
            if not level_alerts:
                continue
            
            icon = {
                AlertLevel.CRITICAL: "🔴",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.INFO: "ℹ️",
                AlertLevel.SUCCESS: "✅"
            }.get(level, "•")
            
            lines.append(f"\n{icon} {level.value.upper()} ({len(level_alerts)}):")
            
            for alert in level_alerts:
                lines.append(f"  • {alert.title}")
                lines.append(f"    {alert.message}")
                if alert.recommendation:
                    lines.append(f"    💡 {alert.recommendation}")
                lines.append("")
        
        lines.append("="*60)
        
        return "\n".join(lines)


