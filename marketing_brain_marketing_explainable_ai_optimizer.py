"""
Marketing Brain Marketing Explainable AI Optimizer
Motor avanzado de optimización de Explainable AI de marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers
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

class MarketingExplainableAIOptimizer:
    def __init__(self):
        self.xai_data = {}
        self.xai_analysis = {}
        self.xai_models = {}
        self.xai_strategies = {}
        self.xai_insights = {}
        self.xai_recommendations = {}
        
    def load_xai_data(self, xai_data):
        """Cargar datos de Explainable AI de marketing"""
        if isinstance(xai_data, str):
            if xai_data.endswith('.csv'):
                self.xai_data = pd.read_csv(xai_data)
            elif xai_data.endswith('.json'):
                with open(xai_data, 'r') as f:
                    data = json.load(f)
                self.xai_data = pd.DataFrame(data)
        else:
            self.xai_data = pd.DataFrame(xai_data)
        
        print(f"✅ Datos de Explainable AI de marketing cargados: {len(self.xai_data)} registros")
        return True
    
    def analyze_xai_capabilities(self):
        """Analizar capacidades de Explainable AI"""
        if self.xai_data.empty:
            return None
        
        # Análisis de técnicas de Explainable AI
        xai_techniques = self._analyze_xai_techniques()
        
        # Análisis de interpretabilidad de modelos
        model_interpretability = self._analyze_model_interpretability()
        
        # Análisis de aplicaciones de Explainable AI
        xai_applications = self._analyze_xai_applications()
        
        # Análisis de explicabilidad local vs global
        local_global_explainability = self._analyze_local_global_explainability()
        
        # Análisis de transparencia y confiabilidad
        transparency_trust = self._analyze_transparency_trust()
        
        # Análisis de regulaciones y compliance
        regulations_compliance = self._analyze_regulations_compliance()
        
        xai_results = {
            'xai_techniques': xai_techniques,
            'model_interpretability': model_interpretability,
            'xai_applications': xai_applications,
            'local_global_explainability': local_global_explainability,
            'transparency_trust': transparency_trust,
            'regulations_compliance': regulations_compliance,
            'overall_xai_assessment': self._calculate_overall_xai_assessment()
        }
        
        self.xai_analysis = xai_results
        return xai_results
    
    def _analyze_xai_techniques(self):
        """Analizar técnicas de Explainable AI"""
        technique_analysis = {}
        
        # Análisis de técnicas de post-hoc explanation
        post_hoc_explanations = self._analyze_post_hoc_explanations()
        technique_analysis['post_hoc_explanations'] = post_hoc_explanations
        
        # Análisis de técnicas de intrinsic interpretability
        intrinsic_interpretability = self._analyze_intrinsic_interpretability()
        technique_analysis['intrinsic_interpretability'] = intrinsic_interpretability
        
        # Análisis de técnicas de model-agnostic
        model_agnostic = self._analyze_model_agnostic()
        technique_analysis['model_agnostic'] = model_agnostic
        
        # Análisis de técnicas de feature importance
        feature_importance = self._analyze_feature_importance()
        technique_analysis['feature_importance'] = feature_importance
        
        return technique_analysis
    
    def _analyze_post_hoc_explanations(self):
        """Analizar técnicas de post-hoc explanation"""
        post_hoc_analysis = {}
        
        # Técnicas disponibles
        techniques = {
            'LIME (Local Interpretable Model-agnostic Explanations)': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Local Explanations', 'Model-agnostic', 'Feature Importance']
            },
            'SHAP (SHapley Additive exPlanations)': {
                'complexity': 4,
                'interpretability': 5,
                'accuracy': 4,
                'use_cases': ['Global and Local Explanations', 'Feature Attribution', 'Model Understanding']
            },
            'Integrated Gradients': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 4,
                'use_cases': ['Deep Learning Models', 'Gradient-based', 'Feature Attribution']
            },
            'Grad-CAM (Gradient-weighted Class Activation Mapping)': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 4,
                'use_cases': ['Computer Vision', 'CNN Models', 'Visual Explanations']
            },
            'Attention Mechanisms': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 4,
                'use_cases': ['NLP Models', 'Transformer Models', 'Attention Visualization']
            },
            'Counterfactual Explanations': {
                'complexity': 4,
                'interpretability': 5,
                'accuracy': 3,
                'use_cases': ['What-if Analysis', 'Decision Understanding', 'Alternative Scenarios']
            }
        }
        
        post_hoc_analysis['techniques'] = techniques
        post_hoc_analysis['best_technique'] = 'SHAP (SHapley Additive exPlanations)'
        post_hoc_analysis['recommendations'] = [
            'Use SHAP for comprehensive explanations',
            'Use LIME for local explanations',
            'Use Integrated Gradients for deep learning models'
        ]
        
        return post_hoc_analysis
    
    def _analyze_intrinsic_interpretability(self):
        """Analizar técnicas de intrinsic interpretability"""
        intrinsic_analysis = {}
        
        # Técnicas disponibles
        techniques = {
            'Linear Models': {
                'complexity': 1,
                'interpretability': 5,
                'accuracy': 2,
                'use_cases': ['Simple Models', 'High Interpretability', 'Linear Relationships']
            },
            'Decision Trees': {
                'complexity': 2,
                'interpretability': 5,
                'accuracy': 3,
                'use_cases': ['Rule-based Models', 'Tree Visualization', 'Decision Paths']
            },
            'Random Forest': {
                'complexity': 2,
                'interpretability': 4,
                'accuracy': 4,
                'use_cases': ['Ensemble Models', 'Feature Importance', 'Robust Predictions']
            },
            'Gradient Boosting': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 4,
                'use_cases': ['High Performance', 'Feature Importance', 'Ensemble Learning']
            },
            'Rule-based Systems': {
                'complexity': 2,
                'interpretability': 5,
                'accuracy': 3,
                'use_cases': ['Expert Systems', 'Business Rules', 'Transparent Logic']
            },
            'Generalized Additive Models (GAM)': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Non-linear Relationships', 'Additive Models', 'Smooth Functions']
            }
        }
        
        intrinsic_analysis['techniques'] = techniques
        intrinsic_analysis['best_technique'] = 'Decision Trees'
        intrinsic_analysis['recommendations'] = [
            'Use Decision Trees for high interpretability',
            'Use Random Forest for balanced performance and interpretability',
            'Consider Linear Models for simple, interpretable solutions'
        ]
        
        return intrinsic_analysis
    
    def _analyze_model_agnostic(self):
        """Analizar técnicas de model-agnostic"""
        model_agnostic_analysis = {}
        
        # Técnicas disponibles
        techniques = {
            'Permutation Importance': {
                'complexity': 2,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Feature Importance', 'Model Validation', 'Any Model Type']
            },
            'Partial Dependence Plots': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Feature Effects', 'Non-linear Relationships', 'Model Understanding']
            },
            'Individual Conditional Expectation (ICE)': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Individual Predictions', 'Heterogeneous Effects', 'Model Understanding']
            },
            'Accumulated Local Effects (ALE)': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Feature Effects', 'Correlated Features', 'Model Understanding']
            },
            'Surrogate Models': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Model Approximation', 'Simplified Explanations', 'Any Model Type']
            },
            'Global Surrogate Models': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Model Approximation', 'Global Understanding', 'Any Model Type']
            }
        }
        
        model_agnostic_analysis['techniques'] = techniques
        model_agnostic_analysis['best_technique'] = 'Permutation Importance'
        model_agnostic_analysis['recommendations'] = [
            'Use Permutation Importance for feature importance',
            'Use Partial Dependence Plots for feature effects',
            'Consider Surrogate Models for model approximation'
        ]
        
        return model_agnostic_analysis
    
    def _analyze_feature_importance(self):
        """Analizar técnicas de feature importance"""
        feature_analysis = {}
        
        # Técnicas disponibles
        techniques = {
            'SHAP Values': {
                'complexity': 4,
                'interpretability': 5,
                'accuracy': 4,
                'use_cases': ['Feature Attribution', 'Global and Local', 'Any Model Type']
            },
            'Permutation Importance': {
                'complexity': 2,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Feature Importance', 'Model Validation', 'Any Model Type']
            },
            'Feature Selection': {
                'complexity': 2,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Feature Ranking', 'Dimensionality Reduction', 'Model Simplification']
            },
            'Mutual Information': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Feature Relevance', 'Non-linear Relationships', 'Information Theory']
            },
            'Correlation Analysis': {
                'complexity': 1,
                'interpretability': 4,
                'accuracy': 2,
                'use_cases': ['Linear Relationships', 'Feature Dependencies', 'Simple Analysis']
            },
            'Recursive Feature Elimination': {
                'complexity': 3,
                'interpretability': 4,
                'accuracy': 3,
                'use_cases': ['Feature Selection', 'Model Optimization', 'Iterative Selection']
            }
        }
        
        feature_analysis['techniques'] = techniques
        feature_analysis['best_technique'] = 'SHAP Values'
        feature_analysis['recommendations'] = [
            'Use SHAP Values for comprehensive feature attribution',
            'Use Permutation Importance for simple feature importance',
            'Consider Feature Selection for model simplification'
        ]
        
        return feature_analysis
    
    def _analyze_model_interpretability(self):
        """Analizar interpretabilidad de modelos"""
        interpretability_analysis = {}
        
        # Tipos de interpretabilidad
        interpretability_types = {
            'Global Interpretability': {
                'complexity': 3,
                'usefulness': 4,
                'scope': 5,
                'use_cases': ['Model Understanding', 'Feature Importance', 'Overall Behavior']
            },
            'Local Interpretability': {
                'complexity': 2,
                'usefulness': 4,
                'scope': 3,
                'use_cases': ['Individual Predictions', 'Specific Cases', 'Decision Understanding']
            },
            'Post-hoc Interpretability': {
                'complexity': 3,
                'usefulness': 4,
                'scope': 4,
                'use_cases': ['Model Analysis', 'Explanation Generation', 'Any Model Type']
            },
            'Intrinsic Interpretability': {
                'complexity': 2,
                'usefulness': 4,
                'scope': 3,
                'use_cases': ['Built-in Explanations', 'Transparent Models', 'Simple Models']
            },
            'Contrastive Explanations': {
                'complexity': 4,
                'usefulness': 4,
                'scope': 3,
                'use_cases': ['What-if Analysis', 'Alternative Scenarios', 'Decision Understanding']
            },
            'Causal Explanations': {
                'complexity': 5,
                'usefulness': 5,
                'scope': 4,
                'use_cases': ['Causal Relationships', 'Intervention Analysis', 'Causal Inference']
            }
        }
        
        interpretability_analysis['types'] = interpretability_types
        interpretability_analysis['best_type'] = 'Global Interpretability'
        interpretability_analysis['recommendations'] = [
            'Use Global Interpretability for overall model understanding',
            'Use Local Interpretability for individual predictions',
            'Consider Post-hoc Interpretability for any model type'
        ]
        
        return interpretability_analysis
    
    def _analyze_xai_applications(self):
        """Analizar aplicaciones de Explainable AI"""
        application_analysis = {}
        
        # Aplicaciones disponibles
        applications = {
            'Financial Services': {
                'complexity': 4,
                'regulatory_importance': 5,
                'business_value': 5,
                'use_cases': ['Credit Scoring', 'Risk Assessment', 'Regulatory Compliance']
            },
            'Healthcare': {
                'complexity': 5,
                'regulatory_importance': 5,
                'business_value': 5,
                'use_cases': ['Medical Diagnosis', 'Treatment Recommendations', 'Patient Safety']
            },
            'Marketing Analytics': {
                'complexity': 3,
                'regulatory_importance': 3,
                'business_value': 4,
                'use_cases': ['Customer Segmentation', 'Campaign Optimization', 'Personalization']
            },
            'Human Resources': {
                'complexity': 4,
                'regulatory_importance': 4,
                'business_value': 4,
                'use_cases': ['Hiring Decisions', 'Performance Evaluation', 'Bias Detection']
            },
            'Autonomous Vehicles': {
                'complexity': 5,
                'regulatory_importance': 5,
                'business_value': 4,
                'use_cases': ['Decision Making', 'Safety Systems', 'Accident Analysis']
            },
            'Criminal Justice': {
                'complexity': 5,
                'regulatory_importance': 5,
                'business_value': 3,
                'use_cases': ['Risk Assessment', 'Sentencing', 'Bias Detection']
            },
            'Insurance': {
                'complexity': 4,
                'regulatory_importance': 4,
                'business_value': 4,
                'use_cases': ['Risk Assessment', 'Claims Processing', 'Pricing']
            },
            'E-commerce': {
                'complexity': 3,
                'regulatory_importance': 2,
                'business_value': 4,
                'use_cases': ['Recommendation Systems', 'Fraud Detection', 'Customer Experience']
            }
        }
        
        application_analysis['applications'] = applications
        application_analysis['best_application'] = 'Financial Services'
        application_analysis['recommendations'] = [
            'Start with Financial Services for regulatory compliance',
            'Implement Healthcare applications for patient safety',
            'Consider Marketing Analytics for business value'
        ]
        
        return application_analysis
    
    def _analyze_local_global_explainability(self):
        """Analizar explicabilidad local vs global"""
        explainability_analysis = {}
        
        # Tipos de explicabilidad
        explainability_types = {
            'Local Explanations': {
                'scope': 'Individual Predictions',
                'complexity': 2,
                'usefulness': 4,
                'use_cases': ['Specific Cases', 'Decision Understanding', 'Individual Analysis']
            },
            'Global Explanations': {
                'scope': 'Overall Model Behavior',
                'complexity': 3,
                'usefulness': 4,
                'use_cases': ['Model Understanding', 'Feature Importance', 'Overall Behavior']
            },
            'Hybrid Explanations': {
                'scope': 'Both Local and Global',
                'complexity': 4,
                'usefulness': 5,
                'use_cases': ['Comprehensive Understanding', 'Multi-level Analysis', 'Complete Picture']
            },
            'Contrastive Explanations': {
                'scope': 'Alternative Scenarios',
                'complexity': 4,
                'usefulness': 4,
                'use_cases': ['What-if Analysis', 'Decision Alternatives', 'Scenario Comparison']
            },
            'Causal Explanations': {
                'scope': 'Causal Relationships',
                'complexity': 5,
                'usefulness': 5,
                'use_cases': ['Causal Inference', 'Intervention Analysis', 'Causal Understanding']
            }
        }
        
        explainability_analysis['types'] = explainability_types
        explainability_analysis['best_type'] = 'Hybrid Explanations'
        explainability_analysis['recommendations'] = [
            'Use Hybrid Explanations for comprehensive understanding',
            'Use Local Explanations for individual predictions',
            'Consider Global Explanations for model understanding'
        ]
        
        return explainability_analysis
    
    def _analyze_transparency_trust(self):
        """Analizar transparencia y confiabilidad"""
        transparency_analysis = {}
        
        # Aspectos de transparencia y confiabilidad
        aspects = {
            'Model Transparency': {
                'importance': 5,
                'implementation_difficulty': 3,
                'business_impact': 4,
                'use_cases': ['Model Understanding', 'Stakeholder Trust', 'Regulatory Compliance']
            },
            'Decision Transparency': {
                'importance': 5,
                'implementation_difficulty': 3,
                'business_impact': 4,
                'use_cases': ['Decision Understanding', 'User Trust', 'Accountability']
            },
            'Data Transparency': {
                'importance': 4,
                'implementation_difficulty': 2,
                'business_impact': 3,
                'use_cases': ['Data Understanding', 'Bias Detection', 'Data Quality']
            },
            'Algorithm Transparency': {
                'importance': 4,
                'implementation_difficulty': 3,
                'business_impact': 3,
                'use_cases': ['Algorithm Understanding', 'Technical Trust', 'Performance Analysis']
            },
            'Process Transparency': {
                'importance': 4,
                'implementation_difficulty': 2,
                'business_impact': 3,
                'use_cases': ['Process Understanding', 'Workflow Trust', 'Process Improvement']
            },
            'Outcome Transparency': {
                'importance': 5,
                'implementation_difficulty': 2,
                'business_impact': 4,
                'use_cases': ['Result Understanding', 'Outcome Trust', 'Performance Evaluation']
            }
        }
        
        transparency_analysis['aspects'] = aspects
        transparency_analysis['best_aspect'] = 'Model Transparency'
        transparency_analysis['recommendations'] = [
            'Focus on Model Transparency for stakeholder trust',
            'Implement Decision Transparency for user trust',
            'Consider Data Transparency for bias detection'
        ]
        
        return transparency_analysis
    
    def _analyze_regulations_compliance(self):
        """Analizar regulaciones y compliance"""
        compliance_analysis = {}
        
        # Regulaciones y estándares
        regulations = {
            'GDPR (General Data Protection Regulation)': {
                'importance': 5,
                'complexity': 4,
                'business_impact': 5,
                'use_cases': ['Data Privacy', 'Right to Explanation', 'EU Compliance']
            },
            'CCPA (California Consumer Privacy Act)': {
                'importance': 4,
                'complexity': 3,
                'business_impact': 4,
                'use_cases': ['Data Privacy', 'Consumer Rights', 'California Compliance']
            },
            'AI Act (EU)': {
                'importance': 5,
                'complexity': 5,
                'business_impact': 5,
                'use_cases': ['AI Regulation', 'High-risk AI', 'EU Compliance']
            },
            'Algorithmic Accountability Act': {
                'importance': 4,
                'complexity': 4,
                'business_impact': 4,
                'use_cases': ['Algorithmic Transparency', 'Bias Detection', 'US Compliance']
            },
            'Fair Credit Reporting Act (FCRA)': {
                'importance': 4,
                'complexity': 3,
                'business_impact': 4,
                'use_cases': ['Credit Decisions', 'Financial Services', 'US Compliance']
            },
            'Equal Credit Opportunity Act (ECOA)': {
                'importance': 4,
                'complexity': 3,
                'business_impact': 4,
                'use_cases': ['Credit Decisions', 'Fair Lending', 'US Compliance']
            }
        }
        
        compliance_analysis['regulations'] = regulations
        compliance_analysis['most_important'] = 'GDPR (General Data Protection Regulation)'
        compliance_analysis['recommendations'] = [
            'Prioritize GDPR compliance for EU operations',
            'Implement AI Act requirements for high-risk AI',
            'Consider Algorithmic Accountability Act for transparency'
        ]
        
        return compliance_analysis
    
    def _calculate_overall_xai_assessment(self):
        """Calcular evaluación general de Explainable AI"""
        overall_assessment = {}
        
        if not self.xai_data.empty:
            overall_assessment = {
                'xai_maturity_level': self._calculate_xai_maturity_level(),
                'xai_readiness_score': self._calculate_xai_readiness_score(),
                'xai_implementation_priority': self._calculate_xai_implementation_priority(),
                'xai_roi_potential': self._calculate_xai_roi_potential()
            }
        
        return overall_assessment
    
    def _calculate_xai_maturity_level(self):
        """Calcular nivel de madurez de Explainable AI"""
        # Basado en capacidades disponibles
        maturity_score = 0
        
        if self.xai_analysis and 'xai_techniques' in self.xai_analysis:
            techniques = self.xai_analysis['xai_techniques']
            
            # Post-hoc explanations
            if 'post_hoc_explanations' in techniques:
                maturity_score += 20
            
            # Intrinsic interpretability
            if 'intrinsic_interpretability' in techniques:
                maturity_score += 20
            
            # Model-agnostic
            if 'model_agnostic' in techniques:
                maturity_score += 20
            
            # Feature importance
            if 'feature_importance' in techniques:
                maturity_score += 20
            
            # Applications
            if 'xai_applications' in self.xai_analysis:
                maturity_score += 20
        
        if maturity_score >= 80:
            return 'Advanced'
        elif maturity_score >= 60:
            return 'Intermediate'
        elif maturity_score >= 40:
            return 'Basic'
        else:
            return 'Beginner'
    
    def _calculate_xai_readiness_score(self):
        """Calcular score de preparación para Explainable AI"""
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
    
    def _calculate_xai_implementation_priority(self):
        """Calcular prioridad de implementación de Explainable AI"""
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
    
    def _calculate_xai_roi_potential(self):
        """Calcular potencial de ROI de Explainable AI"""
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
    
    def build_xai_models(self, target_variable, model_type='classification'):
        """Construir modelos de Explainable AI"""
        if target_variable not in self.xai_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.xai_data.columns if col != target_variable]
        X = self.xai_data[feature_columns]
        y = self.xai_data[target_variable]
        
        # Preprocesamiento
        X_processed, y_processed = self._preprocess_xai_data(X, y, model_type)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42)
        
        # Construir modelos
        models = {}
        
        if model_type == 'classification':
            models = self._build_xai_classification_models(X_train, X_test, y_train, y_test)
        elif model_type == 'regression':
            models = self._build_xai_regression_models(X_train, X_test, y_train, y_test)
        elif model_type == 'clustering':
            models = self._build_xai_clustering_models(X_processed)
        
        # Evaluar modelos
        model_evaluation = self._evaluate_xai_models(models, X_test, y_test, model_type)
        
        # Optimizar modelos
        optimized_models = self._optimize_xai_models(models, X_train, y_train)
        
        self.xai_models = {
            'models': models,
            'optimized_models': optimized_models,
            'model_evaluation': model_evaluation,
            'model_type': model_type,
            'target_variable': target_variable
        }
        
        return self.xai_models
    
    def _preprocess_xai_data(self, X, y, model_type):
        """Preprocesar datos de Explainable AI"""
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
    
    def _build_xai_classification_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de clasificación de Explainable AI"""
        models = {}
        
        # Decision Tree (Intrinsic Interpretability)
        dt_model = self._build_decision_tree_model(X_train.shape[1], len(np.unique(y_train)))
        models['Decision Tree'] = dt_model
        
        # Random Forest (Feature Importance)
        rf_model = self._build_random_forest_model(X_train.shape[1], len(np.unique(y_train)))
        models['Random Forest'] = rf_model
        
        # Linear Model (High Interpretability)
        linear_model = self._build_linear_model(X_train.shape[1], len(np.unique(y_train)))
        models['Linear Model'] = linear_model
        
        return models
    
    def _build_xai_regression_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de regresión de Explainable AI"""
        models = {}
        
        # Linear Regression
        linear_model = self._build_linear_regression_model(X_train.shape[1])
        models['Linear Regression'] = linear_model
        
        # Decision Tree Regressor
        dt_model = self._build_decision_tree_regression_model(X_train.shape[1])
        models['Decision Tree Regressor'] = dt_model
        
        return models
    
    def _build_xai_clustering_models(self, X):
        """Construir modelos de clustering de Explainable AI"""
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
    
    def _build_decision_tree_model(self, input_dim, num_classes):
        """Construir modelo Decision Tree"""
        model = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(input_dim,)),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(16, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_random_forest_model(self, input_dim, num_classes):
        """Construir modelo Random Forest"""
        model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=(input_dim,)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_linear_model(self, input_dim, num_classes):
        """Construir modelo Linear"""
        model = models.Sequential([
            layers.Dense(num_classes, activation='softmax', input_shape=(input_dim,))
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_linear_regression_model(self, input_dim):
        """Construir modelo Linear Regression"""
        model = models.Sequential([
            layers.Dense(1, activation='linear', input_shape=(input_dim,))
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _build_decision_tree_regression_model(self, input_dim):
        """Construir modelo Decision Tree Regressor"""
        model = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(input_dim,)),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _evaluate_xai_models(self, models, X_test, y_test, model_type):
        """Evaluar modelos de Explainable AI"""
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
    
    def _optimize_xai_models(self, models, X_train, y_train):
        """Optimizar modelos de Explainable AI"""
        optimized_models = {}
        
        for model_name, model in models.items():
            try:
                # Optimización de hiperparámetros
                if hasattr(model, 'get_config'):
                    # Crear modelo optimizado con mejores hiperparámetros
                    optimized_model = self._create_optimized_xai_model(model_name, X_train.shape[1], len(np.unique(y_train)))
                    optimized_models[model_name] = optimized_model
                else:
                    optimized_models[model_name] = model
            except Exception as e:
                optimized_models[model_name] = model
        
        return optimized_models
    
    def _create_optimized_xai_model(self, model_name, input_dim, num_classes):
        """Crear modelo de Explainable AI optimizado"""
        if 'Decision Tree' in model_name:
            return self._build_optimized_decision_tree_model(input_dim, num_classes)
        elif 'Random Forest' in model_name:
            return self._build_optimized_random_forest_model(input_dim, num_classes)
        elif 'Linear' in model_name:
            return self._build_optimized_linear_model(input_dim, num_classes)
        else:
            return self._build_decision_tree_model(input_dim, num_classes)
    
    def _build_optimized_decision_tree_model(self, input_dim, num_classes):
        """Construir modelo Decision Tree optimizado"""
        model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_optimized_random_forest_model(self, input_dim, num_classes):
        """Construir modelo Random Forest optimizado"""
        model = models.Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_optimized_linear_model(self, input_dim, num_classes):
        """Construir modelo Linear optimizado"""
        model = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def generate_xai_strategies(self):
        """Generar estrategias de Explainable AI"""
        strategies = []
        
        # Estrategias basadas en técnicas de Explainable AI
        if self.xai_analysis and 'xai_techniques' in self.xai_analysis:
            techniques = self.xai_analysis['xai_techniques']
            
            # Estrategias de post-hoc explanations
            if 'post_hoc_explanations' in techniques:
                strategies.append({
                    'strategy_type': 'Post-hoc Explanations Implementation',
                    'description': 'Implementar técnicas de post-hoc explanations para explicabilidad',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de intrinsic interpretability
            if 'intrinsic_interpretability' in techniques:
                strategies.append({
                    'strategy_type': 'Intrinsic Interpretability Implementation',
                    'description': 'Implementar modelos con interpretabilidad intrínseca',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en aplicaciones de Explainable AI
        if self.xai_analysis and 'xai_applications' in self.xai_analysis:
            applications = self.xai_analysis['xai_applications']
            
            # Estrategias de Financial Services
            if 'Financial Services' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Financial Services XAI Implementation',
                    'description': 'Implementar Explainable AI para servicios financieros',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de Healthcare
            if 'Healthcare' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Healthcare XAI Implementation',
                    'description': 'Implementar Explainable AI para aplicaciones de salud',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en transparencia y confiabilidad
        if self.xai_analysis and 'transparency_trust' in self.xai_analysis:
            transparency_trust = self.xai_analysis['transparency_trust']
            
            strategies.append({
                'strategy_type': 'Transparency and Trust Implementation',
                'description': 'Implementar transparencia y confiabilidad en modelos de AI',
                'priority': 'high',
                'expected_impact': 'high'
            })
        
        # Estrategias basadas en regulaciones y compliance
        if self.xai_analysis and 'regulations_compliance' in self.xai_analysis:
            regulations_compliance = self.xai_analysis['regulations_compliance']
            
            strategies.append({
                'strategy_type': 'Regulatory Compliance Implementation',
                'description': 'Implementar compliance con regulaciones de AI',
                'priority': 'high',
                'expected_impact': 'high'
            })
        
        # Estrategias basadas en explicabilidad local vs global
        if self.xai_analysis and 'local_global_explainability' in self.xai_analysis:
            local_global_explainability = self.xai_analysis['local_global_explainability']
            
            strategies.append({
                'strategy_type': 'Local and Global Explainability Implementation',
                'description': 'Implementar explicabilidad local y global',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        self.xai_strategies = strategies
        return strategies
    
    def generate_xai_insights(self):
        """Generar insights de Explainable AI"""
        insights = []
        
        # Insights de evaluación general de Explainable AI
        if self.xai_analysis and 'overall_xai_assessment' in self.xai_analysis:
            assessment = self.xai_analysis['overall_xai_assessment']
            maturity_level = assessment.get('xai_maturity_level', 'Unknown')
            
            insights.append({
                'category': 'Explainable AI Maturity',
                'insight': f'Nivel de madurez de Explainable AI: {maturity_level}',
                'recommendation': f'{"Mantener" if maturity_level == "Advanced" else "Mejorar"} capacidades de Explainable AI',
                'priority': 'high' if maturity_level in ['Beginner', 'Basic'] else 'medium'
            })
            
            readiness_score = assessment.get('xai_readiness_score', 0)
            if readiness_score < 70:
                insights.append({
                    'category': 'Explainable AI Readiness',
                    'insight': f'Score de preparación para Explainable AI: {readiness_score}',
                    'recommendation': 'Mejorar preparación para implementación de Explainable AI',
                    'priority': 'high'
                })
            
            implementation_priority = assessment.get('xai_implementation_priority', 'Low')
            if implementation_priority == 'High':
                insights.append({
                    'category': 'Explainable AI Implementation',
                    'insight': f'Prioridad de implementación: {implementation_priority}',
                    'recommendation': 'Priorizar implementación de Explainable AI',
                    'priority': 'high'
                })
            
            roi_potential = assessment.get('xai_roi_potential', 'Low')
            if roi_potential in ['High', 'Very High']:
                insights.append({
                    'category': 'Explainable AI ROI',
                    'insight': f'Potencial de ROI: {roi_potential}',
                    'recommendation': 'Invertir en Explainable AI para maximizar ROI',
                    'priority': 'high'
                })
        
        # Insights de técnicas de Explainable AI
        if self.xai_analysis and 'xai_techniques' in self.xai_analysis:
            techniques = self.xai_analysis['xai_techniques']
            
            if 'post_hoc_explanations' in techniques:
                best_post_hoc = techniques['post_hoc_explanations'].get('best_technique', 'Unknown')
                insights.append({
                    'category': 'Post-hoc Explanations',
                    'insight': f'Mejor técnica de post-hoc explanations: {best_post_hoc}',
                    'recommendation': 'Usar esta técnica para explicaciones post-hoc',
                    'priority': 'medium'
                })
            
            if 'intrinsic_interpretability' in techniques:
                best_intrinsic = techniques['intrinsic_interpretability'].get('best_technique', 'Unknown')
                insights.append({
                    'category': 'Intrinsic Interpretability',
                    'insight': f'Mejor técnica de interpretabilidad intrínseca: {best_intrinsic}',
                    'recommendation': 'Usar esta técnica para modelos interpretables',
                    'priority': 'medium'
                })
        
        # Insights de aplicaciones de Explainable AI
        if self.xai_analysis and 'xai_applications' in self.xai_analysis:
            applications = self.xai_analysis['xai_applications']
            best_application = applications.get('best_application', 'Unknown')
            
            insights.append({
                'category': 'Explainable AI Applications',
                'insight': f'Mejor aplicación de Explainable AI: {best_application}',
                'recommendation': 'Implementar esta aplicación para máximo valor de negocio',
                'priority': 'high'
            })
        
        # Insights de modelos de Explainable AI
        if self.xai_models:
            model_evaluation = self.xai_models.get('model_evaluation', {})
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
                        'category': 'Explainable AI Model Performance',
                        'insight': f'Mejor modelo de Explainable AI: {best_model} con score {best_score:.3f}',
                        'recommendation': 'Usar este modelo para predicciones explicables',
                        'priority': 'high'
                    })
        
        self.xai_insights = insights
        return insights
    
    def create_xai_dashboard(self):
        """Crear dashboard de Explainable AI"""
        if self.xai_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('XAI Techniques', 'Model Performance',
                          'XAI Maturity', 'Implementation Priority'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de técnicas de Explainable AI
        if self.xai_analysis and 'xai_techniques' in self.xai_analysis:
            techniques = self.xai_analysis['xai_techniques']
            technique_names = list(techniques.keys())
            technique_scores = [5] * len(technique_names)  # Placeholder scores
            
            fig.add_trace(
                go.Bar(x=technique_names, y=technique_scores, name='XAI Techniques'),
                row=1, col=1
            )
        
        # Gráfico de performance de modelos
        if self.xai_models:
            model_evaluation = self.xai_models.get('model_evaluation', {})
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
        
        # Gráfico de madurez de Explainable AI
        if self.xai_analysis and 'overall_xai_assessment' in self.xai_analysis:
            assessment = self.xai_analysis['overall_xai_assessment']
            maturity_level = assessment.get('xai_maturity_level', 'Unknown')
            
            maturity_data = {
                'Beginner': 1,
                'Basic': 2,
                'Intermediate': 3,
                'Advanced': 4
            }
            
            fig.add_trace(
                go.Pie(labels=list(maturity_data.keys()), values=list(maturity_data.values()), name='XAI Maturity'),
                row=2, col=1
            )
        
        # Gráfico de prioridad de implementación
        if self.xai_analysis and 'overall_xai_assessment' in self.xai_analysis:
            assessment = self.xai_analysis['overall_xai_assessment']
            implementation_priority = assessment.get('xai_implementation_priority', 'Low')
            
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
            title="Dashboard de Explainable AI",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_xai_analysis(self, filename='marketing_xai_analysis.json'):
        """Exportar análisis de Explainable AI"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'xai_analysis': self.xai_analysis,
            'xai_models': {k: {'model_evaluation': v.get('model_evaluation', {})} for k, v in self.xai_models.items()},
            'xai_strategies': self.xai_strategies,
            'xai_insights': self.xai_insights,
            'summary': {
                'total_records': len(self.xai_data),
                'xai_maturity_level': self.xai_analysis.get('overall_xai_assessment', {}).get('xai_maturity_level', 'Unknown'),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de Explainable AI exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de Explainable AI de marketing
    xai_optimizer = MarketingExplainableAIOptimizer()
    
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
        'xai_score': np.random.uniform(0, 100, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de Explainable AI de marketing
    print("📊 Cargando datos de Explainable AI de marketing...")
    xai_optimizer.load_xai_data(sample_data)
    
    # Analizar capacidades de Explainable AI
    print("🤖 Analizando capacidades de Explainable AI...")
    xai_analysis = xai_optimizer.analyze_xai_capabilities()
    
    # Construir modelos de Explainable AI
    print("🔮 Construyendo modelos de Explainable AI...")
    xai_models = xai_optimizer.build_xai_models(target_variable='xai_score', model_type='classification')
    
    # Generar estrategias de Explainable AI
    print("🎯 Generando estrategias de Explainable AI...")
    xai_strategies = xai_optimizer.generate_xai_strategies()
    
    # Generar insights de Explainable AI
    print("💡 Generando insights de Explainable AI...")
    xai_insights = xai_optimizer.generate_xai_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de Explainable AI...")
    dashboard = xai_optimizer.create_xai_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de Explainable AI...")
    export_data = xai_optimizer.export_xai_analysis()
    
    print("✅ Sistema de optimización de Explainable AI de marketing completado!")




