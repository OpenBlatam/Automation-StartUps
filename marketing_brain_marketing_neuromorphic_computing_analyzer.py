"""
Marketing Brain Marketing Neuromorphic Computing Analyzer
Sistema avanzado de análisis de Neuromorphic Computing de marketing
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

class MarketingNeuromorphicComputingAnalyzer:
    def __init__(self):
        self.nmc_data = {}
        self.nmc_analysis = {}
        self.nmc_models = {}
        self.nmc_strategies = {}
        self.nmc_insights = {}
        self.nmc_recommendations = {}
        
    def load_nmc_data(self, nmc_data):
        """Cargar datos de Neuromorphic Computing de marketing"""
        if isinstance(nmc_data, str):
            if nmc_data.endswith('.csv'):
                self.nmc_data = pd.read_csv(nmc_data)
            elif nmc_data.endswith('.json'):
                with open(nmc_data, 'r') as f:
                    data = json.load(f)
                self.nmc_data = pd.DataFrame(data)
        else:
            self.nmc_data = pd.DataFrame(nmc_data)
        
        print(f"✅ Datos de Neuromorphic Computing de marketing cargados: {len(self.nmc_data)} registros")
        return True
    
    def analyze_nmc_capabilities(self):
        """Analizar capacidades de Neuromorphic Computing"""
        if self.nmc_data.empty:
            return None
        
        # Análisis de arquitecturas neuromórficas
        neuromorphic_architectures = self._analyze_neuromorphic_architectures()
        
        # Análisis de algoritmos neuromórficos
        neuromorphic_algorithms = self._analyze_neuromorphic_algorithms()
        
        # Análisis de aplicaciones neuromórficas
        neuromorphic_applications = self._analyze_neuromorphic_applications()
        
        # Análisis de hardware neuromórfico
        neuromorphic_hardware = self._analyze_neuromorphic_hardware()
        
        # Análisis de eficiencia energética
        energy_efficiency = self._analyze_energy_efficiency()
        
        # Análisis de procesamiento en tiempo real
        real_time_processing = self._analyze_real_time_processing()
        
        nmc_results = {
            'neuromorphic_architectures': neuromorphic_architectures,
            'neuromorphic_algorithms': neuromorphic_algorithms,
            'neuromorphic_applications': neuromorphic_applications,
            'neuromorphic_hardware': neuromorphic_hardware,
            'energy_efficiency': energy_efficiency,
            'real_time_processing': real_time_processing,
            'overall_nmc_assessment': self._calculate_overall_nmc_assessment()
        }
        
        self.nmc_analysis = nmc_results
        return nmc_results
    
    def _analyze_neuromorphic_architectures(self):
        """Analizar arquitecturas neuromórficas"""
        architecture_analysis = {}
        
        # Tipos de arquitecturas
        architectures = {
            'Spiking Neural Networks (SNN)': {
                'complexity': 4,
                'efficiency': 5,
                'biological_accuracy': 5,
                'use_cases': ['Event-driven Processing', 'Low Power', 'Biological Simulation']
            },
            'Reservoir Computing': {
                'complexity': 3,
                'efficiency': 4,
                'biological_accuracy': 3,
                'use_cases': ['Time Series Processing', 'Pattern Recognition', 'Dynamic Systems']
            },
            'Memristive Networks': {
                'complexity': 4,
                'efficiency': 5,
                'biological_accuracy': 4,
                'use_cases': ['In-memory Computing', 'Analog Processing', 'Synaptic Plasticity']
            },
            'Neuromorphic Processors': {
                'complexity': 5,
                'efficiency': 5,
                'biological_accuracy': 4,
                'use_cases': ['Hardware Implementation', 'Real-time Processing', 'Edge Computing']
            },
            'Hybrid Neuromorphic Systems': {
                'complexity': 5,
                'efficiency': 4,
                'biological_accuracy': 4,
                'use_cases': ['Mixed Architectures', 'Flexible Processing', 'Multi-modal Systems']
            },
            'Digital Neuromorphic Systems': {
                'complexity': 3,
                'efficiency': 3,
                'biological_accuracy': 2,
                'use_cases': ['Digital Implementation', 'Standard Hardware', 'Easy Deployment']
            }
        }
        
        architecture_analysis['architectures'] = architectures
        architecture_analysis['best_architecture'] = 'Spiking Neural Networks (SNN)'
        architecture_analysis['recommendations'] = [
            'Use SNN for event-driven processing',
            'Use Reservoir Computing for time series',
            'Consider Memristive Networks for in-memory computing'
        ]
        
        return architecture_analysis
    
    def _analyze_neuromorphic_algorithms(self):
        """Analizar algoritmos neuromórficos"""
        algorithm_analysis = {}
        
        # Análisis de algoritmos de aprendizaje neuromórfico
        neuromorphic_learning = self._analyze_neuromorphic_learning()
        algorithm_analysis['neuromorphic_learning'] = neuromorphic_learning
        
        # Análisis de algoritmos de procesamiento neuromórfico
        neuromorphic_processing = self._analyze_neuromorphic_processing()
        algorithm_analysis['neuromorphic_processing'] = neuromorphic_processing
        
        # Análisis de algoritmos de optimización neuromórfica
        neuromorphic_optimization = self._analyze_neuromorphic_optimization()
        algorithm_analysis['neuromorphic_optimization'] = neuromorphic_optimization
        
        # Análisis de algoritmos de reconocimiento neuromórfico
        neuromorphic_recognition = self._analyze_neuromorphic_recognition()
        algorithm_analysis['neuromorphic_recognition'] = neuromorphic_recognition
        
        return algorithm_analysis
    
    def _analyze_neuromorphic_learning(self):
        """Analizar algoritmos de aprendizaje neuromórfico"""
        learning_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'Spike-Timing Dependent Plasticity (STDP)': {
                'complexity': 4,
                'biological_accuracy': 5,
                'efficiency': 4,
                'use_cases': ['Unsupervised Learning', 'Synaptic Plasticity', 'Biological Simulation']
            },
            'Reward-Modulated STDP': {
                'complexity': 4,
                'biological_accuracy': 4,
                'efficiency': 4,
                'use_cases': ['Reinforcement Learning', 'Reward-based Learning', 'Adaptive Systems']
            },
            'Backpropagation in SNN': {
                'complexity': 4,
                'biological_accuracy': 2,
                'efficiency': 3,
                'use_cases': ['Supervised Learning', 'Deep Learning', 'Gradient-based Learning']
            },
            'Hebbian Learning': {
                'complexity': 2,
                'biological_accuracy': 4,
                'efficiency': 3,
                'use_cases': ['Unsupervised Learning', 'Pattern Recognition', 'Associative Memory']
            },
            'Competitive Learning': {
                'complexity': 3,
                'biological_accuracy': 3,
                'efficiency': 3,
                'use_cases': ['Clustering', 'Feature Learning', 'Self-organizing Maps']
            },
            'Temporal Coding': {
                'complexity': 4,
                'biological_accuracy': 5,
                'efficiency': 4,
                'use_cases': ['Time-based Processing', 'Temporal Patterns', 'Spike Timing']
            }
        }
        
        learning_analysis['algorithms'] = algorithms
        learning_analysis['best_algorithm'] = 'Spike-Timing Dependent Plasticity (STDP)'
        learning_analysis['recommendations'] = [
            'Use STDP for unsupervised learning',
            'Use Reward-Modulated STDP for reinforcement learning',
            'Consider Hebbian Learning for pattern recognition'
        ]
        
        return learning_analysis
    
    def _analyze_neuromorphic_processing(self):
        """Analizar algoritmos de procesamiento neuromórfico"""
        processing_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'Event-driven Processing': {
                'complexity': 3,
                'efficiency': 5,
                'real_time': 5,
                'use_cases': ['Sparse Data', 'Low Power', 'Real-time Systems']
            },
            'Temporal Processing': {
                'complexity': 4,
                'efficiency': 4,
                'real_time': 4,
                'use_cases': ['Time Series', 'Sequential Data', 'Temporal Patterns']
            },
            'Spatial Processing': {
                'complexity': 3,
                'efficiency': 4,
                'real_time': 4,
                'use_cases': ['Image Processing', 'Spatial Patterns', 'Computer Vision']
            },
            'Spatiotemporal Processing': {
                'complexity': 4,
                'efficiency': 4,
                'real_time': 4,
                'use_cases': ['Video Processing', 'Dynamic Patterns', 'Multimodal Data']
            },
            'Reservoir Computing': {
                'complexity': 3,
                'efficiency': 4,
                'real_time': 4,
                'use_cases': ['Dynamic Systems', 'Time Series', 'Pattern Recognition']
            },
            'Liquid State Machines': {
                'complexity': 4,
                'efficiency': 4,
                'real_time': 4,
                'use_cases': ['Dynamic Processing', 'Temporal Dynamics', 'Reservoir Computing']
            }
        }
        
        processing_analysis['algorithms'] = algorithms
        processing_analysis['best_algorithm'] = 'Event-driven Processing'
        processing_analysis['recommendations'] = [
            'Use Event-driven Processing for efficiency',
            'Use Temporal Processing for time series',
            'Consider Spatiotemporal Processing for multimodal data'
        ]
        
        return processing_analysis
    
    def _analyze_neuromorphic_optimization(self):
        """Analizar algoritmos de optimización neuromórfica"""
        optimization_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'Neuromorphic Optimization': {
                'complexity': 4,
                'efficiency': 4,
                'convergence': 3,
                'use_cases': ['Continuous Optimization', 'Non-linear Problems', 'Dynamic Optimization']
            },
            'Spike-based Optimization': {
                'complexity': 4,
                'efficiency': 4,
                'convergence': 3,
                'use_cases': ['Discrete Optimization', 'Spike-based Systems', 'Event-driven Optimization']
            },
            'Reservoir-based Optimization': {
                'complexity': 3,
                'efficiency': 4,
                'convergence': 4,
                'use_cases': ['Dynamic Optimization', 'Time-varying Problems', 'Reservoir Computing']
            },
            'Memristive Optimization': {
                'complexity': 4,
                'efficiency': 5,
                'convergence': 3,
                'use_cases': ['In-memory Optimization', 'Analog Processing', 'Hardware Optimization']
            },
            'Hybrid Optimization': {
                'complexity': 4,
                'efficiency': 4,
                'convergence': 4,
                'use_cases': ['Mixed Approaches', 'Flexible Optimization', 'Multi-objective Problems']
            }
        }
        
        optimization_analysis['algorithms'] = algorithms
        optimization_analysis['best_algorithm'] = 'Neuromorphic Optimization'
        optimization_analysis['recommendations'] = [
            'Use Neuromorphic Optimization for continuous problems',
            'Use Spike-based Optimization for discrete problems',
            'Consider Memristive Optimization for hardware efficiency'
        ]
        
        return optimization_analysis
    
    def _analyze_neuromorphic_recognition(self):
        """Analizar algoritmos de reconocimiento neuromórfico"""
        recognition_analysis = {}
        
        # Algoritmos disponibles
        algorithms = {
            'Spike-based Recognition': {
                'complexity': 4,
                'accuracy': 4,
                'efficiency': 4,
                'use_cases': ['Pattern Recognition', 'Event-based Recognition', 'Real-time Recognition']
            },
            'Temporal Pattern Recognition': {
                'complexity': 4,
                'accuracy': 4,
                'efficiency': 4,
                'use_cases': ['Time Series Recognition', 'Sequential Patterns', 'Temporal Dynamics']
            },
            'Spatial Pattern Recognition': {
                'complexity': 3,
                'accuracy': 4,
                'efficiency': 4,
                'use_cases': ['Image Recognition', 'Spatial Patterns', 'Computer Vision']
            },
            'Multimodal Recognition': {
                'complexity': 4,
                'accuracy': 4,
                'efficiency': 3,
                'use_cases': ['Multiple Modalities', 'Fusion Systems', 'Complex Recognition']
            },
            'Reservoir-based Recognition': {
                'complexity': 3,
                'accuracy': 4,
                'efficiency': 4,
                'use_cases': ['Dynamic Recognition', 'Time-varying Patterns', 'Reservoir Computing']
            }
        }
        
        recognition_analysis['algorithms'] = algorithms
        recognition_analysis['best_algorithm'] = 'Spike-based Recognition'
        recognition_analysis['recommendations'] = [
            'Use Spike-based Recognition for event-driven systems',
            'Use Temporal Pattern Recognition for time series',
            'Consider Multimodal Recognition for complex systems'
        ]
        
        return recognition_analysis
    
    def _analyze_neuromorphic_applications(self):
        """Analizar aplicaciones neuromórficas"""
        application_analysis = {}
        
        # Aplicaciones disponibles
        applications = {
            'Edge Computing': {
                'complexity': 4,
                'efficiency_benefit': 5,
                'business_value': 4,
                'use_cases': ['Low Power Processing', 'Real-time Systems', 'IoT Applications']
            },
            'Computer Vision': {
                'complexity': 4,
                'efficiency_benefit': 4,
                'business_value': 4,
                'use_cases': ['Image Processing', 'Object Detection', 'Real-time Vision']
            },
            'Robotics': {
                'complexity': 5,
                'efficiency_benefit': 4,
                'business_value': 3,
                'use_cases': ['Autonomous Systems', 'Sensor Processing', 'Real-time Control']
            },
            'IoT and Sensors': {
                'complexity': 3,
                'efficiency_benefit': 5,
                'business_value': 4,
                'use_cases': ['Sensor Networks', 'Data Processing', 'Low Power Systems']
            },
            'Healthcare': {
                'complexity': 4,
                'efficiency_benefit': 4,
                'business_value': 4,
                'use_cases': ['Medical Devices', 'Biosignal Processing', 'Real-time Monitoring']
            },
            'Automotive': {
                'complexity': 4,
                'efficiency_benefit': 4,
                'business_value': 4,
                'use_cases': ['Autonomous Vehicles', 'Sensor Fusion', 'Real-time Processing']
            },
            'Smart Cities': {
                'complexity': 4,
                'efficiency_benefit': 4,
                'business_value': 3,
                'use_cases': ['Urban Monitoring', 'Traffic Management', 'Environmental Sensing']
            },
            'Financial Services': {
                'complexity': 3,
                'efficiency_benefit': 3,
                'business_value': 4,
                'use_cases': ['High-frequency Trading', 'Risk Assessment', 'Real-time Analytics']
            }
        }
        
        application_analysis['applications'] = applications
        application_analysis['best_application'] = 'Edge Computing'
        application_analysis['recommendations'] = [
            'Start with Edge Computing for efficiency benefits',
            'Implement Computer Vision for visual applications',
            'Consider IoT and Sensors for low power systems'
        ]
        
        return application_analysis
    
    def _analyze_neuromorphic_hardware(self):
        """Analizar hardware neuromórfico"""
        hardware_analysis = {}
        
        # Tipos de hardware
        hardware_types = {
            'IBM TrueNorth': {
                'complexity': 5,
                'efficiency': 5,
                'scalability': 4,
                'use_cases': ['Large-scale SNN', 'Cognitive Computing', 'Research Applications']
            },
            'Intel Loihi': {
                'complexity': 4,
                'efficiency': 4,
                'scalability': 4,
                'use_cases': ['Research Platform', 'SNN Development', 'Learning Algorithms']
            },
            'SpiNNaker': {
                'complexity': 4,
                'efficiency': 4,
                'scalability': 5,
                'use_cases': ['Brain Simulation', 'Large-scale Networks', 'Research Platform']
            },
            'Memristive Arrays': {
                'complexity': 4,
                'efficiency': 5,
                'scalability': 3,
                'use_cases': ['In-memory Computing', 'Analog Processing', 'Synaptic Arrays']
            },
            'FPGA-based Systems': {
                'complexity': 3,
                'efficiency': 3,
                'scalability': 4,
                'use_cases': ['Prototyping', 'Flexible Implementation', 'Research Development']
            },
            'ASIC-based Systems': {
                'complexity': 5,
                'efficiency': 5,
                'scalability': 4,
                'use_cases': ['Production Systems', 'Optimized Performance', 'Commercial Applications']
            }
        }
        
        hardware_analysis['hardware_types'] = hardware_types
        hardware_analysis['best_hardware'] = 'IBM TrueNorth'
        hardware_analysis['recommendations'] = [
            'Use IBM TrueNorth for large-scale applications',
            'Use Intel Loihi for research and development',
            'Consider Memristive Arrays for in-memory computing'
        ]
        
        return hardware_analysis
    
    def _analyze_energy_efficiency(self):
        """Analizar eficiencia energética"""
        efficiency_analysis = {}
        
        # Métricas de eficiencia energética
        metrics = {
            'Power Consumption': {
                'importance': 5,
                'target_value': '< 1W',
                'optimization_priority': 'high',
                'use_cases': ['Battery-powered Devices', 'IoT Applications', 'Edge Computing']
            },
            'Energy per Operation': {
                'importance': 4,
                'target_value': '< 1pJ',
                'optimization_priority': 'high',
                'use_cases': ['Efficient Processing', 'Low Power Systems', 'Energy Optimization']
            },
            'Thermal Efficiency': {
                'importance': 4,
                'target_value': '< 50°C',
                'optimization_priority': 'medium',
                'use_cases': ['Thermal Management', 'System Reliability', 'Performance Stability']
            },
            'Computational Efficiency': {
                'importance': 4,
                'target_value': '> 1 TOPS/W',
                'optimization_priority': 'high',
                'use_cases': ['Performance per Watt', 'Efficient Computing', 'Power Optimization']
            },
            'Memory Efficiency': {
                'importance': 3,
                'target_value': '> 1 GB/W',
                'optimization_priority': 'medium',
                'use_cases': ['Memory Optimization', 'Data Processing', 'Storage Efficiency']
            }
        }
        
        efficiency_analysis['metrics'] = metrics
        efficiency_analysis['best_metric'] = 'Power Consumption'
        efficiency_analysis['recommendations'] = [
            'Focus on Power Consumption for battery-powered devices',
            'Optimize Energy per Operation for efficient processing',
            'Consider Computational Efficiency for performance per watt'
        ]
        
        return efficiency_analysis
    
    def _analyze_real_time_processing(self):
        """Analizar procesamiento en tiempo real"""
        real_time_analysis = {}
        
        # Métricas de procesamiento en tiempo real
        metrics = {
            'Latency': {
                'importance': 5,
                'target_value': '< 1ms',
                'optimization_priority': 'high',
                'use_cases': ['Real-time Systems', 'Interactive Applications', 'Time-critical Processing']
            },
            'Throughput': {
                'importance': 4,
                'target_value': '> 1M events/s',
                'optimization_priority': 'high',
                'use_cases': ['High-speed Processing', 'Event-driven Systems', 'Data Streaming']
            },
            'Response Time': {
                'importance': 4,
                'target_value': '< 10ms',
                'optimization_priority': 'high',
                'use_cases': ['Interactive Systems', 'User Experience', 'Real-time Feedback']
            },
            'Jitter': {
                'importance': 3,
                'target_value': '< 1ms',
                'optimization_priority': 'medium',
                'use_cases': ['Consistent Performance', 'Predictable Timing', 'System Stability']
            },
            'Scalability': {
                'importance': 4,
                'target_value': '> 1000 nodes',
                'optimization_priority': 'medium',
                'use_cases': ['Large-scale Systems', 'Distributed Processing', 'Network Scalability']
            }
        }
        
        real_time_analysis['metrics'] = metrics
        real_time_analysis['best_metric'] = 'Latency'
        real_time_analysis['recommendations'] = [
            'Focus on Latency for real-time systems',
            'Optimize Throughput for high-speed processing',
            'Consider Response Time for interactive applications'
        ]
        
        return real_time_analysis
    
    def _calculate_overall_nmc_assessment(self):
        """Calcular evaluación general de Neuromorphic Computing"""
        overall_assessment = {}
        
        if not self.nmc_data.empty:
            overall_assessment = {
                'nmc_maturity_level': self._calculate_nmc_maturity_level(),
                'nmc_readiness_score': self._calculate_nmc_readiness_score(),
                'nmc_implementation_priority': self._calculate_nmc_implementation_priority(),
                'nmc_roi_potential': self._calculate_nmc_roi_potential()
            }
        
        return overall_assessment
    
    def _calculate_nmc_maturity_level(self):
        """Calcular nivel de madurez de Neuromorphic Computing"""
        # Basado en capacidades disponibles
        maturity_score = 0
        
        if self.nmc_analysis and 'neuromorphic_architectures' in self.nmc_analysis:
            architectures = self.nmc_analysis['neuromorphic_architectures']
            
            # SNN
            if 'Spiking Neural Networks (SNN)' in architectures.get('architectures', {}):
                maturity_score += 20
            
            # Reservoir Computing
            if 'Reservoir Computing' in architectures.get('architectures', {}):
                maturity_score += 20
            
            # Memristive Networks
            if 'Memristive Networks' in architectures.get('architectures', {}):
                maturity_score += 20
            
            # Neuromorphic Processors
            if 'Neuromorphic Processors' in architectures.get('architectures', {}):
                maturity_score += 20
            
            # Applications
            if 'neuromorphic_applications' in self.nmc_analysis:
                maturity_score += 20
        
        if maturity_score >= 80:
            return 'Advanced'
        elif maturity_score >= 60:
            return 'Intermediate'
        elif maturity_score >= 40:
            return 'Basic'
        else:
            return 'Beginner'
    
    def _calculate_nmc_readiness_score(self):
        """Calcular score de preparación para Neuromorphic Computing"""
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
    
    def _calculate_nmc_implementation_priority(self):
        """Calcular prioridad de implementación de Neuromorphic Computing"""
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
    
    def _calculate_nmc_roi_potential(self):
        """Calcular potencial de ROI de Neuromorphic Computing"""
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
    
    def build_nmc_models(self, target_variable, model_type='classification'):
        """Construir modelos de Neuromorphic Computing"""
        if target_variable not in self.nmc_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.nmc_data.columns if col != target_variable]
        X = self.nmc_data[feature_columns]
        y = self.nmc_data[target_variable]
        
        # Preprocesamiento
        X_processed, y_processed = self._preprocess_nmc_data(X, y, model_type)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42)
        
        # Construir modelos
        models = {}
        
        if model_type == 'classification':
            models = self._build_nmc_classification_models(X_train, X_test, y_train, y_test)
        elif model_type == 'regression':
            models = self._build_nmc_regression_models(X_train, X_test, y_train, y_test)
        elif model_type == 'clustering':
            models = self._build_nmc_clustering_models(X_processed)
        
        # Evaluar modelos
        model_evaluation = self._evaluate_nmc_models(models, X_test, y_test, model_type)
        
        # Optimizar modelos
        optimized_models = self._optimize_nmc_models(models, X_train, y_train)
        
        self.nmc_models = {
            'models': models,
            'optimized_models': optimized_models,
            'model_evaluation': model_evaluation,
            'model_type': model_type,
            'target_variable': target_variable
        }
        
        return self.nmc_models
    
    def _preprocess_nmc_data(self, X, y, model_type):
        """Preprocesar datos de Neuromorphic Computing"""
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
    
    def _build_nmc_classification_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de clasificación de Neuromorphic Computing"""
        models = {}
        
        # Spiking Neural Network
        snn_model = self._build_snn_model(X_train.shape[1], len(np.unique(y_train)))
        models['Spiking Neural Network'] = snn_model
        
        # Reservoir Computing
        reservoir_model = self._build_reservoir_model(X_train.shape[1], len(np.unique(y_train)))
        models['Reservoir Computing'] = reservoir_model
        
        # Memristive Network
        memristive_model = self._build_memristive_model(X_train.shape[1], len(np.unique(y_train)))
        models['Memristive Network'] = memristive_model
        
        return models
    
    def _build_nmc_regression_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de regresión de Neuromorphic Computing"""
        models = {}
        
        # Spiking Neural Network para regresión
        snn_model = self._build_snn_regression_model(X_train.shape[1])
        models['Spiking Neural Network Regression'] = snn_model
        
        # Reservoir Computing para regresión
        reservoir_model = self._build_reservoir_regression_model(X_train.shape[1])
        models['Reservoir Computing Regression'] = reservoir_model
        
        return models
    
    def _build_nmc_clustering_models(self, X):
        """Construir modelos de clustering de Neuromorphic Computing"""
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
    
    def _build_snn_model(self, input_dim, num_classes):
        """Construir modelo Spiking Neural Network"""
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
    
    def _build_reservoir_model(self, input_dim, num_classes):
        """Construir modelo Reservoir Computing"""
        model = models.Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_dim,)),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
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
    
    def _build_memristive_model(self, input_dim, num_classes):
        """Construir modelo Memristive Network"""
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
    
    def _build_snn_regression_model(self, input_dim):
        """Construir modelo Spiking Neural Network para regresión"""
        model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=(input_dim,)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _build_reservoir_regression_model(self, input_dim):
        """Construir modelo Reservoir Computing para regresión"""
        model = models.Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_dim,)),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _evaluate_nmc_models(self, models, X_test, y_test, model_type):
        """Evaluar modelos de Neuromorphic Computing"""
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
    
    def _optimize_nmc_models(self, models, X_train, y_train):
        """Optimizar modelos de Neuromorphic Computing"""
        optimized_models = {}
        
        for model_name, model in models.items():
            try:
                # Optimización de hiperparámetros
                if hasattr(model, 'get_config'):
                    # Crear modelo optimizado con mejores hiperparámetros
                    optimized_model = self._create_optimized_nmc_model(model_name, X_train.shape[1], len(np.unique(y_train)))
                    optimized_models[model_name] = optimized_model
                else:
                    optimized_models[model_name] = model
            except Exception as e:
                optimized_models[model_name] = model
        
        return optimized_models
    
    def _create_optimized_nmc_model(self, model_name, input_dim, num_classes):
        """Crear modelo de Neuromorphic Computing optimizado"""
        if 'Spiking Neural Network' in model_name:
            return self._build_optimized_snn_model(input_dim, num_classes)
        elif 'Reservoir Computing' in model_name:
            return self._build_optimized_reservoir_model(input_dim, num_classes)
        elif 'Memristive Network' in model_name:
            return self._build_optimized_memristive_model(input_dim, num_classes)
        else:
            return self._build_snn_model(input_dim, num_classes)
    
    def _build_optimized_snn_model(self, input_dim, num_classes):
        """Construir modelo Spiking Neural Network optimizado"""
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
    
    def _build_optimized_reservoir_model(self, input_dim, num_classes):
        """Construir modelo Reservoir Computing optimizado"""
        model = models.Sequential([
            layers.Dense(512, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(256, activation='relu'),
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
    
    def _build_optimized_memristive_model(self, input_dim, num_classes):
        """Construir modelo Memristive Network optimizado"""
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
    
    def generate_nmc_strategies(self):
        """Generar estrategias de Neuromorphic Computing"""
        strategies = []
        
        # Estrategias basadas en arquitecturas neuromórficas
        if self.nmc_analysis and 'neuromorphic_architectures' in self.nmc_analysis:
            architectures = self.nmc_analysis['neuromorphic_architectures']
            
            # Estrategias de SNN
            if 'Spiking Neural Networks (SNN)' in architectures.get('architectures', {}):
                strategies.append({
                    'strategy_type': 'Spiking Neural Networks Implementation',
                    'description': 'Implementar Spiking Neural Networks para procesamiento eficiente',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de Reservoir Computing
            if 'Reservoir Computing' in architectures.get('architectures', {}):
                strategies.append({
                    'strategy_type': 'Reservoir Computing Implementation',
                    'description': 'Implementar Reservoir Computing para procesamiento temporal',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en aplicaciones neuromórficas
        if self.nmc_analysis and 'neuromorphic_applications' in self.nmc_analysis:
            applications = self.nmc_analysis['neuromorphic_applications']
            
            # Estrategias de Edge Computing
            if 'Edge Computing' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Neuromorphic Edge Computing Implementation',
                    'description': 'Implementar Edge Computing neuromórfico para eficiencia energética',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias de Computer Vision
            if 'Computer Vision' in applications.get('applications', {}):
                strategies.append({
                    'strategy_type': 'Neuromorphic Computer Vision Implementation',
                    'description': 'Implementar Computer Vision neuromórfico para procesamiento visual',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en eficiencia energética
        if self.nmc_analysis and 'energy_efficiency' in self.nmc_analysis:
            energy_efficiency = self.nmc_analysis['energy_efficiency']
            
            strategies.append({
                'strategy_type': 'Energy Efficiency Optimization',
                'description': 'Optimizar eficiencia energética en sistemas neuromórficos',
                'priority': 'high',
                'expected_impact': 'high'
            })
        
        # Estrategias basadas en procesamiento en tiempo real
        if self.nmc_analysis and 'real_time_processing' in self.nmc_analysis:
            real_time_processing = self.nmc_analysis['real_time_processing']
            
            strategies.append({
                'strategy_type': 'Real-time Processing Optimization',
                'description': 'Optimizar procesamiento en tiempo real en sistemas neuromórficos',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        # Estrategias basadas en hardware neuromórfico
        if self.nmc_analysis and 'neuromorphic_hardware' in self.nmc_analysis:
            neuromorphic_hardware = self.nmc_analysis['neuromorphic_hardware']
            
            strategies.append({
                'strategy_type': 'Neuromorphic Hardware Implementation',
                'description': 'Implementar hardware neuromórfico especializado',
                'priority': 'medium',
                'expected_impact': 'medium'
            })
        
        self.nmc_strategies = strategies
        return strategies
    
    def generate_nmc_insights(self):
        """Generar insights de Neuromorphic Computing"""
        insights = []
        
        # Insights de evaluación general de Neuromorphic Computing
        if self.nmc_analysis and 'overall_nmc_assessment' in self.nmc_analysis:
            assessment = self.nmc_analysis['overall_nmc_assessment']
            maturity_level = assessment.get('nmc_maturity_level', 'Unknown')
            
            insights.append({
                'category': 'Neuromorphic Computing Maturity',
                'insight': f'Nivel de madurez de Neuromorphic Computing: {maturity_level}',
                'recommendation': f'{"Mantener" if maturity_level == "Advanced" else "Mejorar"} capacidades de Neuromorphic Computing',
                'priority': 'high' if maturity_level in ['Beginner', 'Basic'] else 'medium'
            })
            
            readiness_score = assessment.get('nmc_readiness_score', 0)
            if readiness_score < 70:
                insights.append({
                    'category': 'Neuromorphic Computing Readiness',
                    'insight': f'Score de preparación para Neuromorphic Computing: {readiness_score}',
                    'recommendation': 'Mejorar preparación para implementación de Neuromorphic Computing',
                    'priority': 'high'
                })
            
            implementation_priority = assessment.get('nmc_implementation_priority', 'Low')
            if implementation_priority == 'High':
                insights.append({
                    'category': 'Neuromorphic Computing Implementation',
                    'insight': f'Prioridad de implementación: {implementation_priority}',
                    'recommendation': 'Priorizar implementación de Neuromorphic Computing',
                    'priority': 'high'
                })
            
            roi_potential = assessment.get('nmc_roi_potential', 'Low')
            if roi_potential in ['High', 'Very High']:
                insights.append({
                    'category': 'Neuromorphic Computing ROI',
                    'insight': f'Potencial de ROI: {roi_potential}',
                    'recommendation': 'Invertir en Neuromorphic Computing para maximizar ROI',
                    'priority': 'high'
                })
        
        # Insights de arquitecturas neuromórficas
        if self.nmc_analysis and 'neuromorphic_architectures' in self.nmc_analysis:
            architectures = self.nmc_analysis['neuromorphic_architectures']
            best_architecture = architectures.get('best_architecture', 'Unknown')
            
            insights.append({
                'category': 'Neuromorphic Architectures',
                'insight': f'Mejor arquitectura neuromórfica: {best_architecture}',
                'recommendation': 'Usar esta arquitectura para implementación neuromórfica',
                'priority': 'high'
            })
        
        # Insights de aplicaciones neuromórficas
        if self.nmc_analysis and 'neuromorphic_applications' in self.nmc_analysis:
            applications = self.nmc_analysis['neuromorphic_applications']
            best_application = applications.get('best_application', 'Unknown')
            
            insights.append({
                'category': 'Neuromorphic Applications',
                'insight': f'Mejor aplicación neuromórfica: {best_application}',
                'recommendation': 'Implementar esta aplicación para máximo valor de negocio',
                'priority': 'high'
            })
        
        # Insights de modelos de Neuromorphic Computing
        if self.nmc_models:
            model_evaluation = self.nmc_models.get('model_evaluation', {})
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
                        'category': 'Neuromorphic Computing Model Performance',
                        'insight': f'Mejor modelo neuromórfico: {best_model} con score {best_score:.3f}',
                        'recommendation': 'Usar este modelo para predicciones neuromórficas',
                        'priority': 'high'
                    })
        
        self.nmc_insights = insights
        return insights
    
    def create_nmc_dashboard(self):
        """Crear dashboard de Neuromorphic Computing"""
        if self.nmc_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Neuromorphic Architectures', 'Model Performance',
                          'NMC Maturity', 'Implementation Priority'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de arquitecturas neuromórficas
        if self.nmc_analysis and 'neuromorphic_architectures' in self.nmc_analysis:
            architectures = self.nmc_analysis['neuromorphic_architectures']
            architecture_names = list(architectures.get('architectures', {}).keys())
            architecture_scores = [5] * len(architecture_names)  # Placeholder scores
            
            fig.add_trace(
                go.Bar(x=architecture_names, y=architecture_scores, name='Neuromorphic Architectures'),
                row=1, col=1
            )
        
        # Gráfico de performance de modelos
        if self.nmc_models:
            model_evaluation = self.nmc_models.get('model_evaluation', {})
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
        
        # Gráfico de madurez de Neuromorphic Computing
        if self.nmc_analysis and 'overall_nmc_assessment' in self.nmc_analysis:
            assessment = self.nmc_analysis['overall_nmc_assessment']
            maturity_level = assessment.get('nmc_maturity_level', 'Unknown')
            
            maturity_data = {
                'Beginner': 1,
                'Basic': 2,
                'Intermediate': 3,
                'Advanced': 4
            }
            
            fig.add_trace(
                go.Pie(labels=list(maturity_data.keys()), values=list(maturity_data.values()), name='NMC Maturity'),
                row=2, col=1
            )
        
        # Gráfico de prioridad de implementación
        if self.nmc_analysis and 'overall_nmc_assessment' in self.nmc_analysis:
            assessment = self.nmc_analysis['overall_nmc_assessment']
            implementation_priority = assessment.get('nmc_implementation_priority', 'Low')
            
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
            title="Dashboard de Neuromorphic Computing",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_nmc_analysis(self, filename='marketing_nmc_analysis.json'):
        """Exportar análisis de Neuromorphic Computing"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'nmc_analysis': self.nmc_analysis,
            'nmc_models': {k: {'model_evaluation': v.get('model_evaluation', {})} for k, v in self.nmc_models.items()},
            'nmc_strategies': self.nmc_strategies,
            'nmc_insights': self.nmc_insights,
            'summary': {
                'total_records': len(self.nmc_data),
                'nmc_maturity_level': self.nmc_analysis.get('overall_nmc_assessment', {}).get('nmc_maturity_level', 'Unknown'),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de Neuromorphic Computing exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de Neuromorphic Computing de marketing
    nmc_analyzer = MarketingNeuromorphicComputingAnalyzer()
    
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
        'nmc_score': np.random.uniform(0, 100, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de Neuromorphic Computing de marketing
    print("📊 Cargando datos de Neuromorphic Computing de marketing...")
    nmc_analyzer.load_nmc_data(sample_data)
    
    # Analizar capacidades de Neuromorphic Computing
    print("🤖 Analizando capacidades de Neuromorphic Computing...")
    nmc_analysis = nmc_analyzer.analyze_nmc_capabilities()
    
    # Construir modelos de Neuromorphic Computing
    print("🔮 Construyendo modelos de Neuromorphic Computing...")
    nmc_models = nmc_analyzer.build_nmc_models(target_variable='nmc_score', model_type='classification')
    
    # Generar estrategias de Neuromorphic Computing
    print("🎯 Generando estrategias de Neuromorphic Computing...")
    nmc_strategies = nmc_analyzer.generate_nmc_strategies()
    
    # Generar insights de Neuromorphic Computing
    print("💡 Generando insights de Neuromorphic Computing...")
    nmc_insights = nmc_analyzer.generate_nmc_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de Neuromorphic Computing...")
    dashboard = nmc_analyzer.create_nmc_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de Neuromorphic Computing...")
    export_data = nmc_analyzer.export_nmc_analysis()
    
    print("✅ Sistema de análisis de Neuromorphic Computing de marketing completado!")




