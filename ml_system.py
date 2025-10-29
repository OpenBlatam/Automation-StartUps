"""
Sistema de Machine Learning Avanzado para Inventario
===================================================

Sistema completo de ML con múltiples algoritmos para predicción,
clasificación y optimización de inventario.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Tipos de modelos ML"""
    DEMAND_FORECASTING = "demand_forecasting"
    PRICE_PREDICTION = "price_prediction"
    STOCK_OPTIMIZATION = "stock_optimization"
    SUPPLIER_CLASSIFICATION = "supplier_classification"
    ANOMALY_DETECTION = "anomaly_detection"
    CUSTOMER_SEGMENTATION = "customer_segmentation"

class AlgorithmType(Enum):
    """Tipos de algoritmos"""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LINEAR_REGRESSION = "linear_regression"
    SVM = "svm"
    NEURAL_NETWORK = "neural_network"
    KMEANS = "kmeans"
    DBSCAN = "dbscan"

@dataclass
class ModelPerformance:
    """Rendimiento del modelo"""
    model_name: str
    algorithm: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mae: float
    mse: float
    rmse: float
    r2_score: float
    training_time: float
    prediction_time: float
    cross_val_score: float
    timestamp: datetime

@dataclass
class PredictionResult:
    """Resultado de predicción"""
    model_name: str
    prediction: Any
    confidence: float
    features_used: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class FeatureEngineer:
    """Ingeniero de características para ML"""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
    
    def create_time_features(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """Crear características temporales"""
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Características temporales básicas
        df['year'] = df[date_column].dt.year
        df['month'] = df[date_column].dt.month
        df['day'] = df[date_column].dt.day
        df['dayofweek'] = df[date_column].dt.dayofweek
        df['dayofyear'] = df[date_column].dt.dayofyear
        df['quarter'] = df[date_column].dt.quarter
        df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
        
        # Características estacionales
        df['is_holiday_season'] = df['month'].isin([11, 12]).astype(int)
        df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
        df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)
        
        # Características cíclicas (usando seno y coseno)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_sin'] = np.sin(2 * np.pi * df['day'] / 31)
        df['day_cos'] = np.cos(2 * np.pi * df['day'] / 31)
        
        return df
    
    def create_lag_features(self, df: pd.DataFrame, target_column: str, lags: List[int]) -> pd.DataFrame:
        """Crear características de retraso"""
        df = df.copy()
        
        for lag in lags:
            df[f'{target_column}_lag_{lag}'] = df[target_column].shift(lag)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, target_column: str, windows: List[int]) -> pd.DataFrame:
        """Crear características de ventana deslizante"""
        df = df.copy()
        
        for window in windows:
            df[f'{target_column}_rolling_mean_{window}'] = df[target_column].rolling(window=window).mean()
            df[f'{target_column}_rolling_std_{window}'] = df[target_column].rolling(window=window).std()
            df[f'{target_column}_rolling_min_{window}'] = df[target_column].rolling(window=window).min()
            df[f'{target_column}_rolling_max_{window}'] = df[target_column].rolling(window=window).max()
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame, feature_pairs: List[Tuple[str, str]]) -> pd.DataFrame:
        """Crear características de interacción"""
        df = df.copy()
        
        for feat1, feat2 in feature_pairs:
            if feat1 in df.columns and feat2 in df.columns:
                df[f'{feat1}_x_{feat2}'] = df[feat1] * df[feat2]
                df[f'{feat1}_div_{feat2}'] = df[feat1] / (df[feat2] + 1e-8)  # Evitar división por cero
        
        return df
    
    def encode_categorical_features(self, df: pd.DataFrame, categorical_columns: List[str]) -> pd.DataFrame:
        """Codificar características categóricas"""
        df = df.copy()
        
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    df[col] = self.encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Manejar valores nuevos
                    unique_values = df[col].astype(str).unique()
                    known_values = self.encoders[col].classes_
                    new_values = set(unique_values) - set(known_values)
                    
                    if new_values:
                        # Agregar nuevos valores al encoder
                        all_values = np.concatenate([known_values, list(new_values)])
                        self.encoders[col] = LabelEncoder()
                        self.encoders[col].fit(all_values)
                    
                    df[col] = self.encoders[col].transform(df[col].astype(str))
        
        return df
    
    def scale_features(self, df: pd.DataFrame, feature_columns: List[str], scaler_type: str = 'standard') -> pd.DataFrame:
        """Escalar características"""
        df = df.copy()
        
        for col in feature_columns:
            if col in df.columns:
                if scaler_type == 'standard':
                    if col not in self.scalers:
                        self.scalers[col] = StandardScaler()
                        df[col] = self.scalers[col].fit_transform(df[[col]]).flatten()
                    else:
                        df[col] = self.scalers[col].transform(df[[col]]).flatten()
                elif scaler_type == 'minmax':
                    if col not in self.scalers:
                        self.scalers[col] = MinMaxScaler()
                        df[col] = self.scalers[col].fit_transform(df[[col]]).flatten()
                    else:
                        df[col] = self.scalers[col].transform(df[[col]]).flatten()
        
        return df
    
    def select_features(self, df: pd.DataFrame, target_column: str, method: str = 'correlation', 
                       n_features: int = 20) -> List[str]:
        """Seleccionar características más importantes"""
        
        if method == 'correlation':
            correlations = df.corr()[target_column].abs().sort_values(ascending=False)
            return correlations.head(n_features + 1).index.tolist()[1:]  # Excluir la columna objetivo
        
        elif method == 'mutual_info':
            from sklearn.feature_selection import mutual_info_regression
            
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            mi_scores = mutual_info_regression(X, y)
            feature_scores = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
            
            return feature_scores.head(n_features).index.tolist()
        
        elif method == 'random_forest':
            from sklearn.ensemble import RandomForestRegressor
            
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            feature_importance = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
            self.feature_importance = feature_importance.to_dict()
            
            return feature_importance.head(n_features).index.tolist()
        
        return df.columns.tolist()

