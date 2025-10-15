#!/usr/bin/env python3
"""
ClickUp Brain - Sistema de Análisis de Sentimientos y Satisfacción del Equipo
============================================================================

Sistema avanzado para analizar sentimientos, satisfacción y bienestar del equipo
basado en comunicaciones, feedback y métricas de comportamiento.
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import Counter, defaultdict
import statistics

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analizador de sentimientos avanzado."""
    
    def __init__(self):
        self.positive_keywords = {
            'excellent', 'great', 'amazing', 'fantastic', 'awesome', 'wonderful',
            'love', 'perfect', 'outstanding', 'brilliant', 'superb', 'marvelous',
            'good', 'nice', 'cool', 'sweet', 'fantastic', 'incredible', 'impressive',
            'satisfied', 'happy', 'pleased', 'delighted', 'thrilled', 'excited',
            'successful', 'achieved', 'completed', 'finished', 'done', 'accomplished',
            'improved', 'better', 'enhanced', 'optimized', 'upgraded', 'progress',
            'teamwork', 'collaboration', 'support', 'helpful', 'cooperative'
        }
        
        self.negative_keywords = {
            'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'dislike',
            'bad', 'worst', 'pathetic', 'useless', 'worthless', 'disappointing',
            'frustrated', 'angry', 'annoyed', 'irritated', 'upset', 'mad',
            'stressed', 'overwhelmed', 'exhausted', 'burned', 'tired', 'drained',
            'failed', 'broken', 'error', 'bug', 'issue', 'problem', 'trouble',
            'delayed', 'late', 'slow', 'blocked', 'stuck', 'impossible',
            'confused', 'lost', 'unclear', 'complicated', 'difficult', 'hard',
            'conflict', 'argument', 'disagreement', 'tension', 'hostile'
        }
        
        self.neutral_keywords = {
            'okay', 'fine', 'alright', 'normal', 'standard', 'regular',
            'average', 'typical', 'usual', 'common', 'basic', 'simple',
            'maybe', 'perhaps', 'possibly', 'might', 'could', 'would',
            'information', 'data', 'update', 'status', 'report', 'summary'
        }
        
        # Palabras de intensidad
        self.intensifiers = {
            'very': 1.5, 'extremely': 2.0, 'incredibly': 2.0, 'absolutely': 1.8,
            'totally': 1.7, 'completely': 1.6, 'really': 1.3, 'quite': 1.2,
            'somewhat': 0.8, 'slightly': 0.7, 'barely': 0.5, 'hardly': 0.4
        }
        
        # Negaciones
        self.negations = {'not', 'no', 'never', 'none', 'nothing', 'nobody', 'nowhere'}
    
    def analyze_text_sentiment(self, text: str) -> Dict:
        """Analizar sentimiento de un texto."""
        try:
            if not text or not isinstance(text, str):
                return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
            
            # Limpiar y tokenizar texto
            cleaned_text = self._clean_text(text)
            words = self._tokenize_text(cleaned_text)
            
            if not words:
                return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
            
            # Calcular sentimiento
            sentiment_score = self._calculate_sentiment_score(words)
            
            # Determinar clasificación
            if sentiment_score > 0.1:
                sentiment = 'positive'
            elif sentiment_score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Calcular confianza
            confidence = self._calculate_confidence(words, sentiment_score)
            
            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'confidence': confidence,
                'word_count': len(words),
                'analysis_details': self._get_analysis_details(words)
            }
            
        except Exception as e:
            logger.error(f"Error analizando sentimiento: {str(e)}")
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
    
    def _clean_text(self, text: str) -> str:
        """Limpiar texto para análisis."""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales pero mantener espacios
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenizar texto en palabras."""
        return text.split()
    
    def _calculate_sentiment_score(self, words: List[str]) -> float:
        """Calcular score de sentimiento."""
        score = 0.0
        word_count = len(words)
        
        for i, word in enumerate(words):
            word_score = 0.0
            
            # Verificar palabra positiva
            if word in self.positive_keywords:
                word_score = 1.0
            # Verificar palabra negativa
            elif word in self.negative_keywords:
                word_score = -1.0
            # Verificar palabra neutral
            elif word in self.neutral_keywords:
                word_score = 0.0
            
            # Aplicar intensificadores
            if i > 0 and words[i-1] in self.intensifiers:
                intensity = self.intensifiers[words[i-1]]
                word_score *= intensity
            
            # Aplicar negaciones
            if i > 0 and words[i-1] in self.negations:
                word_score *= -1.0
            
            score += word_score
        
        # Normalizar score
        if word_count > 0:
            score = score / word_count
        
        return score
    
    def _calculate_confidence(self, words: List[str], sentiment_score: float) -> float:
        """Calcular confianza del análisis."""
        sentiment_words = 0
        total_words = len(words)
        
        for word in words:
            if (word in self.positive_keywords or 
                word in self.negative_keywords or 
                word in self.neutral_keywords):
                sentiment_words += 1
        
        # Confianza basada en proporción de palabras de sentimiento
        word_confidence = sentiment_words / total_words if total_words > 0 else 0
        
        # Confianza basada en magnitud del score
        score_confidence = min(abs(sentiment_score) * 2, 1.0)
        
        # Confianza combinada
        confidence = (word_confidence + score_confidence) / 2
        
        return min(confidence, 1.0)
    
    def _get_analysis_details(self, words: List[str]) -> Dict:
        """Obtener detalles del análisis."""
        positive_words = [w for w in words if w in self.positive_keywords]
        negative_words = [w for w in words if w in self.negative_keywords]
        neutral_words = [w for w in words if w in self.neutral_keywords]
        
        return {
            'positive_words': positive_words,
            'negative_words': negative_words,
            'neutral_words': neutral_words,
            'positive_count': len(positive_words),
            'negative_count': len(negative_words),
            'neutral_count': len(neutral_words)
        }

class TeamSatisfactionAnalyzer:
    """Analizador de satisfacción del equipo."""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.satisfaction_indicators = {
            'workload': ['overwhelmed', 'busy', 'stressed', 'manageable', 'light', 'balanced'],
            'collaboration': ['teamwork', 'support', 'helpful', 'isolated', 'alone', 'collaborative'],
            'recognition': ['appreciated', 'valued', 'recognized', 'ignored', 'overlooked', 'acknowledged'],
            'growth': ['learning', 'developing', 'improving', 'stagnant', 'bored', 'challenging'],
            'communication': ['clear', 'confused', 'transparent', 'unclear', 'open', 'closed']
        }
    
    def analyze_team_satisfaction(self, communication_data: Dict) -> Dict:
        """Analizar satisfacción general del equipo."""
        try:
            logger.info("Analizando satisfacción del equipo...")
            
            # Analizar diferentes tipos de comunicación
            messages_analysis = self._analyze_messages(communication_data.get('messages', []))
            meeting_analysis = self._analyze_meetings(communication_data.get('meetings', []))
            feedback_analysis = self._analyze_feedback(communication_data.get('feedback', []))
            
            # Calcular satisfacción por categorías
            category_scores = self._calculate_category_scores(communication_data)
            
            # Calcular satisfacción general
            overall_satisfaction = self._calculate_overall_satisfaction(
                messages_analysis, meeting_analysis, feedback_analysis, category_scores
            )
            
            # Generar insights
            insights = self._generate_satisfaction_insights(
                overall_satisfaction, category_scores, messages_analysis
            )
            
            # Generar recomendaciones
            recommendations = self._generate_satisfaction_recommendations(
                overall_satisfaction, category_scores
            )
            
            return {
                'overall_satisfaction': overall_satisfaction,
                'category_scores': category_scores,
                'messages_analysis': messages_analysis,
                'meeting_analysis': meeting_analysis,
                'feedback_analysis': feedback_analysis,
                'insights': insights,
                'recommendations': recommendations,
                'analysis_date': datetime.now().isoformat(),
                'confidence': self._calculate_analysis_confidence(
                    messages_analysis, meeting_analysis, feedback_analysis
                )
            }
            
        except Exception as e:
            logger.error(f"Error analizando satisfacción del equipo: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_messages(self, messages: List[Dict]) -> Dict:
        """Analizar sentimientos en mensajes."""
        if not messages:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        sentiments = []
        total_confidence = 0.0
        
        for message in messages:
            content = message.get('content', '')
            sentiment_result = self.sentiment_analyzer.analyze_text_sentiment(content)
            sentiments.append(sentiment_result['score'])
            total_confidence += sentiment_result['confidence']
        
        avg_sentiment = statistics.mean(sentiments) if sentiments else 0.0
        avg_confidence = total_confidence / len(messages) if messages else 0.0
        
        # Clasificar sentimiento general
        if avg_sentiment > 0.1:
            sentiment = 'positive'
        elif avg_sentiment < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': avg_sentiment,
            'confidence': avg_confidence,
            'message_count': len(messages),
            'individual_scores': sentiments
        }
    
    def _analyze_meetings(self, meetings: List[Dict]) -> Dict:
        """Analizar sentimientos en reuniones."""
        if not meetings:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        # Simular análisis de reuniones (en producción sería más complejo)
        meeting_sentiments = []
        
        for meeting in meetings:
            # Analizar notas de reunión si están disponibles
            notes = meeting.get('notes', '')
            if notes:
                sentiment_result = self.sentiment_analyzer.analyze_text_sentiment(notes)
                meeting_sentiments.append(sentiment_result['score'])
            else:
                # Score neutral por defecto
                meeting_sentiments.append(0.0)
        
        avg_sentiment = statistics.mean(meeting_sentiments) if meeting_sentiments else 0.0
        
        return {
            'sentiment': 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral',
            'score': avg_sentiment,
            'confidence': 0.7,  # Confianza media para reuniones
            'meeting_count': len(meetings)
        }
    
    def _analyze_feedback(self, feedback_list: List[Dict]) -> Dict:
        """Analizar feedback del equipo."""
        if not feedback_list:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        feedback_sentiments = []
        
        for feedback in feedback_list:
            content = feedback.get('content', '')
            sentiment_result = self.sentiment_analyzer.analyze_text_sentiment(content)
            feedback_sentiments.append(sentiment_result['score'])
        
        avg_sentiment = statistics.mean(feedback_sentiments) if feedback_sentiments else 0.0
        
        return {
            'sentiment': 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral',
            'score': avg_sentiment,
            'confidence': 0.8,  # Alta confianza para feedback directo
            'feedback_count': len(feedback_list)
        }
    
    def _calculate_category_scores(self, communication_data: Dict) -> Dict:
        """Calcular scores por categorías de satisfacción."""
        category_scores = {}
        
        for category, indicators in self.satisfaction_indicators.items():
            positive_indicators = indicators[:len(indicators)//2]
            negative_indicators = indicators[len(indicators)//2:]
            
            # Buscar indicadores en todos los textos
            all_text = self._extract_all_text(communication_data)
            
            positive_count = sum(1 for indicator in positive_indicators 
                               if indicator in all_text.lower())
            negative_count = sum(1 for indicator in negative_indicators 
                               if indicator in all_text.lower())
            
            # Calcular score de categoría
            total_indicators = positive_count + negative_count
            if total_indicators > 0:
                category_score = (positive_count - negative_count) / total_indicators
            else:
                category_score = 0.0
            
            category_scores[category] = {
                'score': category_score,
                'positive_indicators': positive_count,
                'negative_indicators': negative_count,
                'level': self._get_satisfaction_level(category_score)
            }
        
        return category_scores
    
    def _extract_all_text(self, communication_data: Dict) -> str:
        """Extraer todo el texto de los datos de comunicación."""
        all_text = []
        
        # Mensajes
        for message in communication_data.get('messages', []):
            all_text.append(message.get('content', ''))
        
        # Reuniones
        for meeting in communication_data.get('meetings', []):
            all_text.append(meeting.get('notes', ''))
        
        # Feedback
        for feedback in communication_data.get('feedback', []):
            all_text.append(feedback.get('content', ''))
        
        return ' '.join(all_text)
    
    def _get_satisfaction_level(self, score: float) -> str:
        """Obtener nivel de satisfacción basado en score."""
        if score > 0.3:
            return 'high'
        elif score > 0.1:
            return 'medium'
        elif score > -0.1:
            return 'neutral'
        elif score > -0.3:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_overall_satisfaction(self, messages_analysis: Dict, 
                                      meeting_analysis: Dict, 
                                      feedback_analysis: Dict,
                                      category_scores: Dict) -> Dict:
        """Calcular satisfacción general del equipo."""
        # Ponderar diferentes fuentes
        weights = {
            'messages': 0.4,
            'meetings': 0.3,
            'feedback': 0.3
        }
        
        weighted_score = (
            messages_analysis['score'] * weights['messages'] +
            meeting_analysis['score'] * weights['meetings'] +
            feedback_analysis['score'] * weights['feedback']
        )
        
        # Incluir scores de categorías
        category_avg = statistics.mean([cat['score'] for cat in category_scores.values()])
        
        # Score final combinado
        final_score = (weighted_score + category_avg) / 2
        
        return {
            'score': final_score,
            'level': self._get_satisfaction_level(final_score),
            'trend': self._calculate_trend(final_score),
            'confidence': (messages_analysis['confidence'] + 
                          meeting_analysis['confidence'] + 
                          feedback_analysis['confidence']) / 3
        }
    
    def _calculate_trend(self, current_score: float) -> str:
        """Calcular tendencia de satisfacción."""
        # En producción, comparar con scores históricos
        # Por ahora, simular tendencia
        if current_score > 0.2:
            return 'improving'
        elif current_score < -0.2:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_satisfaction_insights(self, overall_satisfaction: Dict, 
                                      category_scores: Dict,
                                      messages_analysis: Dict) -> List[str]:
        """Generar insights de satisfacción."""
        insights = []
        
        # Insight general
        level = overall_satisfaction['level']
        if level == 'high':
            insights.append("El equipo muestra alta satisfacción general")
        elif level == 'low' or level == 'very_low':
            insights.append("El equipo muestra signos de insatisfacción que requieren atención")
        else:
            insights.append("El equipo mantiene un nivel de satisfacción moderado")
        
        # Insights por categoría
        for category, data in category_scores.items():
            level = data['level']
            if level == 'high':
                insights.append(f"Excelente satisfacción en {category}")
            elif level == 'low' or level == 'very_low':
                insights.append(f"Baja satisfacción en {category} - requiere mejora")
        
        # Insights de comunicación
        if messages_analysis['sentiment'] == 'positive':
            insights.append("La comunicación del equipo es predominantemente positiva")
        elif messages_analysis['sentiment'] == 'negative':
            insights.append("La comunicación muestra signos de frustración o estrés")
        
        return insights
    
    def _generate_satisfaction_recommendations(self, overall_satisfaction: Dict,
                                             category_scores: Dict) -> List[str]:
        """Generar recomendaciones basadas en satisfacción."""
        recommendations = []
        
        level = overall_satisfaction['level']
        
        if level == 'high':
            recommendations.extend([
                "Mantener las prácticas actuales que generan alta satisfacción",
                "Documentar y compartir mejores prácticas con otros equipos",
                "Continuar con reconocimientos y celebraciones de logros"
            ])
        elif level == 'low' or level == 'very_low':
            recommendations.extend([
                "Implementar sesiones de feedback individual con cada miembro del equipo",
                "Revisar carga de trabajo y distribución de tareas",
                "Programar actividades de team building y fortalecimiento del equipo",
                "Establecer canales de comunicación más abiertos y transparentes"
            ])
        else:
            recommendations.extend([
                "Implementar encuestas de satisfacción regulares",
                "Identificar áreas específicas de mejora",
                "Mantener comunicación abierta sobre preocupaciones del equipo"
            ])
        
        # Recomendaciones específicas por categoría
        for category, data in category_scores.items():
            if data['level'] == 'low' or data['level'] == 'very_low':
                if category == 'workload':
                    recommendations.append("Revisar y redistribuir carga de trabajo")
                elif category == 'collaboration':
                    recommendations.append("Implementar actividades de colaboración y team building")
                elif category == 'recognition':
                    recommendations.append("Aumentar reconocimientos y feedback positivo")
                elif category == 'growth':
                    recommendations.append("Proporcionar oportunidades de desarrollo y aprendizaje")
                elif category == 'communication':
                    recommendations.append("Mejorar canales y procesos de comunicación")
        
        return recommendations
    
    def _calculate_analysis_confidence(self, messages_analysis: Dict,
                                     meeting_analysis: Dict,
                                     feedback_analysis: Dict) -> float:
        """Calcular confianza general del análisis."""
        confidences = [
            messages_analysis['confidence'],
            meeting_analysis['confidence'],
            feedback_analysis['confidence']
        ]
        
        return statistics.mean(confidences)

class ClickUpBrainSentimentAnalysis:
    """Sistema principal de análisis de sentimientos."""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.satisfaction_analyzer = TeamSatisfactionAnalyzer()
        self.analysis_history = []
    
    def analyze_team_sentiment(self, communication_data: Dict) -> Dict:
        """Analizar sentimientos del equipo."""
        try:
            logger.info("Iniciando análisis de sentimientos del equipo...")
            
            # Análisis de satisfacción
            satisfaction_analysis = self.satisfaction_analyzer.analyze_team_satisfaction(communication_data)
            
            # Análisis de sentimientos por mensajes
            messages = communication_data.get('messages', [])
            message_sentiments = []
            
            for message in messages:
                sentiment_result = self.sentiment_analyzer.analyze_text_sentiment(
                    message.get('content', '')
                )
                message_sentiments.append(sentiment_result)
            
            # Análisis temporal
            temporal_analysis = self._analyze_temporal_patterns(communication_data)
            
            # Análisis de temas
            topic_analysis = self._analyze_topics(communication_data)
            
            # Compilar resultados
            results = {
                'analysis_timestamp': datetime.now().isoformat(),
                'satisfaction_analysis': satisfaction_analysis,
                'message_sentiments': message_sentiments,
                'temporal_analysis': temporal_analysis,
                'topic_analysis': topic_analysis,
                'overall_sentiment': self._calculate_overall_sentiment(message_sentiments),
                'confidence': self._calculate_overall_confidence(satisfaction_analysis, message_sentiments)
            }
            
            # Guardar en historial
            self.analysis_history.append(results)
            
            logger.info("Análisis de sentimientos completado")
            return results
            
        except Exception as e:
            logger.error(f"Error en análisis de sentimientos: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_temporal_patterns(self, communication_data: Dict) -> Dict:
        """Analizar patrones temporales de sentimientos."""
        try:
            # Simular análisis temporal (en producción sería más complejo)
            return {
                'daily_patterns': {
                    'morning_sentiment': 0.2,
                    'afternoon_sentiment': 0.1,
                    'evening_sentiment': -0.1
                },
                'weekly_patterns': {
                    'monday_sentiment': -0.1,
                    'friday_sentiment': 0.3
                },
                'trends': {
                    'last_week': 0.1,
                    'last_month': 0.05,
                    'trend_direction': 'stable'
                }
            }
        except Exception as e:
            logger.error(f"Error analizando patrones temporales: {str(e)}")
            return {}
    
    def _analyze_topics(self, communication_data: Dict) -> Dict:
        """Analizar temas principales en las comunicaciones."""
        try:
            # Extraer texto de todas las comunicaciones
            all_text = self.satisfaction_analyzer._extract_all_text(communication_data)
            
            # Palabras clave por tema
            topic_keywords = {
                'workload': ['busy', 'overwhelmed', 'tasks', 'deadline', 'pressure'],
                'collaboration': ['team', 'help', 'support', 'together', 'collaborate'],
                'recognition': ['good', 'great', 'excellent', 'appreciate', 'thanks'],
                'challenges': ['difficult', 'problem', 'issue', 'challenge', 'struggle'],
                'growth': ['learn', 'develop', 'improve', 'skill', 'training']
            }
            
            topic_scores = {}
            for topic, keywords in topic_keywords.items():
                score = sum(1 for keyword in keywords if keyword in all_text.lower())
                topic_scores[topic] = score
            
            return {
                'topic_scores': topic_scores,
                'dominant_topics': sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            }
        except Exception as e:
            logger.error(f"Error analizando temas: {str(e)}")
            return {}
    
    def _calculate_overall_sentiment(self, message_sentiments: List[Dict]) -> Dict:
        """Calcular sentimiento general."""
        if not message_sentiments:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        scores = [msg['score'] for msg in message_sentiments]
        confidences = [msg['confidence'] for msg in message_sentiments]
        
        avg_score = statistics.mean(scores)
        avg_confidence = statistics.mean(confidences)
        
        if avg_score > 0.1:
            sentiment = 'positive'
        elif avg_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': avg_score,
            'confidence': avg_confidence,
            'message_count': len(message_sentiments)
        }
    
    def _calculate_overall_confidence(self, satisfaction_analysis: Dict, 
                                    message_sentiments: List[Dict]) -> float:
        """Calcular confianza general del análisis."""
        try:
            satisfaction_confidence = satisfaction_analysis.get('confidence', 0.8)
            message_confidence = statistics.mean([msg['confidence'] for msg in message_sentiments]) if message_sentiments else 0.8
            
            return (satisfaction_confidence + message_confidence) / 2
        except Exception as e:
            logger.error(f"Error calculando confianza general: {str(e)}")
            return 0.8
    
    def generate_sentiment_report(self, analysis_results: Dict) -> str:
        """Generar reporte de análisis de sentimientos."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            report = f"""# 😊 ClickUp Brain - Reporte de Análisis de Sentimientos

