"""
Motor de Pronósticos Avanzado
Sistema de pronósticos con ML, deep learning y técnicas avanzadas de series temporales
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

# Time series libraries
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.exponential_smoothing import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing as HW

# Machine learning libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Deep learning libraries
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Conv1D, MaxPooling1D, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Prophet for advanced forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# XGBoost for time series
import xgboost as xgb
import lightgbm as lgb

class ForecastingType(Enum):
    UNIVARIATE = "univariate"
    MULTIVARIATE = "multivariate"
    SEASONAL = "seasonal"
    TREND = "trend"
    CYCLICAL = "cyclical"
    REGRESSION = "regression"
    DEEP_LEARNING = "deep_learning"
    ENSEMBLE = "ensemble"

class ForecastingAlgorithm(Enum):
    ARIMA = "arima"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    HOLT_WINTERS = "holt_winters"
    PROPHET = "prophet"
    LSTM = "lstm"
    GRU = "gru"
    CNN_LSTM = "cnn_lstm"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    RANDOM_FOREST = "random_forest"
    LINEAR_REGRESSION = "linear_regression"
    ENSEMBLE = "ensemble"

@dataclass
class ForecastingRequest:
    data: pd.DataFrame
    target_column: str
    forecast_type: ForecastingType
    algorithm: ForecastingAlgorithm
    forecast_horizon: int
    confidence_intervals: bool = True
    seasonal_periods: int = 12
    exogenous_variables: List[str] = None
    validation_split: float = 0.2
    parameters: Dict[str, Any] = None

@dataclass
class ForecastingResult:
    predictions: np.ndarray
    confidence_intervals: Optional[Tuple[np.ndarray, np.ndarray]]
    model_metrics: Dict[str, float]
    model_info: Dict[str, Any]
    forecast_dates: pd.DatetimeIndex
    feature_importance: Optional[Dict[str, float]]

class AdvancedForecastingEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.forecasting_history = {}
        self.performance_metrics = {}
        
        # Configuración por defecto
        self.default_config = {
            "max_forecast_horizon": 365,
            "min_data_points": 30,
            "seasonal_periods": 12,
            "confidence_level": 0.95,
            "validation_split": 0.2,
            "early_stopping_patience": 10,
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100
        }
        
    async def create_forecast(self, request: ForecastingRequest) -> ForecastingResult:
        """Crear pronóstico avanzado"""
        try:
            # Validar datos
            await self._validate_data(request)
            
            # Preparar datos
            processed_data = await self._prepare_data(request)
            
            # Crear pronóstico según algoritmo
            if request.algorithm == ForecastingAlgorithm.ARIMA:
                result = await self._create_arima_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.EXPONENTIAL_SMOOTHING:
                result = await self._create_exponential_smoothing_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.HOLT_WINTERS:
                result = await self._create_holt_winters_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.PROPHET:
                result = await self._create_prophet_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.LSTM:
                result = await self._create_lstm_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.GRU:
                result = await self._create_gru_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.CNN_LSTM:
                result = await self._create_cnn_lstm_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.XGBOOST:
                result = await self._create_xgboost_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.LIGHTGBM:
                result = await self._create_lightgbm_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.RANDOM_FOREST:
                result = await self._create_random_forest_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.LINEAR_REGRESSION:
                result = await self._create_linear_regression_forecast(request, processed_data)
            elif request.algorithm == ForecastingAlgorithm.ENSEMBLE:
                result = await self._create_ensemble_forecast(request, processed_data)
            else:
                raise ValueError(f"Unsupported forecasting algorithm: {request.algorithm}")
            
            # Guardar en historial
            await self._save_forecast_history(request, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating forecast: {e}")
            raise
    
    async def _validate_data(self, request: ForecastingRequest) -> None:
        """Validar datos de entrada"""
        try:
            if request.data is None or request.data.empty:
                raise ValueError("Data is empty or None")
            
            if request.target_column not in request.data.columns:
                raise ValueError(f"Target column {request.target_column} not found in data")
            
            if len(request.data) < self.default_config["min_data_points"]:
                raise ValueError(f"Insufficient data points. Minimum required: {self.default_config['min_data_points']}")
            
            if request.forecast_horizon > self.default_config["max_forecast_horizon"]:
                raise ValueError(f"Forecast horizon too large. Maximum allowed: {self.default_config['max_forecast_horizon']}")
            
        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            raise
    
    async def _prepare_data(self, request: ForecastingRequest) -> Dict[str, Any]:
        """Preparar datos para pronóstico"""
        try:
            data = request.data.copy()
            
            # Asegurar que hay una columna de fecha
            if 'date' not in data.columns and 'timestamp' not in data.columns:
                data['date'] = pd.date_range(start='2024-01-01', periods=len(data), freq='D')
            
            date_col = 'date' if 'date' in data.columns else 'timestamp'
            data[date_col] = pd.to_datetime(data[date_col])
            data = data.sort_values(date_col)
            
            # Crear características adicionales
            data = await self._create_time_features(data, date_col)
            
            # Manejar valores faltantes
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            # Crear variables exógenas si se especifican
            exogenous_data = None
            if request.exogenous_variables:
                exogenous_data = data[request.exogenous_variables]
            
            prepared_data = {
                "data": data,
                "target": data[request.target_column],
                "date_column": date_col,
                "exogenous": exogenous_data,
                "time_features": data[['year', 'month', 'day', 'dayofweek', 'quarter']] if all(col in data.columns for col in ['year', 'month', 'day', 'dayofweek', 'quarter']) else None
            }
            
            return prepared_data
            
        except Exception as e:
            self.logger.error(f"Error preparing data: {e}")
            raise
    
    async def _create_time_features(self, data: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """Crear características de tiempo"""
        try:
            data['year'] = data[date_col].dt.year
            data['month'] = data[date_col].dt.month
            data['day'] = data[date_col].dt.day
            data['dayofweek'] = data[date_col].dt.dayofweek
            data['quarter'] = data[date_col].dt.quarter
            data['dayofyear'] = data[date_col].dt.dayofyear
            data['weekofyear'] = data[date_col].dt.isocalendar().week
            
            # Características cíclicas
            data['month_sin'] = np.sin(2 * np.pi * data['month'] / 12)
            data['month_cos'] = np.cos(2 * np.pi * data['month'] / 12)
            data['dayofweek_sin'] = np.sin(2 * np.pi * data['dayofweek'] / 7)
            data['dayofweek_cos'] = np.cos(2 * np.pi * data['dayofweek'] / 7)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error creating time features: {e}")
            return data
    
    async def _create_arima_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con ARIMA"""
        try:
            target = processed_data["target"]
            
            # Determinar orden ARIMA automáticamente
            if request.parameters and "order" in request.parameters:
                order = request.parameters["order"]
            else:
                order = await self._auto_arima_order(target)
            
            # Crear modelo ARIMA
            model = ARIMA(target, order=order)
            fitted_model = model.fit()
            
            # Crear pronóstico
            forecast = fitted_model.forecast(steps=request.forecast_horizon)
            
            # Intervalos de confianza
            confidence_intervals = None
            if request.confidence_intervals:
                conf_int = fitted_model.get_forecast(steps=request.forecast_horizon).conf_int()
                confidence_intervals = (conf_int.iloc[:, 0].values, conf_int.iloc[:, 1].values)
            
            # Métricas del modelo
            aic = fitted_model.aic
            bic = fitted_model.bic
            log_likelihood = fitted_model.llf
            
            # Crear fechas de pronóstico
            last_date = processed_data["data"][processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=forecast.values,
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "aic": aic,
                    "bic": bic,
                    "log_likelihood": log_likelihood
                },
                model_info={
                    "algorithm": "ARIMA",
                    "order": order,
                    "parameters": fitted_model.params.to_dict()
                },
                forecast_dates=forecast_dates,
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating ARIMA forecast: {e}")
            raise
    
    async def _auto_arima_order(self, target: pd.Series) -> Tuple[int, int, int]:
        """Determinar orden ARIMA automáticamente"""
        try:
            # Test de estacionariedad
            adf_result = adfuller(target)
            is_stationary = adf_result[1] < 0.05
            
            if is_stationary:
                d = 0
            else:
                # Diferenciar hasta que sea estacionario
                d = 0
                diff_series = target.copy()
                while d < 3:
                    adf_result = adfuller(diff_series)
                    if adf_result[1] < 0.05:
                        break
                    diff_series = diff_series.diff().dropna()
                    d += 1
            
            # Usar AIC para seleccionar p y q
            best_aic = float('inf')
            best_order = (1, d, 1)
            
            for p in range(0, 4):
                for q in range(0, 4):
                    try:
                        model = ARIMA(target, order=(p, d, q))
                        fitted_model = model.fit()
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = (p, d, q)
                    except:
                        continue
            
            return best_order
            
        except Exception as e:
            self.logger.error(f"Error in auto ARIMA order: {e}")
            return (1, 1, 1)
    
    async def _create_exponential_smoothing_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con suavizado exponencial"""
        try:
            target = processed_data["target"]
            
            # Crear modelo de suavizado exponencial
            model = ExponentialSmoothing(
                target,
                trend='add',
                seasonal='add',
                seasonal_periods=request.seasonal_periods
            )
            fitted_model = model.fit()
            
            # Crear pronóstico
            forecast = fitted_model.forecast(steps=request.forecast_horizon)
            
            # Intervalos de confianza
            confidence_intervals = None
            if request.confidence_intervals:
                # Simular intervalos de confianza
                std_error = np.std(target) * 0.1
                lower_bound = forecast - 1.96 * std_error
                upper_bound = forecast + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Métricas del modelo
            aic = fitted_model.aic
            bic = fitted_model.bic
            
            # Crear fechas de pronóstico
            last_date = processed_data["data"][processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=forecast.values,
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "aic": aic,
                    "bic": bic,
                    "sse": fitted_model.sse
                },
                model_info={
                    "algorithm": "Exponential Smoothing",
                    "trend": "add",
                    "seasonal": "add",
                    "seasonal_periods": request.seasonal_periods
                },
                forecast_dates=forecast_dates,
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating exponential smoothing forecast: {e}")
            raise
    
    async def _create_holt_winters_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con Holt-Winters"""
        try:
            target = processed_data["target"]
            
            # Crear modelo Holt-Winters
            model = HW(
                target,
                trend='add',
                seasonal='add',
                seasonal_periods=request.seasonal_periods
            )
            fitted_model = model.fit()
            
            # Crear pronóstico
            forecast = fitted_model.forecast(steps=request.forecast_horizon)
            
            # Intervalos de confianza
            confidence_intervals = None
            if request.confidence_intervals:
                # Simular intervalos de confianza
                std_error = np.std(target) * 0.1
                lower_bound = forecast - 1.96 * std_error
                upper_bound = forecast + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Métricas del modelo
            aic = fitted_model.aic
            bic = fitted_model.bic
            
            # Crear fechas de pronóstico
            last_date = processed_data["data"][processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=forecast.values,
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "aic": aic,
                    "bic": bic,
                    "sse": fitted_model.sse
                },
                model_info={
                    "algorithm": "Holt-Winters",
                    "trend": "add",
                    "seasonal": "add",
                    "seasonal_periods": request.seasonal_periods
                },
                forecast_dates=forecast_dates,
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating Holt-Winters forecast: {e}")
            raise
    
    async def _create_prophet_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con Prophet"""
        try:
            if not PROPHET_AVAILABLE:
                raise ImportError("Prophet is not available. Please install it with: pip install prophet")
            
            data = processed_data["data"]
            date_col = processed_data["date_column"]
            target_col = request.target_column
            
            # Preparar datos para Prophet
            prophet_data = pd.DataFrame({
                'ds': data[date_col],
                'y': data[target_col]
            })
            
            # Crear modelo Prophet
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='additive'
            )
            
            # Agregar variables exógenas si están disponibles
            if processed_data["exogenous"] is not None:
                for col in processed_data["exogenous"].columns:
                    model.add_regressor(col)
                    prophet_data[col] = processed_data["exogenous"][col]
            
            # Entrenar modelo
            model.fit(prophet_data)
            
            # Crear pronóstico
            future = model.make_future_dataframe(periods=request.forecast_horizon)
            
            # Agregar variables exógenas al futuro
            if processed_data["exogenous"] is not None:
                for col in processed_data["exogenous"].columns:
                    # Extender variables exógenas con el último valor
                    last_value = processed_data["exogenous"][col].iloc[-1]
                    future[col] = last_value
            
            forecast = model.predict(future)
            
            # Extraer predicciones futuras
            future_predictions = forecast['yhat'].iloc[-request.forecast_horizon:].values
            
            # Intervalos de confianza
            confidence_intervals = None
            if request.confidence_intervals:
                lower_bound = forecast['yhat_lower'].iloc[-request.forecast_horizon:].values
                upper_bound = forecast['yhat_upper'].iloc[-request.forecast_horizon:].values
                confidence_intervals = (lower_bound, upper_bound)
            
            # Crear fechas de pronóstico
            last_date = data[date_col].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=future_predictions,
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "mape": np.mean(np.abs((data[target_col] - forecast['yhat'].iloc[:-request.forecast_horizon]) / data[target_col])) * 100
                },
                model_info={
                    "algorithm": "Prophet",
                    "yearly_seasonality": True,
                    "weekly_seasonality": True,
                    "daily_seasonality": False
                },
                forecast_dates=forecast_dates,
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating Prophet forecast: {e}")
            raise
    
    async def _create_lstm_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con LSTM"""
        try:
            target = processed_data["target"]
            
            # Preparar datos para LSTM
            sequence_length = request.parameters.get("sequence_length", 10) if request.parameters else 10
            
            # Normalizar datos
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(target.values.reshape(-1, 1))
            
            # Crear secuencias
            X, y = await self._create_sequences(scaled_data, sequence_length)
            
            # División train/validation
            split_idx = int(len(X) * (1 - request.validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Crear modelo LSTM
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=request.parameters.get("learning_rate", 0.001) if request.parameters else 0.001),
                         loss='mse')
            
            # Callbacks
            early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.0001)
            
            # Entrenar modelo
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=request.parameters.get("epochs", 100) if request.parameters else 100,
                batch_size=request.parameters.get("batch_size", 32) if request.parameters else 32,
                callbacks=[early_stopping, reduce_lr],
                verbose=0
            )
            
            # Crear pronóstico
            last_sequence = scaled_data[-sequence_length:].reshape(1, sequence_length, 1)
            predictions = []
            
            for _ in range(request.forecast_horizon):
                pred = model.predict(last_sequence, verbose=0)
                predictions.append(pred[0, 0])
                
                # Actualizar secuencia
                last_sequence = np.append(last_sequence[:, 1:, :], pred.reshape(1, 1, 1), axis=1)
            
            # Desnormalizar predicciones
            predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            
            # Intervalos de confianza (simulados)
            confidence_intervals = None
            if request.confidence_intervals:
                std_error = np.std(target) * 0.1
                lower_bound = predictions - 1.96 * std_error
                upper_bound = predictions + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Métricas del modelo
            val_loss = min(history.history['val_loss'])
            train_loss = min(history.history['loss'])
            
            # Crear fechas de pronóstico
            last_date = processed_data["data"][processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "val_loss": val_loss,
                    "train_loss": train_loss,
                    "epochs_trained": len(history.history['loss'])
                },
                model_info={
                    "algorithm": "LSTM",
                    "sequence_length": sequence_length,
                    "layers": 2,
                    "units": 50
                },
                forecast_dates=forecast_dates,
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating LSTM forecast: {e}")
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
    
    async def _create_gru_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con GRU"""
        try:
            target = processed_data["target"]
            
            # Preparar datos para GRU
            sequence_length = request.parameters.get("sequence_length", 10) if request.parameters else 10
            
            # Normalizar datos
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(target.values.reshape(-1, 1))
            
            # Crear secuencias
            X, y = await self._create_sequences(scaled_data, sequence_length)
            
            # División train/validation
            split_idx = int(len(X) * (1 - request.validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Crear modelo GRU
            model = Sequential([
                GRU(50, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                GRU(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=request.parameters.get("learning_rate", 0.001) if request.parameters else 0.001),
                         loss='mse')
            
            # Callbacks
            early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.0001)
            
            # Entrenar modelo
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=request.parameters.get("epochs", 100) if request.parameters else 100,
                batch_size=request.parameters.get("batch_size", 32) if request.parameters else 32,
                callbacks=[early_stopping, reduce_lr],
                verbose=0
            )
            
            # Crear pronóstico
            last_sequence = scaled_data[-sequence_length:].reshape(1, sequence_length, 1)
            predictions = []
            
            for _ in range(request.forecast_horizon):
                pred = model.predict(last_sequence, verbose=0)
                predictions.append(pred[0, 0])
                
                # Actualizar secuencia
                last_sequence = np.append(last_sequence[:, 1:, :], pred.reshape(1, 1, 1), axis=1)
            
            # Desnormalizar predicciones
            predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            
            # Intervalos de confianza (simulados)
            confidence_intervals = None
            if request.confidence_intervals:
                std_error = np.std(target) * 0.1
                lower_bound = predictions - 1.96 * std_error
                upper_bound = predictions + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Métricas del modelo
            val_loss = min(history.history['val_loss'])
            train_loss = min(history.history['loss'])
            
            # Crear fechas de pronóstico
            last_date = processed_data["data"][processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "val_loss": val_loss,
                    "train_loss": train_loss,
                    "epochs_trained": len(history.history['loss'])
                },
                model_info={
                    "algorithm": "GRU",
                    "sequence_length": sequence_length,
                    "layers": 2,
                    "units": 50
                },
                forecast_dates=forecast_dates,
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating GRU forecast: {e}")
            raise
    
    async def _create_cnn_lstm_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con CNN-LSTM"""
        try:
            target = processed_data["target"]
            
            # Preparar datos para CNN-LSTM
            sequence_length = request.parameters.get("sequence_length", 10) if request.parameters else 10
            
            # Normalizar datos
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(target.values.reshape(-1, 1))
            
            # Crear secuencias
            X, y = await self._create_sequences(scaled_data, sequence_length)
            
            # División train/validation
            split_idx = int(len(X) * (1 - request.validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Crear modelo CNN-LSTM
            model = Sequential([
                Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(sequence_length, 1)),
                MaxPooling1D(pool_size=2),
                LSTM(50, return_sequences=True),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=request.parameters.get("learning_rate", 0.001) if request.parameters else 0.001),
                         loss='mse')
            
            # Callbacks
            early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.0001)
            
            # Entrenar modelo
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=request.parameters.get("epochs", 100) if request.parameters else 100,
                batch_size=request.parameters.get("batch_size", 32) if request.parameters else 32,
                callbacks=[early_stopping, reduce_lr],
                verbose=0
            )
            
            # Crear pronóstico
            last_sequence = scaled_data[-sequence_length:].reshape(1, sequence_length, 1)
            predictions = []
            
            for _ in range(request.forecast_horizon):
                pred = model.predict(last_sequence, verbose=0)
                predictions.append(pred[0, 0])
                
                # Actualizar secuencia
                last_sequence = np.append(last_sequence[:, 1:, :], pred.reshape(1, 1, 1), axis=1)
            
            # Desnormalizar predicciones
            predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            
            # Intervalos de confianza (simulados)
            confidence_intervals = None
            if request.confidence_intervals:
                std_error = np.std(target) * 0.1
                lower_bound = predictions - 1.96 * std_error
                upper_bound = predictions + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Métricas del modelo
            val_loss = min(history.history['val_loss'])
            train_loss = min(history.history['loss'])
            
            # Crear fechas de pronóstico
            last_date = processed_data["data"][processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "val_loss": val_loss,
                    "train_loss": train_loss,
                    "epochs_trained": len(history.history['loss'])
                },
                model_info={
                    "algorithm": "CNN-LSTM",
                    "sequence_length": sequence_length,
                    "cnn_filters": 64,
                    "lstm_units": 50
                },
                forecast_dates=forecast_dates,
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating CNN-LSTM forecast: {e}")
            raise
    
    async def _create_xgboost_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con XGBoost"""
        try:
            data = processed_data["data"]
            target = processed_data["target"]
            
            # Crear características
            features = await self._create_ml_features(data, target, request.forecast_horizon)
            
            # División train/validation
            split_idx = int(len(features) * (1 - request.validation_split))
            X_train, X_val = features[:split_idx], features[split_idx:]
            y_train, y_val = target[:split_idx], target[split_idx:]
            
            # Crear modelo XGBoost
            model = xgb.XGBRegressor(
                n_estimators=request.parameters.get("n_estimators", 100) if request.parameters else 100,
                learning_rate=request.parameters.get("learning_rate", 0.1) if request.parameters else 0.1,
                max_depth=request.parameters.get("max_depth", 6) if request.parameters else 6,
                random_state=42
            )
            
            # Entrenar modelo
            model.fit(X_train, y_train)
            
            # Evaluar modelo
            val_predictions = model.predict(X_val)
            val_mse = mean_squared_error(y_val, val_predictions)
            val_mae = mean_absolute_error(y_val, val_predictions)
            val_r2 = r2_score(y_val, val_predictions)
            
            # Crear pronóstico
            last_features = features[-1:].copy()
            predictions = []
            
            for i in range(request.forecast_horizon):
                pred = model.predict(last_features)[0]
                predictions.append(pred)
                
                # Actualizar características para la siguiente predicción
                last_features = await self._update_features_for_forecast(last_features, pred, i)
            
            # Intervalos de confianza (simulados)
            confidence_intervals = None
            if request.confidence_intervals:
                std_error = np.std(target) * 0.1
                lower_bound = np.array(predictions) - 1.96 * std_error
                upper_bound = np.array(predictions) + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Feature importance
            feature_importance = dict(zip(range(len(features.columns)), model.feature_importances_))
            
            # Crear fechas de pronóstico
            last_date = data[processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=np.array(predictions),
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "val_mse": val_mse,
                    "val_mae": val_mae,
                    "val_r2": val_r2
                },
                model_info={
                    "algorithm": "XGBoost",
                    "n_estimators": model.n_estimators,
                    "learning_rate": model.learning_rate,
                    "max_depth": model.max_depth
                },
                forecast_dates=forecast_dates,
                feature_importance=feature_importance
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating XGBoost forecast: {e}")
            raise
    
    async def _create_lightgbm_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con LightGBM"""
        try:
            data = processed_data["data"]
            target = processed_data["target"]
            
            # Crear características
            features = await self._create_ml_features(data, target, request.forecast_horizon)
            
            # División train/validation
            split_idx = int(len(features) * (1 - request.validation_split))
            X_train, X_val = features[:split_idx], features[split_idx:]
            y_train, y_val = target[:split_idx], target[split_idx:]
            
            # Crear modelo LightGBM
            model = lgb.LGBMRegressor(
                n_estimators=request.parameters.get("n_estimators", 100) if request.parameters else 100,
                learning_rate=request.parameters.get("learning_rate", 0.1) if request.parameters else 0.1,
                max_depth=request.parameters.get("max_depth", 6) if request.parameters else 6,
                random_state=42,
                verbose=-1
            )
            
            # Entrenar modelo
            model.fit(X_train, y_train)
            
            # Evaluar modelo
            val_predictions = model.predict(X_val)
            val_mse = mean_squared_error(y_val, val_predictions)
            val_mae = mean_absolute_error(y_val, val_predictions)
            val_r2 = r2_score(y_val, val_predictions)
            
            # Crear pronóstico
            last_features = features[-1:].copy()
            predictions = []
            
            for i in range(request.forecast_horizon):
                pred = model.predict(last_features)[0]
                predictions.append(pred)
                
                # Actualizar características para la siguiente predicción
                last_features = await self._update_features_for_forecast(last_features, pred, i)
            
            # Intervalos de confianza (simulados)
            confidence_intervals = None
            if request.confidence_intervals:
                std_error = np.std(target) * 0.1
                lower_bound = np.array(predictions) - 1.96 * std_error
                upper_bound = np.array(predictions) + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Feature importance
            feature_importance = dict(zip(range(len(features.columns)), model.feature_importances_))
            
            # Crear fechas de pronóstico
            last_date = data[processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=np.array(predictions),
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "val_mse": val_mse,
                    "val_mae": val_mae,
                    "val_r2": val_r2
                },
                model_info={
                    "algorithm": "LightGBM",
                    "n_estimators": model.n_estimators,
                    "learning_rate": model.learning_rate,
                    "max_depth": model.max_depth
                },
                forecast_dates=forecast_dates,
                feature_importance=feature_importance
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating LightGBM forecast: {e}")
            raise
    
    async def _create_random_forest_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con Random Forest"""
        try:
            data = processed_data["data"]
            target = processed_data["target"]
            
            # Crear características
            features = await self._create_ml_features(data, target, request.forecast_horizon)
            
            # División train/validation
            split_idx = int(len(features) * (1 - request.validation_split))
            X_train, X_val = features[:split_idx], features[split_idx:]
            y_train, y_val = target[:split_idx], target[split_idx:]
            
            # Crear modelo Random Forest
            model = RandomForestRegressor(
                n_estimators=request.parameters.get("n_estimators", 100) if request.parameters else 100,
                max_depth=request.parameters.get("max_depth", 10) if request.parameters else 10,
                random_state=42
            )
            
            # Entrenar modelo
            model.fit(X_train, y_train)
            
            # Evaluar modelo
            val_predictions = model.predict(X_val)
            val_mse = mean_squared_error(y_val, val_predictions)
            val_mae = mean_absolute_error(y_val, val_predictions)
            val_r2 = r2_score(y_val, val_predictions)
            
            # Crear pronóstico
            last_features = features[-1:].copy()
            predictions = []
            
            for i in range(request.forecast_horizon):
                pred = model.predict(last_features)[0]
                predictions.append(pred)
                
                # Actualizar características para la siguiente predicción
                last_features = await self._update_features_for_forecast(last_features, pred, i)
            
            # Intervalos de confianza (simulados)
            confidence_intervals = None
            if request.confidence_intervals:
                std_error = np.std(target) * 0.1
                lower_bound = np.array(predictions) - 1.96 * std_error
                upper_bound = np.array(predictions) + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Feature importance
            feature_importance = dict(zip(features.columns, model.feature_importances_))
            
            # Crear fechas de pronóstico
            last_date = data[processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=np.array(predictions),
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "val_mse": val_mse,
                    "val_mae": val_mae,
                    "val_r2": val_r2
                },
                model_info={
                    "algorithm": "Random Forest",
                    "n_estimators": model.n_estimators,
                    "max_depth": model.max_depth
                },
                forecast_dates=forecast_dates,
                feature_importance=feature_importance
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating Random Forest forecast: {e}")
            raise
    
    async def _create_linear_regression_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico con Linear Regression"""
        try:
            data = processed_data["data"]
            target = processed_data["target"]
            
            # Crear características
            features = await self._create_ml_features(data, target, request.forecast_horizon)
            
            # División train/validation
            split_idx = int(len(features) * (1 - request.validation_split))
            X_train, X_val = features[:split_idx], features[split_idx:]
            y_train, y_val = target[:split_idx], target[split_idx:]
            
            # Crear modelo Linear Regression
            model = LinearRegression()
            
            # Entrenar modelo
            model.fit(X_train, y_train)
            
            # Evaluar modelo
            val_predictions = model.predict(X_val)
            val_mse = mean_squared_error(y_val, val_predictions)
            val_mae = mean_absolute_error(y_val, val_predictions)
            val_r2 = r2_score(y_val, val_predictions)
            
            # Crear pronóstico
            last_features = features[-1:].copy()
            predictions = []
            
            for i in range(request.forecast_horizon):
                pred = model.predict(last_features)[0]
                predictions.append(pred)
                
                # Actualizar características para la siguiente predicción
                last_features = await self._update_features_for_forecast(last_features, pred, i)
            
            # Intervalos de confianza (simulados)
            confidence_intervals = None
            if request.confidence_intervals:
                std_error = np.std(target) * 0.1
                lower_bound = np.array(predictions) - 1.96 * std_error
                upper_bound = np.array(predictions) + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Feature importance (coeficientes)
            feature_importance = dict(zip(features.columns, model.coef_))
            
            # Crear fechas de pronóstico
            last_date = data[processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=np.array(predictions),
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "val_mse": val_mse,
                    "val_mae": val_mae,
                    "val_r2": val_r2
                },
                model_info={
                    "algorithm": "Linear Regression",
                    "intercept": model.intercept_
                },
                forecast_dates=forecast_dates,
                feature_importance=feature_importance
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating Linear Regression forecast: {e}")
            raise
    
    async def _create_ensemble_forecast(self, request: ForecastingRequest, processed_data: Dict[str, Any]) -> ForecastingResult:
        """Crear pronóstico ensemble"""
        try:
            # Crear pronósticos con múltiples algoritmos
            algorithms = [
                ForecastingAlgorithm.ARIMA,
                ForecastingAlgorithm.EXPONENTIAL_SMOOTHING,
                ForecastingAlgorithm.XGBOOST,
                ForecastingAlgorithm.RANDOM_FOREST
            ]
            
            ensemble_predictions = []
            ensemble_metrics = {}
            
            for algorithm in algorithms:
                try:
                    # Crear solicitud para cada algoritmo
                    alg_request = ForecastingRequest(
                        data=request.data,
                        target_column=request.target_column,
                        forecast_type=request.forecast_type,
                        algorithm=algorithm,
                        forecast_horizon=request.forecast_horizon,
                        confidence_intervals=False,  # No necesitamos intervalos individuales
                        seasonal_periods=request.seasonal_periods,
                        exogenous_variables=request.exogenous_variables,
                        validation_split=request.validation_split,
                        parameters=request.parameters
                    )
                    
                    # Crear pronóstico
                    result = await self.create_forecast(alg_request)
                    ensemble_predictions.append(result.predictions)
                    ensemble_metrics[algorithm.value] = result.model_metrics
                    
                except Exception as e:
                    self.logger.warning(f"Error creating {algorithm.value} forecast: {e}")
                    continue
            
            if not ensemble_predictions:
                raise ValueError("No successful forecasts for ensemble")
            
            # Combinar pronósticos (promedio ponderado)
            weights = [1.0 / len(ensemble_predictions)] * len(ensemble_predictions)
            ensemble_pred = np.average(ensemble_predictions, axis=0, weights=weights)
            
            # Intervalos de confianza (simulados)
            confidence_intervals = None
            if request.confidence_intervals:
                std_error = np.std(ensemble_pred) * 0.1
                lower_bound = ensemble_pred - 1.96 * std_error
                upper_bound = ensemble_pred + 1.96 * std_error
                confidence_intervals = (lower_bound, upper_bound)
            
            # Crear fechas de pronóstico
            last_date = processed_data["data"][processed_data["date_column"]].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.forecast_horizon, freq='D')
            
            result = ForecastingResult(
                predictions=ensemble_pred,
                confidence_intervals=confidence_intervals,
                model_metrics=ensemble_metrics,
                model_info={
                    "algorithm": "Ensemble",
                    "base_algorithms": [alg.value for alg in algorithms],
                    "weights": weights
                },
                forecast_dates=forecast_dates,
                feature_importance=None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating ensemble forecast: {e}")
            raise
    
    async def _create_ml_features(self, data: pd.DataFrame, target: pd.Series, forecast_horizon: int) -> pd.DataFrame:
        """Crear características para modelos de ML"""
        try:
            features = pd.DataFrame()
            
            # Características de tiempo
            if 'year' in data.columns:
                features['year'] = data['year']
            if 'month' in data.columns:
                features['month'] = data['month']
            if 'day' in data.columns:
                features['day'] = data['day']
            if 'dayofweek' in data.columns:
                features['dayofweek'] = data['dayofweek']
            if 'quarter' in data.columns:
                features['quarter'] = data['quarter']
            
            # Características cíclicas
            if 'month_sin' in data.columns:
                features['month_sin'] = data['month_sin']
            if 'month_cos' in data.columns:
                features['month_cos'] = data['month_cos']
            if 'dayofweek_sin' in data.columns:
                features['dayofweek_sin'] = data['dayofweek_sin']
            if 'dayofweek_cos' in data.columns:
                features['dayofweek_cos'] = data['dayofweek_cos']
            
            # Características de lag
            for lag in [1, 2, 3, 7, 14, 30]:
                features[f'lag_{lag}'] = target.shift(lag)
            
            # Características de rolling
            for window in [7, 14, 30]:
                features[f'rolling_mean_{window}'] = target.rolling(window=window).mean()
                features[f'rolling_std_{window}'] = target.rolling(window=window).std()
                features[f'rolling_min_{window}'] = target.rolling(window=window).min()
                features[f'rolling_max_{window}'] = target.rolling(window=window).max()
            
            # Características de diferencia
            features['diff_1'] = target.diff(1)
            features['diff_7'] = target.diff(7)
            features['diff_30'] = target.diff(30)
            
            # Características de tendencia
            features['trend'] = range(len(target))
            features['trend_squared'] = features['trend'] ** 2
            
            # Eliminar filas con NaN
            features = features.fillna(method='ffill').fillna(method='bfill')
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error creating ML features: {e}")
            raise
    
    async def _update_features_for_forecast(self, features: pd.DataFrame, prediction: float, step: int) -> pd.DataFrame:
        """Actualizar características para pronóstico multi-paso"""
        try:
            # Crear nuevas características basadas en la predicción
            new_features = features.copy()
            
            # Actualizar lags
            for lag in [1, 2, 3, 7, 14, 30]:
                if f'lag_{lag}' in new_features.columns:
                    new_features[f'lag_{lag}'] = prediction
            
            # Actualizar características de tiempo
            if 'trend' in new_features.columns:
                new_features['trend'] = new_features['trend'].iloc[0] + step + 1
            
            if 'trend_squared' in new_features.columns:
                new_features['trend_squared'] = new_features['trend'] ** 2
            
            return new_features
            
        except Exception as e:
            self.logger.error(f"Error updating features for forecast: {e}")
            return features
    
    async def _save_forecast_history(self, request: ForecastingRequest, result: ForecastingResult) -> None:
        """Guardar historial de pronósticos"""
        try:
            forecast_id = f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.forecasting_history[forecast_id] = {
                "timestamp": datetime.now().isoformat(),
                "algorithm": request.algorithm.value,
                "forecast_type": request.forecast_type.value,
                "forecast_horizon": request.forecast_horizon,
                "target_column": request.target_column,
                "model_metrics": result.model_metrics,
                "model_info": result.model_info
            }
            
        except Exception as e:
            self.logger.error(f"Error saving forecast history: {e}")
    
    async def get_forecasting_insights(self) -> Dict[str, Any]:
        """Obtener insights de pronósticos"""
        insights = {
            "total_forecasts": len(self.forecasting_history),
            "algorithms_used": {},
            "forecast_types_used": {},
            "average_forecast_horizon": 0,
            "best_performing_algorithm": None,
            "recent_forecasts": []
        }
        
        if self.forecasting_history:
            # Análisis de algoritmos usados
            for forecast in self.forecasting_history.values():
                algorithm = forecast["algorithm"]
                insights["algorithms_used"][algorithm] = insights["algorithms_used"].get(algorithm, 0) + 1
                
                forecast_type = forecast["forecast_type"]
                insights["forecast_types_used"][forecast_type] = insights["forecast_types_used"].get(forecast_type, 0) + 1
            
            # Promedio de horizonte de pronóstico
            horizons = [forecast["forecast_horizon"] for forecast in self.forecasting_history.values()]
            insights["average_forecast_horizon"] = np.mean(horizons) if horizons else 0
            
            # Mejor algoritmo (basado en métricas)
            algorithm_performance = {}
            for forecast in self.forecasting_history.values():
                algorithm = forecast["algorithm"]
                metrics = forecast["model_metrics"]
                
                if algorithm not in algorithm_performance:
                    algorithm_performance[algorithm] = []
                
                # Usar R² si está disponible, sino MSE
                if "val_r2" in metrics:
                    algorithm_performance[algorithm].append(metrics["val_r2"])
                elif "val_mse" in metrics:
                    algorithm_performance[algorithm].append(-metrics["val_mse"])  # Negativo para maximizar
            
            if algorithm_performance:
                best_algorithm = max(algorithm_performance, key=lambda x: np.mean(algorithm_performance[x]))
                insights["best_performing_algorithm"] = best_algorithm
            
            # Pronósticos recientes
            recent_forecasts = sorted(self.forecasting_history.items(), key=lambda x: x[1]["timestamp"], reverse=True)[:5]
            insights["recent_forecasts"] = [
                {
                    "id": forecast_id,
                    "algorithm": forecast["algorithm"],
                    "timestamp": forecast["timestamp"],
                    "horizon": forecast["forecast_horizon"]
                }
                for forecast_id, forecast in recent_forecasts
            ]
        
        return insights

# Función principal para inicializar el motor
async def initialize_forecasting_engine() -> AdvancedForecastingEngine:
    """Inicializar motor de pronósticos avanzado"""
    engine = AdvancedForecastingEngine()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    return engine

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        engine = await initialize_forecasting_engine()
        
        # Crear datos de ejemplo
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=365, freq='D')
        trend = np.linspace(100, 200, 365)
        seasonal = 10 * np.sin(2 * np.pi * np.arange(365) / 365)
        noise = np.random.normal(0, 5, 365)
        values = trend + seasonal + noise
        
        data = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        # Crear solicitud de pronóstico
        request = ForecastingRequest(
            data=data,
            target_column='value',
            forecast_type=ForecastingType.UNIVARIATE,
            algorithm=ForecastingAlgorithm.ARIMA,
            forecast_horizon=30,
            confidence_intervals=True,
            seasonal_periods=365
        )
        
        # Crear pronóstico
        result = await engine.create_forecast(request)
        print("Forecast Result:")
        print(f"Predictions: {result.predictions[:5]}...")
        print(f"Model Metrics: {result.model_metrics}")
        print(f"Model Info: {result.model_info}")
        
        # Obtener insights
        insights = await engine.get_forecasting_insights()
        print("Forecasting Insights:", json.dumps(insights, indent=2, default=str))
    
    asyncio.run(main())



