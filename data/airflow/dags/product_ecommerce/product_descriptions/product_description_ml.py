"""
Sistema de Machine Learning para mejorar descripciones basado en métricas reales.

Incluye:
- Aprendizaje de descripciones de alto rendimiento
- Predicción de conversión
- Optimización automática basada en datos históricos
- Análisis de patrones exitosos
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class DescriptionMLOptimizer:
    """Optimizador ML para descripciones basadas en datos históricos."""
    
    def __init__(self):
        self.success_patterns = defaultdict(list)
        self.conversion_data = []
        self.feature_weights = {}
    
    def learn_from_success(self, description_data: Dict, metrics: Dict):
        """
        Aprende de descripciones exitosas.
        
        Args:
            description_data: Datos de la descripción
            metrics: Métricas de rendimiento (views, clicks, conversions, revenue)
        """
        conversion_rate = metrics.get('conversion_rate', 0)
        if conversion_rate > 0.05:  # >5% conversión es exitoso
            # Extraer características exitosas
            features = self._extract_features(description_data)
            self.success_patterns['high_performance'].append({
                'features': features,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Aprendido de descripción exitosa: {conversion_rate:.2%}")
    
    def predict_conversion(self, description_data: Dict) -> Dict:
        """
        Predice el potencial de conversión basado en patrones aprendidos.
        
        Args:
            description_data: Datos de la descripción a predecir
        
        Returns:
            Dict con predicción y confianza
        """
        if not self.success_patterns.get('high_performance'):
            return {
                'predicted_conversion': 0.03,  # Default
                'confidence': 0.0,
                'message': 'No hay suficientes datos históricos'
            }
        
        features = self._extract_features(description_data)
        
        # Comparar con patrones exitosos
        similarities = []
        for pattern in self.success_patterns['high_performance'][-50:]:  # Últimos 50
            similarity = self._calculate_similarity(features, pattern['features'])
            conversion = pattern['metrics'].get('conversion_rate', 0)
            similarities.append((similarity, conversion))
        
        if similarities:
            # Promedio ponderado por similitud
            total_weight = sum(sim for sim, _ in similarities)
            if total_weight > 0:
                predicted = sum(sim * conv for sim, conv in similarities) / total_weight
                confidence = min(1.0, total_weight / len(similarities))
            else:
                predicted = 0.03
                confidence = 0.0
        else:
            predicted = 0.03
            confidence = 0.0
        
        return {
            'predicted_conversion': round(predicted, 4),
            'confidence': round(confidence, 2),
            'based_on_samples': len(similarities)
        }
    
    def suggest_improvements(self, description_data: Dict, target_conversion: float = 0.05) -> List[str]:
        """
        Sugiere mejoras basadas en patrones exitosos.
        
        Args:
            description_data: Datos de la descripción
            target_conversion: Tasa de conversión objetivo
        
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        if not self.success_patterns.get('high_performance'):
            return suggestions
        
        features = self._extract_features(description_data)
        
        # Analizar diferencias con descripciones exitosas
        successful_features = []
        for pattern in self.success_patterns['high_performance'][-20:]:
            if pattern['metrics'].get('conversion_rate', 0) >= target_conversion:
                successful_features.append(pattern['features'])
        
        if not successful_features:
            return suggestions
        
        # Comparar características
        avg_successful = self._average_features(successful_features)
        
        # Sugerencias basadas en diferencias
        if features.get('word_count', 0) < avg_successful.get('word_count', 300) * 0.9:
            suggestions.append(f"Aumenta la longitud a ~{int(avg_successful.get('word_count', 300))} palabras")
        
        if features.get('power_words_count', 0) < avg_successful.get('power_words_count', 5):
            suggestions.append("Incluye más palabras de poder (garantizado, comprobado, exclusivo)")
        
        if features.get('bullets_count', 0) < avg_successful.get('bullets_count', 3):
            suggestions.append("Agrega más bullets destacando beneficios clave")
        
        if features.get('seo_keywords_count', 0) < avg_successful.get('seo_keywords_count', 5):
            suggestions.append("Incluye más keywords SEO relevantes")
        
        return suggestions
    
    def _extract_features(self, description_data: Dict) -> Dict:
        """Extrae características de una descripción."""
        description = description_data.get('description', '')
        
        return {
            'word_count': description_data.get('word_count', 0),
            'seo_score': description_data.get('seo_analysis', {}).get('score', 0),
            'seo_keywords_count': len(description_data.get('seo_keywords', [])),
            'bullets_count': description.count('•') + description.count('-'),
            'power_words_count': sum(1 for word in ['garantizado', 'comprobado', 'exclusivo', 'premium'] if word in description.lower()),
            'has_cta': bool('compra' in description.lower() or 'buy' in description.lower()),
            'has_numbers': bool(any(char.isdigit() for char in description)),
            'platform': description_data.get('platform', 'generic')
        }
    
    def _calculate_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calcula similitud entre dos conjuntos de características."""
        # Similitud basada en características clave
        similarities = []
        
        # Word count (normalizado)
        wc1, wc2 = features1.get('word_count', 0), features2.get('word_count', 0)
        if max(wc1, wc2) > 0:
            wc_sim = 1 - abs(wc1 - wc2) / max(wc1, wc2)
            similarities.append(wc_sim * 0.2)
        
        # SEO score
        seo1, seo2 = features1.get('seo_score', 0), features2.get('seo_score', 0)
        if max(seo1, seo2) > 0:
            seo_sim = 1 - abs(seo1 - seo2) / max(seo1, seo2)
            similarities.append(seo_sim * 0.3)
        
        # Keywords count
        kw1, kw2 = features1.get('seo_keywords_count', 0), features2.get('seo_keywords_count', 0)
        if max(kw1, kw2) > 0:
            kw_sim = 1 - abs(kw1 - kw2) / max(kw1, kw2)
            similarities.append(kw_sim * 0.2)
        
        # Bullets count
        bullets1, bullets2 = features1.get('bullets_count', 0), features2.get('bullets_count', 0)
        if max(bullets1, bullets2) > 0:
            bullets_sim = 1 - abs(bullets1 - bullets2) / max(bullets1, bullets2)
            similarities.append(bullets_sim * 0.15)
        
        # Power words
        pw1, pw2 = features1.get('power_words_count', 0), features2.get('power_words_count', 0)
        if max(pw1, pw2) > 0:
            pw_sim = 1 - abs(pw1 - pw2) / max(pw1, pw2)
            similarities.append(pw_sim * 0.15)
        
        return sum(similarities) if similarities else 0.0
    
    def _average_features(self, features_list: List[Dict]) -> Dict:
        """Calcula promedio de características."""
        if not features_list:
            return {}
        
        avg = {}
        for key in features_list[0].keys():
            values = [f.get(key, 0) for f in features_list if isinstance(f.get(key), (int, float))]
            if values:
                avg[key] = sum(values) / len(values)
        
        return avg


class ReviewAnalyzer:
    """Analizador de reviews de clientes para mejorar descripciones."""
    
    @staticmethod
    def extract_insights_from_reviews(reviews: List[Dict]) -> Dict:
        """
        Extrae insights de reviews para mejorar descripciones.
        
        Args:
            reviews: Lista de reviews con 'rating', 'text', 'helpful'
        
        Returns:
            Dict con insights extraídos
        """
        if not reviews:
            return {
                'common_praise': [],
                'common_complaints': [],
                'missing_features': [],
                'suggested_keywords': []
            }
        
        # Separar positivas y negativas
        positive_reviews = [r for r in reviews if r.get('rating', 0) >= 4]
        negative_reviews = [r for r in reviews if r.get('rating', 0) <= 2]
        
        # Extraer palabras/frases comunes
        positive_words = ReviewAnalyzer._extract_common_phrases(positive_reviews)
        negative_words = ReviewAnalyzer._extract_common_phrases(negative_reviews)
        
        # Identificar características mencionadas
        mentioned_features = ReviewAnalyzer._extract_features_mentioned(reviews)
        
        return {
            'common_praise': positive_words[:10],
            'common_complaints': negative_words[:10],
            'missing_features': ReviewAnalyzer._identify_missing_features(negative_reviews),
            'suggested_keywords': positive_words[:15],
            'average_rating': sum(r.get('rating', 0) for r in reviews) / len(reviews) if reviews else 0,
            'total_reviews': len(reviews)
        }
    
    @staticmethod
    def _extract_common_phrases(reviews: List[Dict]) -> List[str]:
        """Extrae frases comunes de reviews."""
        from collections import Counter
        import re
        
        phrases = []
        for review in reviews:
            text = review.get('text', '').lower()
            # Extraer frases de 2-3 palabras
            words = re.findall(r'\b\w+\b', text)
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                if len(phrase) > 5:
                    phrases.append(phrase)
        
        counter = Counter(phrases)
        return [phrase for phrase, count in counter.most_common(20)]
    
    @staticmethod
    def _extract_features_mentioned(reviews: List[Dict]) -> List[str]:
        """Extrae características mencionadas en reviews."""
        feature_keywords = ['calidad', 'durabilidad', 'diseño', 'precio', 'tamaño', 
                          'color', 'material', 'funcionalidad', 'facilidad', 'rendimiento',
                          'quality', 'durability', 'design', 'price', 'size', 'color', 
                          'material', 'functionality', 'ease', 'performance']
        
        mentioned = []
        for review in reviews:
            text = review.get('text', '').lower()
            for keyword in feature_keywords:
                if keyword in text and keyword not in mentioned:
                    mentioned.append(keyword)
        
        return mentioned
    
    @staticmethod
    def _identify_missing_features(negative_reviews: List[Dict]) -> List[str]:
        """Identifica características que faltan según reviews negativas."""
        missing = []
        complaint_patterns = [
            ('falta', 'missing', 'no tiene', "doesn't have"),
            ('debería', 'should', 'sería mejor', 'would be better')
        ]
        
        for review in negative_reviews:
            text = review.get('text', '').lower()
            for pattern_group in complaint_patterns:
                if any(pattern in text for pattern in pattern_group):
                    # Extraer siguiente frase
                    missing.append(text[:100])  # Simplificado
        
        return missing[:5]


class CTAOptimizer:
    """Optimizador de Call-to-Actions para descripciones."""
    
    EFFECTIVE_CTAS = {
        'spanish': [
            'Compra ahora y obtén envío gratis',
            'Ordena hoy y recibe mañana',
            'Aprovecha esta oferta limitada',
            'Únete a miles de clientes satisfechos',
            'No esperes más, compra ahora',
            'Garantía de satisfacción 100%',
            'Oferta por tiempo limitado'
        ],
        'english': [
            'Buy now and get free shipping',
            'Order today, receive tomorrow',
            'Take advantage of this limited offer',
            'Join thousands of satisfied customers',
            "Don't wait, buy now",
            '100% satisfaction guarantee',
            'Limited time offer'
        ]
    }
    
    @staticmethod
    def generate_optimized_cta(context: Dict, language: str = 'es') -> str:
        """
        Genera un CTA optimizado basado en el contexto.
        
        Args:
            context: Contexto del producto (precio, oferta, urgencia, etc.)
            language: Idioma del CTA
        
        Returns:
            CTA optimizado
        """
        ctas = CTAOptimizer.EFFECTIVE_CTAS.get(language, CTAOptimizer.EFFECTIVE_CTAS['spanish'])
        
        # Seleccionar CTA basado en contexto
        if context.get('has_discount'):
            if language == 'es':
                return 'Aprovecha esta oferta limitada'
            else:
                return 'Take advantage of this limited offer'
        
        if context.get('has_free_shipping'):
            if language == 'es':
                return 'Compra ahora y obtén envío gratis'
            else:
                return 'Buy now and get free shipping'
        
        if context.get('has_urgency'):
            if language == 'es':
                return 'No esperes más, compra ahora'
            else:
                return "Don't wait, buy now"
        
        # CTA por defecto
        return ctas[0]
    
    @staticmethod
    def optimize_existing_cta(cta: str, language: str = 'es') -> str:
        """
        Optimiza un CTA existente.
        
        Args:
            cta: CTA actual
            language: Idioma
        
        Returns:
            CTA optimizado
        """
        cta_lower = cta.lower()
        
        # Verificar si ya es efectivo
        effective_ctas = CTAOptimizer.EFFECTIVE_CTAS.get(language, CTAOptimizer.EFFECTIVE_CTAS['spanish'])
        for effective in effective_ctas:
            if effective.lower() in cta_lower or cta_lower in effective.lower():
                return cta  # Ya es efectivo
        
        # Mejorar CTA
        improved = cta
        
        # Agregar urgencia si no tiene
        urgency_words = ['ahora', 'hoy', 'inmediatamente', 'now', 'today', 'immediately']
        if not any(word in cta_lower for word in urgency_words):
            if language == 'es':
                improved = f"{cta} - ¡Compra ahora!"
            else:
                improved = f"{cta} - Buy now!"
        
        # Agregar beneficio si no tiene
        benefit_words = ['gratis', 'descuento', 'oferta', 'free', 'discount', 'offer']
        if not any(word in cta_lower for word in benefit_words):
            # No agregar si ya es muy largo
            if len(improved) < 60:
                if language == 'es':
                    improved = f"{improved} - Envío gratis"
                else:
                    improved = f"{improved} - Free shipping"
        
        return improved






