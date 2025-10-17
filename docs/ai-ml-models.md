# 🤖 Modelos de IA/ML - ClickUp Brain

## Visión General

Esta guía detalla los modelos de inteligencia artificial y machine learning utilizados en ClickUp Brain, incluyendo arquitecturas, entrenamiento, optimización y deployment de modelos especializados para análisis estratégico.

## 🧠 Arquitectura de Modelos

### Stack Tecnológico de IA/ML

```yaml
ai_ml_stack:
  frameworks:
    - "TensorFlow 2.x - Modelos de deep learning"
    - "PyTorch - Investigación y prototipado"
    - "Scikit-learn - Modelos clásicos de ML"
    - "Transformers - Modelos de lenguaje natural"
    - "ONNX - Optimización y deployment"
  
  infrastructure:
    - "Kubernetes - Orquestación de modelos"
    - "MLflow - Gestión del ciclo de vida"
    - "Kubeflow - Pipelines de ML"
    - "Seldon Core - Serving de modelos"
    - "Prometheus - Monitoreo de modelos"
  
  data_processing:
    - "Apache Spark - Procesamiento de big data"
    - "Apache Kafka - Streaming de datos"
    - "Apache Airflow - Orquestación de workflows"
    - "Dask - Computación paralela"
    - "Ray - Computación distribuida"
```

## 🎯 Modelos Especializados

### Modelo de Predicción de Éxito Estratégico

