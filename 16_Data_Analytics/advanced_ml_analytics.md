# 🧠 Analytics Avanzados con Machine Learning Mejorado - Outreach Morningscore

## 🎯 Sistema de Predicción de Éxito Avanzado

### 🤖 Modelo de Machine Learning Mejorado para Predicción de Respuesta

#### Dataset de Entrenamiento
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Dataset de características del contacto
contact_features = {
    'role': ['CEO', 'Marketing', 'Content', 'Other'],
    'company_size': ['Startup', 'SME', 'Enterprise'],
    'location': ['Denmark', 'Europe', 'Global'],
    'previous_interactions': [0, 1, 2, 3, 4, 5],
    'email_opens': [0, 1, 2, 3, 4, 5],
    'linkedin_connections': [0, 1, 2, 3, 4, 5],
    'response_time_hours': [0, 24, 48, 72, 168, 336],
    'sentiment_score': [-1, 0, 1],
    'urgency_level': [1, 2, 3, 4, 5],
    'personalization_score': [1, 2, 3, 4, 5]
}

# Dataset de resultados
outcomes = {
    'response_received': [0, 1],
    'positive_response': [0, 1],
    'meeting_scheduled': [0, 1],
    'proposal_accepted': [0, 1],
    'contract_signed': [0, 1]
}

def create_ml_model():
    """
    Crea un modelo de machine learning para predecir el éxito del outreach
    """
    # Cargar datos históricos
    df = pd.read_csv('outreach_data.csv')
    
    # Preparar características
    X = df[['role', 'company_size', 'location', 'previous_interactions', 
            'email_opens', 'linkedin_connections', 'response_time_hours',
            'sentiment_score', 'urgency_level', 'personalization_score']]
    
    # Preparar variable objetivo
    y = df['response_received']
    
    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entrenar modelo
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluar modelo
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.2f}")
    print(classification_report(y_test, y_pred))
    
    return model

def predict_success(contact_data, model):
    """
    Predice la probabilidad de éxito para un contacto específico
    """
    # Preparar datos del contacto
    features = np.array([[
        contact_data['role'],
        contact_data['company_size'],
        contact_data['location'],
        contact_data['previous_interactions'],
        contact_data['email_opens'],
        contact_data['linkedin_connections'],
        contact_data['response_time_hours'],
        contact_data['sentiment_score'],
        contact_data['urgency_level'],
        contact_data['personalization_score']
    ]])
    
    # Hacer predicción
    probability = model.predict_proba(features)[0][1]
    
    return probability
```

#### Sistema de Scoring Inteligente
```python
class IntelligentScoringSystem:
    def __init__(self):
        self.base_score = 0
        self.factors = {
            'role_weight': {'CEO': 0.9, 'Marketing': 0.8, 'Content': 0.7, 'Other': 0.5},
            'company_size_weight': {'Enterprise': 0.9, 'SME': 0.7, 'Startup': 0.5},
            'location_weight': {'Denmark': 0.9, 'Europe': 0.7, 'Global': 0.5},
            'interaction_weight': {0: 0.3, 1: 0.5, 2: 0.7, 3: 0.8, 4: 0.9, 5: 1.0},
            'sentiment_weight': {-1: 0.2, 0: 0.5, 1: 0.9},
            'urgency_weight': {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.8, 5: 0.9},
            'personalization_weight': {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.8, 5: 0.9}
        }
    
    def calculate_score(self, contact_data):
        """
        Calcula el score inteligente para un contacto
        """
        score = 0
        
        # Factor de rol
        role_score = self.factors['role_weight'].get(contact_data['role'], 0.5)
        score += role_score * 25
        
        # Factor de tamaño de empresa
        size_score = self.factors['company_size_weight'].get(contact_data['company_size'], 0.5)
        score += size_score * 20
        
        # Factor de ubicación
        location_score = self.factors['location_weight'].get(contact_data['location'], 0.5)
        score += location_score * 15
        
        # Factor de interacciones previas
        interaction_score = self.factors['interaction_weight'].get(contact_data['previous_interactions'], 0.5)
        score += interaction_score * 15
        
        # Factor de sentimiento
        sentiment_score = self.factors['sentiment_weight'].get(contact_data['sentiment_score'], 0.5)
        score += sentiment_score * 10
        
        # Factor de urgencia
        urgency_score = self.factors['urgency_weight'].get(contact_data['urgency_level'], 0.5)
        score += urgency_score * 10
        
        # Factor de personalización
        personalization_score = self.factors['personalization_weight'].get(contact_data['personalization_score'], 0.5)
        score += personalization_score * 5
        
        return min(score, 100)  # Máximo 100 puntos
    
    def get_recommendations(self, contact_data, score):
        """
        Genera recomendaciones basadas en el score
        """
        recommendations = []
        
        if score >= 80:
            recommendations.append("Lead de alta prioridad - Contactar inmediatamente")
            recommendations.append("Usar template de alta personalización")
            recommendations.append("Programar llamada de seguimiento en 24 horas")
        elif score >= 60:
            recommendations.append("Lead de prioridad media - Contactar esta semana")
            recommendations.append("Usar template de personalización media")
            recommendations.append("Programar seguimiento en 3-5 días")
        elif score >= 40:
            recommendations.append("Lead de baja prioridad - Contactar cuando sea conveniente")
            recommendations.append("Usar template básico")
            recommendations.append("Programar seguimiento en 1-2 semanas")
        else:
            recommendations.append("Lead de muy baja prioridad - Considerar descartar")
            recommendations.append("Usar template genérico")
            recommendations.append("Seguimiento opcional")
        
        return recommendations
