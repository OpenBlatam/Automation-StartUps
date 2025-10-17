"""
Motor de Detección de Anomalías Avanzado
Sistema de detección de anomalías con ML, deep learning y técnicas avanzadas
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
import warnings
warnings.filterwarnings('ignore')

# Machine learning libraries
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN, KMeans
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope

# Deep learning libraries
import tensorflow as tf
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Dense, LSTM, GRU, Conv1D, MaxPooling1D, Flatten, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Time series anomaly detection
from scipy import stats
from scipy.signal import find_peaks
import ruptures as rpt

# Statistical methods
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.stats.diagnostic import acorr_ljungbox

class AnomalyType(Enum):
    POINT = "point"
    CONTEXTUAL = "contextual"
    COLLECTIVE = "collective"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    DEEP_LEARNING = "deep_learning"

class DetectionAlgorithm(Enum):
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    DBSCAN = "dbscan"
    ELLIPTIC_ENVELOPE = "elliptic_envelope"
    Z_SCORE = "z_score"
    IQR = "iqr"
    MAHALANOBIS = "mahalanobis"
    AUTOENCODER = "autoencoder"
    LSTM_ANOMALY = "lstm_anomaly"
    VAE = "vae"
    GAN = "gan"
    CHANGEPOINT = "changepoint"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"

@dataclass
class AnomalyDetectionRequest:
    data: pd.DataFrame
    target_columns: List[str]
    anomaly_type: AnomalyType
    algorithm: DetectionAlgorithm
    contamination: float = 0.1
    threshold: float = 0.5
    window_size: int = 10
    parameters: Dict[str, Any] = None

@dataclass
class AnomalyResult:
    anomalies: List[Dict[str, Any]]
    anomaly_scores: np.ndarray
    threshold: float
    model_metrics: Dict[str, float]
    model_info: Dict[str, Any]
    feature_importance: Optional[Dict[str, float]]

class AdvancedAnomalyDetectionEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.detection_history = {}
        self.performance_metrics = {}
        
        # Configuración por defecto
        self.default_config = {
            "min_data_points": 30,
            "max_contamination": 0.5,
            "default_threshold": 0.5,
            "window_size": 10,
            "confidence_level": 0.95,
            "early_stopping_patience": 10,
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100
        }
        
    async def detect_anomalies(self, request: AnomalyDetectionRequest) -> AnomalyResult:
        """Detectar anomalías avanzadas"""
        try:
            # Validar datos
            await self._validate_data(request)
            
            # Preparar datos
            processed_data = await self._prepare_data(request)
            
            # Detectar anomalías según algoritmo
            if request.algorithm == DetectionAlgorithm.ISOLATION_FOREST:
                result = await self._detect_with_isolation_forest(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.ONE_CLASS_SVM:
                result = await self._detect_with_one_class_svm(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.LOCAL_OUTLIER_FACTOR:
                result = await self._detect_with_lof(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.DBSCAN:
                result = await self._detect_with_dbscan(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.ELLIPTIC_ENVELOPE:
                result = await self._detect_with_elliptic_envelope(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.Z_SCORE:
                result = await self._detect_with_z_score(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.IQR:
                result = await self._detect_with_iqr(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.MAHALANOBIS:
                result = await self._detect_with_mahalanobis(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.AUTOENCODER:
                result = await self._detect_with_autoencoder(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.LSTM_ANOMALY:
                result = await self._detect_with_lstm_anomaly(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.VAE:
                result = await self._detect_with_vae(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.CHANGEPOINT:
                result = await self._detect_with_changepoint(request, processed_data)
            elif request.algorithm == DetectionAlgorithm.SEASONAL_DECOMPOSITION:
                result = await self._detect_with_seasonal_decomposition(request, processed_data)
            else:
                raise ValueError(f"Unsupported detection algorithm: {request.algorithm}")
            
            # Guardar en historial
            await self._save_detection_history(request, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            raise
    
    async def _validate_data(self, request: AnomalyDetectionRequest) -> None:
        """Validar datos de entrada"""
        try:
            if request.data is None or request.data.empty:
                raise ValueError("Data is empty or None")
            
            for column in request.target_columns:
                if column not in request.data.columns:
                    raise ValueError(f"Target column {column} not found in data")
            
            if len(request.data) < self.default_config["min_data_points"]:
                raise ValueError(f"Insufficient data points. Minimum required: {self.default_config['min_data_points']}")
            
            if request.contamination > self.default_config["max_contamination"]:
                raise ValueError(f"Contamination too high. Maximum allowed: {self.default_config['max_contamination']}")
            
        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            raise
    
    async def _prepare_data(self, request: AnomalyDetectionRequest) -> Dict[str, Any]:
        """Preparar datos para detección de anomalías"""
        try:
            data = request.data.copy()
            
            # Seleccionar columnas objetivo
            target_data = data[request.target_columns]
            
            # Manejar valores faltantes
            target_data = target_data.fillna(method='ffill').fillna(method='bfill')
            
            # Normalizar datos
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(target_data)
            
            # Crear características adicionales
            features = await self._create_anomaly_features(data, request.target_columns)
            
            processed_data = {
                "original_data": data,
                "target_data": target_data,
                "scaled_data": scaled_data,
                "features": features,
                "scaler": scaler
            }
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error preparing data: {e}")
            raise
    
    async def _create_anomaly_features(self, data: pd.DataFrame, target_columns: List[str]) -> pd.DataFrame:
        """Crear características para detección de anomalías"""
        try:
            features = pd.DataFrame()
            
            # Características estadísticas
            for column in target_columns:
                # Media móvil
                features[f'{column}_rolling_mean_7'] = data[column].rolling(window=7).mean()
                features[f'{column}_rolling_mean_30'] = data[column].rolling(window=30).mean()
                
                # Desviación estándar móvil
                features[f'{column}_rolling_std_7'] = data[column].rolling(window=7).std()
                features[f'{column}_rolling_std_30'] = data[column].rolling(window=30).std()
                
                # Valores extremos
                features[f'{column}_rolling_max_7'] = data[column].rolling(window=7).max()
                features[f'{column}_rolling_min_7'] = data[column].rolling(window=7).min()
                
                # Diferencias
                features[f'{column}_diff_1'] = data[column].diff(1)
                features[f'{column}_diff_7'] = data[column].diff(7)
                
                # Z-score móvil
                rolling_mean = data[column].rolling(window=30).mean()
                rolling_std = data[column].rolling(window=30).std()
                features[f'{column}_z_score'] = (data[column] - rolling_mean) / rolling_std
            
            # Características de tiempo si hay columna de fecha
            if 'date' in data.columns or 'timestamp' in data.columns:
                date_col = 'date' if 'date' in data.columns else 'timestamp'
                data[date_col] = pd.to_datetime(data[date_col])
                
                features['hour'] = data[date_col].dt.hour
                features['dayofweek'] = data[date_col].dt.dayofweek
                features['month'] = data[date_col].dt.month
                features['quarter'] = data[date_col].dt.quarter
                
                # Características cíclicas
                features['hour_sin'] = np.sin(2 * np.pi * features['hour'] / 24)
                features['hour_cos'] = np.cos(2 * np.pi * features['hour'] / 24)
                features['dayofweek_sin'] = np.sin(2 * np.pi * features['dayofweek'] / 7)
                features['dayofweek_cos'] = np.cos(2 * np.pi * features['dayofweek'] / 7)
            
            # Eliminar filas con NaN
            features = features.fillna(method='ffill').fillna(method='bfill')
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error creating anomaly features: {e}")
            return pd.DataFrame()
    
    async def _detect_with_isolation_forest(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con Isolation Forest"""
        try:
            scaled_data = processed_data["scaled_data"]
            
            # Crear modelo Isolation Forest
            model = IsolationForest(
                contamination=request.contamination,
                random_state=42,
                n_estimators=request.parameters.get("n_estimators", 100) if request.parameters else 100
            )
            
            # Entrenar modelo
            model.fit(scaled_data)
            
            # Detectar anomalías
            anomaly_scores = model.decision_function(scaled_data)
            anomaly_predictions = model.predict(scaled_data)
            
            # Convertir predicciones (-1 = anomalía, 1 = normal)
            anomaly_mask = anomaly_predictions == -1
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict()
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "contamination": request.contamination,
                "n_estimators": model.n_estimators
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=request.threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Isolation Forest",
                    "contamination": request.contamination,
                    "n_estimators": model.n_estimators
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with Isolation Forest: {e}")
            raise
    
    async def _detect_with_one_class_svm(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con One-Class SVM"""
        try:
            scaled_data = processed_data["scaled_data"]
            
            # Crear modelo One-Class SVM
            model = OneClassSVM(
                nu=request.contamination,
                kernel=request.parameters.get("kernel", "rbf") if request.parameters else "rbf",
                gamma=request.parameters.get("gamma", "scale") if request.parameters else "scale"
            )
            
            # Entrenar modelo
            model.fit(scaled_data)
            
            # Detectar anomalías
            anomaly_scores = model.decision_function(scaled_data)
            anomaly_predictions = model.predict(scaled_data)
            
            # Convertir predicciones (-1 = anomalía, 1 = normal)
            anomaly_mask = anomaly_predictions == -1
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict()
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "nu": request.contamination,
                "kernel": model.kernel
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=request.threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "One-Class SVM",
                    "nu": request.contamination,
                    "kernel": model.kernel,
                    "gamma": model.gamma
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with One-Class SVM: {e}")
            raise
    
    async def _detect_with_lof(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con Local Outlier Factor"""
        try:
            scaled_data = processed_data["scaled_data"]
            
            # Crear modelo LOF
            model = LocalOutlierFactor(
                n_neighbors=request.parameters.get("n_neighbors", 20) if request.parameters else 20,
                contamination=request.contamination
            )
            
            # Detectar anomalías
            anomaly_predictions = model.fit_predict(scaled_data)
            anomaly_scores = model.negative_outlier_factor_
            
            # Convertir predicciones (-1 = anomalía, 1 = normal)
            anomaly_mask = anomaly_predictions == -1
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict()
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "n_neighbors": model.n_neighbors,
                "contamination": request.contamination
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=request.threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Local Outlier Factor",
                    "n_neighbors": model.n_neighbors,
                    "contamination": request.contamination
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with LOF: {e}")
            raise
    
    async def _detect_with_dbscan(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con DBSCAN"""
        try:
            scaled_data = processed_data["scaled_data"]
            
            # Crear modelo DBSCAN
            model = DBSCAN(
                eps=request.parameters.get("eps", 0.5) if request.parameters else 0.5,
                min_samples=request.parameters.get("min_samples", 5) if request.parameters else 5
            )
            
            # Detectar anomalías
            cluster_labels = model.fit_predict(scaled_data)
            
            # Anomalías son puntos con label -1
            anomaly_mask = cluster_labels == -1
            
            # Crear scores basados en distancia al centroide más cercano
            anomaly_scores = np.zeros(len(scaled_data))
            for i, label in enumerate(cluster_labels):
                if label == -1:
                    # Calcular distancia al centroide más cercano
                    distances = []
                    for cluster_id in set(cluster_labels):
                        if cluster_id != -1:
                            cluster_points = scaled_data[cluster_labels == cluster_id]
                            if len(cluster_points) > 0:
                                centroid = np.mean(cluster_points, axis=0)
                                distance = np.linalg.norm(scaled_data[i] - centroid)
                                distances.append(distance)
                    anomaly_scores[i] = -min(distances) if distances else -1
                else:
                    anomaly_scores[i] = 1
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict()
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "n_clusters": n_clusters,
                "eps": model.eps,
                "min_samples": model.min_samples
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=request.threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "DBSCAN",
                    "eps": model.eps,
                    "min_samples": model.min_samples,
                    "n_clusters": n_clusters
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with DBSCAN: {e}")
            raise
    
    async def _detect_with_elliptic_envelope(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con Elliptic Envelope"""
        try:
            scaled_data = processed_data["scaled_data"]
            
            # Crear modelo Elliptic Envelope
            model = EllipticEnvelope(
                contamination=request.contamination,
                random_state=42
            )
            
            # Entrenar modelo
            model.fit(scaled_data)
            
            # Detectar anomalías
            anomaly_scores = model.decision_function(scaled_data)
            anomaly_predictions = model.predict(scaled_data)
            
            # Convertir predicciones (-1 = anomalía, 1 = normal)
            anomaly_mask = anomaly_predictions == -1
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict()
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "contamination": request.contamination
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=request.threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Elliptic Envelope",
                    "contamination": request.contamination
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with Elliptic Envelope: {e}")
            raise
    
    async def _detect_with_z_score(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con Z-Score"""
        try:
            target_data = processed_data["target_data"]
            
            # Calcular Z-scores para cada columna
            z_scores = np.abs(stats.zscore(target_data, axis=0))
            
            # Combinar Z-scores (máximo por fila)
            max_z_scores = np.max(z_scores, axis=1)
            
            # Detectar anomalías (Z-score > threshold)
            threshold = request.parameters.get("z_threshold", 3) if request.parameters else 3
            anomaly_mask = max_z_scores > threshold
            
            # Crear scores normalizados
            anomaly_scores = max_z_scores / threshold
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict(),
                        "z_scores": z_scores[i].tolist()
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "z_threshold": threshold,
                "mean_z_score": np.mean(max_z_scores),
                "std_z_score": np.std(max_z_scores)
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Z-Score",
                    "z_threshold": threshold
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with Z-Score: {e}")
            raise
    
    async def _detect_with_iqr(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con IQR"""
        try:
            target_data = processed_data["target_data"]
            
            # Calcular IQR para cada columna
            anomaly_mask = np.zeros(len(target_data), dtype=bool)
            anomaly_scores = np.zeros(len(target_data))
            
            for column in target_data.columns:
                Q1 = target_data[column].quantile(0.25)
                Q3 = target_data[column].quantile(0.75)
                IQR = Q3 - Q1
                
                # Calcular límites
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Detectar anomalías
                column_anomalies = (target_data[column] < lower_bound) | (target_data[column] > upper_bound)
                anomaly_mask |= column_anomalies
                
                # Calcular scores
                for i, is_anomaly in enumerate(column_anomalies):
                    if is_anomaly:
                        if target_data[column].iloc[i] < lower_bound:
                            score = (lower_bound - target_data[column].iloc[i]) / IQR
                        else:
                            score = (target_data[column].iloc[i] - upper_bound) / IQR
                        anomaly_scores[i] = max(anomaly_scores[i], score)
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict()
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "iqr_multiplier": 1.5
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=request.threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "IQR",
                    "iqr_multiplier": 1.5
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with IQR: {e}")
            raise
    
    async def _detect_with_mahalanobis(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con distancia de Mahalanobis"""
        try:
            scaled_data = processed_data["scaled_data"]
            
            # Calcular matriz de covarianza
            cov_matrix = np.cov(scaled_data.T)
            
            # Calcular media
            mean = np.mean(scaled_data, axis=0)
            
            # Calcular distancias de Mahalanobis
            mahalanobis_distances = []
            for i in range(len(scaled_data)):
                diff = scaled_data[i] - mean
                distance = np.sqrt(diff.T @ np.linalg.inv(cov_matrix) @ diff)
                mahalanobis_distances.append(distance)
            
            mahalanobis_distances = np.array(mahalanobis_distances)
            
            # Detectar anomalías (percentil 95)
            threshold = np.percentile(mahalanobis_distances, 95)
            anomaly_mask = mahalanobis_distances > threshold
            
            # Crear scores normalizados
            anomaly_scores = mahalanobis_distances / threshold
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict(),
                        "mahalanobis_distance": mahalanobis_distances[i]
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "threshold": threshold,
                "mean_distance": np.mean(mahalanobis_distances),
                "std_distance": np.std(mahalanobis_distances)
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Mahalanobis Distance",
                    "threshold": threshold
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with Mahalanobis: {e}")
            raise
    
    async def _detect_with_autoencoder(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con Autoencoder"""
        try:
            scaled_data = processed_data["scaled_data"]
            
            # Crear modelo Autoencoder
            input_dim = scaled_data.shape[1]
            encoding_dim = request.parameters.get("encoding_dim", input_dim // 2) if request.parameters else input_dim // 2
            
            # Encoder
            encoder = Sequential([
                Dense(encoding_dim * 2, activation='relu', input_shape=(input_dim,)),
                Dropout(0.2),
                Dense(encoding_dim, activation='relu'),
                Dropout(0.2)
            ])
            
            # Decoder
            decoder = Sequential([
                Dense(encoding_dim * 2, activation='relu'),
                Dropout(0.2),
                Dense(input_dim, activation='sigmoid')
            ])
            
            # Autoencoder completo
            autoencoder = Sequential([
                encoder,
                decoder
            ])
            
            autoencoder.compile(optimizer=Adam(learning_rate=request.parameters.get("learning_rate", 0.001) if request.parameters else 0.001),
                              loss='mse')
            
            # Entrenar modelo
            early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
            
            history = autoencoder.fit(
                scaled_data, scaled_data,
                epochs=request.parameters.get("epochs", 100) if request.parameters else 100,
                batch_size=request.parameters.get("batch_size", 32) if request.parameters else 32,
                callbacks=[early_stopping],
                verbose=0
            )
            
            # Reconstruir datos
            reconstructed = autoencoder.predict(scaled_data)
            
            # Calcular error de reconstrucción
            reconstruction_error = np.mean(np.square(scaled_data - reconstructed), axis=1)
            
            # Detectar anomalías (percentil 95)
            threshold = np.percentile(reconstruction_error, 95)
            anomaly_mask = reconstruction_error > threshold
            
            # Crear scores normalizados
            anomaly_scores = reconstruction_error / threshold
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict(),
                        "reconstruction_error": reconstruction_error[i]
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "threshold": threshold,
                "mean_reconstruction_error": np.mean(reconstruction_error),
                "std_reconstruction_error": np.std(reconstruction_error),
                "final_loss": history.history['loss'][-1]
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Autoencoder",
                    "encoding_dim": encoding_dim,
                    "input_dim": input_dim,
                    "epochs_trained": len(history.history['loss'])
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with Autoencoder: {e}")
            raise
    
    async def _detect_with_lstm_anomaly(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con LSTM"""
        try:
            target_data = processed_data["target_data"]
            
            # Preparar datos para LSTM
            sequence_length = request.parameters.get("sequence_length", 10) if request.parameters else 10
            
            # Normalizar datos
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(target_data.values)
            
            # Crear secuencias
            X, y = await self._create_sequences(scaled_data, sequence_length)
            
            # Crear modelo LSTM
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, target_data.shape[1])),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(target_data.shape[1])
            ])
            
            model.compile(optimizer=Adam(learning_rate=request.parameters.get("learning_rate", 0.001) if request.parameters else 0.001),
                         loss='mse')
            
            # Entrenar modelo
            early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
            
            history = model.fit(
                X, y,
                epochs=request.parameters.get("epochs", 100) if request.parameters else 100,
                batch_size=request.parameters.get("batch_size", 32) if request.parameters else 32,
                callbacks=[early_stopping],
                verbose=0
            )
            
            # Predecir en todos los datos
            predictions = model.predict(X)
            
            # Calcular error de predicción
            prediction_error = np.mean(np.square(y - predictions), axis=1)
            
            # Extender errores a toda la serie
            full_errors = np.zeros(len(target_data))
            full_errors[sequence_length:] = prediction_error
            
            # Detectar anomalías (percentil 95)
            threshold = np.percentile(full_errors, 95)
            anomaly_mask = full_errors > threshold
            
            # Crear scores normalizados
            anomaly_scores = full_errors / threshold
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict(),
                        "prediction_error": full_errors[i]
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "threshold": threshold,
                "mean_prediction_error": np.mean(full_errors),
                "std_prediction_error": np.std(full_errors),
                "final_loss": history.history['loss'][-1]
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "LSTM Anomaly Detection",
                    "sequence_length": sequence_length,
                    "epochs_trained": len(history.history['loss'])
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with LSTM: {e}")
            raise
    
    async def _create_sequences(self, data: np.ndarray, sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Crear secuencias para modelos de deep learning"""
        try:
            X, y = [], []
            for i in range(sequence_length, len(data)):
                X.append(data[i-sequence_length:i])
                y.append(data[i])
            return np.array(X), np.array(y)
            
        except Exception as e:
            self.logger.error(f"Error creating sequences: {e}")
            raise
    
    async def _detect_with_vae(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con Variational Autoencoder"""
        try:
            scaled_data = processed_data["scaled_data"]
            
            # Crear modelo VAE
            input_dim = scaled_data.shape[1]
            latent_dim = request.parameters.get("latent_dim", input_dim // 4) if request.parameters else input_dim // 4
            
            # Encoder
            encoder_input = tf.keras.Input(shape=(input_dim,))
            x = Dense(64, activation='relu')(encoder_input)
            x = Dropout(0.2)(x)
            x = Dense(32, activation='relu')(x)
            x = Dropout(0.2)(x)
            
            z_mean = Dense(latent_dim)(x)
            z_log_var = Dense(latent_dim)(x)
            
            # Sampling layer
            def sampling(args):
                z_mean, z_log_var = args
                batch = tf.shape(z_mean)[0]
                dim = tf.shape(z_mean)[1]
                epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
                return z_mean + tf.exp(0.5 * z_log_var) * epsilon
            
            z = tf.keras.layers.Lambda(sampling)([z_mean, z_log_var])
            
            # Decoder
            decoder_input = tf.keras.Input(shape=(latent_dim,))
            x = Dense(32, activation='relu')(decoder_input)
            x = Dropout(0.2)(x)
            x = Dense(64, activation='relu')(x)
            x = Dropout(0.2)(x)
            decoder_output = Dense(input_dim, activation='sigmoid')(x)
            
            # Modelos
            encoder = Model(encoder_input, [z_mean, z_log_var, z])
            decoder = Model(decoder_input, decoder_output)
            
            # VAE completo
            vae_output = decoder(encoder(encoder_input)[2])
            vae = Model(encoder_input, vae_output)
            
            # Función de pérdida VAE
            def vae_loss(x, x_decoded_mean):
                reconstruction_loss = tf.keras.losses.mse(x, x_decoded_mean)
                kl_loss = -0.5 * tf.keras.backend.sum(1 + z_log_var - tf.keras.backend.square(z_mean) - tf.keras.backend.exp(z_log_var), axis=-1)
                return reconstruction_loss + kl_loss
            
            vae.compile(optimizer=Adam(learning_rate=request.parameters.get("learning_rate", 0.001) if request.parameters else 0.001),
                       loss=vae_loss)
            
            # Entrenar modelo
            early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
            
            history = vae.fit(
                scaled_data, scaled_data,
                epochs=request.parameters.get("epochs", 100) if request.parameters else 100,
                batch_size=request.parameters.get("batch_size", 32) if request.parameters else 32,
                callbacks=[early_stopping],
                verbose=0
            )
            
            # Reconstruir datos
            reconstructed = vae.predict(scaled_data)
            
            # Calcular error de reconstrucción
            reconstruction_error = np.mean(np.square(scaled_data - reconstructed), axis=1)
            
            # Detectar anomalías (percentil 95)
            threshold = np.percentile(reconstruction_error, 95)
            anomaly_mask = reconstruction_error > threshold
            
            # Crear scores normalizados
            anomaly_scores = reconstruction_error / threshold
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict(),
                        "reconstruction_error": reconstruction_error[i]
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "threshold": threshold,
                "mean_reconstruction_error": np.mean(reconstruction_error),
                "std_reconstruction_error": np.std(reconstruction_error),
                "final_loss": history.history['loss'][-1]
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Variational Autoencoder",
                    "latent_dim": latent_dim,
                    "input_dim": input_dim,
                    "epochs_trained": len(history.history['loss'])
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with VAE: {e}")
            raise
    
    async def _detect_with_changepoint(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con detección de cambios"""
        try:
            target_data = processed_data["target_data"]
            
            # Detectar cambios para cada columna
            anomaly_mask = np.zeros(len(target_data), dtype=bool)
            anomaly_scores = np.zeros(len(target_data))
            
            for column in target_data.columns:
                # Detectar cambios
                model = rpt.Pelt(model="rbf").fit(target_data[column].values)
                changepoints = model.predict(pen=10)
                
                # Marcar puntos de cambio como anomalías
                for cp in changepoints:
                    if cp < len(target_data):
                        anomaly_mask[cp] = True
                        anomaly_scores[cp] = 1.0
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict(),
                        "type": "changepoint"
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "changepoints_detected": n_anomalies
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=request.threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Changepoint Detection",
                    "model": "rbf",
                    "penalty": 10
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with changepoint: {e}")
            raise
    
    async def _detect_with_seasonal_decomposition(self, request: AnomalyDetectionRequest, processed_data: Dict[str, Any]) -> AnomalyResult:
        """Detectar anomalías con descomposición estacional"""
        try:
            target_data = processed_data["target_data"]
            
            # Detectar anomalías para cada columna
            anomaly_mask = np.zeros(len(target_data), dtype=bool)
            anomaly_scores = np.zeros(len(target_data))
            
            for column in target_data.columns:
                # Descomposición estacional
                decomposition = seasonal_decompose(target_data[column], model='additive', period=request.parameters.get("period", 12) if request.parameters else 12)
                
                # Detectar anomalías en el residuo
                residuals = decomposition.resid.dropna()
                residual_std = residuals.std()
                residual_mean = residuals.mean()
                
                # Z-score del residuo
                z_scores = np.abs((residuals - residual_mean) / residual_std)
                
                # Detectar anomalías (Z-score > 3)
                threshold = request.parameters.get("z_threshold", 3) if request.parameters else 3
                column_anomalies = z_scores > threshold
                
                # Mapear anomalías a índices originales
                for i, is_anomaly in enumerate(column_anomalies):
                    if is_anomaly:
                        original_idx = residuals.index[i]
                        if original_idx < len(anomaly_mask):
                            anomaly_mask[original_idx] = True
                            anomaly_scores[original_idx] = max(anomaly_scores[original_idx], z_scores.iloc[i] / threshold)
            
            # Crear lista de anomalías
            anomalies = []
            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    anomaly_info = {
                        "index": i,
                        "score": anomaly_scores[i],
                        "timestamp": processed_data["original_data"].index[i] if hasattr(processed_data["original_data"], 'index') else i,
                        "values": processed_data["target_data"].iloc[i].to_dict(),
                        "type": "seasonal_anomaly"
                    }
                    anomalies.append(anomaly_info)
            
            # Métricas del modelo
            n_anomalies = np.sum(anomaly_mask)
            n_total = len(anomaly_mask)
            anomaly_rate = n_anomalies / n_total
            
            model_metrics = {
                "anomaly_count": n_anomalies,
                "anomaly_rate": anomaly_rate,
                "z_threshold": threshold
            }
            
            result = AnomalyResult(
                anomalies=anomalies,
                anomaly_scores=anomaly_scores,
                threshold=threshold,
                model_metrics=model_metrics,
                model_info={
                    "algorithm": "Seasonal Decomposition",
                    "model": "additive",
                    "period": request.parameters.get("period", 12) if request.parameters else 12,
                    "z_threshold": threshold
                },
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting with seasonal decomposition: {e}")
            raise
    
    async def _save_detection_history(self, request: AnomalyDetectionRequest, result: AnomalyResult) -> None:
        """Guardar historial de detección"""
        try:
            detection_id = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.detection_history[detection_id] = {
                "timestamp": datetime.now().isoformat(),
                "algorithm": request.algorithm.value,
                "anomaly_type": request.anomaly_type.value,
                "target_columns": request.target_columns,
                "contamination": request.contamination,
                "anomaly_count": len(result.anomalies),
                "model_metrics": result.model_metrics,
                "model_info": result.model_info
            }
            
        except Exception as e:
            self.logger.error(f"Error saving detection history: {e}")
    
    async def get_anomaly_detection_insights(self) -> Dict[str, Any]:
        """Obtener insights de detección de anomalías"""
        insights = {
            "total_detections": len(self.detection_history),
            "algorithms_used": {},
            "anomaly_types_detected": {},
            "average_anomaly_rate": 0.0,
            "most_effective_algorithm": None,
            "recent_detections": []
        }
        
        if self.detection_history:
            # Análisis de algoritmos usados
            for detection in self.detection_history.values():
                algorithm = detection["algorithm"]
                insights["algorithms_used"][algorithm] = insights["algorithms_used"].get(algorithm, 0) + 1
                
                anomaly_type = detection["anomaly_type"]
                insights["anomaly_types_detected"][anomaly_type] = insights["anomaly_types_detected"].get(anomaly_type, 0) + 1
            
            # Promedio de tasa de anomalías
            anomaly_rates = [detection["model_metrics"].get("anomaly_rate", 0) for detection in self.detection_history.values()]
            insights["average_anomaly_rate"] = np.mean(anomaly_rates) if anomaly_rates else 0.0
            
            # Algoritmo más efectivo (basado en tasa de anomalías)
            algorithm_rates = {}
            for detection in self.detection_history.values():
                algorithm = detection["algorithm"]
                rate = detection["model_metrics"].get("anomaly_rate", 0)
                
                if algorithm not in algorithm_rates:
                    algorithm_rates[algorithm] = []
                algorithm_rates[algorithm].append(rate)
            
            if algorithm_rates:
                # Algoritmo con tasa de anomalías más consistente
                best_algorithm = min(algorithm_rates, key=lambda x: np.std(algorithm_rates[x]))
                insights["most_effective_algorithm"] = best_algorithm
            
            # Detecciones recientes
            recent_detections = sorted(self.detection_history.items(), key=lambda x: x[1]["timestamp"], reverse=True)[:5]
            insights["recent_detections"] = [
                {
                    "id": detection_id,
                    "algorithm": detection["algorithm"],
                    "timestamp": detection["timestamp"],
                    "anomaly_count": detection["anomaly_count"]
                }
                for detection_id, detection in recent_detections
            ]
        
        return insights

# Función principal para inicializar el motor
async def initialize_anomaly_detection_engine() -> AdvancedAnomalyDetectionEngine:
    """Inicializar motor de detección de anomalías avanzado"""
    engine = AdvancedAnomalyDetectionEngine()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    return engine

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        engine = await initialize_anomaly_detection_engine()
        
        # Crear datos de ejemplo
        np.random.seed(42)
        n_samples = 1000
        
        # Datos normales
        normal_data = np.random.normal(100, 10, n_samples)
        
        # Agregar anomalías
        anomaly_indices = np.random.choice(n_samples, size=50, replace=False)
        normal_data[anomaly_indices] = np.random.normal(200, 20, 50)
        
        data = pd.DataFrame({
            'value': normal_data,
            'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='H')
        })
        
        # Crear solicitud de detección
        request = AnomalyDetectionRequest(
            data=data,
            target_columns=['value'],
            anomaly_type=AnomalyType.POINT,
            algorithm=DetectionAlgorithm.ISOLATION_FOREST,
            contamination=0.05,
            threshold=0.5
        )
        
        # Detectar anomalías
        result = await engine.detect_anomalies(request)
        print("Anomaly Detection Result:")
        print(f"Anomalies found: {len(result.anomalies)}")
        print(f"Model metrics: {result.model_metrics}")
        print(f"Model info: {result.model_info}")
        
        # Obtener insights
        insights = await engine.get_anomaly_detection_insights()
        print("Anomaly Detection Insights:", json.dumps(insights, indent=2, default=str))
    
    asyncio.run(main())