```python
# strategic_success_predictor.py
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
from typing import Dict, List, Any, Tuple
import mlflow
import mlflow.tensorflow

class StrategicSuccessPredictor:
    """Modelo de deep learning para predecir éxito de oportunidades estratégicas."""
    
    def __init__(self, input_dim: int = 50, hidden_layers: List[int] = [128, 64, 32]):
        self.input_dim = input_dim
        self.hidden_layers = hidden_layers
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_importance = None
        
    def build_model(self) -> tf.keras.Model:
        """Construir arquitectura del modelo de deep learning."""
        
        # Input layer
        inputs = layers.Input(shape=(self.input_dim,), name='strategic_features')
        
        # Hidden layers con dropout para regularización
        x = inputs
        for i, units in enumerate(self.hidden_layers):
            x = layers.Dense(units, activation='relu', name=f'hidden_{i+1}')(x)
            x = layers.BatchNormalization(name=f'batch_norm_{i+1}')(x)
            x = layers.Dropout(0.3, name=f'dropout_{i+1}')(x)
        
        # Output layer para predicción de éxito (0-1)
        success_output = layers.Dense(1, activation='sigmoid', name='success_probability')(x)
        
        # Output layer para predicción de impacto (0-100)
        impact_output = layers.Dense(1, activation='linear', name='impact_score')(x)
        
        # Output layer para predicción de timeline (días)
        timeline_output = layers.Dense(1, activation='relu', name='timeline_days')(x)
        
        # Crear modelo multi-output
        model = models.Model(
            inputs=inputs,
            outputs=[success_output, impact_output, timeline_output],
            name='StrategicSuccessPredictor'
        )
        
        # Compilar modelo con optimizador Adam y learning rate adaptativo
        optimizer = optimizers.Adam(learning_rate=0.001)
        
        model.compile(
            optimizer=optimizer,
            loss={
                'success_probability': 'binary_crossentropy',
                'impact_score': 'mse',
                'timeline_days': 'mse'
            },
            loss_weights={
                'success_probability': 1.0,
                'impact_score': 0.5,
                'timeline_days': 0.3
            },
            metrics={
                'success_probability': ['accuracy', 'precision', 'recall'],
                'impact_score': ['mae', 'mse'],
                'timeline_days': ['mae', 'mse']
            }
        )
        
        return model
    
    def prepare_training_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Preparar datos de entrenamiento."""
        
        # Features estratégicas
        feature_columns = [
            'market_size', 'competition_level', 'customer_demand',
            'technology_readiness', 'regulatory_environment', 'economic_indicators',
            'team_expertise', 'budget_allocation', 'timeline_realism',
            'stakeholder_support', 'risk_factors', 'market_maturity',
            'competitive_advantage', 'resource_availability', 'market_trend',
            'customer_satisfaction', 'brand_strength', 'innovation_level',
            'partnership_potential', 'scalability', 'profitability',
            'market_penetration', 'customer_acquisition_cost', 'lifetime_value',
            'churn_rate', 'growth_rate', 'market_share', 'revenue_potential',
            'cost_structure', 'operational_efficiency', 'technology_stack',
            'data_quality', 'analytics_capability', 'automation_level',
            'compliance_score', 'security_level', 'integration_complexity',
            'change_management', 'training_requirements', 'support_structure',
            'vendor_relationships', 'supply_chain', 'logistics',
            'geographic_reach', 'cultural_factors', 'language_barriers',
            'time_zone_coverage', 'local_regulations', 'tax_implications'
        ]
        
        # Target variables
        target_columns = {
            'success_probability': 'success_probability',
            'impact_score': 'impact_score',
            'timeline_days': 'timeline_days'
        }
        
        # Limpiar y preparar features
        X = data[feature_columns].fillna(data[feature_columns].median())
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Preparar targets
        y = {}
        for target_name, column_name in target_columns.items():
            y[target_name] = data[column_name].fillna(data[column_name].median()).values
        
        return X_scaled, y
    
    def train_model(self, data: pd.DataFrame, validation_split: float = 0.2, epochs: int = 100):
        """Entrenar modelo con datos históricos."""
        
        # Preparar datos
        X, y = self.prepare_training_data(data)
        
        # Dividir datos
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Construir modelo
        self.model = self.build_model()
        
        # Callbacks para entrenamiento
        callbacks_list = [
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            ),
            callbacks.ModelCheckpoint(
                'models/strategic_success_predictor_best.h5',
                monitor='val_loss',
                save_best_only=True
            )
        ]
        
        # Entrenar modelo
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32,
            callbacks=callbacks_list,
            verbose=1
        )
        
        # Calcular feature importance
        self.calculate_feature_importance(X, y)
        
        return history
    
    def calculate_feature_importance(self, X: np.ndarray, y: Dict[str, np.ndarray]):
        """Calcular importancia de features usando SHAP."""
        
        try:
            import shap
            
            # Crear explainer
            explainer = shap.DeepExplainer(self.model, X[:100])
            
            # Calcular shap values
            shap_values = explainer.shap_values(X[:100])
            
            # Calcular importancia promedio
            self.feature_importance = np.mean(np.abs(shap_values[0]), axis=0)
            
        except ImportError:
            print("SHAP no disponible, usando importancia de gradientes")
            self.calculate_gradient_importance(X, y)
    
    def calculate_gradient_importance(self, X: np.ndarray, y: Dict[str, np.ndarray]):
        """Calcular importancia usando gradientes."""
        
        # Calcular gradientes
        with tf.GradientTape() as tape:
            inputs = tf.Variable(X[:100], dtype=tf.float32)
            predictions = self.model(inputs)
            loss = tf.reduce_mean(predictions[0])  # Usar solo success_probability
        
        gradients = tape.gradient(loss, inputs)
        self.feature_importance = np.mean(np.abs(gradients.numpy()), axis=0)
    
    def predict(self, features: np.ndarray) -> Dict[str, float]:
        """Hacer predicción con el modelo entrenado."""
        
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        # Normalizar features
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Hacer predicción
        predictions = self.model.predict(features_scaled)
        
        return {
            'success_probability': float(predictions[0][0]),
            'impact_score': float(predictions[1][0]),
            'timeline_days': float(predictions[2][0])
        }
    
    def save_model(self, path: str):
        """Guardar modelo y componentes."""
        
        # Guardar modelo
        self.model.save(f"{path}/model.h5")
        
        # Guardar scaler
        joblib.dump(self.scaler, f"{path}/scaler.pkl")
        
        # Guardar feature importance
        if self.feature_importance is not None:
            np.save(f"{path}/feature_importance.npy", self.feature_importance)
        
        # Guardar metadatos
        metadata = {
            'input_dim': self.input_dim,
            'hidden_layers': self.hidden_layers,
            'feature_columns': self.get_feature_columns()
        }
        
        import json
        with open(f"{path}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_model(self, path: str):
        """Cargar modelo y componentes."""
        
        # Cargar modelo
        self.model = tf.keras.models.load_model(f"{path}/model.h5")
        
        # Cargar scaler
        self.scaler = joblib.load(f"{path}/scaler.pkl")
        
        # Cargar feature importance
        try:
            self.feature_importance = np.load(f"{path}/feature_importance.npy")
        except FileNotFoundError:
            self.feature_importance = None
        
        # Cargar metadatos
        import json
        with open(f"{path}/metadata.json", 'r') as f:
            metadata = json.load(f)
            self.input_dim = metadata['input_dim']
            self.hidden_layers = metadata['hidden_layers']
```

