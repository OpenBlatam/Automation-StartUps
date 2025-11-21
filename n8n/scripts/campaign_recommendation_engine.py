#!/usr/bin/env python3
"""
Campaign Recommendation Engine
Sistema de recomendaciones inteligentes para campañas
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import math


class CampaignRecommendationEngine:
    """
    Motor de recomendaciones para campañas
    Recomienda contenido, timing, plataformas y estrategias
    """
    
    def __init__(self, n8n_base_url: str, api_key: str):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def recommend_content(
        self,
        user_profile: Dict[str, Any],
        campaign_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Recomienda contenido personalizado
        
        Args:
            user_profile: Perfil del usuario
            campaign_context: Contexto de la campaña
        
        Returns:
            Lista de recomendaciones de contenido
        """
        recommendations = []
        
        # Recomendación basada en intereses
        interests = user_profile.get("interests", [])
        if "tecnología" in interests:
            recommendations.append({
                "type": "content",
                "priority": "high",
                "title": "Contenido Tecnológico",
                "description": "El usuario muestra interés en tecnología",
                "suggestedContent": {
                    "format": "video",
                    "topics": ["innovación", "tecnología", "futuro"],
                    "tone": "informative"
                },
                "expectedEngagement": 0.08
            })
        
        # Recomendación basada en comportamiento
        if user_profile.get("engagementLevel") == "high":
            recommendations.append({
                "type": "content",
                "priority": "high",
                "title": "Contenido Interactivo",
                "description": "Usuario altamente comprometido, responde bien a contenido interactivo",
                "suggestedContent": {
                    "format": "carousel",
                    "topics": ["beneficios", "testimonios", "casos de uso"],
                    "tone": "engaging"
                },
                "expectedEngagement": 0.12
            })
        
        # Recomendación basada en historial
        past_interactions = user_profile.get("pastInteractions", [])
        if any(i.get("type") == "video" for i in past_interactions):
            recommendations.append({
                "type": "content",
                "priority": "medium",
                "title": "Video Tutorial",
                "description": "Usuario prefiere contenido en video",
                "suggestedContent": {
                    "format": "video",
                    "topics": ["tutorial", "demo", "cómo funciona"],
                    "tone": "educational"
                },
                "expectedEngagement": 0.10
            })
        
        return recommendations
    
    def recommend_timing(
        self,
        user_profile: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Recomienda timing óptimo para publicar
        
        Args:
            user_profile: Perfil del usuario
            historical_data: Datos históricos de engagement
        
        Returns:
            Dict con recomendaciones de timing
        """
        # Análisis de zona horaria
        timezone = user_profile.get("timezone", "UTC")
        
        # Horarios óptimos basados en datos históricos
        optimal_hours = [9, 12, 15, 18, 21]  # Default
        
        if historical_data:
            # Analizar horarios con mejor engagement
            hour_engagement = defaultdict(list)
            for data in historical_data:
                hour = data.get("hour", 12)
                engagement = data.get("engagementRate", 0)
                hour_engagement[hour].append(engagement)
            
            # Calcular promedio por hora
            hour_avg = {
                hour: sum(engagements) / len(engagements)
                for hour, engagements in hour_engagement.items()
            }
            
            # Top 3 horas
            optimal_hours = sorted(hour_avg.items(), key=lambda x: x[1], reverse=True)[:3]
            optimal_hours = [h[0] for h in optimal_hours]
        
        # Días óptimos
        optimal_days = ["Monday", "Wednesday", "Friday"]  # Default
        
        return {
            "optimalHours": optimal_hours,
            "optimalDays": optimal_days,
            "timezone": timezone,
            "nextBestTime": self._calculate_next_best_time(optimal_hours),
            "confidence": 0.8 if historical_data else 0.5
        }
    
    def recommend_platforms(
        self,
        user_profile: Dict[str, Any],
        campaign_goals: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Recomienda plataformas óptimas
        
        Args:
            user_profile: Perfil del usuario
            campaign_goals: Objetivos de la campaña
        
        Returns:
            Lista de recomendaciones de plataformas
        """
        recommendations = []
        
        # Análisis de demografía
        age = user_profile.get("age", 30)
        platform_preferences = user_profile.get("platformPreferences", {})
        
        # Instagram para audiencia joven
        if age < 35:
            recommendations.append({
                "platform": "instagram",
                "priority": "high",
                "reason": "Audiencia joven, alta engagement",
                "expectedReach": 5000,
                "expectedEngagement": 0.06
            })
        
        # LinkedIn para audiencia profesional
        if age > 30 and user_profile.get("profession") == "business":
            recommendations.append({
                "platform": "linkedin",
                "priority": "high",
                "reason": "Audiencia profesional, alto valor",
                "expectedReach": 2000,
                "expectedEngagement": 0.04
            })
        
        # Facebook para alcance amplio
        if campaign_goals.get("primaryGoal") == "reach":
            recommendations.append({
                "platform": "facebook",
                "priority": "medium",
                "reason": "Alcance amplio, buena para awareness",
                "expectedReach": 8000,
                "expectedEngagement": 0.03
            })
        
        # TikTok para contenido viral
        if age < 30 and campaign_goals.get("primaryGoal") == "viral":
            recommendations.append({
                "platform": "tiktok",
                "priority": "high",
                "reason": "Potencial viral, audiencia joven",
                "expectedReach": 10000,
                "expectedEngagement": 0.08
            })
        
        # Ordenar por prioridad
        recommendations.sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x["priority"], 0), reverse=True)
        
        return recommendations
    
    def recommend_strategy(
        self,
        campaign_metrics: Dict[str, Any],
        competitor_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recomienda estrategia completa de campaña
        
        Args:
            campaign_metrics: Métricas actuales de la campaña
            competitor_analysis: Análisis de competencia (opcional)
        
        Returns:
            Dict con recomendaciones estratégicas
        """
        strategy = {
            "overview": {
                "currentPerformance": "good" if campaign_metrics.get("engagementRate", 0) > 0.05 else "needs_improvement",
                "keyInsights": [],
                "recommendedFocus": []
            },
            "content": {
                "recommendedFormats": [],
                "recommendedTopics": [],
                "recommendedTone": "engaging"
            },
            "distribution": {
                "recommendedPlatforms": [],
                "recommendedTiming": {},
                "recommendedFrequency": "daily"
            },
            "optimization": {
                "immediateActions": [],
                "shortTermActions": [],
                "longTermActions": []
            }
        }
        
        # Análisis de performance
        engagement = campaign_metrics.get("engagementRate", 0)
        conversion = campaign_metrics.get("conversionRate", 0)
        
        if engagement < 0.03:
            strategy["overview"]["keyInsights"].append("Engagement bajo, necesita optimización urgente")
            strategy["optimization"]["immediateActions"].append("Mejorar calidad de contenido")
            strategy["optimization"]["immediateActions"].append("Optimizar hashtags")
        
        if conversion < 0.05:
            strategy["overview"]["keyInsights"].append("Conversión baja, revisar funnel")
            strategy["optimization"]["immediateActions"].append("Mejorar CTA")
            strategy["optimization"]["immediateActions"].append("Optimizar landing page")
        
        # Recomendaciones de contenido
        if engagement < 0.05:
            strategy["content"]["recommendedFormats"] = ["video", "carousel"]
            strategy["content"]["recommendedTopics"] = ["beneficios", "testimonios", "casos de uso"]
        
        # Recomendaciones de distribución
        strategy["distribution"]["recommendedPlatforms"] = ["instagram", "facebook", "linkedin"]
        strategy["distribution"]["recommendedTiming"] = {
            "optimalHours": [9, 12, 15, 18],
            "optimalDays": ["Monday", "Wednesday", "Friday"]
        }
        
        return strategy
    
    def _calculate_next_best_time(self, optimal_hours: List[int]) -> Dict[str, Any]:
        """Calcula el próximo mejor momento para publicar"""
        now = datetime.now()
        current_hour = now.hour
        
        # Encontrar próxima hora óptima
        next_hour = None
        for hour in sorted(optimal_hours):
            if hour > current_hour:
                next_hour = hour
                break
        
        if next_hour is None:
            next_hour = optimal_hours[0]  # Próximo día
        
        hours_until = (next_hour - current_hour) % 24
        
        return {
            "hour": next_hour,
            "hoursUntil": hours_until,
            "datetime": (now.replace(hour=next_hour, minute=0, second=0, microsecond=0) 
                        if hours_until > 0 
                        else (now.replace(hour=next_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)))
        }


def main():
    """Ejemplo de uso"""
    engine = CampaignRecommendationEngine(
        n8n_base_url="https://your-n8n.com",
        api_key="your_api_key"
    )
    
    # Perfil de usuario
    user_profile = {
        "age": 28,
        "interests": ["tecnología", "marketing"],
        "engagementLevel": "high",
        "timezone": "America/Mexico_City",
        "platformPreferences": {"instagram": 0.8, "linkedin": 0.6},
        "pastInteractions": [{"type": "video", "engagement": 0.12}]
    }
    
    # Recomendar contenido
    content_recs = engine.recommend_content(user_profile, {})
    print("=== Recomendaciones de Contenido ===")
    print(json.dumps(content_recs, indent=2, ensure_ascii=False))
    
    # Recomendar timing
    timing_recs = engine.recommend_timing(user_profile)
    print("\n=== Recomendaciones de Timing ===")
    print(json.dumps(timing_recs, indent=2, ensure_ascii=False))
    
    # Recomendar plataformas
    platform_recs = engine.recommend_platforms(user_profile, {"primaryGoal": "reach"})
    print("\n=== Recomendaciones de Plataformas ===")
    print(json.dumps(platform_recs, indent=2, ensure_ascii=False))
    
    # Recomendar estrategia
    campaign_metrics = {
        "engagementRate": 0.04,
        "conversionRate": 0.08
    }
    strategy = engine.recommend_strategy(campaign_metrics)
    print("\n=== Recomendaciones Estratégicas ===")
    print(json.dumps(strategy, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

