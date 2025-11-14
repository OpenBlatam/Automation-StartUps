#!/usr/bin/env python3
"""
Campaign Competitor Analyzer
Analiza estrategias de competencia para optimizar campañas
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict


class CampaignCompetitorAnalyzer:
    """
    Analizador de competencia para campañas
    Analiza estrategias, contenido y timing de competidores
    """
    
    def __init__(self, n8n_base_url: str, api_key: str):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def analyze_competitor_content(
        self,
        competitor_id: str,
        platform: str = "instagram",
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analiza contenido de un competidor
        
        Args:
            competitor_id: ID o username del competidor
            platform: Plataforma a analizar
            days_back: Días hacia atrás para analizar
        
        Returns:
            Dict con análisis del contenido
        """
        # En producción, esto consultaría APIs de redes sociales
        # Por ahora, retornamos estructura de ejemplo
        
        analysis = {
            "competitorId": competitor_id,
            "platform": platform,
            "period": {
                "start": (datetime.now() - timedelta(days=days_back)).isoformat(),
                "end": datetime.now().isoformat()
            },
            "contentAnalysis": {
                "totalPosts": 0,
                "averageEngagementRate": 0.0,
                "bestPerformingPost": None,
                "worstPerformingPost": None,
                "contentTypes": {},
                "hashtags": {},
                "postingFrequency": {},
                "optimalPostingTimes": []
            },
            "strategy": {
                "captionLength": {"avg": 0, "min": 0, "max": 0},
                "hashtagCount": {"avg": 0, "min": 0, "max": 0},
                "ctaFrequency": 0.0,
                "emojiUsage": 0.0
            },
            "recommendations": []
        }
        
        return analysis
    
    def compare_with_competitors(
        self,
        your_metrics: Dict[str, Any],
        competitor_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compara tus métricas con competidores
        
        Args:
            your_metrics: Tus métricas actuales
            competitor_metrics: Lista de métricas de competidores
        
        Returns:
            Dict con comparación y recomendaciones
        """
        # Calcular promedios de competidores
        avg_engagement = statistics.mean([c.get("engagementRate", 0) for c in competitor_metrics])
        avg_conversion = statistics.mean([c.get("conversionRate", 0) for c in competitor_metrics])
        avg_reach = statistics.mean([c.get("averageReach", 0) for c in competitor_metrics])
        
        your_engagement = your_metrics.get("engagementRate", 0)
        your_conversion = your_metrics.get("conversionRate", 0)
        your_reach = your_metrics.get("averageReach", 0)
        
        # Calcular gaps
        engagement_gap = your_engagement - avg_engagement
        conversion_gap = your_conversion - avg_conversion
        reach_gap = your_reach - avg_reach
        
        # Generar recomendaciones
        recommendations = []
        
        if engagement_gap < -0.02:  # 2% por debajo
            recommendations.append({
                "metric": "engagement",
                "priority": "high",
                "message": f"Tu engagement está {abs(engagement_gap):.2%} por debajo del promedio de competidores",
                "action": "Revisar contenido, hashtags y timing de publicaciones"
            })
        
        if conversion_gap < -0.05:  # 5% por debajo
            recommendations.append({
                "metric": "conversion",
                "priority": "critical",
                "message": f"Tu tasa de conversión está {abs(conversion_gap):.2%} por debajo del promedio",
                "action": "Optimizar oferta, CTA y landing page urgentemente"
            })
        
        if reach_gap < -1000:  # 1000 usuarios por debajo
            recommendations.append({
                "metric": "reach",
                "priority": "medium",
                "message": f"Tu alcance está {abs(reach_gap):,.0f} usuarios por debajo del promedio",
                "action": "Amplificar en más plataformas y usar hashtags trending"
            })
        
        return {
            "yourMetrics": your_metrics,
            "competitorAverages": {
                "engagementRate": avg_engagement,
                "conversionRate": avg_conversion,
                "averageReach": avg_reach
            },
            "gaps": {
                "engagement": engagement_gap,
                "conversion": conversion_gap,
                "reach": reach_gap
            },
            "benchmark": {
                "engagement": "above" if engagement_gap > 0 else "below",
                "conversion": "above" if conversion_gap > 0 else "below",
                "reach": "above" if reach_gap > 0 else "below"
            },
            "recommendations": recommendations,
            "analyzedAt": datetime.now().isoformat()
        }
    
    def identify_opportunities(
        self,
        competitor_data: List[Dict[str, Any]],
        your_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identifica oportunidades basadas en análisis de competencia
        
        Args:
            competitor_data: Datos de competidores
            your_data: Tus datos
        
        Returns:
            Lista de oportunidades identificadas
        """
        opportunities = []
        
        # Oportunidad: Hashtags trending que no usas
        competitor_hashtags = set()
        for comp in competitor_data:
            competitor_hashtags.update(comp.get("topHashtags", []))
        
        your_hashtags = set(your_data.get("hashtags", []))
        unused_hashtags = competitor_hashtags - your_hashtags
        
        if unused_hashtags:
            opportunities.append({
                "type": "hashtags",
                "priority": "medium",
                "title": "Hashtags Trending No Utilizados",
                "description": f"Competidores están usando {len(unused_hashtags)} hashtags que tú no usas",
                "action": f"Considerar agregar: {', '.join(list(unused_hashtags)[:10])}",
                "potentialImpact": "+10-15% engagement"
            })
        
        # Oportunidad: Horarios óptimos
        competitor_times = []
        for comp in competitor_data:
            competitor_times.extend(comp.get("optimalPostingTimes", []))
        
        if competitor_times:
            most_common_time = max(set(competitor_times), key=competitor_times.count)
            opportunities.append({
                "type": "timing",
                "priority": "high",
                "title": "Horario Óptimo Identificado",
                "description": f"Competidores publican más frecuentemente a las {most_common_time}:00",
                "action": f"Programar publicaciones para las {most_common_time}:00",
                "potentialImpact": "+15-20% engagement"
            })
        
        # Oportunidad: Tipo de contenido
        content_types = defaultdict(int)
        for comp in competitor_data:
            for content_type, count in comp.get("contentTypes", {}).items():
                content_types[content_type] += count
        
        if content_types:
            best_type = max(content_types.items(), key=lambda x: x[1])[0]
            opportunities.append({
                "type": "content",
                "priority": "medium",
                "title": "Tipo de Contenido Efectivo",
                "description": f"El tipo de contenido más usado por competidores es: {best_type}",
                "action": f"Incrementar producción de contenido tipo: {best_type}",
                "potentialImpact": "+20-25% engagement"
            })
        
        return opportunities
    
    def generate_competitive_strategy(
        self,
        analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Genera estrategia competitiva basada en análisis
        
        Args:
            analysis: Análisis de competencia
            opportunities: Oportunidades identificadas
        
        Returns:
            Estrategia competitiva recomendada
        """
        strategy = {
            "overview": {
                "yourPosition": "competitive" if analysis["benchmark"]["engagement"] == "above" else "needs_improvement",
                "keyStrengths": [],
                "keyWeaknesses": [],
                "competitiveAdvantage": []
            },
            "tactics": [],
            "timeline": {
                "immediate": [],
                "shortTerm": [],
                "longTerm": []
            }
        }
        
        # Identificar fortalezas y debilidades
        if analysis["gaps"]["engagement"] > 0:
            strategy["overview"]["keyStrengths"].append("Engagement superior a competidores")
        else:
            strategy["overview"]["keyWeaknesses"].append("Engagement por debajo de competidores")
        
        if analysis["gaps"]["conversion"] > 0:
            strategy["overview"]["keyStrengths"].append("Conversión superior a competidores")
        else:
            strategy["overview"]["keyWeaknesses"].append("Conversión por debajo de competidores")
        
        # Generar tácticas basadas en oportunidades
        for opp in opportunities:
            if opp["priority"] == "critical" or opp["priority"] == "high":
                strategy["tactics"].append({
                    "action": opp["action"],
                    "priority": opp["priority"],
                    "expectedImpact": opp.get("potentialImpact", "Unknown"),
                    "timeline": "immediate"
                })
                strategy["timeline"]["immediate"].append(opp["title"])
            elif opp["priority"] == "medium":
                strategy["tactics"].append({
                    "action": opp["action"],
                    "priority": opp["priority"],
                    "expectedImpact": opp.get("potentialImpact", "Unknown"),
                    "timeline": "shortTerm"
                })
                strategy["timeline"]["shortTerm"].append(opp["title"])
        
        return strategy


def main():
    """Ejemplo de uso"""
    analyzer = CampaignCompetitorAnalyzer(
        n8n_base_url="https://your-n8n.com",
        api_key="your_api_key"
    )
    
    # Tus métricas
    your_metrics = {
        "engagementRate": 0.04,
        "conversionRate": 0.08,
        "averageReach": 3000
    }
    
    # Métricas de competidores
    competitor_metrics = [
        {"engagementRate": 0.06, "conversionRate": 0.10, "averageReach": 5000},
        {"engagementRate": 0.05, "conversionRate": 0.12, "averageReach": 4000},
        {"engagementRate": 0.07, "conversionRate": 0.09, "averageReach": 6000}
    ]
    
    # Comparar
    comparison = analyzer.compare_with_competitors(your_metrics, competitor_metrics)
    print("=== Comparación con Competidores ===")
    print(json.dumps(comparison, indent=2, ensure_ascii=False))
    
    # Identificar oportunidades
    competitor_data = [
        {
            "topHashtags": ["#Lanzamiento", "#NuevoProducto", "#Oferta"],
            "optimalPostingTimes": [9, 14, 18],
            "contentTypes": {"video": 10, "image": 5, "carousel": 3}
        },
        {
            "topHashtags": ["#Lanzamiento", "#Producto", "#Descuento"],
            "optimalPostingTimes": [10, 15, 19],
            "contentTypes": {"video": 8, "image": 7, "carousel": 4}
        }
    ]
    
    your_data = {
        "hashtags": ["#Lanzamiento", "#Producto"]
    }
    
    opportunities = analyzer.identify_opportunities(competitor_data, your_data)
    print("\n=== Oportunidades Identificadas ===")
    print(json.dumps(opportunities, indent=2, ensure_ascii=False))
    
    # Generar estrategia
    strategy = analyzer.generate_competitive_strategy(comparison, opportunities)
    print("\n=== Estrategia Competitiva ===")
    print(json.dumps(strategy, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()



