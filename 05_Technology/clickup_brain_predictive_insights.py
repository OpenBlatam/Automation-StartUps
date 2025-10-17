#!/usr/bin/env python3
"""
ClickUp Brain Predictive Insights System
=======================================

Advanced predictive analytics and forecasting capabilities with
machine learning models, time series analysis, and intelligent predictions.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import threading
from contextlib import asynccontextmanager
import uuid
from abc import ABC, abstractmethod
import hashlib
import pickle
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import AutoTokenizer, AutoModel, pipeline
import openai
import requests
from PIL import Image
import cv2
import librosa
import spacy
import nltk
from textblob import TextBlob
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import redis
import sqlite3
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
import time
import random
from scipy import stats
from scipy.signal import find_peaks
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

ROOT = Path(__file__).parent

class PredictionType(Enum):
    """Prediction types."""
    TIME_SERIES = "time_series"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ANOMALY = "anomaly"
    TREND = "trend"
    PATTERN = "pattern"
    FORECAST = "forecast"
    OPTIMIZATION = "optimization"

class ForecastHorizon(Enum):
    """Forecast horizons."""
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-12 months
    STRATEGIC = "strategic"  # 1+ years

class ConfidenceLevel(Enum):
    """Confidence levels."""
    LOW = "low"  # < 60%
    MEDIUM = "medium"  # 60-80%
    HIGH = "high"  # 80-95%
    VERY_HIGH = "very_high"  # > 95%

@dataclass
class PredictionRequest:
    """Prediction request."""
    id: str
    prediction_type: PredictionType
    data: Dict[str, Any]
    horizon: ForecastHorizon = ForecastHorizon.SHORT_TERM
    confidence_threshold: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PredictionResult:
    """Prediction result."""
    id: str
    request_id: str
    prediction_type: PredictionType
    predicted_value: Any
    confidence: float
    confidence_level: ConfidenceLevel
    forecast_horizon: ForecastHorizon
    prediction_interval: Tuple[float, float] = None
    features_importance: Dict[str, float] = field(default_factory=dict)
    model_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TimeSeriesData:
    """Time series data."""
    timestamps: List[datetime]
    values: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrendAnalysis:
    """Trend analysis result."""
    trend_direction: str  # "upward", "downward", "stable", "volatile"
    trend_strength: float  # 0.0 to 1.0
    trend_confidence: float  # 0.0 to 1.0
    change_rate: float  # Rate of change
    seasonal_patterns: List[Dict[str, Any]] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)

class BasePredictor(ABC):
    """Base class for predictors."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"predictor_{name}")
        self.model = None
        self.is_trained = False
        self.training_data = []
        self.performance_metrics = {}
    
    @abstractmethod
    async def train(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Train the predictor."""
        pass
    
    @abstractmethod
    async def predict(self, request: PredictionRequest) -> PredictionResult:
        """Make a prediction."""
        pass
    
    @abstractmethod
    async def evaluate(self, test_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate predictor performance."""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'name': self.name,
            'is_trained': self.is_trained,
            'training_data_size': len(self.training_data),
            'performance_metrics': self.performance_metrics
        }