```

### Sistema de Análisis de Sentimiento Avanzado

#### Análisis de Sentimiento con NLP
```python
import nltk
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy

class AdvancedSentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.nlp = spacy.load("en_core_web_sm")
        
    def analyze_sentiment(self, text):
        """
        Analiza el sentimiento de un texto usando múltiples métodos
        """
        # Análisis con TextBlob
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment.polarity
        
        # Análisis con VADER
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # Análisis con spaCy
        doc = self.nlp(text)
        spacy_sentiment = self._analyze_spacy_sentiment(doc)
        
        # Combinar resultados
        combined_sentiment = self._combine_sentiments(
            textblob_sentiment, 
            vader_scores['compound'], 
            spacy_sentiment
        )
        
        return {
            'textblob': textblob_sentiment,
            'vader': vader_scores,
            'spacy': spacy_sentiment,
            'combined': combined_sentiment,
            'confidence': self._calculate_confidence(textblob_sentiment, vader_scores['compound'], spacy_sentiment)
        }
    
    def _analyze_spacy_sentiment(self, doc):
        """
        Analiza sentimiento usando spaCy
        """
        sentiment = 0
        for token in doc:
            if token.is_alpha:
                sentiment += token.sentiment
        return sentiment / len(doc) if len(doc) > 0 else 0
    
    def _combine_sentiments(self, textblob, vader, spacy):
        """
        Combina los resultados de diferentes analizadores
        """
        weights = {'textblob': 0.3, 'vader': 0.4, 'spacy': 0.3}
        combined = (textblob * weights['textblob'] + 
                   vader * weights['vader'] + 
                   spacy * weights['spacy'])
        return combined
    
    def _calculate_confidence(self, textblob, vader, spacy):
        """
        Calcula la confianza en el análisis de sentimiento
        """
        scores = [textblob, vader, spacy]
        variance = np.var(scores)
        confidence = 1 - variance
        return max(0, min(1, confidence))
```

### Sistema de Predicción de Timing Óptimo

#### Predicción de Mejor Momento para Contactar
```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import numpy as np

class OptimalTimingPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.label_encoders = {}
        
    def prepare_data(self, df):
        """
        Prepara los datos para el modelo de timing
        """
        # Codificar variables categóricas
        categorical_columns = ['role', 'company_size', 'location', 'timezone']
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[col + '_encoded'] = le.fit_transform(df[col])
                self.label_encoders[col] = le
        
        return df
    
    def train_model(self, df):
        """
        Entrena el modelo de predicción de timing
        """
        # Preparar datos
        df = self.prepare_data(df)
        
        # Características
        feature_columns = ['role_encoded', 'company_size_encoded', 'location_encoded', 
                          'timezone_encoded', 'hour_of_day', 'day_of_week', 'month']
        X = df[feature_columns]
        
        # Variable objetivo (tiempo de respuesta en horas)
        y = df['response_time_hours']
        
        # Entrenar modelo
        self.model.fit(X, y)
        
        return self.model
    
    def predict_optimal_timing(self, contact_data):
        """
        Predice el mejor momento para contactar
        """
        # Preparar datos del contacto
        features = np.array([[
            self.label_encoders['role'].transform([contact_data['role']])[0],
            self.label_encoders['company_size'].transform([contact_data['company_size']])[0],
            self.label_encoders['location'].transform([contact_data['location']])[0],
            self.label_encoders['timezone'].transform([contact_data['timezone']])[0],
            contact_data['hour_of_day'],
            contact_data['day_of_week'],
            contact_data['month']
        ]])
        
        # Hacer predicción
        optimal_time = self.model.predict(features)[0]
        
        return optimal_time
    
    def get_timing_recommendations(self, contact_data):
        """
        Genera recomendaciones de timing
        """
        optimal_time = self.predict_optimal_timing(contact_data)
        
        recommendations = []
        
        if optimal_time < 24:
            recommendations.append("Contactar inmediatamente - Alta probabilidad de respuesta rápida")
        elif optimal_time < 72:
            recommendations.append("Contactar en las próximas 24-48 horas")
        elif optimal_time < 168:
            recommendations.append("Contactar esta semana")
        else:
            recommendations.append("Contactar cuando sea conveniente - Baja probabilidad de respuesta rápida")
        
        return recommendations
```

### Sistema de Análisis de Patrones

#### Detección de Patrones en Respuestas
```python
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

class PatternAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=3, random_state=42)
        
    def analyze_response_patterns(self, df):
        """
        Analiza patrones en las respuestas
        """
        # Preparar datos
        features = ['response_time_hours', 'email_opens', 'linkedin_connections', 
                   'sentiment_score', 'personalization_score']
        X = df[features]
        
        # Escalar datos
        X_scaled = self.scaler.fit_transform(X)
        
        # Aplicar clustering
        clusters = self.kmeans.fit_predict(X_scaled)
        df['cluster'] = clusters
        
        # Analizar clusters
        cluster_analysis = self._analyze_clusters(df)
        
        return cluster_analysis
    
    def _analyze_clusters(self, df):
        """
        Analiza los clusters encontrados
        """
        cluster_analysis = {}
        
        for cluster_id in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster_id]
            
            analysis = {
                'size': len(cluster_data),
                'avg_response_time': cluster_data['response_time_hours'].mean(),
                'avg_sentiment': cluster_data['sentiment_score'].mean(),
                'avg_personalization': cluster_data['personalization_score'].mean(),
                'response_rate': cluster_data['response_received'].mean(),
                'characteristics': self._get_cluster_characteristics(cluster_data)
            }
            
            cluster_analysis[f'cluster_{cluster_id}'] = analysis
        
        return cluster_analysis
    
    def _get_cluster_characteristics(self, cluster_data):
        """
        Obtiene características específicas del cluster
        """
        characteristics = []
        
        if cluster_data['response_time_hours'].mean() < 24:
            characteristics.append("Respuesta rápida")
        elif cluster_data['response_time_hours'].mean() < 72:
            characteristics.append("Respuesta media")
        else:
            characteristics.append("Respuesta lenta")
        
        if cluster_data['sentiment_score'].mean() > 0.5:
            characteristics.append("Sentimiento positivo")
        elif cluster_data['sentiment_score'].mean() < -0.5:
            characteristics.append("Sentimiento negativo")
        else:
            characteristics.append("Sentimiento neutral")
        
        if cluster_data['personalization_score'].mean() > 3:
            characteristics.append("Alta personalización")
        else:
            characteristics.append("Baja personalización")
        
        return characteristics
