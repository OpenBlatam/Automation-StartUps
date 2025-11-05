from datetime import datetime, timedelta
from app import db
from models import Product, SalesRecord, InventoryRecord
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging
from typing import Dict, List, Tuple, Optional
import joblib
import os
import json

class AdvancedMLService:
    """Servicio avanzado de Machine Learning para predicción de demanda"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.model_performance = {}
        self.models_dir = 'ml_models'
        
        # Crear directorio para modelos si no existe
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def prepare_training_data(self, product_id: int = None, days_back: int = 365) -> pd.DataFrame:
        """Prepara datos de entrenamiento para los modelos ML"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Obtener datos de ventas
            if product_id:
                sales_query = SalesRecord.query.filter(
                    SalesRecord.product_id == product_id,
                    SalesRecord.sale_date >= start_date,
                    SalesRecord.sale_date <= end_date
                )
            else:
                sales_query = SalesRecord.query.filter(
                    SalesRecord.sale_date >= start_date,
                    SalesRecord.sale_date <= end_date
                )
            
            sales_data = sales_query.all()
            
            if not sales_data:
                return pd.DataFrame()
            
            # Preparar DataFrame
            data = []
            for sale in sales_data:
                data.append({
                    'date': sale.sale_date,
                    'product_id': sale.product_id,
                    'product_name': sale.product.name,
                    'category': sale.product.category,
                    'quantity_sold': sale.quantity_sold,
                    'unit_price': sale.unit_price,
                    'total_amount': sale.total_amount,
                    'day_of_week': sale.sale_date.weekday(),
                    'day_of_month': sale.sale_date.day,
                    'month': sale.sale_date.month,
                    'quarter': (sale.sale_date.month - 1) // 3 + 1,
                    'is_weekend': sale.sale_date.weekday() >= 5,
                    'is_month_start': sale.sale_date.day <= 7,
                    'is_month_end': sale.sale_date.day >= 25,
                    'year': sale.sale_date.year
                })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Agregar características adicionales
            df = self._add_time_features(df)
            df = self._add_lag_features(df)
            df = self._add_rolling_features(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f'Error preparando datos de entrenamiento: {str(e)}')
            return pd.DataFrame()
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade características temporales"""
        try:
            # Características cíclicas
            df['sin_day_of_year'] = np.sin(2 * np.pi * df['date'].dt.dayofyear / 365)
            df['cos_day_of_year'] = np.cos(2 * np.pi * df['date'].dt.dayofyear / 365)
            df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12)
            df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12)
            
            # Indicadores de temporada
            df['is_holiday_season'] = df['month'].isin([11, 12])  # Nov-Dic
            df['is_summer'] = df['month'].isin([6, 7, 8])  # Jun-Ago
            df['is_winter'] = df['month'].isin([12, 1, 2])  # Dic-Ene-Feb
            
            return df
        except Exception as e:
            self.logger.error(f'Error añadiendo características temporales: {str(e)}')
            return df
    
    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade características de retraso (lag features)"""
        try:
            # Agrupar por producto para calcular lags
            df_sorted = df.sort_values(['product_id', 'date'])
            
            # Lags de cantidad vendida
            for lag in [1, 3, 7, 14, 30]:
                df_sorted[f'quantity_lag_{lag}'] = df_sorted.groupby('product_id')['quantity_sold'].shift(lag)
            
            # Lags de precio
            for lag in [1, 7, 30]:
                df_sorted[f'price_lag_{lag}'] = df_sorted.groupby('product_id')['unit_price'].shift(lag)
            
            return df_sorted
        except Exception as e:
            self.logger.error(f'Error añadiendo características de retraso: {str(e)}')
            return df
    
    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade características de ventana deslizante"""
        try:
            # Promedios móviles
            for window in [3, 7, 14, 30]:
                df[f'quantity_ma_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(
                    window=window, min_periods=1
                ).mean().reset_index(0, drop=True)
                
                df[f'price_ma_{window}'] = df.groupby('product_id')['unit_price'].rolling(
                    window=window, min_periods=1
                ).mean().reset_index(0, drop=True)
            
            # Desviación estándar móvil
            for window in [7, 30]:
                df[f'quantity_std_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(
                    window=window, min_periods=1
                ).std().reset_index(0, drop=True)
            
            return df
        except Exception as e:
            self.logger.error(f'Error añadiendo características de ventana deslizante: {str(e)}')
            return df
    
    def train_models(self, product_id: int = None, test_size: float = 0.2) -> Dict:
        """Entrena múltiples modelos de ML"""
        try:
            # Preparar datos
            df = self.prepare_training_data(product_id)
            
            if df.empty:
                return {'error': 'No hay datos suficientes para entrenar'}
            
            # Seleccionar características
            feature_columns = [
                'day_of_week', 'day_of_month', 'month', 'quarter',
                'is_weekend', 'is_month_start', 'is_month_end',
                'sin_day_of_year', 'cos_day_of_year', 'sin_month', 'cos_month',
                'is_holiday_season', 'is_summer', 'is_winter'
            ]
            
            # Añadir características de lag y rolling si existen
            lag_columns = [col for col in df.columns if 'lag_' in col or 'ma_' in col or 'std_' in col]
            feature_columns.extend(lag_columns)
            
            # Filtrar características que existen en el DataFrame
            feature_columns = [col for col in feature_columns if col in df.columns]
            
            # Preparar datos de entrenamiento
            X = df[feature_columns].fillna(0)
            y = df['quantity_sold']
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, shuffle=False
            )
            
            # Normalizar características
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Definir modelos
            models = {
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
                'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'LinearRegression': LinearRegression(),
                'Ridge': Ridge(alpha=1.0),
                'Lasso': Lasso(alpha=0.1),
                'SVR': SVR(kernel='rbf', C=1.0, gamma='scale')
            }
            
            # Entrenar modelos
            results = {}
            for name, model in models.items():
                try:
                    # Usar datos escalados para modelos que lo requieren
                    if name in ['LinearRegression', 'Ridge', 'Lasso', 'SVR']:
                        model.fit(X_train_scaled, y_train)
                        y_pred = model.predict(X_test_scaled)
                    else:
                        model.fit(X_train, y_train)
                        y_pred = model.predict(X_test)
                    
                    # Calcular métricas
                    mae = mean_absolute_error(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    rmse = np.sqrt(mse)
                    r2 = r2_score(y_test, y_pred)
                    
                    results[name] = {
                        'model': model,
                        'mae': mae,
                        'mse': mse,
                        'rmse': rmse,
                        'r2': r2,
                        'predictions': y_pred.tolist(),
                        'actual': y_test.tolist()
                    }
                    
                    # Guardar modelo si es el mejor
                    if not self.model_performance or r2 > self.model_performance.get('best_r2', 0):
                        self.model_performance = {
                            'best_model': name,
                            'best_r2': r2,
                            'best_mae': mae
                        }
                        
                        # Guardar modelo
                        self._save_model(model, scaler, name, product_id)
                    
                except Exception as e:
                    self.logger.error(f'Error entrenando modelo {name}: {str(e)}')
                    results[name] = {'error': str(e)}
            
            # Guardar resultados
            self.models = results
            self.scalers[product_id or 'global'] = scaler
            
            return {
                'models_trained': len([r for r in results.values() if 'error' not in r]),
                'best_model': self.model_performance.get('best_model'),
                'best_r2': self.model_performance.get('best_r2'),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f'Error entrenando modelos: {str(e)}')
            return {'error': str(e)}
    
    def predict_demand(self, product_id: int, days_ahead: int = 30) -> Dict:
        """Predice la demanda futura usando el mejor modelo"""
        try:
            # Cargar modelo si no está en memoria
            model_info = self._load_best_model(product_id)
            if not model_info:
                return {'error': 'No hay modelo entrenado para este producto'}
            
            model = model_info['model']
            scaler = model_info['scaler']
            
            # Preparar datos recientes
            df = self.prepare_training_data(product_id, days_back=90)
            if df.empty:
                return {'error': 'No hay datos suficientes para predicción'}
            
            # Obtener las últimas características
            feature_columns = [col for col in df.columns if col not in ['date', 'product_id', 'product_name', 'category', 'quantity_sold', 'unit_price', 'total_amount']]
            last_features = df[feature_columns].iloc[-1:].fillna(0)
            
            # Generar predicciones para los próximos días
            predictions = []
            dates = []
            
            for day in range(1, days_ahead + 1):
                # Crear características para el día futuro
                future_date = datetime.utcnow() + timedelta(days=day)
                
                # Actualizar características temporales
                future_features = last_features.copy()
                future_features['day_of_week'] = future_date.weekday()
                future_features['day_of_month'] = future_date.day
                future_features['month'] = future_date.month
                future_features['quarter'] = (future_date.month - 1) // 3 + 1
                future_features['is_weekend'] = future_date.weekday() >= 5
                future_features['is_month_start'] = future_date.day <= 7
                future_features['is_month_end'] = future_date.day >= 25
                future_features['year'] = future_date.year
                
                # Características cíclicas
                future_features['sin_day_of_year'] = np.sin(2 * np.pi * future_date.timetuple().tm_yday / 365)
                future_features['cos_day_of_year'] = np.cos(2 * np.pi * future_date.timetuple().tm_yday / 365)
                future_features['sin_month'] = np.sin(2 * np.pi * future_date.month / 12)
                future_features['cos_month'] = np.cos(2 * np.pi * future_date.month / 12)
                
                # Indicadores de temporada
                future_features['is_holiday_season'] = future_date.month in [11, 12]
                future_features['is_summer'] = future_date.month in [6, 7, 8]
                future_features['is_winter'] = future_date.month in [12, 1, 2]
                
                # Predecir
                if hasattr(model, 'predict'):
                    if model_info['model_name'] in ['LinearRegression', 'Ridge', 'Lasso', 'SVR']:
                        future_features_scaled = scaler.transform(future_features)
                        prediction = model.predict(future_features_scaled)[0]
                    else:
                        prediction = model.predict(future_features)[0]
                    
                    predictions.append(max(0, prediction))  # No permitir valores negativos
                    dates.append(future_date.strftime('%Y-%m-%d'))
            
            return {
                'product_id': product_id,
                'predictions': predictions,
                'dates': dates,
                'model_used': model_info['model_name'],
                'confidence': model_info.get('r2', 0),
                'total_predicted_demand': sum(predictions),
                'average_daily_demand': sum(predictions) / len(predictions)
            }
            
        except Exception as e:
            self.logger.error(f'Error prediciendo demanda: {str(e)}')
            return {'error': str(e)}
    
    def get_model_performance(self, product_id: int = None) -> Dict:
        """Obtiene el rendimiento de los modelos"""
        try:
            if not self.models:
                return {'error': 'No hay modelos entrenados'}
            
            performance = {}
            for model_name, result in self.models.items():
                if 'error' not in result:
                    performance[model_name] = {
                        'r2_score': result['r2'],
                        'mae': result['mae'],
                        'rmse': result['rmse']
                    }
            
            return performance
            
        except Exception as e:
            self.logger.error(f'Error obteniendo rendimiento de modelos: {str(e)}')
            return {'error': str(e)}
    
    def _save_model(self, model, scaler, model_name: str, product_id: int = None):
        """Guarda el modelo entrenado"""
        try:
            key = f"{model_name}_{product_id or 'global'}"
            
            # Guardar modelo
            model_path = os.path.join(self.models_dir, f"{key}_model.pkl")
            joblib.dump(model, model_path)
            
            # Guardar scaler
            scaler_path = os.path.join(self.models_dir, f"{key}_scaler.pkl")
            joblib.dump(scaler, scaler_path)
            
            # Guardar metadatos
            metadata = {
                'model_name': model_name,
                'product_id': product_id,
                'trained_at': datetime.utcnow().isoformat(),
                'model_path': model_path,
                'scaler_path': scaler_path
            }
            
            metadata_path = os.path.join(self.models_dir, f"{key}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
            
            self.logger.info(f'Modelo {model_name} guardado para producto {product_id}')
            
        except Exception as e:
            self.logger.error(f'Error guardando modelo: {str(e)}')
    
    def _load_best_model(self, product_id: int = None) -> Optional[Dict]:
        """Carga el mejor modelo entrenado"""
        try:
            # Buscar metadatos del mejor modelo
            metadata_files = [f for f in os.listdir(self.models_dir) if f.endswith('_metadata.json')]
            
            best_model = None
            best_r2 = 0
            
            for metadata_file in metadata_files:
                metadata_path = os.path.join(self.models_dir, metadata_file)
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Cargar modelo y evaluar
                model_path = metadata['model_path']
                scaler_path = metadata['scaler_path']
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    model = joblib.load(model_path)
                    scaler = joblib.load(scaler_path)
                    
                    # Evaluar modelo (simplificado)
                    r2 = self._evaluate_model(model, scaler, product_id)
                    
                    if r2 > best_r2:
                        best_r2 = r2
                        best_model = {
                            'model': model,
                            'scaler': scaler,
                            'model_name': metadata['model_name'],
                            'r2': r2
                        }
            
            return best_model
            
        except Exception as e:
            self.logger.error(f'Error cargando mejor modelo: {str(e)}')
            return None
    
    def _evaluate_model(self, model, scaler, product_id: int = None) -> float:
        """Evalúa un modelo y retorna el R² score"""
        try:
            # Preparar datos de prueba
            df = self.prepare_training_data(product_id, days_back=30)
            if df.empty:
                return 0.0
            
            # Seleccionar características
            feature_columns = [col for col in df.columns if col not in ['date', 'product_id', 'product_name', 'category', 'quantity_sold', 'unit_price', 'total_amount']]
            X = df[feature_columns].fillna(0)
            y = df['quantity_sold']
            
            # Predecir
            if hasattr(model, 'predict'):
                if hasattr(model, 'coef_') or hasattr(model, 'support_vectors_'):  # Modelos lineales o SVR
                    X_scaled = scaler.transform(X)
                    y_pred = model.predict(X_scaled)
                else:
                    y_pred = model.predict(X)
                
                # Calcular R²
                r2 = r2_score(y, y_pred)
                return max(0, r2)  # No permitir valores negativos
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f'Error evaluando modelo: {str(e)}')
            return 0.0
    
    def get_feature_importance(self, product_id: int = None) -> Dict:
        """Obtiene la importancia de las características"""
        try:
            if not self.models:
                return {'error': 'No hay modelos entrenados'}
            
            importance = {}
            for model_name, result in self.models.items():
                if 'error' not in result and hasattr(result['model'], 'feature_importances_'):
                    importance[model_name] = result['model'].feature_importances_.tolist()
            
            return importance
            
        except Exception as e:
            self.logger.error(f'Error obteniendo importancia de características: {str(e)}')
            return {'error': str(e)}

# Instancia global del servicio de ML
advanced_ml_service = AdvancedMLService()



