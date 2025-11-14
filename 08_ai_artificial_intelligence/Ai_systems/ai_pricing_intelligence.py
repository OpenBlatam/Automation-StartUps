#!/usr/bin/env python3
"""
AI Pricing Intelligence System
==============================

Sistema de inteligencia artificial avanzado para análisis de precios competitivos:
- Análisis de patrones de precios con deep learning
- Predicción de movimientos de mercado
- Análisis de comportamiento de competidores
- Optimización automática de precios
- Detección de anomalías en precios
- Análisis de correlaciones de mercado
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Attention, MultiHeadAttention
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import joblib
import warnings
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import sqlite3
import json
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
import seaborn as sns
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

@dataclass
class PricePattern:
    """Estructura para patrones de precios"""
    pattern_type: str
    confidence: float
    start_date: datetime
    end_date: datetime
    price_range: Tuple[float, float]
    frequency: int
    description: str

@dataclass
class MarketAnomaly:
    """Estructura para anomalías de mercado"""
    anomaly_type: str
    severity: float
    detected_at: datetime
    product_id: str
    competitor: str
    expected_price: float
    actual_price: float
    deviation: float
    description: str

@dataclass
class CompetitorBehavior:
    """Estructura para comportamiento de competidores"""
    competitor: str
    behavior_type: str
    frequency: float
    price_sensitivity: float
    reaction_time: float
    market_share_impact: float
    description: str

class DeepLearningPricePredictor:
    """Predictor de precios con deep learning"""
    
    def __init__(self, sequence_length: int = 30):
        """Inicializar predictor de precios"""
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler()
        self.feature_scaler = StandardScaler()
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos para entrenamiento"""
        try:
            # Crear features adicionales
            df = self._create_features(df)
            
            # Seleccionar features relevantes
            feature_columns = [
                'price', 'price_lag_1', 'price_lag_7', 'price_ma_7', 'price_ma_30',
                'price_volatility', 'competitor_count', 'market_share', 'sentiment_score'
            ]
            
            # Filtrar columnas existentes
            available_features = [col for col in feature_columns if col in df.columns]
            
            if not available_features:
                available_features = ['price']
            
            # Preparar datos
            data = df[available_features].fillna(0)
            
            # Escalar features
            scaled_features = self.feature_scaler.fit_transform(data)
            
            # Crear secuencias
            X, y = self._create_sequences(scaled_features)
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            return np.array([]), np.array([])
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear features adicionales"""
        df = df.copy()
        
        # Features de precios
        df['price_lag_1'] = df['price'].shift(1)
        df['price_lag_7'] = df['price'].shift(7)
        df['price_ma_7'] = df['price'].rolling(7).mean()
        df['price_ma_30'] = df['price'].rolling(30).mean()
        df['price_volatility'] = df['price'].rolling(7).std()
        
        # Features de mercado
        df['competitor_count'] = df.groupby('date')['competitor'].transform('nunique')
        df['market_share'] = df.groupby('date')['price'].rank(pct=True)
        
        # Features de sentimiento (simulados)
        df['sentiment_score'] = np.random.uniform(-1, 1, len(df))
        
        return df
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Crear secuencias para LSTM"""
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data[i-self.sequence_length:i])
            y.append(data[i, 0])  # Predecir precio
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple[int, int]) -> Model:
        """Construir modelo de deep learning"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100) -> Dict[str, Any]:
        """Entrenar modelo"""
        try:
            if len(X) == 0:
                return {'error': 'No data available for training'}
            
            # Construir modelo
            self.model = self.build_model((X.shape[1], X.shape[2]))
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(factor=0.5, patience=5)
            ]
            
            # Entrenar
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=32,
                validation_split=0.2,
                callbacks=callbacks,
                verbose=0
            )
            
            return {
                'training_loss': history.history['loss'][-1],
                'validation_loss': history.history['val_loss'][-1],
                'training_mae': history.history['mae'][-1],
                'validation_mae': history.history['val_mae'][-1]
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {'error': str(e)}
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Hacer predicciones"""
        try:
            if self.model is None:
                return np.array([])
            
            predictions = self.model.predict(X)
            return predictions.flatten()
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return np.array([])

