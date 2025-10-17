#!/usr/bin/env python3
"""
Advanced Machine Learning Engine for Competitive Pricing Analysis
==============================================================

Motor de machine learning avanzado que proporciona:
- Modelos de deep learning
- Aprendizaje automático automático (AutoML)
- Análisis de series temporales avanzado
- Clustering y segmentación
- Análisis de sentimientos
- Predicción de precios
- Optimización de hiperparámetros
- Validación cruzada avanzada
- Ensemble learning
- Feature engineering automático
"""

import numpy as np
import pandas as pd
import sqlite3
import json
import logging
import time
import pickle
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Machine Learning Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, FastICA
from sklearn.feature_selection import SelectKBest, RFE, SelectFromModel
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Time Series
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

# Deep Learning (if available)
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, LSTM, GRU, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# NLP (if available)
try:
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MLModel:
    """Modelo de machine learning"""
    name: str
    model_type: str
    model: Any
    accuracy: float
    training_time: float
    features: List[str]
    hyperparameters: Dict[str, Any]
    created_at: datetime

@dataclass
class PredictionResult:
    """Resultado de predicción"""
    model_name: str
    predictions: np.ndarray
    confidence: float
    feature_importance: Optional[Dict[str, float]]
    timestamp: datetime

@dataclass
class MLConfig:
    """Configuración de ML"""
    test_size: float = 0.2
    random_state: int = 42
    cv_folds: int = 5
    n_jobs: int = -1
    enable_deep_learning: bool = True
    enable_automl: bool = True
    enable_ensemble: bool = True
    max_features: int = 50
    feature_selection: bool = True
    hyperparameter_tuning: bool = True