### Modelo de Análisis de Sentimientos Empresariales

```python
# business_sentiment_analyzer.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import numpy as np
from typing import Dict, List, Any, Tuple
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class BusinessSentimentAnalyzer:
    """Modelo especializado en análisis de sentimientos empresariales."""
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer
        )
        
        # Analizadores adicionales
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Diccionario de sentimientos empresariales
        self.business_lexicon = self.load_business_lexicon()
        
        # Modelo personalizado para contexto empresarial
        self.business_context_model = self.load_business_context_model()
    
    def load_business_lexicon(self) -> Dict[str, List[str]]:
        """Cargar diccionario de sentimientos empresariales."""
        
        return {
            'positive_business': [
                'growth', 'profit', 'success', 'opportunity', 'expansion',
                'innovation', 'breakthrough', 'achievement', 'milestone',
                'competitive advantage', 'market leadership', 'revenue growth',
                'customer satisfaction', 'brand recognition', 'market share',
                'efficiency', 'productivity', 'optimization', 'transformation',
                'digitalization', 'automation', 'scalability', 'sustainability'
            ],
            'negative_business': [
                'loss', 'decline', 'risk', 'threat', 'competition',
                'challenge', 'obstacle', 'failure', 'setback', 'crisis',
                'market share loss', 'revenue decline', 'competitive pressure',
                'customer churn', 'brand damage', 'reputation risk',
                'inefficiency', 'bottleneck', 'downtime', 'outage',
                'security breach', 'compliance violation', 'regulatory risk'
            ],
            'neutral_business': [
                'market', 'strategy', 'analysis', 'planning', 'execution',
                'process', 'system', 'framework', 'methodology', 'approach',
                'implementation', 'deployment', 'integration', 'migration',
                'assessment', 'evaluation', 'review', 'audit', 'compliance'
            ]
        }
    
    def load_business_context_model(self):
        """Cargar modelo personalizado para contexto empresarial."""
        
        try:
            # Modelo fine-tuned para sentimientos empresariales
            business_model = AutoModelForSequenceClassification.from_pretrained(
                "nlptown/bert-base-multilingual-uncased-sentiment"
            )
            business_tokenizer = AutoTokenizer.from_pretrained(
                "nlptown/bert-base-multilingual-uncased-sentiment"
            )
            
            return pipeline(
                "sentiment-analysis",
                model=business_model,
                tokenizer=business_tokenizer
            )
        except Exception as e:
            print(f"Error cargando modelo de contexto empresarial: {e}")
            return None
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analizar sentimiento de texto empresarial."""
        
        # Limpiar texto
        cleaned_text = self.clean_text(text)
        
        # Análisis con modelo principal
        main_sentiment = self.sentiment_pipeline(cleaned_text)[0]
        
        # Análisis con VADER
        vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
        
        # Análisis con TextBlob
        blob = TextBlob(cleaned_text)
        textblob_sentiment = {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
        
        # Análisis de contexto empresarial
        business_sentiment = self.analyze_business_context(cleaned_text)
        
        # Análisis de emociones
        emotions = self.analyze_emotions(cleaned_text)
        
        # Combinar resultados
        combined_sentiment = self.combine_sentiment_analysis(
            main_sentiment, vader_scores, textblob_sentiment, 
            business_sentiment, emotions
        )
        
        return {
            'text': text,
            'cleaned_text': cleaned_text,
            'main_sentiment': main_sentiment,
            'vader_scores': vader_scores,
            'textblob_sentiment': textblob_sentiment,
            'business_sentiment': business_sentiment,
            'emotions': emotions,
            'combined_sentiment': combined_sentiment
        }
    
    def analyze_business_context(self, text: str) -> Dict[str, Any]:
        """Analizar contexto empresarial del texto."""
        
        # Contar palabras clave empresariales
        keyword_scores = {}
        for sentiment, keywords in self.business_lexicon.items():
            count = sum(1 for keyword in keywords if keyword.lower() in text.lower())
            keyword_scores[sentiment] = count
        
        # Análisis de contexto específico
        context_analysis = {
            'financial_context': self.analyze_financial_context(text),
            'strategic_context': self.analyze_strategic_context(text),
            'operational_context': self.analyze_operational_context(text),
            'market_context': self.analyze_market_context(text)
        }
        
        # Análisis de urgencia
        urgency_score = self.analyze_urgency(text)
        
        return {
            'keyword_scores': keyword_scores,
            'context_analysis': context_analysis,
            'urgency_score': urgency_score
        }
    
    def analyze_financial_context(self, text: str) -> Dict[str, float]:
        """Analizar contexto financiero."""
        
        financial_patterns = {
            'revenue': r'\b(?:revenue|income|sales|earnings|profit)\b',
            'costs': r'\b(?:cost|expense|budget|investment|spending)\b',
            'growth': r'\b(?:growth|increase|rise|expansion|scaling)\b',
            'decline': r'\b(?:decline|decrease|fall|reduction|cutback)\b'
        }
        
        context_scores = {}
        for context, pattern in financial_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            context_scores[context] = matches / len(text.split()) if text.split() else 0
        
        return context_scores
    
    def analyze_strategic_context(self, text: str) -> Dict[str, float]:
        """Analizar contexto estratégico."""
        
        strategic_patterns = {
            'planning': r'\b(?:strategy|plan|roadmap|vision|mission)\b',
            'execution': r'\b(?:implementation|execution|deployment|rollout)\b',
            'analysis': r'\b(?:analysis|assessment|evaluation|review)\b',
            'decision': r'\b(?:decision|choice|selection|option)\b'
        }
        
        context_scores = {}
        for context, pattern in strategic_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            context_scores[context] = matches / len(text.split()) if text.split() else 0
        
        return context_scores
    
    def analyze_operational_context(self, text: str) -> Dict[str, float]:
        """Analizar contexto operacional."""
        
        operational_patterns = {
            'process': r'\b(?:process|workflow|procedure|method)\b',
            'efficiency': r'\b(?:efficiency|productivity|optimization|streamline)\b',
            'quality': r'\b(?:quality|standard|benchmark|performance)\b',
            'automation': r'\b(?:automation|digital|technology|system)\b'
        }
        
        context_scores = {}
        for context, pattern in operational_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            context_scores[context] = matches / len(text.split()) if text.split() else 0
        
        return context_scores
    
    def analyze_market_context(self, text: str) -> Dict[str, float]:
        """Analizar contexto de mercado."""
        
        market_patterns = {
            'competition': r'\b(?:competition|competitor|market share|positioning)\b',
            'customer': r'\b(?:customer|client|user|buyer|stakeholder)\b',
            'product': r'\b(?:product|service|offering|solution)\b',
            'trend': r'\b(?:trend|market|industry|sector)\b'
        }
        
        context_scores = {}
        for context, pattern in market_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            context_scores[context] = matches / len(text.split()) if text.split() else 0
        
        return context_scores
    
    def analyze_urgency(self, text: str) -> float:
        """Analizar urgencia del texto."""
        
        urgency_patterns = [
            r'\b(?:urgent|critical|immediate|asap|emergency)\b',
            r'\b(?:deadline|due date|timeline|schedule)\b',
            r'\b(?:priority|important|essential|crucial)\b',
            r'\b(?:quickly|rapidly|fast|speed)\b'
        ]
        
        urgency_score = 0
        for pattern in urgency_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            urgency_score += matches
        
        # Normalizar por longitud del texto
        return urgency_score / len(text.split()) if text.split() else 0
    
    def analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analizar emociones específicas."""
        
        emotion_lexicon = {
            'confidence': ['confident', 'certain', 'assured', 'positive', 'optimistic'],
            'concern': ['worried', 'concerned', 'uncertain', 'doubtful', 'apprehensive'],
            'excitement': ['excited', 'enthusiastic', 'thrilled', 'eager', 'motivated'],
            'frustration': ['frustrated', 'disappointed', 'annoyed', 'irritated', 'upset'],
            'satisfaction': ['satisfied', 'pleased', 'content', 'happy', 'delighted']
        }
        
        emotion_scores = {}
        for emotion, words in emotion_lexicon.items():
            count = sum(1 for word in words if word.lower() in text.lower())
            emotion_scores[emotion] = count / len(words)
        
        return emotion_scores
    
    def combine_sentiment_analysis(self, main_sentiment: Dict, vader_scores: Dict, 
                                 textblob_sentiment: Dict, business_sentiment: Dict, 
                                 emotions: Dict) -> Dict[str, Any]:
        """Combinar múltiples análisis de sentimiento."""
        
        # Ponderar diferentes métodos
        weights = {
            'main_model': 0.4,
            'vader': 0.2,
            'textblob': 0.1,
            'business_context': 0.2,
            'emotions': 0.1
        }
        
        # Calcular score combinado
        main_score = main_sentiment['score'] if main_sentiment['label'] == 'POSITIVE' else -main_sentiment['score']
        vader_score = vader_scores['compound']
        textblob_score = textblob_sentiment['polarity']
        
        # Score de contexto empresarial
        business_score = self.calculate_business_sentiment_score(business_sentiment)
        
        # Score de emociones
        emotion_score = self.calculate_emotion_score(emotions)
        
        # Combinar scores
        combined_polarity = (
            main_score * weights['main_model'] +
            vader_score * weights['vader'] +
            textblob_score * weights['textblob'] +
            business_score * weights['business_context'] +
            emotion_score * weights['emotions']
        )
        
        # Determinar sentimiento general
        if combined_polarity > 0.1:
            overall_sentiment = 'positive'
        elif combined_polarity < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'combined_polarity': combined_polarity,
            'confidence': abs(combined_polarity),
            'weights_used': weights,
            'detailed_scores': {
                'main_model': main_score,
                'vader': vader_score,
                'textblob': textblob_score,
                'business_context': business_score,
                'emotions': emotion_score
            }
        }
    
    def calculate_business_sentiment_score(self, business_sentiment: Dict) -> float:
        """Calcular score de sentimiento empresarial."""
        
        keyword_scores = business_sentiment['keyword_scores']
        positive_score = keyword_scores.get('positive_business', 0)
        negative_score = keyword_scores.get('negative_business', 0)
        
        if positive_score + negative_score == 0:
            return 0.0
        
        return (positive_score - negative_score) / (positive_score + negative_score)
    
    def calculate_emotion_score(self, emotions: Dict) -> float:
        """Calcular score de emociones."""
        
        positive_emotions = emotions.get('confidence', 0) + emotions.get('excitement', 0) + emotions.get('satisfaction', 0)
        negative_emotions = emotions.get('concern', 0) + emotions.get('frustration', 0)
        
        if positive_emotions + negative_emotions == 0:
            return 0.0
        
        return (positive_emotions - negative_emotions) / (positive_emotions + negative_emotions)
    
    def clean_text(self, text: str) -> str:
        """Limpiar texto para análisis."""
        
        # Remover caracteres especiales
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Convertir a minúsculas
        text = text.lower().strip()
        
        return text
```

