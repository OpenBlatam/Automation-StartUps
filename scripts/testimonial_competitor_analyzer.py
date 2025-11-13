#!/usr/bin/env python3
"""
Analizador de Competidores para Testimonios
Analiza contenido de competidores y genera insights competitivos
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from collections import Counter, defaultdict
import re

logger = logging.getLogger(__name__)


@dataclass
class CompetitorPost:
    """Post de competidor"""
    platform: str
    content: str
    hashtags: List[str]
    engagement_rate: float
    likes: int
    comments: int
    shares: int
    published_at: Optional[datetime] = None


@dataclass
class CompetitiveInsight:
    """Insight competitivo"""
    insight_type: str
    description: str
    recommendation: str
    impact: str  # "high", "medium", "low"


class CompetitorAnalyzer:
    """Analizador de competidores"""
    
    def __init__(self):
        """Inicializa el analizador"""
        self.competitor_data: List[CompetitorPost] = []
    
    def add_competitor_post(
        self,
        platform: str,
        content: str,
        hashtags: List[str],
        engagement_rate: float,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        published_at: Optional[datetime] = None
    ):
        """Agrega un post de competidor para análisis"""
        post = CompetitorPost(
            platform=platform,
            content=content,
            hashtags=hashtags,
            engagement_rate=engagement_rate,
            likes=likes,
            comments=comments,
            shares=shares,
            published_at=published_at or datetime.now()
        )
        self.competitor_data.append(post)
    
    def analyze_hashtags(self) -> Dict[str, Any]:
        """Analiza hashtags más efectivos de competidores"""
        if not self.competitor_data:
            return {"error": "No hay datos de competidores"}
        
        hashtag_engagement = defaultdict(list)
        
        for post in self.competitor_data:
            for hashtag in post.hashtags:
                hashtag_engagement[hashtag.lower()].append(post.engagement_rate)
        
        # Calcular engagement promedio por hashtag
        hashtag_stats = {}
        for hashtag, rates in hashtag_engagement.items():
            if rates:
                avg_rate = sum(rates) / len(rates)
                hashtag_stats[hashtag] = {
                    "average_engagement_rate": round(avg_rate, 2),
                    "usage_count": len(rates),
                    "max_engagement": round(max(rates), 2)
                }
        
        # Ordenar por engagement promedio
        top_hashtags = sorted(
            hashtag_stats.items(),
            key=lambda x: x[1]["average_engagement_rate"],
            reverse=True
        )[:20]
        
        return {
            "total_unique_hashtags": len(hashtag_stats),
            "top_hashtags": [
                {
                    "hashtag": hashtag,
                    **stats
                }
                for hashtag, stats in top_hashtags
            ]
        }
    
    def analyze_content_patterns(self) -> Dict[str, Any]:
        """Analiza patrones de contenido exitosos"""
        if not self.competitor_data:
            return {"error": "No hay datos de competidores"}
        
        # Analizar longitud
        lengths = [len(post.content) for post in self.competitor_data]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        # Analizar posts con mejor engagement
        top_posts = sorted(
            self.competitor_data,
            key=lambda x: x.engagement_rate,
            reverse=True
        )[:10]
        
        # Patrones comunes en top posts
        top_lengths = [len(post.content) for post in top_posts]
        top_avg_length = sum(top_lengths) / len(top_lengths) if top_lengths else 0
        
        # Analizar presencia de números
        has_numbers = sum(
            1 for post in top_posts
            if re.search(r'\d+', post.content)
        )
        
        # Analizar presencia de preguntas
        has_questions = sum(
            1 for post in top_posts
            if '?' in post.content
        )
        
        # Analizar presencia de emojis
        has_emojis = sum(
            1 for post in top_posts
            if re.search(r'[😀-🙏🌀-🗿]', post.content)
        )
        
        return {
            "average_length": round(avg_length, 0),
            "top_posts_average_length": round(top_avg_length, 0),
            "top_posts_patterns": {
                "has_numbers": has_numbers,
                "has_questions": has_questions,
                "has_emojis": has_emojis,
                "percentage_with_numbers": round((has_numbers / len(top_posts)) * 100, 1) if top_posts else 0,
                "percentage_with_questions": round((has_questions / len(top_posts)) * 100, 1) if top_posts else 0,
                "percentage_with_emojis": round((has_emojis / len(top_posts)) * 100, 1) if top_posts else 0
            },
            "top_engagement_rate": round(top_posts[0].engagement_rate, 2) if top_posts else 0
        }
    
    def analyze_platform_performance(self) -> Dict[str, Any]:
        """Analiza rendimiento por plataforma"""
        if not self.competitor_data:
            return {"error": "No hay datos de competidores"}
        
        platform_stats = defaultdict(lambda: {
            "posts": 0,
            "total_engagement_rate": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_shares": 0
        })
        
        for post in self.competitor_data:
            stats = platform_stats[post.platform]
            stats["posts"] += 1
            stats["total_engagement_rate"] += post.engagement_rate
            stats["total_likes"] += post.likes
            stats["total_comments"] += post.comments
            stats["total_shares"] += post.shares
        
        # Calcular promedios
        result = {}
        for platform, stats in platform_stats.items():
            posts_count = stats["posts"]
            result[platform] = {
                "posts_analyzed": posts_count,
                "average_engagement_rate": round(stats["total_engagement_rate"] / posts_count, 2),
                "average_likes": round(stats["total_likes"] / posts_count, 0),
                "average_comments": round(stats["total_comments"] / posts_count, 0),
                "average_shares": round(stats["total_shares"] / posts_count, 0)
            }
        
        return result
    
    def generate_competitive_insights(
        self,
        your_post: Dict[str, Any]
    ) -> List[CompetitiveInsight]:
        """Genera insights competitivos comparando tu post con competidores"""
        insights = []
        
        if not self.competitor_data:
            return insights
        
        your_engagement = your_post.get('engagement_prediction', {}).get('predicted_engagement_rate', 0)
        your_length = len(your_post.get('post_content', ''))
        your_hashtags_count = len(your_post.get('hashtags', []))
        
        # Analizar hashtags competitivos
        hashtag_analysis = self.analyze_hashtags()
        if hashtag_analysis.get('top_hashtags'):
            your_hashtags = set(h.lower() for h in your_post.get('hashtags', []))
            top_competitor_hashtags = set(
                h['hashtag'] for h in hashtag_analysis['top_hashtags'][:10]
            )
            
            missing_hashtags = top_competitor_hashtags - your_hashtags
            if missing_hashtags:
                insights.append(CompetitiveInsight(
                    insight_type="hashtags",
                    description=f"Competidores usan {len(missing_hashtags)} hashtags de alto engagement que no tienes",
                    recommendation=f"Considera agregar: {', '.join(list(missing_hashtags)[:5])}",
                    impact="medium"
                ))
        
        # Analizar longitud
        content_patterns = self.analyze_content_patterns()
        optimal_length = content_patterns.get('top_posts_average_length', 0)
        
        if optimal_length > 0:
            length_diff = abs(your_length - optimal_length)
            if length_diff > optimal_length * 0.2:  # Más del 20% de diferencia
                if your_length < optimal_length:
                    insights.append(CompetitiveInsight(
                        insight_type="length",
                        description=f"Tu contenido es {int(optimal_length - your_length)} caracteres más corto que el promedio de posts exitosos",
                        recommendation=f"Considera expandir a ~{int(optimal_length)} caracteres para mejor engagement",
                        impact="high"
                    ))
                else:
                    insights.append(CompetitiveInsight(
                        insight_type="length",
                        description=f"Tu contenido es {int(your_length - optimal_length)} caracteres más largo que el promedio",
                        recommendation="Considera acortar para mantener atención",
                        impact="medium"
                    ))
        
        # Comparar engagement
        platform_perf = self.analyze_platform_performance()
        platform = your_post.get('platform', 'linkedin')
        
        if platform in platform_perf:
            competitor_avg = platform_perf[platform]['average_engagement_rate']
            if your_engagement < competitor_avg * 0.8:  # 20% menos que competidores
                insights.append(CompetitiveInsight(
                    insight_type="engagement",
                    description=f"Tu engagement predicho ({your_engagement:.2f}%) está por debajo del promedio competitivo ({competitor_avg:.2f}%)",
                    recommendation="Revisa estrategia de contenido y optimizaciones sugeridas",
                    impact="high"
                ))
            elif your_engagement > competitor_avg * 1.2:  # 20% más que competidores
                insights.append(CompetitiveInsight(
                    insight_type="engagement",
                    description=f"¡Excelente! Tu engagement predicho ({your_engagement:.2f}%) supera el promedio competitivo ({competitor_avg:.2f}%)",
                    recommendation="Mantén esta estrategia y considera replicar en otras plataformas",
                    impact="low"
                ))
        
        # Analizar patrones de contenido
        patterns = content_patterns.get('top_posts_patterns', {})
        your_content = your_post.get('post_content', '')
        
        if patterns.get('percentage_with_numbers', 0) > 50:
            if not re.search(r'\d+', your_content):
                insights.append(CompetitiveInsight(
                    insight_type="content_pattern",
                    description=f"{patterns['percentage_with_numbers']:.0f}% de posts exitosos incluyen números",
                    recommendation="Agrega números específicos o porcentajes para mayor credibilidad",
                    impact="medium"
                ))
        
        return insights
    
    def get_competitive_report(
        self,
        your_post: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera reporte competitivo completo"""
        return {
            "your_post_metrics": {
                "engagement_rate": your_post.get('engagement_prediction', {}).get('predicted_engagement_rate', 0),
                "length": len(your_post.get('post_content', '')),
                "hashtags_count": len(your_post.get('hashtags', []))
            },
            "competitor_hashtags": self.analyze_hashtags(),
            "competitor_content_patterns": self.analyze_content_patterns(),
            "platform_performance": self.analyze_platform_performance(),
            "competitive_insights": [
                {
                    "type": insight.insight_type,
                    "description": insight.description,
                    "recommendation": insight.recommendation,
                    "impact": insight.impact
                }
                for insight in self.generate_competitive_insights(your_post)
            ],
            "competitors_analyzed": len(self.competitor_data)
        }


