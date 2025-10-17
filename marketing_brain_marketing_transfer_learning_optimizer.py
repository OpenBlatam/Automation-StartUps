"""
Marketing Brain Marketing Transfer Learning Optimizer
Motor avanzado de optimización de transfer learning de marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, applications
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class MarketingTransferLearningOptimizer:
    def __init__(self):
        self.tl_data = {}
        self.tl_analysis = {}
        self.tl_models = {}
        self.tl_strategies = {}
        self.tl_insights = {}
        self.tl_recommendations = {}
        
    def load_tl_data(self, tl_data):
        """Cargar datos de transfer learning de marketing"""
        if isinstance(tl_data, str):
            if tl_data.endswith('.csv'):
                self.tl_data = pd.read_csv(tl_data)
            elif tl_data.endswith('.json'):
                with open(tl_data, 'r') as f:
                    data = json.load(f)
                self.tl_data = pd.DataFrame(data)
        else:
            self.tl_data = pd.DataFrame(tl_data)
        
        print(f"✅ Datos de transfer learning de marketing cargados: {len(self.tl_data)} registros")
        return True
    
    def analyze_tl_capabilities(self):
        """Analizar capacidades de transfer learning"""
        if self.tl_data.empty:
            return None
        
        # Análisis de estrategias de transfer learning
        tl_strategies = self._analyze_tl_strategies()
        
        # Análisis de modelos pre-entrenados
        pretrained_models = self._analyze_pretrained_models()
        
        # Análisis de técnicas de transfer learning
        tl_techniques = self._analyze_tl_techniques()
        
        # Análisis de aplicaciones de transfer learning
        tl_applications = self._analyze_tl_applications()
        
        # Análisis de fine-tuning
        fine_tuning = self._analyze_fine_tuning()
        
        # Análisis de domain adaptation
        domain_adaptation = self._analyze_domain_adaptation()
        
        tl_results = {
            'tl_strategies': tl_strategies,
            'pretrained_models': pretrained_models,
            'tl_techniques': tl_techniques,
            'tl_applications': tl_applications,
            'fine_tuning': fine_tuning,
            'domain_adaptation': domain_adaptation,
            'overall_tl_assessment': self._calculate_overall_tl_assessment()
        }
        
        self.tl_analysis = tl_results
        return tl_results
    
    def _analyze_tl_strategies(self):
        """Analizar estrategias de transfer learning"""
        strategy_analysis = {}
        
        # Estrategias disponibles
        strategies = {
            'Feature Extraction': {
                'complexity': 2,
                'effectiveness': 4,
                'data_requirements': 2,
                'use_cases': ['Limited Data', 'Pre-trained Features', 'Quick Implementation']
            },
            'Fine-tuning': {
                'complexity': 3,
                'effectiveness': 5,
                'data_requirements': 3,
                'use_cases': ['Domain Adaptation', 'Task-specific Training', 'High Performance']
            },
            'Progressive Unfreezing': {
                'complexity': 4,
                'effectiveness': 5,
                'data_requirements': 3,
                'use_cases': ['Large Models', 'Careful Fine-tuning', 'Stable Training']
            },
            'Multi-task Learning': {
                'complexity': 4,
                'effectiveness': 4,
                'data_requirements': 4,
                'use_cases': ['Related Tasks', 'Shared Representations', 'Efficient Learning']
            },
            'Domain Adaptation': {
                'complexity': 4,
                'effectiveness': 4,
                'data_requirements': 3,
                'use_cases': ['Domain Shift', 'Unlabeled Data', 'Cross-domain Learning']
            },
            'Few-shot Learning': {
                'complexity': 4,
                'effectiveness': 4,
                'data_requirements': 1,
                'use_cases': ['Limited Data', 'Quick Adaptation', 'Meta-learning']
            }
        }
        
        strategy_analysis['strategies'] = strategies
        strategy_analysis['best_strategy'] = self._select_best_tl_strategy(strategies)
        strategy_analysis['recommendations'] = self._get_tl_strategy_recommendations(strategies)
        
        return strategy_analysis
    
    def _select_best_tl_strategy(self, strategies):
        """Seleccionar mejor estrategia de transfer learning"""
        best_strategy = None
        best_score = 0
        
        for name, performance in strategies.items():
            # Calcular score combinado
            score = (performance['effectiveness'] * 0.4 + 
                    performance['data_requirements'] * 0.3 + 
                    (6 - performance['complexity']) * 0.3)
            
            if score > best_score:
                best_score = score
                best_strategy = name
        
        return best_strategy
    
    def _get_tl_strategy_recommendations(self, strategies):
        """Obtener recomendaciones de estrategias de transfer learning"""
        recommendations = []
        
        # Recomendaciones basadas en efectividad
        high_effectiveness_strategies = [name for name, perf in strategies.items() 
                                       if perf['effectiveness'] >= 4]
        if high_effectiveness_strategies:
            recommendations.append({
                'criteria': 'High Effectiveness',
                'strategies': high_effectiveness_strategies,
                'reason': 'Excellent performance for transfer learning'
            })
        
        # Recomendaciones basadas en requisitos de datos
        low_data_strategies = [name for name, perf in strategies.items() 
                             if perf['data_requirements'] <= 2]
        if low_data_strategies:
            recommendations.append({
                'criteria': 'Low Data Requirements',
                'strategies': low_data_strategies,
                'reason': 'Suitable for limited data scenarios'
            })
        
        # Recomendaciones basadas en complejidad
        low_complexity_strategies = [name for name, perf in strategies.items() 
                                   if perf['complexity'] <= 3]
        if low_complexity_strategies:
            recommendations.append({
                'criteria': 'Low Complexity',
                'strategies': low_complexity_strategies,
                'reason': 'Easier to implement and maintain'
            })
        
        return recommendations
    
    def _analyze_pretrained_models(self):
        """Analizar modelos pre-entrenados"""
        model_analysis = {}
        
        # Análisis de modelos de computer vision
        cv_models = self._analyze_cv_pretrained_models()
        model_analysis['computer_vision'] = cv_models
        
        # Análisis de modelos de NLP
        nlp_models = self._analyze_nlp_pretrained_models()
        model_analysis['nlp'] = nlp_models
        
        # Análisis de modelos de audio
        audio_models = self._analyze_audio_pretrained_models()
        model_analysis['audio'] = audio_models
        
        # Análisis de modelos de tabular data
        tabular_models = self._analyze_tabular_pretrained_models()
        model_analysis['tabular'] = tabular_models
        
        return model_analysis
    
    def _analyze_cv_pretrained_models(self):
        """Analizar modelos pre-entrenados de computer vision"""
        cv_analysis = {}
        
        # Modelos disponibles
        models = {
            'ResNet50': {
                'complexity': 3,
                'performance': 4,
                'size': 3,
                'use_cases': ['Image Classification', 'Feature Extraction', 'General CV Tasks']
            },
            'VGG16': {
                'complexity': 3,
                'performance': 3,
                'size': 2,
                'use_cases': ['Image Classification', 'Feature Extraction', 'Simple CV Tasks']
            },
            'InceptionV3': {
                'complexity': 4,
                'performance': 4,
                'size': 3,
                'use_cases': ['Image Classification', 'Feature Extraction', 'Complex CV Tasks']
            },
            'EfficientNetB0': {
                'complexity': 3,
                'performance': 4,
                'size': 2,
                'use_cases': ['Efficient Image Classification', 'Mobile Applications', 'Edge Computing']
            },
            'MobileNetV2': {
                'complexity': 2,
                'performance': 3,
                'size': 1,
                'use_cases': ['Mobile Applications', 'Edge Computing', 'Lightweight Models']
            },
            'DenseNet121': {
                'complexity': 3,
                'performance': 4,
                'size': 3,
                'use_cases': ['Image Classification', 'Feature Reuse', 'Dense Connections']
            }
        }
        
        cv_analysis['models'] = models
        cv_analysis['best_model'] = 'ResNet50'
        cv_analysis['recommendations'] = [
            'Use ResNet50 for general computer vision tasks',
            'Use EfficientNetB0 for efficient image classification',
            'Use MobileNetV2 for mobile and edge applications'
        ]
        
        return cv_analysis
    
    def _analyze_nlp_pretrained_models(self):
        """Analizar modelos pre-entrenados de NLP"""
        nlp_analysis = {}
        
        # Modelos disponibles
        models = {
            'BERT': {
                'complexity': 4,
                'performance': 5,
                'size': 4,
                'use_cases': ['Text Classification', 'Question Answering', 'General NLP Tasks']
            },
            'GPT-2': {
                'complexity': 4,
                'performance': 4,
                'size': 4,
                'use_cases': ['Text Generation', 'Language Modeling', 'Creative Writing']
            },
            'RoBERTa': {
                'complexity': 4,
                'performance': 5,
                'size': 4,
                'use_cases': ['Text Classification', 'Sentiment Analysis', 'General NLP Tasks']
            },
            'DistilBERT': {
                'complexity': 3,
                'performance': 4,
                'size': 3,
                'use_cases': ['Efficient NLP', 'Text Classification', 'Lightweight Models']
            },
            'ALBERT': {
                'complexity': 4,
                'performance': 4,
                'size': 3,
                'use_cases': ['Efficient NLP', 'Text Classification', 'Parameter Sharing']
            },
            'T5': {
                'complexity': 5,
                'performance': 5,
                'size': 5,
                'use_cases': ['Text-to-Text Tasks', 'Translation', 'Summarization']
            }
        }
        
        nlp_analysis['models'] = models
        nlp_analysis['best_model'] = 'BERT'
        nlp_analysis['recommendations'] = [
            'Use BERT for general NLP tasks',
            'Use DistilBERT for efficient NLP',
            'Use T5 for text-to-text tasks'
        ]
        
        return nlp_analysis
    
    def _analyze_audio_pretrained_models(self):
        """Analizar modelos pre-entrenados de audio"""
        audio_analysis = {}
        
        # Modelos disponibles
        models = {
            'Wav2Vec2': {
                'complexity': 4,
                'performance': 4,
                'size': 4,
                'use_cases': ['Speech Recognition', 'Audio Classification', 'Audio Understanding']
            },
            'Whisper': {
                'complexity': 4,
                'performance': 5,
                'size': 4,
                'use_cases': ['Speech Recognition', 'Audio Transcription', 'Multilingual Audio']
            },
            'CLAP': {
                'complexity': 4,
                'performance': 4,
                'size': 4,
                'use_cases': ['Audio-Text Matching', 'Audio Classification', 'Multimodal Learning']
            },
            'AudioCLIP': {
                'complexity': 4,
                'performance': 4,
                'size': 4,
                'use_cases': ['Audio-Text Matching', 'Audio Classification', 'Multimodal Learning']
            }
        }
        
        audio_analysis['models'] = models
        audio_analysis['best_model'] = 'Whisper'
        audio_analysis['recommendations'] = [
            'Use Whisper for speech recognition',
            'Use Wav2Vec2 for audio classification',
            'Use CLAP for audio-text matching'
        ]
        
        return audio_analysis
    
    def _analyze_tabular_pretrained_models(self):
        """Analizar modelos pre-entrenados de datos tabulares"""
        tabular_analysis = {}
        
        # Modelos disponibles
        models = {
            'TabNet': {
                'complexity': 4,
                'performance': 4,
                'size': 3,
                'use_cases': ['Tabular Data Classification', 'Feature Selection', 'Interpretable ML']
            },
            'NODE': {
                'complexity': 4,
                'performance': 4,
                'size': 3,
                'use_cases': ['Tabular Data Classification', 'Deep Learning', 'Tree-based Models']
            },
            'SAINT': {
                'complexity': 4,
                'performance': 4,
                'size': 3,
                'use_cases': ['Tabular Data Classification', 'Self-attention', 'Deep Learning']
            },
            'FT-Transformer': {
                'complexity': 4,
                'performance': 4,
                'size': 3,
                'use_cases': ['Tabular Data Classification', 'Transformer', 'Deep Learning']
            }
        }
        
        tabular_analysis['models'] = models
        tabular_analysis['best_model'] = 'TabNet'
        tabular_analysis['recommendations'] = [
            'Use TabNet for interpretable tabular data classification',
            'Use NODE for deep learning on tabular data',
            'Use SAINT for self-attention on tabular data'
        ]
        
        return tabular_analysis
    
    def _analyze_tl_techniques(self):
        """Analizar técnicas de transfer learning"""
        technique_analysis = {}
        
        # Técnicas disponibles
        techniques = {
            'Layer Freezing': {
                'complexity': 2,
                'effectiveness': 3,
                'interpretability': 4,
                'use_cases': ['Feature Extraction', 'Quick Implementation', 'Stable Training']
            },
            'Layer Unfreezing': {
                'complexity': 3,
                'effectiveness': 4,
                'interpretability': 3,
                'use_cases': ['Fine-tuning', 'Domain Adaptation', 'Task-specific Training']
            },
            'Learning Rate Scheduling': {
                'complexity': 3,
                'effectiveness': 4,
                'interpretability': 3,
                'use_cases': ['Fine-tuning', 'Stable Training', 'Performance Optimization']
            },
            'Data Augmentation': {
                'complexity': 2,
                'effectiveness': 4,
                'interpretability': 4,
                'use_cases': ['Data Diversity', 'Overfitting Prevention', 'Performance Improvement']
            },
            'Regularization': {
                'complexity': 2,
                'effectiveness': 3,
                'interpretability': 3,
                'use_cases': ['Overfitting Prevention', 'Generalization', 'Model Stability']
            },
            'Ensemble Methods': {
                'complexity': 4,
                'effectiveness': 4,
                'interpretability': 2,
                'use_cases': ['Performance Improvement', 'Robustness', 'Multiple Models']
            }
        }
        
        technique_analysis['techniques'] = techniques
        technique_analysis['best_technique'] = 'Learning Rate Scheduling'
        technique_analysis['recommendations'] = [
            'Use learning rate scheduling for stable fine-tuning',
            'Use data augmentation for better generalization',
            'Use layer freezing for quick feature extraction'
        ]
        
        return technique_analysis
    
    def _analyze_tl_applications(self):
        """Analizar aplicaciones de transfer learning"""
        application_analysis = {}
        
        # Aplicaciones disponibles
        applications = {
            'Image Classification': {
                'complexity': 3,
                'business_value': 5,
                'implementation_time': 2,
                'use_cases': ['Product Recognition', 'Content Categorization', 'Quality Control']
            },
            'Text Classification': {
                'complexity': 3,
                'business_value': 5,
                'implementation_time': 2,
                'use_cases': ['Sentiment Analysis', 'Content Categorization', 'Spam Detection']
            },
            'Object Detection': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['Product Detection', 'Logo Detection', 'Face Detection']
            },
            'Text Generation': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['Content Creation', 'Chatbots', 'Creative Writing']
            },
            'Speech Recognition': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['Voice Assistants', 'Transcription', 'Customer Service']
            },
            'Recommendation Systems': {
                'complexity': 4,
                'business_value': 5,
                'implementation_time': 3,
                'use_cases': ['Product Recommendations', 'Content Recommendations', 'Personalization']
            },
            'Anomaly Detection': {
                'complexity': 3,
                'business_value': 4,
                'implementation_time': 2,
                'use_cases': ['Fraud Detection', 'Quality Control', 'Security']
            },
            'Time Series Forecasting': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['Sales Forecasting', 'Demand Prediction', 'Trend Analysis']
            }
        }
        
        application_analysis['applications'] = applications
        application_analysis['best_application'] = 'Image Classification'
        application_analysis['recommendations'] = [
            'Start with Image Classification for immediate business value',
            'Implement Text Classification for content analysis',
            'Consider Object Detection for product recognition'
        ]
        
        return application_analysis
    
    def _analyze_fine_tuning(self):
        """Analizar fine-tuning"""
        fine_tuning_analysis = {}
        
        # Técnicas de fine-tuning
        techniques = {
            'Full Fine-tuning': {
                'complexity': 3,
                'effectiveness': 5,
                'data_requirements': 4,
                'use_cases': ['High Performance', 'Sufficient Data', 'Task-specific Training']
            },
            'Partial Fine-tuning': {
                'complexity': 2,
                'effectiveness': 4,
                'data_requirements': 3,
                'use_cases': ['Limited Data', 'Quick Implementation', 'Stable Training']
            },
            'Progressive Unfreezing': {
                'complexity': 4,
                'effectiveness': 5,
                'data_requirements': 3,
                'use_cases': ['Large Models', 'Careful Training', 'Stable Convergence']
            },
            'Layer-wise Learning Rate': {
                'complexity': 3,
                'effectiveness': 4,
                'data_requirements': 3,
                'use_cases': ['Different Learning Rates', 'Stable Training', 'Performance Optimization']
            }
        }
        
        fine_tuning_analysis['techniques'] = techniques
        fine_tuning_analysis['best_technique'] = 'Progressive Unfreezing'
        fine_tuning_analysis['recommendations'] = [
            'Use progressive unfreezing for large models',
            'Use partial fine-tuning for limited data',
            'Use full fine-tuning for maximum performance'
        ]
        
        return fine_tuning_analysis
    
    def _analyze_domain_adaptation(self):
        """Analizar domain adaptation"""
        domain_analysis = {}
        
        # Técnicas de domain adaptation
        techniques = {
            'Domain Adversarial Training': {
                'complexity': 4,
                'effectiveness': 4,
                'interpretability': 2,
                'use_cases': ['Domain Shift', 'Adversarial Learning', 'Cross-domain Transfer']
            },
            'Domain-specific Fine-tuning': {
                'complexity': 3,
                'effectiveness': 4,
                'interpretability': 3,
                'use_cases': ['Domain Adaptation', 'Task-specific Training', 'Fine-tuning']
            },
            'Multi-domain Learning': {
                'complexity': 4,
                'effectiveness': 4,
                'interpretability': 2,
                'use_cases': ['Multiple Domains', 'Shared Representations', 'Efficient Learning']
            },
            'Unsupervised Domain Adaptation': {
                'complexity': 4,
                'effectiveness': 3,
                'interpretability': 2,
                'use_cases': ['Unlabeled Target Data', 'Domain Shift', 'Cross-domain Learning']
            }
        }
        
        domain_analysis['techniques'] = techniques
        domain_analysis['best_technique'] = 'Domain-specific Fine-tuning'
        domain_analysis['recommendations'] = [
            'Use domain-specific fine-tuning for domain adaptation',
            'Use domain adversarial training for domain shift',
            'Consider multi-domain learning for multiple domains'
        ]
        
        return domain_analysis
    
    def _calculate_overall_tl_assessment(self):
        """Calcular evaluación general de transfer learning"""
        overall_assessment = {}
        
        if not self.tl_data.empty:
            overall_assessment = {
                'tl_maturity_level': self._calculate_tl_maturity_level(),
                'tl_readiness_score': self._calculate_tl_readiness_score(),
                'tl_implementation_priority': self._calculate_tl_implementation_priority(),
                'tl_roi_potential': self._calculate_tl_roi_potential()
            }
        
        return overall_assessment
    
    def _calculate_tl_maturity_level(self):
        """Calcular nivel de madurez de transfer learning"""
        # Basado en capacidades disponibles
        maturity_score = 0
        
        if self.tl_analysis and 'tl_strategies' in self.tl_analysis:
            strategies = self.tl_analysis['tl_strategies']
            
            # Feature Extraction
            if 'Feature Extraction' in strategies.get('strategies', {}):
                maturity_score += 20
            
            # Fine-tuning
            if 'Fine-tuning' in strategies.get('strategies', {}):
                maturity_score += 20
            
            # Progressive Unfreezing
            if 'Progressive Unfreezing' in strategies.get('strategies', {}):
                maturity_score += 20
            
            # Multi-task Learning
            if 'Multi-task Learning' in strategies.get('strategies', {}):
                maturity_score += 20
            
            # Domain Adaptation
            if 'Domain Adaptation' in strategies.get('strategies', {}):
                maturity_score += 20
        
        if maturity_score >= 80:
            return 'Advanced'
        elif maturity_score >= 60:
            return 'Intermediate'
        elif maturity_score >= 40:
            return 'Basic'
        else:
            return 'Beginner'
    
    def _calculate_tl_readiness_score(self):
        """Calcular score de preparación para transfer learning"""
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
    
    def _calculate_tl_implementation_priority(self):
        """Calcular prioridad de implementación de transfer learning"""
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
    
    def _calculate_tl_roi_potential(self):
        """Calcular potencial de ROI de transfer learning"""
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
    
    def build_tl_models(self, target_variable, model_type='classification'):
        """Construir modelos de transfer learning"""
        if target_variable not in self.tl_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.tl_data.columns if col != target_variable]
        X = self.tl_data[feature_columns]
        y = self.tl_data[target_variable]
        
        # Preprocesamiento
        X_processed, y_processed = self._preprocess_tl_data(X, y, model_type)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42)
        
        # Construir modelos
        models = {}
        
        if model_type == 'classification':
            models = self._build_tl_classification_models(X_train, X_test, y_train, y_test)
        elif model_type == 'regression':
            models = self._build_tl_regression_models(X_train, X_test, y_train, y_test)
        elif model_type == 'feature_extraction':
            models = self._build_tl_feature_extraction_models(X_processed)
        
        # Evaluar modelos
        model_evaluation = self._evaluate_tl_models(models, X_test, y_test, model_type)
        
        # Optimizar modelos
        optimized_models = self._optimize_tl_models(models, X_train, y_train)
        
        self.tl_models = {
            'models': models,
            'optimized_models': optimized_models,
            'model_evaluation': model_evaluation,
            'model_type': model_type,
            'target_variable': target_variable
        }
        
        return self.tl_models
    
    def _preprocess_tl_data(self, X, y, model_type):
        """Preprocesar datos de transfer learning"""
        # Identificar columnas numéricas y categóricas
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        categorical_columns = X.select_dtypes(include=['object']).columns
        
        # Preprocesar columnas numéricas
        if len(numeric_columns) > 0:
            scaler = StandardScaler()
            X_numeric = scaler.fit_transform(X[numeric_columns])
        else:
            X_numeric = np.array([]).reshape(len(X), 0)
        
        # Preprocesar columnas categóricas
        if len(categorical_columns) > 0:
            # One-hot encoding para columnas categóricas
            X_categorical = pd.get_dummies(X[categorical_columns])
            X_categorical = X_categorical.values
        else:
            X_categorical = np.array([]).reshape(len(X), 0)
        
        # Combinar características
        if X_numeric.shape[1] > 0 and X_categorical.shape[1] > 0:
            X_processed = np.concatenate([X_numeric, X_categorical], axis=1)
        elif X_numeric.shape[1] > 0:
            X_processed = X_numeric
        else:
            X_processed = X_categorical
        
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
    
    def _build_tl_classification_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de clasificación de transfer learning"""
        models = {}
        
        # ResNet50 con transfer learning
        resnet_model = self._build_resnet_tl_model(X_train.shape[1], len(np.unique(y_train)))
        models['ResNet50 TL'] = resnet_model
        
        # VGG16 con transfer learning
        vgg_model = self._build_vgg_tl_model(X_train.shape[1], len(np.unique(y_train)))
        models['VGG16 TL'] = vgg_model
        
        # EfficientNet con transfer learning
        efficientnet_model = self._build_efficientnet_tl_model(X_train.shape[1], len(np.unique(y_train)))
        models['EfficientNet TL'] = efficientnet_model
        
        return models
    
    def _build_tl_regression_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de regresión de transfer learning"""
        models = {}
        
        # ResNet50 para regresión con transfer learning
        resnet_model = self._build_resnet_tl_regression_model(X_train.shape[1])
        models['ResNet50 TL Regression'] = resnet_model
        
        # VGG16 para regresión con transfer learning
        vgg_model = self._build_vgg_tl_regression_model(X_train.shape[1])
        models['VGG16 TL Regression'] = vgg_model
        
        return models
    
    def _build_tl_feature_extraction_models(self, X):
        """Construir modelos de extracción de características de transfer learning"""
        models = {}
        
        # PCA
        pca_model = PCA(n_components=10)
        pca_model.fit(X)
        models['PCA'] = pca_model
        
        # K-Means
        kmeans_model = KMeans(n_clusters=3, random_state=42)
        kmeans_model.fit(X)
        models['K-Means'] = kmeans_model
        
        return models
    
    def _build_resnet_tl_model(self, input_dim, num_classes):
        """Construir modelo ResNet50 con transfer learning"""
        # Usar ResNet50 pre-entrenado
        base_model = applications.ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Agregar capas personalizadas
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_vgg_tl_model(self, input_dim, num_classes):
        """Construir modelo VGG16 con transfer learning"""
        # Usar VGG16 pre-entrenado
        base_model = applications.VGG16(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Agregar capas personalizadas
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_efficientnet_tl_model(self, input_dim, num_classes):
        """Construir modelo EfficientNet con transfer learning"""
        # Usar EfficientNet pre-entrenado
        base_model = applications.EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Agregar capas personalizadas
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_resnet_tl_regression_model(self, input_dim):
        """Construir modelo ResNet50 para regresión con transfer learning"""
        # Usar ResNet50 pre-entrenado
        base_model = applications.ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Agregar capas personalizadas
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _build_vgg_tl_regression_model(self, input_dim):
        """Construir modelo VGG16 para regresión con transfer learning"""
        # Usar VGG16 pre-entrenado
        base_model = applications.VGG16(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Agregar capas personalizadas
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _evaluate_tl_models(self, models, X_test, y_test, model_type):
        """Evaluar modelos de transfer learning"""
        evaluation_results = {}
        
        for model_name, model in models.items():
            try:
                if model_type == 'classification':
                    if hasattr(model, 'predict'):
                        y_pred = model.predict(X_test)
                        y_pred_classes = np.argmax(y_pred, axis=1)
                        
                        evaluation_results[model_name] = {
                            'accuracy': accuracy_score(y_test, y_pred_classes),
                            'precision': precision_score(y_test, y_pred_classes, average='weighted'),
                            'recall': recall_score(y_test, y_pred_classes, average='weighted'),
                            'f1_score': f1_score(y_test, y_pred_classes, average='weighted')
                        }
                elif model_type == 'regression':
                    if hasattr(model, 'predict'):
                        y_pred = model.predict(X_test)
                        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
                        evaluation_results[model_name] = {
                            'mse': mean_squared_error(y_test, y_pred),
                            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                            'mae': mean_absolute_error(y_test, y_pred),
                            'r2': r2_score(y_test, y_pred)
                        }
                elif model_type == 'feature_extraction':
                    if hasattr(model, 'transform'):
                        X_transformed = model.transform(X_test)
                        evaluation_results[model_name] = {
                            'n_components': X_transformed.shape[1],
                            'explained_variance': getattr(model, 'explained_variance_ratio_', None)
                        }
            except Exception as e:
                evaluation_results[model_name] = {'error': str(e)}
        
        return evaluation_results
    
    def _optimize_tl_models(self, models, X_train, y_train):
        """Optimizar modelos de transfer learning"""
        optimized_models = {}
        
        for model_name, model in models.items():
            try:
                # Optimización de hiperparámetros
                if hasattr(model, 'get_config'):
                    # Crear modelo optimizado con mejores hiperparámetros
                    optimized_model = self._create_optimized_tl_model(model_name, X_train.shape[1], len(np.unique(y_train)))
                    optimized_models[model_name] = optimized_model
                else:
                    optimized_models[model_name] = model
            except Exception as e:
                optimized_models[model_name] = model
        
        return optimized_models
    
    def _create_optimized_tl_model(self, model_name, input_dim, num_classes):
        """Crear modelo de transfer learning optimizado"""
        if 'ResNet50' in model_name:
            return self._build_optimized_resnet_tl_model(input_dim, num_classes)
        elif 'VGG16' in model_name:
            return self._build_optimized_vgg_tl_model(input_dim, num_classes)
        elif 'EfficientNet' in model_name:
            return self._build_optimized_efficientnet_tl_model(input_dim, num_classes)
        else:
            return self._build_resnet_tl_model(input_dim, num_classes)
    
    def _build_optimized_resnet_tl_model(self, input_dim, num_classes):
        """Construir modelo ResNet50 optimizado con transfer learning"""
        # Usar ResNet50 pre-entrenado
        base_model = applications.ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Agregar capas personalizadas optimizadas
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(1024, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_optimized_vgg_tl_model(self, input_dim, num_classes):
        """Construir modelo VGG16 optimizado con transfer learning"""
        # Usar VGG16 pre-entrenado
        base_model = applications.VGG16(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Agregar capas personalizadas optimizadas
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(1024, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_optimized_efficientnet_tl_model(self, input_dim, num_classes):
        """Construir modelo EfficientNet optimizado con transfer learning"""
        # Usar EfficientNet pre-entrenado
        base_model = applications.EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base
        base_model.trainable = False
        
        # Agregar capas personalizadas optimizadas
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(1024, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def generate_tl_strategies(self):
        """Generar estrategias de transfer learning"""
        strategies = []
        
        # Estrategias basadas en estrategias de transfer learning
        if self.tl_analysis and 'tl_strategies' in self.tl_analysis:
            tl_strategies = self.tl_analysis['tl_strategies']
            
            # Estrategias de feature extraction
            if 'Feature Extraction' in tl_strategies.get('strategies', {}):
                strategies.append({
                    'strategy_type': 'Feature Extraction Implementation',
                    'description': 'Implementar feature extraction con modelos pre-entrenados',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de fine-tuning
            if 'Fine-tuning' in tl_strategies.get('strategies', {}):
                strategies.append({
                    'strategy_type': 'Fine-tuning Implementation',
                    'description': 'Implementar fine-tuning para adaptación de dominio',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de progressive unfreezing
            if 'Progressive Unfreezing' in tl_strategies.get('strategies', {}):
                strategies.append({
                    'strategy_type': 'Progressive Unfreezing Implementation',
                    'description': 'Implementar progressive unfreezing para modelos grandes',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en aplicaciones de transfer learning
        if self.tl_analysis and 'tl_applications' in self.tl_analysis:
            applications = self.tl_analysis['tl_applications']
            
            # Estrategias de image classification
            if 'Image Classification' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Image Classification Implementation',
                    'description': 'Implementar clasificación de imágenes con transfer learning',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de text classification
            if 'Text Classification' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Text Classification Implementation',
                    'description': 'Implementar clasificación de texto con transfer learning',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en fine-tuning
        if self.tl_analysis and 'fine_tuning' in self.tl_analysis:
            fine_tuning = self.tl_analysis['fine_tuning']
            
            strategies.append({
                'strategy_type': 'Fine-tuning Optimization',
                'description': 'Optimizar técnicas de fine-tuning para mejor performance',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        # Estrategias basadas en domain adaptation
        if self.tl_analysis and 'domain_adaptation' in self.tl_analysis:
            domain_adaptation = self.tl_analysis['domain_adaptation']
            
            strategies.append({
                'strategy_type': 'Domain Adaptation Implementation',
                'description': 'Implementar domain adaptation para transferencia entre dominios',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        self.tl_strategies = strategies
        return strategies
    
    def generate_tl_insights(self):
        """Generar insights de transfer learning"""
        insights = []
        
        # Insights de evaluación general de transfer learning
        if self.tl_analysis and 'overall_tl_assessment' in self.tl_analysis:
            assessment = self.tl_analysis['overall_tl_assessment']
            maturity_level = assessment.get('tl_maturity_level', 'Unknown')
            
            insights.append({
                'category': 'Transfer Learning Maturity',
                'insight': f'Nivel de madurez de transfer learning: {maturity_level}',
                'recommendation': f'{"Mantener" if maturity_level == "Advanced" else "Mejorar"} capacidades de transfer learning',
                'priority': 'high' if maturity_level in ['Beginner', 'Basic'] else 'medium'
            })
            
            readiness_score = assessment.get('tl_readiness_score', 0)
            if readiness_score < 70:
                insights.append({
                    'category': 'Transfer Learning Readiness',
                    'insight': f'Score de preparación para transfer learning: {readiness_score}',
                    'recommendation': 'Mejorar preparación para implementación de transfer learning',
                    'priority': 'high'
                })
            
            implementation_priority = assessment.get('tl_implementation_priority', 'Low')
            if implementation_priority == 'High':
                insights.append({
                    'category': 'Transfer Learning Implementation',
                    'insight': f'Prioridad de implementación: {implementation_priority}',
                    'recommendation': 'Priorizar implementación de transfer learning',
                    'priority': 'high'
                })
            
            roi_potential = assessment.get('tl_roi_potential', 'Low')
            if roi_potential in ['High', 'Very High']:
                insights.append({
                    'category': 'Transfer Learning ROI',
                    'insight': f'Potencial de ROI: {roi_potential}',
                    'recommendation': 'Invertir en transfer learning para maximizar ROI',
                    'priority': 'high'
                })
        
        # Insights de estrategias de transfer learning
        if self.tl_analysis and 'tl_strategies' in self.tl_analysis:
            strategies = self.tl_analysis['tl_strategies']
            best_strategy = strategies.get('best_strategy', 'Unknown')
            
            insights.append({
                'category': 'Transfer Learning Strategies',
                'insight': f'Mejor estrategia de transfer learning: {best_strategy}',
                'recommendation': 'Usar esta estrategia para implementación de transfer learning',
                'priority': 'high'
            })
        
        # Insights de aplicaciones de transfer learning
        if self.tl_analysis and 'tl_applications' in self.tl_analysis:
            applications = self.tl_analysis['tl_applications']
            best_application = applications.get('best_application', 'Unknown')
            
            insights.append({
                'category': 'Transfer Learning Applications',
                'insight': f'Mejor aplicación de transfer learning: {best_application}',
                'recommendation': 'Implementar esta aplicación para máximo valor de negocio',
                'priority': 'high'
            })
        
        # Insights de modelos de transfer learning
        if self.tl_models:
            model_evaluation = self.tl_models.get('model_evaluation', {})
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
                        'category': 'Transfer Learning Model Performance',
                        'insight': f'Mejor modelo de transfer learning: {best_model} con score {best_score:.3f}',
                        'recommendation': 'Usar este modelo para predicciones con transfer learning',
                        'priority': 'high'
                    })
        
        self.tl_insights = insights
        return insights
    
    def create_tl_dashboard(self):
        """Crear dashboard de transfer learning"""
        if self.tl_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('TL Strategies', 'Model Performance',
                          'TL Maturity', 'Implementation Priority'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de estrategias de transfer learning
        if self.tl_analysis and 'tl_strategies' in self.tl_analysis:
            strategies = self.tl_analysis['tl_strategies']
            strategy_names = list(strategies.get('strategies', {}).keys())
            strategy_scores = [5] * len(strategy_names)  # Placeholder scores
            
            fig.add_trace(
                go.Bar(x=strategy_names, y=strategy_scores, name='TL Strategies'),
                row=1, col=1
            )
        
        # Gráfico de performance de modelos
        if self.tl_models:
            model_evaluation = self.tl_models.get('model_evaluation', {})
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
        
        # Gráfico de madurez de transfer learning
        if self.tl_analysis and 'overall_tl_assessment' in self.tl_analysis:
            assessment = self.tl_analysis['overall_tl_assessment']
            maturity_level = assessment.get('tl_maturity_level', 'Unknown')
            
            maturity_data = {
                'Beginner': 1,
                'Basic': 2,
                'Intermediate': 3,
                'Advanced': 4
            }
            
            fig.add_trace(
                go.Pie(labels=list(maturity_data.keys()), values=list(maturity_data.values()), name='TL Maturity'),
                row=2, col=1
            )
        
        # Gráfico de prioridad de implementación
        if self.tl_analysis and 'overall_tl_assessment' in self.tl_analysis:
            assessment = self.tl_analysis['overall_tl_assessment']
            implementation_priority = assessment.get('tl_implementation_priority', 'Low')
            
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
            title="Dashboard de Transfer Learning",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_tl_analysis(self, filename='marketing_tl_analysis.json'):
        """Exportar análisis de transfer learning"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'tl_analysis': self.tl_analysis,
            'tl_models': {k: {'model_evaluation': v.get('model_evaluation', {})} for k, v in self.tl_models.items()},
            'tl_strategies': self.tl_strategies,
            'tl_insights': self.tl_insights,
            'summary': {
                'total_records': len(self.tl_data),
                'tl_maturity_level': self.tl_analysis.get('overall_tl_assessment', {}).get('tl_maturity_level', 'Unknown'),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de transfer learning exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de transfer learning de marketing
    tl_optimizer = MarketingTransferLearningOptimizer()
    
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
        'tl_score': np.random.uniform(0, 100, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de transfer learning de marketing
    print("📊 Cargando datos de transfer learning de marketing...")
    tl_optimizer.load_tl_data(sample_data)
    
    # Analizar capacidades de transfer learning
    print("🤖 Analizando capacidades de transfer learning...")
    tl_analysis = tl_optimizer.analyze_tl_capabilities()
    
    # Construir modelos de transfer learning
    print("🔮 Construyendo modelos de transfer learning...")
    tl_models = tl_optimizer.build_tl_models(target_variable='tl_score', model_type='classification')
    
    # Generar estrategias de transfer learning
    print("🎯 Generando estrategias de transfer learning...")
    tl_strategies = tl_optimizer.generate_tl_strategies()
    
    # Generar insights de transfer learning
    print("💡 Generando insights de transfer learning...")
    tl_insights = tl_optimizer.generate_tl_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de transfer learning...")
    dashboard = tl_optimizer.create_tl_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de transfer learning...")
    export_data = tl_optimizer.export_tl_analysis()
    
    print("✅ Sistema de optimización de transfer learning de marketing completado!")




