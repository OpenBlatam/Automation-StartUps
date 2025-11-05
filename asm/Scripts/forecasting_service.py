import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from app import db
from models import Product, SalesRecord, DemandForecast
import logging
from typing import List, Dict, Tuple

class DemandForecastingService:
    """Servicio de previsión de demanda usando múltiples algoritmos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def forecast_demand(self, product_id: int, days_ahead: int = 30, method: str = 'auto') -> Dict:
        """
        Predice la demanda futura para un producto
        
        Args:
            product_id: ID del producto
            days_ahead: Días hacia adelante para predecir
            method: Método de predicción ('auto', 'moving_average', 'exponential_smoothing', 'linear_regression')
        
        Returns:
            Dict con predicciones y métricas de precisión
        """
        try:
            # Obtener datos históricos de ventas
            sales_data = self.get_sales_history(product_id)
            
            if len(sales_data) < 7:  # Mínimo de datos requeridos
                return self._fallback_forecast(product_id, days_ahead)
            
            # Preparar datos para análisis
            df = self._prepare_dataframe(sales_data)
            
            # Seleccionar mejor método si es 'auto'
            if method == 'auto':
                method = self._select_best_method(df)
            
            # Generar predicciones según el método seleccionado
            if method == 'moving_average':
                predictions = self._moving_average_forecast(df, days_ahead)
            elif method == 'exponential_smoothing':
                predictions = self._exponential_smoothing_forecast(df, days_ahead)
            elif method == 'linear_regression':
                predictions = self._linear_regression_forecast(df, days_ahead)
            else:
                predictions = self._moving_average_forecast(df, days_ahead)
            
            # Calcular métricas de precisión
            accuracy_metrics = self._calculate_accuracy_metrics(df, predictions)
            
            # Guardar predicciones en la base de datos
            self._save_forecasts(product_id, predictions, method)
            
            return {
                'product_id': product_id,
                'method_used': method,
                'predictions': predictions,
                'accuracy_metrics': accuracy_metrics,
                'forecast_period': days_ahead,
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f'Error en previsión de demanda para producto {product_id}: {str(e)}')
            return self._fallback_forecast(product_id, days_ahead)
    
    def get_sales_history(self, product_id: int, days_back: int = 90) -> List[Dict]:
        """Obtiene historial de ventas de un producto"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            sales_records = SalesRecord.query.filter(
                SalesRecord.product_id == product_id,
                SalesRecord.sale_date >= start_date
            ).order_by(SalesRecord.sale_date).all()
            
            return [
                {
                    'date': record.sale_date,
                    'quantity': record.quantity_sold,
                    'price': record.unit_price
                }
                for record in sales_records
            ]
            
        except Exception as e:
            self.logger.error(f'Error al obtener historial de ventas: {str(e)}')
            return []
    
    def _prepare_dataframe(self, sales_data: List[Dict]) -> pd.DataFrame:
        """Prepara DataFrame para análisis"""
        df = pd.DataFrame(sales_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Agrupar por día y sumar cantidades
        daily_sales = df['quantity'].resample('D').sum().fillna(0)
        
        return daily_sales.to_frame('quantity')
    
    def _select_best_method(self, df: pd.DataFrame) -> str:
        """Selecciona el mejor método basado en datos históricos"""
        try:
            if len(df) < 14:
                return 'moving_average'
            
            # Dividir datos para validación
            train_size = int(len(df) * 0.8)
            train_data = df[:train_size]
            test_data = df[train_size:]
            
            methods = ['moving_average', 'exponential_smoothing', 'linear_regression']
            best_method = 'moving_average'
            best_error = float('inf')
            
            for method in methods:
                try:
                    if method == 'moving_average':
                        predictions = self._moving_average_forecast(train_data, len(test_data))
                    elif method == 'exponential_smoothing':
                        predictions = self._moving_average_forecast(train_data, len(test_data))
                    elif method == 'linear_regression':
                        predictions = self._linear_regression_forecast(train_data, len(test_data))
                    
                    # Calcular error
                    actual = test_data['quantity'].values
                    predicted = predictions[:len(actual)]
                    
                    if len(predicted) == len(actual):
                        mae = mean_absolute_error(actual, predicted)
                        if mae < best_error:
                            best_error = mae
                            best_method = method
                            
                except Exception as e:
                    self.logger.warning(f'Error evaluando método {method}: {str(e)}')
                    continue
            
            return best_method
            
        except Exception as e:
            self.logger.error(f'Error seleccionando mejor método: {str(e)}')
            return 'moving_average'
    
    def _moving_average_forecast(self, df: pd.DataFrame, days_ahead: int) -> List[float]:
        """Predicción usando media móvil"""
        try:
            window_size = min(7, len(df) // 2)  # Ventana de 7 días o la mitad de los datos
            if window_size < 2:
                window_size = 2
            
            # Calcular media móvil
            moving_avg = df['quantity'].rolling(window=window_size).mean()
            last_avg = moving_avg.iloc[-1]
            
            # Generar predicciones (asumiendo tendencia estable)
            predictions = [last_avg] * days_ahead
            
            return predictions
            
        except Exception as e:
            self.logger.error(f'Error en media móvil: {str(e)}')
            return [0] * days_ahead
    
    def _exponential_smoothing_forecast(self, df: pd.DataFrame, days_ahead: int) -> List[float]:
        """Predicción usando suavizado exponencial"""
        try:
            alpha = 0.3  # Factor de suavizado
            values = df['quantity'].values
            
            if len(values) == 0:
                return [0] * days_ahead
            
            # Suavizado exponencial simple
            smoothed = [values[0]]
            for i in range(1, len(values)):
                smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[i-1])
            
            last_value = smoothed[-1]
            predictions = [last_value] * days_ahead
            
            return predictions
            
        except Exception as e:
            self.logger.error(f'Error en suavizado exponencial: {str(e)}')
            return [0] * days_ahead
    
    def _linear_regression_forecast(self, df: pd.DataFrame, days_ahead: int) -> List[float]:
        """Predicción usando regresión lineal"""
        try:
            if len(df) < 3:
                return [0] * days_ahead
            
            # Preparar datos para regresión
            X = np.arange(len(df)).reshape(-1, 1)
            y = df['quantity'].values
            
            # Entrenar modelo
            model = LinearRegression()
            model.fit(X, y)
            
            # Generar predicciones
            future_X = np.arange(len(df), len(df) + days_ahead).reshape(-1, 1)
            predictions = model.predict(future_X)
            
            # Asegurar valores no negativos
            predictions = np.maximum(predictions, 0)
            
            return predictions.tolist()
            
        except Exception as e:
            self.logger.error(f'Error en regresión lineal: {str(e)}')
            return [0] * days_ahead
    
    def _calculate_accuracy_metrics(self, df: pd.DataFrame, predictions: List[float]) -> Dict:
        """Calcula métricas de precisión"""
        try:
            if len(df) < 2:
                return {'mae': 0, 'rmse': 0, 'mape': 0}
            
            # Usar últimos datos para validación
            actual = df['quantity'].tail(min(len(predictions), len(df))).values
            predicted = predictions[:len(actual)]
            
            if len(actual) == 0 or len(predicted) == 0:
                return {'mae': 0, 'rmse': 0, 'mape': 0}
            
            mae = mean_absolute_error(actual, predicted)
            rmse = np.sqrt(mean_squared_error(actual, predicted))
            
            # MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((actual - predicted) / np.maximum(actual, 1))) * 100
            
            return {
                'mae': round(mae, 2),
                'rmse': round(rmse, 2),
                'mape': round(mape, 2)
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando métricas: {str(e)}')
            return {'mae': 0, 'rmse': 0, 'mape': 0}
    
    def _save_forecasts(self, product_id: int, predictions: List[float], method: str):
        """Guarda predicciones en la base de datos"""
        try:
            # Eliminar predicciones anteriores del mismo producto
            DemandForecast.query.filter(DemandForecast.product_id == product_id).delete()
            
            # Guardar nuevas predicciones
            for i, prediction in enumerate(predictions):
                forecast_date = datetime.utcnow().date() + timedelta(days=i+1)
                
                forecast = DemandForecast(
                    product_id=product_id,
                    forecast_date=forecast_date,
                    predicted_demand=prediction,
                    method_used=method,
                    confidence_level=0.8  # Nivel de confianza por defecto
                )
                
                db.session.add(forecast)
            
            db.session.commit()
            self.logger.info(f'Predicciones guardadas para producto {product_id}')
            
        except Exception as e:
            self.logger.error(f'Error guardando predicciones: {str(e)}')
            db.session.rollback()
    
    def _fallback_forecast(self, product_id: int, days_ahead: int) -> Dict:
        """Predicción de respaldo cuando no hay suficientes datos"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return {'error': 'Producto no encontrado'}
            
            # Usar promedio histórico simple o valor por defecto
            avg_daily_sales = 1.0  # Valor por defecto
            
            predictions = [avg_daily_sales] * days_ahead
            
            return {
                'product_id': product_id,
                'method_used': 'fallback',
                'predictions': predictions,
                'accuracy_metrics': {'mae': 0, 'rmse': 0, 'mape': 0},
                'forecast_period': days_ahead,
                'generated_at': datetime.utcnow(),
                'note': 'Predicción usando método de respaldo por falta de datos históricos'
            }
            
        except Exception as e:
            self.logger.error(f'Error en predicción de respaldo: {str(e)}')
            return {'error': str(e)}
    
    def get_forecast_summary(self) -> Dict:
        """Obtiene resumen de todas las predicciones"""
        try:
            forecasts = DemandForecast.query.all()
            
            if not forecasts:
                return {'total_forecasts': 0, 'products_with_forecasts': 0}
            
            products_with_forecasts = len(set(f.product_id for f in forecasts))
            total_predicted_demand = sum(f.predicted_demand for f in forecasts)
            
            return {
                'total_forecasts': len(forecasts),
                'products_with_forecasts': products_with_forecasts,
                'total_predicted_demand': round(total_predicted_demand, 2),
                'average_daily_demand': round(total_predicted_demand / len(forecasts), 2)
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo resumen de predicciones: {str(e)}')
            return {'error': str(e)}

# Instancia global del servicio de previsión
demand_forecasting_service = DemandForecastingService()