## 📊 Resumen del Análisis

**Fecha:** {timestamp}
**Confianza General:** {analysis_results.get('confidence', 0.8):.1%}

## 🎯 Satisfacción del Equipo

"""
            
            if 'satisfaction_analysis' in analysis_results:
                satisfaction = analysis_results['satisfaction_analysis']
                if 'error' not in satisfaction:
                    overall = satisfaction.get('overall_satisfaction', {})
                    report += f"""
### Satisfacción General:
- **Score:** {overall.get('score', 0):.2f}
- **Nivel:** {overall.get('level', 'neutral').title()}
- **Tendencia:** {overall.get('trend', 'stable').title()}
- **Confianza:** {overall.get('confidence', 0.8):.1%}

### Satisfacción por Categorías:
"""
                    for category, data in satisfaction.get('category_scores', {}).items():
                        report += f"- **{category.title()}:** {data['level'].title()} (Score: {data['score']:.2f})\n"
                    
                    report += f"""
### Insights de Satisfacción:
"""
                    for insight in satisfaction.get('insights', []):
                        report += f"- {insight}\n"
                    
                    report += f"""
### Recomendaciones:
"""
                    for rec in satisfaction.get('recommendations', []):
                        report += f"- {rec}\n"
            
            # Análisis de sentimientos
            if 'overall_sentiment' in analysis_results:
                sentiment = analysis_results['overall_sentiment']
                report += f"""
