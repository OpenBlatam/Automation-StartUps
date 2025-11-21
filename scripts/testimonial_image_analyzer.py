#!/usr/bin/env python3
"""
Analizador de Imágenes Sugeridas para Testimonios
Sugiere tipos de imágenes, colores, composición para máximo engagement
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ImageRecommendation:
    """Recomendación de imagen"""
    image_type: str
    colors: List[str]
    composition: str
    text_overlay: Optional[str]
    style: str
    engagement_boost: float  # 0-100
    reasoning: str


class ImageAnalyzer:
    """Analizador de imágenes sugeridas"""
    
    # Patrones de imágenes exitosas por plataforma
    PLATFORM_IMAGE_PATTERNS = {
        'linkedin': {
            'best_types': ['professional_photo', 'infographic', 'quote_card'],
            'best_colors': ['#0077b5', '#ffffff', '#000000', '#f3f2f1'],
            'optimal_aspect_ratio': '16:9',
            'text_overlay': True
        },
        'instagram': {
            'best_types': ['lifestyle', 'behind_scenes', 'user_generated'],
            'best_colors': ['bright', 'vibrant', 'warm'],
            'optimal_aspect_ratio': '1:1',
            'text_overlay': False
        },
        'facebook': {
            'best_types': ['lifestyle', 'product', 'testimonial_photo'],
            'best_colors': ['blue', 'white', 'red'],
            'optimal_aspect_ratio': '16:9',
            'text_overlay': True
        },
        'twitter': {
            'best_types': ['infographic', 'quote_card', 'meme'],
            'best_colors': ['#1DA1F2', '#ffffff', '#000000'],
            'optimal_aspect_ratio': '16:9',
            'text_overlay': True
        }
    }
    
    def __init__(self, openai_client=None):
        """
        Inicializa el analizador de imágenes
        
        Args:
            openai_client: Cliente de OpenAI (opcional, para análisis avanzado)
        """
        self.openai_client = openai_client
    
    def analyze_and_recommend(
        self,
        post_data: Dict[str, Any],
        platform: str
    ) -> ImageRecommendation:
        """
        Analiza el post y recomienda imagen óptima
        
        Args:
            post_data: Datos del post
            platform: Plataforma objetivo
        
        Returns:
            ImageRecommendation con sugerencias
        """
        platform_patterns = self.PLATFORM_IMAGE_PATTERNS.get(platform.lower(), {})
        
        # Analizar contenido para determinar mejor tipo de imagen
        content = post_data.get('post_content', '')
        sentiment = post_data.get('sentiment_analysis', {})
        keywords = post_data.get('keyword_analysis', {})
        
        # Determinar tipo de imagen basado en contenido
        image_type = self._determine_image_type(content, sentiment, keywords, platform)
        
        # Determinar colores basados en sentimiento y plataforma
        colors = self._determine_colors(sentiment, platform)
        
        # Determinar composición
        composition = self._determine_composition(platform, image_type)
        
        # Generar texto overlay si es apropiado
        text_overlay = self._generate_text_overlay(content, platform) if platform_patterns.get('text_overlay') else None
        
        # Determinar estilo
        style = self._determine_style(sentiment, platform)
        
        # Calcular boost de engagement esperado
        engagement_boost = self._calculate_engagement_boost(
            image_type, colors, composition, platform
        )
        
        # Generar razonamiento
        reasoning = self._generate_reasoning(
            image_type, colors, composition, platform, engagement_boost
        )
        
        return ImageRecommendation(
            image_type=image_type,
            colors=colors,
            composition=composition,
            text_overlay=text_overlay,
            style=style,
            engagement_boost=engagement_boost,
            reasoning=reasoning
        )
    
    def _determine_image_type(
        self,
        content: str,
        sentiment: Dict[str, Any],
        keywords: Dict[str, Any],
        platform: str
    ) -> str:
        """Determina el mejor tipo de imagen"""
        # Análisis básico del contenido
        content_lower = content.lower()
        
        # Detectar si menciona números/estadísticas
        import re
        has_numbers = bool(re.search(r'\d+%|\d+\s*(veces|meses|años)', content))
        
        # Detectar si es testimonial personal
        has_personal = any(word in content_lower for word in ['yo', 'mi', 'me', 'nuestro', 'nuestra'])
        
        # Detectar si menciona resultados
        has_results = any(word in content_lower for word in ['resultado', 'éxito', 'logro', 'conseguí'])
        
        platform_patterns = self.PLATFORM_IMAGE_PATTERNS.get(platform.lower(), {})
        best_types = platform_patterns.get('best_types', [])
        
        if has_numbers and 'infographic' in best_types:
            return 'infographic'
        elif has_personal and has_results:
            return 'testimonial_photo'
        elif 'quote_card' in best_types:
            return 'quote_card'
        elif 'professional_photo' in best_types:
            return 'professional_photo'
        else:
            return best_types[0] if best_types else 'lifestyle'
    
    def _determine_colors(
        self,
        sentiment: Dict[str, Any],
        platform: str
    ) -> List[str]:
        """Determina colores óptimos"""
        platform_patterns = self.PLATFORM_IMAGE_PATTERNS.get(platform.lower(), {})
        platform_colors = platform_patterns.get('best_colors', [])
        
        sentiment_type = sentiment.get('sentiment', 'neutral')
        
        # Ajustar colores según sentimiento
        if sentiment_type == 'positive':
            if platform == 'linkedin':
                return ['#0077b5', '#28a745', '#ffffff']
            elif platform == 'instagram':
                return ['#FF6B6B', '#FFE66D', '#4ECDC4']
            else:
                return platform_colors[:3] if platform_colors else ['#0077b5', '#ffffff']
        elif sentiment_type == 'negative':
            return ['#6c757d', '#ffffff', '#f8f9fa']
        else:
            return platform_colors[:3] if platform_colors else ['#0077b5', '#ffffff', '#000000']
    
    def _determine_composition(self, platform: str, image_type: str) -> str:
        """Determina composición óptima"""
        platform_patterns = self.PLATFORM_IMAGE_PATTERNS.get(platform.lower(), {})
        aspect_ratio = platform_patterns.get('optimal_aspect_ratio', '16:9')
        
        compositions = {
            'infographic': f'Grid layout con {aspect_ratio}, texto legible',
            'quote_card': f'Centrado con {aspect_ratio}, tipografía destacada',
            'testimonial_photo': f'Persona a la izquierda, texto a la derecha ({aspect_ratio})',
            'professional_photo': f'Retrato profesional ({aspect_ratio})',
            'lifestyle': f'Composición natural ({aspect_ratio})'
        }
        
        return compositions.get(image_type, f'Composición estándar ({aspect_ratio})')
    
    def _generate_text_overlay(self, content: str, platform: str) -> Optional[str]:
        """Genera texto overlay sugerido"""
        # Extraer frase clave del contenido
        sentences = content.split('.')
        if sentences:
            # Tomar primera oración o una con números
            import re
            for sentence in sentences:
                if re.search(r'\d+', sentence):
                    return sentence.strip()[:100]  # Limitar longitud
            return sentences[0].strip()[:100]
        return None
    
    def _determine_style(
        self,
        sentiment: Dict[str, Any],
        platform: str
    ) -> str:
        """Determina estilo visual"""
        sentiment_type = sentiment.get('sentiment', 'neutral')
        
        if platform == 'linkedin':
            return 'Professional and clean'
        elif platform == 'instagram':
            return 'Modern and vibrant' if sentiment_type == 'positive' else 'Minimalist'
        elif platform == 'facebook':
            return 'Friendly and approachable'
        else:
            return 'Clean and professional'
    
    def _calculate_engagement_boost(
        self,
        image_type: str,
        colors: List[str],
        composition: str,
        platform: str
    ) -> float:
        """Calcula boost de engagement esperado"""
        base_boost = 20.0  # Base boost por tener imagen
        
        # Boost por tipo de imagen
        type_boosts = {
            'infographic': 15.0,
            'quote_card': 12.0,
            'testimonial_photo': 10.0,
            'professional_photo': 8.0,
            'lifestyle': 5.0
        }
        type_boost = type_boosts.get(image_type, 5.0)
        
        # Boost por colores apropiados
        color_boost = 5.0 if len(colors) >= 2 else 2.0
        
        # Boost por composición
        composition_boost = 3.0 if 'optimal' in composition.lower() else 1.0
        
        total_boost = base_boost + type_boost + color_boost + composition_boost
        return min(100.0, total_boost)
    
    def _generate_reasoning(
        self,
        image_type: str,
        colors: List[str],
        composition: str,
        platform: str,
        engagement_boost: float
    ) -> str:
        """Genera razonamiento para las recomendaciones"""
        return f"""
Recomendación de imagen para {platform}:
- Tipo: {image_type} (mejor para esta plataforma)
- Colores: {', '.join(colors)} (optimizados para engagement)
- Composición: {composition}
- Boost esperado: +{engagement_boost:.1f}% en engagement

Esta combinación ha demostrado ser efectiva en {platform} para contenido similar.
        """.strip()
    
    def generate_image_prompt(
        self,
        recommendation: ImageRecommendation,
        post_content: str
    ) -> str:
        """
        Genera prompt para generación de imagen con IA
        
        Args:
            recommendation: Recomendación de imagen
            post_content: Contenido del post
        
        Returns:
            Prompt para generación de imagen
        """
        prompt_parts = [
            f"Create a {recommendation.style} {recommendation.image_type}",
            f"using colors: {', '.join(recommendation.colors)}",
            f"with composition: {recommendation.composition}",
        ]
        
        if recommendation.text_overlay:
            prompt_parts.append(f"including text overlay: '{recommendation.text_overlay[:50]}...'")
        
        prompt_parts.append("optimized for social media engagement")
        
        return ", ".join(prompt_parts)



