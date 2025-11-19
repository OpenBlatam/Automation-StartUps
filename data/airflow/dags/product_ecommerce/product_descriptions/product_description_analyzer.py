"""
Analizador avanzado de descripciones de productos.

Incluye:
- Análisis de sentimiento
- Análisis de tono
- Scoring de calidad
- Análisis de legibilidad
- Detección de palabras de poder
- Análisis de estructura
"""

import re
import logging
from typing import Dict, List, Optional
from collections import Counter
import math

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analizador de sentimiento y tono de texto."""
    
    # Palabras positivas comunes
    POSITIVE_WORDS = {
        'excelente', 'perfecto', 'increíble', 'fantástico', 'maravilloso',
        'superior', 'premium', 'excepcional', 'destacado', 'innovador',
        'revolucionario', 'único', 'especial', 'mejor', 'óptimo',
        'excellent', 'perfect', 'amazing', 'fantastic', 'wonderful',
        'superior', 'premium', 'exceptional', 'outstanding', 'innovative'
    }
    
    # Palabras negativas (a evitar)
    NEGATIVE_WORDS = {
        'malo', 'peor', 'defectuoso', 'barato', 'inferior',
        'bad', 'worse', 'defective', 'cheap', 'inferior'
    }
    
    # Palabras de poder (aumentan persuasión)
    POWER_WORDS = {
        'garantizado', 'comprobado', 'verificado', 'certificado',
        'exclusivo', 'limitado', 'nuevo', 'mejorado', 'avanzado',
        'guaranteed', 'proven', 'verified', 'certified',
        'exclusive', 'limited', 'new', 'improved', 'advanced'
    }
    
    @staticmethod
    def analyze_sentiment(text: str) -> Dict:
        """
        Analiza el sentimiento del texto.
        
        Args:
            text: Texto a analizar
        
        Returns:
            Dict con análisis de sentimiento
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        
        if total_words == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'power_words_count': 0
            }
        
        positive_count = sum(1 for word in words if word in SentimentAnalyzer.POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in SentimentAnalyzer.NEGATIVE_WORDS)
        power_words_count = sum(1 for word in words if word in SentimentAnalyzer.POWER_WORDS)
        
        # Calcular score (-1 a 1)
        sentiment_score = (positive_count - negative_count) / max(total_words, 1)
        
        # Determinar sentimiento
        if sentiment_score > 0.1:
            sentiment = 'positive'
        elif sentiment_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': round(sentiment_score, 3),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'power_words_count': power_words_count,
            'power_words_density': round(power_words_count / total_words * 100, 2) if total_words > 0 else 0
        }
    
    @staticmethod
    def detect_tone(text: str) -> str:
        """
        Detecta el tono general del texto.
        
        Args:
            text: Texto a analizar
        
        Returns:
            Tono detectado
        """
        text_lower = text.lower()
        
        # Indicadores de tono
        professional_indicators = ['certificado', 'garantizado', 'verificado', 'estándar', 'certified', 'guaranteed']
        emotional_indicators = ['imagina', 'siente', 'experimenta', 'disfruta', 'imagine', 'feel', 'experience', 'enjoy']
        technical_indicators = ['especificación', 'técnico', 'medida', 'dimensión', 'specification', 'technical', 'measure']
        friendly_indicators = ['tú', 'tu', 'nosotros', 'juntos', 'you', 'your', 'we', 'together']
        
        professional_score = sum(1 for ind in professional_indicators if ind in text_lower)
        emotional_score = sum(1 for ind in emotional_indicators if ind in text_lower)
        technical_score = sum(1 for ind in technical_indicators if ind in text_lower)
        friendly_score = sum(1 for ind in friendly_indicators if ind in text_lower)
        
        scores = {
            'professional': professional_score,
            'emotional': emotional_score,
            'technical': technical_score,
            'friendly': friendly_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'neutral'
        
        return max(scores, key=scores.get)


class ReadabilityAnalyzer:
    """Analizador de legibilidad del texto."""
    
    @staticmethod
    def calculate_flesch_reading_ease(text: str, language: str = 'es') -> Dict:
        """
        Calcula el índice de legibilidad Flesch.
        
        Args:
            text: Texto a analizar
            language: Idioma del texto
        
        Returns:
            Dict con métricas de legibilidad
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text)
        syllables = ReadabilityAnalyzer._count_syllables(text, language)
        
        if len(sentences) == 0 or len(words) == 0:
            return {
                'flesch_score': 0,
                'readability_level': 'unknown',
                'sentence_count': 0,
                'word_count': 0,
                'avg_sentence_length': 0,
                'avg_syllables_per_word': 0
            }
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words) if len(words) > 0 else 0
        
        # Fórmula Flesch (adaptada para español)
        if language == 'es':
            flesch_score = 206.84 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        else:  # inglés
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Nivel de legibilidad
        if flesch_score >= 80:
            level = 'very_easy'
        elif flesch_score >= 70:
            level = 'easy'
        elif flesch_score >= 60:
            level = 'fairly_easy'
        elif flesch_score >= 50:
            level = 'standard'
        elif flesch_score >= 30:
            level = 'fairly_difficult'
        else:
            level = 'difficult'
        
        return {
            'flesch_score': round(flesch_score, 2),
            'readability_level': level,
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2)
        }
    
    @staticmethod
    def _count_syllables(text: str, language: str = 'es') -> int:
        """
        Cuenta las sílabas en el texto (aproximación).
        
        Args:
            text: Texto a analizar
            language: Idioma
        
        Returns:
            Número aproximado de sílabas
        """
        words = re.findall(r'\b\w+\b', text.lower())
        total_syllables = 0
        
        for word in words:
            if language == 'es':
                # Aproximación para español: contar vocales
                vowels = len(re.findall(r'[aeiouáéíóúü]', word))
                if vowels == 0:
                    vowels = 1
                total_syllables += vowels
            else:  # inglés
                # Aproximación para inglés
                vowels = len(re.findall(r'[aeiouy]', word))
                if vowels == 0:
                    vowels = 1
                total_syllables += vowels
        
        return total_syllables


class QualityScorer:
    """Sistema de scoring de calidad para descripciones."""
    
    @staticmethod
    def calculate_quality_score(description_data: Dict) -> Dict:
        """
        Calcula un score de calidad general (0-100) para la descripción.
        
        Args:
            description_data: Dict con datos de la descripción
        
        Returns:
            Dict con score y desglose
        """
        description = description_data.get('description', '')
        word_count = description_data.get('word_count', 0)
        seo_analysis = description_data.get('seo_analysis', {})
        
        scores = {}
        
        # Score de longitud (0-20 puntos)
        if 200 <= word_count <= 400:
            scores['length'] = 20
        elif 150 <= word_count < 200 or 400 < word_count <= 500:
            scores['length'] = 15
        elif 100 <= word_count < 150 or 500 < word_count <= 600:
            scores['length'] = 10
        else:
            scores['length'] = 5
        
        # Score SEO (0-25 puntos)
        seo_score = seo_analysis.get('score', 0)
        scores['seo'] = min(25, seo_score * 0.25)
        
        # Score de sentimiento (0-15 puntos)
        sentiment_analysis = SentimentAnalyzer.analyze_sentiment(description)
        if sentiment_analysis['sentiment'] == 'positive':
            scores['sentiment'] = 15
        elif sentiment_analysis['sentiment'] == 'neutral':
            scores['sentiment'] = 10
        else:
            scores['sentiment'] = 5
        
        # Score de palabras de poder (0-15 puntos)
        power_words_density = sentiment_analysis.get('power_words_density', 0)
        scores['power_words'] = min(15, power_words_density * 0.5)
        
        # Score de legibilidad (0-15 puntos)
        readability = ReadabilityAnalyzer.calculate_flesch_reading_ease(description)
        flesch_score = readability.get('flesch_score', 0)
        if flesch_score >= 60:
            scores['readability'] = 15
        elif flesch_score >= 50:
            scores['readability'] = 12
        elif flesch_score >= 40:
            scores['readability'] = 8
        else:
            scores['readability'] = 5
        
        # Score de estructura (0-10 puntos)
        structure_score = QualityScorer._analyze_structure(description)
        scores['structure'] = structure_score
        
        # Calcular score total
        total_score = sum(scores.values())
        
        # Determinar nivel de calidad
        if total_score >= 85:
            quality_level = 'excellent'
        elif total_score >= 70:
            quality_level = 'good'
        elif total_score >= 55:
            quality_level = 'fair'
        else:
            quality_level = 'needs_improvement'
        
        return {
            'total_score': round(total_score, 1),
            'quality_level': quality_level,
            'breakdown': scores,
            'recommendations': QualityScorer._generate_quality_recommendations(scores, description_data)
        }
    
    @staticmethod
    def _analyze_structure(description: str) -> float:
        """
        Analiza la estructura de la descripción.
        
        Args:
            description: Texto de la descripción
        
        Returns:
            Score de estructura (0-10)
        """
        score = 0
        
        # Tiene párrafos o bullets
        if '\n\n' in description or '\n•' in description or '\n-' in description:
            score += 3
        
        # Tiene al menos 3 párrafos o bullets
        paragraphs = [p for p in description.split('\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 3
        
        # Tiene título o encabezado
        if description[0].isupper() or description.startswith('#'):
            score += 2
        
        # Longitud de párrafos variada (no todos muy cortos o muy largos)
        para_lengths = [len(p.split()) for p in paragraphs if p.strip()]
        if para_lengths:
            avg_length = sum(para_lengths) / len(para_lengths)
            if 20 <= avg_length <= 80:
                score += 2
        
        return min(10, score)
    
    @staticmethod
    def _generate_quality_recommendations(scores: Dict, description_data: Dict) -> List[str]:
        """
        Genera recomendaciones para mejorar la calidad.
        
        Args:
            scores: Dict con scores por categoría
            description_data: Datos completos de la descripción
        
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        if scores.get('length', 0) < 15:
            recommendations.append('Ajusta la longitud a 200-400 palabras para mejor conversión')
        
        if scores.get('seo', 0) < 15:
            recommendations.append('Mejora la optimización SEO incluyendo más keywords relevantes')
        
        if scores.get('sentiment', 0) < 12:
            recommendations.append('Aumenta el uso de palabras positivas y motivadoras')
        
        if scores.get('power_words', 0) < 10:
            recommendations.append('Incluye más palabras de poder (garantizado, comprobado, exclusivo)')
        
        if scores.get('readability', 0) < 12:
            recommendations.append('Simplifica el lenguaje para mejorar la legibilidad')
        
        if scores.get('structure', 0) < 7:
            recommendations.append('Mejora la estructura con párrafos claros y bullets cuando sea apropiado')
        
        return recommendations


class ProductDescriptionAnalyzer:
    """Analizador completo de descripciones de productos."""
    
    @staticmethod
    def analyze_complete(description_data: Dict) -> Dict:
        """
        Realiza un análisis completo de la descripción.
        
        Args:
            description_data: Dict con datos de la descripción
        
        Returns:
            Dict con análisis completo
        """
        description = description_data.get('description', '')
        
        # Análisis de sentimiento
        sentiment = SentimentAnalyzer.analyze_sentiment(description)
        
        # Análisis de tono
        tone = SentimentAnalyzer.detect_tone(description)
        
        # Análisis de legibilidad
        readability = ReadabilityAnalyzer.calculate_flesch_reading_ease(
            description,
            description_data.get('language', 'es')
        )
        
        # Score de calidad
        quality = QualityScorer.calculate_quality_score(description_data)
        
        return {
            'sentiment_analysis': sentiment,
            'tone': tone,
            'readability': readability,
            'quality_score': quality,
            'summary': {
                'overall_quality': quality['quality_level'],
                'total_score': quality['total_score'],
                'sentiment': sentiment['sentiment'],
                'readability_level': readability['readability_level']
            }
        }






