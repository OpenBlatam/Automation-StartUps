#!/usr/bin/env python3
"""
Comparador de Variaciones de Testimonios
Compara múltiples variaciones y recomienda la mejor
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class VariationComparison:
    """Comparación entre variaciones"""
    variation_number: int
    engagement_score: float
    length_score: float
    hashtag_score: float
    content_quality_score: float
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str


class VariationComparator:
    """Compara y analiza múltiples variaciones de publicaciones"""
    
    def __init__(self):
        """Inicializa el comparador"""
        pass
    
    def compare_variations(
        self,
        variations: List[Dict[str, Any]],
        platform: str = "general"
    ) -> Dict[str, Any]:
        """
        Compara múltiples variaciones y genera análisis
        
        Args:
            variations: Lista de variaciones a comparar
            platform: Plataforma objetivo
        
        Returns:
            Dict con análisis comparativo completo
        """
        if not variations:
            return {"error": "No hay variaciones para comparar"}
        
        comparisons = []
        
        # Analizar cada variación
        for var in variations:
            comparison = self._analyze_variation(var, platform)
            comparisons.append(comparison)
        
        # Encontrar la mejor variación
        best_variation = max(comparisons, key=lambda x: x.overall_score)
        
        # Generar insights comparativos
        insights = self._generate_insights(comparisons, platform)
        
        # Recomendaciones finales
        recommendations = self._generate_recommendations(comparisons, best_variation)
        
        return {
            "total_variations": len(variations),
            "comparisons": [asdict(comp) for comp in comparisons],
            "best_variation": {
                "variation_number": best_variation.variation_number,
                "overall_score": best_variation.overall_score,
                "recommendation": best_variation.recommendation
            },
            "insights": insights,
            "recommendations": recommendations,
            "summary": self._generate_summary(comparisons, best_variation)
        }
    
    def _analyze_variation(
        self,
        variation: Dict[str, Any],
        platform: str
    ) -> VariationComparison:
        """Analiza una variación individual"""
        var_num = variation.get("variation_number", 0)
        
        # Score de engagement (40 puntos)
        engagement_score = 0
        if "engagement_prediction" in variation:
            pred = variation["engagement_prediction"]
            engagement_score = pred.get("predicted_score", 0) * 0.4
        else:
            # Estimación básica si no hay predicción
            engagement_score = 20  # Score base
        
        # Score de longitud (20 puntos)
        length = variation.get("length", 0)
        optimal_lengths = {
            'instagram': 200, 'linkedin': 300, 'facebook': 250,
            'twitter': 200, 'tiktok': 150
        }
        optimal = optimal_lengths.get(platform, 200)
        length_diff = abs(length - optimal)
        length_score = max(0, 20 - (length_diff / optimal) * 20)
        
        # Score de hashtags (20 puntos)
        hashtags = variation.get("hashtags", [])
        optimal_counts = {
            'instagram': 10, 'linkedin': 5, 'facebook': 5,
            'twitter': 3, 'tiktok': 5
        }
        optimal_count = optimal_counts.get(platform, 5)
        hashtag_count = len(hashtags)
        if hashtag_count == optimal_count:
            hashtag_score = 20
        elif hashtag_count > 0:
            hashtag_score = max(0, 20 - abs(hashtag_count - optimal_count) * 2)
        else:
            hashtag_score = 0
        
        # Score de calidad de contenido (20 puntos)
        content_score = 20
        post_content = variation.get("post_content", "")
        
        # Penalizar si no tiene CTA
        if not variation.get("call_to_action"):
            content_score -= 5
        
        # Bonificar si tiene números
        import re
        if not re.search(r'\d+', post_content):
            content_score -= 3
        
        # Bonificar si tiene estructura narrativa
        storytelling_indicators = [
            r'\b(antes|después|entonces|cuando|mientras|finalmente)\b',
            r'\b(logré|conseguí|obtuve|alcanzé|mejoré)\b'
        ]
        if sum(1 for pattern in storytelling_indicators if re.search(pattern, post_content, re.IGNORECASE)) >= 2:
            content_score += 3
        
        content_score = max(0, min(20, content_score))
        
        # Score total
        overall_score = engagement_score + length_score + hashtag_score + content_score
        
        # Identificar fortalezas y debilidades
        strengths = []
        weaknesses = []
        
        if engagement_score >= 30:
            strengths.append("Excelente predicción de engagement")
        elif engagement_score < 20:
            weaknesses.append("Baja predicción de engagement")
        
        if length_score >= 18:
            strengths.append("Longitud óptima")
        elif length_score < 12:
            weaknesses.append("Longitud no óptima")
        
        if hashtag_score >= 18:
            strengths.append("Hashtags bien optimizados")
        elif hashtag_score < 10:
            weaknesses.append("Faltan o sobran hashtags")
        
        if content_score >= 18:
            strengths.append("Alta calidad de contenido")
        elif content_score < 12:
            weaknesses.append("Contenido necesita mejoras")
        
        # Recomendación
        if overall_score >= 80:
            recommendation = "Excelente - Usar esta variación"
        elif overall_score >= 65:
            recommendation = "Buena - Considerar usar con mejoras menores"
        elif overall_score >= 50:
            recommendation = "Aceptable - Necesita optimizaciones"
        else:
            recommendation = "Mejorar - Requiere cambios significativos"
        
        return VariationComparison(
            variation_number=var_num,
            engagement_score=round(engagement_score, 1),
            length_score=round(length_score, 1),
            hashtag_score=round(hashtag_score, 1),
            content_quality_score=round(content_score, 1),
            overall_score=round(overall_score, 1),
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation
        )
    
    def _generate_insights(
        self,
        comparisons: List[VariationComparison],
        platform: str
    ) -> Dict[str, Any]:
        """Genera insights comparativos"""
        insights = {
            "score_range": {
                "min": min(c.overall_score for c in comparisons),
                "max": max(c.overall_score for c in comparisons),
                "average": sum(c.overall_score for c in comparisons) / len(comparisons)
            },
            "best_aspects": defaultdict(list),
            "common_weaknesses": [],
            "variability": {}
        }
        
        # Analizar mejores aspectos
        best_engagement = max(comparisons, key=lambda x: x.engagement_score)
        best_length = max(comparisons, key=lambda x: x.length_score)
        best_hashtags = max(comparisons, key=lambda x: x.hashtag_score)
        best_content = max(comparisons, key=lambda x: x.content_quality_score)
        
        insights["best_aspects"]["engagement"] = best_engagement.variation_number
        insights["best_aspects"]["length"] = best_length.variation_number
        insights["best_aspects"]["hashtags"] = best_hashtags.variation_number
        insights["best_aspects"]["content"] = best_content.variation_number
        
        # Debilidades comunes
        all_weaknesses = []
        for comp in comparisons:
            all_weaknesses.extend(comp.weaknesses)
        
        weakness_counts = defaultdict(int)
        for weakness in all_weaknesses:
            weakness_counts[weakness] += 1
        
        insights["common_weaknesses"] = [
            w for w, count in sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)
            if count >= len(comparisons) * 0.5  # Aparece en al menos 50% de variaciones
        ]
        
        # Variabilidad
        scores = [c.overall_score for c in comparisons]
        score_range = max(scores) - min(scores)
        insights["variability"] = {
            "range": round(score_range, 1),
            "is_consistent": score_range < 15,  # Variaciones consistentes si diferencia < 15 puntos
            "recommendation": "Usar la mejor variación" if score_range >= 10 else "Todas las variaciones son similares"
        }
        
        return insights
    
    def _generate_recommendations(
        self,
        comparisons: List[VariationComparison],
        best: VariationComparison
    ) -> List[str]:
        """Genera recomendaciones basadas en la comparación"""
        recommendations = []
        
        recommendations.append(f"Variación #{best.variation_number} es la mejor opción (Score: {best.overall_score}/100)")
        
        # Recomendaciones específicas
        if best.engagement_score < 30:
            recommendations.append("Considera mejorar el engagement agregando más elementos interactivos")
        
        if best.length_score < 15:
            recommendations.append("Ajusta la longitud del contenido para mejor rendimiento")
        
        if best.hashtag_score < 15:
            recommendations.append("Optimiza la cantidad y calidad de hashtags")
        
        # Si hay variaciones muy diferentes, recomendar A/B testing
        scores = [c.overall_score for c in comparisons]
        if max(scores) - min(scores) > 20:
            recommendations.append("Las variaciones son muy diferentes - considera hacer A/B testing")
        
        return recommendations
    
    def _generate_summary(
        self,
        comparisons: List[VariationComparison],
        best: VariationComparison
    ) -> str:
        """Genera un resumen textual"""
        lines = []
        lines.append(f"Análisis de {len(comparisons)} variaciones:")
        lines.append(f"Mejor variación: #{best.variation_number} (Score: {best.overall_score}/100)")
        lines.append(f"\nFortalezas de la mejor variación:")
        for strength in best.strengths:
            lines.append(f"  • {strength}")
        
        if best.weaknesses:
            lines.append(f"\nÁreas de mejora:")
            for weakness in best.weaknesses[:3]:
                lines.append(f"  • {weakness}")
        
        return "\n".join(lines)


def asdict(obj):
    """Convierte dataclass a dict"""
    from dataclasses import asdict as dc_asdict
    return dc_asdict(obj)