## 😊 Análisis de Sentimientos

- **Sentimiento General:** {sentiment.get('sentiment', 'neutral').title()}
- **Score:** {sentiment.get('score', 0):.2f}
- **Confianza:** {sentiment.get('confidence', 0.8):.1%}
- **Mensajes Analizados:** {sentiment.get('message_count', 0)}
"""
            
            # Análisis temporal
            if 'temporal_analysis' in analysis_results:
                temporal = analysis_results['temporal_analysis']
                if temporal:
                    report += f"""
## ⏰ Patrones Temporales

### Patrones Diarios:
- **Mañana:** {temporal.get('daily_patterns', {}).get('morning_sentiment', 0):.2f}
- **Tarde:** {temporal.get('daily_patterns', {}).get('afternoon_sentiment', 0):.2f}
- **Noche:** {temporal.get('daily_patterns', {}).get('evening_sentiment', 0):.2f}

### Tendencias:
- **Última Semana:** {temporal.get('trends', {}).get('last_week', 0):.2f}
- **Último Mes:** {temporal.get('trends', {}).get('last_month', 0):.2f}
- **Dirección:** {temporal.get('trends', {}).get('trend_direction', 'stable').title()}
"""
            
            # Análisis de temas
            if 'topic_analysis' in analysis_results:
                topics = analysis_results['topic_analysis']
                if topics:
                    report += f"""
