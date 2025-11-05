#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Análisis de Sentimientos Avanzado para Campañas de Marketing con IA
==============================================================================
Análisis de sentimientos en tiempo real para optimizar campañas de marketing.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class AdvancedSentimentAnalyzer:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el analizador de sentimientos avanzado"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Diccionarios de sentimientos en español
        self.positive_words = {
            'excelente', 'bueno', 'genial', 'fantástico', 'increíble', 'maravilloso',
            'perfecto', 'súper', 'increíble', 'asombroso', 'brillante', 'magnífico',
            'satisfecho', 'contento', 'feliz', 'emocionado', 'impresionado', 'recomiendo',
            'recomendado', 'útil', 'eficaz', 'efectivo', 'valioso', 'precioso',
            'increíble', 'sorprendente', 'extraordinario', 'excepcional', 'sobresaliente'
        }
        
        self.negative_words = {
            'malo', 'terrible', 'horrible', 'pésimo', 'decepcionante', 'frustrante',
            'molesto', 'irritante', 'inútil', 'basura', 'desastre', 'catástrofe',
            'odio', 'detesto', 'aburrido', 'monótono', 'lento', 'ineficaz',
            'inútil', 'desperdicio', 'estafa', 'fraude', 'engaño', 'mentira',
            'problema', 'error', 'fallo', 'defecto', 'falla', 'avería'
        }
        
        self.neutral_words = {
            'normal', 'regular', 'aceptable', 'promedio', 'estándar', 'típico',
            'común', 'habitual', 'usual', 'convencional', 'básico', 'simple'
        }
        
        # Palabras de intensidad
        self.intensity_words = {
            'muy': 2.0, 'extremadamente': 3.0, 'súper': 2.5, 'súper': 2.5,
            'increíblemente': 3.0, 'totalmente': 2.0, 'completamente': 2.0,
            'absolutamente': 2.5, 'realmente': 1.5, 'bastante': 1.5,
            'algo': 0.5, 'poco': 0.3, 'nada': 0.1, 'nunca': 0.1
        }
        
        # Palabras de negación
        self.negation_words = {'no', 'nunca', 'jamás', 'tampoco', 'nadie', 'nada', 'ningún'}
        
        # Contextos específicos de marketing
        self.marketing_contexts = {
            'conversion': ['comprar', 'adquirir', 'contratar', 'solicitar', 'registrar'],
            'engagement': ['compartir', 'like', 'comentar', 'seguir', 'interactuar'],
            'satisfaction': ['satisfecho', 'contento', 'feliz', 'recomendar', 'volver'],
            'complaint': ['queja', 'reclamo', 'problema', 'error', 'fallo']
        }
    
    def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analiza el sentimiento de un texto"""
        if not text or not isinstance(text, str):
            return {"error": "Texto inválido para análisis"}
        
        # Preprocesar texto
        processed_text = self._preprocess_text(text)
        
        # Análisis básico de sentimientos
        basic_sentiment = self._analyze_basic_sentiment(processed_text)
        
        # Análisis de intensidad
        intensity = self._analyze_intensity(processed_text)
        
        # Análisis contextual de marketing
        marketing_context = self._analyze_marketing_context(processed_text)
        
        # Análisis de emociones específicas
        emotions = self._analyze_emotions(processed_text)
        
        # Score compuesto
        composite_score = self._calculate_composite_score(
            basic_sentiment, intensity, marketing_context, emotions
        )
        
        return {
            'text': text,
            'processed_text': processed_text,
            'basic_sentiment': basic_sentiment,
            'intensity': intensity,
            'marketing_context': marketing_context,
            'emotions': emotions,
            'composite_score': composite_score,
            'sentiment_label': self._get_sentiment_label(composite_score),
            'confidence': self._calculate_confidence(basic_sentiment, intensity),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocesa el texto para análisis"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales pero mantener acentos
        text = re.sub(r'[^\w\sáéíóúüñ]', ' ', text)
        
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Remover espacios al inicio y final
        text = text.strip()
        
        return text
    
    def _analyze_basic_sentiment(self, text: str) -> Dict[str, Any]:
        """Analiza el sentimiento básico del texto"""
        words = text.split()
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for word in words:
            if word in self.positive_words:
                positive_count += 1
            elif word in self.negative_words:
                negative_count += 1
            elif word in self.neutral_words:
                neutral_count += 1
        
        total_words = len(words)
        
        if total_words == 0:
            return {
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0,
                'sentiment_score': 0
            }
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        neutral_ratio = neutral_count / total_words
        
        # Aplicar lógica de negación
        sentiment_score = self._apply_negation_logic(words, positive_ratio, negative_ratio)
        
        return {
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'neutral_ratio': neutral_ratio,
            'sentiment_score': sentiment_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count
        }
    
    def _apply_negation_logic(self, words: List[str], positive_ratio: float, negative_ratio: float) -> float:
        """Aplica lógica de negación para ajustar el score de sentimiento"""
        score = positive_ratio - negative_ratio
        
        # Buscar patrones de negación
        for i, word in enumerate(words):
            if word in self.negation_words:
                # Verificar si la siguiente palabra es positiva o negativa
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word in self.positive_words:
                        score -= 0.2  # Negación de palabra positiva
                    elif next_word in self.negative_words:
                        score += 0.2  # Negación de palabra negativa
        
        return max(-1, min(1, score))  # Normalizar entre -1 y 1
    
    def _analyze_intensity(self, text: str) -> Dict[str, Any]:
        """Analiza la intensidad del sentimiento"""
        words = text.split()
        intensity_score = 1.0
        intensity_words_found = []
        
        for word in words:
            if word in self.intensity_words:
                intensity_score *= self.intensity_words[word]
                intensity_words_found.append(word)
        
        # Normalizar intensidad
        intensity_score = min(3.0, max(0.1, intensity_score))
        
        return {
            'intensity_score': intensity_score,
            'intensity_words': intensity_words_found,
            'intensity_level': self._get_intensity_level(intensity_score)
        }
    
    def _get_intensity_level(self, intensity_score: float) -> str:
        """Obtiene el nivel de intensidad"""
        if intensity_score >= 2.5:
            return 'muy_alto'
        elif intensity_score >= 2.0:
            return 'alto'
        elif intensity_score >= 1.5:
            return 'medio'
        elif intensity_score >= 1.0:
            return 'bajo'
        else:
            return 'muy_bajo'
    
    def _analyze_marketing_context(self, text: str) -> Dict[str, Any]:
        """Analiza el contexto específico de marketing"""
        words = text.split()
        context_scores = {}
        
        for context, keywords in self.marketing_contexts.items():
            score = 0
            for keyword in keywords:
                if keyword in words:
                    score += 1
            context_scores[context] = score
        
        # Determinar contexto dominante
        dominant_context = max(context_scores.keys(), key=lambda x: context_scores[x])
        
        return {
            'context_scores': context_scores,
            'dominant_context': dominant_context,
            'marketing_relevance': sum(context_scores.values()) / len(words) if words else 0
        }
    
    def _analyze_emotions(self, text: str) -> Dict[str, Any]:
        """Analiza emociones específicas en el texto"""
        # Diccionarios de emociones
        emotion_words = {
            'alegria': ['feliz', 'contento', 'alegre', 'gozoso', 'eufórico', 'emocionado'],
            'tristeza': ['triste', 'deprimido', 'melancólico', 'afligido', 'desanimado'],
            'ira': ['enojado', 'furioso', 'molesto', 'irritado', 'indignado', 'rabioso'],
            'miedo': ['asustado', 'aterrorizado', 'nervioso', 'ansioso', 'preocupado'],
            'sorpresa': ['sorprendido', 'asombrado', 'impresionado', 'desconcertado'],
            'disgusto': ['disgustado', 'repugnado', 'asqueado', 'ofendido']
        }
        
        words = text.split()
        emotion_scores = {}
        
        for emotion, keywords in emotion_words.items():
            score = 0
            for keyword in keywords:
                if keyword in words:
                    score += 1
            emotion_scores[emotion] = score
        
        # Determinar emoción dominante
        dominant_emotion = max(emotion_scores.keys(), key=lambda x: emotion_scores[x]) if any(emotion_scores.values()) else 'neutral'
        
        return {
            'emotion_scores': emotion_scores,
            'dominant_emotion': dominant_emotion,
            'emotional_intensity': max(emotion_scores.values()) if emotion_scores else 0
        }
    
    def _calculate_composite_score(self, basic_sentiment: Dict, intensity: Dict, 
                                 marketing_context: Dict, emotions: Dict) -> float:
        """Calcula un score compuesto de sentimiento"""
        # Score base
        base_score = basic_sentiment['sentiment_score']
        
        # Ajustar por intensidad
        intensity_adjusted = base_score * intensity['intensity_score']
        
        # Ajustar por contexto de marketing
        marketing_multiplier = 1.0 + (marketing_context['marketing_relevance'] * 0.5)
        context_adjusted = intensity_adjusted * marketing_multiplier
        
        # Ajustar por emociones
        emotion_adjustment = 0
        if emotions['dominant_emotion'] in ['alegria', 'sorpresa']:
            emotion_adjustment = 0.1
        elif emotions['dominant_emotion'] in ['ira', 'disgusto']:
            emotion_adjustment = -0.1
        
        final_score = context_adjusted + emotion_adjustment
        
        return max(-1, min(1, final_score))  # Normalizar entre -1 y 1
    
    def _get_sentiment_label(self, composite_score: float) -> str:
        """Obtiene la etiqueta de sentimiento"""
        if composite_score >= 0.6:
            return 'muy_positivo'
        elif composite_score >= 0.2:
            return 'positivo'
        elif composite_score >= -0.2:
            return 'neutral'
        elif composite_score >= -0.6:
            return 'negativo'
        else:
            return 'muy_negativo'
    
    def _calculate_confidence(self, basic_sentiment: Dict, intensity: Dict) -> float:
        """Calcula la confianza del análisis"""
        # Confianza basada en la diferencia entre sentimientos
        sentiment_diff = abs(basic_sentiment['positive_ratio'] - basic_sentiment['negative_ratio'])
        
        # Confianza basada en la intensidad
        intensity_confidence = min(1.0, intensity['intensity_score'] / 2.0)
        
        # Confianza combinada
        confidence = (sentiment_diff + intensity_confidence) / 2
        
        return max(0.1, min(1.0, confidence))
    
    def analyze_campaign_sentiment(self, campaign_id: int, 
                                 feedback_data: List[Dict] = None) -> Dict[str, Any]:
        """Analiza el sentimiento de una campaña específica"""
        campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
        if not campaign:
            return {"error": f"Campaña {campaign_id} no encontrada"}
        
        # Generar datos de feedback simulados si no se proporcionan
        if feedback_data is None:
            feedback_data = self._generate_simulated_feedback(campaign)
        
        # Analizar cada feedback
        sentiment_analyses = []
        for feedback in feedback_data:
            analysis = self.analyze_text_sentiment(feedback['text'])
            sentiment_analyses.append({
                'feedback_id': feedback['id'],
                'source': feedback['source'],
                'analysis': analysis
            })
        
        # Análisis agregado
        aggregate_analysis = self._calculate_aggregate_sentiment(sentiment_analyses)
        
        # Recomendaciones basadas en sentimiento
        recommendations = self._generate_sentiment_recommendations(
            campaign, aggregate_analysis, sentiment_analyses
        )
        
        return {
            'campaign_id': campaign_id,
            'campaign_name': campaign['name'],
            'total_feedback': len(feedback_data),
            'sentiment_analyses': sentiment_analyses,
            'aggregate_analysis': aggregate_analysis,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _generate_simulated_feedback(self, campaign: Dict) -> List[Dict]:
        """Genera feedback simulado para una campaña"""
        # Feedback positivo
        positive_feedback = [
            "Excelente campaña, muy efectiva para mi negocio",
            "Me encanta cómo funciona esta herramienta de marketing",
            "Increíble ROI, superó mis expectativas",
            "Muy recomendado, funciona perfectamente",
            "Fantástico servicio, muy satisfecho"
        ]
        
        # Feedback negativo
        negative_feedback = [
            "No funcionó como esperaba, muy decepcionante",
            "Problemas técnicos constantes, no lo recomiendo",
            "Muy caro para lo que ofrece, no vale la pena",
            "Interfaz confusa y difícil de usar",
            "Soporte al cliente terrible, muy frustrante"
        ]
        
        # Feedback neutral
        neutral_feedback = [
            "Funciona bien, nada especial",
            "Aceptable, cumple su función básica",
            "Normal, esperaba algo más",
            "Regular, podría ser mejor",
            "Está bien, pero hay mejores opciones"
        ]
        
        # Combinar feedback
        all_feedback = positive_feedback + negative_feedback + neutral_feedback
        
        feedback_data = []
        for i, text in enumerate(all_feedback):
            feedback_data.append({
                'id': i + 1,
                'text': text,
                'source': 'simulated',
                'timestamp': datetime.now().isoformat()
            })
        
        return feedback_data
    
    def _calculate_aggregate_sentiment(self, sentiment_analyses: List[Dict]) -> Dict[str, Any]:
        """Calcula el sentimiento agregado de múltiples análisis"""
        if not sentiment_analyses:
            return {"error": "No hay análisis de sentimiento disponibles"}
        
        # Extraer scores
        scores = [analysis['analysis']['composite_score'] for analysis in sentiment_analyses]
        confidences = [analysis['analysis']['confidence'] for analysis in sentiment_analyses]
        labels = [analysis['analysis']['sentiment_label'] for analysis in sentiment_analyses]
        
        # Estadísticas básicas
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        mean_confidence = np.mean(confidences)
        
        # Distribución de etiquetas
        label_counts = Counter(labels)
        total_analyses = len(sentiment_analyses)
        
        # Distribución porcentual
        label_distribution = {label: (count / total_analyses) * 100 for label, count in label_counts.items()}
        
        # Determinar sentimiento dominante
        dominant_sentiment = max(label_counts.keys(), key=lambda x: label_counts[x])
        
        return {
            'mean_score': mean_score,
            'std_score': std_score,
            'mean_confidence': mean_confidence,
            'label_distribution': label_distribution,
            'dominant_sentiment': dominant_sentiment,
            'total_analyses': total_analyses,
            'sentiment_trend': self._calculate_sentiment_trend(scores)
        }
    
    def _calculate_sentiment_trend(self, scores: List[float]) -> str:
        """Calcula la tendencia del sentimiento"""
        if len(scores) < 2:
            return 'insufficient_data'
        
        # Dividir en dos mitades
        mid = len(scores) // 2
        first_half = scores[:mid]
        second_half = scores[mid:]
        
        first_mean = np.mean(first_half)
        second_mean = np.mean(second_half)
        
        if second_mean > first_mean + 0.1:
            return 'improving'
        elif second_mean < first_mean - 0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_sentiment_recommendations(self, campaign: Dict, 
                                          aggregate_analysis: Dict, 
                                          sentiment_analyses: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en el análisis de sentimiento"""
        recommendations = []
        
        mean_score = aggregate_analysis['mean_score']
        dominant_sentiment = aggregate_analysis['dominant_sentiment']
        trend = aggregate_analysis['sentiment_trend']
        
        # Recomendaciones basadas en score promedio
        if mean_score >= 0.6:
            recommendations.append("🎉 **Sentimiento muy positivo**: Mantener estrategia actual y escalar")
        elif mean_score >= 0.2:
            recommendations.append("👍 **Sentimiento positivo**: Continuar con optimizaciones menores")
        elif mean_score >= -0.2:
            recommendations.append("😐 **Sentimiento neutral**: Implementar mejoras para aumentar satisfacción")
        elif mean_score >= -0.6:
            recommendations.append("😞 **Sentimiento negativo**: Revisar estrategia y hacer ajustes significativos")
        else:
            recommendations.append("😡 **Sentimiento muy negativo**: Revisión urgente y cambios drásticos necesarios")
        
        # Recomendaciones basadas en tendencia
        if trend == 'improving':
            recommendations.append("📈 **Tendencia positiva**: Continuar con las mejoras implementadas")
        elif trend == 'declining':
            recommendations.append("📉 **Tendencia negativa**: Investigar causas del deterioro")
        else:
            recommendations.append("📊 **Tendencia estable**: Mantener monitoreo y buscar oportunidades de mejora")
        
        # Recomendaciones específicas por categoría de campaña
        category = campaign['category']
        if category == 'Personalización con IA' and mean_score < 0.3:
            recommendations.append("🤖 **Mejorar personalización**: Revisar algoritmos de IA y datos de entrada")
        elif category == 'Chatbots y Asistentes Virtuales' and mean_score < 0.3:
            recommendations.append("💬 **Mejorar chatbots**: Optimizar respuestas y flujo de conversación")
        elif category == 'Generación de Contenido' and mean_score < 0.3:
            recommendations.append("📝 **Mejorar contenido**: Revisar calidad y relevancia del contenido generado")
        
        # Recomendaciones basadas en confianza
        mean_confidence = aggregate_analysis['mean_confidence']
        if mean_confidence < 0.6:
            recommendations.append("🔍 **Baja confianza en análisis**: Recopilar más datos de feedback")
        
        return recommendations
    
    def monitor_sentiment_trends(self, campaign_ids: List[int], 
                               time_period_days: int = 30) -> Dict[str, Any]:
        """Monitorea tendencias de sentimiento en múltiples campañas"""
        trend_analysis = {
            'total_campaigns': len(campaign_ids),
            'time_period_days': time_period_days,
            'campaign_trends': [],
            'overall_trend': 'stable',
            'recommendations': []
        }
        
        all_scores = []
        
        for campaign_id in campaign_ids:
            campaign_analysis = self.analyze_campaign_sentiment(campaign_id)
            
            if 'error' not in campaign_analysis:
                aggregate = campaign_analysis['aggregate_analysis']
                all_scores.append(aggregate['mean_score'])
                
                trend_analysis['campaign_trends'].append({
                    'campaign_id': campaign_id,
                    'campaign_name': campaign_analysis['campaign_name'],
                    'mean_score': aggregate['mean_score'],
                    'dominant_sentiment': aggregate['dominant_sentiment'],
                    'trend': aggregate['sentiment_trend']
                })
        
        # Análisis general
        if all_scores:
            overall_mean = np.mean(all_scores)
            overall_std = np.std(all_scores)
            
            # Determinar tendencia general
            if overall_mean >= 0.3:
                trend_analysis['overall_trend'] = 'positive'
            elif overall_mean <= -0.3:
                trend_analysis['overall_trend'] = 'negative'
            else:
                trend_analysis['overall_trend'] = 'neutral'
            
            # Generar recomendaciones generales
            if overall_mean >= 0.5:
                trend_analysis['recommendations'].append("🎯 **Excelente sentimiento general**: Mantener estrategia y escalar")
            elif overall_mean >= 0.0:
                trend_analysis['recommendations'].append("👍 **Sentimiento positivo**: Continuar con optimizaciones")
            elif overall_mean >= -0.5:
                trend_analysis['recommendations'].append("⚠️ **Sentimiento mixto**: Revisar campañas problemáticas")
            else:
                trend_analysis['recommendations'].append("🚨 **Sentimiento negativo**: Revisión urgente de estrategia")
        
        return trend_analysis