class PricePatternAnalyzer:
    """Analizador de patrones de precios"""
    
    def __init__(self):
        """Inicializar analizador de patrones"""
        self.patterns = []
        
    def detect_patterns(self, df: pd.DataFrame) -> List[PricePattern]:
        """Detectar patrones en precios"""
        try:
            patterns = []
            
            # Patrón de tendencia
            trend_pattern = self._detect_trend_pattern(df)
            if trend_pattern:
                patterns.append(trend_pattern)
            
            # Patrón estacional
            seasonal_pattern = self._detect_seasonal_pattern(df)
            if seasonal_pattern:
                patterns.append(seasonal_pattern)
            
            # Patrón cíclico
            cyclical_pattern = self._detect_cyclical_pattern(df)
            if cyclical_pattern:
                patterns.append(cyclical_pattern)
            
            # Patrón de volatilidad
            volatility_pattern = self._detect_volatility_pattern(df)
            if volatility_pattern:
                patterns.append(volatility_pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return []
    
    def _detect_trend_pattern(self, df: pd.DataFrame) -> Optional[PricePattern]:
        """Detectar patrón de tendencia"""
        try:
            if len(df) < 10:
                return None
            
            # Calcular tendencia usando regresión lineal
            x = np.arange(len(df))
            y = df['price'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            if abs(r_value) > 0.7:  # Correlación fuerte
                trend_type = "increasing" if slope > 0 else "decreasing"
                
                return PricePattern(
                    pattern_type=f"trend_{trend_type}",
                    confidence=abs(r_value),
                    start_date=df['date'].iloc[0],
                    end_date=df['date'].iloc[-1],
                    price_range=(y.min(), y.max()),
                    frequency=1,
                    description=f"Strong {trend_type} trend with {abs(r_value):.2f} correlation"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting trend pattern: {e}")
            return None
    
    def _detect_seasonal_pattern(self, df: pd.DataFrame) -> Optional[PricePattern]:
        """Detectar patrón estacional"""
        try:
            if len(df) < 30:
                return None
            
            # Agrupar por día de la semana
            df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
            weekly_avg = df.groupby('day_of_week')['price'].mean()
            
            # Calcular variabilidad semanal
            weekly_std = df.groupby('day_of_week')['price'].std()
            coefficient_of_variation = weekly_std / weekly_avg
            
            if coefficient_of_variation.mean() > 0.1:  # Variabilidad significativa
                return PricePattern(
                    pattern_type="seasonal_weekly",
                    confidence=coefficient_of_variation.mean(),
                    start_date=df['date'].iloc[0],
                    end_date=df['date'].iloc[-1],
                    price_range=(df['price'].min(), df['price'].max()),
                    frequency=7,
                    description=f"Weekly seasonal pattern with {coefficient_of_variation.mean():.2f} variability"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting seasonal pattern: {e}")
            return None
    
    def _detect_cyclical_pattern(self, df: pd.DataFrame) -> Optional[PricePattern]:
        """Detectar patrón cíclico"""
        try:
            if len(df) < 20:
                return None
            
            # Usar FFT para detectar ciclos
            prices = df['price'].values
            fft = np.fft.fft(prices)
            frequencies = np.fft.fftfreq(len(prices))
            
            # Encontrar frecuencias dominantes
            power_spectrum = np.abs(fft) ** 2
            dominant_freq_idx = np.argmax(power_spectrum[1:len(power_spectrum)//2]) + 1
            dominant_frequency = frequencies[dominant_freq_idx]
            
            if abs(dominant_frequency) > 0.01:  # Frecuencia significativa
                cycle_length = int(1 / abs(dominant_frequency))
                
                return PricePattern(
                    pattern_type="cyclical",
                    confidence=power_spectrum[dominant_freq_idx] / power_spectrum.sum(),
                    start_date=df['date'].iloc[0],
                    end_date=df['date'].iloc[-1],
                    price_range=(prices.min(), prices.max()),
                    frequency=cycle_length,
                    description=f"Cyclical pattern with {cycle_length} day cycle"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting cyclical pattern: {e}")
            return None
    
    def _detect_volatility_pattern(self, df: pd.DataFrame) -> Optional[PricePattern]:
        """Detectar patrón de volatilidad"""
        try:
            if len(df) < 10:
                return None
            
            # Calcular volatilidad móvil
            df['volatility'] = df['price'].rolling(7).std()
            
            # Detectar períodos de alta/baja volatilidad
            high_vol_threshold = df['volatility'].quantile(0.8)
            low_vol_threshold = df['volatility'].quantile(0.2)
            
            high_vol_periods = df[df['volatility'] > high_vol_threshold]
            low_vol_periods = df[df['volatility'] < low_vol_threshold]
            
            if len(high_vol_periods) > 0 and len(low_vol_periods) > 0:
                return PricePattern(
                    pattern_type="volatility_clustering",
                    confidence=0.7,
                    start_date=df['date'].iloc[0],
                    end_date=df['date'].iloc[-1],
                    price_range=(df['price'].min(), df['price'].max()),
                    frequency=len(high_vol_periods),
                    description=f"Volatility clustering with {len(high_vol_periods)} high volatility periods"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting volatility pattern: {e}")
            return None

class MarketAnomalyDetector:
    """Detector de anomalías de mercado"""
    
    def __init__(self):
        """Inicializar detector de anomalías"""
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        
    def detect_anomalies(self, df: pd.DataFrame) -> List[MarketAnomaly]:
        """Detectar anomalías en precios"""
        try:
            anomalies = []
            
            # Anomalías estadísticas
            statistical_anomalies = self._detect_statistical_anomalies(df)
            anomalies.extend(statistical_anomalies)
            
            # Anomalías de comportamiento
            behavior_anomalies = self._detect_behavior_anomalies(df)
            anomalies.extend(behavior_anomalies)
            
            # Anomalías de correlación
            correlation_anomalies = self._detect_correlation_anomalies(df)
            anomalies.extend(correlation_anomalies)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def _detect_statistical_anomalies(self, df: pd.DataFrame) -> List[MarketAnomaly]:
        """Detectar anomalías estadísticas"""
        anomalies = []
        
        try:
            # Usar Isolation Forest
            features = df[['price']].values
            anomaly_scores = self.isolation_forest.fit_predict(features)
            
            for i, score in enumerate(anomaly_scores):
                if score == -1:  # Anomalía detectada
                    expected_price = df['price'].mean()
                    actual_price = df['price'].iloc[i]
                    deviation = abs(actual_price - expected_price) / expected_price
                    
                    anomaly = MarketAnomaly(
                        anomaly_type="statistical_outlier",
                        severity=deviation,
                        detected_at=datetime.now(),
                        product_id=df['product_id'].iloc[i] if 'product_id' in df.columns else "unknown",
                        competitor=df['competitor'].iloc[i] if 'competitor' in df.columns else "unknown",
                        expected_price=expected_price,
                        actual_price=actual_price,
                        deviation=deviation,
                        description=f"Statistical outlier: price {actual_price:.2f} vs expected {expected_price:.2f}"
                    )
                    
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting statistical anomalies: {e}")
            return []
    
    def _detect_behavior_anomalies(self, df: pd.DataFrame) -> List[MarketAnomaly]:
        """Detectar anomalías de comportamiento"""
        anomalies = []
        
        try:
            # Detectar cambios bruscos de precio
            price_changes = df['price'].pct_change().abs()
            sudden_changes = price_changes > price_changes.quantile(0.95)
            
            for i, is_anomaly in enumerate(sudden_changes):
                if is_anomaly and i > 0:
                    price_change = price_changes.iloc[i]
                    expected_change = price_changes.rolling(10).mean().iloc[i]
                    
                    anomaly = MarketAnomaly(
                        anomaly_type="sudden_price_change",
                        severity=price_change,
                        detected_at=datetime.now(),
                        product_id=df['product_id'].iloc[i] if 'product_id' in df.columns else "unknown",
                        competitor=df['competitor'].iloc[i] if 'competitor' in df.columns else "unknown",
                        expected_price=df['price'].iloc[i-1] * (1 + expected_change),
                        actual_price=df['price'].iloc[i],
                        deviation=price_change,
                        description=f"Sudden price change: {price_change:.1%} vs expected {expected_change:.1%}"
                    )
                    
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting behavior anomalies: {e}")
            return []
    
    def _detect_correlation_anomalies(self, df: pd.DataFrame) -> List[MarketAnomaly]:
        """Detectar anomalías de correlación"""
        anomalies = []
        
        try:
            # Agrupar por competidor y calcular correlaciones
            if 'competitor' in df.columns:
                competitors = df['competitor'].unique()
                
                for competitor in competitors:
                    competitor_data = df[df['competitor'] == competitor]
                    
                    if len(competitor_data) > 10:
                        # Calcular correlación con el mercado
                        market_avg = df.groupby('date')['price'].mean()
                        competitor_avg = competitor_data.groupby('date')['price'].mean()
                        
                        # Alinear fechas
                        common_dates = market_avg.index.intersection(competitor_avg.index)
                        if len(common_dates) > 5:
                            correlation = np.corrcoef(
                                market_avg[common_dates],
                                competitor_avg[common_dates]
                            )[0, 1]
                            
                            if abs(correlation) < 0.3:  # Correlación baja
                                anomaly = MarketAnomaly(
                                    anomaly_type="correlation_anomaly",
                                    severity=1 - abs(correlation),
                                    detected_at=datetime.now(),
                                    product_id=competitor_data['product_id'].iloc[0] if 'product_id' in competitor_data.columns else "unknown",
                                    competitor=competitor,
                                    expected_price=market_avg.mean(),
                                    actual_price=competitor_avg.mean(),
                                    deviation=1 - abs(correlation),
                                    description=f"Low correlation with market: {correlation:.2f}"
                                )
                                
                                anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting correlation anomalies: {e}")
            return []

class CompetitorBehaviorAnalyzer:
    """Analizador de comportamiento de competidores"""
    
    def __init__(self):
        """Inicializar analizador de comportamiento"""
        self.behaviors = []
        
    def analyze_behavior(self, df: pd.DataFrame) -> List[CompetitorBehavior]:
        """Analizar comportamiento de competidores"""
        try:
            behaviors = []
            
            if 'competitor' not in df.columns:
                return behaviors
            
            competitors = df['competitor'].unique()
            
            for competitor in competitors:
                competitor_data = df[df['competitor'] == competitor]
                
                if len(competitor_data) > 5:
                    # Análisis de frecuencia de cambios
                    frequency_behavior = self._analyze_change_frequency(competitor_data, competitor)
                    if frequency_behavior:
                        behaviors.append(frequency_behavior)
                    
                    # Análisis de sensibilidad a precios
                    sensitivity_behavior = self._analyze_price_sensitivity(competitor_data, competitor)
                    if sensitivity_behavior:
                        behaviors.append(sensitivity_behavior)
                    
                    # Análisis de tiempo de reacción
                    reaction_behavior = self._analyze_reaction_time(competitor_data, competitor)
                    if reaction_behavior:
                        behaviors.append(reaction_behavior)
            
            return behaviors
            
        except Exception as e:
            logger.error(f"Error analyzing competitor behavior: {e}")
            return []
    
    def _analyze_change_frequency(self, competitor_data: pd.DataFrame, competitor: str) -> Optional[CompetitorBehavior]:
        """Analizar frecuencia de cambios de precio"""
        try:
            price_changes = competitor_data['price'].diff().abs()
            change_frequency = (price_changes > 0).sum() / len(price_changes)
            
            return CompetitorBehavior(
                competitor=competitor,
                behavior_type="price_change_frequency",
                frequency=change_frequency,
                price_sensitivity=0.0,
                reaction_time=0.0,
                market_share_impact=0.0,
                description=f"Changes prices {change_frequency:.1%} of the time"
            )
            
        except Exception as e:
            logger.error(f"Error analyzing change frequency: {e}")
            return None
    
    def _analyze_price_sensitivity(self, competitor_data: pd.DataFrame, competitor: str) -> Optional[CompetitorBehavior]:
        """Analizar sensibilidad a precios del mercado"""
        try:
            # Calcular correlación con precios promedio del mercado
            market_avg = competitor_data.groupby('date')['price'].mean()
            competitor_avg = competitor_data.groupby('date')['price'].mean()
            
            if len(market_avg) > 3:
                correlation = np.corrcoef(market_avg, competitor_avg)[0, 1]
                
                return CompetitorBehavior(
                    competitor=competitor,
                    behavior_type="market_price_sensitivity",
                    frequency=0.0,
                    price_sensitivity=abs(correlation),
                    reaction_time=0.0,
                    market_share_impact=0.0,
                    description=f"Price sensitivity to market: {correlation:.2f}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing price sensitivity: {e}")
            return None
    
    def _analyze_reaction_time(self, competitor_data: pd.DataFrame, competitor: str) -> Optional[CompetitorBehavior]:
        """Analizar tiempo de reacción a cambios de mercado"""
        try:
            # Simular análisis de tiempo de reacción
            # En implementación real, analizarías el tiempo entre cambios de mercado y respuesta del competidor
            
            reaction_time = np.random.uniform(1, 7)  # Días
            
            return CompetitorBehavior(
                competitor=competitor,
                behavior_type="market_reaction_time",
                frequency=0.0,
                price_sensitivity=0.0,
                reaction_time=reaction_time,
                market_share_impact=0.0,
                description=f"Average reaction time: {reaction_time:.1f} days"
            )
            
        except Exception as e:
            logger.error(f"Error analyzing reaction time: {e}")
            return None

class AIPricingIntelligence:
    """Sistema principal de inteligencia artificial para precios"""
    
    def __init__(self, db_path: str = "pricing_analysis.db"):
        """Inicializar sistema de IA"""
        self.db_path = db_path
        self.price_predictor = DeepLearningPricePredictor()
        self.pattern_analyzer = PricePatternAnalyzer()
        self.anomaly_detector = MarketAnomalyDetector()
        self.behavior_analyzer = CompetitorBehaviorAnalyzer()
        
        logger.info("AI Pricing Intelligence System initialized")
    
    def run_comprehensive_analysis(self, product_id: str) -> Dict[str, Any]:
        """Ejecutar análisis integral con IA"""
        try:
            # Obtener datos
            df = self._get_product_data(product_id)
            
            if df.empty:
                return {'error': 'No data available for analysis'}
            
            # Análisis de patrones
            patterns = self.pattern_analyzer.detect_patterns(df)
            
            # Detección de anomalías
            anomalies = self.anomaly_detector.detect_anomalies(df)
            
            # Análisis de comportamiento de competidores
            behaviors = self.behavior_analyzer.analyze_behavior(df)
            
            # Predicción de precios con deep learning
            predictions = self._run_price_prediction(df)
            
            # Análisis de correlaciones
            correlations = self._analyze_correlations(df)
            
            # Clustering de competidores
            clusters = self._cluster_competitors(df)
            
            return {
                'product_id': product_id,
                'analysis_date': datetime.now().isoformat(),
                'patterns': [self._pattern_to_dict(p) for p in patterns],
                'anomalies': [self._anomaly_to_dict(a) for a in anomalies],
                'behaviors': [self._behavior_to_dict(b) for b in behaviors],
                'predictions': predictions,
                'correlations': correlations,
                'clusters': clusters,
                'summary': self._generate_ai_summary(patterns, anomalies, behaviors, predictions)
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {'error': str(e)}
    
    def _get_product_data(self, product_id: str) -> pd.DataFrame:
        """Obtener datos del producto"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT product_id, product_name, competitor, price, date_collected
                FROM pricing_data
                WHERE product_id = ?
                AND date_collected >= date('now', '-365 days')
                ORDER BY date_collected
            """
            
            df = pd.read_sql_query(query, conn, params=[product_id])
            conn.close()
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date_collected'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting product data: {e}")
            return pd.DataFrame()
    
    def _run_price_prediction(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Ejecutar predicción de precios"""
        try:
            # Preparar datos
            X, y = self.price_predictor.prepare_data(df)
            
            if len(X) == 0:
                return {'error': 'Insufficient data for prediction'}
            
            # Entrenar modelo
            training_results = self.price_predictor.train(X, y, epochs=50)
            
            if 'error' in training_results:
                return training_results
            
            # Hacer predicciones
            predictions = self.price_predictor.predict(X[-10:])  # Últimas 10 predicciones
            
            return {
                'training_results': training_results,
                'predictions': predictions.tolist(),
                'model_accuracy': 1 - training_results['validation_loss'] / training_results['training_loss']
            }
            
        except Exception as e:
            logger.error(f"Error in price prediction: {e}")
            return {'error': str(e)}
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analizar correlaciones entre competidores"""
        try:
            if 'competitor' not in df.columns:
                return {}
            
            # Crear matriz de precios por competidor
            price_matrix = df.pivot_table(
                index='date',
                columns='competitor',
                values='price',
                aggfunc='mean'
            ).fillna(method='ffill')
            
            # Calcular correlaciones
            correlation_matrix = price_matrix.corr()
            
            # Encontrar correlaciones más fuertes
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            'competitor_1': correlation_matrix.columns[i],
                            'competitor_2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'strong_correlations': strong_correlations,
                'average_correlation': correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            return {}
    
    def _cluster_competitors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Agrupar competidores por comportamiento"""
        try:
            if 'competitor' not in df.columns:
                return {}
            
            # Crear features para clustering
            competitor_features = []
            competitor_names = []
            
            for competitor in df['competitor'].unique():
                competitor_data = df[df['competitor'] == competitor]
                
                if len(competitor_data) > 5:
                    features = [
                        competitor_data['price'].mean(),
                        competitor_data['price'].std(),
                        competitor_data['price'].pct_change().abs().mean(),
                        len(competitor_data)
                    ]
                    
                    competitor_features.append(features)
                    competitor_names.append(competitor)
            
            if len(competitor_features) < 2:
                return {}
            
            # Aplicar clustering
            features_array = np.array(competitor_features)
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_array)
            
            kmeans = KMeans(n_clusters=min(3, len(competitor_names)), random_state=42)
            clusters = kmeans.fit_predict(features_scaled)
            
            # Organizar resultados
            cluster_results = {}
            for i, (name, cluster) in enumerate(zip(competitor_names, clusters)):
                if cluster not in cluster_results:
                    cluster_results[cluster] = []
                cluster_results[cluster].append(name)
            
            return {
                'clusters': cluster_results,
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'inertia': kmeans.inertia_
            }
            
        except Exception as e:
            logger.error(f"Error clustering competitors: {e}")
            return {}
    
    def _pattern_to_dict(self, pattern: PricePattern) -> Dict[str, Any]:
        """Convertir patrón a diccionario"""
        return {
            'type': pattern.pattern_type,
            'confidence': pattern.confidence,
            'start_date': pattern.start_date.isoformat(),
            'end_date': pattern.end_date.isoformat(),
            'price_range': pattern.price_range,
            'frequency': pattern.frequency,
            'description': pattern.description
        }
    
    def _anomaly_to_dict(self, anomaly: MarketAnomaly) -> Dict[str, Any]:
        """Convertir anomalía a diccionario"""
        return {
            'type': anomaly.anomaly_type,
            'severity': anomaly.severity,
            'detected_at': anomaly.detected_at.isoformat(),
            'product_id': anomaly.product_id,
            'competitor': anomaly.competitor,
            'expected_price': anomaly.expected_price,
            'actual_price': anomaly.actual_price,
            'deviation': anomaly.deviation,
            'description': anomaly.description
        }
    
    def _behavior_to_dict(self, behavior: CompetitorBehavior) -> Dict[str, Any]:
        """Convertir comportamiento a diccionario"""
        return {
            'competitor': behavior.competitor,
            'type': behavior.behavior_type,
            'frequency': behavior.frequency,
            'price_sensitivity': behavior.price_sensitivity,
            'reaction_time': behavior.reaction_time,
            'market_share_impact': behavior.market_share_impact,
            'description': behavior.description
        }
    
    def _generate_ai_summary(self, patterns: List[PricePattern], 
                           anomalies: List[MarketAnomaly],
                           behaviors: List[CompetitorBehavior],
                           predictions: Dict[str, Any]) -> str:
        """Generar resumen de IA"""
        summary_parts = []
        
        # Resumen de patrones
        if patterns:
            pattern_types = [p.pattern_type for p in patterns]
            summary_parts.append(f"Detected {len(patterns)} pricing patterns: {', '.join(set(pattern_types))}")
        
        # Resumen de anomalías
        if anomalies:
            high_severity = len([a for a in anomalies if a.severity > 0.5])
            summary_parts.append(f"Found {len(anomalies)} market anomalies ({high_severity} high severity)")
        
        # Resumen de comportamientos
        if behaviors:
            competitors_analyzed = len(set([b.competitor for b in behaviors]))
            summary_parts.append(f"Analyzed behavior of {competitors_analyzed} competitors")
        
        # Resumen de predicciones
        if 'error' not in predictions:
            model_accuracy = predictions.get('model_accuracy', 0)
            summary_parts.append(f"Price prediction model accuracy: {model_accuracy:.1%}")
        
        return ". ".join(summary_parts) + "."

def main():
    """Función principal para demostrar IA de precios"""
    print("=" * 60)
    print("AI PRICING INTELLIGENCE SYSTEM - DEMO")
    print("=" * 60)
    
    # Inicializar sistema de IA
    ai_system = AIPricingIntelligence()
    
    # Ejecutar análisis integral
    print("\nRunning comprehensive AI analysis...")
    analysis = ai_system.run_comprehensive_analysis("product_001")
    
    if 'error' not in analysis:
        print(f"\nAnalysis completed for {analysis['product_id']}")
        print(f"Analysis Date: {analysis['analysis_date']}")
        
        # Mostrar patrones detectados
        print(f"\nPatterns Detected: {len(analysis['patterns'])}")
        for pattern in analysis['patterns']:
            print(f"  - {pattern['type']}: {pattern['description']} (confidence: {pattern['confidence']:.2f})")
        
        # Mostrar anomalías
        print(f"\nAnomalies Found: {len(analysis['anomalies'])}")
        for anomaly in analysis['anomalies']:
            print(f"  - {anomaly['type']}: {anomaly['description']} (severity: {anomaly['severity']:.2f})")
        
        # Mostrar comportamientos
        print(f"\nCompetitor Behaviors: {len(analysis['behaviors'])}")
        for behavior in analysis['behaviors']:
            print(f"  - {behavior['competitor']}: {behavior['description']}")
        
        # Mostrar predicciones
        if 'error' not in analysis['predictions']:
            print(f"\nPrice Predictions:")
            print(f"  - Model Accuracy: {analysis['predictions']['model_accuracy']:.1%}")
            print(f"  - Training Loss: {analysis['predictions']['training_results']['training_loss']:.4f}")
        
        # Mostrar resumen de IA
        print(f"\nAI Summary: {analysis['summary']}")
        
    else:
        print(f"Analysis failed: {analysis['error']}")
    
    print("\n" + "=" * 60)
    print("AI PRICING INTELLIGENCE DEMO COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()