class MLModelManager:
    """Gestor de modelos de Machine Learning"""
    
    def __init__(self, models_dir: str = "ml_models"):
        self.models_dir = models_dir
        self.models = {}
        self.feature_engineer = FeatureEngineer()
        self.model_performance = {}
        
        # Crear directorio si no existe
        import os
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
    
    def prepare_data(self, df: pd.DataFrame, target_column: str, 
                    date_column: Optional[str] = None,
                    categorical_columns: List[str] = None) -> Tuple[pd.DataFrame, List[str]]:
        """Preparar datos para ML"""
        
        df = df.copy()
        
        # Crear características temporales si hay columna de fecha
        if date_column and date_column in df.columns:
            df = self.feature_engineer.create_time_features(df, date_column)
        
        # Crear características de retraso
        if target_column in df.columns:
            df = self.feature_engineer.create_lag_features(df, target_column, [1, 2, 3, 7, 14, 30])
            df = self.feature_engineer.create_rolling_features(df, target_column, [7, 14, 30])
        
        # Codificar características categóricas
        if categorical_columns:
            df = self.feature_engineer.encode_categorical_features(df, categorical_columns)
        
        # Eliminar filas con NaN
        df = df.dropna()
        
        # Seleccionar características
        feature_columns = [col for col in df.columns if col != target_column]
        selected_features = self.feature_engineer.select_features(df, target_column, method='random_forest')
        
        return df, selected_features
    
    def train_demand_forecasting_model(self, df: pd.DataFrame, target_column: str = 'quantity',
                                     date_column: str = 'date', algorithm: AlgorithmType = AlgorithmType.RANDOM_FOREST) -> str:
        """Entrenar modelo de predicción de demanda"""
        
        logger.info(f"Entrenando modelo de predicción de demanda con {algorithm.value}")
        
        # Preparar datos
        df_processed, feature_columns = self.prepare_data(df, target_column, date_column)
        
        X = df_processed[feature_columns]
        y = df_processed[target_column]
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Seleccionar algoritmo
        if algorithm == AlgorithmType.RANDOM_FOREST:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif algorithm == AlgorithmType.GRADIENT_BOOSTING:
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif algorithm == AlgorithmType.LINEAR_REGRESSION:
            model = LinearRegression()
        elif algorithm == AlgorithmType.SVM:
            model = SVR(kernel='rbf')
        elif algorithm == AlgorithmType.NEURAL_NETWORK:
            model = MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        else:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")
        
        # Entrenar modelo
        start_time = datetime.now()
        model.fit(X_train, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Evaluar modelo
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # Validación cruzada
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_absolute_error')
        cv_score = -cv_scores.mean()
        
        # Guardar modelo
        model_name = f"demand_forecasting_{algorithm.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = f"{self.models_dir}/{model_name}.joblib"
        joblib.dump(model, model_path)
        
        # Guardar información del modelo
        model_info = {
            'model_name': model_name,
            'algorithm': algorithm.value,
            'feature_columns': feature_columns,
            'target_column': target_column,
            'date_column': date_column,
            'model_path': model_path,
            'created_at': datetime.now().isoformat(),
            'performance': {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r2_score': r2,
                'cv_score': cv_score,
                'training_time': training_time
            }
        }
        
        self.models[model_name] = model_info
        
        # Guardar información en archivo
        import json
        with open(f"{self.models_dir}/{model_name}_info.json", 'w') as f:
            json.dump(model_info, f, indent=2)
        
        logger.info(f"Modelo {model_name} entrenado exitosamente. MAE: {mae:.2f}, R²: {r2:.2f}")
        
        return model_name
    
    def predict_demand(self, model_name: str, features: Dict[str, Any]) -> PredictionResult:
        """Predecir demanda usando modelo entrenado"""
        
        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} no encontrado")
        
        model_info = self.models[model_name]
        
        # Cargar modelo
        model = joblib.load(model_info['model_path'])
        
        # Preparar características
        feature_df = pd.DataFrame([features])
        
        # Aplicar transformaciones necesarias
        for col in model_info['feature_columns']:
            if col not in feature_df.columns:
                feature_df[col] = 0  # Valor por defecto
        
        X = feature_df[model_info['feature_columns']]
        
        # Hacer predicción
        start_time = datetime.now()
        prediction = model.predict(X)[0]
        prediction_time = (datetime.now() - start_time).total_seconds()
        
        # Calcular confianza (basado en la varianza del modelo)
        if hasattr(model, 'predict_proba'):
            confidence = model.predict_proba(X)[0].max()
        else:
            # Para regresión, usar la desviación estándar de las predicciones del conjunto
            if hasattr(model, 'estimators_'):
                predictions = [estimator.predict(X)[0] for estimator in model.estimators_]
                confidence = 1 - (np.std(predictions) / (np.mean(predictions) + 1e-8))
            else:
                confidence = 0.8  # Valor por defecto
        
        return PredictionResult(
            model_name=model_name,
            prediction=prediction,
            confidence=confidence,
            features_used=model_info['feature_columns'],
            timestamp=datetime.now(),
            metadata={
                'algorithm': model_info['algorithm'],
                'prediction_time': prediction_time
            }
        )
    
    def train_supplier_classification_model(self, df: pd.DataFrame, target_column: str = 'supplier_rating',
                                          categorical_columns: List[str] = None) -> str:
        """Entrenar modelo de clasificación de proveedores"""
        
        logger.info("Entrenando modelo de clasificación de proveedores")
        
        # Preparar datos
        df_processed, feature_columns = self.prepare_data(df, target_column, categorical_columns=categorical_columns)
        
        X = df_processed[feature_columns]
        y = df_processed[target_column]
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        start_time = datetime.now()
        model.fit(X_train, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Evaluar modelo
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Guardar modelo
        model_name = f"supplier_classification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = f"{self.models_dir}/{model_name}.joblib"
        joblib.dump(model, model_path)
        
        # Guardar información del modelo
        model_info = {
            'model_name': model_name,
            'algorithm': 'random_forest_classifier',
            'feature_columns': feature_columns,
            'target_column': target_column,
            'model_path': model_path,
            'created_at': datetime.now().isoformat(),
            'performance': {
                'accuracy': accuracy,
                'classification_report': report,
                'training_time': training_time
            }
        }
        
        self.models[model_name] = model_info
        
        logger.info(f"Modelo de clasificación {model_name} entrenado. Accuracy: {accuracy:.2f}")
        
        return model_name
    
    def detect_anomalies(self, df: pd.DataFrame, columns: List[str], 
                        algorithm: AlgorithmType = AlgorithmType.DBSCAN) -> pd.DataFrame:
        """Detectar anomalías en los datos"""
        
        logger.info(f"Detectando anomalías usando {algorithm.value}")
        
        # Preparar datos
        df_processed = df[columns].copy()
        df_processed = df_processed.dropna()
        
        # Escalar características
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_processed)
        
        # Aplicar algoritmo de detección de anomalías
        if algorithm == AlgorithmType.DBSCAN:
            model = DBSCAN(eps=0.5, min_samples=5)
            clusters = model.fit_predict(scaled_data)
            
            # Marcar anomalías (cluster -1)
            df_processed['is_anomaly'] = clusters == -1
            df_processed['cluster'] = clusters
            
        elif algorithm == AlgorithmType.KMEANS:
            model = KMeans(n_clusters=3, random_state=42)
            clusters = model.fit_predict(scaled_data)
            
            # Calcular distancias al centroide más cercano
            distances = model.transform(scaled_data)
            min_distances = np.min(distances, axis=1)
            
            # Marcar como anomalía si la distancia es mayor al percentil 95
            threshold = np.percentile(min_distances, 95)
            df_processed['is_anomaly'] = min_distances > threshold
            df_processed['cluster'] = clusters
            df_processed['distance_to_centroid'] = min_distances
        
        return df_processed
    
    def optimize_hyperparameters(self, df: pd.DataFrame, target_column: str, 
                                algorithm: AlgorithmType) -> Dict[str, Any]:
        """Optimizar hiperparámetros del modelo"""
        
        logger.info(f"Optimizando hiperparámetros para {algorithm.value}")
        
        # Preparar datos
        df_processed, feature_columns = self.prepare_data(df, target_column)
        
        X = df_processed[feature_columns]
        y = df_processed[target_column]
        
        # Definir grilla de parámetros según el algoritmo
        if algorithm == AlgorithmType.RANDOM_FOREST:
            model = RandomForestRegressor(random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        elif algorithm == AlgorithmType.GRADIENT_BOOSTING:
            model = GradientBoostingRegressor(random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 0.9, 1.0]
            }
        else:
            raise ValueError(f"Optimización de hiperparámetros no soportada para {algorithm}")
        
        # Búsqueda en grilla
        grid_search = GridSearchCV(
            model, param_grid, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1
        )
        
        start_time = datetime.now()
        grid_search.fit(X, y)
        optimization_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': -grid_search.best_score_,
            'optimization_time': optimization_time,
            'cv_results': grid_search.cv_results_
        }
    
    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen del rendimiento de todos los modelos"""
        
        summary = {
            'total_models': len(self.models),
            'models': {},
            'best_performing_model': None,
            'average_performance': {}
        }
        
        if not self.models:
            return summary
        
        # Calcular métricas promedio
        mae_scores = []
        r2_scores = []
        accuracies = []
        
        for model_name, model_info in self.models.items():
            performance = model_info.get('performance', {})
            summary['models'][model_name] = {
                'algorithm': model_info['algorithm'],
                'created_at': model_info['created_at'],
                'performance': performance
            }
            
            if 'mae' in performance:
                mae_scores.append(performance['mae'])
            if 'r2_score' in performance:
                r2_scores.append(performance['r2_score'])
            if 'accuracy' in performance:
                accuracies.append(performance['accuracy'])
        
        # Calcular promedios
        if mae_scores:
            summary['average_performance']['mae'] = np.mean(mae_scores)
        if r2_scores:
            summary['average_performance']['r2_score'] = np.mean(r2_scores)
        if accuracies:
            summary['average_performance']['accuracy'] = np.mean(accuracies)
        
        # Encontrar mejor modelo
        if mae_scores:
            best_model = min(self.models.keys(), 
                            key=lambda x: self.models[x]['performance'].get('mae', float('inf')))
            summary['best_performing_model'] = best_model
        
        return summary
    
    def load_model(self, model_name: str):
        """Cargar modelo desde archivo"""
        if model_name in self.models:
            model_info = self.models[model_name]
            model = joblib.load(model_info['model_path'])
            return model, model_info
        else:
            raise ValueError(f"Modelo {model_name} no encontrado")
    
    def delete_model(self, model_name: str):
        """Eliminar modelo"""
        if model_name in self.models:
            model_info = self.models[model_name]
            
            # Eliminar archivos
            import os
            if os.path.exists(model_info['model_path']):
                os.remove(model_info['model_path'])
            
            info_path = f"{self.models_dir}/{model_name}_info.json"
            if os.path.exists(info_path):
                os.remove(info_path)
            
            # Eliminar de diccionario
            del self.models[model_name]
            
            logger.info(f"Modelo {model_name} eliminado")
        else:
            raise ValueError(f"Modelo {model_name} no encontrado")

# Instancia global del gestor de ML
ml_manager = MLModelManager()

# Funciones de conveniencia
def train_demand_model(df: pd.DataFrame, algorithm: AlgorithmType = AlgorithmType.RANDOM_FOREST) -> str:
    """Entrenar modelo de demanda"""
    return ml_manager.train_demand_forecasting_model(df, algorithm=algorithm)

def predict_demand(model_name: str, features: Dict[str, Any]) -> PredictionResult:
    """Predecir demanda"""
    return ml_manager.predict_demand(model_name, features)

def detect_data_anomalies(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Detectar anomalías en datos"""
    return ml_manager.detect_anomalies(df, columns)

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de Machine Learning...")
    
    # Crear datos de ejemplo
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    df = pd.DataFrame({
        'date': dates,
        'quantity': np.random.poisson(50, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 10,
        'price': np.random.normal(100, 10, len(dates)),
        'category': np.random.choice(['A', 'B', 'C'], len(dates)),
        'supplier_id': np.random.choice(['SUP1', 'SUP2', 'SUP3'], len(dates))
    })
    
    # Entrenar modelo de demanda
    model_name = train_demand_model(df)
    print(f"Modelo entrenado: {model_name}")
    
    # Hacer predicción
    features = {
        'year': 2024,
        'month': 1,
        'day': 15,
        'dayofweek': 1,
        'is_weekend': 0,
        'quantity_lag_1': 45,
        'quantity_lag_7': 52,
        'quantity_rolling_mean_7': 48
    }
    
    prediction = predict_demand(model_name, features)
    print(f"Predicción: {prediction.prediction:.2f} (confianza: {prediction.confidence:.2f})")
    
    # Detectar anomalías
    anomaly_df = detect_data_anomalies(df, ['quantity', 'price'])
    anomalies = anomaly_df[anomaly_df['is_anomaly']]
    print(f"Anomalías detectadas: {len(anomalies)}")
    
    # Resumen de rendimiento
    summary = ml_manager.get_model_performance_summary()
    print(f"Resumen de modelos: {summary['total_models']} modelos entrenados")
    
    print("✅ Sistema de Machine Learning funcionando correctamente")