## 🎯 Temas Principales

### Temas Más Mencionados:
"""
                    for topic, score in topics.get('dominant_topics', []):
                        report += f"- **{topic.title()}:** {score} menciones\n"
            
            report += f"""
---
*Reporte generado automáticamente por ClickUp Brain Sentiment Analysis System*
*Confianza general del análisis: {analysis_results.get('confidence', 0.8):.1%}*
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte de sentimientos: {str(e)}")
            return f"Error generando reporte: {str(e)}"

def main():
    """Función principal para demostrar el análisis de sentimientos."""
    print("😊 ClickUp Brain - Sistema de Análisis de Sentimientos y Satisfacción del Equipo")
    print("=" * 80)
    
    # Inicializar sistema
    sentiment_system = ClickUpBrainSentimentAnalysis()
    
    # Datos de comunicación de ejemplo
    communication_data = {
        'messages': [
            {'content': 'Great work on the new feature! Really impressed with the quality.'},
            {'content': 'Thanks for the help with the bug fix. You saved me hours of work.'},
            {'content': 'Feeling a bit overwhelmed with all these deadlines. Need some support.'},
            {'content': 'Love the new collaboration tools. Makes teamwork so much easier.'},
            {'content': 'The code review process is working really well. Great improvements!'},
            {'content': 'Struggling with the new framework. Could use some training.'},
            {'content': 'Excellent team meeting today. Clear direction and good communication.'},
            {'content': 'Frustrated with the constant changes. Hard to keep up.'},
            {'content': 'Really appreciate the recognition for the project. Motivated to do more!'},
            {'content': 'The workload is manageable this week. Good balance.'}
        ],
        'meetings': [
            {'notes': 'Positive discussion about project progress. Team is motivated and collaborative.'},
            {'notes': 'Some concerns raised about timeline but overall good team spirit.'},
            {'notes': 'Great brainstorming session. Everyone contributed valuable ideas.'}
        ],
        'feedback': [
            {'content': 'Really enjoying working with this team. Great collaboration and support.'},
            {'content': 'Would like more opportunities for professional development.'},
            {'content': 'The workload is sometimes overwhelming but the team helps each other.'},
            {'content': 'Appreciate the clear communication and regular updates.'}
        ]
    }
    
    print("🔍 Analizando sentimientos del equipo...")
    
    # Realizar análisis
    results = sentiment_system.analyze_team_sentiment(communication_data)
    
    if 'error' in results:
        print(f"❌ Error en análisis: {results['error']}")
        return False
    
    print("✅ Análisis completado exitosamente")
    
    # Mostrar resultados principales
    print(f"\n📊 Resultados del Análisis:")
    print(f"   • Confianza General: {results.get('confidence', 0.8):.1%}")
    
    if 'overall_sentiment' in results:
        sentiment = results['overall_sentiment']
        print(f"   • Sentimiento General: {sentiment.get('sentiment', 'neutral').title()}")
        print(f"   • Score: {sentiment.get('score', 0):.2f}")
        print(f"   • Mensajes Analizados: {sentiment.get('message_count', 0)}")
    
    if 'satisfaction_analysis' in results:
        satisfaction = results['satisfaction_analysis']
        if 'error' not in satisfaction:
            overall = satisfaction.get('overall_satisfaction', {})
            print(f"   • Satisfacción General: {overall.get('level', 'neutral').title()}")
            print(f"   • Score de Satisfacción: {overall.get('score', 0):.2f}")
    
    # Generar reporte
    print("\n📄 Generando reporte detallado...")
    report = sentiment_system.generate_sentiment_report(results)
    
    # Guardar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"sentiment_analysis_report_{timestamp}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Reporte guardado: {report_filename}")
    
    print("\n🎉 Sistema de análisis de sentimientos funcionando correctamente!")
    print("🚀 Listo para monitorear satisfacción y bienestar del equipo")
    
    return True

if __name__ == "__main__":
    main()