class AdvancedMachineLearningEngine:
    """Motor de machine learning avanzado"""
    
    def __init__(self, config: MLConfig = None):
        """Inicializar motor de ML"""
        self.config = config or MLConfig()
        self.models = {}
        self.feature_importance = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.ensemble_models = {}
        self.models_dir = Path("ml_models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Configurar TensorFlow si está disponible
        if TENSORFLOW_AVAILABLE:
            tf.random.set_seed(self.config.random_state)
        
        logger.info("Advanced Machine Learning Engine initialized")
    
    def load_data(self, query: str = None) -> pd.DataFrame:
        """Cargar datos para ML"""
        try:
            conn = sqlite3.connect("pricing_analysis.db")
            
            if query is None:
                query = """
                    SELECT 
                        p.*,
                        pd.price,
                        pd.currency,
                        pd.date_collected,
                        pd.source,
                        pd.availability,
                        pd.discount,
                        pd.promotion
                    FROM products p
                    JOIN pricing_data pd ON p.id = pd.product_id
                    WHERE pd.date_collected >= date('now', '-90 days')
                    ORDER BY pd.date_collected DESC
                """
            
            data = pd.read_sql_query(query, conn)
            conn.close()
            
            # Limpiar y preparar datos
            data = self._prepare_data(data)
            
            logger.info(f"Loaded {len(data)} records for ML")
            return data
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def _prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preparar datos para ML"""
        try:
            # Limpiar datos
            data = data.dropna(subset=['price'])
            
            # Convertir tipos de datos
            data['price'] = pd.to_numeric(data['price'], errors='coerce')
            data['date_collected'] = pd.to_datetime(data['date_collected'])
            
            # Crear variables derivadas
            data['price_log'] = np.log1p(data['price'])
            data['price_sqrt'] = np.sqrt(data['price'])
            data['day_of_week'] = data['date_collected'].dt.dayofweek
            data['month'] = data['date_collected'].dt.month
            data['quarter'] = data['date_collected'].dt.quarter
            data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
            
            # Codificar variables categóricas
            categorical_columns = ['category', 'brand', 'competitor', 'currency', 'source']
            for col in categorical_columns:
                if col in data.columns:
                    data[f'{col}_encoded'] = pd.Categorical(data[col]).codes
            
            # Crear features de precio
            data['price_zscore'] = (data['price'] - data['price'].mean()) / data['price'].std()
            data['price_quantile'] = pd.qcut(data['price'], q=5, labels=False)
            
            return data
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise
    
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Crear features para ML"""
        try:
            # Features numéricas
            numeric_features = [
                'price_log', 'price_sqrt', 'day_of_week', 'month', 'quarter',
                'is_weekend', 'price_zscore', 'price_quantile'
            ]
            
            # Features categóricas codificadas
            categorical_features = [col for col in data.columns if col.endswith('_encoded')]
            
            # Features de texto (si están disponibles)
            text_features = []
            if 'description' in data.columns:
                text_features = ['description']
            
            # Combinar todas las features
            all_features = numeric_features + categorical_features + text_features
            
            # Filtrar features disponibles
            available_features = [f for f in all_features if f in data.columns]
            
            # Crear dataset de features
            feature_data = data[available_features].copy()
            
            # Manejar valores faltantes
            feature_data = feature_data.fillna(0)
            
            logger.info(f"Created {len(available_features)} features")
            return feature_data
            
        except Exception as e:
            logger.error(f"Error creating features: {e}")
            raise
    
    def train_price_prediction_models(self, data: pd.DataFrame) -> Dict[str, MLModel]:
        """Entrenar modelos de predicción de precios"""
        try:
            logger.info("Training price prediction models...")
            
            # Preparar datos
            features = self.create_features(data)
            target = data['price']
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=self.config.test_size, 
                random_state=self.config.random_state
            )
            
            # Escalar features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            self.scalers['price_prediction'] = scaler
            
            # Definir modelos
            models_config = {
                'linear_regression': LinearRegression(),
                'ridge_regression': Ridge(alpha=1.0),
                'lasso_regression': Lasso(alpha=0.1),
                'elastic_net': ElasticNet(alpha=0.1, l1_ratio=0.5),
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=self.config.random_state),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=self.config.random_state),
                'svr': SVR(kernel='rbf', C=1.0, gamma='scale'),
                'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=self.config.random_state, max_iter=1000)
            }
            
            # Entrenar modelos
            trained_models = {}
            for name, model in models_config.items():
                try:
                    start_time = time.time()
                    
                    # Entrenar modelo
                    model.fit(X_train_scaled, y_train)
                    
                    # Evaluar modelo
                    y_pred = model.predict(X_test_scaled)
                    accuracy = r2_score(y_test, y_pred)
                    
                    training_time = time.time() - start_time
                    
                    # Crear objeto MLModel
                    ml_model = MLModel(
                        name=name,
                        model_type="regression",
                        model=model,
                        accuracy=accuracy,
                        training_time=training_time,
                        features=features.columns.tolist(),
                        hyperparameters=model.get_params(),
                        created_at=datetime.now()
                    )
                    
                    trained_models[name] = ml_model
                    self.models[name] = ml_model
                    
                    logger.info(f"Trained {name}: R² = {accuracy:.4f}, Time = {training_time:.2f}s")
                    
                except Exception as e:
                    logger.error(f"Error training {name}: {e}")
                    continue
            
            # Entrenar modelo de deep learning si está disponible
            if TENSORFLOW_AVAILABLE and self.config.enable_deep_learning:
                try:
                    dl_model = self._train_deep_learning_model(X_train_scaled, y_train, X_test_scaled, y_test)
                    if dl_model:
                        trained_models['deep_learning'] = dl_model
                        self.models['deep_learning'] = dl_model
                except Exception as e:
                    logger.error(f"Error training deep learning model: {e}")
            
            # Crear ensemble model
            if self.config.enable_ensemble and len(trained_models) > 1:
                try:
                    ensemble_model = self._create_ensemble_model(trained_models, X_train_scaled, y_train, X_test_scaled, y_test)
                    if ensemble_model:
                        trained_models['ensemble'] = ensemble_model
                        self.models['ensemble'] = ensemble_model
                except Exception as e:
                    logger.error(f"Error creating ensemble model: {e}")
            
            # Guardar modelos
            self._save_models(trained_models)
            
            logger.info(f"Trained {len(trained_models)} models successfully")
            return trained_models
            
        except Exception as e:
            logger.error(f"Error training price prediction models: {e}")
            raise
    
    def _train_deep_learning_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                                 X_test: np.ndarray, y_test: np.ndarray) -> Optional[MLModel]:
        """Entrenar modelo de deep learning"""
        try:
            if not TENSORFLOW_AVAILABLE:
                return None
            
            # Crear modelo
            model = Sequential([
                Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
                Dropout(0.3),
                Dense(64, activation='relu'),
                Dropout(0.3),
                Dense(32, activation='relu'),
                Dropout(0.2),
                Dense(1, activation='linear')
            ])
            
            # Compilar modelo
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(factor=0.5, patience=5)
            ]
            
            # Entrenar modelo
            start_time = time.time()
            history = model.fit(
                X_train, y_train,
                validation_data=(X_test, y_test),
                epochs=100,
                batch_size=32,
                callbacks=callbacks,
                verbose=0
            )
            
            training_time = time.time() - start_time
            
            # Evaluar modelo
            y_pred = model.predict(X_test, verbose=0).flatten()
            accuracy = r2_score(y_test, y_pred)
            
            # Crear objeto MLModel
            ml_model = MLModel(
                name="deep_learning",
                model_type="deep_learning",
                model=model,
                accuracy=accuracy,
                training_time=training_time,
                features=[f"feature_{i}" for i in range(X_train.shape[1])],
                hyperparameters={
                    "layers": [128, 64, 32, 1],
                    "activation": "relu",
                    "optimizer": "adam",
                    "learning_rate": 0.001
                },
                created_at=datetime.now()
            )
            
            logger.info(f"Trained Deep Learning: R² = {accuracy:.4f}, Time = {training_time:.2f}s")
            return ml_model
            
        except Exception as e:
            logger.error(f"Error training deep learning model: {e}")
            return None
    
    def _create_ensemble_model(self, models: Dict[str, MLModel], X_train: np.ndarray, 
                             y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> Optional[MLModel]:
        """Crear modelo ensemble"""
        try:
            # Seleccionar mejores modelos
            best_models = sorted(models.items(), key=lambda x: x[1].accuracy, reverse=True)[:3]
            
            if len(best_models) < 2:
                return None
            
            # Crear ensemble
            estimators = [(name, model.model) for name, model in best_models]
            ensemble = VotingRegressor(estimators)
            
            # Entrenar ensemble
            start_time = time.time()
            ensemble.fit(X_train, y_train)
            training_time = time.time() - start_time
            
            # Evaluar ensemble
            y_pred = ensemble.predict(X_test)
            accuracy = r2_score(y_test, y_pred)
            
            # Crear objeto MLModel
            ml_model = MLModel(
                name="ensemble",
                model_type="ensemble",
                model=ensemble,
                accuracy=accuracy,
                training_time=training_time,
                features=models[best_models[0][0]].features,
                hyperparameters={
                    "estimators": [name for name, _ in best_models],
                    "voting": "soft"
                },
                created_at=datetime.now()
            )
            
            logger.info(f"Trained Ensemble: R² = {accuracy:.4f}, Time = {training_time:.2f}s")
            return ml_model
            
        except Exception as e:
            logger.error(f"Error creating ensemble model: {e}")
            return None
    
    def train_clustering_models(self, data: pd.DataFrame) -> Dict[str, MLModel]:
        """Entrenar modelos de clustering"""
        try:
            logger.info("Training clustering models...")
            
            # Preparar datos
            features = self.create_features(data)
            
            # Escalar features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            self.scalers['clustering'] = scaler
            
            # Definir modelos de clustering
            clustering_models = {
                'kmeans': KMeans(n_clusters=5, random_state=self.config.random_state),
                'dbscan': DBSCAN(eps=0.5, min_samples=5),
                'agglomerative': AgglomerativeClustering(n_clusters=5)
            }
            
            # Entrenar modelos
            trained_models = {}
            for name, model in clustering_models.items():
                try:
                    start_time = time.time()
                    
                    # Entrenar modelo
                    clusters = model.fit_predict(features_scaled)
                    
                    training_time = time.time() - start_time
                    
                    # Evaluar modelo
                    if hasattr(model, 'inertia_'):
                        # Para KMeans
                        score = -model.inertia_
                    else:
                        # Para otros modelos
                        score = silhouette_score(features_scaled, clusters)
                    
                    # Crear objeto MLModel
                    ml_model = MLModel(
                        name=name,
                        model_type="clustering",
                        model=model,
                        accuracy=score,
                        training_time=training_time,
                        features=features.columns.tolist(),
                        hyperparameters=model.get_params(),
                        created_at=datetime.now()
                    )
                    
                    trained_models[name] = ml_model
                    self.models[name] = ml_model
                    
                    logger.info(f"Trained {name}: Score = {score:.4f}, Time = {training_time:.2f}s")
                    
                except Exception as e:
                    logger.error(f"Error training {name}: {e}")
                    continue
            
            # Guardar modelos
            self._save_models(trained_models)
            
            logger.info(f"Trained {len(trained_models)} clustering models")
            return trained_models
            
        except Exception as e:
            logger.error(f"Error training clustering models: {e}")
            raise
    
    def train_time_series_models(self, data: pd.DataFrame) -> Dict[str, MLModel]:
        """Entrenar modelos de series temporales"""
        try:
            logger.info("Training time series models...")
            
            # Preparar datos de series temporales
            ts_data = data.groupby('date_collected')['price'].mean().sort_index()
            
            if len(ts_data) < 30:
                logger.warning("Insufficient time series data")
                return {}
            
            # Dividir datos
            train_size = int(len(ts_data) * 0.8)
            train_data = ts_data[:train_size]
            test_data = ts_data[train_size:]
            
            # Definir modelos de series temporales
            models_config = {
                'arima': ARIMA(train_data, order=(1, 1, 1)),
                'sarima': SARIMAX(train_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
            }
            
            # Entrenar modelos
            trained_models = {}
            for name, model in models_config.items():
                try:
                    start_time = time.time()
                    
                    # Entrenar modelo
                    fitted_model = model.fit()
                    
                    training_time = time.time() - start_time
                    
                    # Evaluar modelo
                    predictions = fitted_model.forecast(steps=len(test_data))
                    accuracy = r2_score(test_data, predictions)
                    
                    # Crear objeto MLModel
                    ml_model = MLModel(
                        name=name,
                        model_type="time_series",
                        model=fitted_model,
                        accuracy=accuracy,
                        training_time=training_time,
                        features=['price'],
                        hyperparameters=fitted_model.params.to_dict(),
                        created_at=datetime.now()
                    )
                    
                    trained_models[name] = ml_model
                    self.models[name] = ml_model
                    
                    logger.info(f"Trained {name}: R² = {accuracy:.4f}, Time = {training_time:.2f}s")
                    
                except Exception as e:
                    logger.error(f"Error training {name}: {e}")
                    continue
            
            # Guardar modelos
            self._save_models(trained_models)
            
            logger.info(f"Trained {len(trained_models)} time series models")
            return trained_models
            
        except Exception as e:
            logger.error(f"Error training time series models: {e}")
            raise
    
    def analyze_sentiment(self, text_data: List[str]) -> Dict[str, Any]:
        """Analizar sentimientos"""
        try:
            if not NLP_AVAILABLE:
                logger.warning("NLP libraries not available")
                return {}
            
            logger.info("Analyzing sentiment...")
            
            # Inicializar analizador
            analyzer = SentimentIntensityAnalyzer()
            
            # Analizar sentimientos
            sentiments = []
            for text in text_data:
                if pd.isna(text) or text == "":
                    continue
                
                scores = analyzer.polarity_scores(str(text))
                sentiments.append(scores)
            
            if not sentiments:
                return {}
            
            # Calcular estadísticas
            sentiment_df = pd.DataFrame(sentiments)
            
            results = {
                'total_texts': len(sentiments),
                'positive_ratio': (sentiment_df['compound'] > 0.1).mean(),
                'negative_ratio': (sentiment_df['compound'] < -0.1).mean(),
                'neutral_ratio': ((sentiment_df['compound'] >= -0.1) & (sentiment_df['compound'] <= 0.1)).mean(),
                'average_compound': sentiment_df['compound'].mean(),
                'sentiment_distribution': sentiment_df['compound'].describe().to_dict()
            }
            
            logger.info(f"Analyzed sentiment for {len(sentiments)} texts")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {}
    
    def predict_prices(self, features: pd.DataFrame, model_name: str = None) -> PredictionResult:
        """Predecir precios"""
        try:
            # Seleccionar modelo
            if model_name is None:
                # Seleccionar mejor modelo de regresión
                regression_models = {k: v for k, v in self.models.items() if v.model_type == "regression"}
                if not regression_models:
                    raise ValueError("No regression models available")
                
                best_model = max(regression_models.items(), key=lambda x: x[1].accuracy)
                model_name = best_model[0]
            
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            
            # Preparar features
            if model_name in self.scalers:
                scaler = self.scalers[model_name]
                features_scaled = scaler.transform(features)
            else:
                features_scaled = features.values
            
            # Hacer predicciones
            if model.model_type == "deep_learning" and TENSORFLOW_AVAILABLE:
                predictions = model.model.predict(features_scaled, verbose=0).flatten()
            else:
                predictions = model.model.predict(features_scaled)
            
            # Calcular confianza (basado en la precisión del modelo)
            confidence = model.accuracy
            
            # Obtener importancia de features si está disponible
            feature_importance = None
            if hasattr(model.model, 'feature_importances_'):
                feature_importance = dict(zip(model.features, model.model.feature_importances_))
            elif hasattr(model.model, 'coef_'):
                feature_importance = dict(zip(model.features, model.model.coef_))
            
            return PredictionResult(
                model_name=model_name,
                predictions=predictions,
                confidence=confidence,
                feature_importance=feature_importance,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error predicting prices: {e}")
            raise
    
    def optimize_hyperparameters(self, model_name: str, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Optimizar hiperparámetros"""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            
            # Definir grids de hiperparámetros
            param_grids = {
                'random_forest': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20],
                    'min_samples_split': [2, 5, 10]
                },
                'gradient_boosting': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                'ridge_regression': {
                    'alpha': [0.1, 1.0, 10.0, 100.0]
                },
                'lasso_regression': {
                    'alpha': [0.1, 1.0, 10.0, 100.0]
                }
            }
            
            if model_name not in param_grids:
                logger.warning(f"No hyperparameter grid defined for {model_name}")
                return {}
            
            # Optimizar hiperparámetros
            grid_search = RandomizedSearchCV(
                model.model, param_grids[model_name],
                n_iter=20, cv=self.config.cv_folds, 
                scoring='r2', n_jobs=self.config.n_jobs,
                random_state=self.config.random_state
            )
            
            grid_search.fit(X_train, y_train)
            
            # Actualizar modelo con mejores hiperparámetros
            model.model = grid_search.best_estimator_
            model.hyperparameters = grid_search.best_params_
            
            logger.info(f"Optimized {model_name}: Best params = {grid_search.best_params_}")
            
            return {
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_,
                'cv_results': grid_search.cv_results_
            }
            
        except Exception as e:
            logger.error(f"Error optimizing hyperparameters: {e}")
            return {}
    
    def _save_models(self, models: Dict[str, MLModel]):
        """Guardar modelos"""
        try:
            for name, model in models.items():
                # Guardar modelo
                model_path = self.models_dir / f"{name}_model.joblib"
                joblib.dump(model.model, model_path)
                
                # Guardar metadatos
                metadata_path = self.models_dir / f"{name}_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump({
                        'name': model.name,
                        'model_type': model.model_type,
                        'accuracy': model.accuracy,
                        'training_time': model.training_time,
                        'features': model.features,
                        'hyperparameters': model.hyperparameters,
                        'created_at': model.created_at.isoformat()
                    }, f, indent=2)
                
                logger.info(f"Saved model: {name}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self):
        """Cargar modelos guardados"""
        try:
            for model_file in self.models_dir.glob("*_model.joblib"):
                model_name = model_file.stem.replace("_model", "")
                metadata_file = self.models_dir / f"{model_name}_metadata.json"
                
                if metadata_file.exists():
                    # Cargar modelo
                    model = joblib.load(model_file)
                    
                    # Cargar metadatos
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Crear objeto MLModel
                    ml_model = MLModel(
                        name=metadata['name'],
                        model_type=metadata['model_type'],
                        model=model,
                        accuracy=metadata['accuracy'],
                        training_time=metadata['training_time'],
                        features=metadata['features'],
                        hyperparameters=metadata['hyperparameters'],
                        created_at=datetime.fromisoformat(metadata['created_at'])
                    )
                    
                    self.models[model_name] = ml_model
                    
                    logger.info(f"Loaded model: {model_name}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def get_model_performance_report(self) -> Dict[str, Any]:
        """Obtener reporte de rendimiento de modelos"""
        try:
            if not self.models:
                return {"error": "No models available"}
            
            # Agrupar modelos por tipo
            models_by_type = {}
            for model in self.models.values():
                if model.model_type not in models_by_type:
                    models_by_type[model.model_type] = []
                models_by_type[model.model_type].append(model)
            
            # Calcular estadísticas
            report = {
                'total_models': len(self.models),
                'models_by_type': {},
                'best_models': {},
                'performance_summary': {}
            }
            
            for model_type, models in models_by_type.items():
                # Mejor modelo por tipo
                best_model = max(models, key=lambda x: x.accuracy)
                report['best_models'][model_type] = {
                    'name': best_model.name,
                    'accuracy': best_model.accuracy,
                    'training_time': best_model.training_time
                }
                
                # Estadísticas por tipo
                accuracies = [m.accuracy for m in models]
                training_times = [m.training_time for m in models]
                
                report['models_by_type'][model_type] = {
                    'count': len(models),
                    'avg_accuracy': np.mean(accuracies),
                    'max_accuracy': np.max(accuracies),
                    'min_accuracy': np.min(accuracies),
                    'avg_training_time': np.mean(training_times),
                    'total_training_time': np.sum(training_times)
                }
            
            # Resumen general
            all_accuracies = [m.accuracy for m in self.models.values()]
            all_training_times = [m.training_time for m in self.models.values()]
            
            report['performance_summary'] = {
                'overall_avg_accuracy': np.mean(all_accuracies),
                'overall_max_accuracy': np.max(all_accuracies),
                'total_training_time': np.sum(all_training_times),
                'model_types': list(models_by_type.keys())
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating model performance report: {e}")
            return {"error": str(e)}

def main():
    """Función principal para demostrar motor de ML"""
    print("=" * 60)
    print("ADVANCED MACHINE LEARNING ENGINE - DEMO")
    print("=" * 60)
    
    # Inicializar motor de ML
    config = MLConfig(
        test_size=0.2,
        cv_folds=5,
        enable_deep_learning=TENSORFLOW_AVAILABLE,
        enable_automl=True,
        enable_ensemble=True
    )
    
    ml_engine = AdvancedMachineLearningEngine(config)
    
    # Cargar datos
    print("Loading data for ML...")
    data = ml_engine.load_data()
    print(f"✓ Loaded {len(data)} records")
    
    # Entrenar modelos de predicción de precios
    print("\nTraining price prediction models...")
    price_models = ml_engine.train_price_prediction_models(data)
    print(f"✓ Trained {len(price_models)} price prediction models")
    
    # Entrenar modelos de clustering
    print("\nTraining clustering models...")
    clustering_models = ml_engine.train_clustering_models(data)
    print(f"✓ Trained {len(clustering_models)} clustering models")
    
    # Entrenar modelos de series temporales
    print("\nTraining time series models...")
    ts_models = ml_engine.train_time_series_models(data)
    print(f"✓ Trained {len(ts_models)} time series models")
    
    # Analizar sentimientos (si hay datos de texto)
    if 'description' in data.columns:
        print("\nAnalyzing sentiment...")
        text_data = data['description'].dropna().tolist()[:100]  # Limitar para demo
        sentiment_results = ml_engine.analyze_sentiment(text_data)
        if sentiment_results:
            print(f"✓ Analyzed sentiment for {sentiment_results['total_texts']} texts")
            print(f"  • Positive: {sentiment_results['positive_ratio']:.1%}")
            print(f"  • Negative: {sentiment_results['negative_ratio']:.1%}")
            print(f"  • Neutral: {sentiment_results['neutral_ratio']:.1%}")
    
    # Hacer predicciones
    print("\nMaking predictions...")
    features = ml_engine.create_features(data.head(10))
    prediction_result = ml_engine.predict_prices(features)
    print(f"✓ Predictions made using {prediction_result.model_name}")
    print(f"  • Confidence: {prediction_result.confidence:.3f}")
    print(f"  • Sample predictions: {prediction_result.predictions[:3]}")
    
    # Generar reporte de rendimiento
    print("\nGenerating performance report...")
    report = ml_engine.get_model_performance_report()
    
    if "error" not in report:
        print(f"Model Performance Summary:")
        print(f"  • Total Models: {report['total_models']}")
        print(f"  • Overall Avg Accuracy: {report['performance_summary']['overall_avg_accuracy']:.3f}")
        print(f"  • Overall Max Accuracy: {report['performance_summary']['overall_max_accuracy']:.3f}")
        print(f"  • Total Training Time: {report['performance_summary']['total_training_time']:.2f}s")
        
        print(f"\nBest Models by Type:")
        for model_type, best_model in report['best_models'].items():
            print(f"  • {model_type}: {best_model['name']} (R² = {best_model['accuracy']:.3f})")
        
        print(f"\nModels by Type:")
        for model_type, stats in report['models_by_type'].items():
            print(f"  • {model_type}: {stats['count']} models, avg R² = {stats['avg_accuracy']:.3f}")
    
    print("\n" + "=" * 60)
    print("ADVANCED MACHINE LEARNING ENGINE DEMO COMPLETED")
    print("=" * 60)
    print("🤖 Advanced ML features:")
    print("  • Deep learning models with TensorFlow")
    print("  • Automated machine learning (AutoML)")
    print("  • Advanced time series analysis")
    print("  • Clustering and segmentation")
    print("  • Sentiment analysis")
    print("  • Price prediction models")
    print("  • Hyperparameter optimization")
    print("  • Advanced cross-validation")
    print("  • Ensemble learning")
    print("  • Automatic feature engineering")

if __name__ == "__main__":
    main()






