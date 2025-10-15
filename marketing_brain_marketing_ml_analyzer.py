"""
Marketing Brain Marketing ML Analyzer
Sistema avanzado de análisis de machine learning de marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, VotingClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.feature_selection import SelectKBest, RFE, SelectFromModel, mutual_info_classif, mutual_info_regression
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.ensemble import BaggingClassifier, AdaBoostClassifier, ExtraTreesClassifier, IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import make_scorer, confusion_matrix, roc_auc_score, mean_squared_error, r2_score
from sklearn.manifold import TSNE
from sklearn.mixture import GaussianMixture
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class MarketingMLAnalyzer:
    def __init__(self):
        self.ml_data = {}
        self.ml_analysis = {}
        self.ml_models = {}
        self.ml_strategies = {}
        self.ml_insights = {}
        self.ml_recommendations = {}
        
    def load_ml_data(self, ml_data):
        """Cargar datos de ML de marketing"""
        if isinstance(ml_data, str):
            if ml_data.endswith('.csv'):
                self.ml_data = pd.read_csv(ml_data)
            elif ml_data.endswith('.json'):
                with open(ml_data, 'r') as f:
                    data = json.load(f)
                self.ml_data = pd.DataFrame(data)
        else:
            self.ml_data = pd.DataFrame(ml_data)
        
        print(f"✅ Datos de ML de marketing cargados: {len(self.ml_data)} registros")
        return True
    
    def analyze_ml_capabilities(self):
        """Analizar capacidades de ML"""
        if self.ml_data.empty:
            return None
        
        # Análisis de algoritmos de ML
        ml_algorithms = self._analyze_ml_algorithms()
        
        # Análisis de feature engineering
        feature_engineering = self._analyze_feature_engineering()
        
        # Análisis de model selection
        model_selection = self._analyze_model_selection()
        
        # Análisis de hyperparameter tuning
        hyperparameter_tuning = self._analyze_hyperparameter_tuning()
        
        # Análisis de model evaluation
        model_evaluation = self._analyze_model_evaluation()
        
        # Análisis de model deployment
        model_deployment = self._analyze_model_deployment()
        
        ml_results = {
            'ml_algorithms': ml_algorithms,
            'feature_engineering': feature_engineering,
            'model_selection': model_selection,
            'hyperparameter_tuning': hyperparameter_tuning,
            'model_evaluation': model_evaluation,
            'model_deployment': model_deployment,
            'overall_ml_assessment': self._calculate_overall_ml_assessment()
        }
        
        self.ml_analysis = ml_results
        return ml_results
    
    def _analyze_ml_algorithms(self):
        """Analizar algoritmos de ML"""
        algorithm_analysis = {}
        
        # Análisis de algoritmos de clasificación
        classification_algorithms = self._analyze_classification_algorithms()
        algorithm_analysis['classification'] = classification_algorithms
        
        # Análisis de algoritmos de regresión
        regression_algorithms = self._analyze_regression_algorithms()
        algorithm_analysis['regression'] = regression_algorithms
        
        # Análisis de algoritmos de clustering
        clustering_algorithms = self._analyze_clustering_algorithms()
        algorithm_analysis['clustering'] = clustering_algorithms
        
        # Análisis de algoritmos de reducción de dimensionalidad
        dimensionality_algorithms = self._analyze_dimensionality_algorithms()
        algorithm_analysis['dimensionality_reduction'] = dimensionality_algorithms
        
        # Análisis de algoritmos de ensemble
        ensemble_algorithms = self._analyze_ensemble_algorithms()
        algorithm_analysis['ensemble'] = ensemble_algorithms
        
        # Análisis de algoritmos de detección de anomalías
        anomaly_algorithms = self._analyze_anomaly_algorithms()
        algorithm_analysis['anomaly_detection'] = anomaly_algorithms
        
        return algorithm_analysis
    
    def _analyze_classification_algorithms(self):
        """Analizar algoritmos de clasificación"""
        classification_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'Random Forest': {
                'algorithm': RandomForestClassifier,
                'complexity': 3,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 5,
                'performance': 4
            },
            'Gradient Boosting': {
                'algorithm': GradientBoostingRegressor,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 4,
                'performance': 5
            },
            'SVM': {
                'algorithm': SVC,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 2,
                'robustness': 4,
                'performance': 4
            },
            'Logistic Regression': {
                'algorithm': LogisticRegression,
                'complexity': 1,
                'interpretability': 5,
                'scalability': 5,
                'robustness': 3,
                'performance': 3
            },
            'Naive Bayes': {
                'algorithm': GaussianNB,
                'complexity': 1,
                'interpretability': 4,
                'scalability': 4,
                'robustness': 3,
                'performance': 3
            },
            'K-Nearest Neighbors': {
                'algorithm': KNeighborsClassifier,
                'complexity': 2,
                'interpretability': 3,
                'scalability': 2,
                'robustness': 3,
                'performance': 3
            },
            'Decision Tree': {
                'algorithm': DecisionTreeClassifier,
                'complexity': 2,
                'interpretability': 4,
                'scalability': 4,
                'robustness': 2,
                'performance': 3
            },
            'Neural Network': {
                'algorithm': MLPClassifier,
                'complexity': 5,
                'interpretability': 1,
                'scalability': 3,
                'robustness': 3,
                'performance': 4
            }
        }
        
        classification_analysis['algorithms'] = algorithms
        classification_analysis['best_algorithm'] = self._select_best_algorithm(algorithms)
        classification_analysis['algorithm_recommendations'] = self._get_algorithm_recommendations(algorithms)
        
        return classification_analysis
    
    def _analyze_regression_algorithms(self):
        """Analizar algoritmos de regresión"""
        regression_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'Linear Regression': {
                'algorithm': LinearRegression,
                'complexity': 1,
                'interpretability': 5,
                'scalability': 5,
                'robustness': 3,
                'performance': 3
            },
            'Ridge Regression': {
                'algorithm': Ridge,
                'complexity': 1,
                'interpretability': 5,
                'scalability': 5,
                'robustness': 4,
                'performance': 3
            },
            'Lasso Regression': {
                'algorithm': Lasso,
                'complexity': 1,
                'interpretability': 5,
                'scalability': 5,
                'robustness': 4,
                'performance': 3
            },
            'Elastic Net': {
                'algorithm': ElasticNet,
                'complexity': 1,
                'interpretability': 5,
                'scalability': 5,
                'robustness': 4,
                'performance': 3
            },
            'Random Forest': {
                'algorithm': RandomForestRegressor,
                'complexity': 3,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 5,
                'performance': 4
            },
            'Gradient Boosting': {
                'algorithm': GradientBoostingRegressor,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 4,
                'performance': 5
            },
            'SVM': {
                'algorithm': SVR,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 2,
                'robustness': 4,
                'performance': 4
            },
            'K-Nearest Neighbors': {
                'algorithm': KNeighborsRegressor,
                'complexity': 2,
                'interpretability': 3,
                'scalability': 2,
                'robustness': 3,
                'performance': 3
            },
            'Decision Tree': {
                'algorithm': DecisionTreeRegressor,
                'complexity': 2,
                'interpretability': 4,
                'scalability': 4,
                'robustness': 2,
                'performance': 3
            },
            'Neural Network': {
                'algorithm': MLPRegressor,
                'complexity': 5,
                'interpretability': 1,
                'scalability': 3,
                'robustness': 3,
                'performance': 4
            }
        }
        
        regression_analysis['algorithms'] = algorithms
        regression_analysis['best_algorithm'] = self._select_best_algorithm(algorithms)
        regression_analysis['algorithm_recommendations'] = self._get_algorithm_recommendations(algorithms)
        
        return regression_analysis
    
    def _analyze_clustering_algorithms(self):
        """Analizar algoritmos de clustering"""
        clustering_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'K-Means': {
                'algorithm': KMeans,
                'complexity': 3,
                'interpretability': 3,
                'scalability': 4,
                'robustness': 3,
                'performance': 4
            },
            'DBSCAN': {
                'algorithm': DBSCAN,
                'complexity': 3,
                'interpretability': 3,
                'scalability': 3,
                'robustness': 4,
                'performance': 4
            },
            'Agglomerative Clustering': {
                'algorithm': AgglomerativeClustering,
                'complexity': 3,
                'interpretability': 3,
                'scalability': 2,
                'robustness': 3,
                'performance': 3
            },
            'Gaussian Mixture': {
                'algorithm': GaussianMixture,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 3,
                'performance': 4
            }
        }
        
        clustering_analysis['algorithms'] = algorithms
        clustering_analysis['best_algorithm'] = self._select_best_algorithm(algorithms)
        clustering_analysis['algorithm_recommendations'] = self._get_algorithm_recommendations(algorithms)
        
        return clustering_analysis
    
    def _analyze_dimensionality_algorithms(self):
        """Analizar algoritmos de reducción de dimensionalidad"""
        dimensionality_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'PCA': {
                'algorithm': PCA,
                'complexity': 2,
                'interpretability': 4,
                'scalability': 5,
                'robustness': 4,
                'performance': 4
            },
            'FastICA': {
                'algorithm': FastICA,
                'complexity': 3,
                'interpretability': 3,
                'scalability': 4,
                'robustness': 3,
                'performance': 4
            },
            'Truncated SVD': {
                'algorithm': TruncatedSVD,
                'complexity': 2,
                'interpretability': 4,
                'scalability': 5,
                'robustness': 4,
                'performance': 4
            },
            't-SNE': {
                'algorithm': TSNE,
                'complexity': 4,
                'interpretability': 3,
                'scalability': 2,
                'robustness': 3,
                'performance': 4
            }
        }
        
        dimensionality_analysis['algorithms'] = algorithms
        dimensionality_analysis['best_algorithm'] = self._select_best_algorithm(algorithms)
        dimensionality_analysis['algorithm_recommendations'] = self._get_algorithm_recommendations(algorithms)
        
        return dimensionality_analysis
    
    def _analyze_ensemble_algorithms(self):
        """Analizar algoritmos de ensemble"""
        ensemble_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'Voting Classifier': {
                'algorithm': VotingClassifier,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 4,
                'performance': 4
            },
            'Bagging': {
                'algorithm': BaggingClassifier,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 4,
                'performance': 4
            },
            'AdaBoost': {
                'algorithm': AdaBoostClassifier,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 4,
                'performance': 4
            },
            'Extra Trees': {
                'algorithm': ExtraTreesClassifier,
                'complexity': 3,
                'interpretability': 2,
                'scalability': 3,
                'robustness': 5,
                'performance': 4
            }
        }
        
        ensemble_analysis['algorithms'] = algorithms
        ensemble_analysis['best_algorithm'] = self._select_best_algorithm(algorithms)
        ensemble_analysis['algorithm_recommendations'] = self._get_algorithm_recommendations(algorithms)
        
        return ensemble_analysis
    
    def _analyze_anomaly_algorithms(self):
        """Analizar algoritmos de detección de anomalías"""
        anomaly_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'Isolation Forest': {
                'algorithm': IsolationForest,
                'complexity': 3,
                'interpretability': 3,
                'scalability': 4,
                'robustness': 4,
                'performance': 4
            },
            'One-Class SVM': {
                'algorithm': SVC,
                'complexity': 4,
                'interpretability': 2,
                'scalability': 2,
                'robustness': 4,
                'performance': 4
            },
            'Local Outlier Factor': {
                'algorithm': None,  # Placeholder
                'complexity': 3,
                'interpretability': 3,
                'scalability': 2,
                'robustness': 3,
                'performance': 3
            }
        }
        
        anomaly_analysis['algorithms'] = algorithms
        anomaly_analysis['best_algorithm'] = self._select_best_algorithm(algorithms)
        anomaly_analysis['algorithm_recommendations'] = self._get_algorithm_recommendations(algorithms)
        
        return anomaly_analysis
    
    def _select_best_algorithm(self, algorithms):
        """Seleccionar mejor algoritmo"""
        best_algorithm = None
        best_score = 0
        
        for name, performance in algorithms.items():
            # Calcular score combinado
            score = (performance['interpretability'] * 0.2 + 
                    performance['scalability'] * 0.2 + 
                    performance['robustness'] * 0.3 + 
                    performance['performance'] * 0.3)
            
            if score > best_score:
                best_score = score
                best_algorithm = name
        
        return best_algorithm
    
    def _get_algorithm_recommendations(self, algorithms):
        """Obtener recomendaciones de algoritmos"""
        recommendations = []
        
        # Recomendaciones basadas en interpretabilidad
        interpretable_algorithms = [name for name, perf in algorithms.items() 
                                  if perf['interpretability'] >= 4]
        if interpretable_algorithms:
            recommendations.append({
                'criteria': 'Interpretability',
                'algorithms': interpretable_algorithms,
                'reason': 'High interpretability for business understanding'
            })
        
        # Recomendaciones basadas en performance
        high_performance_algorithms = [name for name, perf in algorithms.items() 
                                     if perf['performance'] >= 4]
        if high_performance_algorithms:
            recommendations.append({
                'criteria': 'Performance',
                'algorithms': high_performance_algorithms,
                'reason': 'High performance for accurate predictions'
            })
        
        # Recomendaciones basadas en escalabilidad
        scalable_algorithms = [name for name, perf in algorithms.items() 
                             if perf['scalability'] >= 4]
        if scalable_algorithms:
            recommendations.append({
                'criteria': 'Scalability',
                'algorithms': scalable_algorithms,
                'reason': 'High scalability for large datasets'
            })
        
        return recommendations
    
    def _analyze_feature_engineering(self):
        """Analizar feature engineering"""
        feature_analysis = {}
        
        # Análisis de feature selection
        feature_selection = self._analyze_feature_selection()
        feature_analysis['feature_selection'] = feature_selection
        
        # Análisis de feature creation
        feature_creation = self._analyze_feature_creation()
        feature_analysis['feature_creation'] = feature_creation
        
        # Análisis de feature transformation
        feature_transformation = self._analyze_feature_transformation()
        feature_analysis['feature_transformation'] = feature_transformation
        
        # Análisis de feature scaling
        feature_scaling = self._analyze_feature_scaling()
        feature_analysis['feature_scaling'] = feature_scaling
        
        return feature_analysis
    
    def _analyze_feature_selection(self):
        """Analizar feature selection"""
        selection_analysis = {}
        
        # Técnicas de feature selection
        techniques = {
            'Univariate Selection': {
                'algorithm': SelectKBest,
                'complexity': 2,
                'effectiveness': 3,
                'interpretability': 4
            },
            'Recursive Feature Elimination': {
                'algorithm': RFE,
                'complexity': 3,
                'effectiveness': 4,
                'interpretability': 3
            },
            'Feature Importance': {
                'algorithm': SelectFromModel,
                'complexity': 2,
                'effectiveness': 4,
                'interpretability': 4
            },
            'Mutual Information': {
                'algorithm': mutual_info_classif,
                'complexity': 3,
                'effectiveness': 4,
                'interpretability': 3
            }
        }
        
        selection_analysis['techniques'] = techniques
        selection_analysis['best_technique'] = 'Feature Importance'
        selection_analysis['recommendations'] = [
            'Use feature importance for tree-based models',
            'Use mutual information for non-linear relationships',
            'Use RFE for wrapper methods'
        ]
        
        return selection_analysis
    
    def _analyze_feature_creation(self):
        """Analizar feature creation"""
        creation_analysis = {}
        
        # Técnicas de feature creation
        techniques = {
            'Polynomial Features': {
                'algorithm': PolynomialFeatures,
                'complexity': 2,
                'effectiveness': 3,
                'interpretability': 2
            },
            'Interaction Features': {
                'algorithm': None,  # Custom implementation
                'complexity': 3,
                'effectiveness': 4,
                'interpretability': 3
            },
            'Time-based Features': {
                'algorithm': None,  # Custom implementation
                'complexity': 2,
                'effectiveness': 4,
                'interpretability': 4
            },
            'Domain-specific Features': {
                'algorithm': None,  # Custom implementation
                'complexity': 4,
                'effectiveness': 5,
                'interpretability': 4
            }
        }
        
        creation_analysis['techniques'] = techniques
        creation_analysis['best_technique'] = 'Domain-specific Features'
        creation_analysis['recommendations'] = [
            'Create domain-specific features for better performance',
            'Use time-based features for temporal data',
            'Create interaction features for non-linear relationships'
        ]
        
        return creation_analysis
    
    def _analyze_feature_transformation(self):
        """Analizar feature transformation"""
        transformation_analysis = {}
        
        # Técnicas de feature transformation
        techniques = {
            'Log Transformation': {
                'complexity': 1,
                'effectiveness': 3,
                'interpretability': 4
            },
            'Box-Cox Transformation': {
                'complexity': 2,
                'effectiveness': 4,
                'interpretability': 3
            },
            'Standardization': {
                'complexity': 1,
                'effectiveness': 4,
                'interpretability': 4
            },
            'Normalization': {
                'complexity': 1,
                'effectiveness': 3,
                'interpretability': 4
            }
        }
        
        transformation_analysis['techniques'] = techniques
        transformation_analysis['best_technique'] = 'Standardization'
        transformation_analysis['recommendations'] = [
            'Use standardization for algorithms sensitive to scale',
            'Use log transformation for skewed data',
            'Use Box-Cox for power transformations'
        ]
        
        return transformation_analysis
    
    def _analyze_feature_scaling(self):
        """Analizar feature scaling"""
        scaling_analysis = {}
        
        # Técnicas de feature scaling
        techniques = {
            'StandardScaler': {
                'algorithm': StandardScaler,
                'complexity': 1,
                'effectiveness': 4,
                'interpretability': 4
            },
            'MinMaxScaler': {
                'algorithm': MinMaxScaler,
                'complexity': 1,
                'effectiveness': 3,
                'interpretability': 4
            },
            'RobustScaler': {
                'algorithm': None,  # Placeholder
                'complexity': 2,
                'effectiveness': 4,
                'interpretability': 3
            }
        }
        
        scaling_analysis['techniques'] = techniques
        scaling_analysis['best_technique'] = 'StandardScaler'
        scaling_analysis['recommendations'] = [
            'Use StandardScaler for most algorithms',
            'Use MinMaxScaler for algorithms requiring bounded features',
            'Use RobustScaler for data with outliers'
        ]
        
        return scaling_analysis
    
    def _analyze_model_selection(self):
        """Analizar model selection"""
        selection_analysis = {}
        
        # Técnicas de model selection
        techniques = {
            'Train-Test Split': {
                'complexity': 1,
                'effectiveness': 3,
                'interpretability': 5
            },
            'Cross-Validation': {
                'complexity': 2,
                'effectiveness': 4,
                'interpretability': 4
            },
            'Stratified Cross-Validation': {
                'complexity': 2,
                'effectiveness': 4,
                'interpretability': 4
            },
            'Time Series Split': {
                'complexity': 3,
                'effectiveness': 4,
                'interpretability': 3
            }
        }
        
        selection_analysis['techniques'] = techniques
        selection_analysis['best_technique'] = 'Cross-Validation'
        selection_analysis['recommendations'] = [
            'Use cross-validation for robust model selection',
            'Use stratified CV for imbalanced datasets',
            'Use time series split for temporal data'
        ]
        
        return selection_analysis
    
    def _analyze_hyperparameter_tuning(self):
        """Analizar hyperparameter tuning"""
        tuning_analysis = {}
        
        # Técnicas de hyperparameter tuning
        techniques = {
            'Grid Search': {
                'complexity': 2,
                'effectiveness': 4,
                'efficiency': 2
            },
            'Random Search': {
                'complexity': 2,
                'effectiveness': 3,
                'efficiency': 3
            },
            'Bayesian Optimization': {
                'complexity': 4,
                'effectiveness': 5,
                'efficiency': 4
            },
            'Genetic Algorithms': {
                'complexity': 4,
                'effectiveness': 4,
                'efficiency': 3
            }
        }
        
        tuning_analysis['techniques'] = techniques
        tuning_analysis['best_technique'] = 'Bayesian Optimization'
        tuning_analysis['recommendations'] = [
            'Use Bayesian optimization for efficient tuning',
            'Use grid search for small parameter spaces',
            'Use random search for large parameter spaces'
        ]
        
        return tuning_analysis
    
    def _analyze_model_evaluation(self):
        """Analizar model evaluation"""
        evaluation_analysis = {}
        
        # Métricas de evaluación
        metrics = {
            'Classification': {
                'Accuracy': {'importance': 5, 'interpretability': 5},
                'Precision': {'importance': 4, 'interpretability': 4},
                'Recall': {'importance': 4, 'interpretability': 4},
                'F1-Score': {'importance': 4, 'interpretability': 4},
                'AUC-ROC': {'importance': 4, 'interpretability': 3},
                'Confusion Matrix': {'importance': 3, 'interpretability': 5}
            },
            'Regression': {
                'MSE': {'importance': 4, 'interpretability': 3},
                'RMSE': {'importance': 4, 'interpretability': 4},
                'MAE': {'importance': 4, 'interpretability': 4},
                'R²': {'importance': 4, 'interpretability': 4},
                'MAPE': {'importance': 3, 'interpretability': 4}
            },
            'Clustering': {
                'Silhouette Score': {'importance': 4, 'interpretability': 3},
                'Inertia': {'importance': 3, 'interpretability': 3},
                'Calinski-Harabasz': {'importance': 3, 'interpretability': 3}
            }
        }
        
        evaluation_analysis['metrics'] = metrics
        evaluation_analysis['recommendations'] = [
            'Use multiple metrics for comprehensive evaluation',
            'Consider business context when selecting metrics',
            'Use cross-validation for robust evaluation'
        ]
        
        return evaluation_analysis
    
    def _analyze_model_deployment(self):
        """Analizar model deployment"""
        deployment_analysis = {}
        
        # Estrategias de deployment
        strategies = {
            'Batch Processing': {
                'complexity': 2,
                'latency': 3,
                'scalability': 4
            },
            'Real-time Processing': {
                'complexity': 4,
                'latency': 5,
                'scalability': 3
            },
            'Stream Processing': {
                'complexity': 4,
                'latency': 4,
                'scalability': 4
            },
            'Edge Deployment': {
                'complexity': 5,
                'latency': 5,
                'scalability': 2
            }
        }
        
        deployment_analysis['strategies'] = strategies
        deployment_analysis['best_strategy'] = 'Real-time Processing'
        deployment_analysis['recommendations'] = [
            'Use real-time processing for immediate predictions',
            'Use batch processing for large-scale analysis',
            'Consider edge deployment for low-latency requirements'
        ]
        
        return deployment_analysis
    
    def _calculate_overall_ml_assessment(self):
        """Calcular evaluación general de ML"""
        overall_assessment = {}
        
        if not self.ml_data.empty:
            overall_assessment = {
                'ml_maturity_level': self._calculate_ml_maturity_level(),
                'ml_readiness_score': self._calculate_ml_readiness_score(),
                'ml_implementation_priority': self._calculate_ml_implementation_priority(),
                'ml_roi_potential': self._calculate_ml_roi_potential()
            }
        
        return overall_assessment
    
    def _calculate_ml_maturity_level(self):
        """Calcular nivel de madurez de ML"""
        # Basado en capacidades disponibles
        maturity_score = 0
        
        if self.ml_analysis and 'ml_algorithms' in self.ml_analysis:
            algorithms = self.ml_analysis['ml_algorithms']
            
            # Classification algorithms
            if 'classification' in algorithms:
                maturity_score += 20
            
            # Regression algorithms
            if 'regression' in algorithms:
                maturity_score += 20
            
            # Clustering algorithms
            if 'clustering' in algorithms:
                maturity_score += 20
            
            # Dimensionality reduction
            if 'dimensionality_reduction' in algorithms:
                maturity_score += 20
            
            # Ensemble algorithms
            if 'ensemble' in algorithms:
                maturity_score += 20
        
        if maturity_score >= 80:
            return 'Advanced'
        elif maturity_score >= 60:
            return 'Intermediate'
        elif maturity_score >= 40:
            return 'Basic'
        else:
            return 'Beginner'
    
    def _calculate_ml_readiness_score(self):
        """Calcular score de preparación para ML"""
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
    
    def _calculate_ml_implementation_priority(self):
        """Calcular prioridad de implementación de ML"""
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
    
    def _calculate_ml_roi_potential(self):
        """Calcular potencial de ROI de ML"""
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
    
    def build_ml_models(self, target_variable, model_type='classification'):
        """Construir modelos de ML"""
        if target_variable not in self.ml_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.ml_data.columns if col != target_variable]
        X = self.ml_data[feature_columns]
        y = self.ml_data[target_variable]
        
        # Preprocesamiento
        X_processed, y_processed = self._preprocess_ml_data(X, y)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42)
        
        # Construir modelos
        models = {}
        
        if model_type == 'classification':
            models = self._build_ml_classification_models(X_train, X_test, y_train, y_test)
        elif model_type == 'regression':
            models = self._build_ml_regression_models(X_train, X_test, y_train, y_test)
        elif model_type == 'clustering':
            models = self._build_ml_clustering_models(X_processed)
        
        # Evaluar modelos
        model_evaluation = self._evaluate_ml_models(models, X_test, y_test, model_type)
        
        # Optimizar modelos
        optimized_models = self._optimize_ml_models(models, X_train, y_train)
        
        self.ml_models = {
            'models': models,
            'optimized_models': optimized_models,
            'model_evaluation': model_evaluation,
            'model_type': model_type,
            'target_variable': target_variable
        }
        
        return self.ml_models
    
    def _preprocess_ml_data(self, X, y):
        """Preprocesar datos de ML"""
        # Identificar columnas numéricas y categóricas
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        categorical_columns = X.select_dtypes(include=['object']).columns
        
        # Crear transformador de columnas
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_columns),
                ('cat', categorical_transformer, categorical_columns)
            ]
        )
        
        # Aplicar preprocesamiento
        X_processed = preprocessor.fit_transform(X)
        
        # Preprocesar variable objetivo si es categórica
        if y.dtype == 'object':
            label_encoder = LabelEncoder()
            y_processed = label_encoder.fit_transform(y)
        else:
            y_processed = y
        
        return X_processed, y_processed
    
    def _build_ml_classification_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de clasificación de ML"""
        models = {}
        
        # Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        models['Random Forest'] = rf_model
        
        # Gradient Boosting
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gb_model.fit(X_train, y_train)
        models['Gradient Boosting'] = gb_model
        
        # SVM
        svm_model = SVC(random_state=42)
        svm_model.fit(X_train, y_train)
        models['SVM'] = svm_model
        
        # Neural Network
        nn_model = MLPClassifier(random_state=42)
        nn_model.fit(X_train, y_train)
        models['Neural Network'] = nn_model
        
        # Ensemble
        ensemble_model = VotingClassifier([
            ('rf', rf_model),
            ('svm', svm_model),
            ('nn', nn_model)
        ])
        ensemble_model.fit(X_train, y_train)
        models['Ensemble'] = ensemble_model
        
        return models
    
    def _build_ml_regression_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de regresión de ML"""
        models = {}
        
        # Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        models['Linear Regression'] = lr_model
        
        # Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        models['Random Forest'] = rf_model
        
        # Gradient Boosting
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gb_model.fit(X_train, y_train)
        models['Gradient Boosting'] = gb_model
        
        # Neural Network
        nn_model = MLPRegressor(random_state=42)
        nn_model.fit(X_train, y_train)
        models['Neural Network'] = nn_model
        
        return models
    
    def _build_ml_clustering_models(self, X):
        """Construir modelos de clustering de ML"""
        models = {}
        
        # K-Means
        kmeans_model = KMeans(n_clusters=3, random_state=42)
        kmeans_model.fit(X)
        models['K-Means'] = kmeans_model
        
        # DBSCAN
        dbscan_model = DBSCAN(eps=0.5, min_samples=5)
        dbscan_model.fit(X)
        models['DBSCAN'] = dbscan_model
        
        # Gaussian Mixture
        gmm_model = GaussianMixture(n_components=3, random_state=42)
        gmm_model.fit(X)
        models['Gaussian Mixture'] = gmm_model
        
        return models
    
    def _evaluate_ml_models(self, models, X_test, y_test, model_type):
        """Evaluar modelos de ML"""
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
    
    def _optimize_ml_models(self, models, X_train, y_train):
        """Optimizar modelos de ML"""
        optimized_models = {}
        
        for model_name, model in models.items():
            try:
                # Optimización de hiperparámetros
                if hasattr(model, 'get_params'):
                    param_grid = self._get_ml_param_grid(model_name)
                    if param_grid:
                        grid_search = GridSearchCV(model, param_grid, cv=3, scoring='accuracy')
                        grid_search.fit(X_train, y_train)
                        optimized_models[model_name] = grid_search.best_estimator_
                    else:
                        optimized_models[model_name] = model
                else:
                    optimized_models[model_name] = model
            except Exception as e:
                optimized_models[model_name] = model
        
        return optimized_models
    
    def _get_ml_param_grid(self, model_name):
        """Obtener grid de parámetros para optimización de ML"""
        param_grids = {
            'Random Forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            },
            'SVM': {
                'C': [0.1, 1, 10],
                'kernel': ['linear', 'rbf'],
                'gamma': ['scale', 'auto']
            },
            'Neural Network': {
                'hidden_layer_sizes': [(50,), (100,), (50, 50)],
                'activation': ['relu', 'tanh'],
                'alpha': [0.0001, 0.001, 0.01]
            },
            'Gradient Boosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
        }
        
        return param_grids.get(model_name, None)
    
    def generate_ml_strategies(self):
        """Generar estrategias de ML"""
        strategies = []
        
        # Estrategias basadas en capacidades de ML
        if self.ml_analysis and 'ml_algorithms' in self.ml_analysis:
            algorithms = self.ml_analysis['ml_algorithms']
            
            # Estrategias de clasificación
            if 'classification' in algorithms:
                strategies.append({
                    'strategy_type': 'Classification Implementation',
                    'description': 'Implementar modelos de clasificación para segmentación y predicción',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de regresión
            if 'regression' in algorithms:
                strategies.append({
                    'strategy_type': 'Regression Implementation',
                    'description': 'Implementar modelos de regresión para predicción de valores',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de clustering
            if 'clustering' in algorithms:
                strategies.append({
                    'strategy_type': 'Clustering Implementation',
                    'description': 'Implementar modelos de clustering para segmentación no supervisada',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en feature engineering
        if self.ml_analysis and 'feature_engineering' in self.ml_analysis:
            feature_engineering = self.ml_analysis['feature_engineering']
            
            strategies.append({
                'strategy_type': 'Feature Engineering',
                'description': 'Mejorar feature engineering para mejor performance',
                'priority': 'high',
                'expected_impact': 'high'
            })
        
        # Estrategias basadas en model selection
        if self.ml_analysis and 'model_selection' in self.ml_analysis:
            model_selection = self.ml_analysis['model_selection']
            
            strategies.append({
                'strategy_type': 'Model Selection',
                'description': 'Implementar técnicas avanzadas de model selection',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        # Estrategias basadas en hyperparameter tuning
        if self.ml_analysis and 'hyperparameter_tuning' in self.ml_analysis:
            hyperparameter_tuning = self.ml_analysis['hyperparameter_tuning']
            
            strategies.append({
                'strategy_type': 'Hyperparameter Tuning',
                'description': 'Implementar optimización automática de hiperparámetros',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        # Estrategias basadas en model deployment
        if self.ml_analysis and 'model_deployment' in self.ml_analysis:
            model_deployment = self.ml_analysis['model_deployment']
            
            strategies.append({
                'strategy_type': 'Model Deployment',
                'description': 'Implementar estrategias de deployment de modelos',
                'priority': 'high',
                'expected_impact': 'high'
            })
        
        self.ml_strategies = strategies
        return strategies
    
    def generate_ml_insights(self):
        """Generar insights de ML"""
        insights = []
        
        # Insights de evaluación general de ML
        if self.ml_analysis and 'overall_ml_assessment' in self.ml_analysis:
            assessment = self.ml_analysis['overall_ml_assessment']
            maturity_level = assessment.get('ml_maturity_level', 'Unknown')
            
            insights.append({
                'category': 'ML Maturity',
                'insight': f'Nivel de madurez de ML: {maturity_level}',
                'recommendation': f'{"Mantener" if maturity_level == "Advanced" else "Mejorar"} capacidades de ML',
                'priority': 'high' if maturity_level in ['Beginner', 'Basic'] else 'medium'
            })
            
            readiness_score = assessment.get('ml_readiness_score', 0)
            if readiness_score < 70:
                insights.append({
                    'category': 'ML Readiness',
                    'insight': f'Score de preparación para ML: {readiness_score}',
                    'recommendation': 'Mejorar preparación para implementación de ML',
                    'priority': 'high'
                })
            
            implementation_priority = assessment.get('ml_implementation_priority', 'Low')
            if implementation_priority == 'High':
                insights.append({
                    'category': 'ML Implementation',
                    'insight': f'Prioridad de implementación: {implementation_priority}',
                    'recommendation': 'Priorizar implementación de ML',
                    'priority': 'high'
                })
            
            roi_potential = assessment.get('ml_roi_potential', 'Low')
            if roi_potential in ['High', 'Very High']:
                insights.append({
                    'category': 'ML ROI',
                    'insight': f'Potencial de ROI: {roi_potential}',
                    'recommendation': 'Invertir en ML para maximizar ROI',
                    'priority': 'high'
                })
        
        # Insights de algoritmos de ML
        if self.ml_analysis and 'ml_algorithms' in self.ml_analysis:
            algorithms = self.ml_analysis['ml_algorithms']
            
            if 'classification' in algorithms:
                best_classification = algorithms['classification'].get('best_algorithm', 'Unknown')
                insights.append({
                    'category': 'Classification Algorithms',
                    'insight': f'Mejor algoritmo de clasificación: {best_classification}',
                    'recommendation': 'Usar este algoritmo para tareas de clasificación',
                    'priority': 'medium'
                })
            
            if 'regression' in algorithms:
                best_regression = algorithms['regression'].get('best_algorithm', 'Unknown')
                insights.append({
                    'category': 'Regression Algorithms',
                    'insight': f'Mejor algoritmo de regresión: {best_regression}',
                    'recommendation': 'Usar este algoritmo para tareas de regresión',
                    'priority': 'medium'
                })
        
        # Insights de feature engineering
        if self.ml_analysis and 'feature_engineering' in self.ml_analysis:
            feature_engineering = self.ml_analysis['feature_engineering']
            
            if 'feature_selection' in feature_engineering:
                best_selection = feature_engineering['feature_selection'].get('best_technique', 'Unknown')
                insights.append({
                    'category': 'Feature Selection',
                    'insight': f'Mejor técnica de feature selection: {best_selection}',
                    'recommendation': 'Implementar esta técnica para feature selection',
                    'priority': 'medium'
                })
        
        # Insights de modelos de ML
        if self.ml_models:
            model_evaluation = self.ml_models.get('model_evaluation', {})
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
                        'category': 'ML Model Performance',
                        'insight': f'Mejor modelo de ML: {best_model} con score {best_score:.3f}',
                        'recommendation': 'Usar este modelo para predicciones',
                        'priority': 'high'
                    })
        
        self.ml_insights = insights
        return insights
    
    def create_ml_dashboard(self):
        """Crear dashboard de ML"""
        if self.ml_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('ML Algorithms', 'Model Performance',
                          'ML Maturity', 'Implementation Priority'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de algoritmos de ML
        if self.ml_analysis and 'ml_algorithms' in self.ml_analysis:
            algorithms = self.ml_analysis['ml_algorithms']
            algorithm_names = list(algorithms.keys())
            algorithm_scores = [5] * len(algorithm_names)  # Placeholder scores
            
            fig.add_trace(
                go.Bar(x=algorithm_names, y=algorithm_scores, name='ML Algorithms'),
                row=1, col=1
            )
        
        # Gráfico de performance de modelos
        if self.ml_models:
            model_evaluation = self.ml_models.get('model_evaluation', {})
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
        
        # Gráfico de madurez de ML
        if self.ml_analysis and 'overall_ml_assessment' in self.ml_analysis:
            assessment = self.ml_analysis['overall_ml_assessment']
            maturity_level = assessment.get('ml_maturity_level', 'Unknown')
            
            maturity_data = {
                'Beginner': 1,
                'Basic': 2,
                'Intermediate': 3,
                'Advanced': 4
            }
            
            fig.add_trace(
                go.Pie(labels=list(maturity_data.keys()), values=list(maturity_data.values()), name='ML Maturity'),
                row=2, col=1
            )
        
        # Gráfico de prioridad de implementación
        if self.ml_analysis and 'overall_ml_assessment' in self.ml_analysis:
            assessment = self.ml_analysis['overall_ml_assessment']
            implementation_priority = assessment.get('ml_implementation_priority', 'Low')
            
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
            title="Dashboard de ML",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_ml_analysis(self, filename='marketing_ml_analysis.json'):
        """Exportar análisis de ML"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'ml_analysis': self.ml_analysis,
            'ml_models': {k: {'model_evaluation': v.get('model_evaluation', {})} for k, v in self.ml_models.items()},
            'ml_strategies': self.ml_strategies,
            'ml_insights': self.ml_insights,
            'summary': {
                'total_records': len(self.ml_data),
                'ml_maturity_level': self.ml_analysis.get('overall_ml_assessment', {}).get('ml_maturity_level', 'Unknown'),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de ML exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de ML de marketing
    ml_analyzer = MarketingMLAnalyzer()
    
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
        'ml_score': np.random.uniform(0, 100, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de ML de marketing
    print("📊 Cargando datos de ML de marketing...")
    ml_analyzer.load_ml_data(sample_data)
    
    # Analizar capacidades de ML
    print("🤖 Analizando capacidades de ML...")
    ml_analysis = ml_analyzer.analyze_ml_capabilities()
    
    # Construir modelos de ML
    print("🔮 Construyendo modelos de ML...")
    ml_models = ml_analyzer.build_ml_models(target_variable='ml_score', model_type='regression')
    
    # Generar estrategias de ML
    print("🎯 Generando estrategias de ML...")
    ml_strategies = ml_analyzer.generate_ml_strategies()
    
    # Generar insights de ML
    print("💡 Generando insights de ML...")
    ml_insights = ml_analyzer.generate_ml_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de ML...")
    dashboard = ml_analyzer.create_ml_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de ML...")
    export_data = ml_analyzer.export_ml_analysis()
    
    print("✅ Sistema de análisis de ML de marketing completado!")


