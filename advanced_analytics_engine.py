#!/usr/bin/env python3
"""
Advanced Analytics Engine for Competitive Pricing Analysis
=========================================================

Motor de análisis avanzado que proporciona:
- Análisis predictivo de precios
- Modelado de comportamiento del mercado
- Análisis de elasticidad de precios
- Segmentación de mercado
- Análisis de correlación avanzado
- Modelado de series temporales
- Análisis de clustering
- Análisis de componentes principales
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
import logging
import json
import pickle
import joblib
from pathlib import Path
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsConfig:
    """Configuración de análisis"""
    analysis_type: str
    target_variable: str
    features: List[str]
    model_type: str
    test_size: float = 0.2
    random_state: int = 42
    cross_validation: int = 5
    hyperparameter_tuning: bool = True
    feature_selection: bool = True
    scaling: bool = True

@dataclass
class ModelResults:
    """Resultados del modelo"""
    model_name: str
    model: Any
    predictions: np.ndarray
    actual_values: np.ndarray
    metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None
    cross_val_scores: Optional[List[float]] = None
    hyperparameters: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsInsight:
    """Insight de análisis"""
    insight_type: str
    title: str
    description: str
    confidence: float
    impact_score: float
    recommendation: str
    supporting_data: Dict[str, Any]

class AdvancedAnalyticsEngine:
    """Motor de análisis avanzado"""
    
    def __init__(self, db_path: str = "pricing_analysis.db"):
        """Inicializar motor de análisis"""
        self.db_path = db_path
        self.models_dir = Path("models")
        self.results_dir = Path("analytics_results")
        self.charts_dir = Path("analytics_charts")
        
        # Crear directorios
        self.models_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        self.charts_dir.mkdir(exist_ok=True)
        
        # Configuración de modelos
        self.models = {
            'linear_regression': LinearRegression(),
            'ridge_regression': Ridge(),
            'lasso_regression': Lasso(),
            'elastic_net': ElasticNet(),
            'random_forest': RandomForestRegressor(random_state=42),
            'gradient_boosting': GradientBoostingRegressor(random_state=42),
            'svr': SVR(),
            'neural_network': MLPRegressor(random_state=42, max_iter=1000)
        }
        
        # Configuración de clustering
        self.clustering_models = {
            'kmeans': KMeans(random_state=42),
            'dbscan': DBSCAN(),
            'agglomerative': AgglomerativeClustering()
        }
        
        logger.info("Advanced Analytics Engine initialized")
    
    def load_data(self, query: str = None) -> pd.DataFrame:
        """Cargar datos para análisis"""
        try:
            conn = sqlite3.connect(self.db_path)
            
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
            
            # Limpiar datos
            data = self._clean_data(data)
            
            logger.info(f"Loaded {len(data)} records for analysis")
            return data
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Limpiar datos para análisis"""
        # Eliminar valores nulos
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
        
        # Codificar variables categóricas
        categorical_columns = ['category', 'brand', 'competitor', 'currency', 'source']
        for col in categorical_columns:
            if col in data.columns:
                le = LabelEncoder()
                data[f'{col}_encoded'] = le.fit_transform(data[col].astype(str))
        
        return data
    
    def perform_price_elasticity_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Realizar análisis de elasticidad de precios"""
        try:
            logger.info("Performing price elasticity analysis...")
            
            # Agrupar por producto y competidor
            product_analysis = []
            
            for product_id in data['product_id'].unique():
                product_data = data[data['product_id'] == product_id]
                
                for competitor in product_data['competitor'].unique():
                    comp_data = product_data[product_data['competitor'] == competitor]
                    
                    if len(comp_data) > 10:  # Mínimo de datos para análisis
                        # Ordenar por fecha
                        comp_data = comp_data.sort_values('date_collected')
                        
                        # Calcular cambios de precio
                        comp_data['price_change'] = comp_data['price'].pct_change()
                        comp_data['price_change_lag'] = comp_data['price_change'].shift(1)
                        
                        # Calcular elasticidad
                        if comp_data['price_change'].std() > 0:
                            elasticity = comp_data['price_change'].corr(comp_data['price_change_lag'])
                            
                            product_analysis.append({
                                'product_id': product_id,
                                'competitor': competitor,
                                'elasticity': elasticity,
                                'price_volatility': comp_data['price'].std(),
                                'price_trend': comp_data['price'].iloc[-1] - comp_data['price'].iloc[0],
                                'data_points': len(comp_data)
                            })
            
            elasticity_df = pd.DataFrame(product_analysis)
            
            # Análisis de elasticidad
            results = {
                'elasticity_stats': {
                    'mean_elasticity': elasticity_df['elasticity'].mean(),
                    'median_elasticity': elasticity_df['elasticity'].median(),
                    'std_elasticity': elasticity_df['elasticity'].std(),
                    'min_elasticity': elasticity_df['elasticity'].min(),
                    'max_elasticity': elasticity_df['elasticity'].max()
                },
                'elasticity_distribution': elasticity_df['elasticity'].describe().to_dict(),
                'high_elasticity_products': elasticity_df[elasticity_df['elasticity'] > 0.5].to_dict('records'),
                'low_elasticity_products': elasticity_df[elasticity_df['elasticity'] < -0.5].to_dict('records'),
                'volatility_analysis': {
                    'high_volatility': elasticity_df[elasticity_df['price_volatility'] > elasticity_df['price_volatility'].quantile(0.8)].to_dict('records'),
                    'low_volatility': elasticity_df[elasticity_df['price_volatility'] < elasticity_df['price_volatility'].quantile(0.2)].to_dict('records')
                }
            }
            
            # Crear visualizaciones
            self._create_elasticity_charts(elasticity_df)
            
            logger.info("Price elasticity analysis completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in price elasticity analysis: {e}")
            raise
    
    def _create_elasticity_charts(self, elasticity_df: pd.DataFrame):
        """Crear gráficos de elasticidad"""
        try:
            # Gráfico de distribución de elasticidad
            fig = px.histogram(
                elasticity_df, 
                x='elasticity', 
                nbins=30,
                title='Price Elasticity Distribution',
                labels={'elasticity': 'Price Elasticity', 'count': 'Frequency'}
            )
            
            chart_path = self.charts_dir / f"elasticity_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            
            # Gráfico de elasticidad vs volatilidad
            fig = px.scatter(
                elasticity_df,
                x='price_volatility',
                y='elasticity',
                color='competitor',
                title='Price Elasticity vs Volatility',
                labels={'price_volatility': 'Price Volatility', 'elasticity': 'Price Elasticity'}
            )
            
            chart_path = self.charts_dir / f"elasticity_vs_volatility_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            
        except Exception as e:
            logger.error(f"Error creating elasticity charts: {e}")
    
    def perform_market_segmentation(self, data: pd.DataFrame, n_clusters: int = 5) -> Dict[str, Any]:
        """Realizar segmentación de mercado"""
        try:
            logger.info("Performing market segmentation...")
            
            # Preparar datos para clustering
            features = ['price', 'price_log', 'day_of_week', 'month', 'quarter']
            if 'category_encoded' in data.columns:
                features.append('category_encoded')
            if 'brand_encoded' in data.columns:
                features.append('brand_encoded')
            
            # Filtrar características disponibles
            available_features = [f for f in features if f in data.columns]
            
            if len(available_features) < 2:
                raise ValueError("Insufficient features for clustering")
            
            # Preparar datos
            X = data[available_features].fillna(0)
            
            # Escalar datos
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Aplicar clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Agregar clusters a los datos
            data['cluster'] = clusters
            
            # Análisis de clusters
            cluster_analysis = []
            for cluster_id in range(n_clusters):
                cluster_data = data[data['cluster'] == cluster_id]
                
                analysis = {
                    'cluster_id': cluster_id,
                    'size': len(cluster_data),
                    'percentage': len(cluster_data) / len(data) * 100,
                    'avg_price': cluster_data['price'].mean(),
                    'price_std': cluster_data['price'].std(),
                    'dominant_category': cluster_data['category'].mode().iloc[0] if 'category' in cluster_data.columns else 'N/A',
                    'dominant_brand': cluster_data['brand'].mode().iloc[0] if 'brand' in cluster_data.columns else 'N/A',
                    'dominant_competitor': cluster_data['competitor'].mode().iloc[0] if 'competitor' in cluster_data.columns else 'N/A'
                }
                
                cluster_analysis.append(analysis)
            
            # Análisis de componentes principales
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            
            results = {
                'clusters': cluster_analysis,
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'pca_components': pca.components_.tolist(),
                'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                'silhouette_score': self._calculate_silhouette_score(X_scaled, clusters),
                'inertia': kmeans.inertia_
            }
            
            # Crear visualizaciones
            self._create_segmentation_charts(data, X_pca, clusters, cluster_analysis)
            
            logger.info("Market segmentation completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in market segmentation: {e}")
            raise
    
    def _calculate_silhouette_score(self, X: np.ndarray, clusters: np.ndarray) -> float:
        """Calcular silhouette score"""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(X, clusters)
        except:
            return 0.0
    
    def _create_segmentation_charts(self, data: pd.DataFrame, X_pca: np.ndarray, clusters: np.ndarray, cluster_analysis: List[Dict]):
        """Crear gráficos de segmentación"""
        try:
            # Gráfico de clusters en espacio PCA
            fig = px.scatter(
                x=X_pca[:, 0],
                y=X_pca[:, 1],
                color=clusters,
                title='Market Segments (PCA View)',
                labels={'x': 'First Principal Component', 'y': 'Second Principal Component'}
            )
            
            chart_path = self.charts_dir / f"market_segments_pca_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            
            # Gráfico de distribución de precios por cluster
            fig = px.box(
                data,
                x='cluster',
                y='price',
                title='Price Distribution by Market Segment',
                labels={'cluster': 'Market Segment', 'price': 'Price ($)'}
            )
            
            chart_path = self.charts_dir / f"price_distribution_by_segment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            
            # Gráfico de tamaño de clusters
            cluster_sizes = [analysis['size'] for analysis in cluster_analysis]
            cluster_labels = [f"Segment {i}" for i in range(len(cluster_analysis))]
            
            fig = px.pie(
                values=cluster_sizes,
                names=cluster_labels,
                title='Market Segment Sizes'
            )
            
            chart_path = self.charts_dir / f"segment_sizes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            
        except Exception as e:
            logger.error(f"Error creating segmentation charts: {e}")
    
    def perform_time_series_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Realizar análisis de series temporales"""
        try:
            logger.info("Performing time series analysis...")
            
            # Agrupar por fecha
            daily_prices = data.groupby('date_collected')['price'].agg(['mean', 'std', 'count']).reset_index()
            daily_prices = daily_prices.set_index('date_collected')
            
            # Completar fechas faltantes
            date_range = pd.date_range(start=daily_prices.index.min(), end=daily_prices.index.max(), freq='D')
            daily_prices = daily_prices.reindex(date_range, fill_value=np.nan)
            
            # Interpolar valores faltantes
            daily_prices['mean'] = daily_prices['mean'].interpolate(method='linear')
            daily_prices['std'] = daily_prices['std'].fillna(daily_prices['std'].mean())
            daily_prices['count'] = daily_prices['count'].fillna(0)
            
            # Análisis de estacionalidad
            decomposition = seasonal_decompose(daily_prices['mean'], model='additive', period=7)
            
            # Prueba de estacionariedad
            adf_result = adfuller(daily_prices['mean'].dropna())
            
            # Modelo ARIMA
            arima_model = ARIMA(daily_prices['mean'].dropna(), order=(1, 1, 1))
            arima_fit = arima_model.fit()
            
            # Predicciones
            forecast_steps = 30
            forecast = arima_fit.forecast(steps=forecast_steps)
            forecast_ci = arima_fit.get_forecast(steps=forecast_steps).conf_int()
            
            # Análisis de autocorrelación
            ljung_box = acorr_ljungbox(arima_fit.resid, lags=10, return_df=True)
            
            results = {
                'decomposition': {
                    'trend': decomposition.trend.dropna().tolist(),
                    'seasonal': decomposition.seasonal.dropna().tolist(),
                    'residual': decomposition.resid.dropna().tolist()
                },
                'stationarity_test': {
                    'adf_statistic': adf_result[0],
                    'p_value': adf_result[1],
                    'critical_values': adf_result[4],
                    'is_stationary': adf_result[1] < 0.05
                },
                'arima_model': {
                    'aic': arima_fit.aic,
                    'bic': arima_fit.bic,
                    'params': arima_fit.params.to_dict()
                },
                'forecast': {
                    'values': forecast.tolist(),
                    'confidence_interval': {
                        'lower': forecast_ci.iloc[:, 0].tolist(),
                        'upper': forecast_ci.iloc[:, 1].tolist()
                    }
                },
                'autocorrelation_test': {
                    'ljung_box_statistic': ljung_box['lb_stat'].tolist(),
                    'ljung_box_p_value': ljung_box['lb_pvalue'].tolist()
                }
            }
            
            # Crear visualizaciones
            self._create_time_series_charts(daily_prices, decomposition, forecast, forecast_ci)
            
            logger.info("Time series analysis completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in time series analysis: {e}")
            raise
    
    def _create_time_series_charts(self, daily_prices: pd.DataFrame, decomposition, forecast, forecast_ci):
        """Crear gráficos de series temporales"""
        try:
            # Gráfico principal de series temporales
            fig = go.Figure()
            
            # Datos históricos
            fig.add_trace(go.Scatter(
                x=daily_prices.index,
                y=daily_prices['mean'],
                mode='lines',
                name='Historical Prices',
                line=dict(color='blue')
            ))
            
            # Predicciones
            future_dates = pd.date_range(start=daily_prices.index[-1] + timedelta(days=1), periods=len(forecast), freq='D')
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=forecast,
                mode='lines',
                name='Forecast',
                line=dict(color='red', dash='dash')
            ))
            
            # Intervalo de confianza
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=forecast_ci.iloc[:, 1],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=forecast_ci.iloc[:, 0],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.2)',
                name='Confidence Interval'
            ))
            
            fig.update_layout(
                title='Price Time Series Analysis and Forecast',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                template='plotly_white'
            )
            
            chart_path = self.charts_dir / f"time_series_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            
            # Gráfico de descomposición
            fig = make_subplots(
                rows=4, cols=1,
                subplot_titles=('Original', 'Trend', 'Seasonal', 'Residual'),
                vertical_spacing=0.05
            )
            
            fig.add_trace(go.Scatter(x=daily_prices.index, y=daily_prices['mean'], name='Original'), row=1, col=1)
            fig.add_trace(go.Scatter(x=decomposition.trend.index, y=decomposition.trend, name='Trend'), row=2, col=1)
            fig.add_trace(go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal, name='Seasonal'), row=3, col=1)
            fig.add_trace(go.Scatter(x=decomposition.resid.index, y=decomposition.resid, name='Residual'), row=4, col=1)
            
            fig.update_layout(
                title='Time Series Decomposition',
                height=800,
                template='plotly_white'
            )
            
            chart_path = self.charts_dir / f"time_series_decomposition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            
        except Exception as e:
            logger.error(f"Error creating time series charts: {e}")
    
    def perform_correlation_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Realizar análisis de correlación avanzado"""
        try:
            logger.info("Performing correlation analysis...")
            
            # Seleccionar variables numéricas
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_columns) < 2:
                raise ValueError("Insufficient numeric variables for correlation analysis")
            
            # Calcular matriz de correlación
            correlation_matrix = data[numeric_columns].corr()
            
            # Análisis de correlaciones significativas
            significant_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:  # Correlación significativa
                        significant_correlations.append({
                            'variable1': correlation_matrix.columns[i],
                            'variable2': correlation_matrix.columns[j],
                            'correlation': corr_value,
                            'strength': 'strong' if abs(corr_value) > 0.7 else 'moderate'
                        })
            
            # Análisis de correlación parcial
            partial_correlations = self._calculate_partial_correlations(data[numeric_columns])
            
            # Análisis de correlación por grupos
            group_correlations = {}
            if 'competitor' in data.columns:
                for competitor in data['competitor'].unique():
                    comp_data = data[data['competitor'] == competitor]
                    if len(comp_data) > 10:
                        comp_corr = comp_data[numeric_columns].corr()
                        group_correlations[competitor] = comp_corr.to_dict()
            
            results = {
                'correlation_matrix': correlation_matrix.to_dict(),
                'significant_correlations': significant_correlations,
                'partial_correlations': partial_correlations,
                'group_correlations': group_correlations,
                'correlation_summary': {
                    'total_correlations': len(significant_correlations),
                    'strong_correlations': len([c for c in significant_correlations if c['strength'] == 'strong']),
                    'moderate_correlations': len([c for c in significant_correlations if c['strength'] == 'moderate'])
                }
            }
            
            # Crear visualizaciones
            self._create_correlation_charts(correlation_matrix, significant_correlations)
            
            logger.info("Correlation analysis completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {e}")
            raise
    
    def _calculate_partial_correlations(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calcular correlaciones parciales"""
        try:
            from scipy.stats import pearsonr
            
            partial_correlations = {}
            
            # Calcular correlación parcial entre las dos primeras variables
            # controlando por las demás
            if len(data.columns) >= 3:
                var1, var2 = data.columns[0], data.columns[1]
                control_vars = data.columns[2:]
                
                # Regresión múltiple para calcular residuos
                from sklearn.linear_model import LinearRegression
                
                # Regresión de var1 sobre variables de control
                X_control = data[control_vars].fillna(0)
                y1 = data[var1].fillna(0)
                reg1 = LinearRegression().fit(X_control, y1)
                residuals1 = y1 - reg1.predict(X_control)
                
                # Regresión de var2 sobre variables de control
                y2 = data[var2].fillna(0)
                reg2 = LinearRegression().fit(X_control, y2)
                residuals2 = y2 - reg2.predict(X_control)
                
                # Correlación entre residuos
                partial_corr, _ = pearsonr(residuals1, residuals2)
                partial_correlations[f"{var1}_vs_{var2}"] = partial_corr
            
            return partial_correlations
            
        except Exception as e:
            logger.error(f"Error calculating partial correlations: {e}")
            return {}
    
    def _create_correlation_charts(self, correlation_matrix: pd.DataFrame, significant_correlations: List[Dict]):
        """Crear gráficos de correlación"""
        try:
            # Heatmap de correlación
            fig = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix Heatmap",
                color_continuous_scale="RdBu_r"
            )
            
            chart_path = self.charts_dir / f"correlation_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            
            # Gráfico de correlaciones significativas
            if significant_correlations:
                corr_data = pd.DataFrame(significant_correlations)
                
                fig = px.bar(
                    corr_data,
                    x='correlation',
                    y='variable1',
                    color='strength',
                    title='Significant Correlations',
                    labels={'correlation': 'Correlation Coefficient', 'variable1': 'Variable 1'}
                )
                
                chart_path = self.charts_dir / f"significant_correlations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                fig.write_html(str(chart_path))
            
        except Exception as e:
            logger.error(f"Error creating correlation charts: {e}")
    
    def build_predictive_models(self, data: pd.DataFrame, config: AnalyticsConfig) -> List[ModelResults]:
        """Construir modelos predictivos"""
        try:
            logger.info("Building predictive models...")
            
            # Preparar datos
            X, y = self._prepare_model_data(data, config)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=config.test_size, random_state=config.random_state
            )
            
            # Escalar datos si es necesario
            if config.scaling:
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)
            
            # Selección de características
            if config.feature_selection:
                selector = SelectKBest(f_regression, k=min(10, X.shape[1]))
                X_train = selector.fit_transform(X_train, y_train)
                X_test = selector.transform(X_test)
            
            # Entrenar modelos
            results = []
            for model_name, model in self.models.items():
                try:
                    # Optimización de hiperparámetros
                    if config.hyperparameter_tuning:
                        model = self._optimize_hyperparameters(model, model_name, X_train, y_train)
                    
                    # Entrenar modelo
                    model.fit(X_train, y_train)
                    
                    # Predicciones
                    y_pred = model.predict(X_test)
                    
                    # Métricas
                    metrics = {
                        'mse': mean_squared_error(y_test, y_pred),
                        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                        'mae': mean_absolute_error(y_test, y_pred),
                        'r2': r2_score(y_test, y_pred)
                    }
                    
                    # Validación cruzada
                    cv_scores = cross_val_score(model, X_train, y_train, cv=config.cross_validation, scoring='r2')
                    
                    # Importancia de características
                    feature_importance = None
                    if hasattr(model, 'feature_importances_'):
                        feature_importance = dict(zip(config.features, model.feature_importances_))
                    elif hasattr(model, 'coef_'):
                        feature_importance = dict(zip(config.features, model.coef_))
                    
                    result = ModelResults(
                        model_name=model_name,
                        model=model,
                        predictions=y_pred,
                        actual_values=y_test,
                        metrics=metrics,
                        feature_importance=feature_importance,
                        cross_val_scores=cv_scores.tolist(),
                        hyperparameters=model.get_params() if hasattr(model, 'get_params') else None
                    )
                    
                    results.append(result)
                    
                    # Guardar modelo
                    self._save_model(model, model_name)
                    
                except Exception as e:
                    logger.error(f"Error training model {model_name}: {e}")
                    continue
            
            # Ordenar por R²
            results.sort(key=lambda x: x.metrics['r2'], reverse=True)
            
            logger.info(f"Built {len(results)} predictive models")
            return results
            
        except Exception as e:
            logger.error(f"Error building predictive models: {e}")
            raise
    
    def _prepare_model_data(self, data: pd.DataFrame, config: AnalyticsConfig) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos para modelado"""
        # Seleccionar características disponibles
        available_features = [f for f in config.features if f in data.columns]
        
        if not available_features:
            raise ValueError("No features available for modeling")
        
        X = data[available_features].fillna(0)
        y = data[config.target_variable].fillna(0)
        
        return X.values, y.values
    
    def _optimize_hyperparameters(self, model, model_name: str, X_train: np.ndarray, y_train: np.ndarray) -> Any:
        """Optimizar hiperparámetros"""
        try:
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
            
            if model_name in param_grids:
                grid_search = GridSearchCV(
                    model, param_grids[model_name], 
                    cv=3, scoring='r2', n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                return grid_search.best_estimator_
            
            return model
            
        except Exception as e:
            logger.error(f"Error optimizing hyperparameters: {e}")
            return model
    
    def _save_model(self, model: Any, model_name: str):
        """Guardar modelo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{model_name}_{timestamp}.joblib"
            filepath = self.models_dir / filename
            
            joblib.dump(model, filepath)
            logger.info(f"Model saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def generate_analytics_insights(self, data: pd.DataFrame) -> List[AnalyticsInsight]:
        """Generar insights de análisis"""
        try:
            logger.info("Generating analytics insights...")
            
            insights = []
            
            # Insight 1: Análisis de precios
            price_stats = data['price'].describe()
            if price_stats['std'] / price_stats['mean'] > 0.3:
                insights.append(AnalyticsInsight(
                    insight_type="price_volatility",
                    title="High Price Volatility Detected",
                    description=f"Price volatility is {price_stats['std'] / price_stats['mean']:.2%}, indicating significant price fluctuations",
                    confidence=0.85,
                    impact_score=0.7,
                    recommendation="Consider implementing price stabilization strategies or dynamic pricing models",
                    supporting_data={"volatility_ratio": price_stats['std'] / price_stats['mean']}
                ))
            
            # Insight 2: Análisis de competidores
            if 'competitor' in data.columns:
                competitor_prices = data.groupby('competitor')['price'].mean()
                price_gaps = competitor_prices.max() - competitor_prices.min()
                avg_price = competitor_prices.mean()
                
                if price_gaps / avg_price > 0.2:
                    insights.append(AnalyticsInsight(
                        insight_type="competitive_positioning",
                        title="Significant Price Gaps Between Competitors",
                        description=f"Price gap of ${price_gaps:.2f} ({price_gaps/avg_price:.1%}) between highest and lowest priced competitors",
                        confidence=0.9,
                        impact_score=0.8,
                        recommendation="Analyze positioning opportunities and consider price adjustments",
                        supporting_data={"price_gap": price_gaps, "gap_percentage": price_gaps/avg_price}
                    ))
            
            # Insight 3: Análisis temporal
            if 'date_collected' in data.columns:
                data['date'] = pd.to_datetime(data['date_collected'])
                daily_prices = data.groupby(data['date'].dt.date)['price'].mean()
                
                if len(daily_prices) > 7:
                    price_trend = (daily_prices.iloc[-1] - daily_prices.iloc[0]) / daily_prices.iloc[0]
                    
                    if abs(price_trend) > 0.1:
                        insights.append(AnalyticsInsight(
                            insight_type="price_trend",
                            title=f"Significant Price Trend Detected",
                            description=f"Prices have {'increased' if price_trend > 0 else 'decreased'} by {abs(price_trend):.1%} over the analysis period",
                            confidence=0.8,
                            impact_score=0.6,
                            recommendation="Monitor trend continuation and adjust strategy accordingly",
                            supporting_data={"trend_percentage": price_trend}
                        ))
            
            # Insight 4: Análisis de categorías
            if 'category' in data.columns:
                category_prices = data.groupby('category')['price'].agg(['mean', 'std', 'count'])
                high_volatility_categories = category_prices[category_prices['std'] / category_prices['mean'] > 0.3]
                
                if len(high_volatility_categories) > 0:
                    insights.append(AnalyticsInsight(
                        insight_type="category_analysis",
                        title="High Volatility Categories Identified",
                        description=f"{len(high_volatility_categories)} categories show high price volatility",
                        confidence=0.75,
                        impact_score=0.5,
                        recommendation="Focus monitoring efforts on high-volatility categories",
                        supporting_data={"volatile_categories": high_volatility_categories.index.tolist()}
                    ))
            
            logger.info(f"Generated {len(insights)} analytics insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating analytics insights: {e}")
            raise
    
    def run_comprehensive_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Ejecutar análisis integral"""
        try:
            logger.info("Running comprehensive analytics analysis...")
            
            results = {}
            
            # Análisis de elasticidad
            results['elasticity_analysis'] = self.perform_price_elasticity_analysis(data)
            
            # Segmentación de mercado
            results['market_segmentation'] = self.perform_market_segmentation(data)
            
            # Análisis de series temporales
            results['time_series_analysis'] = self.perform_time_series_analysis(data)
            
            # Análisis de correlación
            results['correlation_analysis'] = self.perform_correlation_analysis(data)
            
            # Modelos predictivos
            config = AnalyticsConfig(
                analysis_type="price_prediction",
                target_variable="price",
                features=["price_log", "day_of_week", "month", "quarter"],
                model_type="regression"
            )
            results['predictive_models'] = self.build_predictive_models(data, config)
            
            # Insights
            results['insights'] = self.generate_analytics_insights(data)
            
            # Guardar resultados
            self._save_analysis_results(results)
            
            logger.info("Comprehensive analytics analysis completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            raise
    
    def _save_analysis_results(self, results: Dict[str, Any]):
        """Guardar resultados del análisis"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analytics_results_{timestamp}.json"
            filepath = self.results_dir / filename
            
            # Convertir resultados a formato serializable
            serializable_results = self._make_serializable(results)
            
            with open(filepath, 'w') as f:
                json.dump(serializable_results, f, indent=2, default=str)
            
            logger.info(f"Analysis results saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
    
    def _make_serializable(self, obj):
        """Hacer objeto serializable para JSON"""
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return obj

def main():
    """Función principal para demostrar motor de análisis"""
    print("=" * 60)
    print("ADVANCED ANALYTICS ENGINE - DEMO")
    print("=" * 60)
    
    # Inicializar motor de análisis
    analytics_engine = AdvancedAnalyticsEngine()
    
    # Cargar datos
    print("Loading data for analysis...")
    data = analytics_engine.load_data()
    print(f"✓ Loaded {len(data)} records")
    
    # Ejecutar análisis integral
    print("\nRunning comprehensive analysis...")
    results = analytics_engine.run_comprehensive_analysis(data)
    print("✓ Comprehensive analysis completed")
    
    # Mostrar resumen de resultados
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS SUMMARY")
    print("=" * 60)
    
    # Elasticidad
    if 'elasticity_analysis' in results:
        elasticity = results['elasticity_analysis']['elasticity_stats']
        print(f"📊 Price Elasticity Analysis:")
        print(f"   • Mean Elasticity: {elasticity['mean_elasticity']:.3f}")
        print(f"   • Price Volatility: {elasticity['std_elasticity']:.3f}")
    
    # Segmentación
    if 'market_segmentation' in results:
        segments = results['market_segmentation']['clusters']
        print(f"\n🎯 Market Segmentation:")
        print(f"   • Number of Segments: {len(segments)}")
        print(f"   • Silhouette Score: {results['market_segmentation']['silhouette_score']:.3f}")
    
    # Series temporales
    if 'time_series_analysis' in results:
        ts = results['time_series_analysis']
        print(f"\n📈 Time Series Analysis:")
        print(f"   • Stationary: {ts['stationarity_test']['is_stationary']}")
        print(f"   • AIC: {ts['arima_model']['aic']:.2f}")
    
    # Correlación
    if 'correlation_analysis' in results:
        corr = results['correlation_analysis']['correlation_summary']
        print(f"\n🔗 Correlation Analysis:")
        print(f"   • Significant Correlations: {corr['total_correlations']}")
        print(f"   • Strong Correlations: {corr['strong_correlations']}")
    
    # Modelos predictivos
    if 'predictive_models' in results:
        models = results['predictive_models']
        best_model = models[0] if models else None
        if best_model:
            print(f"\n🤖 Predictive Models:")
            print(f"   • Best Model: {best_model.model_name}")
            print(f"   • R² Score: {best_model.metrics['r2']:.3f}")
            print(f"   • RMSE: {best_model.metrics['rmse']:.2f}")
    
    # Insights
    if 'insights' in results:
        insights = results['insights']
        print(f"\n💡 Analytics Insights:")
        print(f"   • Total Insights: {len(insights)}")
        for insight in insights[:3]:  # Mostrar primeros 3
            print(f"   • {insight.title} (Confidence: {insight.confidence:.2f})")
    
    print("\n" + "=" * 60)
    print("ANALYTICS ENGINE DEMO COMPLETED")
    print("=" * 60)
    print("📁 Results saved in analytics_results/")
    print("📊 Charts saved in analytics_charts/")
    print("🤖 Models saved in models/")

if __name__ == "__main__":
    main()






