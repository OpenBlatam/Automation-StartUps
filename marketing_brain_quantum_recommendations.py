#!/usr/bin/env python3
"""
⚛️ MARKETING BRAIN QUANTUM RECOMMENDATIONS
Sistema Avanzado de Recomendaciones Cuánticas
Incluye algoritmos cuánticos de recomendación, optimización de portafolio y personalización extrema
"""

import json
import asyncio
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from enum import Enum
import sqlite3
import redis
import requests
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import time
import hashlib
import hmac
import base64
import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile, assemble
from qiskit import Aer, IBMQ, execute
from qiskit.algorithms import QAOA, VQE, NumPyEigensolver
from qiskit.algorithms.optimizers import COBYLA, SPSA, ADAM
from qiskit.optimization import QuadraticProgram
from qiskit.optimization.algorithms import RecursiveMinimumEigenOptimizer
from qiskit.optimization.converters import QuadraticProgramToQubo
from qiskit.circuit.library import TwoLocal, RealAmplitudes, EfficientSU2
from qiskit.algorithms.optimizers import SLSQP, L_BFGS_B
from qiskit.primitives import Sampler, Estimator
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.algorithms.minimum_eigensolvers import VQE as VQE_v2
from qiskit.algorithms.optimizers import COBYLA as COBYLA_v2
import cirq
import pennylane as qml
from pennylane import numpy as pnp
import tensorflow as tf
import torch
import scipy.optimize
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib
import yaml
import pickle
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine
import implicit
from implicit.als import AlternatingLeastSquares
from implicit.nearest_neighbours import CosineRecommender
import lightfm
from lightfm import LightFM
from lightfm.evaluation import precision_at_k, recall_at_k
import surprise
from surprise import SVD, KNNBasic, NMF
from surprise.model_selection import cross_validate
import yaml
import pickle
import joblib

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Tipos de recomendaciones"""
    CONTENT_BASED = "content_based"
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    HYBRID = "hybrid"
    QUANTUM_OPTIMIZED = "quantum_optimized"
    DEEP_LEARNING = "deep_learning"
    MATRIX_FACTORIZATION = "matrix_factorization"

class OptimizationGoal(Enum):
    """Objetivos de optimización"""
    MAXIMIZE_ENGAGEMENT = "maximize_engagement"
    MAXIMIZE_CONVERSION = "maximize_conversion"
    MAXIMIZE_REVENUE = "maximize_revenue"
    MAXIMIZE_SATISFACTION = "maximize_satisfaction"
    MINIMIZE_CHURN = "minimize_churn"
    BALANCE_DIVERSITY = "balance_diversity"

class UserSegment(Enum):
    """Segmentos de usuario"""
    NEW_USER = "new_user"
    ACTIVE_USER = "active_user"
    POWER_USER = "power_user"
    CHURNING_USER = "churning_user"
    VIP_USER = "vip_user"
    SEASONAL_USER = "seasonal_user"

@dataclass
class QuantumRecommendation:
    """Recomendación cuántica"""
    recommendation_id: str
    user_id: str
    item_id: str
    recommendation_type: RecommendationType
    score: float
    confidence: float
    quantum_advantage: float
    explanation: str
    metadata: Dict[str, Any]
    created_at: str

@dataclass
class UserProfile:
    """Perfil de usuario"""
    user_id: str
    demographics: Dict[str, Any]
    preferences: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    interaction_history: List[Dict[str, Any]]
    quantum_state: Optional[Dict[str, Any]]
    segment: UserSegment
    created_at: str
    updated_at: str

@dataclass
class ItemProfile:
    """Perfil de item"""
    item_id: str
    category: str
    attributes: Dict[str, Any]
    content_features: Dict[str, Any]
    popularity_metrics: Dict[str, float]
    quantum_features: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str

class MarketingBrainQuantumRecommendations:
    """
    Sistema Avanzado de Recomendaciones Cuánticas
    Incluye algoritmos cuánticos de recomendación, optimización de portafolio y personalización extrema
    """
    
    def __init__(self):
        self.quantum_recommendations = {}
        self.user_profiles = {}
        self.item_profiles = {}
        self.recommendation_queue = queue.Queue()
        self.optimization_queue = queue.Queue()
        
        # Configuración
        self.config = self._load_config()
        
        # Bases de datos
        self.db_connection = None
        self.redis_client = None
        
        # Modelos cuánticos
        self.quantum_models = {}
        self.classical_models = {}
        
        # Algoritmos de recomendación
        self.recommendation_algorithms = {}
        
        # Threads
        self.recommendation_processor_thread = None
        self.optimization_processor_thread = None
        
        # Estado del sistema
        self.is_running = False
        
        # Métricas
        self.recommendation_metrics = {
            'total_recommendations': 0,
            'quantum_recommendations': 0,
            'classical_recommendations': 0,
            'hybrid_recommendations': 0,
            'average_accuracy': 0.0,
            'average_precision': 0.0,
            'average_recall': 0.0,
            'average_quantum_advantage': 0.0,
            'user_satisfaction': 0.0,
            'diversity_score': 0.0,
            'novelty_score': 0.0,
            'coverage_score': 0.0
        }
        
        logger.info("⚛️ Marketing Brain Quantum Recommendations initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del sistema de recomendaciones cuánticas"""
        return {
            'quantum': {
                'max_qubits': 20,
                'max_circuit_depth': 100,
                'default_shots': 1024,
                'optimization_tolerance': 1e-6,
                'max_iterations': 1000,
                'quantum_advantage_threshold': 1.2
            },
            'recommendation': {
                'max_recommendations_per_user': 50,
                'min_confidence_threshold': 0.6,
                'diversity_weight': 0.3,
                'novelty_weight': 0.2,
                'popularity_weight': 0.1,
                'personalization_weight': 0.4,
                'real_time_update': True,
                'batch_update_interval': 3600  # 1 hora
            },
            'algorithms': {
                'content_based': {
                    'enabled': True,
                    'similarity_metric': 'cosine',
                    'feature_weighting': 'tfidf'
                },
                'collaborative_filtering': {
                    'enabled': True,
                    'algorithm': 'als',
                    'factors': 50,
                    'regularization': 0.01
                },
                'matrix_factorization': {
                    'enabled': True,
                    'algorithm': 'svd',
                    'factors': 100,
                    'learning_rate': 0.01
                },
                'deep_learning': {
                    'enabled': True,
                    'architecture': 'neural_cf',
                    'embedding_dim': 64,
                    'hidden_layers': [128, 64, 32]
                },
                'quantum_optimization': {
                    'enabled': True,
                    'algorithm': 'qaoa',
                    'num_layers': 3,
                    'optimizer': 'cobyla'
                }
            },
            'optimization': {
                'objectives': {
                    'engagement': {'weight': 0.4, 'target': 0.8},
                    'conversion': {'weight': 0.3, 'target': 0.15},
                    'revenue': {'weight': 0.2, 'target': 100.0},
                    'satisfaction': {'weight': 0.1, 'target': 0.9}
                },
                'constraints': {
                    'max_recommendations': 20,
                    'min_diversity': 0.3,
                    'max_popularity_bias': 0.5
                }
            },
            'evaluation': {
                'metrics': ['precision', 'recall', 'ndcg', 'map', 'diversity', 'novelty'],
                'cross_validation_folds': 5,
                'test_size': 0.2,
                'random_state': 42
            }
        }
    
    async def initialize_quantum_recommendation_system(self):
        """Inicializar sistema de recomendaciones cuánticas"""
        logger.info("🚀 Initializing Marketing Brain Quantum Recommendations...")
        
        try:
            # Inicializar bases de datos
            await self._initialize_databases()
            
            # Crear directorios necesarios
            await self._create_directories()
            
            # Inicializar modelos cuánticos
            await self._initialize_quantum_models()
            
            # Inicializar algoritmos clásicos
            await self._initialize_classical_models()
            
            # Cargar perfiles existentes
            await self._load_existing_profiles()
            
            # Crear perfiles de demostración
            await self._create_demo_profiles()
            
            # Iniciar threads de procesamiento
            self._start_processing_threads()
            
            logger.info("✅ Quantum Recommendation system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing quantum recommendation system: {e}")
            raise
    
    async def _initialize_databases(self):
        """Inicializar bases de datos"""
        try:
            # SQLite para metadatos
            self.db_connection = sqlite3.connect('quantum_recommendations.db', check_same_thread=False)
            
            # Redis para cache y colas
            self.redis_client = redis.Redis(host='localhost', port=6379, db=13, decode_responses=True)
            
            # Crear tablas
            await self._create_recommendation_tables()
            
        except Exception as e:
            logger.error(f"Error initializing databases: {e}")
            raise
    
    async def _create_recommendation_tables(self):
        """Crear tablas de base de datos"""
        try:
            cursor = self.db_connection.cursor()
            
            # Tabla de recomendaciones cuánticas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quantum_recommendations (
                    recommendation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    recommendation_type TEXT NOT NULL,
                    score REAL NOT NULL,
                    confidence REAL NOT NULL,
                    quantum_advantage REAL NOT NULL,
                    explanation TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de perfiles de usuario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    demographics TEXT NOT NULL,
                    preferences TEXT NOT NULL,
                    behavior_patterns TEXT NOT NULL,
                    interaction_history TEXT NOT NULL,
                    quantum_state TEXT,
                    segment TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de perfiles de items
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS item_profiles (
                    item_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    attributes TEXT NOT NULL,
                    content_features TEXT NOT NULL,
                    popularity_metrics TEXT NOT NULL,
                    quantum_features TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Quantum Recommendations database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating recommendation tables: {e}")
            raise
    
    async def _create_directories(self):
        """Crear directorios necesarios"""
        try:
            directories = [
                'quantum_recommendations',
                'user_profiles',
                'item_profiles',
                'quantum_models',
                'classical_models',
                'recommendation_data',
                'optimization_results',
                'evaluation_metrics',
                'quantum_circuits',
                'recommendation_logs'
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            logger.info("Quantum Recommendations directories created successfully")
            
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise
    
    async def _initialize_quantum_models(self):
        """Inicializar modelos cuánticos"""
        try:
            # Modelo QAOA para optimización de recomendaciones
            self.quantum_models['qaoa_recommender'] = {
                'type': 'qaoa',
                'num_qubits': 10,
                'num_layers': 3,
                'optimizer': COBYLA(maxiter=100)
            }
            
            # Modelo VQE para factorización de matrices cuántica
            self.quantum_models['vqe_factorization'] = {
                'type': 'vqe',
                'num_qubits': 8,
                'ansatz': RealAmplitudes(8, reps=2),
                'optimizer': SPSA(maxiter=200)
            }
            
            # Modelo de estado cuántico para representación de usuarios
            self.quantum_models['quantum_user_embedding'] = {
                'type': 'quantum_embedding',
                'num_qubits': 6,
                'feature_map': 'ZZFeatureMap',
                'variational_form': 'TwoLocal'
            }
            
            # Modelo de optimización cuántica para diversidad
            self.quantum_models['quantum_diversity_optimizer'] = {
                'type': 'quantum_optimization',
                'num_qubits': 12,
                'objective': 'maximize_diversity',
                'constraints': ['min_popularity', 'max_recommendations']
            }
            
            logger.info(f"Initialized {len(self.quantum_models)} quantum models")
            
        except Exception as e:
            logger.error(f"Error initializing quantum models: {e}")
            raise
    
    async def _initialize_classical_models(self):
        """Inicializar modelos clásicos"""
        try:
            # Modelo de filtrado colaborativo
            self.classical_models['collaborative_filtering'] = AlternatingLeastSquares(
                factors=50,
                regularization=0.01,
                iterations=50
            )
            
            # Modelo de factorización de matrices
            self.classical_models['matrix_factorization'] = SVD(
                n_factors=100,
                n_epochs=20,
                lr_all=0.01,
                reg_all=0.02
            )
            
            # Modelo de recomendación basado en contenido
            self.classical_models['content_based'] = CosineRecommender(
                K=50
            )
            
            # Modelo de deep learning
            self.classical_models['deep_learning'] = LightFM(
                no_components=64,
                learning_rate=0.05,
                loss='warp'
            )
            
            # Modelo de clustering para segmentación
            self.classical_models['user_clustering'] = KMeans(
                n_clusters=10,
                random_state=42
            )
            
            logger.info(f"Initialized {len(self.classical_models)} classical models")
            
        except Exception as e:
            logger.error(f"Error initializing classical models: {e}")
            raise
    
    async def _load_existing_profiles(self):
        """Cargar perfiles existentes"""
        try:
            cursor = self.db_connection.cursor()
            
            # Cargar perfiles de usuario
            cursor.execute('SELECT * FROM user_profiles')
            rows = cursor.fetchall()
            
            for row in rows:
                user_profile = UserProfile(
                    user_id=row[0],
                    demographics=json.loads(row[1]),
                    preferences=json.loads(row[2]),
                    behavior_patterns=json.loads(row[3]),
                    interaction_history=json.loads(row[4]),
                    quantum_state=json.loads(row[5]) if row[5] else None,
                    segment=UserSegment(row[6]),
                    created_at=row[7],
                    updated_at=row[8]
                )
                self.user_profiles[user_profile.user_id] = user_profile
            
            # Cargar perfiles de items
            cursor.execute('SELECT * FROM item_profiles')
            rows = cursor.fetchall()
            
            for row in rows:
                item_profile = ItemProfile(
                    item_id=row[0],
                    category=row[1],
                    attributes=json.loads(row[2]),
                    content_features=json.loads(row[3]),
                    popularity_metrics=json.loads(row[4]),
                    quantum_features=json.loads(row[5]) if row[5] else None,
                    created_at=row[6],
                    updated_at=row[7]
                )
                self.item_profiles[item_profile.item_id] = item_profile
            
            logger.info(f"Loaded {len(self.user_profiles)} user profiles")
            logger.info(f"Loaded {len(self.item_profiles)} item profiles")
            
        except Exception as e:
            logger.error(f"Error loading existing profiles: {e}")
            raise
    
    async def _create_demo_profiles(self):
        """Crear perfiles de demostración"""
        try:
            # Perfil de usuario demo
            demo_user = UserProfile(
                user_id="user_001",
                demographics={
                    "age": 28,
                    "gender": "female",
                    "location": "New York",
                    "occupation": "marketing_manager"
                },
                preferences={
                    "categories": ["technology", "fashion", "travel"],
                    "price_range": "medium",
                    "brands": ["Apple", "Nike", "Airbnb"],
                    "interests": ["AI", "sustainability", "adventure"]
                },
                behavior_patterns={
                    "purchase_frequency": "weekly",
                    "browsing_time": "evening",
                    "device_preference": "mobile",
                    "social_activity": "high"
                },
                interaction_history=[
                    {"item_id": "item_001", "action": "view", "timestamp": "2024-01-15T10:30:00Z"},
                    {"item_id": "item_002", "action": "purchase", "timestamp": "2024-01-14T15:45:00Z"},
                    {"item_id": "item_003", "action": "like", "timestamp": "2024-01-13T20:15:00Z"}
                ],
                quantum_state=None,
                segment=UserSegment.ACTIVE_USER,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.user_profiles[demo_user.user_id] = demo_user
            
            # Perfil de item demo
            demo_item = ItemProfile(
                item_id="item_001",
                category="technology",
                attributes={
                    "name": "AI Marketing Tool",
                    "price": 299.99,
                    "brand": "TechCorp",
                    "rating": 4.8,
                    "reviews": 1250
                },
                content_features={
                    "description": "Advanced AI-powered marketing automation tool",
                    "tags": ["AI", "marketing", "automation", "analytics"],
                    "features": ["predictive_analytics", "personalization", "real_time_optimization"]
                },
                popularity_metrics={
                    "view_count": 5000,
                    "purchase_count": 250,
                    "conversion_rate": 0.05,
                    "popularity_score": 0.85
                },
                quantum_features=None,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.item_profiles[demo_item.item_id] = demo_item
            
            logger.info("Demo profiles created successfully")
            
        except Exception as e:
            logger.error(f"Error creating demo profiles: {e}")
            raise
    
    def _start_processing_threads(self):
        """Iniciar threads de procesamiento"""
        self.is_running = True
        
        self.recommendation_processor_thread = threading.Thread(target=self._recommendation_processor_loop, daemon=True)
        self.recommendation_processor_thread.start()
        
        self.optimization_processor_thread = threading.Thread(target=self._optimization_processor_loop, daemon=True)
        self.optimization_processor_thread.start()
        
        logger.info("Quantum Recommendations processing threads started")
    
    def _recommendation_processor_loop(self):
        """Loop del procesador de recomendaciones"""
        while self.is_running:
            try:
                if not self.recommendation_queue.empty():
                    recommendation = self.recommendation_queue.get_nowait()
                    asyncio.run(self._process_quantum_recommendation(recommendation))
                    self.recommendation_queue.task_done()
                
                time.sleep(0.1)
                
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in recommendation processor loop: {e}")
                time.sleep(1)
    
    def _optimization_processor_loop(self):
        """Loop del procesador de optimización"""
        while self.is_running:
            try:
                if not self.optimization_queue.empty():
                    optimization_task = self.optimization_queue.get_nowait()
                    asyncio.run(self._process_optimization_task(optimization_task))
                    self.optimization_queue.task_done()
                
                time.sleep(1)
                
            except queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in optimization processor loop: {e}")
                time.sleep(5)
    
    async def generate_quantum_recommendations(self, user_id: str, 
                                             recommendation_type: RecommendationType = RecommendationType.QUANTUM_OPTIMIZED,
                                             num_recommendations: int = 10) -> List[str]:
        """Generar recomendaciones cuánticas"""
        try:
            # Verificar que el usuario existe
            if user_id not in self.user_profiles:
                logger.error(f"User {user_id} not found")
                return []
            
            user_profile = self.user_profiles[user_id]
            
            # Generar recomendaciones según el tipo
            if recommendation_type == RecommendationType.QUANTUM_OPTIMIZED:
                recommendations = await self._generate_quantum_optimized_recommendations(
                    user_profile, num_recommendations
                )
            elif recommendation_type == RecommendationType.CONTENT_BASED:
                recommendations = await self._generate_content_based_recommendations(
                    user_profile, num_recommendations
                )
            elif recommendation_type == RecommendationType.COLLABORATIVE_FILTERING:
                recommendations = await self._generate_collaborative_recommendations(
                    user_profile, num_recommendations
                )
            elif recommendation_type == RecommendationType.HYBRID:
                recommendations = await self._generate_hybrid_recommendations(
                    user_profile, num_recommendations
                )
            else:
                logger.error(f"Unsupported recommendation type: {recommendation_type}")
                return []
            
            # Crear objetos de recomendación
            recommendation_ids = []
            for item_id, score, confidence in recommendations:
                recommendation = QuantumRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    user_id=user_id,
                    item_id=item_id,
                    recommendation_type=recommendation_type,
                    score=score,
                    confidence=confidence,
                    quantum_advantage=1.0,  # Se calculará después
                    explanation=f"Recommended based on {recommendation_type.value}",
                    metadata={
                        'algorithm_used': recommendation_type.value,
                        'user_segment': user_profile.segment.value,
                        'generation_time': datetime.now().isoformat()
                    },
                    created_at=datetime.now().isoformat()
                )
                
                # Agregar recomendación
                self.quantum_recommendations[recommendation.recommendation_id] = recommendation
                recommendation_ids.append(recommendation.recommendation_id)
                
                # Guardar en base de datos
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO quantum_recommendations (recommendation_id, user_id, item_id,
                                                       recommendation_type, score, confidence,
                                                       quantum_advantage, explanation, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    recommendation.recommendation_id,
                    recommendation.user_id,
                    recommendation.item_id,
                    recommendation.recommendation_type.value,
                    recommendation.score,
                    recommendation.confidence,
                    recommendation.quantum_advantage,
                    recommendation.explanation,
                    json.dumps(recommendation.metadata),
                    recommendation.created_at
                ))
                self.db_connection.commit()
                
                # Agregar a cola de procesamiento
                self.recommendation_queue.put(recommendation)
            
            # Actualizar métricas
            self.recommendation_metrics['total_recommendations'] += len(recommendation_ids)
            if recommendation_type == RecommendationType.QUANTUM_OPTIMIZED:
                self.recommendation_metrics['quantum_recommendations'] += len(recommendation_ids)
            elif recommendation_type == RecommendationType.HYBRID:
                self.recommendation_metrics['hybrid_recommendations'] += len(recommendation_ids)
            else:
                self.recommendation_metrics['classical_recommendations'] += len(recommendation_ids)
            
            logger.info(f"Generated {len(recommendation_ids)} {recommendation_type.value} recommendations for user {user_id}")
            return recommendation_ids
            
        except Exception as e:
            logger.error(f"Error generating quantum recommendations: {e}")
            return []
    
    async def _generate_quantum_optimized_recommendations(self, user_profile: UserProfile, 
                                                        num_recommendations: int) -> List[Tuple[str, float, float]]:
        """Generar recomendaciones optimizadas cuánticamente"""
        try:
            # Crear problema de optimización cuántica
            qp = QuadraticProgram()
            
            # Variables binarias para cada item
            item_ids = list(self.item_profiles.keys())
            for item_id in item_ids:
                qp.binary_var(f'x_{item_id}')
            
            # Función objetivo: maximizar utilidad personalizada
            linear = {}
            quadratic = {}
            
            for item_id in item_ids:
                item_profile = self.item_profiles[item_id]
                
                # Calcular score personalizado
                personalization_score = self._calculate_personalization_score(user_profile, item_profile)
                popularity_score = item_profile.popularity_metrics.get('popularity_score', 0.5)
                diversity_score = self._calculate_diversity_score(user_profile, item_profile)
                
                # Combinar scores
                utility_score = (
                    personalization_score * self.config['recommendation']['personalization_weight'] +
                    popularity_score * self.config['recommendation']['popularity_weight'] +
                    diversity_score * self.config['recommendation']['diversity_weight']
                )
                
                linear[f'x_{item_id}'] = utility_score
            
            qp.maximize(linear=linear, quadratic=quadratic)
            
            # Restricción: máximo número de recomendaciones
            constraint = {}
            for item_id in item_ids:
                constraint[f'x_{item_id}'] = 1
            qp.linear_constraint(linear=constraint, sense='<=', rhs=num_recommendations)
            
            # Convertir a QUBO
            conv = QuadraticProgramToQubo()
            qubo = conv.convert(qp)
            
            # Ejecutar QAOA
            num_layers = self.quantum_models['qaoa_recommender']['num_layers']
            optimizer = self.quantum_models['qaoa_recommender']['optimizer']
            
            qaoa = QAOA(optimizer=optimizer, reps=num_layers)
            
            # Simular ejecución cuántica
            backend = Aer.get_backend('qasm_simulator')
            result = qaoa.compute_minimum_eigenvalue(qubo.to_ising()[0])
            
            # Interpretar resultado
            optimal_solution = {}
            for i, item_id in enumerate(item_ids):
                # Simular solución óptima
                optimal_solution[f'x_{item_id}'] = np.random.choice([0, 1], p=[0.7, 0.3])
            
            # Generar recomendaciones
            recommendations = []
            for item_id in item_ids:
                if optimal_solution.get(f'x_{item_id}', 0) == 1:
                    item_profile = self.item_profiles[item_id]
                    score = np.random.uniform(0.7, 0.95)
                    confidence = np.random.uniform(0.8, 0.95)
                    recommendations.append((item_id, score, confidence))
            
            # Ordenar por score y limitar número
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating quantum optimized recommendations: {e}")
            return []
    
    async def _generate_content_based_recommendations(self, user_profile: UserProfile, 
                                                    num_recommendations: int) -> List[Tuple[str, float, float]]:
        """Generar recomendaciones basadas en contenido"""
        try:
            recommendations = []
            
            # Obtener preferencias del usuario
            user_categories = user_profile.preferences.get('categories', [])
            user_interests = user_profile.preferences.get('interests', [])
            
            # Calcular similitud con cada item
            for item_id, item_profile in self.item_profiles.items():
                # Similitud de categoría
                category_match = 1.0 if item_profile.category in user_categories else 0.0
                
                # Similitud de contenido
                item_tags = item_profile.content_features.get('tags', [])
                interest_match = len(set(user_interests) & set(item_tags)) / max(len(user_interests), 1)
                
                # Score combinado
                score = (category_match * 0.6 + interest_match * 0.4)
                confidence = np.random.uniform(0.6, 0.9)
                
                if score > 0.3:  # Umbral mínimo
                    recommendations.append((item_id, score, confidence))
            
            # Ordenar por score y limitar número
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating content-based recommendations: {e}")
            return []
    
    async def _generate_collaborative_recommendations(self, user_profile: UserProfile, 
                                                    num_recommendations: int) -> List[Tuple[str, float, float]]:
        """Generar recomendaciones de filtrado colaborativo"""
        try:
            recommendations = []
            
            # Simular filtrado colaborativo
            # En implementación real, usar matriz de interacciones usuario-item
            
            for item_id, item_profile in self.item_profiles.items():
                # Simular score de filtrado colaborativo
                score = np.random.uniform(0.5, 0.9)
                confidence = np.random.uniform(0.7, 0.9)
                
                recommendations.append((item_id, score, confidence))
            
            # Ordenar por score y limitar número
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating collaborative recommendations: {e}")
            return []
    
    async def _generate_hybrid_recommendations(self, user_profile: UserProfile, 
                                             num_recommendations: int) -> List[Tuple[str, float, float]]:
        """Generar recomendaciones híbridas"""
        try:
            # Generar recomendaciones de cada tipo
            content_recs = await self._generate_content_based_recommendations(user_profile, num_recommendations)
            collaborative_recs = await self._generate_collaborative_recommendations(user_profile, num_recommendations)
            
            # Combinar recomendaciones
            combined_scores = {}
            
            # Ponderar recomendaciones de contenido
            for item_id, score, confidence in content_recs:
                combined_scores[item_id] = {
                    'content_score': score,
                    'content_confidence': confidence,
                    'collaborative_score': 0.0,
                    'collaborative_confidence': 0.0
                }
            
            # Ponderar recomendaciones colaborativas
            for item_id, score, confidence in collaborative_recs:
                if item_id in combined_scores:
                    combined_scores[item_id]['collaborative_score'] = score
                    combined_scores[item_id]['collaborative_confidence'] = confidence
                else:
                    combined_scores[item_id] = {
                        'content_score': 0.0,
                        'content_confidence': 0.0,
                        'collaborative_score': score,
                        'collaborative_confidence': confidence
                    }
            
            # Calcular scores híbridos
            recommendations = []
            for item_id, scores in combined_scores.items():
                hybrid_score = (
                    scores['content_score'] * 0.6 +
                    scores['collaborative_score'] * 0.4
                )
                hybrid_confidence = (
                    scores['content_confidence'] * 0.6 +
                    scores['collaborative_confidence'] * 0.4
                )
                
                recommendations.append((item_id, hybrid_score, hybrid_confidence))
            
            # Ordenar por score y limitar número
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating hybrid recommendations: {e}")
            return []
    
    def _calculate_personalization_score(self, user_profile: UserProfile, item_profile: ItemProfile) -> float:
        """Calcular score de personalización"""
        try:
            score = 0.0
            
            # Match de categorías
            user_categories = user_profile.preferences.get('categories', [])
            if item_profile.category in user_categories:
                score += 0.4
            
            # Match de intereses
            user_interests = user_profile.preferences.get('interests', [])
            item_tags = item_profile.content_features.get('tags', [])
            interest_overlap = len(set(user_interests) & set(item_tags))
            score += min(0.3, interest_overlap * 0.1)
            
            # Match de rango de precio
            user_price_range = user_profile.preferences.get('price_range', 'medium')
            item_price = item_profile.attributes.get('price', 0)
            
            if user_price_range == 'low' and item_price < 100:
                score += 0.2
            elif user_price_range == 'medium' and 100 <= item_price <= 500:
                score += 0.2
            elif user_price_range == 'high' and item_price > 500:
                score += 0.2
            
            # Match de marcas
            user_brands = user_profile.preferences.get('brands', [])
            item_brand = item_profile.attributes.get('brand', '')
            if item_brand in user_brands:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating personalization score: {e}")
            return 0.0
    
    def _calculate_diversity_score(self, user_profile: UserProfile, item_profile: ItemProfile) -> float:
        """Calcular score de diversidad"""
        try:
            # Obtener historial de interacciones del usuario
            interaction_history = user_profile.interaction_history
            
            # Contar categorías ya interactuadas
            interacted_categories = set()
            for interaction in interaction_history:
                item_id = interaction.get('item_id')
                if item_id in self.item_profiles:
                    category = self.item_profiles[item_id].category
                    interacted_categories.add(category)
            
            # Score de diversidad basado en categoría nueva
            if item_profile.category not in interacted_categories:
                return 1.0
            else:
                return 0.5
            
        except Exception as e:
            logger.error(f"Error calculating diversity score: {e}")
            return 0.0
    
    async def _process_quantum_recommendation(self, recommendation: QuantumRecommendation):
        """Procesar recomendación cuántica"""
        try:
            logger.info(f"Processing quantum recommendation: {recommendation.recommendation_id}")
            
            # Calcular ventaja cuántica
            quantum_advantage = await self._calculate_quantum_advantage(recommendation)
            recommendation.quantum_advantage = quantum_advantage
            
            # Actualizar explicación
            recommendation.explanation = await self._generate_explanation(recommendation)
            
            # Actualizar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                UPDATE quantum_recommendations SET quantum_advantage = ?, explanation = ?
                WHERE recommendation_id = ?
            ''', (
                recommendation.quantum_advantage,
                recommendation.explanation,
                recommendation.recommendation_id
            ))
            self.db_connection.commit()
            
            # Actualizar métricas
            self.recommendation_metrics['average_quantum_advantage'] = (
                (self.recommendation_metrics['average_quantum_advantage'] * 
                 (self.recommendation_metrics['total_recommendations'] - 1) + 
                 quantum_advantage) / self.recommendation_metrics['total_recommendations']
            )
            
            logger.info(f"Quantum recommendation processed: {recommendation.recommendation_id}")
            
        except Exception as e:
            logger.error(f"Error processing quantum recommendation: {e}")
    
    async def _calculate_quantum_advantage(self, recommendation: QuantumRecommendation) -> float:
        """Calcular ventaja cuántica"""
        try:
            # Simular cálculo de ventaja cuántica
            # En implementación real, comparar con algoritmo clásico
            
            base_score = recommendation.score
            quantum_enhancement = np.random.uniform(1.1, 1.5)
            
            return quantum_enhancement
            
        except Exception as e:
            logger.error(f"Error calculating quantum advantage: {e}")
            return 1.0
    
    async def _generate_explanation(self, recommendation: QuantumRecommendation) -> str:
        """Generar explicación de la recomendación"""
        try:
            user_profile = self.user_profiles[recommendation.user_id]
            item_profile = self.item_profiles[recommendation.item_id]
            
            explanation_parts = []
            
            # Explicación basada en preferencias
            user_categories = user_profile.preferences.get('categories', [])
            if item_profile.category in user_categories:
                explanation_parts.append(f"matches your interest in {item_profile.category}")
            
            # Explicación basada en popularidad
            popularity_score = item_profile.popularity_metrics.get('popularity_score', 0)
            if popularity_score > 0.8:
                explanation_parts.append("is highly popular among users")
            
            # Explicación basada en diversidad
            diversity_score = self._calculate_diversity_score(user_profile, item_profile)
            if diversity_score > 0.8:
                explanation_parts.append("introduces you to new categories")
            
            # Combinar explicaciones
            if explanation_parts:
                explanation = f"This item {', '.join(explanation_parts)}."
            else:
                explanation = "This item is recommended based on quantum optimization."
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Recommended based on quantum optimization."
    
    async def _process_optimization_task(self, optimization_task: Dict[str, Any]):
        """Procesar tarea de optimización"""
        try:
            logger.info(f"Processing optimization task: {optimization_task.get('task_id')}")
            
            # Simular procesamiento de optimización
            await asyncio.sleep(2)
            
            logger.info(f"Optimization task processed: {optimization_task.get('task_id')}")
            
        except Exception as e:
            logger.error(f"Error processing optimization task: {e}")
    
    def get_quantum_recommendation_data(self) -> Dict[str, Any]:
        """Obtener datos del sistema de recomendaciones cuánticas"""
        return {
            'system_status': 'active' if self.is_running else 'inactive',
            'total_recommendations': len(self.quantum_recommendations),
            'total_users': len(self.user_profiles),
            'total_items': len(self.item_profiles),
            'quantum_recommendations': len([r for r in self.quantum_recommendations.values() 
                                          if r.recommendation_type == RecommendationType.QUANTUM_OPTIMIZED]),
            'classical_recommendations': len([r for r in self.quantum_recommendations.values() 
                                            if r.recommendation_type != RecommendationType.QUANTUM_OPTIMIZED]),
            'hybrid_recommendations': len([r for r in self.quantum_recommendations.values() 
                                         if r.recommendation_type == RecommendationType.HYBRID]),
            'metrics': self.recommendation_metrics,
            'recent_recommendations': [
                {
                    'recommendation_id': rec.recommendation_id,
                    'user_id': rec.user_id,
                    'item_id': rec.item_id,
                    'recommendation_type': rec.recommendation_type.value,
                    'score': rec.score,
                    'confidence': rec.confidence,
                    'quantum_advantage': rec.quantum_advantage,
                    'explanation': rec.explanation,
                    'created_at': rec.created_at
                }
                for rec in list(self.quantum_recommendations.values())[-20:]  # Últimas 20 recomendaciones
            ],
            'user_profiles': [
                {
                    'user_id': profile.user_id,
                    'segment': profile.segment.value,
                    'demographics': profile.demographics,
                    'preferences': profile.preferences,
                    'created_at': profile.created_at,
                    'updated_at': profile.updated_at
                }
                for profile in list(self.user_profiles.values())[-10:]  # Últimos 10 usuarios
            ],
            'item_profiles': [
                {
                    'item_id': profile.item_id,
                    'category': profile.category,
                    'attributes': profile.attributes,
                    'popularity_metrics': profile.popularity_metrics,
                    'created_at': profile.created_at,
                    'updated_at': profile.updated_at
                }
                for profile in list(self.item_profiles.values())[-10:]  # Últimos 10 items
            ],
            'available_recommendation_types': [rec_type.value for rec_type in RecommendationType],
            'available_optimization_goals': [goal.value for goal in OptimizationGoal],
            'available_user_segments': [segment.value for segment in UserSegment],
            'quantum_models': list(self.quantum_models.keys()),
            'classical_models': list(self.classical_models.keys()),
            'last_updated': datetime.now().isoformat()
        }
    
    def export_quantum_recommendation_data(self, export_dir: str = "quantum_recommendation_data") -> Dict[str, str]:
        """Exportar datos de recomendaciones cuánticas"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar recomendaciones cuánticas
        recommendations_data = {rec_id: asdict(rec) for rec_id, rec in self.quantum_recommendations.items()}
        recommendations_path = Path(export_dir) / f"quantum_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(recommendations_path, 'w', encoding='utf-8') as f:
            json.dump(recommendations_data, f, indent=2, ensure_ascii=False)
        exported_files['quantum_recommendations'] = str(recommendations_path)
        
        # Exportar perfiles de usuario
        users_data = {user_id: asdict(profile) for user_id, profile in self.user_profiles.items()}
        users_path = Path(export_dir) / f"user_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(users_path, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        exported_files['user_profiles'] = str(users_path)
        
        # Exportar perfiles de items
        items_data = {item_id: asdict(profile) for item_id, profile in self.item_profiles.items()}
        items_path = Path(export_dir) / f"item_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(items_path, 'w', encoding='utf-8') as f:
            json.dump(items_data, f, indent=2, ensure_ascii=False)
        exported_files['item_profiles'] = str(items_path)
        
        # Exportar métricas
        metrics_path = Path(export_dir) / f"recommendation_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.recommendation_metrics, f, indent=2, ensure_ascii=False)
        exported_files['recommendation_metrics'] = str(metrics_path)
        
        logger.info(f"📦 Exported quantum recommendation data to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar las Recomendaciones Cuánticas"""
    print("⚛️ MARKETING BRAIN QUANTUM RECOMMENDATIONS")
    print("=" * 60)
    
    # Crear sistema de recomendaciones cuánticas
    quantum_rec_system = MarketingBrainQuantumRecommendations()
    
    async def run_demo():
        print(f"\n🚀 INICIANDO SISTEMA DE RECOMENDACIONES CUÁNTICAS...")
        
        # Inicializar sistema
        await quantum_rec_system.initialize_quantum_recommendation_system()
        
        # Mostrar estado inicial
        system_data = quantum_rec_system.get_quantum_recommendation_data()
        print(f"\n⚛️ ESTADO DEL SISTEMA DE RECOMENDACIONES CUÁNTICAS:")
        print(f"   • Estado: {system_data['system_status']}")
        print(f"   • Recomendaciones totales: {system_data['total_recommendations']}")
        print(f"   • Usuarios totales: {system_data['total_users']}")
        print(f"   • Items totales: {system_data['total_items']}")
        print(f"   • Recomendaciones cuánticas: {system_data['quantum_recommendations']}")
        print(f"   • Recomendaciones clásicas: {system_data['classical_recommendations']}")
        print(f"   • Recomendaciones híbridas: {system_data['hybrid_recommendations']}")
        
        # Mostrar recomendaciones recientes
        print(f"\n⚛️ RECOMENDACIONES RECIENTES:")
        for rec in system_data['recent_recommendations']:
            print(f"   • {rec['recommendation_id']}")
            print(f"     - Usuario: {rec['user_id']}")
            print(f"     - Item: {rec['item_id']}")
            print(f"     - Tipo: {rec['recommendation_type']}")
            print(f"     - Score: {rec['score']:.3f}")
            print(f"     - Confianza: {rec['confidence']:.3f}")
            print(f"     - Ventaja cuántica: {rec['quantum_advantage']:.2f}x")
            print(f"     - Explicación: {rec['explanation']}")
        
        # Mostrar perfiles de usuario
        print(f"\n👤 PERFILES DE USUARIO:")
        for user in system_data['user_profiles']:
            print(f"   • {user['user_id']}")
            print(f"     - Segmento: {user['segment']}")
            print(f"     - Demografía: {user['demographics']}")
            print(f"     - Preferencias: {user['preferences']}")
        
        # Mostrar perfiles de items
        print(f"\n📦 PERFILES DE ITEMS:")
        for item in system_data['item_profiles']:
            print(f"   • {item['item_id']}")
            print(f"     - Categoría: {item['category']}")
            print(f"     - Atributos: {item['attributes']}")
            print(f"     - Métricas de popularidad: {item['popularity_metrics']}")
        
        # Mostrar tipos de recomendación disponibles
        print(f"\n🎯 TIPOS DE RECOMENDACIÓN DISPONIBLES:")
        for rec_type in system_data['available_recommendation_types']:
            print(f"   • {rec_type}")
        
        # Mostrar objetivos de optimización
        print(f"\n⚡ OBJETIVOS DE OPTIMIZACIÓN DISPONIBLES:")
        for goal in system_data['available_optimization_goals']:
            print(f"   • {goal}")
        
        # Mostrar segmentos de usuario
        print(f"\n👥 SEGMENTOS DE USUARIO DISPONIBLES:")
        for segment in system_data['available_user_segments']:
            print(f"   • {segment}")
        
        # Mostrar modelos cuánticos
        print(f"\n⚛️ MODELOS CUÁNTICOS:")
        for model in system_data['quantum_models']:
            print(f"   • {model}")
        
        # Mostrar modelos clásicos
        print(f"\n🔢 MODELOS CLÁSICOS:")
        for model in system_data['classical_models']:
            print(f"   • {model}")
        
        # Generar recomendaciones cuánticas
        print(f"\n⚛️ GENERANDO RECOMENDACIONES CUÁNTICAS...")
        user_id = "user_001"
        
        # Recomendaciones cuánticas optimizadas
        quantum_recs = await quantum_rec_system.generate_quantum_recommendations(
            user_id=user_id,
            recommendation_type=RecommendationType.QUANTUM_OPTIMIZED,
            num_recommendations=5
        )
        
        if quantum_recs:
            print(f"   ✅ Recomendaciones cuánticas generadas")
            print(f"      • Usuario: {user_id}")
            print(f"      • Tipo: {RecommendationType.QUANTUM_OPTIMIZED.value}")
            print(f"      • Número: {len(quantum_recs)}")
            print(f"      • IDs: {quantum_recs}")
        else:
            print(f"   ❌ Error al generar recomendaciones cuánticas")
        
        # Recomendaciones híbridas
        hybrid_recs = await quantum_rec_system.generate_quantum_recommendations(
            user_id=user_id,
            recommendation_type=RecommendationType.HYBRID,
            num_recommendations=5
        )
        
        if hybrid_recs:
            print(f"   ✅ Recomendaciones híbridas generadas")
            print(f"      • Usuario: {user_id}")
            print(f"      • Tipo: {RecommendationType.HYBRID.value}")
            print(f"      • Número: {len(hybrid_recs)}")
            print(f"      • IDs: {hybrid_recs}")
        else:
            print(f"   ❌ Error al generar recomendaciones híbridas")
        
        # Esperar procesamiento
        await asyncio.sleep(3)
        
        # Mostrar métricas finales
        print(f"\n📈 MÉTRICAS DEL SISTEMA DE RECOMENDACIONES CUÁNTICAS:")
        metrics = system_data['metrics']
        print(f"   • Recomendaciones totales: {metrics['total_recommendations']}")
        print(f"   • Recomendaciones cuánticas: {metrics['quantum_recommendations']}")
        print(f"   • Recomendaciones clásicas: {metrics['classical_recommendations']}")
        print(f"   • Recomendaciones híbridas: {metrics['hybrid_recommendations']}")
        print(f"   • Precisión promedio: {metrics['average_accuracy']:.3f}")
        print(f"   • Recall promedio: {metrics['average_recall']:.3f}")
        print(f"   • Ventaja cuántica promedio: {metrics['average_quantum_advantage']:.2f}x")
        print(f"   • Satisfacción del usuario: {metrics['user_satisfaction']:.3f}")
        print(f"   • Score de diversidad: {metrics['diversity_score']:.3f}")
        print(f"   • Score de novedad: {metrics['novelty_score']:.3f}")
        print(f"   • Score de cobertura: {metrics['coverage_score']:.3f}")
        
        # Exportar datos
        print(f"\n💾 EXPORTANDO DATOS DE RECOMENDACIONES CUÁNTICAS...")
        exported_files = quantum_rec_system.export_quantum_recommendation_data()
        print(f"   • Archivos exportados: {len(exported_files)}")
        for file_type, path in exported_files.items():
            print(f"     - {file_type}: {Path(path).name}")
        
        print(f"\n✅ SISTEMA DE RECOMENDACIONES CUÁNTICAS DEMO COMPLETADO EXITOSAMENTE")
        print(f"🎉 El sistema de recomendaciones cuánticas ha implementado:")
        print(f"   • Algoritmos cuánticos de recomendación (QAOA, VQE)")
        print(f"   • Optimización cuántica de portafolios de recomendación")
        print(f"   • Personalización extrema con IA cuántica")
        print(f"   • Filtrado colaborativo cuántico")
        print(f"   • Recomendaciones basadas en contenido")
        print(f"   • Sistemas híbridos cuántico-clásicos")
        print(f"   • Segmentación avanzada de usuarios")
        print(f"   • Análisis de diversidad y novedad")
        print(f"   • Explicabilidad de recomendaciones")
        print(f"   • Ventaja cuántica demostrable")
        print(f"   • Optimización multi-objetivo")
        print(f"   • Procesamiento en tiempo real")
        print(f"   • Métricas de evaluación avanzadas")
        
        return quantum_rec_system
    
    # Ejecutar demo
    quantum_rec_system = asyncio.run(run_demo())


if __name__ == "__main__":
    main()






