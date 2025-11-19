"""
Optimizador inteligente de descripciones de productos.

Incluye:
- Recomendaciones basadas en métricas
- Optimización automática de bullets
- Análisis de conversión potencial
- Sugerencias de mejora contextuales
- Comparación de versiones
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class BulletOptimizer:
    """Optimizador de bullet points para descripciones."""
    
    POWER_PHRASES = [
        'garantizado', 'comprobado', 'verificado', 'certificado',
        'exclusivo', 'limitado', 'mejorado', 'avanzado', 'premium',
        'guaranteed', 'proven', 'verified', 'certified',
        'exclusive', 'limited', 'improved', 'advanced'
    ]
    
    NUMBERS_PATTERN = re.compile(r'\d+[xX]|\d+%|\d+\s*(años|horas|días|veces|meses)')
    
    @staticmethod
    def optimize_bullets(bullets: List[str], max_bullets: int = 5) -> List[str]:
        """
        Optimiza una lista de bullets para máximo impacto.
        
        Args:
            bullets: Lista de bullets originales
            max_bullets: Número máximo de bullets
        
        Returns:
            Lista de bullets optimizados
        """
        if not bullets:
            return []
        
        scored_bullets = []
        
        for bullet in bullets:
            score = BulletOptimizer._score_bullet(bullet)
            scored_bullets.append((bullet, score))
        
        # Ordenar por score (mayor a menor)
        scored_bullets.sort(key=lambda x: x[1], reverse=True)
        
        # Tomar los mejores y optimizar
        optimized = []
        for bullet, score in scored_bullets[:max_bullets]:
            optimized_bullet = BulletOptimizer._enhance_bullet(bullet)
            optimized.append(optimized_bullet)
        
        return optimized
    
    @staticmethod
    def _score_bullet(bullet: str) -> float:
        """
        Calcula un score para un bullet basado en características persuasivas.
        
        Args:
            bullet: Texto del bullet
        
        Returns:
            Score (0-100)
        """
        score = 0.0
        bullet_lower = bullet.lower()
        
        # Longitud óptima (20-60 caracteres)
        length = len(bullet)
        if 20 <= length <= 60:
            score += 30
        elif 15 <= length < 20 or 60 < length <= 80:
            score += 20
        else:
            score += 10
        
        # Contiene números/datos específicos
        if BulletOptimizer.NUMBERS_PATTERN.search(bullet):
            score += 25
        
        # Contiene palabras de poder
        power_count = sum(1 for phrase in BulletOptimizer.POWER_PHRASES if phrase in bullet_lower)
        score += min(20, power_count * 5)
        
        # Comienza con mayúscula y termina con punto
        if bullet[0].isupper() and bullet.endswith('.'):
            score += 10
        
        # No tiene palabras negativas
        negative_words = ['no', 'sin', 'sin', 'without', 'not']
        if not any(word in bullet_lower for word in negative_words):
            score += 10
        
        # Tiene acción/beneficio claro
        action_words = ['mejora', 'aumenta', 'reduce', 'proporciona', 'garantiza',
                       'improves', 'increases', 'reduces', 'provides', 'guarantees']
        if any(word in bullet_lower for word in action_words):
            score += 5
        
        return min(100, score)
    
    @staticmethod
    def _enhance_bullet(bullet: str) -> str:
        """
        Mejora un bullet agregando elementos persuasivos si es necesario.
        
        Args:
            bullet: Bullet original
        
        Returns:
            Bullet mejorado
        """
        bullet = bullet.strip()
        
        # Asegurar que comienza con mayúscula
        if bullet and not bullet[0].isupper():
            bullet = bullet[0].upper() + bullet[1:]
        
        # Asegurar que termina con punto
        if bullet and not bullet.endswith(('.', '!', '?')):
            bullet = bullet + '.'
        
        # Remover bullet points existentes
        bullet = re.sub(r'^[•\-\*]\s*', '', bullet)
        
        return bullet
    
    @staticmethod
    def generate_bullets_from_description(description: str, num_bullets: int = 5) -> List[str]:
        """
        Extrae y genera bullets optimizados desde una descripción completa.
        
        Args:
            description: Descripción completa
            num_bullets: Número de bullets a generar
        
        Returns:
            Lista de bullets optimizados
        """
        # Dividir en oraciones
        sentences = re.split(r'[.!?]+', description)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
        
        # Si ya hay bullets, extraerlos
        existing_bullets = []
        lines = description.split('\n')
        for line in lines:
            if re.match(r'^[•\-\*]\s+', line.strip()):
                bullet = re.sub(r'^[•\-\*]\s+', '', line.strip())
                if len(bullet) > 15:
                    existing_bullets.append(bullet)
        
        if existing_bullets:
            return BulletOptimizer.optimize_bullets(existing_bullets, num_bullets)
        
        # Si no hay bullets, crear desde oraciones
        if sentences:
            return BulletOptimizer.optimize_bullets(sentences[:num_bullets * 2], num_bullets)
        
        return []


class ConversionOptimizer:
    """Optimizador basado en potencial de conversión."""
    
    CONVERSION_KEYWORDS = {
        'high': ['garantizado', 'comprobado', 'exclusivo', 'limitado', 'ahora',
                'guaranteed', 'proven', 'exclusive', 'limited', 'now'],
        'medium': ['mejor', 'superior', 'premium', 'avanzado', 'innovador',
                  'better', 'superior', 'premium', 'advanced', 'innovative'],
        'low': ['bueno', 'decente', 'aceptable', 'good', 'decent', 'acceptable']
    }
    
    @staticmethod
    def calculate_conversion_potential(description_data: Dict) -> Dict:
        """
        Calcula el potencial de conversión de una descripción.
        
        Args:
            description_data: Datos de la descripción
        
        Returns:
            Dict con análisis de conversión
        """
        description = description_data.get('description', '').lower()
        word_count = description_data.get('word_count', 0)
        
        # Contar keywords de conversión
        high_conv = sum(1 for kw in ConversionOptimizer.CONVERSION_KEYWORDS['high'] if kw in description)
        medium_conv = sum(1 for kw in ConversionOptimizer.CONVERSION_KEYWORDS['medium'] if kw in description)
        low_conv = sum(1 for kw in ConversionOptimizer.CONVERSION_KEYWORDS['low'] if kw in description)
        
        # Calcular score (0-100)
        conversion_score = (
            high_conv * 10 +
            medium_conv * 5 +
            low_conv * 2
        )
        conversion_score = min(100, conversion_score)
        
        # Factores adicionales
        factors = {
            'has_cta': bool(re.search(r'(compra|adquiere|ordena|ahora|comprar|buy|order|now)', description, re.I)),
            'has_urgency': bool(re.search(r'(limitado|exclusivo|últimas|limited|exclusive|last)', description, re.I)),
            'has_social_proof': bool(re.search(r'(miles|cientos|recomendado|popular|thousands|hundreds|recommended)', description, re.I)),
            'has_benefits': len(re.findall(r'(mejora|aumenta|reduce|proporciona|improves|increases|reduces)', description, re.I)) > 0,
            'optimal_length': 200 <= word_count <= 400
        }
        
        # Ajustar score según factores
        if factors['has_cta']:
            conversion_score += 5
        if factors['has_urgency']:
            conversion_score += 5
        if factors['has_social_proof']:
            conversion_score += 5
        if factors['has_benefits']:
            conversion_score += 5
        if not factors['optimal_length']:
            conversion_score -= 10
        
        conversion_score = max(0, min(100, conversion_score))
        
        # Determinar nivel
        if conversion_score >= 70:
            level = 'high'
        elif conversion_score >= 50:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'conversion_score': round(conversion_score, 1),
            'conversion_level': level,
            'factors': factors,
            'keyword_counts': {
                'high': high_conv,
                'medium': medium_conv,
                'low': low_conv
            },
            'recommendations': ConversionOptimizer._generate_conversion_recommendations(factors, conversion_score)
        }
    
    @staticmethod
    def _generate_conversion_recommendations(factors: Dict, score: float) -> List[str]:
        """Genera recomendaciones para mejorar conversión."""
        recommendations = []
        
        if not factors['has_cta']:
            recommendations.append('Agrega un call-to-action claro (ej: "Compra ahora", "Ordena hoy")')
        
        if not factors['has_urgency']:
            recommendations.append('Crea urgencia con términos como "limitado", "exclusivo" o "últimas unidades"')
        
        if not factors['has_social_proof']:
            recommendations.append('Incluye prueba social (ej: "Miles de clientes satisfechos", "Recomendado por expertos")')
        
        if not factors['has_benefits']:
            recommendations.append('Destaca más beneficios con verbos de acción (mejora, aumenta, reduce)')
        
        if not factors['optimal_length']:
            recommendations.append('Ajusta la longitud a 200-400 palabras para mejor conversión')
        
        if score < 50:
            recommendations.append('Considera revisar la estructura general para aumentar el potencial de conversión')
        
        return recommendations


class DescriptionRecommender:
    """Sistema de recomendaciones inteligentes para descripciones."""
    
    @staticmethod
    def generate_recommendations(description_data: Dict) -> Dict:
        """
        Genera recomendaciones completas para mejorar una descripción.
        
        Args:
            description_data: Datos de la descripción
        
        Returns:
            Dict con recomendaciones categorizadas
        """
        recommendations = {
            'seo': [],
            'conversion': [],
            'structure': [],
            'content': [],
            'priority': []
        }
        
        # Recomendaciones SEO
        seo_analysis = description_data.get('seo_analysis', {})
        if seo_analysis.get('score', 0) < 70:
            recommendations['seo'] = seo_analysis.get('recommendations', [])
        
        # Recomendaciones de conversión
        conversion_analysis = ConversionOptimizer.calculate_conversion_potential(description_data)
        if conversion_analysis['conversion_score'] < 70:
            recommendations['conversion'] = conversion_analysis.get('recommendations', [])
        
        # Recomendaciones de estructura
        description = description_data.get('description', '')
        if not re.search(r'\n\n|\n•|\n-', description):
            recommendations['structure'].append('Considera usar bullets o párrafos para mejor legibilidad')
        
        paragraphs = [p for p in description.split('\n\n') if p.strip()]
        if len(paragraphs) < 2:
            recommendations['structure'].append('Divide el contenido en al menos 2-3 párrafos')
        
        # Recomendaciones de contenido
        word_count = description_data.get('word_count', 0)
        if word_count < 200:
            recommendations['content'].append('Aumenta el contenido a al menos 200 palabras para mejor SEO')
        elif word_count > 400:
            recommendations['content'].append('Considera reducir a 400 palabras máximo para mantener atención')
        
        # Verificar bullets
        bullets = BulletOptimizer.generate_bullets_from_description(description)
        if len(bullets) < 3:
            recommendations['content'].append('Agrega al menos 3-5 bullets destacando beneficios clave')
        
        # Priorizar recomendaciones
        priority_map = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Alta prioridad: SEO bajo, conversión baja
        if seo_analysis.get('score', 100) < 60:
            priority_map['high'].extend(recommendations['seo'][:2])
        if conversion_analysis['conversion_score'] < 60:
            priority_map['high'].extend(recommendations['conversion'][:2])
        
        # Media prioridad: mejoras estructurales
        priority_map['medium'].extend(recommendations['structure'])
        
        # Baja prioridad: optimizaciones menores
        priority_map['low'].extend(recommendations['content'])
        
        recommendations['priority'] = {
            'high': priority_map['high'][:3],
            'medium': priority_map['medium'][:3],
            'low': priority_map['low'][:3]
        }
        
        return recommendations


class VersionComparator:
    """Comparador de versiones de descripciones."""
    
    @staticmethod
    def compare_versions(version1: Dict, version2: Dict) -> Dict:
        """
        Compara dos versiones de descripción y proporciona insights.
        
        Args:
            version1: Primera versión
            version2: Segunda versión
        
        Returns:
            Dict con comparación detallada
        """
        comparison = {
            'word_count_diff': version2.get('word_count', 0) - version1.get('word_count', 0),
            'seo_score_diff': version2.get('seo_analysis', {}).get('score', 0) - version1.get('seo_analysis', {}).get('score', 0),
            'keywords_diff': {
                'added': list(set(version2.get('seo_keywords', [])) - set(version1.get('seo_keywords', []))),
                'removed': list(set(version1.get('seo_keywords', [])) - set(version2.get('seo_keywords', [])))
            },
            'improvements': [],
            'regressions': []
        }
        
        # Analizar mejoras
        if comparison['seo_score_diff'] > 0:
            comparison['improvements'].append(f"SEO mejoró en {comparison['seo_score_diff']:.1f} puntos")
        
        if comparison['word_count_diff'] > 0 and version1.get('word_count', 0) < 200:
            comparison['improvements'].append(f"Longitud aumentó {comparison['word_count_diff']} palabras (mejor para SEO)")
        elif comparison['word_count_diff'] < 0 and version1.get('word_count', 0) > 400:
            comparison['improvements'].append(f"Longitud reducida {abs(comparison['word_count_diff'])} palabras (mejor legibilidad)")
        
        # Analizar regresiones
        if comparison['seo_score_diff'] < 0:
            comparison['regressions'].append(f"SEO disminuyó en {abs(comparison['seo_score_diff']):.1f} puntos")
        
        if len(comparison['keywords_diff']['removed']) > len(comparison['keywords_diff']['added']):
            comparison['regressions'].append("Se removieron más keywords de las que se agregaron")
        
        # Determinar mejor versión
        v1_score = version1.get('seo_analysis', {}).get('score', 0)
        v2_score = version2.get('seo_analysis', {}).get('score', 0)
        
        if v2_score > v1_score:
            comparison['better_version'] = 'version2'
        elif v1_score > v2_score:
            comparison['better_version'] = 'version1'
        else:
            comparison['better_version'] = 'equal'
        
        return comparison