```

### Dashboard de Analytics Avanzados

#### Dashboard Interactivo con ML
```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class MLDashboard:
    def __init__(self):
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        self.scoring_system = IntelligentScoringSystem()
        self.timing_predictor = OptimalTimingPredictor()
        self.pattern_analyzer = PatternAnalyzer()
    
    def create_dashboard(self):
        """
        Crea el dashboard interactivo
        """
        st.title("🚀 Outreach Analytics Dashboard - Morningscore")
        
        # Sidebar
        st.sidebar.title("Configuración")
        selected_metric = st.sidebar.selectbox(
            "Métrica Principal",
            ["Response Rate", "Sentiment Analysis", "Timing Prediction", "Pattern Analysis"]
        )
        
        # Métricas principales
        self._display_main_metrics()
        
        # Gráficos específicos
        if selected_metric == "Response Rate":
            self._display_response_rate_charts()
        elif selected_metric == "Sentiment Analysis":
            self._display_sentiment_charts()
        elif selected_metric == "Timing Prediction":
            self._display_timing_charts()
        elif selected_metric == "Pattern Analysis":
            self._display_pattern_charts()
        
        # Recomendaciones
        self._display_recommendations()
    
    def _display_main_metrics(self):
        """
        Muestra las métricas principales
        """
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Contacts", "150", "12%")
        
        with col2:
            st.metric("Response Rate", "18.5%", "3.2%")
        
        with col3:
            st.metric("Conversion Rate", "8.2%", "1.5%")
        
        with col4:
            st.metric("ML Score", "73.4", "5.1%")
    
    def _display_response_rate_charts(self):
        """
        Muestra gráficos de tasa de respuesta
        """
        st.subheader("📊 Response Rate Analysis")
        
        # Gráfico de respuesta por canal
        fig = px.bar(
            x=['Email', 'LinkedIn', 'Phone', 'Other'],
            y=[15.2, 22.1, 35.0, 8.5],
            title="Response Rate by Channel"
        )
        st.plotly_chart(fig)
        
        # Gráfico de tendencia temporal
        fig = px.line(
            x=pd.date_range('2024-01-01', periods=30, freq='D'),
            y=np.random.randn(30).cumsum() + 15,
            title="Response Rate Trend"
        )
        st.plotly_chart(fig)
    
    def _display_sentiment_charts(self):
        """
        Muestra gráficos de análisis de sentimiento
        """
        st.subheader("😊 Sentiment Analysis")
        
        # Distribución de sentimientos
        fig = px.pie(
            values=[45, 35, 20],
            names=['Positive', 'Neutral', 'Negative'],
            title="Sentiment Distribution"
        )
        st.plotly_chart(fig)
        
        # Sentimiento por rol
        fig = px.bar(
            x=['CEO', 'Marketing', 'Content', 'Other'],
            y=[0.6, 0.4, 0.3, 0.2],
            title="Sentiment by Role"
        )
        st.plotly_chart(fig)
    
    def _display_timing_charts(self):
        """
        Muestra gráficos de predicción de timing
        """
        st.subheader("⏰ Timing Prediction")
        
        # Mejor hora para contactar
        fig = px.bar(
            x=['9 AM', '10 AM', '11 AM', '2 PM', '3 PM', '4 PM'],
            y=[0.8, 0.9, 0.7, 0.6, 0.8, 0.5],
            title="Optimal Contact Time"
        )
        st.plotly_chart(fig)
        
        # Predicción de tiempo de respuesta
        fig = px.scatter(
            x=[1, 2, 3, 4, 5],
            y=[24, 48, 72, 96, 120],
            title="Predicted Response Time"
        )
        st.plotly_chart(fig)
    
    def _display_pattern_charts(self):
        """
        Muestra gráficos de análisis de patrones
        """
        st.subheader("🔍 Pattern Analysis")
        
        # Clusters de contactos
        fig = px.scatter(
            x=[1, 2, 3, 4, 5],
            y=[0.8, 0.6, 0.4, 0.2, 0.1],
            color=['Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4', 'Cluster 5'],
            title="Contact Clusters"
        )
        st.plotly_chart(fig)
    
    def _display_recommendations(self):
        """
        Muestra recomendaciones basadas en ML
        """
        st.subheader("🎯 ML Recommendations")
        
        recommendations = [
            "Focus on LinkedIn outreach - 22% higher response rate",
            "Contact CEOs between 9-10 AM for best results",
            "Increase personalization score to 4+ for better outcomes",
            "Follow up within 48 hours for optimal conversion",
            "Use positive sentiment templates for better engagement"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
```

### Sistema de Alertas Inteligentes

#### Alertas Basadas en ML
```python
class IntelligentAlerts:
    def __init__(self):
        self.alert_thresholds = {
            'response_rate': 0.15,
            'sentiment_score': -0.3,
            'conversion_rate': 0.05,
            'response_time': 168  # 7 days
        }
    
    def check_alerts(self, current_metrics):
        """
        Verifica si se deben activar alertas
        """
        alerts = []
        
        # Alerta de tasa de respuesta baja
        if current_metrics['response_rate'] < self.alert_thresholds['response_rate']:
            alerts.append({
                'type': 'warning',
                'message': f"Response rate ({current_metrics['response_rate']:.1%}) is below threshold",
                'action': 'Review email templates and personalization'
            })
        
        # Alerta de sentimiento negativo
        if current_metrics['sentiment_score'] < self.alert_thresholds['sentiment_score']:
            alerts.append({
                'type': 'error',
                'message': f"Negative sentiment detected ({current_metrics['sentiment_score']:.2f})",
                'action': 'Review recent communications and adjust approach'
            })
        
        # Alerta de tasa de conversión baja
        if current_metrics['conversion_rate'] < self.alert_thresholds['conversion_rate']:
            alerts.append({
                'type': 'warning',
                'message': f"Conversion rate ({current_metrics['conversion_rate']:.1%}) is below threshold",
                'action': 'Review follow-up process and qualification criteria'
            })
        
        # Alerta de tiempo de respuesta alto
        if current_metrics['avg_response_time'] > self.alert_thresholds['response_time']:
            alerts.append({
                'type': 'info',
                'message': f"Average response time ({current_metrics['avg_response_time']:.0f} hours) is high",
                'action': 'Consider increasing follow-up frequency'
            })
        
        return alerts
    
    def send_alert(self, alert):
        """
        Envía una alerta
        """
        # Enviar a Slack
        self._send_slack_alert(alert)
        
        # Enviar email
        self._send_email_alert(alert)
        
        # Registrar en log
        self._log_alert(alert)
    
    def _send_slack_alert(self, alert):
        """
        Envía alerta a Slack
        """
        message = f"🚨 {alert['type'].upper()}: {alert['message']}\n💡 Action: {alert['action']}"
        # Implementar envío a Slack
    
    def _send_email_alert(self, alert):
        """
        Envía alerta por email
        """
        subject = f"Outreach Alert: {alert['type'].upper()}"
        body = f"{alert['message']}\n\nRecommended Action: {alert['action']}"
        # Implementar envío de email
    
    def _log_alert(self, alert):
        """
        Registra alerta en log
        """
        timestamp = pd.Timestamp.now()
        log_entry = f"{timestamp}: {alert['type']} - {alert['message']}"
        # Implementar logging
```

## Checklist de Implementación ML

### Fase 1: Configuración Inicial
- [ ] Instalar librerías de ML (scikit-learn, pandas, numpy)
- [ ] Configurar base de datos para datos históricos
- [ ] Implementar sistema de scoring básico
- [ ] Crear dashboard básico
- [ ] Configurar alertas simples

### Fase 2: Implementación Avanzada
- [ ] Implementar modelos de predicción
- [ ] Configurar análisis de sentimiento
- [ ] Crear sistema de timing óptimo
- [ ] Implementar análisis de patrones
- [ ] Configurar alertas inteligentes

### Fase 3: Optimización
- [ ] Entrenar modelos con datos reales
- [ ] Ajustar parámetros de ML
- [ ] Optimizar dashboard
- [ ] Refinar alertas
- [ ] Escalar sistema


