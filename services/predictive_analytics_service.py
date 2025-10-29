from datetime import datetime, timedelta
from app import db
from models import Product, SalesRecord, InventoryRecord, Alert
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import os
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

@dataclass
class TimeSeriesModel:
    """Modelo de series temporales"""
    name: str
    model: object
    scaler: object
    accuracy: float
    mae: float
    rmse: float
    trained_at: datetime
    features_used: List[str]
    model_type: str  # 'arima', 'lstm', 'prophet', 'ensemble'

@dataclass
class ForecastResult:
    """Resultado de pronóstico"""
    product_id: int
    forecast_periods: int
    predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    model_used: str
    accuracy: float
    generated_at: datetime
    metadata: Dict

class AdvancedPredictiveAnalyticsService:
    """Servicio avanzado de análisis predictivo"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.models_dir = 'predictive_models'
        self.forecast_history = []
        
        # Crear directorio para modelos si no existe
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def prepare_time_series_data(self, product_id: int = None, days_back: int = 365) -> pd.DataFrame:
        """Prepara datos de series temporales"""
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
            
            # Preparar DataFrame con datos diarios
            data = []
            for sale in sales_data:
                data.append({
                    'date': sale.sale_date.date(),
                    'product_id': sale.product_id,
                    'quantity_sold': sale.quantity_sold,
                    'unit_price': sale.unit_price,
                    'total_amount': sale.total_amount
                })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Agrupar por fecha y producto
            daily_sales = df.groupby(['date', 'product_id']).agg({
                'quantity_sold': 'sum',
                'unit_price': 'mean',
                'total_amount': 'sum'
            }).reset_index()
            
            # Crear serie temporal completa
            date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
            
            # Para cada producto, crear serie temporal completa
            time_series_data = []
            for product_id in daily_sales['product_id'].unique():
                product_sales = daily_sales[daily_sales['product_id'] == product_id]
                
                # Crear serie temporal completa
                ts_df = pd.DataFrame({'date': date_range})
                ts_df = ts_df.merge(product_sales, on='date', how='left')
                ts_df['product_id'] = product_id
                ts_df['quantity_sold'] = ts_df['quantity_sold'].fillna(0)
                ts_df['unit_price'] = ts_df['unit_price'].fillna(method='ffill')
                ts_df['total_amount'] = ts_df['total_amount'].fillna(0)
                
                # Añadir características temporales
                ts_df['day_of_week'] = ts_df['date'].dt.dayofweek
                ts_df['day_of_month'] = ts_df['date'].dt.day
                ts_df['month'] = ts_df['date'].dt.month
                ts_df['quarter'] = ts_df['date'].dt.quarter
                ts_df['year'] = ts_df['date'].dt.year
                ts_df['is_weekend'] = ts_df['day_of_week'].isin([5, 6])
                ts_df['is_month_start'] = ts_df['day_of_month'] <= 7
                ts_df['is_month_end'] = ts_df['day_of_month'] >= 25
                
                # Características cíclicas
                ts_df['sin_day_of_year'] = np.sin(2 * np.pi * ts_df['date'].dt.dayofyear / 365.25)
                ts_df['cos_day_of_year'] = np.cos(2 * np.pi * ts_df['date'].dt.dayofyear / 365.25)
                ts_df['sin_month'] = np.sin(2 * np.pi * ts_df['month'] / 12)
                ts_df['cos_month'] = np.cos(2 * np.pi * ts_df['month'] / 12)
                
                # Estadísticas móviles
                for window in [7, 14, 30]:
                    ts_df[f'ma_{window}'] = ts_df['quantity_sold'].rolling(window=window, min_periods=1).mean()
                    ts_df[f'std_{window}'] = ts_df['quantity_sold'].rolling(window=window, min_periods=1).std()
                    ts_df[f'max_{window}'] = ts_df['quantity_sold'].rolling(window=window, min_periods=1).max()
                    ts_df[f'min_{window}'] = ts_df['quantity_sold'].rolling(window=window, min_periods=1).min()
                
                # Lag features
                for lag in [1, 2, 3, 7, 14]:
                    ts_df[f'lag_{lag}'] = ts_df['quantity_sold'].shift(lag)
                
                time_series_data.append(ts_df)
            
            if time_series_data:
                return pd.concat(time_series_data, ignore_index=True)
            else:
                return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f'Error preparando datos de series temporales: {str(e)}')
            return pd.DataFrame()
    
    def train_time_series_models(self, product_id: int = None) -> Dict:
        """Entrena modelos de series temporales"""
        try:
            # Preparar datos
            df = self.prepare_time_series_data(product_id)
            
            if df.empty:
                return {'error': 'No hay datos suficientes para entrenar'}
            
            # Seleccionar características
            feature_columns = [col for col in df.columns if col not in [
                'date', 'product_id', 'quantity_sold', 'unit_price', 'total_amount'
            ]]
            
            # Entrenar modelos para cada producto
            models_trained = {}
            
            for pid in df['product_id'].unique():
                product_data = df[df['product_id'] == pid].copy()
                
                if len(product_data) < 30:  # Necesitamos al menos 30 días de datos
                    continue
                
                # Preparar características y objetivo
                X = product_data[feature_columns].fillna(0)
                y = product_data['quantity_sold']
                
                # Dividir datos temporalmente
                split_point = int(len(X) * 0.8)
                X_train, X_test = X[:split_point], X[split_point:]
                y_train, y_test = y[:split_point], y[split_point:]
                
                # Normalizar características
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Entrenar múltiples modelos
                models = {
                    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
                    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                    'Linear Regression': LinearRegression(),
                    'Ridge Regression': Ridge(alpha=1.0),
                    'Lasso Regression': Lasso(alpha=0.1),
                    'SVR': SVR(kernel='rbf', C=1.0, gamma='scale')
                }
                
                product_models = {}
                
                for name, model in models.items():
                    try:
                        # Entrenar modelo
                        model.fit(X_train_scaled, y_train)
                        
                        # Predecir
                        y_pred = model.predict(X_test_scaled)
                        
                        # Calcular métricas
                        mae = mean_absolute_error(y_test, y_pred)
                        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                        r2 = r2_score(y_test, y_pred)
                        
                        # Crear modelo de serie temporal
                        ts_model = TimeSeriesModel(
                            name=name,
                            model=model,
                            scaler=scaler,
                            accuracy=r2,
                            mae=mae,
                            rmse=rmse,
                            trained_at=datetime.utcnow(),
                            features_used=feature_columns,
                            model_type='ensemble'
                        )
                        
                        product_models[name] = ts_model
                        
                        self.logger.info(f'Modelo {name} entrenado para producto {pid} - R²: {r2:.3f}, MAE: {mae:.3f}')
                        
                    except Exception as e:
                        self.logger.error(f'Error entrenando modelo {name} para producto {pid}: {str(e)}')
                
                if product_models:
                    models_trained[pid] = product_models
            
            # Guardar modelos
            self.models.update(models_trained)
            self._save_models(models_trained)
            
            return {
                'success': True,
                'models_trained': len(models_trained),
                'products': list(models_trained.keys()),
                'total_models': sum(len(models) for models in models_trained.values())
            }
            
        except Exception as e:
            self.logger.error(f'Error entrenando modelos de series temporales: {str(e)}')
            return {'error': str(e)}
    
    def generate_forecast(self, product_id: int, periods: int = 30) -> Dict:
        """Genera pronóstico para un producto"""
        try:
            # Buscar mejor modelo para el producto
            if product_id not in self.models:
                return {'error': 'No hay modelos entrenados para este producto'}
            
            product_models = self.models[product_id]
            if not product_models:
                return {'error': 'No hay modelos disponibles para este producto'}
            
            # Seleccionar mejor modelo basado en R²
            best_model_name = max(product_models.keys(), key=lambda k: product_models[k].accuracy)
            best_model = product_models[best_model_name]
            
            # Preparar datos recientes
            df = self.prepare_time_series_data(product_id, days_back=90)
            if df.empty:
                return {'error': 'No hay datos suficientes para pronóstico'}
            
            product_data = df[df['product_id'] == product_id].copy()
            if len(product_data) < 7:
                return {'error': 'Datos insuficientes para pronóstico'}
            
            # Obtener características más recientes
            feature_columns = best_model.features_used
            last_features = product_data[feature_columns].iloc[-1:].fillna(0)
            
            # Preprocesar características
            features_scaled = best_model.scaler.transform(last_features)
            
            # Generar pronósticos
            predictions = []
            confidence_intervals = []
            
            for period in range(1, periods + 1):
                # Predecir
                prediction = best_model.model.predict(features_scaled)[0]
                predictions.append(max(0, prediction))  # No permitir valores negativos
                
                # Calcular intervalo de confianza (simplificado)
                std_error = best_model.rmse
                confidence_interval = (
                    max(0, prediction - 1.96 * std_error),
                    prediction + 1.96 * std_error
                )
                confidence_intervals.append(confidence_interval)
            
            # Crear resultado de pronóstico
            forecast_result = ForecastResult(
                product_id=product_id,
                forecast_periods=periods,
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                model_used=best_model_name,
                accuracy=best_model.accuracy,
                generated_at=datetime.utcnow(),
                metadata={
                    'mae': best_model.mae,
                    'rmse': best_model.rmse,
                    'features_count': len(feature_columns)
                }
            )
            
            # Guardar en historial
            self.forecast_history.append(forecast_result)
            
            return {
                'success': True,
                'product_id': product_id,
                'forecast_periods': periods,
                'predictions': predictions,
                'confidence_intervals': confidence_intervals,
                'model_used': best_model_name,
                'accuracy': best_model.accuracy,
                'total_predicted_demand': sum(predictions),
                'average_daily_demand': sum(predictions) / len(predictions),
                'generated_at': forecast_result.generated_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f'Error generando pronóstico: {str(e)}')
            return {'error': str(e)}
    
    def analyze_demand_patterns(self, product_id: int = None) -> Dict:
        """Analiza patrones de demanda"""
        try:
            df = self.prepare_time_series_data(product_id, days_back=180)
            
            if df.empty:
                return {'error': 'No hay datos suficientes para análisis'}
            
            analysis_results = {}
            
            for pid in df['product_id'].unique():
                product_data = df[df['product_id'] == pid].copy()
                
                if len(product_data) < 30:
                    continue
                
                # Análisis de tendencia
                product_data['trend'] = product_data['quantity_sold'].rolling(window=7).mean()
                recent_trend = product_data['trend'].tail(14).mean()
                historical_trend = product_data['trend'].head(14).mean()
                trend_change = (recent_trend - historical_trend) / historical_trend if historical_trend > 0 else 0
                
                # Análisis de estacionalidad
                monthly_sales = product_data.groupby('month')['quantity_sold'].mean()
                seasonality_ratio = monthly_sales.max() / monthly_sales.min() if monthly_sales.min() > 0 else 1
                
                # Análisis de volatilidad
                volatility = product_data['quantity_sold'].std() / product_data['quantity_sold'].mean() if product_data['quantity_sold'].mean() > 0 else 0
                
                # Análisis de autocorrelación
                autocorr_7 = product_data['quantity_sold'].autocorr(lag=7)
                autocorr_30 = product_data['quantity_sold'].autocorr(lag=30)
                
                # Detectar patrones
                patterns = []
                
                if abs(trend_change) > 0.2:
                    patterns.append({
                        'type': 'trend',
                        'description': f'Tendencia {"creciente" if trend_change > 0 else "decreciente"} del {abs(trend_change)*100:.1f}%',
                        'strength': min(abs(trend_change), 1.0)
                    })
                
                if seasonality_ratio > 2.0:
                    patterns.append({
                        'type': 'seasonality',
                        'description': f'Estacionalidad fuerte (ratio: {seasonality_ratio:.1f})',
                        'strength': min((seasonality_ratio - 1) / 3, 1.0)
                    })
                
                if volatility > 0.5:
                    patterns.append({
                        'type': 'volatility',
                        'description': f'Alta volatilidad (CV: {volatility:.2f})',
                        'strength': min(volatility, 1.0)
                    })
                
                if abs(autocorr_7) > 0.3:
                    patterns.append({
                        'type': 'autocorrelation',
                        'description': f'Autocorrelación semanal fuerte ({autocorr_7:.2f})',
                        'strength': abs(autocorr_7)
                    })
                
                analysis_results[pid] = {
                    'trend_change': trend_change,
                    'seasonality_ratio': seasonality_ratio,
                    'volatility': volatility,
                    'autocorr_7': autocorr_7,
                    'autocorr_30': autocorr_30,
                    'patterns': patterns,
                    'data_points': len(product_data)
                }
            
            return {
                'success': True,
                'analysis': analysis_results,
                'total_products': len(analysis_results)
            }
            
        except Exception as e:
            self.logger.error(f'Error analizando patrones de demanda: {str(e)}')
            return {'error': str(e)}
    
    def detect_anomalies_advanced(self, product_id: int = None) -> Dict:
        """Detecta anomalías avanzadas en series temporales"""
        try:
            df = self.prepare_time_series_data(product_id, days_back=90)
            
            if df.empty:
                return {'error': 'No hay datos suficientes para detección de anomalías'}
            
            anomalies = []
            
            for pid in df['product_id'].unique():
                product_data = df[df['product_id'] == pid].copy()
                
                if len(product_data) < 14:
                    continue
                
                # Calcular estadísticas móviles
                product_data['ma_7'] = product_data['quantity_sold'].rolling(window=7).mean()
                product_data['std_7'] = product_data['quantity_sold'].rolling(window=7).std()
                
                # Detectar anomalías usando Z-score
                product_data['z_score'] = (product_data['quantity_sold'] - product_data['ma_7']) / product_data['std_7']
                
                # Anomalías por Z-score
                z_anomalies = product_data[abs(product_data['z_score']) > 2.5]
                
                for _, row in z_anomalies.iterrows():
                    anomalies.append({
                        'product_id': pid,
                        'date': row['date'].isoformat(),
                        'value': row['quantity_sold'],
                        'expected': row['ma_7'],
                        'z_score': row['z_score'],
                        'type': 'statistical',
                        'severity': 'high' if abs(row['z_score']) > 3 else 'medium'
                    })
                
                # Detectar cambios bruscos
                product_data['change'] = product_data['quantity_sold'].pct_change()
                sudden_changes = product_data[abs(product_data['change']) > 0.5]
                
                for _, row in sudden_changes.iterrows():
                    anomalies.append({
                        'product_id': pid,
                        'date': row['date'].isoformat(),
                        'value': row['quantity_sold'],
                        'change': row['change'],
                        'type': 'sudden_change',
                        'severity': 'high' if abs(row['change']) > 1.0 else 'medium'
                    })
            
            return {
                'success': True,
                'anomalies': anomalies,
                'total_anomalies': len(anomalies),
                'high_severity': len([a for a in anomalies if a['severity'] == 'high'])
            }
            
        except Exception as e:
            self.logger.error(f'Error detectando anomalías avanzadas: {str(e)}')
            return {'error': str(e)}
    
    def get_model_performance(self) -> Dict:
        """Obtiene rendimiento de los modelos"""
        try:
            performance = {}
            
            for product_id, product_models in self.models.items():
                performance[product_id] = {}
                
                for model_name, model in product_models.items():
                    performance[product_id][model_name] = {
                        'accuracy': model.accuracy,
                        'mae': model.mae,
                        'rmse': model.rmse,
                        'trained_at': model.trained_at.isoformat(),
                        'features_count': len(model.features_used)
                    }
            
            return {
                'success': True,
                'performance': performance,
                'total_products': len(self.models),
                'total_models': sum(len(models) for models in self.models.values())
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo rendimiento de modelos: {str(e)}')
            return {'error': str(e)}
    
    def get_forecast_history(self) -> List[Dict]:
        """Obtiene historial de pronósticos"""
        try:
            history_data = []
            
            for forecast in self.forecast_history[-50:]:  # Últimos 50 pronósticos
                history_data.append({
                    'product_id': forecast.product_id,
                    'forecast_periods': forecast.forecast_periods,
                    'model_used': forecast.model_used,
                    'accuracy': forecast.accuracy,
                    'total_predicted_demand': sum(forecast.predictions),
                    'generated_at': forecast.generated_at.isoformat(),
                    'metadata': forecast.metadata
                })
            
            return history_data
            
        except Exception as e:
            self.logger.error(f'Error obteniendo historial de pronósticos: {str(e)}')
            return []
    
    def _save_models(self, models: Dict):
        """Guarda modelos entrenados"""
        try:
            for product_id, product_models in models.items():
                for model_name, model in product_models.items():
                    model_data = {
                        'name': model.name,
                        'accuracy': model.accuracy,
                        'mae': model.mae,
                        'rmse': model.rmse,
                        'trained_at': model.trained_at.isoformat(),
                        'features_used': model.features_used,
                        'model_type': model.model_type
                    }
                    
                    # Guardar metadatos
                    metadata_path = os.path.join(self.models_dir, f"product_{product_id}_{model_name}_metadata.json")
                    with open(metadata_path, 'w') as f:
                        json.dump(model_data, f, indent=2)
                    
                    # Guardar modelo
                    model_path = os.path.join(self.models_dir, f"product_{product_id}_{model_name}_model.pkl")
                    with open(model_path, 'wb') as f:
                        pickle.dump(model.model, f)
                    
                    # Guardar scaler
                    scaler_path = os.path.join(self.models_dir, f"product_{product_id}_{model_name}_scaler.pkl")
                    with open(scaler_path, 'wb') as f:
                        pickle.dump(model.scaler, f)
                    
                    self.logger.info(f'Modelo {model_name} para producto {product_id} guardado exitosamente')
                
        except Exception as e:
            self.logger.error(f'Error guardando modelos: {str(e)}')

# Instancia global del servicio de análisis predictivo
advanced_predictive_analytics_service = AdvancedPredictiveAnalyticsService()



