#!/usr/bin/env python3
"""
Analizador de Tendencias Temporales para Testimonios
Analiza patrones temporales, detecta tendencias y genera predicciones mejoradas
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class TemporalTrend:
    """Tendencia temporal detectada"""
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    growth_rate: float  # Porcentaje de crecimiento
    confidence: str  # "high", "medium", "low"
    period: str  # "daily", "weekly", "monthly"
    forecast_value: float
    seasonality_detected: bool
    anomaly_detected: bool


@dataclass
class SuccessPattern:
    """Patrón de éxito detectado"""
    pattern_type: str  # "time", "content", "hashtag", "platform"
    pattern_description: str
    success_rate: float
    frequency: int
    recommendation: str


class TrendAnalyzer:
    """Analizador de tendencias temporales para testimonios"""
    
    def __init__(self, historical_posts: Optional[List[Dict[str, Any]]] = None):
        """
        Inicializa el analizador de tendencias
        
        Args:
            historical_posts: Lista de publicaciones históricas con métricas
        """
        self.historical_posts = historical_posts or []
        self._analyze_patterns()
    
    def _analyze_patterns(self):
        """Analiza patrones en los datos históricos"""
        if not self.historical_posts:
            return
        
        # Patrones por día de la semana
        self.weekly_patterns = defaultdict(list)
        # Patrones por hora
        self.hourly_patterns = defaultdict(list)
        # Patrones por tipo de contenido
        self.content_patterns = defaultdict(list)
        
        for post in self.historical_posts:
            fecha = post.get('fecha_publicacion') or post.get('timestamp')
            if fecha:
                try:
                    if isinstance(fecha, str):
                        fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                    else:
                        fecha_dt = fecha
                    
                    day_of_week = fecha_dt.strftime('%A')
                    hour = fecha_dt.hour
                    
                    engagement_rate = post.get('engagement_rate', 0)
                    engagement_score = post.get('engagement_score', 0)
                    
                    self.weekly_patterns[day_of_week].append({
                        'engagement_rate': engagement_rate,
                        'engagement_score': engagement_score
                    })
                    
                    self.hourly_patterns[hour].append({
                        'engagement_rate': engagement_rate,
                        'engagement_score': engagement_score
                    })
                except:
                    pass
            
            # Patrones por tipo de contenido
            content_type = post.get('tipo_contenido', 'testimonial')
            self.content_patterns[content_type].append({
                'engagement_rate': post.get('engagement_rate', 0),
                'engagement_score': post.get('engagement_score', 0)
            })
    
    def analyze_temporal_trends(
        self,
        metric: str = 'engagement_rate',
        period: str = 'daily'
    ) -> TemporalTrend:
        """
        Analiza tendencias temporales en el engagement
        
        Args:
            metric: Métrica a analizar ('engagement_rate', 'engagement_score')
            period: Período de análisis ('daily', 'weekly', 'monthly')
        
        Returns:
            TemporalTrend con análisis de tendencias
        """
        if not self.historical_posts or len(self.historical_posts) < 3:
            return TemporalTrend(
                trend_direction="stable",
                growth_rate=0.0,
                confidence="low",
                period=period,
                forecast_value=0.0,
                seasonality_detected=False,
                anomaly_detected=False
            )
        
        # Agrupar por período
        grouped_data = defaultdict(list)
        
        for post in self.historical_posts:
            fecha = post.get('fecha_publicacion') or post.get('timestamp')
            if not fecha:
                continue
            
            try:
                if isinstance(fecha, str):
                    fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                else:
                    fecha_dt = fecha
                
                if period == 'daily':
                    key = fecha_dt.date().isoformat()
                elif period == 'weekly':
                    # Semana del año
                    week = fecha_dt.isocalendar()[1]
                    key = f"{fecha_dt.year}-W{week}"
                elif period == 'monthly':
                    key = f"{fecha_dt.year}-{fecha_dt.month:02d}"
                else:
                    key = fecha_dt.date().isoformat()
                
                value = post.get(metric, 0)
                grouped_data[key].append(value)
            except:
                continue
        
        if not grouped_data:
            return TemporalTrend(
                trend_direction="stable",
                growth_rate=0.0,
                confidence="low",
                period=period,
                forecast_value=0.0,
                seasonality_detected=False,
                anomaly_detected=False
            )
        
        # Calcular promedios por período
        period_averages = {
            period_key: statistics.mean(values)
            for period_key, values in grouped_data.items()
        }
        
        # Ordenar por fecha
        sorted_periods = sorted(period_averages.keys())
        values = [period_averages[p] for p in sorted_periods]
        
        if len(values) < 2:
            return TemporalTrend(
                trend_direction="stable",
                growth_rate=0.0,
                confidence="low",
                period=period,
                forecast_value=values[0] if values else 0.0,
                seasonality_detected=False,
                anomaly_detected=False
            )
        
        # Calcular tasa de crecimiento
        first_value = values[0]
        last_value = values[-1]
        
        if first_value > 0:
            growth_rate = ((last_value - first_value) / first_value) * 100
        else:
            growth_rate = 0.0
        
        # Determinar dirección de tendencia
        if abs(growth_rate) < 5:
            trend_direction = "stable"
        elif growth_rate > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"
        
        # Detectar volatilidad
        if len(values) >= 3:
            std_dev = statistics.stdev(values)
            mean_val = statistics.mean(values)
            coefficient_of_variation = (std_dev / mean_val * 100) if mean_val > 0 else 0
            
            if coefficient_of_variation > 30:
                trend_direction = "volatile"
        else:
            coefficient_of_variation = 0
        
        # Detectar anomalías
        anomaly_detected = False
        if len(values) >= 3:
            mean_val = statistics.mean(values)
            std_dev = statistics.stdev(values)
            if std_dev > 0:
                z_score_last = abs((last_value - mean_val) / std_dev)
                if z_score_last > 2.5:
                    anomaly_detected = True
        
        # Detectar estacionalidad (simplificado)
        seasonality_detected = False
        if len(values) >= 7 and period == 'weekly':
            # Buscar patrones repetitivos
            if len(set(values[-7:])) < 4:  # Menos de 4 valores únicos en última semana
                seasonality_detected = True
        
        # Calcular confianza
        if len(values) >= 7:
            confidence = "high"
        elif len(values) >= 3:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Forecast simple (promedio móvil)
        if len(values) >= 3:
            recent_avg = statistics.mean(values[-3:])
            forecast_value = recent_avg * (1 + growth_rate / 100) if growth_rate != 0 else recent_avg
        else:
            forecast_value = last_value
        
        return TemporalTrend(
            trend_direction=trend_direction,
            growth_rate=round(growth_rate, 2),
            confidence=confidence,
            period=period,
            forecast_value=round(forecast_value, 2),
            seasonality_detected=seasonality_detected,
            anomaly_detected=anomaly_detected
        )
    
    def detect_success_patterns(self) -> List[SuccessPattern]:
        """
        Detecta patrones de éxito en las publicaciones históricas
        
        Returns:
            Lista de SuccessPattern detectados
        """
        patterns = []
        
        if not self.historical_posts:
            return patterns
        
        # Filtrar publicaciones exitosas (top 25%)
        engagement_rates = [p.get('engagement_rate', 0) for p in self.historical_posts]
        if not engagement_rates:
            return patterns
        
        threshold = sorted(engagement_rates, reverse=True)[max(0, len(engagement_rates) // 4)]
        successful_posts = [
            p for p in self.historical_posts
            if p.get('engagement_rate', 0) >= threshold
        ]
        
        if not successful_posts:
            return patterns
        
        # Patrón: Día de la semana
        if self.weekly_patterns:
            day_success_rates = {}
            for day, posts in self.weekly_patterns.items():
                if posts:
                    avg_rate = statistics.mean([p['engagement_rate'] for p in posts])
                    day_success_rates[day] = avg_rate
            
            if day_success_rates:
                best_day = max(day_success_rates.items(), key=lambda x: x[1])
                patterns.append(SuccessPattern(
                    pattern_type="time",
                    pattern_description=f"Mejor día: {best_day[0]}",
                    success_rate=best_day[1],
                    frequency=len(self.weekly_patterns[best_day[0]]),
                    recommendation=f"Publicar los {best_day[0]} para máximo engagement"
                ))
        
        # Patrón: Hora del día
        if self.hourly_patterns:
            hour_success_rates = {}
            for hour, posts in self.hourly_patterns.items():
                if posts:
                    avg_rate = statistics.mean([p['engagement_rate'] for p in posts])
                    hour_success_rates[hour] = avg_rate
            
            if hour_success_rates:
                best_hour = max(hour_success_rates.items(), key=lambda x: x[1])
                patterns.append(SuccessPattern(
                    pattern_type="time",
                    pattern_description=f"Mejor hora: {best_hour[0]}:00",
                    success_rate=best_hour[1],
                    frequency=len(self.hourly_patterns[best_hour[0]]),
                    recommendation=f"Publicar a las {best_hour[0]}:00 para mejor rendimiento"
                ))
        
        # Patrón: Tipo de contenido
        if self.content_patterns:
            content_success_rates = {}
            for content_type, posts in self.content_patterns.items():
                if posts:
                    avg_rate = statistics.mean([p['engagement_rate'] for p in posts])
                    content_success_rates[content_type] = avg_rate
            
            if content_success_rates:
                best_type = max(content_success_rates.items(), key=lambda x: x[1])
                patterns.append(SuccessPattern(
                    pattern_type="content",
                    pattern_description=f"Mejor tipo: {best_type[0]}",
                    success_rate=best_type[1],
                    frequency=len(self.content_patterns[best_type[0]]),
                    recommendation=f"Usar tipo de contenido '{best_type[0]}' más frecuentemente"
                ))
        
        # Patrón: Longitud de contenido
        length_groups = defaultdict(list)
        for post in successful_posts:
            length = len(post.get('content', ''))
            if length < 100:
                group = "corto"
            elif length < 300:
                group = "medio"
            else:
                group = "largo"
            
            length_groups[group].append(post.get('engagement_rate', 0))
        
        if length_groups:
            length_success_rates = {
                group: statistics.mean(rates)
                for group, rates in length_groups.items()
                if rates
            }
            if length_success_rates:
                best_length = max(length_success_rates.items(), key=lambda x: x[1])
                patterns.append(SuccessPattern(
                    pattern_type="content",
                    pattern_description=f"Mejor longitud: {best_length[0]}",
                    success_rate=best_length[1],
                    frequency=len(length_groups[best_length[0]]),
                    recommendation=f"Usar contenido de longitud {best_length[0]} para mejor engagement"
                ))
        
        return patterns
    
    def predict_optimal_posting_time(
        self,
        platform: str
    ) -> Dict[str, Any]:
        """
        Predice el mejor momento para publicar basado en patrones históricos
        
        Args:
            platform: Plataforma objetivo
        
        Returns:
            Dict con recomendaciones de timing
        """
        if not self.historical_posts:
            return {
                "recommendation": "No hay datos históricos suficientes",
                "confidence": "low"
            }
        
        # Filtrar por plataforma si es posible
        platform_posts = [
            p for p in self.historical_posts
            if p.get('platform', '').lower() == platform.lower()
        ] or self.historical_posts
        
        # Analizar días de la semana
        day_engagement = defaultdict(list)
        hour_engagement = defaultdict(list)
        
        for post in platform_posts:
            fecha = post.get('fecha_publicacion') or post.get('timestamp')
            if fecha:
                try:
                    if isinstance(fecha, str):
                        fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                    else:
                        fecha_dt = fecha
                    
                    day = fecha_dt.strftime('%A')
                    hour = fecha_dt.hour
                    
                    day_engagement[day].append(post.get('engagement_rate', 0))
                    hour_engagement[hour].append(post.get('engagement_rate', 0))
                except:
                    pass
        
        # Encontrar mejor día
        best_day = None
        if day_engagement:
            day_avg = {day: statistics.mean(rates) for day, rates in day_engagement.items() if rates}
            if day_avg:
                best_day = max(day_avg.items(), key=lambda x: x[1])
        
        # Encontrar mejor hora
        best_hour = None
        if hour_engagement:
            hour_avg = {hour: statistics.mean(rates) for hour, rates in hour_engagement.items() if rates}
            if hour_avg:
                best_hour = max(hour_avg.items(), key=lambda x: x[1])
        
        # Calcular confianza
        confidence = "medium"
        if len(platform_posts) >= 20:
            confidence = "high"
        elif len(platform_posts) < 5:
            confidence = "low"
        
        recommendation = []
        if best_day:
            recommendation.append(f"Mejor día: {best_day[0]} (engagement promedio: {best_day[1]:.2f}%)")
        if best_hour:
            recommendation.append(f"Mejor hora: {best_hour[0]}:00 (engagement promedio: {best_hour[1]:.2f}%)")
        
        return {
            "best_day": best_day[0] if best_day else None,
            "best_day_engagement": round(best_day[1], 2) if best_day else None,
            "best_hour": best_hour[0] if best_hour else None,
            "best_hour_engagement": round(best_hour[1], 2) if best_hour else None,
            "recommendation": " | ".join(recommendation) if recommendation else "Usar horarios estándar de la plataforma",
            "confidence": confidence,
            "sample_size": len(platform_posts)
        }
    
    def generate_insights(self) -> Dict[str, Any]:
        """
        Genera insights completos basados en análisis temporal
        
        Returns:
            Dict con insights y recomendaciones
        """
        insights = {
            "temporal_trends": {},
            "success_patterns": [],
            "recommendations": []
        }
        
        # Analizar tendencias
        for period in ['daily', 'weekly', 'monthly']:
            trend = self.analyze_temporal_trends(period=period)
            insights["temporal_trends"][period] = {
                "direction": trend.trend_direction,
                "growth_rate": trend.growth_rate,
                "confidence": trend.confidence,
                "forecast": trend.forecast_value,
                "anomaly": trend.anomaly_detected
            }
        
        # Detectar patrones de éxito
        patterns = self.detect_success_patterns()
        insights["success_patterns"] = [
            {
                "type": p.pattern_type,
                "description": p.pattern_description,
                "success_rate": p.success_rate,
                "recommendation": p.recommendation
            }
            for p in patterns
        ]
        
        # Generar recomendaciones
        if insights["temporal_trends"].get('weekly', {}).get('direction') == 'decreasing':
            insights["recommendations"].append(
                "El engagement está disminuyendo. Considera revisar tu estrategia de contenido."
            )
        
        if insights["temporal_trends"].get('weekly', {}).get('anomaly'):
            insights["recommendations"].append(
                "Se detectó una anomalía en el engagement. Revisa las publicaciones recientes."
            )
        
        if patterns:
            top_pattern = max(patterns, key=lambda x: x.success_rate)
            insights["recommendations"].append(top_pattern.recommendation)
        
        return insights