class TimeSeriesPredictor(BasePredictor):
    """Time series predictor."""
    
    def __init__(self, name: str = "time_series_predictor"):
        super().__init__(name)
        self.scaler = StandardScaler()
        self.lookback_window = 30
        self.forecast_steps = 7
    
    async def train(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Train time series predictor."""
        try:
            # Prepare time series data
            ts_data = self._prepare_time_series_data(data)
            
            if len(ts_data.values) < self.lookback_window:
                raise ValueError("Insufficient data for training")
            
            # Create sequences for training
            X, y = self._create_sequences(ts_data.values)
            
            # Scale the data
            X_scaled = self.scaler.fit_transform(X)
            y_scaled = self.scaler.transform(y.reshape(-1, 1)).flatten()
            
            # Build LSTM model
            self.model = self._build_lstm_model(X_scaled.shape[1])
            
            # Train the model
            history = self.model.fit(
                X_scaled, y_scaled,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
            
            self.is_trained = True
            self.training_data = data
            
            # Calculate performance metrics
            train_loss = history.history['loss'][-1]
            val_loss = history.history['val_loss'][-1]
            
            self.performance_metrics = {
                'train_loss': train_loss,
                'val_loss': val_loss,
                'data_points': len(ts_data.values)
            }
            
            self.logger.info(f"Time series predictor trained with {len(ts_data.values)} data points")
            return self.performance_metrics
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise
    
    def _prepare_time_series_data(self, data: List[Dict[str, Any]]) -> TimeSeriesData:
        """Prepare time series data from raw data."""
        timestamps = []
        values = []
        
        for item in data:
            if 'timestamp' in item and 'value' in item:
                timestamps.append(datetime.fromisoformat(item['timestamp']))
                values.append(float(item['value']))
        
        # Sort by timestamp
        sorted_data = sorted(zip(timestamps, values))
        timestamps, values = zip(*sorted_data)
        
        return TimeSeriesData(
            timestamps=list(timestamps),
            values=list(values)
        )
    
    def _create_sequences(self, values: List[float]) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training."""
        X, y = [], []
        
        for i in range(self.lookback_window, len(values)):
            X.append(values[i-self.lookback_window:i])
            y.append(values[i])
        
        return np.array(X), np.array(y)
    
    def _build_lstm_model(self, input_shape: int) -> keras.Model:
        """Build LSTM model for time series prediction."""
        model = keras.Sequential([
            layers.LSTM(50, return_sequences=True, input_shape=(input_shape, 1)),
            layers.Dropout(0.2),
            layers.LSTM(50, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(25),
            layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse')
        return model
    
    async def predict(self, request: PredictionRequest) -> PredictionResult:
        """Make time series prediction."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Get recent data for prediction
            recent_data = request.data.get('recent_values', [])
            
            if len(recent_data) < self.lookback_window:
                # Use training data if insufficient recent data
                recent_data = self.training_data[-self.lookback_window:]
                recent_values = [item['value'] for item in recent_data]
            else:
                recent_values = recent_data[-self.lookback_window:]
            
            # Prepare input sequence
            X = np.array(recent_values).reshape(1, self.lookback_window, 1)
            X_scaled = self.scaler.transform(X.reshape(-1, 1)).reshape(1, self.lookback_window, 1)
            
            # Make prediction
            prediction_scaled = self.model.predict(X_scaled, verbose=0)
            prediction = self.scaler.inverse_transform(prediction_scaled)[0][0]
            
            # Calculate confidence based on model performance
            confidence = max(0.0, 1.0 - self.performance_metrics.get('val_loss', 0.1))
            
            # Determine confidence level
            if confidence >= 0.95:
                confidence_level = ConfidenceLevel.VERY_HIGH
            elif confidence >= 0.8:
                confidence_level = ConfidenceLevel.HIGH
            elif confidence >= 0.6:
                confidence_level = ConfidenceLevel.MEDIUM
            else:
                confidence_level = ConfidenceLevel.LOW
            
            # Calculate prediction interval
            std_error = np.sqrt(self.performance_metrics.get('val_loss', 0.1))
            prediction_interval = (
                prediction - 1.96 * std_error,
                prediction + 1.96 * std_error
            )
            
            return PredictionResult(
                id=str(uuid.uuid4()),
                request_id=request.id,
                prediction_type=request.prediction_type,
                predicted_value=prediction,
                confidence=confidence,
                confidence_level=confidence_level,
                forecast_horizon=request.horizon,
                prediction_interval=prediction_interval,
                model_info=self.get_model_info(),
                metadata=request.metadata
            )
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise
    
    async def evaluate(self, test_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate predictor performance."""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        try:
            # Prepare test data
            ts_data = self._prepare_time_series_data(test_data)
            X, y = self._create_sequences(ts_data.values)
            
            # Scale the data
            X_scaled = self.scaler.transform(X)
            y_scaled = self.scaler.transform(y.reshape(-1, 1)).flatten()
            
            # Make predictions
            predictions_scaled = self.model.predict(X_scaled, verbose=0)
            predictions = self.scaler.inverse_transform(predictions_scaled).flatten()
            
            # Calculate metrics
            mse = mean_squared_error(y, predictions)
            mae = mean_absolute_error(y, predictions)
            r2 = r2_score(y, predictions)
            
            return {
                'mse': mse,
                'mae': mae,
                'r2_score': r2,
                'rmse': np.sqrt(mse)
            }
            
        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}")
            raise

class TrendPredictor(BasePredictor):
    """Trend prediction and analysis."""
    
    def __init__(self, name: str = "trend_predictor"):
        super().__init__(name)
        self.trend_model = None
        self.seasonal_model = None
    
    async def train(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Train trend predictor."""
        try:
            # Prepare time series data
            ts_data = self._prepare_time_series_data(data)
            
            if len(ts_data.values) < 10:
                raise ValueError("Insufficient data for trend analysis")
            
            # Analyze trends
            trend_analysis = await self._analyze_trends(ts_data)
            
            # Train trend model
            self.trend_model = await self._train_trend_model(ts_data)
            
            # Train seasonal model
            self.seasonal_model = await self._train_seasonal_model(ts_data)
            
            self.is_trained = True
            self.training_data = data
            
            # Calculate performance metrics
            self.performance_metrics = {
                'trend_strength': trend_analysis.trend_strength,
                'trend_confidence': trend_analysis.trend_confidence,
                'data_points': len(ts_data.values),
                'seasonal_patterns': len(trend_analysis.seasonal_patterns)
            }
            
            self.logger.info(f"Trend predictor trained with {len(ts_data.values)} data points")
            return self.performance_metrics
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise
    
    def _prepare_time_series_data(self, data: List[Dict[str, Any]]) -> TimeSeriesData:
        """Prepare time series data from raw data."""
        timestamps = []
        values = []
        
        for item in data:
            if 'timestamp' in item and 'value' in item:
                timestamps.append(datetime.fromisoformat(item['timestamp']))
                values.append(float(item['value']))
        
        # Sort by timestamp
        sorted_data = sorted(zip(timestamps, values))
        timestamps, values = zip(*sorted_data)
        
        return TimeSeriesData(
            timestamps=list(timestamps),
            values=list(values)
        )
    
    async def _analyze_trends(self, ts_data: TimeSeriesData) -> TrendAnalysis:
        """Analyze trends in time series data."""
        values = np.array(ts_data.values)
        timestamps = np.array(ts_data.timestamps)
        
        # Calculate trend using linear regression
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Determine trend direction
        if slope > 0.1:
            trend_direction = "upward"
        elif slope < -0.1:
            trend_direction = "downward"
        else:
            trend_direction = "stable"
        
        # Calculate trend strength
        trend_strength = abs(r_value)
        
        # Calculate trend confidence
        trend_confidence = 1.0 - p_value
        
        # Calculate change rate
        change_rate = slope
        
        # Detect seasonal patterns
        seasonal_patterns = await self._detect_seasonal_patterns(values)
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(values, timestamps)
        
        return TrendAnalysis(
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            trend_confidence=trend_confidence,
            change_rate=change_rate,
            seasonal_patterns=seasonal_patterns,
            anomalies=anomalies
        )
    
    async def _detect_seasonal_patterns(self, values: np.ndarray) -> List[Dict[str, Any]]:
        """Detect seasonal patterns in data."""
        patterns = []
        
        # Simple seasonal detection
        if len(values) >= 7:  # Weekly pattern
            weekly_avg = np.mean(values.reshape(-1, 7), axis=0)
            if np.std(weekly_avg) > 0.1 * np.mean(weekly_avg):
                patterns.append({
                    'type': 'weekly',
                    'strength': np.std(weekly_avg) / np.mean(weekly_avg),
                    'pattern': weekly_avg.tolist()
                })
        
        if len(values) >= 30:  # Monthly pattern
            monthly_avg = np.mean(values.reshape(-1, 30), axis=0)
            if np.std(monthly_avg) > 0.1 * np.mean(monthly_avg):
                patterns.append({
                    'type': 'monthly',
                    'strength': np.std(monthly_avg) / np.mean(monthly_avg),
                    'pattern': monthly_avg.tolist()
                })
        
        return patterns
    
    async def _detect_anomalies(self, values: np.ndarray, timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detect anomalies in time series data."""
        anomalies = []
        
        # Use Z-score method
        z_scores = np.abs(stats.zscore(values))
        threshold = 2.5
        
        for i, (z_score, timestamp, value) in enumerate(zip(z_scores, timestamps, values)):
            if z_score > threshold:
                anomalies.append({
                    'timestamp': timestamp.isoformat(),
                    'value': value,
                    'z_score': z_score,
                    'severity': 'high' if z_score > 3 else 'medium'
                })
        
        return anomalies
    
    async def _train_trend_model(self, ts_data: TimeSeriesData) -> Any:
        """Train trend model."""
        # Simple linear trend model
        x = np.arange(len(ts_data.values))
        y = ts_data.values
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(x.reshape(-1, 1), y)
        
        return model
    
    async def _train_seasonal_model(self, ts_data: TimeSeriesData) -> Any:
        """Train seasonal model."""
        # Simple seasonal model
        values = np.array(ts_data.values)
        
        # Calculate seasonal averages
        if len(values) >= 7:
            seasonal_avg = np.mean(values.reshape(-1, 7), axis=0)
        else:
            seasonal_avg = np.array([np.mean(values)])
        
        return seasonal_avg
    
    async def predict(self, request: PredictionRequest) -> PredictionResult:
        """Make trend prediction."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Get recent data
            recent_data = request.data.get('recent_values', [])
            
            if not recent_data:
                recent_data = self.training_data[-10:]
                recent_values = [item['value'] for item in recent_data]
            else:
                recent_values = recent_data[-10:]
            
            # Predict trend
            if self.trend_model:
                future_x = np.arange(len(recent_values), len(recent_values) + 7)
                trend_prediction = self.trend_model.predict(future_x.reshape(-1, 1))
                
                # Apply seasonal adjustment
                if self.seasonal_model is not None:
                    seasonal_factor = self.seasonal_model[len(recent_values) % len(self.seasonal_model)]
                    trend_prediction = trend_prediction * seasonal_factor
                
                predicted_value = trend_prediction[0]
            else:
                predicted_value = np.mean(recent_values)
            
            # Calculate confidence based on trend strength
            confidence = self.performance_metrics.get('trend_confidence', 0.5)
            
            # Determine confidence level
            if confidence >= 0.95:
                confidence_level = ConfidenceLevel.VERY_HIGH
            elif confidence >= 0.8:
                confidence_level = ConfidenceLevel.HIGH
            elif confidence >= 0.6:
                confidence_level = ConfidenceLevel.MEDIUM
            else:
                confidence_level = ConfidenceLevel.LOW
            
            return PredictionResult(
                id=str(uuid.uuid4()),
                request_id=request.id,
                prediction_type=request.prediction_type,
                predicted_value=predicted_value,
                confidence=confidence,
                confidence_level=confidence_level,
                forecast_horizon=request.horizon,
                model_info=self.get_model_info(),
                metadata=request.metadata
            )
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise
    
    async def evaluate(self, test_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate trend predictor performance."""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        try:
            # Prepare test data
            ts_data = self._prepare_time_series_data(test_data)
            
            # Analyze trends in test data
            trend_analysis = await self._analyze_trends(ts_data)
            
            return {
                'trend_strength': trend_analysis.trend_strength,
                'trend_confidence': trend_analysis.trend_confidence,
                'anomalies_detected': len(trend_analysis.anomalies),
                'seasonal_patterns': len(trend_analysis.seasonal_patterns)
            }
            
        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}")
            raise

class AnomalyPredictor(BasePredictor):
    """Anomaly detection and prediction."""
    
    def __init__(self, name: str = "anomaly_predictor"):
        super().__init__(name)
        self.threshold = 2.5
        self.isolation_forest = None
    
    async def train(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Train anomaly predictor."""
        try:
            # Prepare data
            features = self._extract_features(data)
            
            if len(features) < 10:
                raise ValueError("Insufficient data for anomaly detection")
            
            # Train isolation forest
            from sklearn.ensemble import IsolationForest
            
            self.isolation_forest = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            self.isolation_forest.fit(features)
            
            self.is_trained = True
            self.training_data = data
            
            # Calculate performance metrics
            anomaly_scores = self.isolation_forest.decision_function(features)
            anomalies_detected = np.sum(anomaly_scores < 0)
            
            self.performance_metrics = {
                'anomalies_detected': anomalies_detected,
                'anomaly_rate': anomalies_detected / len(features),
                'data_points': len(features)
            }
            
            self.logger.info(f"Anomaly predictor trained with {len(features)} data points")
            return self.performance_metrics
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise
    
    def _extract_features(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features from data."""
        features = []
        
        for item in data:
            feature_vector = []
            
            # Extract numerical features
            if 'value' in item:
                feature_vector.append(float(item['value']))
            
            if 'timestamp' in item:
                timestamp = datetime.fromisoformat(item['timestamp'])
                feature_vector.extend([
                    timestamp.hour,
                    timestamp.day_of_week,
                    timestamp.day,
                    timestamp.month
                ])
            
            # Add metadata features
            if 'metadata' in item:
                metadata = item['metadata']
                feature_vector.extend([
                    len(str(metadata.get('description', ''))),
                    metadata.get('priority', 0),
                    metadata.get('complexity', 0)
                ])
            
            if feature_vector:
                features.append(feature_vector)
        
        return np.array(features)
    
    async def predict(self, request: PredictionRequest) -> PredictionResult:
        """Make anomaly prediction."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Extract features from request data
            features = self._extract_features([request.data])
            
            if len(features) == 0:
                raise ValueError("No features extracted from request data")
            
            # Predict anomaly
            anomaly_score = self.isolation_forest.decision_function(features)[0]
            is_anomaly = anomaly_score < 0
            
            # Calculate confidence
            confidence = abs(anomaly_score)
            
            # Determine confidence level
            if confidence >= 0.8:
                confidence_level = ConfidenceLevel.VERY_HIGH
            elif confidence >= 0.6:
                confidence_level = ConfidenceLevel.HIGH
            elif confidence >= 0.4:
                confidence_level = ConfidenceLevel.MEDIUM
            else:
                confidence_level = ConfidenceLevel.LOW
            
            return PredictionResult(
                id=str(uuid.uuid4()),
                request_id=request.id,
                prediction_type=request.prediction_type,
                predicted_value=is_anomaly,
                confidence=confidence,
                confidence_level=confidence_level,
                forecast_horizon=request.horizon,
                model_info=self.get_model_info(),
                metadata=request.metadata
            )
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise
    
    async def evaluate(self, test_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate anomaly predictor performance."""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        try:
            # Prepare test data
            features = self._extract_features(test_data)
            
            # Make predictions
            anomaly_scores = self.isolation_forest.decision_function(features)
            predictions = anomaly_scores < 0
            
            # Calculate metrics
            true_anomalies = np.sum(predictions)
            total_samples = len(predictions)
            anomaly_rate = true_anomalies / total_samples
            
            return {
                'anomaly_rate': anomaly_rate,
                'anomalies_detected': true_anomalies,
                'total_samples': total_samples
            }
            
        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}")
            raise

class PredictiveInsights:
    """Main predictive insights system."""
    
    def __init__(self):
        self.predictors: Dict[str, BasePredictor] = {}
        self.prediction_history = []
        self.logger = logging.getLogger("predictive_insights")
        self._lock = threading.RLock()
    
    def add_predictor(self, predictor: BasePredictor) -> None:
        """Add a predictor to the system."""
        with self._lock:
            self.predictors[predictor.name] = predictor
        self.logger.info(f"Added predictor: {predictor.name}")
    
    async def train_predictor(self, predictor_name: str, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Train a predictor."""
        if predictor_name not in self.predictors:
            raise ValueError(f"Predictor {predictor_name} not found")
        
        predictor = self.predictors[predictor_name]
        return await predictor.train(data)
    
    async def make_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Make a prediction using the appropriate predictor."""
        # Select predictor based on prediction type
        predictor_name = self._select_predictor(request.prediction_type)
        
        if predictor_name not in self.predictors:
            raise ValueError(f"No predictor available for type: {request.prediction_type}")
        
        predictor = self.predictors[predictor_name]
        result = await predictor.predict(request)
        
        # Store prediction history
        with self._lock:
            self.prediction_history.append(result)
        
        return result
    
    def _select_predictor(self, prediction_type: PredictionType) -> str:
        """Select the appropriate predictor for the prediction type."""
        if prediction_type == PredictionType.TIME_SERIES:
            return "time_series_predictor"
        elif prediction_type == PredictionType.TREND:
            return "trend_predictor"
        elif prediction_type == PredictionType.ANOMALY:
            return "anomaly_predictor"
        else:
            return "time_series_predictor"  # Default
    
    async def get_insights(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get comprehensive insights from data."""
        insights = {
            'summary': {},
            'trends': {},
            'anomalies': {},
            'forecasts': {},
            'recommendations': []
        }
        
        # Analyze trends
        if 'trend_predictor' in self.predictors:
            trend_predictor = self.predictors['trend_predictor']
            if trend_predictor.is_trained:
                # Get trend analysis
                ts_data = trend_predictor._prepare_time_series_data(data)
                trend_analysis = await trend_predictor._analyze_trends(ts_data)
                
                insights['trends'] = {
                    'direction': trend_analysis.trend_direction,
                    'strength': trend_analysis.trend_strength,
                    'confidence': trend_analysis.trend_confidence,
                    'change_rate': trend_analysis.change_rate,
                    'seasonal_patterns': trend_analysis.seasonal_patterns,
                    'anomalies': trend_analysis.anomalies
                }
        
        # Detect anomalies
        if 'anomaly_predictor' in self.predictors:
            anomaly_predictor = self.predictors['anomaly_predictor']
            if anomaly_predictor.is_trained:
                features = anomaly_predictor._extract_features(data)
                anomaly_scores = anomaly_predictor.isolation_forest.decision_function(features)
                anomalies = data[np.where(anomaly_scores < 0)[0]]
                
                insights['anomalies'] = {
                    'count': len(anomalies),
                    'rate': len(anomalies) / len(data),
                    'details': anomalies.tolist()
                }
        
        # Generate recommendations
        insights['recommendations'] = await self._generate_recommendations(insights)
        
        return insights
    
    async def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on insights."""
        recommendations = []
        
        # Trend-based recommendations
        if 'trends' in insights:
            trends = insights['trends']
            if trends.get('direction') == 'downward' and trends.get('strength', 0) > 0.7:
                recommendations.append("Consider investigating the downward trend and taking corrective action")
            
            if trends.get('anomalies'):
                recommendations.append("Review detected anomalies for potential issues")
        
        # Anomaly-based recommendations
        if 'anomalies' in insights:
            anomalies = insights['anomalies']
            if anomalies.get('rate', 0) > 0.1:
                recommendations.append("High anomaly rate detected - investigate data quality and processes")
        
        return recommendations
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            'predictors': {name: predictor.get_model_info() for name, predictor in self.predictors.items()},
            'prediction_history_count': len(self.prediction_history),
            'active_predictors': sum(1 for p in self.predictors.values() if p.is_trained)
        }

# Global predictive insights
predictive_insights = PredictiveInsights()

def get_predictive_insights() -> PredictiveInsights:
    """Get global predictive insights."""
    return predictive_insights

async def create_time_series_predictor(name: str = "time_series_predictor") -> TimeSeriesPredictor:
    """Create a time series predictor."""
    predictor = TimeSeriesPredictor(name)
    predictive_insights.add_predictor(predictor)
    return predictor

async def create_trend_predictor(name: str = "trend_predictor") -> TrendPredictor:
    """Create a trend predictor."""
    predictor = TrendPredictor(name)
    predictive_insights.add_predictor(predictor)
    return predictor

async def create_anomaly_predictor(name: str = "anomaly_predictor") -> AnomalyPredictor:
    """Create an anomaly predictor."""
    predictor = AnomalyPredictor(name)
    predictive_insights.add_predictor(predictor)
    return predictor

if __name__ == "__main__":
    # Demo predictive insights
    print("ClickUp Brain Predictive Insights Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Get predictive insights
        insights = get_predictive_insights()
        
        # Create predictors
        ts_predictor = await create_time_series_predictor()
        trend_predictor = await create_trend_predictor()
        anomaly_predictor = await create_anomaly_predictor()
        
        # Generate sample data
        sample_data = []
        base_value = 100
        for i in range(100):
            timestamp = datetime.now() - timedelta(days=100-i)
            value = base_value + np.sin(i * 0.1) * 10 + np.random.normal(0, 5)
            sample_data.append({
                'timestamp': timestamp.isoformat(),
                'value': value,
                'metadata': {
                    'description': f'Sample data point {i}',
                    'priority': random.randint(1, 5),
                    'complexity': random.uniform(0, 1)
                }
            })
        
        # Train predictors
        print("Training predictors...")
        await insights.train_predictor("time_series_predictor", sample_data)
        await insights.train_predictor("trend_predictor", sample_data)
        await insights.train_predictor("anomaly_predictor", sample_data)
        
        # Make predictions
        print("\nMaking predictions...")
        
        # Time series prediction
        ts_request = PredictionRequest(
            id="ts_req_1",
            prediction_type=PredictionType.TIME_SERIES,
            data={'recent_values': [sample_data[-10:]]},
            horizon=ForecastHorizon.SHORT_TERM
        )
        
        ts_result = await insights.make_prediction(ts_request)
        print(f"Time Series Prediction: {ts_result.predicted_value:.2f}")
        print(f"Confidence: {ts_result.confidence:.2f}")
        print(f"Confidence Level: {ts_result.confidence_level.value}")
        
        # Trend prediction
        trend_request = PredictionRequest(
            id="trend_req_1",
            prediction_type=PredictionType.TREND,
            data={'recent_values': [item['value'] for item in sample_data[-10:]]},
            horizon=ForecastHorizon.MEDIUM_TERM
        )
        
        trend_result = await insights.make_prediction(trend_request)
        print(f"\nTrend Prediction: {trend_result.predicted_value:.2f}")
        print(f"Confidence: {trend_result.confidence:.2f}")
        print(f"Confidence Level: {trend_result.confidence_level.value}")
        
        # Anomaly prediction
        anomaly_request = PredictionRequest(
            id="anomaly_req_1",
            prediction_type=PredictionType.ANOMALY,
            data=sample_data[-1],
            horizon=ForecastHorizon.SHORT_TERM
        )
        
        anomaly_result = await insights.make_prediction(anomaly_request)
        print(f"\nAnomaly Prediction: {anomaly_result.predicted_value}")
        print(f"Confidence: {anomaly_result.confidence:.2f}")
        print(f"Confidence Level: {anomaly_result.confidence_level.value}")
        
        # Get comprehensive insights
        print("\nGenerating comprehensive insights...")
        comprehensive_insights = await insights.get_insights(sample_data)
        
        print(f"Trend Direction: {comprehensive_insights['trends'].get('direction', 'unknown')}")
        print(f"Trend Strength: {comprehensive_insights['trends'].get('strength', 0):.2f}")
        print(f"Anomalies Detected: {comprehensive_insights['anomalies'].get('count', 0)}")
        
        if comprehensive_insights['recommendations']:
            print("\nRecommendations:")
            for rec in comprehensive_insights['recommendations']:
                print(f"  - {rec}")
        
        # Get system status
        status = insights.get_system_status()
        print(f"\nSystem Status:")
        print(f"Active Predictors: {status['active_predictors']}")
        print(f"Prediction History: {status['prediction_history_count']}")
        
        print("\nPredictive insights demo completed!")
    
    asyncio.run(demo())









