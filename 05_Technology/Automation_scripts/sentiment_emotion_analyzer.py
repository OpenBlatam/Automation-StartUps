#!/usr/bin/env python3
"""
Sistema de Análisis de Sentimientos y Emociones para Neural Marketing Consciousness Platform
"""

import json
import time
import sqlite3
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import random
from collections import Counter, defaultdict
import math

class SentimentEmotionAnalyzer:
    def __init__(self, db_path="sentiment_analysis.db"):
        self.db_path = db_path
        self.sentiment_lexicons = {}
        self.emotion_models = {}
        self.init_sentiment_database()
        self.load_sentiment_lexicons()
        self.load_emotion_models()
    
    def init_sentiment_database(self):
        """Inicializar base de datos de análisis de sentimientos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de análisis de sentimientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                text_content TEXT,
                sentiment_score REAL,
                sentiment_label TEXT,
                confidence REAL,
                emotions TEXT,
                language TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de métricas de sentimientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                time_period TEXT,
                avg_sentiment REAL,
                sentiment_distribution TEXT,
                emotion_trends TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de feedback de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                content_id TEXT,
                feedback_text TEXT,
                sentiment_score REAL,
                emotions TEXT,
                rating INTEGER,
                created_at TEXT
            )
        ''')
        
        # Tabla de tendencias de sentimientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trend_type TEXT,
                trend_data TEXT,
                time_period TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_sentiment_lexicons(self):
        """Cargar léxicos de sentimientos"""
        self.sentiment_lexicons = {
            'positive_words': {
                'excellent': 0.9, 'amazing': 0.9, 'fantastic': 0.9, 'wonderful': 0.8,
                'great': 0.8, 'good': 0.7, 'nice': 0.6, 'awesome': 0.9, 'brilliant': 0.8,
                'outstanding': 0.9, 'perfect': 1.0, 'love': 0.9, 'like': 0.7, 'enjoy': 0.8,
                'happy': 0.8, 'pleased': 0.7, 'satisfied': 0.7, 'impressed': 0.8,
                'recommend': 0.8, 'excellent': 0.9, 'superb': 0.9, 'marvelous': 0.9
            },
            'negative_words': {
                'terrible': -0.9, 'awful': -0.9, 'horrible': -0.9, 'bad': -0.7,
                'worst': -0.9, 'hate': -0.9, 'dislike': -0.6, 'disappointed': -0.7,
                'angry': -0.8, 'frustrated': -0.7, 'annoyed': -0.6, 'upset': -0.7,
                'sad': -0.6, 'unhappy': -0.7, 'disgusted': -0.8, 'furious': -0.9,
                'terrible': -0.9, 'awful': -0.9, 'horrible': -0.9, 'disgusting': -0.8
            },
            'intensifiers': {
                'very': 1.5, 'extremely': 2.0, 'incredibly': 2.0, 'absolutely': 1.8,
                'totally': 1.5, 'completely': 1.5, 'really': 1.3, 'quite': 1.2,
                'somewhat': 0.8, 'slightly': 0.7, 'barely': 0.5, 'hardly': 0.3
            },
            'negators': {
                'not': -1.0, 'no': -1.0, 'never': -1.0, 'none': -1.0,
                'nothing': -1.0, 'nobody': -1.0, 'nowhere': -1.0, 'neither': -1.0
            }
        }
    
    def load_emotion_models(self):
        """Cargar modelos de emociones"""
        self.emotion_models = {
            'basic_emotions': {
                'joy': {
                    'keywords': ['happy', 'joy', 'excited', 'thrilled', 'delighted', 'cheerful', 'elated'],
                    'weight': 1.0
                },
                'sadness': {
                    'keywords': ['sad', 'depressed', 'melancholy', 'gloomy', 'sorrowful', 'dejected', 'miserable'],
                    'weight': 1.0
                },
                'anger': {
                    'keywords': ['angry', 'mad', 'furious', 'rage', 'irritated', 'annoyed', 'outraged'],
                    'weight': 1.0
                },
                'fear': {
                    'keywords': ['afraid', 'scared', 'terrified', 'worried', 'anxious', 'nervous', 'frightened'],
                    'weight': 1.0
                },
                'surprise': {
                    'keywords': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'bewildered'],
                    'weight': 1.0
                },
                'disgust': {
                    'keywords': ['disgusted', 'revolted', 'repulsed', 'sickened', 'appalled', 'horrified'],
                    'weight': 1.0
                }
            },
            'marketing_emotions': {
                'trust': {
                    'keywords': ['trust', 'reliable', 'credible', 'honest', 'authentic', 'genuine', 'transparent'],
                    'weight': 1.2
                },
                'excitement': {
                    'keywords': ['excited', 'thrilled', 'enthusiastic', 'eager', 'passionate', 'energetic'],
                    'weight': 1.1
                },
                'curiosity': {
                    'keywords': ['curious', 'interested', 'intrigued', 'fascinated', 'wondering', 'questioning'],
                    'weight': 1.0
                },
                'urgency': {
                    'keywords': ['urgent', 'immediate', 'now', 'quickly', 'hurry', 'limited', 'deadline'],
                    'weight': 1.3
                },
                'satisfaction': {
                    'keywords': ['satisfied', 'pleased', 'content', 'fulfilled', 'gratified', 'happy'],
                    'weight': 1.1
                }
            }
        }
    
    def analyze_sentiment(self, text: str, content_id: str = None) -> Dict:
        """Analizar sentimiento del texto"""
        try:
            # Preprocesar texto
            processed_text = self.preprocess_text(text)
            
            # Calcular puntuación de sentimiento
            sentiment_score = self.calculate_sentiment_score(processed_text)
            
            # Determinar etiqueta de sentimiento
            sentiment_label = self.get_sentiment_label(sentiment_score)
            
            # Calcular confianza
            confidence = self.calculate_confidence(processed_text, sentiment_score)
            
            # Analizar emociones
            emotions = self.analyze_emotions(processed_text)
            
            # Detectar idioma
            language = self.detect_language(text)
            
            # Guardar análisis
            if content_id:
                self.save_sentiment_analysis(content_id, text, sentiment_score, 
                                           sentiment_label, confidence, emotions, language)
            
            return {
                'success': True,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'confidence': confidence,
                'emotions': emotions,
                'language': language,
                'text_length': len(text),
                'processed_text': processed_text
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def preprocess_text(self, text: str) -> str:
        """Preprocesar texto para análisis"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales pero mantener puntuación básica
        text = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', text)
        
        # Normalizar espacios en blanco
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Calcular puntuación de sentimiento"""
        words = text.split()
        total_score = 0.0
        word_count = 0
        
        i = 0
        while i < len(words):
            word = words[i]
            word_score = 0.0
            
            # Verificar si es una palabra de sentimiento
            if word in self.sentiment_lexicons['positive_words']:
                word_score = self.sentiment_lexicons['positive_words'][word]
            elif word in self.sentiment_lexicons['negative_words']:
                word_score = self.sentiment_lexicons['negative_words'][word]
            
            # Verificar intensificadores
            if i > 0 and words[i-1] in self.sentiment_lexicons['intensifiers']:
                intensifier = self.sentiment_lexicons['intensifiers'][words[i-1]]
                word_score *= intensifier
            
            # Verificar negadores
            if i > 0 and words[i-1] in self.sentiment_lexicons['negators']:
                word_score *= -1.0
            
            # Verificar doble negación
            if i > 1 and (words[i-1] in self.sentiment_lexicons['negators'] and 
                         words[i-2] in self.sentiment_lexicons['negators']):
                word_score *= -1.0
            
            total_score += word_score
            if word_score != 0:
                word_count += 1
            
            i += 1
        
        # Normalizar puntuación
        if word_count > 0:
            normalized_score = total_score / word_count
            return max(-1.0, min(1.0, normalized_score))
        
        return 0.0
    
    def get_sentiment_label(self, score: float) -> str:
        """Obtener etiqueta de sentimiento basada en puntuación"""
        if score >= 0.3:
            return 'positive'
        elif score <= -0.3:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_confidence(self, text: str, sentiment_score: float) -> float:
        """Calcular confianza del análisis"""
        words = text.split()
        sentiment_words = 0
        
        for word in words:
            if (word in self.sentiment_lexicons['positive_words'] or 
                word in self.sentiment_lexicons['negative_words']):
                sentiment_words += 1
        
        # Confianza basada en densidad de palabras de sentimiento
        if len(words) > 0:
            density = sentiment_words / len(words)
            confidence = min(1.0, density * 2)  # Escalar densidad
        else:
            confidence = 0.0
        
        # Ajustar por magnitud del score
        magnitude = abs(sentiment_score)
        confidence = (confidence + magnitude) / 2
        
        return round(confidence, 3)
    
    def analyze_emotions(self, text: str) -> Dict:
        """Analizar emociones en el texto"""
        emotions = {}
        words = text.split()
        
        # Analizar emociones básicas
        for emotion, data in self.emotion_models['basic_emotions'].items():
            emotion_score = 0.0
            for keyword in data['keywords']:
                if keyword in words:
                    emotion_score += data['weight']
            
            if emotion_score > 0:
                emotions[emotion] = round(emotion_score, 3)
        
        # Analizar emociones de marketing
        for emotion, data in self.emotion_models['marketing_emotions'].items():
            emotion_score = 0.0
            for keyword in data['keywords']:
                if keyword in words:
                    emotion_score += data['weight']
            
            if emotion_score > 0:
                emotions[emotion] = round(emotion_score, 3)
        
        return emotions
    
    def detect_language(self, text: str) -> str:
        """Detectar idioma del texto (simplificado)"""
        # Detectar patrones básicos de idiomas comunes
        if re.search(r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b', text.lower()):
            return 'en'  # Inglés
        elif re.search(r'\b(el|la|de|que|y|en|un|es|se|no|te|lo|le|da|su|por|son|con|para|al|del|los|las)\b', text.lower()):
            return 'es'  # Español
        elif re.search(r'\b(le|de|et|du|des|la|les|un|une|est|pour|avec|dans|sur|par)\b', text.lower()):
            return 'fr'  # Francés
        else:
            return 'unknown'
    
    def save_sentiment_analysis(self, content_id: str, text: str, sentiment_score: float,
                              sentiment_label: str, confidence: float, emotions: Dict, 
                              language: str):
        """Guardar análisis de sentimiento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sentiment_analysis 
                (content_id, text_content, sentiment_score, sentiment_label, 
                 confidence, emotions, language, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (content_id, text, sentiment_score, sentiment_label, confidence,
                  json.dumps(emotions), language, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving sentiment analysis: {e}")
    
    def analyze_user_sentiment_trends(self, user_id: str, days: int = 30) -> Dict:
        """Analizar tendencias de sentimiento de usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener análisis de sentimientos del usuario
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT sentiment_score, sentiment_label, emotions, created_at
                FROM sentiment_analysis sa
                JOIN user_feedback uf ON sa.content_id = uf.content_id
                WHERE uf.user_id = ? AND sa.created_at > ?
                ORDER BY sa.created_at
            ''', (user_id, start_date))
            
            analyses = cursor.fetchall()
            conn.close()
            
            if not analyses:
                return {'success': False, 'error': 'No sentiment data found for user'}
            
            # Calcular métricas de tendencia
            scores = [analysis[0] for analysis in analyses]
            labels = [analysis[1] for analysis in analyses]
            emotions_list = [json.loads(analysis[2]) for analysis in analyses]
            
            # Estadísticas básicas
            avg_sentiment = sum(scores) / len(scores)
            sentiment_distribution = Counter(labels)
            
            # Tendencias de emociones
            emotion_trends = defaultdict(list)
            for emotions in emotions_list:
                for emotion, score in emotions.items():
                    emotion_trends[emotion].append(score)
            
            # Calcular promedios de emociones
            emotion_averages = {}
            for emotion, scores in emotion_trends.items():
                emotion_averages[emotion] = sum(scores) / len(scores)
            
            # Detectar tendencia temporal
            if len(scores) > 1:
                recent_scores = scores[-7:]  # Últimos 7 análisis
                older_scores = scores[:-7] if len(scores) > 7 else scores[:-1]
                
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores) if older_scores else recent_avg
                
                trend_direction = 'improving' if recent_avg > older_avg else 'declining'
                trend_magnitude = abs(recent_avg - older_avg)
            else:
                trend_direction = 'stable'
                trend_magnitude = 0.0
            
            return {
                'success': True,
                'user_id': user_id,
                'period_days': days,
                'total_analyses': len(analyses),
                'avg_sentiment': round(avg_sentiment, 3),
                'sentiment_distribution': dict(sentiment_distribution),
                'emotion_averages': emotion_averages,
                'trend_direction': trend_direction,
                'trend_magnitude': round(trend_magnitude, 3),
                'recommendations': self.generate_sentiment_recommendations(avg_sentiment, emotion_averages)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_sentiment_recommendations(self, avg_sentiment: float, 
                                         emotion_averages: Dict) -> List[str]:
        """Generar recomendaciones basadas en sentimientos"""
        recommendations = []
        
        # Recomendaciones basadas en sentimiento general
        if avg_sentiment < -0.3:
            recommendations.append("Consider creating more positive content to improve user sentiment")
            recommendations.append("Focus on addressing user concerns and pain points")
        elif avg_sentiment > 0.3:
            recommendations.append("Great sentiment! Continue with current content strategy")
            recommendations.append("Consider leveraging positive sentiment for testimonials")
        else:
            recommendations.append("Neutral sentiment detected - try to add more engaging elements")
        
        # Recomendaciones basadas en emociones específicas
        if 'anger' in emotion_averages and emotion_averages['anger'] > 0.5:
            recommendations.append("High anger detected - implement customer service improvements")
        
        if 'joy' in emotion_averages and emotion_averages['joy'] > 0.7:
            recommendations.append("High joy levels - perfect for viral content creation")
        
        if 'trust' in emotion_averages and emotion_averages['trust'] < 0.3:
            recommendations.append("Low trust levels - focus on building credibility and transparency")
        
        if 'urgency' in emotion_averages and emotion_averages['urgency'] > 0.6:
            recommendations.append("High urgency detected - consider time-sensitive offers")
        
        return recommendations
    
    def analyze_content_sentiment_batch(self, content_list: List[Dict]) -> Dict:
        """Analizar sentimientos de múltiples contenidos"""
        try:
            results = []
            total_positive = 0
            total_negative = 0
            total_neutral = 0
            emotion_counts = defaultdict(int)
            
            for content in content_list:
                content_id = content.get('id', f"content_{len(results)}")
                text = content.get('text', '')
                
                analysis = self.analyze_sentiment(text, content_id)
                if analysis['success']:
                    results.append({
                        'content_id': content_id,
                        'sentiment_score': analysis['sentiment_score'],
                        'sentiment_label': analysis['sentiment_label'],
                        'confidence': analysis['confidence'],
                        'emotions': analysis['emotions']
                    })
                    
                    # Contar sentimientos
                    if analysis['sentiment_label'] == 'positive':
                        total_positive += 1
                    elif analysis['sentiment_label'] == 'negative':
                        total_negative += 1
                    else:
                        total_neutral += 1
                    
                    # Contar emociones
                    for emotion in analysis['emotions']:
                        emotion_counts[emotion] += 1
            
            total_content = len(results)
            
            return {
                'success': True,
                'total_content': total_content,
                'sentiment_distribution': {
                    'positive': total_positive,
                    'negative': total_negative,
                    'neutral': total_neutral,
                    'positive_percentage': round((total_positive / total_content) * 100, 2) if total_content > 0 else 0
                },
                'top_emotions': dict(Counter(emotion_counts).most_common(5)),
                'results': results
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_sentiment_insights(self, time_period: str = 'week') -> Dict:
        """Obtener insights generales de sentimientos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Determinar período de tiempo
            if time_period == 'day':
                start_date = (datetime.now() - timedelta(days=1)).isoformat()
            elif time_period == 'week':
                start_date = (datetime.now() - timedelta(weeks=1)).isoformat()
            elif time_period == 'month':
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            else:
                start_date = (datetime.now() - timedelta(weeks=1)).isoformat()
            
            # Obtener análisis de sentimientos del período
            cursor.execute('''
                SELECT sentiment_score, sentiment_label, emotions, created_at
                FROM sentiment_analysis
                WHERE created_at > ?
                ORDER BY created_at
            ''', (start_date,))
            
            analyses = cursor.fetchall()
            conn.close()
            
            if not analyses:
                return {'success': False, 'error': 'No sentiment data found for the period'}
            
            # Calcular insights
            scores = [analysis[0] for analysis in analyses]
            labels = [analysis[1] for analysis in analyses]
            emotions_list = [json.loads(analysis[2]) for analysis in analyses]
            
            # Estadísticas generales
            avg_sentiment = sum(scores) / len(scores)
            sentiment_distribution = Counter(labels)
            
            # Tendencias de emociones
            all_emotions = defaultdict(list)
            for emotions in emotions_list:
                for emotion, score in emotions.items():
                    all_emotions[emotion].append(score)
            
            emotion_averages = {}
            for emotion, scores in all_emotions.items():
                emotion_averages[emotion] = sum(scores) / len(scores)
            
            # Contenido más positivo y negativo
            positive_content = [analysis for analysis in analyses if analysis[1] == 'positive']
            negative_content = [analysis for analysis in analyses if analysis[1] == 'negative']
            
            return {
                'success': True,
                'time_period': time_period,
                'total_analyses': len(analyses),
                'avg_sentiment': round(avg_sentiment, 3),
                'sentiment_distribution': dict(sentiment_distribution),
                'emotion_averages': emotion_averages,
                'positive_content_count': len(positive_content),
                'negative_content_count': len(negative_content),
                'sentiment_trend': self.calculate_sentiment_trend(scores),
                'insights': self.generate_general_insights(avg_sentiment, emotion_averages, sentiment_distribution)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def calculate_sentiment_trend(self, scores: List[float]) -> str:
        """Calcular tendencia de sentimientos"""
        if len(scores) < 2:
            return 'insufficient_data'
        
        # Dividir en dos mitades
        mid = len(scores) // 2
        first_half = scores[:mid]
        second_half = scores[mid:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 0.1:
            return 'improving'
        elif second_avg < first_avg - 0.1:
            return 'declining'
        else:
            return 'stable'
    
    def generate_general_insights(self, avg_sentiment: float, emotion_averages: Dict, 
                                sentiment_distribution: Dict) -> List[str]:
        """Generar insights generales"""
        insights = []
        
        # Insights de sentimiento general
        if avg_sentiment > 0.3:
            insights.append("Overall positive sentiment detected - great content performance")
        elif avg_sentiment < -0.3:
            insights.append("Overall negative sentiment detected - content strategy needs adjustment")
        else:
            insights.append("Neutral sentiment detected - opportunity for more engaging content")
        
        # Insights de emociones
        if 'joy' in emotion_averages and emotion_averages['joy'] > 0.5:
            insights.append("High joy levels - perfect for viral marketing opportunities")
        
        if 'trust' in emotion_averages and emotion_averages['trust'] < 0.3:
            insights.append("Low trust levels - focus on building credibility and social proof")
        
        if 'urgency' in emotion_averages and emotion_averages['urgency'] > 0.6:
            insights.append("High urgency detected - consider time-sensitive campaigns")
        
        # Insights de distribución
        positive_pct = sentiment_distribution.get('positive', 0) / sum(sentiment_distribution.values()) * 100
        if positive_pct > 70:
            insights.append("Excellent sentiment distribution - 70%+ positive content")
        elif positive_pct < 30:
            insights.append("Poor sentiment distribution - less than 30% positive content")
        
        return insights

def main():
    analyzer = SentimentEmotionAnalyzer()
    
    print("😊 Analizador de Sentimientos y Emociones")
    print("=" * 50)
    print("1. Analizar sentimiento de texto")
    print("2. Analizar tendencias de usuario")
    print("3. Analizar lote de contenidos")
    print("4. Obtener insights generales")
    print("5. Simular análisis")
    print("6. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-6): ").strip()
        
        if choice == '1':
            text = input("Texto a analizar: ").strip()
            content_id = input("ID de contenido (opcional): ").strip() or None
            
            result = analyzer.analyze_sentiment(text, content_id)
            if result['success']:
                print(f"\n📊 Análisis de Sentimiento:")
                print(f"   Puntuación: {result['sentiment_score']:.3f}")
                print(f"   Etiqueta: {result['sentiment_label']}")
                print(f"   Confianza: {result['confidence']:.3f}")
                print(f"   Idioma: {result['language']}")
                print(f"   Emociones: {result['emotions']}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '2':
            user_id = input("ID de usuario: ").strip()
            days = int(input("Período en días (default 30): ").strip() or "30")
            
            result = analyzer.analyze_user_sentiment_trends(user_id, days)
            if result['success']:
                print(f"\n👤 Tendencias de {user_id}:")
                print(f"   Análisis totales: {result['total_analyses']}")
                print(f"   Sentimiento promedio: {result['avg_sentiment']}")
                print(f"   Distribución: {result['sentiment_distribution']}")
                print(f"   Tendencia: {result['trend_direction']}")
                print(f"   Recomendaciones:")
                for rec in result['recommendations']:
                    print(f"     • {rec}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '3':
            print("Ingrese contenidos (JSON format):")
            content_text = input("Contenidos: ").strip()
            try:
                content_list = json.loads(content_text) if content_text else [
                    {"id": "content1", "text": "This is amazing content!"},
                    {"id": "content2", "text": "I hate this product."},
                    {"id": "content3", "text": "It's okay, nothing special."}
                ]
                
                result = analyzer.analyze_content_sentiment_batch(content_list)
                if result['success']:
                    print(f"\n📈 Análisis de Lote:")
                    print(f"   Total contenidos: {result['total_content']}")
                    print(f"   Distribución: {result['sentiment_distribution']}")
                    print(f"   Top emociones: {result['top_emotions']}")
                else:
                    print(f"❌ {result['error']}")
            except json.JSONDecodeError:
                print("❌ Formato JSON inválido")
        
        elif choice == '4':
            period = input("Período (day/week/month): ").strip() or "week"
            
            result = analyzer.get_sentiment_insights(period)
            if result['success']:
                print(f"\n📊 Insights de Sentimiento ({period}):")
                print(f"   Análisis totales: {result['total_analyses']}")
                print(f"   Sentimiento promedio: {result['avg_sentiment']}")
                print(f"   Distribución: {result['sentiment_distribution']}")
                print(f"   Tendencia: {result['sentiment_trend']}")
                print(f"   Insights:")
                for insight in result['insights']:
                    print(f"     • {insight}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '5':
            print("🔄 Simulando análisis...")
            
            # Simular análisis de sentimientos
            sample_texts = [
                "This product is absolutely amazing! I love it!",
                "Terrible experience, worst product ever.",
                "It's okay, nothing special but works fine.",
                "I'm so excited about this new feature!",
                "This is frustrating and disappointing.",
                "Great service, highly recommend!",
                "Not sure about this, seems average.",
                "Outstanding quality and excellent support!"
            ]
            
            for i, text in enumerate(sample_texts):
                result = analyzer.analyze_sentiment(text, f"sample_{i+1}")
                if result['success']:
                    print(f"   {text[:50]}... -> {result['sentiment_label']} ({result['sentiment_score']:.2f})")
            
            print("✅ Análisis simulados completados")
        
        elif choice == '6':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()
