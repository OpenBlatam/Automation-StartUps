"""
Motor de Recomendaciones con IA Avanzada
Sistema de recomendaciones inteligente con ML, deep learning y técnicas avanzadas
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dense, Dropout, Concatenate
from tensorflow.keras.optimizers import Adam
import lightfm
from lightfm import LightFM
from lightfm.evaluation import precision_at_k, recall_at_k
import surprise
from surprise import SVD, NMF, KNNBasic, KNNWithMeans
from surprise.model_selection import cross_validate
import networkx as nx
from scipy.sparse import csr_matrix
import joblib

class RecommendationType(Enum):
    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    DEEP_LEARNING = "deep_learning"
    MATRIX_FACTORIZATION = "matrix_factorization"
    GRAPH_BASED = "graph_based"
    CONTEXTUAL = "contextual"
    REAL_TIME = "real_time"

class RecommendationAlgorithm(Enum):
    USER_BASED_CF = "user_based_cf"
    ITEM_BASED_CF = "item_based_cf"
    SVD = "svd"
    NMF = "nmf"
    LIGHTFM = "lightfm"
    NEURAL_CF = "neural_cf"
    DEEP_FM = "deep_fm"
    GRAPH_CONV = "graph_conv"
    BERT_BASED = "bert_based"
    TRANSFORMER = "transformer"

@dataclass
class RecommendationRequest:
    user_id: str
    item_type: str
    context: Dict[str, Any]
    num_recommendations: int = 10
    algorithm: RecommendationAlgorithm = RecommendationAlgorithm.SVD
    filters: Dict[str, Any] = None
    diversity: float = 0.5
    novelty: float = 0.3

@dataclass
class RecommendationResult:
    item_id: str
    score: float
    confidence: float
    explanation: str
    metadata: Dict[str, Any]

class AdvancedAIRecommendationEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.user_profiles = {}
        self.item_features = {}
        self.interaction_matrix = None
        self.recommendation_history = {}
        self.performance_metrics = {}
        
        # Configuración por defecto
        self.default_config = {
            "min_interactions": 5,
            "max_recommendations": 100,
            "diversity_threshold": 0.5,
            "novelty_threshold": 0.3,
            "confidence_threshold": 0.7,
            "model_retrain_interval": 86400,  # 24 horas
            "feature_dimension": 50,
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100
        }
        
    async def initialize(self) -> None:
        """Inicializar motor de recomendaciones"""
        try:
            # Inicializar modelos base
            await self._initialize_base_models()
            
            # Cargar datos existentes
            await self._load_existing_data()
            
            self.logger.info("AI Recommendation Engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing recommendation engine: {e}")
            raise
    
    async def _initialize_base_models(self) -> None:
        """Inicializar modelos base"""
        try:
            # Modelo SVD
            self.models["svd"] = SVD(n_factors=50, n_epochs=20, lr_all=0.005, reg_all=0.02)
            
            # Modelo NMF
            self.models["nmf"] = NMF(n_factors=50, n_epochs=20, lr_bu=0.005, lr_bi=0.005, reg_bu=0.02, reg_bi=0.02)
            
            # Modelo LightFM
            self.models["lightfm"] = LightFM(no_components=50, learning_rate=0.05, loss='warp')
            
            # Modelo KNN
            self.models["knn"] = KNNWithMeans(k=50, sim_options={'name': 'cosine', 'user_based': True})
            
            # Modelo Neural Collaborative Filtering
            await self._initialize_neural_cf_model()
            
            # Modelo Deep FM
            await self._initialize_deep_fm_model()
            
        except Exception as e:
            self.logger.error(f"Error initializing base models: {e}")
            raise
    
    async def _initialize_neural_cf_model(self) -> None:
        """Inicializar modelo Neural Collaborative Filtering"""
        try:
            # Crear modelo Neural CF
            user_input = Input(shape=(1,), name='user_input')
            item_input = Input(shape=(1,), name='item_input')
            
            # Embeddings
            user_embedding = Embedding(10000, 50)(user_input)
            item_embedding = Embedding(10000, 50)(item_input)
            
            # Flatten
            user_flat = tf.keras.layers.Flatten()(user_embedding)
            item_flat = tf.keras.layers.Flatten()(item_embedding)
            
            # Concatenate
            concat = Concatenate()([user_flat, item_flat])
            
            # Dense layers
            dense1 = Dense(128, activation='relu')(concat)
            dropout1 = Dropout(0.2)(dense1)
            dense2 = Dense(64, activation='relu')(dropout1)
            dropout2 = Dropout(0.2)(dense2)
            output = Dense(1, activation='sigmoid')(dropout2)
            
            # Compile model
            model = Model(inputs=[user_input, item_input], outputs=output)
            model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
            
            self.models["neural_cf"] = model
            
        except Exception as e:
            self.logger.error(f"Error initializing Neural CF model: {e}")
            raise
    
    async def _initialize_deep_fm_model(self) -> None:
        """Inicializar modelo Deep FM"""
        try:
            # Crear modelo Deep FM
            user_input = Input(shape=(1,), name='user_input')
            item_input = Input(shape=(1,), name='item_input')
            
            # Embeddings
            user_embedding = Embedding(10000, 50)(user_input)
            item_embedding = Embedding(10000, 50)(item_input)
            
            # Flatten
            user_flat = tf.keras.layers.Flatten()(user_embedding)
            item_flat = tf.keras.layers.Flatten()(item_embedding)
            
            # FM component
            fm_concat = Concatenate()([user_flat, item_flat])
            fm_dense = Dense(1, activation='linear')(fm_concat)
            
            # Deep component
            deep_concat = Concatenate()([user_flat, item_flat])
            deep_dense1 = Dense(128, activation='relu')(deep_concat)
            deep_dropout1 = Dropout(0.2)(deep_dense1)
            deep_dense2 = Dense(64, activation='relu')(deep_dropout1)
            deep_dropout2 = Dropout(0.2)(deep_dense2)
            deep_output = Dense(1, activation='sigmoid')(deep_dropout2)
            
            # Combine FM and Deep
            combined = tf.keras.layers.Add()([fm_dense, deep_output])
            output = Dense(1, activation='sigmoid')(combined)
            
            # Compile model
            model = Model(inputs=[user_input, item_input], outputs=output)
            model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
            
            self.models["deep_fm"] = model
            
        except Exception as e:
            self.logger.error(f"Error initializing Deep FM model: {e}")
            raise
    
    async def _load_existing_data(self) -> None:
        """Cargar datos existentes"""
        try:
            # Simular carga de datos
            self.user_profiles = {}
            self.item_features = {}
            self.interaction_matrix = None
            
            # Crear datos de ejemplo
            await self._create_sample_data()
            
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
            raise
    
    async def _create_sample_data(self) -> None:
        """Crear datos de muestra"""
        try:
            # Crear perfiles de usuario
            np.random.seed(42)
            n_users = 1000
            n_items = 500
            
            # Perfiles de usuario
            for i in range(n_users):
                self.user_profiles[f"user_{i}"] = {
                    "age": np.random.randint(18, 65),
                    "gender": np.random.choice(["M", "F"]),
                    "preferences": np.random.choice(["tech", "fashion", "sports", "books", "music"], 3),
                    "location": np.random.choice(["US", "EU", "AS", "LA"]),
                    "activity_level": np.random.choice(["low", "medium", "high"])
                }
            
            # Características de items
            for i in range(n_items):
                self.item_features[f"item_{i}"] = {
                    "category": np.random.choice(["tech", "fashion", "sports", "books", "music"]),
                    "price": np.random.uniform(10, 1000),
                    "rating": np.random.uniform(1, 5),
                    "popularity": np.random.uniform(0, 1),
                    "tags": np.random.choice(["new", "trending", "sale", "premium"], 2)
                }
            
            # Matriz de interacciones
            interactions = []
            for user_id in self.user_profiles.keys():
                user_interactions = np.random.choice(
                    list(self.item_features.keys()),
                    size=np.random.randint(5, 50),
                    replace=False
                )
                for item_id in user_interactions:
                    rating = np.random.uniform(1, 5)
                    interactions.append((user_id, item_id, rating))
            
            self.interaction_matrix = pd.DataFrame(interactions, columns=['user_id', 'item_id', 'rating'])
            
        except Exception as e:
            self.logger.error(f"Error creating sample data: {e}")
            raise
    
    async def train_models(self, algorithm: RecommendationAlgorithm = None) -> Dict[str, Any]:
        """Entrenar modelos de recomendación"""
        try:
            training_results = {}
            
            if algorithm is None:
                # Entrenar todos los modelos
                algorithms = [RecommendationAlgorithm.SVD, RecommendationAlgorithm.NMF, 
                            RecommendationAlgorithm.LIGHTFM, RecommendationAlgorithm.NEURAL_CF]
            else:
                algorithms = [algorithm]
            
            for alg in algorithms:
                try:
                    if alg == RecommendationAlgorithm.SVD:
                        result = await self._train_svd_model()
                    elif alg == RecommendationAlgorithm.NMF:
                        result = await self._train_nmf_model()
                    elif alg == RecommendationAlgorithm.LIGHTFM:
                        result = await self._train_lightfm_model()
                    elif alg == RecommendationAlgorithm.NEURAL_CF:
                        result = await self._train_neural_cf_model()
                    elif alg == RecommendationAlgorithm.DEEP_FM:
                        result = await self._train_deep_fm_model()
                    
                    training_results[alg.value] = result
                    
                except Exception as e:
                    self.logger.error(f"Error training {alg.value}: {e}")
                    training_results[alg.value] = {"error": str(e)}
            
            return training_results
            
        except Exception as e:
            self.logger.error(f"Error training models: {e}")
            raise
    
    async def _train_svd_model(self) -> Dict[str, Any]:
        """Entrenar modelo SVD"""
        try:
            # Preparar datos para Surprise
            from surprise import Dataset, Reader
            
            reader = Reader(rating_scale=(1, 5))
            data = Dataset.load_from_df(self.interaction_matrix, reader)
            
            # Entrenar modelo
            trainset = data.build_full_trainset()
            self.models["svd"].fit(trainset)
            
            # Evaluar modelo
            cv_results = cross_validate(self.models["svd"], data, measures=['RMSE', 'MAE'], cv=5, verbose=False)
            
            return {
                "model": "SVD",
                "rmse": cv_results['test_rmse'].mean(),
                "mae": cv_results['test_mae'].mean(),
                "fit_time": cv_results['fit_time'].mean(),
                "test_time": cv_results['test_time'].mean()
            }
            
        except Exception as e:
            self.logger.error(f"Error training SVD model: {e}")
            raise
    
    async def _train_nmf_model(self) -> Dict[str, Any]:
        """Entrenar modelo NMF"""
        try:
            # Preparar datos para Surprise
            from surprise import Dataset, Reader
            
            reader = Reader(rating_scale=(1, 5))
            data = Dataset.load_from_df(self.interaction_matrix, reader)
            
            # Entrenar modelo
            trainset = data.build_full_trainset()
            self.models["nmf"].fit(trainset)
            
            # Evaluar modelo
            cv_results = cross_validate(self.models["nmf"], data, measures=['RMSE', 'MAE'], cv=5, verbose=False)
            
            return {
                "model": "NMF",
                "rmse": cv_results['test_rmse'].mean(),
                "mae": cv_results['test_mae'].mean(),
                "fit_time": cv_results['fit_time'].mean(),
                "test_time": cv_results['test_time'].mean()
            }
            
        except Exception as e:
            self.logger.error(f"Error training NMF model: {e}")
            raise
    
    async def _train_lightfm_model(self) -> Dict[str, Any]:
        """Entrenar modelo LightFM"""
        try:
            # Preparar datos para LightFM
            user_ids = self.interaction_matrix['user_id'].unique()
            item_ids = self.interaction_matrix['item_id'].unique()
            
            user_id_map = {uid: i for i, uid in enumerate(user_ids)}
            item_id_map = {iid: i for i, iid in enumerate(item_ids)}
            
            # Crear matriz de interacciones
            interactions = []
            for _, row in self.interaction_matrix.iterrows():
                user_idx = user_id_map[row['user_id']]
                item_idx = item_id_map[row['item_id']]
                interactions.append((user_idx, item_idx, row['rating']))
            
            # Crear matriz sparse
            interaction_matrix = csr_matrix(([r for _, _, r in interactions], 
                                           ([u for u, _, _ in interactions], [i for _, i, _ in interactions])),
                                          shape=(len(user_ids), len(item_ids)))
            
            # Entrenar modelo
            self.models["lightfm"].fit(interaction_matrix, epochs=20, num_threads=4)
            
            # Evaluar modelo
            precision = precision_at_k(self.models["lightfm"], interaction_matrix, k=10).mean()
            recall = recall_at_k(self.models["lightfm"], interaction_matrix, k=10).mean()
            
            return {
                "model": "LightFM",
                "precision_at_k": precision,
                "recall_at_k": recall,
                "users": len(user_ids),
                "items": len(item_ids)
            }
            
        except Exception as e:
            self.logger.error(f"Error training LightFM model: {e}")
            raise
    
    async def _train_neural_cf_model(self) -> Dict[str, Any]:
        """Entrenar modelo Neural CF"""
        try:
            # Preparar datos
            user_ids = self.interaction_matrix['user_id'].unique()
            item_ids = self.interaction_matrix['item_id'].unique()
            
            user_id_map = {uid: i for i, uid in enumerate(user_ids)}
            item_id_map = {iid: i for i, iid in enumerate(item_ids)}
            
            # Crear datos de entrenamiento
            X_user = []
            X_item = []
            y = []
            
            for _, row in self.interaction_matrix.iterrows():
                X_user.append(user_id_map[row['user_id']])
                X_item.append(item_id_map[row['item_id']])
                y.append(1 if row['rating'] >= 4 else 0)
            
            X_user = np.array(X_user)
            X_item = np.array(X_item)
            y = np.array(y)
            
            # Entrenar modelo
            history = self.models["neural_cf"].fit(
                [X_user, X_item], y,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
            
            return {
                "model": "Neural CF",
                "final_loss": history.history['loss'][-1],
                "final_accuracy": history.history['accuracy'][-1],
                "val_loss": history.history['val_loss'][-1],
                "val_accuracy": history.history['val_accuracy'][-1]
            }
            
        except Exception as e:
            self.logger.error(f"Error training Neural CF model: {e}")
            raise
    
    async def _train_deep_fm_model(self) -> Dict[str, Any]:
        """Entrenar modelo Deep FM"""
        try:
            # Preparar datos
            user_ids = self.interaction_matrix['user_id'].unique()
            item_ids = self.interaction_matrix['item_id'].unique()
            
            user_id_map = {uid: i for i, uid in enumerate(user_ids)}
            item_id_map = {iid: i for i, iid in enumerate(item_ids)}
            
            # Crear datos de entrenamiento
            X_user = []
            X_item = []
            y = []
            
            for _, row in self.interaction_matrix.iterrows():
                X_user.append(user_id_map[row['user_id']])
                X_item.append(item_id_map[row['item_id']])
                y.append(1 if row['rating'] >= 4 else 0)
            
            X_user = np.array(X_user)
            X_item = np.array(X_item)
            y = np.array(y)
            
            # Entrenar modelo
            history = self.models["deep_fm"].fit(
                [X_user, X_item], y,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
            
            return {
                "model": "Deep FM",
                "final_loss": history.history['loss'][-1],
                "final_accuracy": history.history['accuracy'][-1],
                "val_loss": history.history['val_loss'][-1],
                "val_accuracy": history.history['val_accuracy'][-1]
            }
            
        except Exception as e:
            self.logger.error(f"Error training Deep FM model: {e}")
            raise
    
    async def get_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """Obtener recomendaciones"""
        try:
            # Validar usuario
            if request.user_id not in self.user_profiles:
                raise ValueError(f"User {request.user_id} not found")
            
            # Obtener recomendaciones según algoritmo
            if request.algorithm == RecommendationAlgorithm.SVD:
                recommendations = await self._get_svd_recommendations(request)
            elif request.algorithm == RecommendationAlgorithm.NMF:
                recommendations = await self._get_nmf_recommendations(request)
            elif request.algorithm == RecommendationAlgorithm.LIGHTFM:
                recommendations = await self._get_lightfm_recommendations(request)
            elif request.algorithm == RecommendationAlgorithm.NEURAL_CF:
                recommendations = await self._get_neural_cf_recommendations(request)
            elif request.algorithm == RecommendationAlgorithm.DEEP_FM:
                recommendations = await self._get_deep_fm_recommendations(request)
            else:
                # Algoritmo híbrido por defecto
                recommendations = await self._get_hybrid_recommendations(request)
            
            # Aplicar filtros
            if request.filters:
                recommendations = await self._apply_filters(recommendations, request.filters)
            
            # Aplicar diversidad
            if request.diversity > 0:
                recommendations = await self._apply_diversity(recommendations, request.diversity)
            
            # Aplicar novedad
            if request.novelty > 0:
                recommendations = await self._apply_novelty(recommendations, request.novelty)
            
            # Limitar número de recomendaciones
            recommendations = recommendations[:request.num_recommendations]
            
            # Guardar en historial
            self.recommendation_history[request.user_id] = {
                "timestamp": datetime.now().isoformat(),
                "recommendations": [r.item_id for r in recommendations],
                "algorithm": request.algorithm.value
            }
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            raise
    
    async def _get_svd_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """Obtener recomendaciones con SVD"""
        try:
            recommendations = []
            
            # Obtener items no interactuados
            user_interactions = set(self.interaction_matrix[self.interaction_matrix['user_id'] == request.user_id]['item_id'])
            all_items = set(self.item_features.keys())
            candidate_items = all_items - user_interactions
            
            # Predecir ratings
            for item_id in candidate_items:
                try:
                    predicted_rating = self.models["svd"].predict(request.user_id, item_id).est
                    confidence = min(predicted_rating / 5.0, 1.0)
                    
                    recommendation = RecommendationResult(
                        item_id=item_id,
                        score=predicted_rating,
                        confidence=confidence,
                        explanation=f"Based on similar users who liked {item_id}",
                        metadata=self.item_features.get(item_id, {})
                    )
                    recommendations.append(recommendation)
                    
                except Exception as e:
                    continue
            
            # Ordenar por score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting SVD recommendations: {e}")
            raise
    
    async def _get_nmf_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """Obtener recomendaciones con NMF"""
        try:
            recommendations = []
            
            # Obtener items no interactuados
            user_interactions = set(self.interaction_matrix[self.interaction_matrix['user_id'] == request.user_id]['item_id'])
            all_items = set(self.item_features.keys())
            candidate_items = all_items - user_interactions
            
            # Predecir ratings
            for item_id in candidate_items:
                try:
                    predicted_rating = self.models["nmf"].predict(request.user_id, item_id).est
                    confidence = min(predicted_rating / 5.0, 1.0)
                    
                    recommendation = RecommendationResult(
                        item_id=item_id,
                        score=predicted_rating,
                        confidence=confidence,
                        explanation=f"Based on item features and user preferences",
                        metadata=self.item_features.get(item_id, {})
                    )
                    recommendations.append(recommendation)
                    
                except Exception as e:
                    continue
            
            # Ordenar por score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting NMF recommendations: {e}")
            raise
    
    async def _get_lightfm_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """Obtener recomendaciones con LightFM"""
        try:
            recommendations = []
            
            # Obtener items no interactuados
            user_interactions = set(self.interaction_matrix[self.interaction_matrix['user_id'] == request.user_id]['item_id'])
            all_items = set(self.item_features.keys())
            candidate_items = all_items - user_interactions
            
            # Predecir scores
            user_ids = list(self.interaction_matrix['user_id'].unique())
            item_ids = list(self.interaction_matrix['item_id'].unique())
            
            user_id_map = {uid: i for i, uid in enumerate(user_ids)}
            item_id_map = {iid: i for i, iid in enumerate(item_ids)}
            
            user_idx = user_id_map.get(request.user_id)
            if user_idx is not None:
                for item_id in candidate_items:
                    item_idx = item_id_map.get(item_id)
                    if item_idx is not None:
                        score = self.models["lightfm"].predict(user_idx, item_idx)
                        confidence = min(score / 5.0, 1.0)
                        
                        recommendation = RecommendationResult(
                            item_id=item_id,
                            score=score,
                            confidence=confidence,
                            explanation=f"Based on user-item interactions and features",
                            metadata=self.item_features.get(item_id, {})
                        )
                        recommendations.append(recommendation)
            
            # Ordenar por score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting LightFM recommendations: {e}")
            raise
    
    async def _get_neural_cf_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """Obtener recomendaciones con Neural CF"""
        try:
            recommendations = []
            
            # Obtener items no interactuados
            user_interactions = set(self.interaction_matrix[self.interaction_matrix['user_id'] == request.user_id]['item_id'])
            all_items = set(self.item_features.keys())
            candidate_items = all_items - user_interactions
            
            # Predecir scores
            user_ids = list(self.interaction_matrix['user_id'].unique())
            item_ids = list(self.interaction_matrix['item_id'].unique())
            
            user_id_map = {uid: i for i, uid in enumerate(user_ids)}
            item_id_map = {iid: i for i, iid in enumerate(item_ids)}
            
            user_idx = user_id_map.get(request.user_id)
            if user_idx is not None:
                for item_id in candidate_items:
                    item_idx = item_id_map.get(item_id)
                    if item_idx is not None:
                        score = self.models["neural_cf"].predict([np.array([user_idx]), np.array([item_idx])])[0][0]
                        confidence = score
                        
                        recommendation = RecommendationResult(
                            item_id=item_id,
                            score=score * 5,  # Escalar a 1-5
                            confidence=confidence,
                            explanation=f"Based on neural collaborative filtering",
                            metadata=self.item_features.get(item_id, {})
                        )
                        recommendations.append(recommendation)
            
            # Ordenar por score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting Neural CF recommendations: {e}")
            raise
    
    async def _get_deep_fm_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """Obtener recomendaciones con Deep FM"""
        try:
            recommendations = []
            
            # Obtener items no interactuados
            user_interactions = set(self.interaction_matrix[self.interaction_matrix['user_id'] == request.user_id]['item_id'])
            all_items = set(self.item_features.keys())
            candidate_items = all_items - user_interactions
            
            # Predecir scores
            user_ids = list(self.interaction_matrix['user_id'].unique())
            item_ids = list(self.interaction_matrix['item_id'].unique())
            
            user_id_map = {uid: i for i, uid in enumerate(user_ids)}
            item_id_map = {iid: i for i, iid in enumerate(item_ids)}
            
            user_idx = user_id_map.get(request.user_id)
            if user_idx is not None:
                for item_id in candidate_items:
                    item_idx = item_id_map.get(item_id)
                    if item_idx is not None:
                        score = self.models["deep_fm"].predict([np.array([user_idx]), np.array([item_idx])])[0][0]
                        confidence = score
                        
                        recommendation = RecommendationResult(
                            item_id=item_id,
                            score=score * 5,  # Escalar a 1-5
                            confidence=confidence,
                            explanation=f"Based on Deep FM model",
                            metadata=self.item_features.get(item_id, {})
                        )
                        recommendations.append(recommendation)
            
            # Ordenar por score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting Deep FM recommendations: {e}")
            raise
    
    async def _get_hybrid_recommendations(self, request: RecommendationRequest) -> List[RecommendationResult]:
        """Obtener recomendaciones híbridas"""
        try:
            # Obtener recomendaciones de múltiples algoritmos
            svd_recs = await self._get_svd_recommendations(request)
            nmf_recs = await self._get_nmf_recommendations(request)
            
            # Combinar recomendaciones
            combined_scores = {}
            for rec in svd_recs:
                combined_scores[rec.item_id] = combined_scores.get(rec.item_id, 0) + rec.score * 0.5
            
            for rec in nmf_recs:
                combined_scores[rec.item_id] = combined_scores.get(rec.item_id, 0) + rec.score * 0.5
            
            # Crear recomendaciones combinadas
            recommendations = []
            for item_id, score in combined_scores.items():
                recommendation = RecommendationResult(
                    item_id=item_id,
                    score=score,
                    confidence=min(score / 5.0, 1.0),
                    explanation="Hybrid recommendation combining multiple algorithms",
                    metadata=self.item_features.get(item_id, {})
                )
                recommendations.append(recommendation)
            
            # Ordenar por score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting hybrid recommendations: {e}")
            raise
    
    async def _apply_filters(self, recommendations: List[RecommendationResult], 
                           filters: Dict[str, Any]) -> List[RecommendationResult]:
        """Aplicar filtros a las recomendaciones"""
        try:
            filtered_recommendations = []
            
            for rec in recommendations:
                include = True
                
                # Filtro por categoría
                if "category" in filters:
                    if rec.metadata.get("category") != filters["category"]:
                        include = False
                
                # Filtro por precio
                if "max_price" in filters:
                    if rec.metadata.get("price", 0) > filters["max_price"]:
                        include = False
                
                # Filtro por rating mínimo
                if "min_rating" in filters:
                    if rec.metadata.get("rating", 0) < filters["min_rating"]:
                        include = False
                
                if include:
                    filtered_recommendations.append(rec)
            
            return filtered_recommendations
            
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
            return recommendations
    
    async def _apply_diversity(self, recommendations: List[RecommendationResult], 
                             diversity: float) -> List[RecommendationResult]:
        """Aplicar diversidad a las recomendaciones"""
        try:
            if diversity <= 0:
                return recommendations
            
            diverse_recommendations = []
            used_categories = set()
            
            for rec in recommendations:
                category = rec.metadata.get("category", "unknown")
                
                # Si la categoría no está usada o la diversidad es baja, incluir
                if category not in used_categories or np.random.random() > diversity:
                    diverse_recommendations.append(rec)
                    used_categories.add(category)
            
            return diverse_recommendations
            
        except Exception as e:
            self.logger.error(f"Error applying diversity: {e}")
            return recommendations
    
    async def _apply_novelty(self, recommendations: List[RecommendationResult], 
                           novelty: float) -> List[RecommendationResult]:
        """Aplicar novedad a las recomendaciones"""
        try:
            if novelty <= 0:
                return recommendations
            
            novel_recommendations = []
            
            for rec in recommendations:
                # Items con baja popularidad son más novedosos
                popularity = rec.metadata.get("popularity", 0.5)
                novelty_score = 1 - popularity
                
                # Si el item es novedoso o la novedad es baja, incluir
                if novelty_score > novelty or np.random.random() > novelty:
                    novel_recommendations.append(rec)
            
            return novel_recommendations
            
        except Exception as e:
            self.logger.error(f"Error applying novelty: {e}")
            return recommendations
    
    async def get_recommendation_insights(self) -> Dict[str, Any]:
        """Obtener insights de recomendaciones"""
        insights = {
            "total_users": len(self.user_profiles),
            "total_items": len(self.item_features),
            "total_interactions": len(self.interaction_matrix),
            "models_trained": len(self.models),
            "recommendation_history": len(self.recommendation_history),
            "average_recommendations_per_user": 0,
            "most_popular_items": [],
            "algorithm_usage": {}
        }
        
        if self.recommendation_history:
            # Promedio de recomendaciones por usuario
            total_recs = sum(len(hist["recommendations"]) for hist in self.recommendation_history.values())
            insights["average_recommendations_per_user"] = total_recs / len(self.recommendation_history)
            
            # Uso de algoritmos
            for hist in self.recommendation_history.values():
                algorithm = hist["algorithm"]
                insights["algorithm_usage"][algorithm] = insights["algorithm_usage"].get(algorithm, 0) + 1
        
        # Items más populares
        if self.interaction_matrix is not None:
            item_counts = self.interaction_matrix['item_id'].value_counts()
            insights["most_popular_items"] = item_counts.head(10).to_dict()
        
        return insights

# Función principal para inicializar el motor
async def initialize_ai_recommendation_engine() -> AdvancedAIRecommendationEngine:
    """Inicializar motor de recomendaciones con IA"""
    engine = AdvancedAIRecommendationEngine()
    await engine.initialize()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    return engine

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        engine = await initialize_ai_recommendation_engine()
        
        # Entrenar modelos
        training_results = await engine.train_models()
        print("Training Results:", json.dumps(training_results, indent=2, default=str))
        
        # Crear solicitud de recomendación
        request = RecommendationRequest(
            user_id="user_0",
            item_type="product",
            context={"session_id": "session_123"},
            num_recommendations=10,
            algorithm=RecommendationAlgorithm.SVD,
            filters={"max_price": 500},
            diversity=0.3,
            novelty=0.2
        )
        
        # Obtener recomendaciones
        recommendations = await engine.get_recommendations(request)
        print("Recommendations:", json.dumps([{
            "item_id": r.item_id,
            "score": r.score,
            "confidence": r.confidence,
            "explanation": r.explanation
        } for r in recommendations], indent=2, default=str))
        
        # Obtener insights
        insights = await engine.get_recommendation_insights()
        print("Recommendation Insights:", json.dumps(insights, indent=2, default=str))
    
    asyncio.run(main())