### Modelo de Clustering de Oportunidades

```python
# opportunity_clustering.py
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class OpportunityClustering:
    """Modelo de clustering para agrupar oportunidades estratégicas similares."""
    
    def __init__(self, n_clusters: int = 5, algorithm: str = 'kmeans'):
        self.n_clusters = n_clusters
        self.algorithm = algorithm
        self.model = None
        self.scaler = StandardScaler()
        self.pca = None
        self.cluster_centers = None
        self.cluster_labels = None
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Preparar features para clustering."""
        
        # Features numéricas
        numeric_features = [
            'market_size', 'competition_level', 'customer_demand',
            'technology_readiness', 'budget_allocation', 'timeline_realism',
            'success_probability', 'estimated_value', 'risk_score'
        ]
        
        # Features categóricas (convertir a numéricas)
        categorical_features = [
            'market_segment', 'priority', 'status', 'industry'
        ]
        
        # Preparar features numéricas
        X_numeric = data[numeric_features].fillna(data[numeric_features].median())
        
        # Preparar features categóricas
        X_categorical = pd.get_dummies(data[categorical_features], prefix=categorical_features)
        
        # Combinar features
        X = np.hstack([X_numeric.values, X_categorical.values])
        
        return X
    
    def fit_clustering_model(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Entrenar modelo de clustering."""
        
        # Preparar features
        X = self.prepare_features(data)
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Aplicar PCA para reducción de dimensionalidad
        self.pca = PCA(n_components=0.95)  # Mantener 95% de varianza
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Entrenar modelo de clustering
        if self.algorithm == 'kmeans':
            self.model = KMeans(n_clusters=self.n_clusters, random_state=42)
        elif self.algorithm == 'dbscan':
            self.model = DBSCAN(eps=0.5, min_samples=5)
        elif self.algorithm == 'agglomerative':
            self.model = AgglomerativeClustering(n_clusters=self.n_clusters)
        
        # Entrenar modelo
        self.cluster_labels = self.model.fit_predict(X_pca)
        
        # Calcular métricas de clustering
        metrics = self.calculate_clustering_metrics(X_pca, self.cluster_labels)
        
        # Analizar clusters
        cluster_analysis = self.analyze_clusters(data, self.cluster_labels)
        
        return {
            'cluster_labels': self.cluster_labels,
            'metrics': metrics,
            'cluster_analysis': cluster_analysis,
            'n_components_pca': self.pca.n_components_,
            'explained_variance_ratio': self.pca.explained_variance_ratio_
        }
    
    def calculate_clustering_metrics(self, X: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """Calcular métricas de calidad del clustering."""
        
        # Silhouette score
        silhouette_avg = silhouette_score(X, labels)
        
        # Calinski-Harabasz score
        calinski_score = calinski_harabasz_score(X, labels)
        
        # Número de clusters únicos
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        return {
            'silhouette_score': silhouette_avg,
            'calinski_harabasz_score': calinski_score,
            'n_clusters': n_clusters,
            'n_noise_points': list(labels).count(-1) if -1 in labels else 0
        }
    
    def analyze_clusters(self, data: pd.DataFrame, labels: np.ndarray) -> Dict[int, Dict[str, Any]]:
        """Analizar características de cada cluster."""
        
        cluster_analysis = {}
        
        for cluster_id in set(labels):
            if cluster_id == -1:  # Skip noise points
                continue
            
            # Obtener datos del cluster
            cluster_mask = labels == cluster_id
            cluster_data = data[cluster_mask]
            
            # Calcular estadísticas del cluster
            cluster_stats = {
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(data) * 100,
                'avg_success_probability': cluster_data['success_probability'].mean(),
                'avg_estimated_value': cluster_data['estimated_value'].mean(),
                'avg_risk_score': cluster_data['risk_score'].mean(),
                'most_common_market_segment': cluster_data['market_segment'].mode().iloc[0] if not cluster_data['market_segment'].mode().empty else 'Unknown',
                'most_common_priority': cluster_data['priority'].mode().iloc[0] if not cluster_data['priority'].mode().empty else 'Unknown',
                'avg_timeline_days': cluster_data['timeline_days'].mean()
            }
            
            cluster_analysis[cluster_id] = cluster_stats
        
        return cluster_analysis
    
    def predict_cluster(self, opportunity_data: Dict[str, Any]) -> int:
        """Predecir cluster para una nueva oportunidad."""
        
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        # Convertir a DataFrame
        df = pd.DataFrame([opportunity_data])
        
        # Preparar features
        X = self.prepare_features(df)
        
        # Normalizar
        X_scaled = self.scaler.transform(X)
        
        # Aplicar PCA
        X_pca = self.pca.transform(X_scaled)
        
        # Predecir cluster
        cluster = self.model.predict(X_pca)[0]
        
        return cluster
    
    def get_cluster_recommendations(self, cluster_id: int) -> List[Dict[str, Any]]:
        """Obtener recomendaciones para un cluster específico."""
        
        recommendations = []
        
        if cluster_id == 0:  # Cluster de alto valor, baja probabilidad
            recommendations = [
                {
                    'type': 'risk_mitigation',
                    'title': 'Reducir riesgos para aumentar probabilidad de éxito',
                    'description': 'Este cluster tiene alto valor pero baja probabilidad de éxito. Enfocarse en mitigación de riesgos.',
                    'actions': [
                        'Realizar análisis de riesgo detallado',
                        'Desarrollar planes de contingencia',
                        'Aumentar recursos para gestión de riesgos'
                    ]
                }
            ]
        elif cluster_id == 1:  # Cluster de alto valor, alta probabilidad
            recommendations = [
                {
                    'type': 'acceleration',
                    'title': 'Acelerar ejecución para maximizar valor',
                    'description': 'Este cluster tiene excelentes perspectivas. Priorizar recursos y acelerar timeline.',
                    'actions': [
                        'Asignar recursos adicionales',
                        'Acelerar timeline de ejecución',
                        'Expandir alcance de la oportunidad'
                    ]
                }
            ]
        elif cluster_id == 2:  # Cluster de bajo valor, alta probabilidad
            recommendations = [
                {
                    'type': 'value_optimization',
                    'title': 'Optimizar valor de la oportunidad',
                    'description': 'Este cluster tiene alta probabilidad pero bajo valor. Buscar formas de aumentar el valor.',
                    'actions': [
                        'Explorar oportunidades de expansión',
                        'Identificar productos/servicios adicionales',
                        'Considerar bundling con otras oportunidades'
                    ]
                }
            ]
        
        return recommendations
    
    def visualize_clusters(self, data: pd.DataFrame, labels: np.ndarray, save_path: str = None):
        """Visualizar clusters."""
        
        # Preparar features
        X = self.prepare_features(data)
        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.transform(X_scaled)
        
        # Crear visualización
        plt.figure(figsize=(12, 8))
        
        # Scatter plot de clusters
        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='viridis', alpha=0.7)
        plt.colorbar(scatter)
        
        # Agregar centroides si es KMeans
        if hasattr(self.model, 'cluster_centers_'):
            centers = self.pca.transform(self.scaler.transform(self.model.cluster_centers_))
            plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='x', s=200, linewidths=3)
        
        plt.title('Clustering de Oportunidades Estratégicas')
        plt.xlabel(f'PC1 ({self.pca.explained_variance_ratio_[0]:.2%} varianza)')
        plt.ylabel(f'PC2 ({self.pca.explained_variance_ratio_[1]:.2%} varianza)')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def optimize_number_of_clusters(self, data: pd.DataFrame, max_clusters: int = 10) -> Dict[str, Any]:
        """Optimizar número de clusters usando método del codo y silhouette."""
        
        X = self.prepare_features(data)
        X_scaled = self.scaler.fit_transform(X)
        
        # Método del codo
        inertias = []
        silhouette_scores = []
        k_range = range(2, max_clusters + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(X_scaled)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X_scaled, labels))
        
        # Encontrar número óptimo de clusters
        optimal_k = k_range[np.argmax(silhouette_scores)]
        
        return {
            'optimal_k': optimal_k,
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'k_range': list(k_range)
        }
```

