"""
Marketing Brain Marketing NLP Optimizer
Motor avanzado de optimización de NLP de marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Descargar recursos de NLTK
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class MarketingNLPOptimizer:
    def __init__(self):
        self.nlp_data = {}
        self.nlp_analysis = {}
        self.nlp_models = {}
        self.nlp_strategies = {}
        self.nlp_insights = {}
        self.nlp_recommendations = {}
        
    def load_nlp_data(self, nlp_data):
        """Cargar datos de NLP de marketing"""
        if isinstance(nlp_data, str):
            if nlp_data.endswith('.csv'):
                self.nlp_data = pd.read_csv(nlp_data)
            elif nlp_data.endswith('.json'):
                with open(nlp_data, 'r') as f:
                    data = json.load(f)
                self.nlp_data = pd.DataFrame(data)
        else:
            self.nlp_data = pd.DataFrame(nlp_data)
        
        print(f"✅ Datos de NLP de marketing cargados: {len(self.nlp_data)} registros")
        return True
    
    def analyze_nlp_capabilities(self):
        """Analizar capacidades de NLP"""
        if self.nlp_data.empty:
            return None
        
        # Análisis de técnicas de NLP
        nlp_techniques = self._analyze_nlp_techniques()
        
        # Análisis de modelos de NLP
        nlp_models = self._analyze_nlp_models()
        
        # Análisis de aplicaciones de NLP
        nlp_applications = self._analyze_nlp_applications()
        
        # Análisis de preprocesamiento de texto
        text_preprocessing = self._analyze_text_preprocessing()
        
        # Análisis de análisis de sentimientos
        sentiment_analysis = self._analyze_sentiment_analysis()
        
        # Análisis de extracción de características
        feature_extraction = self._analyze_feature_extraction()
        
        nlp_results = {
            'nlp_techniques': nlp_techniques,
            'nlp_models': nlp_models,
            'nlp_applications': nlp_applications,
            'text_preprocessing': text_preprocessing,
            'sentiment_analysis': sentiment_analysis,
            'feature_extraction': feature_extraction,
            'overall_nlp_assessment': self._calculate_overall_nlp_assessment()
        }
        
        self.nlp_analysis = nlp_results
        return nlp_results
    
    def _analyze_nlp_techniques(self):
        """Analizar técnicas de NLP"""
        technique_analysis = {}
        
        # Técnicas disponibles
        techniques = {
            'Tokenization': {
                'complexity': 2,
                'applicability': 5,
                'performance': 4,
                'interpretability': 4,
                'use_cases': ['Text Processing', 'Feature Extraction', 'Preprocessing']
            },
            'POS Tagging': {
                'complexity': 3,
                'applicability': 4,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Grammar Analysis', 'Feature Extraction', 'Text Understanding']
            },
            'Named Entity Recognition': {
                'complexity': 4,
                'applicability': 4,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Entity Extraction', 'Information Extraction', 'Knowledge Graphs']
            },
            'Sentiment Analysis': {
                'complexity': 3,
                'applicability': 5,
                'performance': 4,
                'interpretability': 4,
                'use_cases': ['Opinion Mining', 'Brand Monitoring', 'Customer Feedback']
            },
            'Text Classification': {
                'complexity': 3,
                'applicability': 5,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Content Categorization', 'Spam Detection', 'Topic Classification']
            },
            'Text Summarization': {
                'complexity': 4,
                'applicability': 4,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Content Summarization', 'Report Generation', 'Information Extraction']
            },
            'Machine Translation': {
                'complexity': 5,
                'applicability': 3,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Multilingual Content', 'Global Marketing', 'Localization']
            },
            'Text Generation': {
                'complexity': 5,
                'applicability': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Content Creation', 'Chatbots', 'Creative Writing']
            },
            'Question Answering': {
                'complexity': 4,
                'applicability': 4,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Customer Support', 'FAQ Systems', 'Information Retrieval']
            },
            'Topic Modeling': {
                'complexity': 3,
                'applicability': 4,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Content Analysis', 'Trend Detection', 'Market Research']
            }
        }
        
        technique_analysis['techniques'] = techniques
        technique_analysis['best_technique'] = self._select_best_nlp_technique(techniques)
        technique_analysis['recommendations'] = self._get_nlp_technique_recommendations(techniques)
        
        return technique_analysis
    
    def _select_best_nlp_technique(self, techniques):
        """Seleccionar mejor técnica de NLP"""
        best_technique = None
        best_score = 0
        
        for name, performance in techniques.items():
            # Calcular score combinado
            score = (performance['applicability'] * 0.3 + 
                    performance['performance'] * 0.3 + 
                    performance['interpretability'] * 0.2 + 
                    (6 - performance['complexity']) * 0.2)
            
            if score > best_score:
                best_score = score
                best_technique = name
        
        return best_technique
    
    def _get_nlp_technique_recommendations(self, techniques):
        """Obtener recomendaciones de técnicas de NLP"""
        recommendations = []
        
        # Recomendaciones basadas en aplicabilidad
        high_applicability_techniques = [name for name, perf in techniques.items() 
                                       if perf['applicability'] >= 4]
        if high_applicability_techniques:
            recommendations.append({
                'criteria': 'High Applicability',
                'techniques': high_applicability_techniques,
                'reason': 'Suitable for most marketing applications'
            })
        
        # Recomendaciones basadas en performance
        high_performance_techniques = [name for name, perf in techniques.items() 
                                     if perf['performance'] >= 4]
        if high_performance_techniques:
            recommendations.append({
                'criteria': 'High Performance',
                'techniques': high_performance_techniques,
                'reason': 'Excellent performance for complex tasks'
            })
        
        # Recomendaciones basadas en interpretabilidad
        high_interpretability_techniques = [name for name, perf in techniques.items() 
                                         if perf['interpretability'] >= 3]
        if high_interpretability_techniques:
            recommendations.append({
                'criteria': 'High Interpretability',
                'techniques': high_interpretability_techniques,
                'reason': 'Easier to understand and explain'
            })
        
        return recommendations
    
    def _analyze_nlp_models(self):
        """Analizar modelos de NLP"""
        model_analysis = {}
        
        # Análisis de modelos de clasificación
        classification_models = self._analyze_classification_models()
        model_analysis['classification'] = classification_models
        
        # Análisis de modelos de regresión
        regression_models = self._analyze_regression_models()
        model_analysis['regression'] = regression_models
        
        # Análisis de modelos de clustering
        clustering_models = self._analyze_clustering_models()
        model_analysis['clustering'] = clustering_models
        
        # Análisis de modelos de topic modeling
        topic_models = self._analyze_topic_models()
        model_analysis['topic_modeling'] = topic_models
        
        return model_analysis
    
    def _analyze_classification_models(self):
        """Analizar modelos de clasificación"""
        classification_analysis = {}
        
        # Modelos disponibles
        models = {
            'Naive Bayes': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 4,
                'use_cases': ['Text Classification', 'Spam Detection', 'Sentiment Analysis']
            },
            'Logistic Regression': {
                'complexity': 2,
                'performance': 4,
                'interpretability': 4,
                'use_cases': ['Text Classification', 'Binary Classification', 'Feature Analysis']
            },
            'Random Forest': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Text Classification', 'Feature Importance', 'Robust Classification']
            },
            'SVM': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Text Classification', 'High-dimensional Data', 'Non-linear Classification']
            },
            'Neural Networks': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 1,
                'use_cases': ['Complex Text Classification', 'Deep Learning', 'Feature Learning']
            }
        }
        
        classification_analysis['models'] = models
        classification_analysis['best_model'] = 'Logistic Regression'
        classification_analysis['recommendations'] = [
            'Use Logistic Regression for balanced performance and interpretability',
            'Use Naive Bayes for simple text classification tasks',
            'Use Random Forest for robust classification with feature importance'
        ]
        
        return classification_analysis
    
    def _analyze_regression_models(self):
        """Analizar modelos de regresión"""
        regression_analysis = {}
        
        # Modelos disponibles
        models = {
            'Linear Regression': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 4,
                'use_cases': ['Text Regression', 'Simple Relationships', 'Baseline Models']
            },
            'Ridge Regression': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 4,
                'use_cases': ['Text Regression', 'Regularized Regression', 'Overfitting Prevention']
            },
            'Lasso Regression': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 4,
                'use_cases': ['Text Regression', 'Feature Selection', 'Sparse Models']
            },
            'Random Forest': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Text Regression', 'Non-linear Relationships', 'Feature Importance']
            },
            'Neural Networks': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 1,
                'use_cases': ['Complex Text Regression', 'Deep Learning', 'Non-linear Relationships']
            }
        }
        
        regression_analysis['models'] = models
        regression_analysis['best_model'] = 'Random Forest'
        regression_analysis['recommendations'] = [
            'Use Random Forest for robust text regression',
            'Use Linear Regression for simple relationships',
            'Use Ridge Regression for regularized regression'
        ]
        
        return regression_analysis
    
    def _analyze_clustering_models(self):
        """Analizar modelos de clustering"""
        clustering_analysis = {}
        
        # Modelos disponibles
        models = {
            'K-Means': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Text Clustering', 'Document Grouping', 'Content Segmentation']
            },
            'Hierarchical Clustering': {
                'complexity': 3,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Text Clustering', 'Hierarchical Grouping', 'Dendrogram Analysis']
            },
            'DBSCAN': {
                'complexity': 3,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Text Clustering', 'Noise Detection', 'Density-based Clustering']
            },
            'Gaussian Mixture': {
                'complexity': 3,
                'performance': 3,
                'interpretability': 2,
                'use_cases': ['Text Clustering', 'Probabilistic Clustering', 'Soft Clustering']
            }
        }
        
        clustering_analysis['models'] = models
        clustering_analysis['best_model'] = 'K-Means'
        clustering_analysis['recommendations'] = [
            'Use K-Means for general text clustering',
            'Use Hierarchical Clustering for hierarchical grouping',
            'Use DBSCAN for noise detection and density-based clustering'
        ]
        
        return clustering_analysis
    
    def _analyze_topic_models(self):
        """Analizar modelos de topic modeling"""
        topic_analysis = {}
        
        # Modelos disponibles
        models = {
            'Latent Dirichlet Allocation (LDA)': {
                'complexity': 3,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Topic Discovery', 'Content Analysis', 'Document Clustering']
            },
            'Non-negative Matrix Factorization (NMF)': {
                'complexity': 3,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Topic Discovery', 'Feature Extraction', 'Dimensionality Reduction']
            },
            'Latent Semantic Analysis (LSA)': {
                'complexity': 2,
                'performance': 2,
                'interpretability': 3,
                'use_cases': ['Topic Discovery', 'Semantic Analysis', 'Dimensionality Reduction']
            },
            'BERTopic': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Advanced Topic Modeling', 'BERT-based Topics', 'Modern NLP']
            }
        }
        
        topic_analysis['models'] = models
        topic_analysis['best_model'] = 'Latent Dirichlet Allocation (LDA)'
        topic_analysis['recommendations'] = [
            'Use LDA for general topic modeling',
            'Use NMF for feature extraction and topic discovery',
            'Use BERTopic for advanced topic modeling with BERT'
        ]
        
        return topic_analysis
    
    def _analyze_nlp_applications(self):
        """Analizar aplicaciones de NLP"""
        application_analysis = {}
        
        # Aplicaciones disponibles
        applications = {
            'Chatbots': {
                'complexity': 4,
                'business_value': 5,
                'implementation_time': 3,
                'use_cases': ['Customer Support', 'Lead Generation', 'User Engagement']
            },
            'Content Generation': {
                'complexity': 5,
                'business_value': 4,
                'implementation_time': 4,
                'use_cases': ['Content Marketing', 'Copywriting', 'Creative Writing']
            },
            'Sentiment Analysis': {
                'complexity': 3,
                'business_value': 5,
                'implementation_time': 2,
                'use_cases': ['Brand Monitoring', 'Customer Feedback', 'Market Research']
            },
            'Text Summarization': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['Content Summarization', 'Report Generation', 'Information Extraction']
            },
            'Language Translation': {
                'complexity': 5,
                'business_value': 3,
                'implementation_time': 4,
                'use_cases': ['Global Marketing', 'Multilingual Content', 'Localization']
            },
            'Text Classification': {
                'complexity': 3,
                'business_value': 4,
                'implementation_time': 2,
                'use_cases': ['Content Categorization', 'Spam Detection', 'Topic Classification']
            },
            'Named Entity Recognition': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['Information Extraction', 'Knowledge Graphs', 'Entity Analysis']
            },
            'Question Answering': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['Customer Support', 'FAQ Systems', 'Information Retrieval']
            }
        }
        
        application_analysis['applications'] = applications
        application_analysis['best_application'] = 'Sentiment Analysis'
        application_analysis['recommendations'] = [
            'Start with Sentiment Analysis for immediate business value',
            'Implement Chatbots for customer engagement',
            'Consider Content Generation for marketing automation'
        ]
        
        return application_analysis
    
    def _analyze_text_preprocessing(self):
        """Analizar preprocesamiento de texto"""
        preprocessing_analysis = {}
        
        # Técnicas de preprocesamiento
        techniques = {
            'Tokenization': {
                'complexity': 1,
                'effectiveness': 4,
                'use_cases': ['Text Splitting', 'Word Analysis', 'Feature Extraction']
            },
            'Stop Words Removal': {
                'complexity': 1,
                'effectiveness': 3,
                'use_cases': ['Noise Reduction', 'Feature Selection', 'Text Cleaning']
            },
            'Stemming': {
                'complexity': 2,
                'effectiveness': 3,
                'use_cases': ['Word Normalization', 'Feature Reduction', 'Text Standardization']
            },
            'Lemmatization': {
                'complexity': 2,
                'effectiveness': 4,
                'use_cases': ['Word Normalization', 'Morphological Analysis', 'Text Standardization']
            },
            'Lowercasing': {
                'complexity': 1,
                'effectiveness': 3,
                'use_cases': ['Case Normalization', 'Text Standardization', 'Feature Consistency']
            },
            'Punctuation Removal': {
                'complexity': 1,
                'effectiveness': 3,
                'use_cases': ['Text Cleaning', 'Noise Reduction', 'Feature Extraction']
            },
            'Number Removal': {
                'complexity': 1,
                'effectiveness': 2,
                'use_cases': ['Text Cleaning', 'Feature Selection', 'Noise Reduction']
            },
            'Special Character Removal': {
                'complexity': 1,
                'effectiveness': 3,
                'use_cases': ['Text Cleaning', 'Noise Reduction', 'Feature Extraction']
            }
        }
        
        preprocessing_analysis['techniques'] = techniques
        preprocessing_analysis['best_technique'] = 'Lemmatization'
        preprocessing_analysis['recommendations'] = [
            'Use lemmatization for better word normalization',
            'Apply stop words removal for noise reduction',
            'Use tokenization for text splitting and analysis'
        ]
        
        return preprocessing_analysis
    
    def _analyze_sentiment_analysis(self):
        """Analizar análisis de sentimientos"""
        sentiment_analysis = {}
        
        # Técnicas de análisis de sentimientos
        techniques = {
            'VADER': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 4,
                'use_cases': ['Social Media Analysis', 'Real-time Sentiment', 'General Sentiment']
            },
            'TextBlob': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 4,
                'use_cases': ['Simple Sentiment Analysis', 'Polarity Analysis', 'Quick Analysis']
            },
            'Naive Bayes': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Text Classification', 'Sentiment Classification', 'Supervised Learning']
            },
            'Logistic Regression': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 4,
                'use_cases': ['Sentiment Classification', 'Binary Classification', 'Feature Analysis']
            },
            'Random Forest': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Sentiment Classification', 'Robust Classification', 'Feature Importance']
            },
            'BERT': {
                'complexity': 5,
                'performance': 5,
                'interpretability': 2,
                'use_cases': ['Advanced Sentiment Analysis', 'Contextual Understanding', 'State-of-the-art Performance']
            }
        }
        
        sentiment_analysis['techniques'] = techniques
        sentiment_analysis['best_technique'] = 'VADER'
        sentiment_analysis['recommendations'] = [
            'Use VADER for general sentiment analysis',
            'Use BERT for advanced contextual sentiment analysis',
            'Use Naive Bayes for supervised sentiment classification'
        ]
        
        return sentiment_analysis
    
    def _analyze_feature_extraction(self):
        """Analizar extracción de características"""
        feature_analysis = {}
        
        # Técnicas de extracción de características
        techniques = {
            'Bag of Words': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 4,
                'use_cases': ['Text Classification', 'Feature Extraction', 'Baseline Models']
            },
            'TF-IDF': {
                'complexity': 2,
                'performance': 4,
                'interpretability': 4,
                'use_cases': ['Text Classification', 'Feature Extraction', 'Document Similarity']
            },
            'Word Embeddings': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Semantic Analysis', 'Word Similarity', 'Feature Learning']
            },
            'N-grams': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Phrase Analysis', 'Context Preservation', 'Feature Extraction']
            },
            'Character N-grams': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 2,
                'use_cases': ['Spelling Variations', 'Morphological Analysis', 'Feature Extraction']
            },
            'POS Tagging': {
                'complexity': 3,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Grammar Analysis', 'Syntactic Features', 'Text Understanding']
            },
            'Named Entity Recognition': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Entity Extraction', 'Information Extraction', 'Knowledge Graphs']
            }
        }
        
        feature_analysis['techniques'] = techniques
        feature_analysis['best_technique'] = 'TF-IDF'
        feature_analysis['recommendations'] = [
            'Use TF-IDF for general feature extraction',
            'Use Word Embeddings for semantic analysis',
            'Use N-grams for phrase and context analysis'
        ]
        
        return feature_analysis
    
    def _calculate_overall_nlp_assessment(self):
        """Calcular evaluación general de NLP"""
        overall_assessment = {}
        
        if not self.nlp_data.empty:
            overall_assessment = {
                'nlp_maturity_level': self._calculate_nlp_maturity_level(),
                'nlp_readiness_score': self._calculate_nlp_readiness_score(),
                'nlp_implementation_priority': self._calculate_nlp_implementation_priority(),
                'nlp_roi_potential': self._calculate_nlp_roi_potential()
            }
        
        return overall_assessment
    
    def _calculate_nlp_maturity_level(self):
        """Calcular nivel de madurez de NLP"""
        # Basado en capacidades disponibles
        maturity_score = 0
        
        if self.nlp_analysis and 'nlp_techniques' in self.nlp_analysis:
            techniques = self.nlp_analysis['nlp_techniques']
            
            # Tokenization
            if 'Tokenization' in techniques.get('techniques', {}):
                maturity_score += 20
            
            # Sentiment Analysis
            if 'Sentiment Analysis' in techniques.get('techniques', {}):
                maturity_score += 20
            
            # Text Classification
            if 'Text Classification' in techniques.get('techniques', {}):
                maturity_score += 20
            
            # Named Entity Recognition
            if 'Named Entity Recognition' in techniques.get('techniques', {}):
                maturity_score += 20
            
            # Topic Modeling
            if 'Topic Modeling' in techniques.get('techniques', {}):
                maturity_score += 20
        
        if maturity_score >= 80:
            return 'Advanced'
        elif maturity_score >= 60:
            return 'Intermediate'
        elif maturity_score >= 40:
            return 'Basic'
        else:
            return 'Beginner'
    
    def _calculate_nlp_readiness_score(self):
        """Calcular score de preparación para NLP"""
        readiness_score = 0
        
        # Data readiness
        readiness_score += 25
        
        # Infrastructure readiness
        readiness_score += 20
        
        # Skills readiness
        readiness_score += 20
        
        # Process readiness
        readiness_score += 20
        
        # Culture readiness
        readiness_score += 15
        
        return readiness_score
    
    def _calculate_nlp_implementation_priority(self):
        """Calcular prioridad de implementación de NLP"""
        priority_score = 0
        
        # Business impact
        priority_score += 30
        
        # Technical feasibility
        priority_score += 25
        
        # Resource availability
        priority_score += 20
        
        # Time to value
        priority_score += 15
        
        # Risk level
        priority_score += 10
        
        if priority_score >= 80:
            return 'High'
        elif priority_score >= 60:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_nlp_roi_potential(self):
        """Calcular potencial de ROI de NLP"""
        roi_score = 0
        
        # Cost reduction potential
        roi_score += 25
        
        # Revenue increase potential
        roi_score += 25
        
        # Efficiency improvement potential
        roi_score += 25
        
        # Competitive advantage potential
        roi_score += 25
        
        if roi_score >= 80:
            return 'Very High'
        elif roi_score >= 60:
            return 'High'
        elif roi_score >= 40:
            return 'Medium'
        else:
            return 'Low'
    
    def build_nlp_models(self, target_variable, model_type='classification'):
        """Construir modelos de NLP"""
        if target_variable not in self.nlp_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.nlp_data.columns if col != target_variable]
        X = self.nlp_data[feature_columns]
        y = self.nlp_data[target_variable]
        
        # Preprocesamiento
        X_processed, y_processed = self._preprocess_nlp_data(X, y, model_type)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42)
        
        # Construir modelos
        models = {}
        
        if model_type == 'classification':
            models = self._build_nlp_classification_models(X_train, X_test, y_train, y_test)
        elif model_type == 'regression':
            models = self._build_nlp_regression_models(X_train, X_test, y_train, y_test)
        elif model_type == 'clustering':
            models = self._build_nlp_clustering_models(X_processed)
        elif model_type == 'topic_modeling':
            models = self._build_nlp_topic_models(X_processed)
        
        # Evaluar modelos
        model_evaluation = self._evaluate_nlp_models(models, X_test, y_test, model_type)
        
        # Optimizar modelos
        optimized_models = self._optimize_nlp_models(models, X_train, y_train)
        
        self.nlp_models = {
            'models': models,
            'optimized_models': optimized_models,
            'model_evaluation': model_evaluation,
            'model_type': model_type,
            'target_variable': target_variable
        }
        
        return self.nlp_models
    
    def _preprocess_nlp_data(self, X, y, model_type):
        """Preprocesar datos de NLP"""
        # Identificar columnas de texto
        text_columns = X.select_dtypes(include=['object']).columns
        
        # Preprocesar columnas de texto
        if len(text_columns) > 0:
            # Aplicar preprocesamiento de texto
            X_text = X[text_columns].apply(lambda x: self._preprocess_text(x))
            
            # Vectorizar texto
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            X_text_vectorized = vectorizer.fit_transform(X_text.astype(str))
            
            # Convertir a array denso
            X_text_dense = X_text_vectorized.toarray()
        else:
            X_text_dense = np.array([]).reshape(len(X), 0)
        
        # Preprocesar columnas numéricas
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            scaler = StandardScaler()
            X_numeric = scaler.fit_transform(X[numeric_columns])
        else:
            X_numeric = np.array([]).reshape(len(X), 0)
        
        # Combinar características
        if X_text_dense.shape[1] > 0 and X_numeric.shape[1] > 0:
            X_processed = np.concatenate([X_text_dense, X_numeric], axis=1)
        elif X_text_dense.shape[1] > 0:
            X_processed = X_text_dense
        else:
            X_processed = X_numeric
        
        # Preprocesar variable objetivo
        if model_type == 'classification':
            if y.dtype == 'object':
                label_encoder = LabelEncoder()
                y_processed = label_encoder.fit_transform(y)
            else:
                y_processed = y.values
        else:
            y_processed = y.values
        
        return X_processed, y_processed
    
    def _preprocess_text(self, text):
        """Preprocesar texto"""
        if pd.isna(text):
            return ""
        
        # Convertir a string
        text = str(text)
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenizar
        tokens = word_tokenize(text)
        
        # Remover stop words
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        
        # Lematizar
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        
        # Unir tokens
        processed_text = ' '.join(tokens)
        
        return processed_text
    
    def _build_nlp_classification_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de clasificación de NLP"""
        models = {}
        
        # Naive Bayes
        nb_model = MultinomialNB()
        nb_model.fit(X_train, y_train)
        models['Naive Bayes'] = nb_model
        
        # Logistic Regression
        lr_model = LogisticRegression(random_state=42)
        lr_model.fit(X_train, y_train)
        models['Logistic Regression'] = lr_model
        
        # Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        models['Random Forest'] = rf_model
        
        # SVM
        svm_model = SVC(random_state=42)
        svm_model.fit(X_train, y_train)
        models['SVM'] = svm_model
        
        return models
    
    def _build_nlp_regression_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de regresión de NLP"""
        models = {}
        
        # Linear Regression
        from sklearn.linear_model import LinearRegression
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        models['Linear Regression'] = lr_model
        
        # Ridge Regression
        from sklearn.linear_model import Ridge
        ridge_model = Ridge(random_state=42)
        ridge_model.fit(X_train, y_train)
        models['Ridge Regression'] = ridge_model
        
        # Random Forest
        from sklearn.ensemble import RandomForestRegressor
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        models['Random Forest'] = rf_model
        
        return models
    
    def _build_nlp_clustering_models(self, X):
        """Construir modelos de clustering de NLP"""
        models = {}
        
        # K-Means
        kmeans_model = KMeans(n_clusters=3, random_state=42)
        kmeans_model.fit(X)
        models['K-Means'] = kmeans_model
        
        # Hierarchical Clustering
        from sklearn.cluster import AgglomerativeClustering
        hierarchical_model = AgglomerativeClustering(n_clusters=3)
        hierarchical_model.fit(X)
        models['Hierarchical Clustering'] = hierarchical_model
        
        return models
    
    def _build_nlp_topic_models(self, X):
        """Construir modelos de topic modeling de NLP"""
        models = {}
        
        # LDA
        lda_model = LatentDirichletAllocation(n_components=5, random_state=42)
        lda_model.fit(X)
        models['LDA'] = lda_model
        
        # NMF
        from sklearn.decomposition import NMF
        nmf_model = NMF(n_components=5, random_state=42)
        nmf_model.fit(X)
        models['NMF'] = nmf_model
        
        return models
    
    def _evaluate_nlp_models(self, models, X_test, y_test, model_type):
        """Evaluar modelos de NLP"""
        evaluation_results = {}
        
        for model_name, model in models.items():
            try:
                if model_type == 'classification':
                    y_pred = model.predict(X_test)
                    evaluation_results[model_name] = {
                        'accuracy': accuracy_score(y_test, y_pred),
                        'precision': precision_score(y_test, y_pred, average='weighted'),
                        'recall': recall_score(y_test, y_pred, average='weighted'),
                        'f1_score': f1_score(y_test, y_pred, average='weighted')
                    }
                elif model_type == 'regression':
                    y_pred = model.predict(X_test)
                    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
                    evaluation_results[model_name] = {
                        'mse': mean_squared_error(y_test, y_pred),
                        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                        'mae': mean_absolute_error(y_test, y_pred),
                        'r2': r2_score(y_test, y_pred)
                    }
                elif model_type == 'clustering':
                    if hasattr(model, 'labels_'):
                        labels = model.labels_
                        evaluation_results[model_name] = {
                            'n_clusters': len(set(labels)) - (1 if -1 in labels else 0),
                            'n_noise': list(labels).count(-1) if -1 in labels else 0
                        }
                elif model_type == 'topic_modeling':
                    # Para topic modeling, evaluar perplexity
                    if hasattr(model, 'perplexity'):
                        perplexity = model.perplexity(X_test)
                        evaluation_results[model_name] = {
                            'perplexity': perplexity
                        }
            except Exception as e:
                evaluation_results[model_name] = {'error': str(e)}
        
        return evaluation_results
    
    def _optimize_nlp_models(self, models, X_train, y_train):
        """Optimizar modelos de NLP"""
        optimized_models = {}
        
        for model_name, model in models.items():
            try:
                # Optimización de hiperparámetros
                if hasattr(model, 'get_params'):
                    # Crear modelo optimizado con mejores hiperparámetros
                    optimized_model = self._create_optimized_nlp_model(model_name, X_train.shape[1])
                    optimized_models[model_name] = optimized_model
                else:
                    optimized_models[model_name] = model
            except Exception as e:
                optimized_models[model_name] = model
        
        return optimized_models
    
    def _create_optimized_nlp_model(self, model_name, input_dim):
        """Crear modelo de NLP optimizado"""
        if model_name == 'Naive Bayes':
            return MultinomialNB(alpha=0.1)
        elif model_name == 'Logistic Regression':
            return LogisticRegression(random_state=42, C=1.0, max_iter=1000)
        elif model_name == 'Random Forest':
            return RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
        elif model_name == 'SVM':
            return SVC(random_state=42, C=1.0, kernel='rbf')
        else:
            return MultinomialNB()
    
    def generate_nlp_strategies(self):
        """Generar estrategias de NLP"""
        strategies = []
        
        # Estrategias basadas en técnicas de NLP
        if self.nlp_analysis and 'nlp_techniques' in self.nlp_analysis:
            techniques = self.nlp_analysis['nlp_techniques']
            
            # Estrategias de análisis de sentimientos
            if 'Sentiment Analysis' in techniques.get('techniques', {}):
                strategies.append({
                    'strategy_type': 'Sentiment Analysis Implementation',
                    'description': 'Implementar análisis de sentimientos para monitoreo de marca',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de clasificación de texto
            if 'Text Classification' in techniques.get('techniques', {}):
                strategies.append({
                    'strategy_type': 'Text Classification Implementation',
                    'description': 'Implementar clasificación de texto para categorización de contenido',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de chatbots
            if 'Question Answering' in techniques.get('techniques', {}):
                strategies.append({
                    'strategy_type': 'Chatbot Implementation',
                    'description': 'Implementar chatbots para soporte al cliente',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en aplicaciones de NLP
        if self.nlp_analysis and 'nlp_applications' in self.nlp_analysis:
            applications = self.nlp_analysis['nlp_applications']
            
            # Estrategias de análisis de sentimientos
            if 'Sentiment Analysis' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Sentiment Analysis Application',
                    'description': 'Implementar análisis de sentimientos para feedback de clientes',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de chatbots
            if 'Chatbots' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Chatbot Application',
                    'description': 'Implementar chatbots para engagement de clientes',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en preprocesamiento de texto
        if self.nlp_analysis and 'text_preprocessing' in self.nlp_analysis:
            preprocessing = self.nlp_analysis['text_preprocessing']
            
            strategies.append({
                'strategy_type': 'Text Preprocessing Optimization',
                'description': 'Optimizar preprocesamiento de texto para mejor performance',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        # Estrategias basadas en análisis de sentimientos
        if self.nlp_analysis and 'sentiment_analysis' in self.nlp_analysis:
            sentiment_analysis = self.nlp_analysis['sentiment_analysis']
            
            strategies.append({
                'strategy_type': 'Sentiment Analysis Optimization',
                'description': 'Optimizar análisis de sentimientos para mejor precisión',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        # Estrategias basadas en extracción de características
        if self.nlp_analysis and 'feature_extraction' in self.nlp_analysis:
            feature_extraction = self.nlp_analysis['feature_extraction']
            
            strategies.append({
                'strategy_type': 'Feature Extraction Optimization',
                'description': 'Optimizar extracción de características para mejor representación',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        self.nlp_strategies = strategies
        return strategies
    
    def generate_nlp_insights(self):
        """Generar insights de NLP"""
        insights = []
        
        # Insights de evaluación general de NLP
        if self.nlp_analysis and 'overall_nlp_assessment' in self.nlp_analysis:
            assessment = self.nlp_analysis['overall_nlp_assessment']
            maturity_level = assessment.get('nlp_maturity_level', 'Unknown')
            
            insights.append({
                'category': 'NLP Maturity',
                'insight': f'Nivel de madurez de NLP: {maturity_level}',
                'recommendation': f'{"Mantener" if maturity_level == "Advanced" else "Mejorar"} capacidades de NLP',
                'priority': 'high' if maturity_level in ['Beginner', 'Basic'] else 'medium'
            })
            
            readiness_score = assessment.get('nlp_readiness_score', 0)
            if readiness_score < 70:
                insights.append({
                    'category': 'NLP Readiness',
                    'insight': f'Score de preparación para NLP: {readiness_score}',
                    'recommendation': 'Mejorar preparación para implementación de NLP',
                    'priority': 'high'
                })
            
            implementation_priority = assessment.get('nlp_implementation_priority', 'Low')
            if implementation_priority == 'High':
                insights.append({
                    'category': 'NLP Implementation',
                    'insight': f'Prioridad de implementación: {implementation_priority}',
                    'recommendation': 'Priorizar implementación de NLP',
                    'priority': 'high'
                })
            
            roi_potential = assessment.get('nlp_roi_potential', 'Low')
            if roi_potential in ['High', 'Very High']:
                insights.append({
                    'category': 'NLP ROI',
                    'insight': f'Potencial de ROI: {roi_potential}',
                    'recommendation': 'Invertir en NLP para maximizar ROI',
                    'priority': 'high'
                })
        
        # Insights de técnicas de NLP
        if self.nlp_analysis and 'nlp_techniques' in self.nlp_analysis:
            techniques = self.nlp_analysis['nlp_techniques']
            best_technique = techniques.get('best_technique', 'Unknown')
            
            insights.append({
                'category': 'NLP Techniques',
                'insight': f'Mejor técnica de NLP: {best_technique}',
                'recommendation': 'Usar esta técnica para aplicaciones de NLP',
                'priority': 'high'
            })
        
        # Insights de aplicaciones de NLP
        if self.nlp_analysis and 'nlp_applications' in self.nlp_analysis:
            applications = self.nlp_analysis['nlp_applications']
            best_application = applications.get('best_application', 'Unknown')
            
            insights.append({
                'category': 'NLP Applications',
                'insight': f'Mejor aplicación de NLP: {best_application}',
                'recommendation': 'Implementar esta aplicación para máximo valor de negocio',
                'priority': 'high'
            })
        
        # Insights de modelos de NLP
        if self.nlp_models:
            model_evaluation = self.nlp_models.get('model_evaluation', {})
            if model_evaluation:
                # Encontrar mejor modelo
                best_model = None
                best_score = 0
                
                for model_name, metrics in model_evaluation.items():
                    if 'error' not in metrics:
                        if 'accuracy' in metrics:
                            score = metrics['accuracy']
                        elif 'r2' in metrics:
                            score = metrics['r2']
                        else:
                            score = 0
                        
                        if score > best_score:
                            best_score = score
                            best_model = model_name
                
                if best_model:
                    insights.append({
                        'category': 'NLP Model Performance',
                        'insight': f'Mejor modelo de NLP: {best_model} con score {best_score:.3f}',
                        'recommendation': 'Usar este modelo para predicciones de NLP',
                        'priority': 'high'
                    })
        
        self.nlp_insights = insights
        return insights
    
    def create_nlp_dashboard(self):
        """Crear dashboard de NLP"""
        if self.nlp_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('NLP Techniques', 'Model Performance',
                          'NLP Maturity', 'Implementation Priority'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de técnicas de NLP
        if self.nlp_analysis and 'nlp_techniques' in self.nlp_analysis:
            techniques = self.nlp_analysis['nlp_techniques']
            technique_names = list(techniques.get('techniques', {}).keys())
            technique_scores = [5] * len(technique_names)  # Placeholder scores
            
            fig.add_trace(
                go.Bar(x=technique_names, y=technique_scores, name='NLP Techniques'),
                row=1, col=1
            )
        
        # Gráfico de performance de modelos
        if self.nlp_models:
            model_evaluation = self.nlp_models.get('model_evaluation', {})
            if model_evaluation:
                model_names = list(model_evaluation.keys())
                model_scores = []
                
                for model_name, metrics in model_evaluation.items():
                    if 'error' not in metrics:
                        if 'accuracy' in metrics:
                            score = metrics['accuracy']
                        elif 'r2' in metrics:
                            score = metrics['r2']
                        else:
                            score = 0
                        model_scores.append(score)
                    else:
                        model_scores.append(0)
                
                fig.add_trace(
                    go.Bar(x=model_names, y=model_scores, name='Model Performance'),
                    row=1, col=2
                )
        
        # Gráfico de madurez de NLP
        if self.nlp_analysis and 'overall_nlp_assessment' in self.nlp_analysis:
            assessment = self.nlp_analysis['overall_nlp_assessment']
            maturity_level = assessment.get('nlp_maturity_level', 'Unknown')
            
            maturity_data = {
                'Beginner': 1,
                'Basic': 2,
                'Intermediate': 3,
                'Advanced': 4
            }
            
            fig.add_trace(
                go.Pie(labels=list(maturity_data.keys()), values=list(maturity_data.values()), name='NLP Maturity'),
                row=2, col=1
            )
        
        # Gráfico de prioridad de implementación
        if self.nlp_analysis and 'overall_nlp_assessment' in self.nlp_analysis:
            assessment = self.nlp_analysis['overall_nlp_assessment']
            implementation_priority = assessment.get('nlp_implementation_priority', 'Low')
            
            priority_data = {
                'Low': 1,
                'Medium': 2,
                'High': 3
            }
            
            fig.add_trace(
                go.Bar(x=list(priority_data.keys()), y=list(priority_data.values()), name='Implementation Priority'),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Dashboard de NLP",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_nlp_analysis(self, filename='marketing_nlp_analysis.json'):
        """Exportar análisis de NLP"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'nlp_analysis': self.nlp_analysis,
            'nlp_models': {k: {'model_evaluation': v.get('model_evaluation', {})} for k, v in self.nlp_models.items()},
            'nlp_strategies': self.nlp_strategies,
            'nlp_insights': self.nlp_insights,
            'summary': {
                'total_records': len(self.nlp_data),
                'nlp_maturity_level': self.nlp_analysis.get('overall_nlp_assessment', {}).get('nlp_maturity_level', 'Unknown'),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de NLP exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de NLP de marketing
    nlp_optimizer = MarketingNLPOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 1000, 1000),
        'age': np.random.normal(35, 10, 1000),
        'income': np.random.normal(50000, 15000, 1000),
        'spending': np.random.normal(1000, 300, 1000),
        'conversion_rate': np.random.uniform(0, 100, 1000),
        'ctr': np.random.uniform(0, 10, 1000),
        'engagement_rate': np.random.uniform(0, 100, 1000),
        'channel': np.random.choice(['Email', 'Social', 'Paid Search', 'Display'], 1000),
        'device': np.random.choice(['Desktop', 'Mobile', 'Tablet'], 1000),
        'location': np.random.choice(['US', 'UK', 'CA', 'AU'], 1000),
        'segment': np.random.choice(['New', 'Active', 'Inactive', 'VIP'], 1000),
        'text_content': ['This is a sample text for NLP analysis'] * 1000,
        'nlp_score': np.random.uniform(0, 100, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de NLP de marketing
    print("📊 Cargando datos de NLP de marketing...")
    nlp_optimizer.load_nlp_data(sample_data)
    
    # Analizar capacidades de NLP
    print("🤖 Analizando capacidades de NLP...")
    nlp_analysis = nlp_optimizer.analyze_nlp_capabilities()
    
    # Construir modelos de NLP
    print("🔮 Construyendo modelos de NLP...")
    nlp_models = nlp_optimizer.build_nlp_models(target_variable='nlp_score', model_type='regression')
    
    # Generar estrategias de NLP
    print("🎯 Generando estrategias de NLP...")
    nlp_strategies = nlp_optimizer.generate_nlp_strategies()
    
    # Generar insights de NLP
    print("💡 Generando insights de NLP...")
    nlp_insights = nlp_optimizer.generate_nlp_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de NLP...")
    dashboard = nlp_optimizer.create_nlp_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de NLP...")
    export_data = nlp_optimizer.export_nlp_analysis()
    
    print("✅ Sistema de optimización de NLP de marketing completado!")