def main():
    """Función principal de demostración"""
    print("=== SISTEMA DE ANÁLISIS DE SENTIMIENTOS AVANZADO ===")
    
    # Inicializar analizador
    analyzer = AdvancedSentimentAnalyzer()
    
    # Analizar texto individual
    print("Analizando texto individual...")
    sample_texts = [
        "Excelente campaña, muy efectiva y me encanta cómo funciona",
        "No me gustó nada, fue una pérdida de tiempo total",
        "Está bien, cumple su función pero nada especial",
        "Increíblemente decepcionante, no funciona como prometieron",
        "Fantástico servicio, superó todas mis expectativas"
    ]
    
    for text in sample_texts:
        analysis = analyzer.analyze_text_sentiment(text)
        print(f"\n📝 Texto: '{text}'")
        print(f"Sentimiento: {analysis['sentiment_label']} (Score: {analysis['composite_score']:.2f})")
        print(f"Confianza: {analysis['confidence']:.2f}")
        print(f"Intensidad: {analysis['intensity']['intensity_level']}")
        print(f"Emoción dominante: {analysis['emotions']['dominant_emotion']}")
    
    # Analizar campaña específica
    print(f"\n🔄 ANALIZANDO CAMPAÑA ESPECÍFICA...")
    campaign_analysis = analyzer.analyze_campaign_sentiment(1)
    
    if 'error' not in campaign_analysis:
        print(f"Campaña: {campaign_analysis['campaign_name']}")
        print(f"Total de feedback: {campaign_analysis['total_feedback']}")
        
        aggregate = campaign_analysis['aggregate_analysis']
        print(f"Score promedio: {aggregate['mean_score']:.2f}")
        print(f"Sentimiento dominante: {aggregate['dominant_sentiment']}")
        print(f"Tendencia: {aggregate['sentiment_trend']}")
        
        print(f"\n💡 RECOMENDACIONES")
        for recommendation in campaign_analysis['recommendations']:
            print(f"• {recommendation}")
    
    # Monitorear tendencias
    print(f"\n📊 MONITOREANDO TENDENCIAS...")
    trend_analysis = analyzer.monitor_sentiment_trends([1, 2, 3, 4, 5])
    
    print(f"Total de campañas: {trend_analysis['total_campaigns']}")
    print(f"Tendencia general: {trend_analysis['overall_trend']}")
    
    print(f"\n💡 RECOMENDACIONES DE TENDENCIAS")
    for recommendation in trend_analysis['recommendations']:
        print(f"• {recommendation}")
    
    print(f"\n✅ Sistema de análisis de sentimientos configurado y funcionando")

if __name__ == "__main__":
    main()
