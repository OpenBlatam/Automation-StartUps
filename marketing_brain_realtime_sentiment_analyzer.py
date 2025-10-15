"""
Marketing Brain Real-time Sentiment Analyzer
Sistema avanzado de análisis de sentimientos en tiempo real
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import warnings
warnings.filterwarnings('ignore')

class RealtimeSentimentAnalyzer:
    def __init__(self):
        self.sentiment_data = {}
        self.sentiment_models = {}
        self.topic_models = {}
        self.brand_mentions = {}
        self.competitor_mentions = {}
        self.sentiment_trends = {}
        self.alert_system = {}
        
    def analyze_text_sentiment(self, text, source='unknown'):
        """Analizar sentimiento de texto"""
        if not text or not isinstance(text, str):
            return None
        
        # Limpiar texto
        cleaned_text = self._clean_text(text)
        
        # Análisis con múltiples métodos
        sentiment_scores = {}
        
        # TextBlob
        blob = TextBlob(cleaned_text)
        sentiment_scores['textblob'] = {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'sentiment': self._classify_sentiment(blob.sentiment.polarity)
        }
        
        # VADER
        vader_analyzer = SentimentIntensityAnalyzer()
        vader_scores = vader_analyzer.polarity_scores(cleaned_text)
        sentiment_scores['vader'] = {
            'compound': vader_scores['compound'],
            'positive': vader_scores['pos'],
            'neutral': vader_scores['neu'],
            'negative': vader_scores['neg'],
            'sentiment': self._classify_sentiment(vader_scores['compound'])
        }
        
        # Análisis de emociones
        emotions = self._analyze_emotions(cleaned_text)
        
        # Análisis de aspectos
        aspects = self._analyze_aspects(cleaned_text)
        
        # Detectar menciones de marca
        brand_mentions = self._detect_brand_mentions(cleaned_text)
        
        # Detectar menciones de competidores
        competitor_mentions = self._detect_competitor_mentions(cleaned_text)
        
        sentiment_analysis = {
            'text': text,
            'cleaned_text': cleaned_text,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'sentiment_scores': sentiment_scores,
            'emotions': emotions,
            'aspects': aspects,
            'brand_mentions': brand_mentions,
            'competitor_mentions': competitor_mentions,
            'overall_sentiment': self._calculate_overall_sentiment(sentiment_scores)
        }
        
        return sentiment_analysis
    
    def _clean_text(self, text):
        """Limpiar texto para análisis"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remover menciones y hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remover caracteres especiales
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remover espacios extra
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _classify_sentiment(self, score):
        """Clasificar sentimiento basado en score"""
        if score >= 0.1:
            return 'positive'
        elif score <= -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_emotions(self, text):
        """Analizar emociones en el texto"""
        emotions = {
            'joy': 0,
            'sadness': 0,
            'anger': 0,
            'fear': 0,
            'surprise': 0,
            'disgust': 0
        }
        
        # Diccionario de palabras emocionales (simplificado)
        emotion_words = {
            'joy': ['happy', 'excited', 'great', 'amazing', 'wonderful', 'fantastic'],
            'sadness': ['sad', 'disappointed', 'terrible', 'awful', 'horrible', 'depressed'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'irritated', 'rage'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'terrified'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'unexpected'],
            'disgust': ['disgusted', 'revolted', 'sick', 'gross', 'nasty', 'repulsive']
        }
        
        words = text.split()
        for word in words:
            for emotion, emotion_list in emotion_words.items():
                if word in emotion_list:
                    emotions[emotion] += 1
        
        # Normalizar scores
        total_words = len(words)
        if total_words > 0:
            for emotion in emotions:
                emotions[emotion] = emotions[emotion] / total_words
        
        return emotions
    
    def _analyze_aspects(self, text):
        """Analizar aspectos mencionados en el texto"""
        aspects = {
            'product': 0,
            'service': 0,
            'price': 0,
            'quality': 0,
            'delivery': 0,
            'support': 0
        }
        
        # Diccionario de palabras por aspecto
        aspect_words = {
            'product': ['product', 'item', 'goods', 'merchandise'],
            'service': ['service', 'help', 'assistance', 'support'],
            'price': ['price', 'cost', 'expensive', 'cheap', 'affordable'],
            'quality': ['quality', 'good', 'bad', 'excellent', 'poor'],
            'delivery': ['delivery', 'shipping', 'fast', 'slow', 'arrived'],
            'support': ['support', 'customer', 'service', 'help', 'assistance']
        }
        
        words = text.split()
        for word in words:
            for aspect, aspect_list in aspect_words.items():
                if word in aspect_list:
                    aspects[aspect] += 1
        
        return aspects
    
    def _detect_brand_mentions(self, text):
        """Detectar menciones de marca"""
        brand_keywords = ['brand', 'company', 'our', 'we', 'us']
        mentions = []
        
        for keyword in brand_keywords:
            if keyword in text:
                mentions.append(keyword)
        
        return mentions
    
    def _detect_competitor_mentions(self, text):
        """Detectar menciones de competidores"""
        competitor_keywords = ['competitor', 'alternative', 'other', 'instead']
        mentions = []
        
        for keyword in competitor_keywords:
            if keyword in text:
                mentions.append(keyword)
        
        return mentions
    
    def _calculate_overall_sentiment(self, sentiment_scores):
        """Calcular sentimiento general"""
        # Promedio de scores de diferentes métodos
        textblob_score = sentiment_scores['textblob']['polarity']
        vader_score = sentiment_scores['vader']['compound']
        
        overall_score = (textblob_score + vader_score) / 2
        
        return {
            'score': overall_score,
            'sentiment': self._classify_sentiment(overall_score),
            'confidence': abs(overall_score)
        }
    
    def analyze_sentiment_trends(self, sentiment_data, time_window='24h'):
        """Analizar tendencias de sentimiento"""
        if not sentiment_data:
            return None
        
        # Convertir a DataFrame
        df = pd.DataFrame(sentiment_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filtrar por ventana de tiempo
        if time_window == '24h':
            cutoff_time = datetime.now() - timedelta(hours=24)
        elif time_window == '7d':
            cutoff_time = datetime.now() - timedelta(days=7)
        elif time_window == '30d':
            cutoff_time = datetime.now() - timedelta(days=30)
        else:
            cutoff_time = datetime.now() - timedelta(hours=1)
        
        df_filtered = df[df['timestamp'] >= cutoff_time]
        
        if df_filtered.empty:
            return None
        
        # Análisis de tendencias
        trends = {
            'time_window': time_window,
            'total_mentions': len(df_filtered),
            'sentiment_distribution': df_filtered['overall_sentiment'].apply(lambda x: x['sentiment']).value_counts().to_dict(),
            'average_sentiment': df_filtered['overall_sentiment'].apply(lambda x: x['score']).mean(),
            'sentiment_volatility': df_filtered['overall_sentiment'].apply(lambda x: x['score']).std(),
            'positive_mentions': len(df_filtered[df_filtered['overall_sentiment'].apply(lambda x: x['sentiment']) == 'positive']),
            'negative_mentions': len(df_filtered[df_filtered['overall_sentiment'].apply(lambda x: x['sentiment']) == 'negative']),
            'neutral_mentions': len(df_filtered[df_filtered['overall_sentiment'].apply(lambda x: x['sentiment']) == 'neutral'])
        }
        
        # Análisis por fuente
        if 'source' in df_filtered.columns:
            trends['sentiment_by_source'] = df_filtered.groupby('source')['overall_sentiment'].apply(
                lambda x: x.apply(lambda y: y['sentiment']).value_counts().to_dict()
            ).to_dict()
        
        # Análisis temporal
        df_filtered['hour'] = df_filtered['timestamp'].dt.hour
        hourly_sentiment = df_filtered.groupby('hour')['overall_sentiment'].apply(
            lambda x: x.apply(lambda y: y['score']).mean()
        ).to_dict()
        
        trends['hourly_sentiment'] = hourly_sentiment
        
        self.sentiment_trends[time_window] = trends
        return trends
    
    def build_topic_model(self, text_data, n_topics=5):
        """Construir modelo de temas"""
        if not text_data:
            return None
        
        # Preparar textos
        texts = [item['cleaned_text'] for item in text_data if item.get('cleaned_text')]
        
        if len(texts) < 10:
            return None
        
        # Vectorización TF-IDF
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Modelo LDA
        lda_model = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda_model.fit(tfidf_matrix)
        
        # Extraer temas
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(lda_model.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append({
                'topic_id': topic_idx,
                'top_words': top_words,
                'topic_weight': topic.sum()
            })
        
        # Asignar temas a documentos
        doc_topic_probs = lda_model.transform(tfidf_matrix)
        document_topics = []
        
        for i, doc_probs in enumerate(doc_topic_probs):
            dominant_topic = np.argmax(doc_probs)
            document_topics.append({
                'document_id': i,
                'dominant_topic': dominant_topic,
                'topic_probability': doc_probs[dominant_topic],
                'all_topic_probs': doc_probs.tolist()
            })
        
        topic_model = {
            'topics': topics,
            'document_topics': document_topics,
            'model_metrics': {
                'perplexity': lda_model.perplexity(tfidf_matrix),
                'log_likelihood': lda_model.score(tfidf_matrix)
            }
        }
        
        self.topic_models['lda'] = topic_model
        return topic_model
    
    def detect_sentiment_alerts(self, sentiment_data, alert_thresholds=None):
        """Detectar alertas de sentimiento"""
        if alert_thresholds is None:
            alert_thresholds = {
                'negative_sentiment_ratio': 0.3,
                'sentiment_volatility': 0.5,
                'negative_mention_spike': 2.0
            }
        
        alerts = []
        
        # Análisis de tendencias recientes
        recent_trends = self.analyze_sentiment_trends(sentiment_data, '24h')
        
        if recent_trends:
            # Alerta por ratio de sentimiento negativo
            total_mentions = recent_trends['total_mentions']
            negative_mentions = recent_trends['negative_mentions']
            
            if total_mentions > 0:
                negative_ratio = negative_mentions / total_mentions
                if negative_ratio > alert_thresholds['negative_sentiment_ratio']:
                    alerts.append({
                        'type': 'high_negative_sentiment',
                        'severity': 'high',
                        'message': f'High negative sentiment ratio: {negative_ratio:.2%}',
                        'threshold': alert_thresholds['negative_sentiment_ratio'],
                        'current_value': negative_ratio
                    })
            
            # Alerta por volatilidad de sentimiento
            volatility = recent_trends['sentiment_volatility']
            if volatility > alert_thresholds['sentiment_volatility']:
                alerts.append({
                    'type': 'high_sentiment_volatility',
                    'severity': 'medium',
                    'message': f'High sentiment volatility: {volatility:.2f}',
                    'threshold': alert_thresholds['sentiment_volatility'],
                    'current_value': volatility
                })
            
            # Alerta por spike de menciones negativas
            if 'sentiment_by_source' in recent_trends:
                for source, sentiment_dist in recent_trends['sentiment_by_source'].items():
                    if 'negative' in sentiment_dist:
                        negative_count = sentiment_dist['negative']
                        if negative_count > alert_thresholds['negative_mention_spike'] * 10:  # Ajustar threshold
                            alerts.append({
                                'type': 'negative_mention_spike',
                                'severity': 'high',
                                'message': f'Negative mention spike in {source}: {negative_count} mentions',
                                'source': source,
                                'count': negative_count
                            })
        
        self.alert_system['sentiment_alerts'] = alerts
        return alerts
    
    def create_sentiment_dashboard(self):
        """Crear dashboard de análisis de sentimientos"""
        if not self.sentiment_data and not self.sentiment_trends:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribución de Sentimientos', 'Tendencias Temporales',
                          'Análisis de Emociones', 'Temas Principales'),
            specs=[[{"type": "pie"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de distribución de sentimientos
        if self.sentiment_trends:
            for time_window, trends in self.sentiment_trends.items():
                sentiment_dist = trends.get('sentiment_distribution', {})
                if sentiment_dist:
                    fig.add_trace(
                        go.Pie(
                            labels=list(sentiment_dist.keys()),
                            values=list(sentiment_dist.values()),
                            name=f'Sentiment Distribution ({time_window})'
                        ),
                        row=1, col=1
                    )
                    break
        
        # Gráfico de tendencias temporales
        if self.sentiment_trends:
            for time_window, trends in self.sentiment_trends.items():
                hourly_sentiment = trends.get('hourly_sentiment', {})
                if hourly_sentiment:
                    hours = list(hourly_sentiment.keys())
                    sentiment_scores = list(hourly_sentiment.values())
                    
                    fig.add_trace(
                        go.Scatter(
                            x=hours,
                            y=sentiment_scores,
                            mode='lines+markers',
                            name=f'Hourly Sentiment ({time_window})'
                        ),
                        row=1, col=2
                    )
                    break
        
        # Gráfico de emociones
        if self.sentiment_data:
            # Agregar datos de emociones (simplificado)
            emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust']
            emotion_counts = [np.random.randint(0, 100) for _ in emotions]  # Simulado
            
            fig.add_trace(
                go.Bar(x=emotions, y=emotion_counts, name='Emotion Analysis'),
                row=2, col=1
            )
        
        # Gráfico de temas
        if self.topic_models:
            lda_model = self.topic_models.get('lda', {})
            topics = lda_model.get('topics', [])
            if topics:
                topic_ids = [topic['topic_id'] for topic in topics]
                topic_weights = [topic['topic_weight'] for topic in topics]
                
                fig.add_trace(
                    go.Bar(x=topic_ids, y=topic_weights, name='Topic Weights'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Análisis de Sentimientos en Tiempo Real",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_sentiment_analysis(self, filename='realtime_sentiment_analysis.json'):
        """Exportar análisis de sentimientos"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'sentiment_data': self.sentiment_data,
            'sentiment_trends': self.sentiment_trends,
            'topic_models': self.topic_models,
            'alert_system': self.alert_system,
            'summary': {
                'total_analyses': len(self.sentiment_data),
                'trends_analyzed': len(self.sentiment_trends),
                'alerts_generated': len(self.alert_system.get('sentiment_alerts', [])),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de sentimientos exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de sentimientos
    sentiment_analyzer = RealtimeSentimentAnalyzer()
    
    # Textos de ejemplo para análisis
    sample_texts = [
        "I love this product! It's amazing and works perfectly.",
        "This service is terrible. I'm very disappointed with the quality.",
        "The product is okay, nothing special but it works.",
        "Excellent customer service! They were very helpful.",
        "I hate this company. Worst experience ever!",
        "Great value for money. Highly recommended!",
        "The delivery was slow but the product is good.",
        "Outstanding quality and fast shipping. Will buy again!",
        "Poor customer support. They don't respond to emails.",
        "Fantastic experience! Everything was perfect."
    ]
    
    # Analizar sentimientos
    print("😊 Analizando sentimientos en tiempo real...")
    sentiment_results = []
    
    for i, text in enumerate(sample_texts):
        analysis = sentiment_analyzer.analyze_text_sentiment(text, f'source_{i}')
        if analysis:
            sentiment_results.append(analysis)
    
    # Analizar tendencias
    print("📈 Analizando tendencias de sentimiento...")
    trends = sentiment_analyzer.analyze_sentiment_trends(sentiment_results, '24h')
    
    # Construir modelo de temas
    print("🎯 Construyendo modelo de temas...")
    topic_model = sentiment_analyzer.build_topic_model(sentiment_results)
    
    # Detectar alertas
    print("🚨 Detectando alertas de sentimiento...")
    alerts = sentiment_analyzer.detect_sentiment_alerts(sentiment_results)
    
    # Crear dashboard
    print("📊 Creando dashboard de sentimientos...")
    dashboard = sentiment_analyzer.create_sentiment_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de sentimientos...")
    export_data = sentiment_analyzer.export_sentiment_analysis()
    
    print("✅ Sistema de análisis de sentimientos en tiempo real completado!")




