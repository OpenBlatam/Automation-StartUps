"""
Machine Learning para Predicciones de Tendencias de Mercado

Sistema de ML para predecir tendencias futuras basado en datos históricos.
Incluye:
- Predicción de tendencias futuras
- Detección de anomalías
- Scoring de oportunidades
- Análisis de patrones temporales
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


@dataclass
class TrendPrediction:
    """Predicción de tendencia futura."""
    metric_name: str
    current_value: float
    predicted_value: float
    confidence: float  # 0-1
    timeframe_days: int
    trend_direction: str  # 'up', 'down', 'stable'
    change_percentage: float
    prediction_date: datetime


@dataclass
class AnomalyDetection:
    """Detección de anomalía en tendencia."""
    metric_name: str
    anomaly_type: str  # 'spike', 'drop', 'unusual_pattern'
    severity: str  # 'high', 'medium', 'low'
    current_value: float
    expected_value: float
    deviation: float
    detected_at: datetime
    explanation: str


class MarketMLPredictor:
    """Predictor ML para tendencias de mercado."""
    
    def __init__(self):
        """Inicializa el predictor ML."""
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.training_history: List[Dict[str, Any]] = []
    
    def prepare_features(
        self,
        historical_data: List[Dict[str, Any]],
        lookback_days: int = 30
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara features para entrenamiento.
        
        Args:
            historical_data: Datos históricos de tendencias
            lookback_days: Días hacia atrás para features
            
        Returns:
            Features y targets para entrenamiento
        """
        if len(historical_data) < lookback_days + 7:
            logger.warning(f"Insufficient data: {len(historical_data)} < {lookback_days + 7}")
            return np.array([]), np.array([])
        
        # Convertir a DataFrame
        df = pd.DataFrame(historical_data)
        
        # Ordenar por fecha
        if 'date' in df.columns:
            df = df.sort_values('date')
        
        # Extraer features temporales
        features = []
        targets = []
        
        for i in range(lookback_days, len(df) - 7):
            # Features: últimos N días
            window = df.iloc[i-lookback_days:i]
            
            feature_vector = [
                window['value'].mean(),  # Media
                window['value'].std(),   # Desviación estándar
                window['value'].min(),   # Mínimo
                window['value'].max(),   # Máximo
                window['value'].iloc[-1] - window['value'].iloc[0],  # Cambio en ventana
                (window['value'].iloc[-1] - window['value'].mean()) / (window['value'].std() + 1e-6),  # Z-score
            ]
            
            # Agregar tendencia (pendiente)
            if len(window) > 1:
                x = np.arange(len(window))
                slope = np.polyfit(x, window['value'].values, 1)[0]
                feature_vector.append(slope)
            else:
                feature_vector.append(0)
            
            # Agregar features de día de semana si hay fecha
            if 'date' in df.columns:
                date = pd.to_datetime(df.iloc[i]['date'])
                feature_vector.extend([
                    date.dayofweek,
                    date.day,
                    date.month
                ])
            
            features.append(feature_vector)
            
            # Target: valor promedio de los próximos 7 días
            future_window = df.iloc[i:i+7]
            target = future_window['value'].mean()
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def train_model(
        self,
        metric_name: str,
        historical_data: List[Dict[str, Any]],
        model_type: str = "random_forest"
    ) -> Dict[str, Any]:
        """
        Entrena modelo ML para una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            historical_data: Datos históricos
            model_type: Tipo de modelo ("random_forest", "gradient_boosting")
            
        Returns:
            Resultados del entrenamiento
        """
        logger.info(f"Training ML model for {metric_name}")
        
        try:
            # Preparar datos
            X, y = self.prepare_features(historical_data)
            
            if len(X) == 0:
                return {
                    "success": False,
                    "error": "Insufficient data for training"
                }
            
            # Dividir en train/test
            if len(X) < 20:
                X_train, X_test, y_train, y_test = X, X, y, y
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
            
            # Escalar features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Entrenar modelo
            if model_type == "random_forest":
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
            else:  # gradient_boosting
                model = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=5,
                    random_state=42
                )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluar
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test) if len(X_test) > 0 else train_score
            
            # Guardar modelo y scaler
            self.models[metric_name] = model
            self.scalers[metric_name] = scaler
            
            # Guardar historial
            training_result = {
                "metric_name": metric_name,
                "model_type": model_type,
                "train_score": float(train_score),
                "test_score": float(test_score),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "trained_at": datetime.utcnow().isoformat()
            }
            self.training_history.append(training_result)
            
            logger.info(f"Model trained successfully: train_score={train_score:.3f}, test_score={test_score:.3f}")
            
            return {
                "success": True,
                **training_result
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def predict_trend(
        self,
        metric_name: str,
        current_data: List[Dict[str, Any]],
        timeframe_days: int = 30
    ) -> Optional[TrendPrediction]:
        """
        Predice tendencia futura.
        
        Args:
            metric_name: Nombre de la métrica
            current_data: Datos actuales
            timeframe_days: Días hacia adelante para predecir
            
        Returns:
            Predicción de tendencia
        """
        if metric_name not in self.models:
            logger.warning(f"Model not trained for {metric_name}, training now...")
            train_result = self.train_model(metric_name, current_data)
            if not train_result.get("success"):
                return None
        
        try:
            model = self.models[metric_name]
            scaler = self.scalers[metric_name]
            
            # Preparar features del último punto
            if len(current_data) < 30:
                logger.warning(f"Insufficient data for prediction: {len(current_data)}")
                return None
            
            # Obtener últimos 30 días
            recent_data = current_data[-30:]
            df = pd.DataFrame(recent_data)
            
            if 'date' in df.columns:
                df = df.sort_values('date')
            
            # Extraer features
            window = df.tail(30)
            feature_vector = [
                window['value'].mean(),
                window['value'].std(),
                window['value'].min(),
                window['value'].max(),
                window['value'].iloc[-1] - window['value'].iloc[0],
                (window['value'].iloc[-1] - window['value'].mean()) / (window['value'].std() + 1e-6),
            ]
            
            # Pendiente
            if len(window) > 1:
                x = np.arange(len(window))
                slope = np.polyfit(x, window['value'].values, 1)[0]
                feature_vector.append(slope)
            else:
                feature_vector.append(0)
            
            # Features de fecha
            if 'date' in df.columns:
                date = pd.to_datetime(df.iloc[-1]['date'])
                feature_vector.extend([
                    date.dayofweek,
                    date.day,
                    date.month
                ])
            
            # Escalar y predecir
            X = np.array([feature_vector])
            X_scaled = scaler.transform(X)
            prediction = model.predict(X_scaled)[0]
            
            # Valor actual
            current_value = float(df['value'].iloc[-1])
            
            # Calcular confianza basada en score del modelo
            test_score = next(
                (t["test_score"] for t in self.training_history if t["metric_name"] == metric_name),
                0.7
            )
            confidence = max(0.5, min(0.95, test_score))
            
            # Dirección de tendencia
            change = prediction - current_value
            change_pct = (change / current_value * 100) if current_value != 0 else 0
            
            if abs(change_pct) < 2:
                direction = "stable"
            elif change_pct > 0:
                direction = "up"
            else:
                direction = "down"
            
            return TrendPrediction(
                metric_name=metric_name,
                current_value=current_value,
                predicted_value=float(prediction),
                confidence=confidence,
                timeframe_days=timeframe_days,
                trend_direction=direction,
                change_percentage=change_pct,
                prediction_date=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error predicting trend: {e}")
            return None
    
    def detect_anomalies(
        self,
        metric_name: str,
        current_data: List[Dict[str, Any]],
        threshold_std: float = 2.5
    ) -> List[AnomalyDetection]:
        """
        Detecta anomalías en tendencias.
        
        Args:
            metric_name: Nombre de la métrica
            current_data: Datos actuales
            threshold_std: Umbral de desviación estándar
            
        Returns:
            Lista de anomalías detectadas
        """
        anomalies = []
        
        try:
            if len(current_data) < 10:
                return anomalies
            
            df = pd.DataFrame(current_data)
            if 'date' in df.columns:
                df = df.sort_values('date')
            
            values = df['value'].values
            mean = np.mean(values)
            std = np.std(values)
            
            # Detectar valores anómalos
            for i, value in enumerate(values):
                z_score = abs((value - mean) / (std + 1e-6))
                
                if z_score > threshold_std:
                    # Determinar tipo de anomalía
                    if value > mean + threshold_std * std:
                        anomaly_type = "spike"
                        severity = "high" if z_score > 3 else "medium"
                    else:
                        anomaly_type = "drop"
                        severity = "high" if z_score > 3 else "medium"
                    
                    # Predecir valor esperado
                    if metric_name in self.models:
                        prediction = self.predict_trend(metric_name, current_data[:i+1])
                        expected_value = prediction.current_value if prediction else mean
                    else:
                        expected_value = mean
                    
                    anomaly = AnomalyDetection(
                        metric_name=metric_name,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        current_value=float(value),
                        expected_value=float(expected_value),
                        deviation=float(z_score),
                        detected_at=datetime.utcnow(),
                        explanation=f"{anomaly_type.capitalize()} detected: value {value:.2f} is {z_score:.2f} standard deviations from mean"
                    )
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def score_opportunity(
        self,
        trend_data: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> float:
        """
        Calcula score de oportunidad (0-100).
        
        Args:
            trend_data: Datos de la tendencia
            market_context: Contexto del mercado
            
        Returns:
            Score de oportunidad (0-100)
        """
        score = 50.0  # Base score
        
        # Factor 1: Magnitud del cambio
        change_pct = abs(trend_data.get("change_percentage", 0))
        if change_pct > 20:
            score += 20
        elif change_pct > 10:
            score += 10
        elif change_pct > 5:
            score += 5
        
        # Factor 2: Confianza
        confidence = trend_data.get("confidence", 0.5)
        score += confidence * 15
        
        # Factor 3: Dirección (alcista es mejor)
        if trend_data.get("trend_direction") == "up":
            score += 10
        
        # Factor 4: Momentum del mercado
        market_momentum = market_context.get("momentum", 0)
        if market_momentum > 0.7:
            score += 10
        elif market_momentum > 0.5:
            score += 5
        
        # Factor 5: Competencia
        competition_level = market_context.get("competition_level", 0.5)
        if competition_level < 0.3:  # Baja competencia
            score += 5
        
        return min(100.0, max(0.0, score))