## 🚀 Deployment y Serving de Modelos

### Sistema de Model Serving

```python
# model_serving.py
import mlflow
import mlflow.sklearn
import mlflow.tensorflow
from seldon_core import SeldonClient
import requests
import json
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from datetime import datetime
import logging

class ModelServingSystem:
    """Sistema de serving de modelos de IA/ML."""
    
    def __init__(self, mlflow_tracking_uri: str, seldon_endpoint: str):
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.seldon_endpoint = seldon_endpoint
        self.mlflow_client = mlflow.tracking.MlflowClient(tracking_uri=mlflow_tracking_uri)
        self.seldon_client = SeldonClient(seldon_endpoint)
        self.deployed_models = {}
        
    def deploy_model(self, model_name: str, model_version: str, 
                    deployment_config: Dict[str, Any]) -> str:
        """Desplegar modelo usando MLflow y Seldon."""
        
        try:
            # Obtener modelo de MLflow
            model_uri = f"models:/{model_name}/{model_version}"
            model = mlflow.sklearn.load_model(model_uri)
            
            # Crear deployment en Seldon
            deployment_name = f"{model_name}-{model_version}"
            
            deployment_spec = {
                "apiVersion": "machinelearning.seldon.io/v1",
                "kind": "SeldonDeployment",
                "metadata": {
                    "name": deployment_name,
                    "namespace": "clickup-brain"
                },
                "spec": {
                    "name": deployment_name,
                    "predictors": [
                        {
                            "name": "default",
                            "replicas": deployment_config.get('replicas', 1),
                            "graph": {
                                "name": "model",
                                "type": "MODEL",
                                "implementation": "SKLEARN_SERVER",
                                "modelUri": model_uri
                            }
                        }
                    ]
                }
            }
            
            # Desplegar modelo
            response = self.seldon_client.deploy(deployment_spec)
            
            if response.status_code == 200:
                self.deployed_models[deployment_name] = {
                    'model_name': model_name,
                    'model_version': model_version,
                    'deployment_name': deployment_name,
                    'status': 'deployed',
                    'deployed_at': datetime.now()
                }
                
                return deployment_name
            else:
                raise Exception(f"Error desplegando modelo: {response.text}")
                
        except Exception as e:
            logging.error(f"Error desplegando modelo {model_name}: {e}")
            raise e
    
    def predict(self, deployment_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hacer predicción usando modelo desplegado."""
        
        if deployment_name not in self.deployed_models:
            raise ValueError(f"Modelo {deployment_name} no está desplegado")
        
        try:
            # Preparar datos para predicción
            prediction_data = {
                "data": {
                    "ndarray": [list(input_data.values())]
                }
            }
            
            # Hacer predicción
            response = self.seldon_client.predict(
                deployment_name=deployment_name,
                data=prediction_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'prediction': result['data']['ndarray'][0],
                    'model_name': self.deployed_models[deployment_name]['model_name'],
                    'model_version': self.deployed_models[deployment_name]['model_version'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception(f"Error en predicción: {response.text}")
                
        except Exception as e:
            logging.error(f"Error haciendo predicción con {deployment_name}: {e}")
            raise e
    
    def batch_predict(self, deployment_name: str, input_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Hacer predicciones en lote."""
        
        if deployment_name not in self.deployed_models:
            raise ValueError(f"Modelo {deployment_name} no está desplegado")
        
        try:
            # Preparar datos para predicción en lote
            batch_data = []
            for data in input_data:
                batch_data.append(list(data.values()))
            
            prediction_data = {
                "data": {
                    "ndarray": batch_data
                }
            }
            
            # Hacer predicción en lote
            response = self.seldon_client.predict(
                deployment_name=deployment_name,
                data=prediction_data
            )
            
            if response.status_code == 200:
                result = response.json()
                predictions = result['data']['ndarray']
                
                return [
                    {
                        'prediction': pred,
                        'model_name': self.deployed_models[deployment_name]['model_name'],
                        'model_version': self.deployed_models[deployment_name]['model_version'],
                        'timestamp': datetime.now().isoformat()
                    }
                    for pred in predictions
                ]
            else:
                raise Exception(f"Error en predicción en lote: {response.text}")
                
        except Exception as e:
            logging.error(f"Error haciendo predicción en lote con {deployment_name}: {e}")
            raise e
    
    def get_model_metrics(self, deployment_name: str) -> Dict[str, Any]:
        """Obtener métricas del modelo desplegado."""
        
        try:
            # Obtener métricas de Seldon
            metrics_response = self.seldon_client.get_metrics(deployment_name)
            
            if metrics_response.status_code == 200:
                metrics = metrics_response.json()
                
                return {
                    'deployment_name': deployment_name,
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception(f"Error obteniendo métricas: {metrics_response.text}")
                
        except Exception as e:
            logging.error(f"Error obteniendo métricas de {deployment_name}: {e}")
            raise e
    
    def update_model(self, deployment_name: str, new_model_version: str) -> bool:
        """Actualizar modelo desplegado."""
        
        if deployment_name not in self.deployed_models:
            raise ValueError(f"Modelo {deployment_name} no está desplegado")
        
        try:
            # Obtener configuración actual
            current_config = self.deployed_models[deployment_name]
            
            # Actualizar modelo
            updated_config = current_config.copy()
            updated_config['model_version'] = new_model_version
            updated_config['updated_at'] = datetime.now()
            
            # Actualizar deployment en Seldon
            # (Implementar lógica de actualización)
            
            # Actualizar registro local
            self.deployed_models[deployment_name] = updated_config
            
            return True
            
        except Exception as e:
            logging.error(f"Error actualizando modelo {deployment_name}: {e}")
            return False
    
    def undeploy_model(self, deployment_name: str) -> bool:
        """Desplegar modelo."""
        
        if deployment_name not in self.deployed_models:
            raise ValueError(f"Modelo {deployment_name} no está desplegado")
        
        try:
            # Desplegar modelo en Seldon
            response = self.seldon_client.undeploy(deployment_name)
            
            if response.status_code == 200:
                # Remover de registro local
                del self.deployed_models[deployment_name]
                return True
            else:
                raise Exception(f"Error desplegando modelo: {response.text}")
                
        except Exception as e:
            logging.error(f"Error desplegando modelo {deployment_name}: {e}")
            return False
    
    def list_deployed_models(self) -> List[Dict[str, Any]]:
        """Listar modelos desplegados."""
        
        return list(self.deployed_models.values())
    
    def health_check(self, deployment_name: str) -> Dict[str, Any]:
        """Verificar salud del modelo desplegado."""
        
        try:
            # Hacer health check
            response = self.seldon_client.health_check(deployment_name)
            
            if response.status_code == 200:
                return {
                    'deployment_name': deployment_name,
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'deployment_name': deployment_name,
                    'status': 'unhealthy',
                    'error': response.text,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'deployment_name': deployment_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
```

---

Esta guía de modelos de IA/ML proporciona un framework completo para implementar, entrenar, optimizar y desplegar modelos especializados en ClickUp Brain, desde predicción de éxito estratégico hasta análisis de sentimientos empresariales y clustering de oportunidades.


