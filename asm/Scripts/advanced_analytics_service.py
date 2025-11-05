from datetime import datetime, timedelta
from app import db
from models import Product, SalesRecord, InventoryRecord, Alert
from services.alert_service import alert_system
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging
from typing import Dict, List, Tuple
import json

class AdvancedAnalyticsService:
    """Servicio de análisis avanzado con machine learning"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_product_performance(self, days_back: int = 90) -> Dict:
        """Análisis avanzado de rendimiento de productos"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Obtener datos de ventas
            sales_data = SalesRecord.query.filter(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            ).all()
            
            if not sales_data:
                return {'error': 'No hay datos de ventas suficientes'}
            
            # Preparar datos para análisis
            df = self._prepare_sales_dataframe(sales_data)
            
            # Análisis ABC
            abc_analysis = self._perform_abc_analysis(df)
            
            # Análisis de estacionalidad
            seasonality = self._analyze_seasonality(df)
            
            # Clustering de productos
            clusters = self._cluster_products(df)
            
            # Análisis de correlaciones
            correlations = self._analyze_correlations(df)
            
            # Predicción de demanda avanzada
            demand_forecast = self._advanced_demand_forecast(df)
            
            return {
                'abc_analysis': abc_analysis,
                'seasonality': seasonality,
                'clusters': clusters,
                'correlations': correlations,
                'demand_forecast': demand_forecast,
                'analysis_period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'total_products_analyzed': len(df['product_id'].unique())
            }
            
        except Exception as e:
            self.logger.error(f'Error en análisis de rendimiento: {str(e)}')
            return {'error': str(e)}
    
    def _prepare_sales_dataframe(self, sales_data: List) -> pd.DataFrame:
        """Prepara DataFrame para análisis"""
        data = []
        for sale in sales_data:
            data.append({
                'product_id': sale.product_id,
                'product_name': sale.product.name,
                'category': sale.product.category,
                'quantity_sold': sale.quantity_sold,
                'unit_price': sale.unit_price,
                'total_amount': sale.total_amount,
                'sale_date': sale.sale_date,
                'day_of_week': sale.sale_date.weekday(),
                'month': sale.sale_date.month,
                'quarter': (sale.sale_date.month - 1) // 3 + 1
            })
        
        df = pd.DataFrame(data)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        return df
    
    def _perform_abc_analysis(self, df: pd.DataFrame) -> Dict:
        """Análisis ABC de productos"""
        try:
            # Calcular ventas totales por producto
            product_sales = df.groupby('product_id').agg({
                'total_amount': 'sum',
                'quantity_sold': 'sum',
                'product_name': 'first',
                'category': 'first'
            }).reset_index()
            
            # Ordenar por ventas
            product_sales = product_sales.sort_values('total_amount', ascending=False)
            
            # Calcular porcentajes acumulados
            product_sales['cumulative_amount'] = product_sales['total_amount'].cumsum()
            product_sales['cumulative_percentage'] = (
                product_sales['cumulative_amount'] / product_sales['total_amount'].sum() * 100
            )
            
            # Clasificar ABC
            def classify_abc(percentage):
                if percentage <= 80:
                    return 'A'
                elif percentage <= 95:
                    return 'B'
                else:
                    return 'C'
            
            product_sales['abc_class'] = product_sales['cumulative_percentage'].apply(classify_abc)
            
            # Resumen por clase
            abc_summary = product_sales.groupby('abc_class').agg({
                'product_id': 'count',
                'total_amount': 'sum',
                'quantity_sold': 'sum'
            }).to_dict('index')
            
            return {
                'products': product_sales.to_dict('records'),
                'summary': abc_summary,
                'total_products': len(product_sales),
                'total_revenue': product_sales['total_amount'].sum()
            }
            
        except Exception as e:
            self.logger.error(f'Error en análisis ABC: {str(e)}')
            return {'error': str(e)}
    
    def _analyze_seasonality(self, df: pd.DataFrame) -> Dict:
        """Análisis de estacionalidad"""
        try:
            # Agrupar por mes
            monthly_sales = df.groupby('month').agg({
                'total_amount': 'sum',
                'quantity_sold': 'sum'
            }).reset_index()
            
            # Agrupar por día de la semana
            weekly_sales = df.groupby('day_of_week').agg({
                'total_amount': 'sum',
                'quantity_sold': 'sum'
            }).reset_index()
            
            # Agrupar por trimestre
            quarterly_sales = df.groupby('quarter').agg({
                'total_amount': 'sum',
                'quantity_sold': 'sum'
            }).reset_index()
            
            return {
                'monthly': monthly_sales.to_dict('records'),
                'weekly': weekly_sales.to_dict('records'),
                'quarterly': quarterly_sales.to_dict('records')
            }
            
        except Exception as e:
            self.logger.error(f'Error en análisis de estacionalidad: {str(e)}')
            return {'error': str(e)}
    
    def _cluster_products(self, df: pd.DataFrame) -> Dict:
        """Clustering de productos usando K-means"""
        try:
            # Preparar características para clustering
            product_features = df.groupby('product_id').agg({
                'total_amount': 'sum',
                'quantity_sold': 'sum',
                'unit_price': 'mean',
                'sale_date': 'count'  # Frecuencia de ventas
            }).reset_index()
            
            # Normalizar características
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(product_features[['total_amount', 'quantity_sold', 'unit_price', 'sale_date']])
            
            # Aplicar K-means
            kmeans = KMeans(n_clusters=3, random_state=42)
            clusters = kmeans.fit_predict(features_scaled)
            
            product_features['cluster'] = clusters
            
            # Análisis de clusters
            cluster_analysis = product_features.groupby('cluster').agg({
                'product_id': 'count',
                'total_amount': ['sum', 'mean'],
                'quantity_sold': ['sum', 'mean'],
                'unit_price': 'mean',
                'sale_date': 'mean'
            }).round(2)
            
            return {
                'products': product_features.to_dict('records'),
                'cluster_analysis': cluster_analysis.to_dict(),
                'cluster_centers': kmeans.cluster_centers_.tolist()
            }
            
        except Exception as e:
            self.logger.error(f'Error en clustering: {str(e)}')
            return {'error': str(e)}
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict:
        """Análisis de correlaciones"""
        try:
            # Crear matriz de correlación
            numeric_columns = ['quantity_sold', 'unit_price', 'total_amount', 'day_of_week', 'month']
            correlation_matrix = df[numeric_columns].corr()
            
            # Encontrar correlaciones fuertes
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:  # Correlación fuerte
                        strong_correlations.append({
                            'variable1': correlation_matrix.columns[i],
                            'variable2': correlation_matrix.columns[j],
                            'correlation': round(corr_value, 3)
                        })
            
            return {
                'correlation_matrix': correlation_matrix.round(3).to_dict(),
                'strong_correlations': strong_correlations
            }
            
        except Exception as e:
            self.logger.error(f'Error en análisis de correlaciones: {str(e)}')
            return {'error': str(e)}
    
    def _advanced_demand_forecast(self, df: pd.DataFrame) -> Dict:
        """Predicción avanzada de demanda usando múltiples métodos"""
        try:
            # Preparar serie temporal
            daily_sales = df.groupby('sale_date')['quantity_sold'].sum().reset_index()
            daily_sales = daily_sales.set_index('sale_date')
            
            # Completar fechas faltantes
            date_range = pd.date_range(start=daily_sales.index.min(), end=daily_sales.index.max(), freq='D')
            daily_sales = daily_sales.reindex(date_range, fill_value=0)
            
            # Métodos de predicción
            forecasts = {}
            
            # Media móvil exponencial
            alpha = 0.3
            ema_forecast = daily_sales['quantity_sold'].ewm(alpha=alpha).mean().iloc[-1]
            forecasts['exponential_moving_average'] = round(ema_forecast, 2)
            
            # Tendencia lineal
            x = np.arange(len(daily_sales))
            y = daily_sales['quantity_sold'].values
            slope, intercept = np.polyfit(x, y, 1)
            linear_forecast = slope * len(daily_sales) + intercept
            forecasts['linear_trend'] = round(linear_forecast, 2)
            
            # Promedio estacional
            monthly_avg = daily_sales.groupby(daily_sales.index.month)['quantity_sold'].mean()
            current_month = datetime.utcnow().month
            seasonal_forecast = monthly_avg[current_month]
            forecasts['seasonal_average'] = round(seasonal_avg, 2)
            
            # Combinación ponderada
            combined_forecast = (
                0.4 * ema_forecast + 
                0.3 * linear_forecast + 
                0.3 * seasonal_forecast
            )
            forecasts['combined'] = round(combined_forecast, 2)
            
            return {
                'forecasts': forecasts,
                'confidence_level': 0.85,
                'forecast_horizon': '30 days',
                'method': 'ensemble'
            }
            
        except Exception as e:
            self.logger.error(f'Error en predicción avanzada: {str(e)}')
            return {'error': str(e)}
    
    def generate_insights_report(self) -> Dict:
        """Genera reporte de insights automáticos"""
        try:
            insights = []
            
            # Análisis de rendimiento
            performance = self.analyze_product_performance()
            
            if 'abc_analysis' in performance:
                abc_data = performance['abc_analysis']
                if 'summary' in abc_data:
                    class_a_count = abc_data['summary'].get('A', {}).get('product_id', 0)
                    total_products = abc_data.get('total_products', 0)
                    
                    if class_a_count > 0:
                        insights.append({
                            'type': 'abc_analysis',
                            'title': 'Análisis ABC',
                            'message': f'{class_a_count} productos clase A generan el 80% de los ingresos',
                            'recommendation': 'Enfocar recursos en productos clase A para maximizar ROI',
                            'priority': 'high'
                        })
            
            # Análisis de estacionalidad
            if 'seasonality' in performance:
                seasonality_data = performance['seasonality']
                if 'monthly' in seasonality_data:
                    monthly_sales = seasonality_data['monthly']
                    if len(monthly_sales) > 1:
                        max_month = max(monthly_sales, key=lambda x: x['total_amount'])
                        min_month = min(monthly_sales, key=lambda x: x['total_amount'])
                        
                        insights.append({
                            'type': 'seasonality',
                            'title': 'Estacionalidad Detectada',
                            'message': f'Mejor mes: {max_month["month"]}, Peor mes: {min_month["month"]}',
                            'recommendation': 'Ajustar inventario según patrones estacionales',
                            'priority': 'medium'
                        })
            
            # Análisis de clustering
            if 'clusters' in performance:
                clusters_data = performance['clusters']
                if 'products' in clusters_data:
                    cluster_counts = {}
                    for product in clusters_data['products']:
                        cluster = product['cluster']
                        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1
                    
                    insights.append({
                        'type': 'clustering',
                        'title': 'Segmentación de Productos',
                        'message': f'Productos segmentados en {len(cluster_counts)} grupos distintos',
                        'recommendation': 'Desarrollar estrategias específicas por segmento',
                        'priority': 'medium'
                    })
            
            return {
                'insights': insights,
                'total_insights': len(insights),
                'generated_at': datetime.utcnow().isoformat(),
                'analysis_period': performance.get('analysis_period', 'N/A')
            }
            
        except Exception as e:
            self.logger.error(f'Error generando insights: {str(e)}')
            return {'error': str(e)}

# Instancia global del servicio de análisis avanzado
advanced_analytics_service = AdvancedAnalyticsService()



