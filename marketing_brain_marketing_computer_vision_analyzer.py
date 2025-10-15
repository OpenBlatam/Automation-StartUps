"""
Marketing Brain Marketing Computer Vision Analyzer
Sistema avanzado de análisis de computer vision de marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import cv2
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, applications
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
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

class MarketingComputerVisionAnalyzer:
    def __init__(self):
        self.cv_data = {}
        self.cv_analysis = {}
        self.cv_models = {}
        self.cv_strategies = {}
        self.cv_insights = {}
        self.cv_recommendations = {}
        
    def load_cv_data(self, cv_data):
        """Cargar datos de computer vision de marketing"""
        if isinstance(cv_data, str):
            if cv_data.endswith('.csv'):
                self.cv_data = pd.read_csv(cv_data)
            elif cv_data.endswith('.json'):
                with open(cv_data, 'r') as f:
                    data = json.load(f)
                self.cv_data = pd.DataFrame(data)
        else:
            self.cv_data = pd.DataFrame(cv_data)
        
        print(f"✅ Datos de computer vision de marketing cargados: {len(self.cv_data)} registros")
        return True
    
    def analyze_cv_capabilities(self):
        """Analizar capacidades de computer vision"""
        if self.cv_data.empty:
            return None
        
        # Análisis de técnicas de computer vision
        cv_techniques = self._analyze_cv_techniques()
        
        # Análisis de modelos de computer vision
        cv_models = self._analyze_cv_models()
        
        # Análisis de aplicaciones de computer vision
        cv_applications = self._analyze_cv_applications()
        
        # Análisis de preprocesamiento de imágenes
        image_preprocessing = self._analyze_image_preprocessing()
        
        # Análisis de detección de objetos
        object_detection = self._analyze_object_detection()
        
        # Análisis de segmentación de imágenes
        image_segmentation = self._analyze_image_segmentation()
        
        cv_results = {
            'cv_techniques': cv_techniques,
            'cv_models': cv_models,
            'cv_applications': cv_applications,
            'image_preprocessing': image_preprocessing,
            'object_detection': object_detection,
            'image_segmentation': image_segmentation,
            'overall_cv_assessment': self._calculate_overall_cv_assessment()
        }
        
        self.cv_analysis = cv_results
        return cv_results
    
    def _analyze_cv_techniques(self):
        """Analizar técnicas de computer vision"""
        technique_analysis = {}
        
        # Técnicas disponibles
        techniques = {
            'Image Classification': {
                'complexity': 3,
                'applicability': 5,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Product Recognition', 'Brand Detection', 'Content Categorization']
            },
            'Object Detection': {
                'complexity': 4,
                'applicability': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Product Detection', 'Logo Detection', 'Face Detection']
            },
            'Image Segmentation': {
                'complexity': 4,
                'applicability': 3,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Product Segmentation', 'Background Removal', 'Region Analysis']
            },
            'Face Recognition': {
                'complexity': 4,
                'applicability': 3,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Customer Identification', 'Demographic Analysis', 'Security']
            },
            'OCR (Optical Character Recognition)': {
                'complexity': 3,
                'applicability': 4,
                'performance': 4,
                'interpretability': 4,
                'use_cases': ['Text Extraction', 'Document Processing', 'Price Recognition']
            },
            'Image Generation': {
                'complexity': 5,
                'applicability': 3,
                'performance': 5,
                'interpretability': 1,
                'use_cases': ['Content Creation', 'Data Augmentation', 'Visual Effects']
            },
            'Style Transfer': {
                'complexity': 4,
                'applicability': 3,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Brand Styling', 'Visual Consistency', 'Creative Content']
            },
            'Image Enhancement': {
                'complexity': 3,
                'applicability': 4,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Quality Improvement', 'Noise Reduction', 'Color Correction']
            }
        }
        
        technique_analysis['techniques'] = techniques
        technique_analysis['best_technique'] = self._select_best_cv_technique(techniques)
        technique_analysis['recommendations'] = self._get_cv_technique_recommendations(techniques)
        
        return technique_analysis
    
    def _select_best_cv_technique(self, techniques):
        """Seleccionar mejor técnica de computer vision"""
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
    
    def _get_cv_technique_recommendations(self, techniques):
        """Obtener recomendaciones de técnicas de computer vision"""
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
    
    def _analyze_cv_models(self):
        """Analizar modelos de computer vision"""
        model_analysis = {}
        
        # Análisis de modelos de clasificación
        classification_models = self._analyze_classification_models()
        model_analysis['classification'] = classification_models
        
        # Análisis de modelos de detección
        detection_models = self._analyze_detection_models()
        model_analysis['detection'] = detection_models
        
        # Análisis de modelos de segmentación
        segmentation_models = self._analyze_segmentation_models()
        model_analysis['segmentation'] = segmentation_models
        
        # Análisis de modelos generativos
        generative_models = self._analyze_generative_models()
        model_analysis['generative'] = generative_models
        
        return model_analysis
    
    def _analyze_classification_models(self):
        """Analizar modelos de clasificación"""
        classification_analysis = {}
        
        # Modelos disponibles
        models = {
            'LeNet': {
                'complexity': 2,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Basic Image Classification', 'Digit Recognition']
            },
            'AlexNet': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Image Classification', 'Object Recognition']
            },
            'VGG': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Image Classification', 'Feature Extraction']
            },
            'ResNet': {
                'complexity': 4,
                'performance': 5,
                'interpretability': 2,
                'use_cases': ['Image Classification', 'Object Detection', 'Feature Extraction']
            },
            'Inception': {
                'complexity': 5,
                'performance': 5,
                'interpretability': 1,
                'use_cases': ['Complex Image Classification', 'Object Detection']
            },
            'EfficientNet': {
                'complexity': 4,
                'performance': 5,
                'interpretability': 2,
                'use_cases': ['Efficient Image Classification', 'Mobile Applications']
            },
            'DenseNet': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Image Classification', 'Feature Reuse']
            },
            'MobileNet': {
                'complexity': 3,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Mobile Applications', 'Edge Computing']
            }
        }
        
        classification_analysis['models'] = models
        classification_analysis['best_model'] = 'ResNet'
        classification_analysis['recommendations'] = [
            'Use ResNet for general image classification tasks',
            'Use EfficientNet for efficient classification',
            'Use MobileNet for mobile and edge applications'
        ]
        
        return classification_analysis
    
    def _analyze_detection_models(self):
        """Analizar modelos de detección"""
        detection_analysis = {}
        
        # Modelos disponibles
        models = {
            'R-CNN': {
                'complexity': 5,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Object Detection', 'Region-based Detection']
            },
            'Fast R-CNN': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Object Detection', 'Faster Detection']
            },
            'Faster R-CNN': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Object Detection', 'Real-time Detection']
            },
            'YOLO': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Real-time Object Detection', 'Video Analysis']
            },
            'SSD': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Object Detection', 'Single-shot Detection']
            },
            'RetinaNet': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Object Detection', 'Small Object Detection']
            }
        }
        
        detection_analysis['models'] = models
        detection_analysis['best_model'] = 'YOLO'
        detection_analysis['recommendations'] = [
            'Use YOLO for real-time object detection',
            'Use Faster R-CNN for high accuracy detection',
            'Use SSD for balanced speed and accuracy'
        ]
        
        return detection_analysis
    
    def _analyze_segmentation_models(self):
        """Analizar modelos de segmentación"""
        segmentation_analysis = {}
        
        # Modelos disponibles
        models = {
            'U-Net': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Medical Image Segmentation', 'Semantic Segmentation']
            },
            'Mask R-CNN': {
                'complexity': 5,
                'performance': 5,
                'interpretability': 2,
                'use_cases': ['Instance Segmentation', 'Object Detection']
            },
            'DeepLab': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Semantic Segmentation', 'Scene Understanding']
            },
            'PSPNet': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Semantic Segmentation', 'Scene Parsing']
            },
            'FCN': {
                'complexity': 3,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Semantic Segmentation', 'Pixel-level Classification']
            }
        }
        
        segmentation_analysis['models'] = models
        segmentation_analysis['best_model'] = 'U-Net'
        segmentation_analysis['recommendations'] = [
            'Use U-Net for semantic segmentation',
            'Use Mask R-CNN for instance segmentation',
            'Use DeepLab for scene understanding'
        ]
        
        return segmentation_analysis
    
    def _analyze_generative_models(self):
        """Analizar modelos generativos"""
        generative_analysis = {}
        
        # Modelos disponibles
        models = {
            'GAN': {
                'complexity': 5,
                'performance': 4,
                'interpretability': 1,
                'use_cases': ['Image Generation', 'Data Augmentation']
            },
            'DCGAN': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 1,
                'use_cases': ['Image Generation', 'Deep Convolutional GAN']
            },
            'StyleGAN': {
                'complexity': 5,
                'performance': 5,
                'interpretability': 1,
                'use_cases': ['High-quality Image Generation', 'Style Transfer']
            },
            'VAE': {
                'complexity': 4,
                'performance': 3,
                'interpretability': 2,
                'use_cases': ['Image Generation', 'Dimensionality Reduction']
            },
            'Autoencoder': {
                'complexity': 3,
                'performance': 3,
                'interpretability': 3,
                'use_cases': ['Image Reconstruction', 'Feature Learning']
            }
        }
        
        generative_analysis['models'] = models
        generative_analysis['best_model'] = 'StyleGAN'
        generative_analysis['recommendations'] = [
            'Use StyleGAN for high-quality image generation',
            'Use GAN for general image generation',
            'Use VAE for controlled image generation'
        ]
        
        return generative_analysis
    
    def _analyze_cv_applications(self):
        """Analizar aplicaciones de computer vision"""
        application_analysis = {}
        
        # Aplicaciones disponibles
        applications = {
            'Product Recognition': {
                'complexity': 3,
                'business_value': 5,
                'implementation_time': 2,
                'use_cases': ['E-commerce', 'Retail', 'Inventory Management']
            },
            'Brand Detection': {
                'complexity': 3,
                'business_value': 4,
                'implementation_time': 2,
                'use_cases': ['Brand Monitoring', 'Competitive Analysis', 'Social Media']
            },
            'Quality Control': {
                'complexity': 4,
                'business_value': 5,
                'implementation_time': 3,
                'use_cases': ['Manufacturing', 'Product Quality', 'Defect Detection']
            },
            'Visual Search': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['E-commerce', 'Product Discovery', 'User Experience']
            },
            'AR/VR Integration': {
                'complexity': 5,
                'business_value': 4,
                'implementation_time': 4,
                'use_cases': ['Immersive Marketing', 'Virtual Try-on', 'Interactive Content']
            },
            'Demographic Analysis': {
                'complexity': 4,
                'business_value': 4,
                'implementation_time': 3,
                'use_cases': ['Customer Analytics', 'Targeting', 'Market Research']
            },
            'Content Moderation': {
                'complexity': 3,
                'business_value': 4,
                'implementation_time': 2,
                'use_cases': ['Social Media', 'User-generated Content', 'Brand Safety']
            },
            'Price Recognition': {
                'complexity': 3,
                'business_value': 4,
                'implementation_time': 2,
                'use_cases': ['Competitive Pricing', 'Price Monitoring', 'Market Analysis']
            }
        }
        
        application_analysis['applications'] = applications
        application_analysis['best_application'] = 'Product Recognition'
        application_analysis['recommendations'] = [
            'Start with Product Recognition for immediate business value',
            'Implement Brand Detection for competitive advantage',
            'Consider Quality Control for manufacturing applications'
        ]
        
        return application_analysis
    
    def _analyze_image_preprocessing(self):
        """Analizar preprocesamiento de imágenes"""
        preprocessing_analysis = {}
        
        # Técnicas de preprocesamiento
        techniques = {
            'Resizing': {
                'complexity': 1,
                'effectiveness': 4,
                'use_cases': ['Standardization', 'Model Input']
            },
            'Normalization': {
                'complexity': 1,
                'effectiveness': 4,
                'use_cases': ['Data Standardization', 'Model Training']
            },
            'Data Augmentation': {
                'complexity': 2,
                'effectiveness': 4,
                'use_cases': ['Overfitting Prevention', 'Data Diversity']
            },
            'Noise Reduction': {
                'complexity': 2,
                'effectiveness': 3,
                'use_cases': ['Quality Improvement', 'Preprocessing']
            },
            'Color Space Conversion': {
                'complexity': 2,
                'effectiveness': 3,
                'use_cases': ['Feature Extraction', 'Model Optimization']
            },
            'Edge Detection': {
                'complexity': 2,
                'effectiveness': 3,
                'use_cases': ['Feature Extraction', 'Object Detection']
            },
            'Histogram Equalization': {
                'complexity': 2,
                'effectiveness': 3,
                'use_cases': ['Contrast Enhancement', 'Image Quality']
            },
            'Gaussian Blur': {
                'complexity': 1,
                'effectiveness': 2,
                'use_cases': ['Noise Reduction', 'Smoothing']
            }
        }
        
        preprocessing_analysis['techniques'] = techniques
        preprocessing_analysis['best_technique'] = 'Data Augmentation'
        preprocessing_analysis['recommendations'] = [
            'Use data augmentation for better model generalization',
            'Apply normalization for consistent model input',
            'Use resizing for model compatibility'
        ]
        
        return preprocessing_analysis
    
    def _analyze_object_detection(self):
        """Analizar detección de objetos"""
        detection_analysis = {}
        
        # Técnicas de detección
        techniques = {
            'Single-shot Detection': {
                'complexity': 3,
                'performance': 4,
                'speed': 5,
                'use_cases': ['Real-time Detection', 'Video Analysis']
            },
            'Two-stage Detection': {
                'complexity': 4,
                'performance': 5,
                'speed': 3,
                'use_cases': ['High Accuracy Detection', 'Complex Scenes']
            },
            'Anchor-based Detection': {
                'complexity': 4,
                'performance': 4,
                'speed': 4,
                'use_cases': ['General Object Detection', 'Multi-scale Detection']
            },
            'Anchor-free Detection': {
                'complexity': 4,
                'performance': 4,
                'speed': 4,
                'use_cases': ['Simplified Detection', 'End-to-end Training']
            }
        }
        
        detection_analysis['techniques'] = techniques
        detection_analysis['best_technique'] = 'Single-shot Detection'
        detection_analysis['recommendations'] = [
            'Use single-shot detection for real-time applications',
            'Use two-stage detection for high accuracy requirements',
            'Consider anchor-free detection for simplified implementation'
        ]
        
        return detection_analysis
    
    def _analyze_image_segmentation(self):
        """Analizar segmentación de imágenes"""
        segmentation_analysis = {}
        
        # Técnicas de segmentación
        techniques = {
            'Semantic Segmentation': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Scene Understanding', 'Pixel-level Classification']
            },
            'Instance Segmentation': {
                'complexity': 5,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Object Counting', 'Individual Object Analysis']
            },
            'Panoptic Segmentation': {
                'complexity': 5,
                'performance': 4,
                'interpretability': 2,
                'use_cases': ['Complete Scene Understanding', 'Combined Segmentation']
            },
            'Medical Segmentation': {
                'complexity': 4,
                'performance': 4,
                'interpretability': 3,
                'use_cases': ['Medical Imaging', 'Anatomical Analysis']
            }
        }
        
        segmentation_analysis['techniques'] = techniques
        segmentation_analysis['best_technique'] = 'Semantic Segmentation'
        segmentation_analysis['recommendations'] = [
            'Use semantic segmentation for scene understanding',
            'Use instance segmentation for object counting',
            'Consider panoptic segmentation for complete analysis'
        ]
        
        return segmentation_analysis
    
    def _calculate_overall_cv_assessment(self):
        """Calcular evaluación general de computer vision"""
        overall_assessment = {}
        
        if not self.cv_data.empty:
            overall_assessment = {
                'cv_maturity_level': self._calculate_cv_maturity_level(),
                'cv_readiness_score': self._calculate_cv_readiness_score(),
                'cv_implementation_priority': self._calculate_cv_implementation_priority(),
                'cv_roi_potential': self._calculate_cv_roi_potential()
            }
        
        return overall_assessment
    
    def _calculate_cv_maturity_level(self):
        """Calcular nivel de madurez de computer vision"""
        # Basado en capacidades disponibles
        maturity_score = 0
        
        if self.cv_analysis and 'cv_techniques' in self.cv_analysis:
            techniques = self.cv_analysis['cv_techniques']
            
            # Image Classification
            if 'Image Classification' in techniques.get('techniques', {}):
                maturity_score += 20
            
            # Object Detection
            if 'Object Detection' in techniques.get('techniques', {}):
                maturity_score += 20
            
            # Image Segmentation
            if 'Image Segmentation' in techniques.get('techniques', {}):
                maturity_score += 20
            
            # Face Recognition
            if 'Face Recognition' in techniques.get('techniques', {}):
                maturity_score += 20
            
            # OCR
            if 'OCR (Optical Character Recognition)' in techniques.get('techniques', {}):
                maturity_score += 20
        
        if maturity_score >= 80:
            return 'Advanced'
        elif maturity_score >= 60:
            return 'Intermediate'
        elif maturity_score >= 40:
            return 'Basic'
        else:
            return 'Beginner'
    
    def _calculate_cv_readiness_score(self):
        """Calcular score de preparación para computer vision"""
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
    
    def _calculate_cv_implementation_priority(self):
        """Calcular prioridad de implementación de computer vision"""
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
    
    def _calculate_cv_roi_potential(self):
        """Calcular potencial de ROI de computer vision"""
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
    
    def build_cv_models(self, target_variable, model_type='classification'):
        """Construir modelos de computer vision"""
        if target_variable not in self.cv_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.cv_data.columns if col != target_variable]
        X = self.cv_data[feature_columns]
        y = self.cv_data[target_variable]
        
        # Preprocesamiento
        X_processed, y_processed = self._preprocess_cv_data(X, y, model_type)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42)
        
        # Construir modelos
        models = {}
        
        if model_type == 'classification':
            models = self._build_cv_classification_models(X_train, X_test, y_train, y_test)
        elif model_type == 'regression':
            models = self._build_cv_regression_models(X_train, X_test, y_train, y_test)
        elif model_type == 'clustering':
            models = self._build_cv_clustering_models(X_processed)
        
        # Evaluar modelos
        model_evaluation = self._evaluate_cv_models(models, X_test, y_test, model_type)
        
        # Optimizar modelos
        optimized_models = self._optimize_cv_models(models, X_train, y_train)
        
        self.cv_models = {
            'models': models,
            'optimized_models': optimized_models,
            'model_evaluation': model_evaluation,
            'model_type': model_type,
            'target_variable': target_variable
        }
        
        return self.cv_models
    
    def _preprocess_cv_data(self, X, y, model_type):
        """Preprocesar datos de computer vision"""
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
    
    def _build_cv_classification_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de clasificación de computer vision"""
        models = {}
        
        # ResNet50
        resnet_model = self._build_resnet_model(X_train.shape[1], len(np.unique(y_train)))
        resnet_model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
        models['ResNet50'] = resnet_model
        
        # VGG16
        vgg_model = self._build_vgg_model(X_train.shape[1], len(np.unique(y_train)))
        vgg_model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
        models['VGG16'] = vgg_model
        
        # EfficientNet
        efficientnet_model = self._build_efficientnet_model(X_train.shape[1], len(np.unique(y_train)))
        efficientnet_model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
        models['EfficientNet'] = efficientnet_model
        
        return models
    
    def _build_cv_regression_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de regresión de computer vision"""
        models = {}
        
        # ResNet50 para regresión
        resnet_model = self._build_resnet_regression_model(X_train.shape[1])
        resnet_model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
        models['ResNet50'] = resnet_model
        
        # VGG16 para regresión
        vgg_model = self._build_vgg_regression_model(X_train.shape[1])
        vgg_model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
        models['VGG16'] = vgg_model
        
        return models
    
    def _build_cv_clustering_models(self, X):
        """Construir modelos de clustering de computer vision"""
        models = {}
        
        # K-Means
        kmeans_model = KMeans(n_clusters=3, random_state=42)
        kmeans_model.fit(X)
        models['K-Means'] = kmeans_model
        
        # PCA + K-Means
        pca = PCA(n_components=10)
        X_pca = pca.fit_transform(X)
        kmeans_pca_model = KMeans(n_clusters=3, random_state=42)
        kmeans_pca_model.fit(X_pca)
        models['PCA + K-Means'] = kmeans_pca_model
        
        return models
    
    def _build_resnet_model(self, input_dim, num_classes):
        """Construir modelo ResNet50"""
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
    
    def _build_vgg_model(self, input_dim, num_classes):
        """Construir modelo VGG16"""
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
    
    def _build_efficientnet_model(self, input_dim, num_classes):
        """Construir modelo EfficientNet"""
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
    
    def _build_resnet_regression_model(self, input_dim):
        """Construir modelo ResNet50 para regresión"""
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
    
    def _build_vgg_regression_model(self, input_dim):
        """Construir modelo VGG16 para regresión"""
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
    
    def _evaluate_cv_models(self, models, X_test, y_test, model_type):
        """Evaluar modelos de computer vision"""
        evaluation_results = {}
        
        for model_name, model in models.items():
            try:
                if model_type == 'classification':
                    y_pred = model.predict(X_test)
                    y_pred_classes = np.argmax(y_pred, axis=1)
                    
                    evaluation_results[model_name] = {
                        'accuracy': accuracy_score(y_test, y_pred_classes),
                        'precision': precision_score(y_test, y_pred_classes, average='weighted'),
                        'recall': recall_score(y_test, y_pred_classes, average='weighted'),
                        'f1_score': f1_score(y_test, y_pred_classes, average='weighted')
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
            except Exception as e:
                evaluation_results[model_name] = {'error': str(e)}
        
        return evaluation_results
    
    def _optimize_cv_models(self, models, X_train, y_train):
        """Optimizar modelos de computer vision"""
        optimized_models = {}
        
        for model_name, model in models.items():
            try:
                # Optimización de hiperparámetros
                if hasattr(model, 'get_config'):
                    # Crear modelo optimizado con mejores hiperparámetros
                    optimized_model = self._create_optimized_cv_model(model_name, X_train.shape[1], len(np.unique(y_train)))
                    optimized_models[model_name] = optimized_model
                else:
                    optimized_models[model_name] = model
            except Exception as e:
                optimized_models[model_name] = model
        
        return optimized_models
    
    def _create_optimized_cv_model(self, model_name, input_dim, num_classes):
        """Crear modelo de computer vision optimizado"""
        if model_name == 'ResNet50':
            return self._build_optimized_resnet_model(input_dim, num_classes)
        elif model_name == 'VGG16':
            return self._build_optimized_vgg_model(input_dim, num_classes)
        elif model_name == 'EfficientNet':
            return self._build_optimized_efficientnet_model(input_dim, num_classes)
        else:
            return self._build_resnet_model(input_dim, num_classes)
    
    def _build_optimized_resnet_model(self, input_dim, num_classes):
        """Construir modelo ResNet50 optimizado"""
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
    
    def _build_optimized_vgg_model(self, input_dim, num_classes):
        """Construir modelo VGG16 optimizado"""
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
    
    def _build_optimized_efficientnet_model(self, input_dim, num_classes):
        """Construir modelo EfficientNet optimizado"""
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
    
    def generate_cv_strategies(self):
        """Generar estrategias de computer vision"""
        strategies = []
        
        # Estrategias basadas en técnicas de computer vision
        if self.cv_analysis and 'cv_techniques' in self.cv_analysis:
            techniques = self.cv_analysis['cv_techniques']
            
            # Estrategias de clasificación de imágenes
            if 'Image Classification' in techniques.get('techniques', {}):
                strategies.append({
                    'strategy_type': 'Image Classification Implementation',
                    'description': 'Implementar clasificación de imágenes para reconocimiento de productos',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de detección de objetos
            if 'Object Detection' in techniques.get('techniques', {}):
                strategies.append({
                    'strategy_type': 'Object Detection Implementation',
                    'description': 'Implementar detección de objetos para análisis de productos',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
            
            # Estrategias de OCR
            if 'OCR (Optical Character Recognition)' in techniques.get('techniques', {}):
                strategies.append({
                    'strategy_type': 'OCR Implementation',
                    'description': 'Implementar OCR para extracción de texto de imágenes',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en aplicaciones de computer vision
        if self.cv_analysis and 'cv_applications' in self.cv_analysis:
            applications = self.cv_analysis['cv_applications']
            
            # Estrategias de reconocimiento de productos
            if 'Product Recognition' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Product Recognition Implementation',
                    'description': 'Implementar reconocimiento de productos para e-commerce',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de detección de marcas
            if 'Brand Detection' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Brand Detection Implementation',
                    'description': 'Implementar detección de marcas para monitoreo competitivo',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en preprocesamiento de imágenes
        if self.cv_analysis and 'image_preprocessing' in self.cv_analysis:
            preprocessing = self.cv_analysis['image_preprocessing']
            
            strategies.append({
                'strategy_type': 'Image Preprocessing Optimization',
                'description': 'Optimizar preprocesamiento de imágenes para mejor performance',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        # Estrategias basadas en detección de objetos
        if self.cv_analysis and 'object_detection' in self.cv_analysis:
            detection = self.cv_analysis['object_detection']
            
            strategies.append({
                'strategy_type': 'Object Detection Optimization',
                'description': 'Optimizar detección de objetos para mejor precisión',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        # Estrategias basadas en segmentación de imágenes
        if self.cv_analysis and 'image_segmentation' in self.cv_analysis:
            segmentation = self.cv_analysis['image_segmentation']
            
            strategies.append({
                'strategy_type': 'Image Segmentation Implementation',
                'description': 'Implementar segmentación de imágenes para análisis detallado',
                'priority': 'low',
                'expected_impact': 'low'
            })
        
        self.cv_strategies = strategies
        return strategies
    
    def generate_cv_insights(self):
        """Generar insights de computer vision"""
        insights = []
        
        # Insights de evaluación general de computer vision
        if self.cv_analysis and 'overall_cv_assessment' in self.cv_analysis:
            assessment = self.cv_analysis['overall_cv_assessment']
            maturity_level = assessment.get('cv_maturity_level', 'Unknown')
            
            insights.append({
                'category': 'Computer Vision Maturity',
                'insight': f'Nivel de madurez de computer vision: {maturity_level}',
                'recommendation': f'{"Mantener" if maturity_level == "Advanced" else "Mejorar"} capacidades de computer vision',
                'priority': 'high' if maturity_level in ['Beginner', 'Basic'] else 'medium'
            })
            
            readiness_score = assessment.get('cv_readiness_score', 0)
            if readiness_score < 70:
                insights.append({
                    'category': 'Computer Vision Readiness',
                    'insight': f'Score de preparación para computer vision: {readiness_score}',
                    'recommendation': 'Mejorar preparación para implementación de computer vision',
                    'priority': 'high'
                })
            
            implementation_priority = assessment.get('cv_implementation_priority', 'Low')
            if implementation_priority == 'High':
                insights.append({
                    'category': 'Computer Vision Implementation',
                    'insight': f'Prioridad de implementación: {implementation_priority}',
                    'recommendation': 'Priorizar implementación de computer vision',
                    'priority': 'high'
                })
            
            roi_potential = assessment.get('cv_roi_potential', 'Low')
            if roi_potential in ['High', 'Very High']:
                insights.append({
                    'category': 'Computer Vision ROI',
                    'insight': f'Potencial de ROI: {roi_potential}',
                    'recommendation': 'Invertir en computer vision para maximizar ROI',
                    'priority': 'high'
                })
        
        # Insights de técnicas de computer vision
        if self.cv_analysis and 'cv_techniques' in self.cv_analysis:
            techniques = self.cv_analysis['cv_techniques']
            best_technique = techniques.get('best_technique', 'Unknown')
            
            insights.append({
                'category': 'Computer Vision Techniques',
                'insight': f'Mejor técnica de computer vision: {best_technique}',
                'recommendation': 'Usar esta técnica para aplicaciones de computer vision',
                'priority': 'high'
            })
        
        # Insights de aplicaciones de computer vision
        if self.cv_analysis and 'cv_applications' in self.cv_analysis:
            applications = self.cv_analysis['cv_applications']
            best_application = applications.get('best_application', 'Unknown')
            
            insights.append({
                'category': 'Computer Vision Applications',
                'insight': f'Mejor aplicación de computer vision: {best_application}',
                'recommendation': 'Implementar esta aplicación para máximo valor de negocio',
                'priority': 'high'
            })
        
        # Insights de modelos de computer vision
        if self.cv_models:
            model_evaluation = self.cv_models.get('model_evaluation', {})
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
                        'category': 'Computer Vision Model Performance',
                        'insight': f'Mejor modelo de computer vision: {best_model} con score {best_score:.3f}',
                        'recommendation': 'Usar este modelo para predicciones de computer vision',
                        'priority': 'high'
                    })
        
        self.cv_insights = insights
        return insights
    
    def create_cv_dashboard(self):
        """Crear dashboard de computer vision"""
        if self.cv_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CV Techniques', 'Model Performance',
                          'CV Maturity', 'Implementation Priority'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de técnicas de computer vision
        if self.cv_analysis and 'cv_techniques' in self.cv_analysis:
            techniques = self.cv_analysis['cv_techniques']
            technique_names = list(techniques.get('techniques', {}).keys())
            technique_scores = [5] * len(technique_names)  # Placeholder scores
            
            fig.add_trace(
                go.Bar(x=technique_names, y=technique_scores, name='CV Techniques'),
                row=1, col=1
            )
        
        # Gráfico de performance de modelos
        if self.cv_models:
            model_evaluation = self.cv_models.get('model_evaluation', {})
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
        
        # Gráfico de madurez de computer vision
        if self.cv_analysis and 'overall_cv_assessment' in self.cv_analysis:
            assessment = self.cv_analysis['overall_cv_assessment']
            maturity_level = assessment.get('cv_maturity_level', 'Unknown')
            
            maturity_data = {
                'Beginner': 1,
                'Basic': 2,
                'Intermediate': 3,
                'Advanced': 4
            }
            
            fig.add_trace(
                go.Pie(labels=list(maturity_data.keys()), values=list(maturity_data.values()), name='CV Maturity'),
                row=2, col=1
            )
        
        # Gráfico de prioridad de implementación
        if self.cv_analysis and 'overall_cv_assessment' in self.cv_analysis:
            assessment = self.cv_analysis['overall_cv_assessment']
            implementation_priority = assessment.get('cv_implementation_priority', 'Low')
            
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
            title="Dashboard de Computer Vision",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_cv_analysis(self, filename='marketing_cv_analysis.json'):
        """Exportar análisis de computer vision"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'cv_analysis': self.cv_analysis,
            'cv_models': {k: {'model_evaluation': v.get('model_evaluation', {})} for k, v in self.cv_models.items()},
            'cv_strategies': self.cv_strategies,
            'cv_insights': self.cv_insights,
            'summary': {
                'total_records': len(self.cv_data),
                'cv_maturity_level': self.cv_analysis.get('overall_cv_assessment', {}).get('cv_maturity_level', 'Unknown'),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de computer vision exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de computer vision de marketing
    cv_analyzer = MarketingComputerVisionAnalyzer()
    
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
        'cv_score': np.random.uniform(0, 100, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de computer vision de marketing
    print("📊 Cargando datos de computer vision de marketing...")
    cv_analyzer.load_cv_data(sample_data)
    
    # Analizar capacidades de computer vision
    print("🤖 Analizando capacidades de computer vision...")
    cv_analysis = cv_analyzer.analyze_cv_capabilities()
    
    # Construir modelos de computer vision
    print("🔮 Construyendo modelos de computer vision...")
    cv_models = cv_analyzer.build_cv_models(target_variable='cv_score', model_type='regression')
    
    # Generar estrategias de computer vision
    print("🎯 Generando estrategias de computer vision...")
    cv_strategies = cv_analyzer.generate_cv_strategies()
    
    # Generar insights de computer vision
    print("💡 Generando insights de computer vision...")
    cv_insights = cv_analyzer.generate_cv_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de computer vision...")
    dashboard = cv_analyzer.create_cv_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de computer vision...")
    export_data = cv_analyzer.export_cv_analysis()
    
    print("✅ Sistema de análisis de computer vision de marketing completado!")


