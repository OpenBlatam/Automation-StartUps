"""
Marketing Brain Marketing Forecasting Optimizer
Motor avanzado de optimización de forecasting de marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class MarketingForecastingOptimizer:
    def __init__(self):
        self.forecasting_data = {}
        self.forecasting_models = {}
        self.forecast_analysis = {}
        self.forecasting_strategies = {}
        self.forecasting_insights = {}
        self.forecast_results = {}
        
    def load_forecasting_data(self, forecasting_data):
        """Cargar datos de forecasting de marketing"""
        if isinstance(forecasting_data, str):
            if forecasting_data.endswith('.csv'):
                self.forecasting_data = pd.read_csv(forecasting_data)
            elif forecasting_data.endswith('.json'):
                with open(forecasting_data, 'r') as f:
                    data = json.load(f)
                self.forecasting_data = pd.DataFrame(data)
        else:
            self.forecasting_data = pd.DataFrame(forecasting_data)
        
        print(f"✅ Datos de forecasting de marketing cargados: {len(self.forecasting_data)} registros")
        return True
    
    def analyze_forecasting_trends(self):
        """Analizar tendencias de forecasting"""
        if self.forecasting_data.empty:
            return None
        
        # Análisis de tendencias por métrica
        metric_trends = self._analyze_metric_trends()
        
        # Análisis de tendencias por canal
        channel_trends = self._analyze_channel_trends()
        
        # Análisis de tendencias por período
        period_trends = self._analyze_period_trends()
        
        # Análisis de estacionalidad
        seasonality_analysis = self._analyze_seasonality()
        
        # Análisis de correlaciones
        correlation_analysis = self._analyze_correlations()
        
        trends_results = {
            'metric_trends': metric_trends,
            'channel_trends': channel_trends,
            'period_trends': period_trends,
            'seasonality_analysis': seasonality_analysis,
            'correlation_analysis': correlation_analysis,
            'overall_trends': self._calculate_overall_trends()
        }
        
        self.forecast_analysis = trends_results
        return trends_results
    
    def _analyze_metric_trends(self):
        """Analizar tendencias por métrica"""
        metric_trends = {}
        
        # Métricas a analizar
        metrics_to_analyze = ['revenue', 'conversions', 'clicks', 'impressions', 'cost']
        
        for metric in metrics_to_analyze:
            if metric in self.forecasting_data.columns:
                # Análisis de tendencia temporal
                if 'date' in self.forecasting_data.columns:
                    self.forecasting_data['date'] = pd.to_datetime(self.forecasting_data['date'])
                    self.forecasting_data['month'] = self.forecasting_data['date'].dt.to_period('M')
                    
                    monthly_data = self.forecasting_data.groupby('month')[metric].sum().reset_index()
                    
                    # Calcular tendencia
                    x = np.arange(len(monthly_data))
                    y = monthly_data[metric].values
                    
                    # Regresión lineal para calcular tendencia
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                    
                    # Calcular crecimiento
                    if len(monthly_data) > 1:
                        first_value = monthly_data[metric].iloc[0]
                        last_value = monthly_data[metric].iloc[-1]
                        growth_rate = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
                    else:
                        growth_rate = 0
                    
                    metric_trends[metric] = {
                        'monthly_data': monthly_data.to_dict('records'),
                        'trend_slope': slope,
                        'trend_intercept': intercept,
                        'trend_r_squared': r_value ** 2,
                        'trend_p_value': p_value,
                        'growth_rate': growth_rate,
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                        'trend_strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.4 else 'weak'
                    }
        
        return metric_trends
    
    def _analyze_channel_trends(self):
        """Analizar tendencias por canal"""
        channel_trends = {}
        
        if 'channel' in self.forecasting_data.columns and 'date' in self.forecasting_data.columns:
            # Análisis de tendencias por canal y métrica
            self.forecasting_data['date'] = pd.to_datetime(self.forecasting_data['date'])
            self.forecasting_data['month'] = self.forecasting_data['date'].dt.to_period('M')
            
            # Métricas a analizar
            metrics_to_analyze = ['revenue', 'conversions', 'clicks', 'impressions', 'cost']
            
            for metric in metrics_to_analyze:
                if metric in self.forecasting_data.columns:
                    channel_metric_data = self.forecasting_data.groupby(['month', 'channel'])[metric].sum().reset_index()
                    
                    # Análisis por canal
                    channel_analysis = {}
                    for channel in self.forecasting_data['channel'].unique():
                        channel_data = channel_metric_data[channel_metric_data['channel'] == channel]
                        
                        if len(channel_data) > 1:
                            x = np.arange(len(channel_data))
                            y = channel_data[metric].values
                            
                            # Regresión lineal
                            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                            
                            # Calcular crecimiento
                            first_value = channel_data[metric].iloc[0]
                            last_value = channel_data[metric].iloc[-1]
                            growth_rate = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
                            
                            channel_analysis[channel] = {
                                'trend_slope': slope,
                                'trend_intercept': intercept,
                                'trend_r_squared': r_value ** 2,
                                'trend_p_value': p_value,
                                'growth_rate': growth_rate,
                                'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                                'trend_strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.4 else 'weak'
                            }
                    
                    channel_trends[metric] = channel_analysis
        
        return channel_trends
    
    def _analyze_period_trends(self):
        """Analizar tendencias por período"""
        period_trends = {}
        
        if 'date' in self.forecasting_data.columns:
            # Análisis de tendencias por día de la semana
            self.forecasting_data['date'] = pd.to_datetime(self.forecasting_data['date'])
            self.forecasting_data['day_of_week'] = self.forecasting_data['date'].dt.day_name()
            
            daily_trends = self.forecasting_data.groupby('day_of_week').agg({
                'revenue': 'mean',
                'conversions': 'mean',
                'clicks': 'mean',
                'impressions': 'mean',
                'cost': 'mean'
            }).reset_index()
            
            # Análisis de tendencias por hora del día
            self.forecasting_data['hour'] = self.forecasting_data['date'].dt.hour
            
            hourly_trends = self.forecasting_data.groupby('hour').agg({
                'revenue': 'mean',
                'conversions': 'mean',
                'clicks': 'mean',
                'impressions': 'mean',
                'cost': 'mean'
            }).reset_index()
            
            # Análisis de tendencias por mes del año
            self.forecasting_data['month_of_year'] = self.forecasting_data['date'].dt.month
            
            monthly_trends = self.forecasting_data.groupby('month_of_year').agg({
                'revenue': 'mean',
                'conversions': 'mean',
                'clicks': 'mean',
                'impressions': 'mean',
                'cost': 'mean'
            }).reset_index()
            
            period_trends = {
                'daily_trends': daily_trends.to_dict('records'),
                'hourly_trends': hourly_trends.to_dict('records'),
                'monthly_trends': monthly_trends.to_dict('records')
            }
        
        return period_trends
    
    def _analyze_seasonality(self):
        """Analizar estacionalidad"""
        seasonality_analysis = {}
        
        if 'date' in self.forecasting_data.columns:
            # Análisis de estacionalidad por mes
            self.forecasting_data['date'] = pd.to_datetime(self.forecasting_data['date'])
            self.forecasting_data['month'] = self.forecasting_data['date'].dt.month
            
            # Métricas a analizar
            metrics_to_analyze = ['revenue', 'conversions', 'clicks', 'impressions', 'cost']
            
            for metric in metrics_to_analyze:
                if metric in self.forecasting_data.columns:
                    monthly_data = self.forecasting_data.groupby('month')[metric].mean().reset_index()
                    
                    # Calcular coeficiente de variación para medir estacionalidad
                    mean_value = monthly_data[metric].mean()
                    std_value = monthly_data[metric].std()
                    coefficient_of_variation = (std_value / mean_value) * 100 if mean_value > 0 else 0
                    
                    # Identificar meses pico y valle
                    peak_month = monthly_data.loc[monthly_data[metric].idxmax(), 'month']
                    valley_month = monthly_data.loc[monthly_data[metric].idxmin(), 'month']
                    
                    # Calcular ratio pico/valle
                    peak_value = monthly_data[metric].max()
                    valley_value = monthly_data[metric].min()
                    peak_valley_ratio = peak_value / valley_value if valley_value > 0 else 0
                    
                    seasonality_analysis[metric] = {
                        'monthly_data': monthly_data.to_dict('records'),
                        'coefficient_of_variation': coefficient_of_variation,
                        'peak_month': peak_month,
                        'valley_month': valley_month,
                        'peak_valley_ratio': peak_valley_ratio,
                        'seasonality_strength': 'strong' if coefficient_of_variation > 30 else 'moderate' if coefficient_of_variation > 15 else 'weak'
                    }
        
        return seasonality_analysis
    
    def _analyze_correlations(self):
        """Analizar correlaciones"""
        correlation_analysis = {}
        
        # Métricas a analizar
        metrics_to_analyze = ['revenue', 'conversions', 'clicks', 'impressions', 'cost']
        available_metrics = [metric for metric in metrics_to_analyze if metric in self.forecasting_data.columns]
        
        if len(available_metrics) > 1:
            # Calcular matriz de correlación
            correlation_matrix = self.forecasting_data[available_metrics].corr()
            
            # Encontrar correlaciones fuertes
            strong_correlations = []
            for i in range(len(available_metrics)):
                for j in range(i+1, len(available_metrics)):
                    metric1 = available_metrics[i]
                    metric2 = available_metrics[j]
                    correlation = correlation_matrix.loc[metric1, metric2]
                    
                    if abs(correlation) > 0.7:
                        strong_correlations.append({
                            'metric1': metric1,
                            'metric2': metric2,
                            'correlation': correlation,
                            'strength': 'strong'
                        })
                    elif abs(correlation) > 0.4:
                        strong_correlations.append({
                            'metric1': metric1,
                            'metric2': metric2,
                            'correlation': correlation,
                            'strength': 'moderate'
                        })
            
            correlation_analysis = {
                'correlation_matrix': correlation_matrix.to_dict(),
                'strong_correlations': strong_correlations,
                'correlation_summary': {
                    'total_correlations': len(strong_correlations),
                    'strong_correlations': len([c for c in strong_correlations if c['strength'] == 'strong']),
                    'moderate_correlations': len([c for c in strong_correlations if c['strength'] == 'moderate'])
                }
            }
        
        return correlation_analysis
    
    def _calculate_overall_trends(self):
        """Calcular tendencias generales"""
        overall_trends = {}
        
        if not self.forecasting_data.empty:
            # Métricas a analizar
            metrics_to_analyze = ['revenue', 'conversions', 'clicks', 'impressions', 'cost']
            
            for metric in metrics_to_analyze:
                if metric in self.forecasting_data.columns:
                    # Calcular tendencia general
                    if 'date' in self.forecasting_data.columns:
                        self.forecasting_data['date'] = pd.to_datetime(self.forecasting_data['date'])
                        self.forecasting_data['month'] = self.forecasting_data['date'].dt.to_period('M')
                        
                        monthly_data = self.forecasting_data.groupby('month')[metric].sum().reset_index()
                        
                        if len(monthly_data) > 1:
                            x = np.arange(len(monthly_data))
                            y = monthly_data[metric].values
                            
                            # Regresión lineal
                            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                            
                            # Calcular crecimiento
                            first_value = monthly_data[metric].iloc[0]
                            last_value = monthly_data[metric].iloc[-1]
                            growth_rate = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
                            
                            overall_trends[metric] = {
                                'trend_slope': slope,
                                'trend_intercept': intercept,
                                'trend_r_squared': r_value ** 2,
                                'trend_p_value': p_value,
                                'growth_rate': growth_rate,
                                'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                                'trend_strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.4 else 'weak'
                            }
        
        return overall_trends
    
    def build_forecasting_models(self, target_metric='revenue', forecast_periods=12):
        """Construir modelos de forecasting"""
        if target_metric not in self.forecasting_data.columns:
            raise ValueError(f"Métrica objetivo '{target_metric}' no encontrada")
        
        # Preparar datos para forecasting
        forecasting_data = self._prepare_forecasting_data(target_metric)
        
        # Construir diferentes modelos de forecasting
        forecasting_models = {}
        
        # Modelo de tendencia lineal
        linear_model = self._build_linear_forecasting_model(forecasting_data, target_metric)
        forecasting_models['linear'] = linear_model
        
        # Modelo de tendencia exponencial
        exponential_model = self._build_exponential_forecasting_model(forecasting_data, target_metric)
        forecasting_models['exponential'] = exponential_model
        
        # Modelo de tendencia polinomial
        polynomial_model = self._build_polynomial_forecasting_model(forecasting_data, target_metric)
        forecasting_models['polynomial'] = polynomial_model
        
        # Modelo de tendencia estacional
        seasonal_model = self._build_seasonal_forecasting_model(forecasting_data, target_metric)
        forecasting_models['seasonal'] = seasonal_model
        
        # Modelo de machine learning
        ml_model = self._build_ml_forecasting_model(forecasting_data, target_metric)
        forecasting_models['ml'] = ml_model
        
        # Generar forecast
        forecast_results = self._generate_forecast(forecasting_models, forecast_periods)
        
        # Evaluar modelos
        model_evaluation = self._evaluate_forecasting_models(forecasting_models, forecasting_data)
        
        self.forecasting_models = {
            'models': forecasting_models,
            'forecast_results': forecast_results,
            'model_evaluation': model_evaluation
        }
        
        return self.forecasting_models
    
    def _prepare_forecasting_data(self, target_metric):
        """Preparar datos para forecasting"""
        if 'date' not in self.forecasting_data.columns:
            raise ValueError("Columna 'date' no encontrada")
        
        # Agrupar por fecha
        self.forecasting_data['date'] = pd.to_datetime(self.forecasting_data['date'])
        self.forecasting_data['month'] = self.forecasting_data['date'].dt.to_period('M')
        
        forecasting_data = self.forecasting_data.groupby('month')[target_metric].sum().reset_index()
        forecasting_data['date'] = forecasting_data['month'].dt.to_timestamp()
        forecasting_data = forecasting_data.sort_values('date')
        
        return forecasting_data
    
    def _build_linear_forecasting_model(self, forecasting_data, target_metric):
        """Construir modelo de forecasting lineal"""
        x = np.arange(len(forecasting_data))
        y = forecasting_data[target_metric].values
        
        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Calcular métricas de error
        y_pred = slope * x + intercept
        mse = np.mean((y - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y - y_pred))
        
        return {
            'type': 'linear',
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'predict_function': lambda x: slope * x + intercept
        }
    
    def _build_exponential_forecasting_model(self, forecasting_data, target_metric):
        """Construir modelo de forecasting exponencial"""
        x = np.arange(len(forecasting_data))
        y = forecasting_data[target_metric].values
        
        # Aplicar logaritmo para linealizar
        y_log = np.log(y + 1)  # +1 para evitar log(0)
        
        # Regresión lineal en escala logarítmica
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y_log)
        
        # Calcular métricas de error
        y_pred_log = slope * x + intercept
        y_pred = np.exp(y_pred_log) - 1
        mse = np.mean((y - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y - y_pred))
        
        return {
            'type': 'exponential',
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'predict_function': lambda x: np.exp(slope * x + intercept) - 1
        }
    
    def _build_polynomial_forecasting_model(self, forecasting_data, target_metric):
        """Construir modelo de forecasting polinomial"""
        x = np.arange(len(forecasting_data))
        y = forecasting_data[target_metric].values
        
        # Ajustar polinomio de grado 2
        coeffs = np.polyfit(x, y, 2)
        
        # Calcular métricas de error
        y_pred = np.polyval(coeffs, x)
        mse = np.mean((y - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y - y_pred))
        
        # Calcular R²
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        return {
            'type': 'polynomial',
            'coefficients': coeffs.tolist(),
            'r_squared': r_squared,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'predict_function': lambda x: np.polyval(coeffs, x)
        }
    
    def _build_seasonal_forecasting_model(self, forecasting_data, target_metric):
        """Construir modelo de forecasting estacional"""
        x = np.arange(len(forecasting_data))
        y = forecasting_data[target_metric].values
        
        # Calcular componente estacional
        seasonal_component = self._calculate_seasonal_component(forecasting_data, target_metric)
        
        # Remover estacionalidad
        y_deseasonalized = y - seasonal_component
        
        # Ajustar tendencia a datos desestacionalizados
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y_deseasonalized)
        
        # Calcular métricas de error
        y_pred = slope * x + intercept + seasonal_component
        mse = np.mean((y - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y - y_pred))
        
        return {
            'type': 'seasonal',
            'slope': slope,
            'intercept': intercept,
            'seasonal_component': seasonal_component.tolist(),
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'predict_function': lambda x: slope * x + intercept + seasonal_component[x % len(seasonal_component)]
        }
    
    def _calculate_seasonal_component(self, forecasting_data, target_metric):
        """Calcular componente estacional"""
        # Agrupar por mes del año
        forecasting_data['month_of_year'] = forecasting_data['date'].dt.month
        monthly_means = forecasting_data.groupby('month_of_year')[target_metric].mean()
        
        # Calcular desviación de la media general
        overall_mean = forecasting_data[target_metric].mean()
        seasonal_component = monthly_means - overall_mean
        
        # Aplicar a cada observación
        seasonal_values = []
        for _, row in forecasting_data.iterrows():
            month = row['month_of_year']
            seasonal_values.append(seasonal_component[month])
        
        return np.array(seasonal_values)
    
    def _build_ml_forecasting_model(self, forecasting_data, target_metric):
        """Construir modelo de forecasting de machine learning"""
        # Crear características
        features = self._create_ml_features(forecasting_data)
        target = forecasting_data[target_metric].values
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test)
        mse = np.mean((y_test - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_test - y_pred))
        
        # Calcular R²
        from sklearn.metrics import r2_score
        r_squared = r2_score(y_test, y_pred)
        
        return {
            'type': 'ml',
            'model': model,
            'r_squared': r_squared,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'feature_importance': dict(zip(features.columns, model.feature_importances_))
        }
    
    def _create_ml_features(self, forecasting_data):
        """Crear características para modelo de ML"""
        features = pd.DataFrame()
        
        # Características temporales
        features['month'] = forecasting_data['date'].dt.month
        features['quarter'] = forecasting_data['date'].dt.quarter
        features['year'] = forecasting_data['date'].dt.year
        
        # Características de tendencia
        features['trend'] = np.arange(len(forecasting_data))
        
        # Características de estacionalidad
        features['sin_month'] = np.sin(2 * np.pi * features['month'] / 12)
        features['cos_month'] = np.cos(2 * np.pi * features['month'] / 12)
        
        # Características de lag
        if len(forecasting_data) > 1:
            features['lag_1'] = forecasting_data[forecasting_data.columns[1]].shift(1).fillna(0)
            if len(forecasting_data) > 2:
                features['lag_2'] = forecasting_data[forecasting_data.columns[1]].shift(2).fillna(0)
        
        return features.fillna(0)
    
    def _generate_forecast(self, forecasting_models, forecast_periods):
        """Generar forecast"""
        forecast_results = {}
        
        for model_name, model in forecasting_models['models'].items():
            if model_name == 'ml':
                # Para modelo de ML, necesitamos crear características futuras
                future_features = self._create_future_ml_features(forecast_periods)
                forecast = model['model'].predict(future_features)
            else:
                # Para modelos matemáticos
                future_periods = np.arange(len(self.forecasting_data), len(self.forecasting_data) + forecast_periods)
                forecast = model['predict_function'](future_periods)
            
            forecast_results[model_name] = {
                'forecast': forecast.tolist(),
                'forecast_periods': forecast_periods,
                'model_metrics': {
                    'r_squared': model.get('r_squared', 0),
                    'mse': model.get('mse', 0),
                    'rmse': model.get('rmse', 0),
                    'mae': model.get('mae', 0)
                }
            }
        
        return forecast_results
    
    def _create_future_ml_features(self, forecast_periods):
        """Crear características futuras para modelo de ML"""
        features = pd.DataFrame()
        
        # Características temporales futuras
        last_date = self.forecasting_data['date'].iloc[-1]
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_periods, freq='M')
        
        features['month'] = future_dates.month
        features['quarter'] = future_dates.quarter
        features['year'] = future_dates.year
        
        # Características de tendencia
        features['trend'] = np.arange(len(self.forecasting_data), len(self.forecasting_data) + forecast_periods)
        
        # Características de estacionalidad
        features['sin_month'] = np.sin(2 * np.pi * features['month'] / 12)
        features['cos_month'] = np.cos(2 * np.pi * features['month'] / 12)
        
        # Características de lag (usar últimos valores conocidos)
        if len(self.forecasting_data) > 1:
            last_value = self.forecasting_data.iloc[-1, 1]
            features['lag_1'] = [last_value] * forecast_periods
            if len(self.forecasting_data) > 2:
                second_last_value = self.forecasting_data.iloc[-2, 1]
                features['lag_2'] = [second_last_value] * forecast_periods
        
        return features.fillna(0)
    
    def _evaluate_forecasting_models(self, forecasting_models, forecasting_data):
        """Evaluar modelos de forecasting"""
        model_evaluation = {}
        
        for model_name, model in forecasting_models['models'].items():
            # Calcular métricas de evaluación
            evaluation_metrics = {
                'r_squared': model.get('r_squared', 0),
                'mse': model.get('mse', 0),
                'rmse': model.get('rmse', 0),
                'mae': model.get('mae', 0)
            }
            
            # Calcular score de evaluación
            evaluation_score = 0
            
            # R² (40% del score)
            r_squared = evaluation_metrics['r_squared']
            if r_squared > 0.8:
                evaluation_score += 40
            elif r_squared > 0.6:
                evaluation_score += 30
            elif r_squared > 0.4:
                evaluation_score += 20
            else:
                evaluation_score += 10
            
            # RMSE (30% del score)
            rmse = evaluation_metrics['rmse']
            if rmse < 1000:
                evaluation_score += 30
            elif rmse < 5000:
                evaluation_score += 20
            elif rmse < 10000:
                evaluation_score += 10
            
            # MAE (30% del score)
            mae = evaluation_metrics['mae']
            if mae < 500:
                evaluation_score += 30
            elif mae < 2000:
                evaluation_score += 20
            elif mae < 5000:
                evaluation_score += 10
            
            model_evaluation[model_name] = {
                'evaluation_metrics': evaluation_metrics,
                'evaluation_score': evaluation_score,
                'model_quality': 'excellent' if evaluation_score >= 80 else 'good' if evaluation_score >= 60 else 'fair' if evaluation_score >= 40 else 'poor'
            }
        
        # Ordenar modelos por score
        sorted_models = sorted(model_evaluation.items(), key=lambda x: x[1]['evaluation_score'], reverse=True)
        
        return {
            'model_evaluation': model_evaluation,
            'best_model': sorted_models[0][0] if sorted_models else None,
            'model_ranking': [model[0] for model in sorted_models]
        }
    
    def generate_forecasting_strategies(self):
        """Generar estrategias de forecasting"""
        strategies = []
        
        # Estrategias basadas en análisis de tendencias
        if self.forecast_analysis:
            overall_trends = self.forecast_analysis.get('overall_trends', {})
            
            for metric, trend_data in overall_trends.items():
                trend_direction = trend_data.get('trend_direction', 'unknown')
                growth_rate = trend_data.get('growth_rate', 0)
                
                if trend_direction == 'increasing' and growth_rate > 10:
                    strategies.append({
                        'strategy_type': 'Scale Up',
                        'description': f'Escalar {metric} - tendencia creciente con {growth_rate:.1f}% de crecimiento',
                        'priority': 'high',
                        'expected_impact': 'high'
                    })
                elif trend_direction == 'decreasing' and growth_rate < -10:
                    strategies.append({
                        'strategy_type': 'Scale Down',
                        'description': f'Reducir {metric} - tendencia decreciente con {growth_rate:.1f}% de declive',
                        'priority': 'high',
                        'expected_impact': 'high'
                    })
        
        # Estrategias basadas en estacionalidad
        if self.forecast_analysis:
            seasonality_analysis = self.forecast_analysis.get('seasonality_analysis', {})
            
            for metric, seasonality_data in seasonality_analysis.items():
                seasonality_strength = seasonality_data.get('seasonality_strength', 'weak')
                peak_month = seasonality_data.get('peak_month', 0)
                
                if seasonality_strength == 'strong':
                    strategies.append({
                        'strategy_type': 'Seasonal Optimization',
                        'description': f'Optimizar {metric} para estacionalidad - pico en mes {peak_month}',
                        'priority': 'medium',
                        'expected_impact': 'medium'
                    })
        
        # Estrategias basadas en modelos de forecasting
        if self.forecasting_models:
            model_evaluation = self.forecasting_models.get('model_evaluation', {})
            best_model = model_evaluation.get('best_model', None)
            
            if best_model:
                strategies.append({
                    'strategy_type': 'Model Selection',
                    'description': f'Usar modelo {best_model} para forecasting - mejor performance',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        self.forecasting_strategies = strategies
        return strategies
    
    def generate_forecasting_insights(self):
        """Generar insights de forecasting"""
        insights = []
        
        # Insights de tendencias
        if self.forecast_analysis:
            overall_trends = self.forecast_analysis.get('overall_trends', {})
            
            for metric, trend_data in overall_trends.items():
                trend_direction = trend_data.get('trend_direction', 'unknown')
                growth_rate = trend_data.get('growth_rate', 0)
                trend_strength = trend_data.get('trend_strength', 'weak')
                
                if trend_strength == 'strong':
                    insights.append({
                        'category': 'Trend Analysis',
                        'insight': f'{metric} muestra tendencia {trend_direction} fuerte con {growth_rate:.1f}% de crecimiento',
                        'recommendation': f'{"Mantener" if trend_direction == "increasing" else "Revisar"} estrategias de {metric}',
                        'priority': 'high'
                    })
        
        # Insights de estacionalidad
        if self.forecast_analysis:
            seasonality_analysis = self.forecast_analysis.get('seasonality_analysis', {})
            
            for metric, seasonality_data in seasonality_analysis.items():
                seasonality_strength = seasonality_data.get('seasonality_strength', 'weak')
                peak_month = seasonality_data.get('peak_month', 0)
                valley_month = seasonality_data.get('valley_month', 0)
                
                if seasonality_strength == 'strong':
                    insights.append({
                        'category': 'Seasonality Analysis',
                        'insight': f'{metric} muestra estacionalidad fuerte - pico en mes {peak_month}, valle en mes {valley_month}',
                        'recommendation': 'Ajustar estrategias según estacionalidad',
                        'priority': 'medium'
                    })
        
        # Insights de correlaciones
        if self.forecast_analysis:
            correlation_analysis = self.forecast_analysis.get('correlation_analysis', {})
            strong_correlations = correlation_analysis.get('strong_correlations', [])
            
            if strong_correlations:
                insights.append({
                    'category': 'Correlation Analysis',
                    'insight': f'{len(strong_correlations)} correlaciones fuertes encontradas entre métricas',
                    'recommendation': 'Aprovechar correlaciones para forecasting',
                    'priority': 'low'
                })
        
        # Insights de modelos
        if self.forecasting_models:
            model_evaluation = self.forecasting_models.get('model_evaluation', {})
            best_model = model_evaluation.get('best_model', None)
            
            if best_model:
                best_model_data = model_evaluation.get('model_evaluation', {}).get(best_model, {})
                model_quality = best_model_data.get('model_quality', 'unknown')
                
                insights.append({
                    'category': 'Model Performance',
                    'insight': f'Mejor modelo de forecasting: {best_model} con calidad {model_quality}',
                    'recommendation': 'Usar este modelo para forecasting',
                    'priority': 'medium'
                })
        
        self.forecasting_insights = insights
        return insights
    
    def create_forecasting_dashboard(self):
        """Crear dashboard de forecasting"""
        if not self.forecasting_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Trend Analysis', 'Seasonality Analysis',
                          'Model Performance', 'Forecast Results'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Gráfico de análisis de tendencias
        if self.forecast_analysis:
            overall_trends = self.forecast_analysis.get('overall_trends', {})
            
            if 'revenue' in overall_trends:
                trend_data = overall_trends['revenue']
                monthly_data = trend_data.get('monthly_data', [])
                
                if monthly_data:
                    months = [data['month'] for data in monthly_data]
                    values = [data['revenue'] for data in monthly_data]
                    
                    fig.add_trace(
                        go.Scatter(x=months, y=values, mode='lines+markers', name='Revenue Trend'),
                        row=1, col=1
                    )
        
        # Gráfico de análisis de estacionalidad
        if self.forecast_analysis:
            seasonality_analysis = self.forecast_analysis.get('seasonality_analysis', {})
            
            if 'revenue' in seasonality_analysis:
                seasonality_data = seasonality_analysis['revenue']
                monthly_data = seasonality_data.get('monthly_data', [])
                
                if monthly_data:
                    months = [data['month'] for data in monthly_data]
                    values = [data['revenue'] for data in monthly_data]
                    
                    fig.add_trace(
                        go.Bar(x=months, y=values, name='Seasonal Revenue'),
                        row=1, col=2
                    )
        
        # Gráfico de performance de modelos
        if self.forecasting_models:
            model_evaluation = self.forecasting_models.get('model_evaluation', {})
            model_evaluation_data = model_evaluation.get('model_evaluation', {})
            
            if model_evaluation_data:
                models = list(model_evaluation_data.keys())
                scores = [data['evaluation_score'] for data in model_evaluation_data.values()]
                
                fig.add_trace(
                    go.Bar(x=models, y=scores, name='Model Performance'),
                    row=2, col=1
                )
        
        # Gráfico de resultados de forecast
        if self.forecasting_models:
            forecast_results = self.forecasting_models.get('forecast_results', {})
            
            if 'linear' in forecast_results:
                linear_forecast = forecast_results['linear']
                forecast_values = linear_forecast.get('forecast', [])
                
                if forecast_values:
                    periods = list(range(len(forecast_values)))
                    
                    fig.add_trace(
                        go.Scatter(x=periods, y=forecast_values, mode='lines+markers', name='Linear Forecast'),
                        row=2, col=2
                    )
        
        fig.update_layout(
            title="Dashboard de Marketing Forecasting",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_forecasting_analysis(self, filename='marketing_forecasting_analysis.json'):
        """Exportar análisis de forecasting"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'forecast_analysis': self.forecast_analysis,
            'forecasting_models': {k: {'model_evaluation': v.get('model_evaluation', {}), 'forecast_results': v.get('forecast_results', {})} for k, v in self.forecasting_models.items()},
            'forecasting_strategies': self.forecasting_strategies,
            'forecasting_insights': self.forecasting_insights,
            'summary': {
                'total_periods': len(self.forecasting_data) if 'date' in self.forecasting_data.columns else 0,
                'forecast_periods': 12,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de forecasting exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de forecasting de marketing
    forecasting_optimizer = MarketingForecastingOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=24, freq='M'),
        'revenue': np.random.normal(100000, 20000, 24) + np.sin(np.arange(24) * 2 * np.pi / 12) * 10000,
        'conversions': np.random.poisson(1000, 24) + np.sin(np.arange(24) * 2 * np.pi / 12) * 100,
        'clicks': np.random.poisson(10000, 24) + np.sin(np.arange(24) * 2 * np.pi / 12) * 1000,
        'impressions': np.random.poisson(100000, 24) + np.sin(np.arange(24) * 2 * np.pi / 12) * 10000,
        'cost': np.random.normal(50000, 10000, 24) + np.sin(np.arange(24) * 2 * np.pi / 12) * 5000,
        'channel': np.random.choice(['Email', 'Social Media', 'Paid Search', 'Display'], 24)
    })
    
    # Cargar datos de forecasting de marketing
    print("📊 Cargando datos de forecasting de marketing...")
    forecasting_optimizer.load_forecasting_data(sample_data)
    
    # Analizar tendencias de forecasting
    print("📈 Analizando tendencias de forecasting...")
    forecast_analysis = forecasting_optimizer.analyze_forecasting_trends()
    
    # Construir modelos de forecasting
    print("🔮 Construyendo modelos de forecasting...")
    forecasting_models = forecasting_optimizer.build_forecasting_models(target_metric='revenue', forecast_periods=12)
    
    # Generar estrategias de forecasting
    print("🎯 Generando estrategias de forecasting...")
    forecasting_strategies = forecasting_optimizer.generate_forecasting_strategies()
    
    # Generar insights de forecasting
    print("💡 Generando insights de forecasting...")
    forecasting_insights = forecasting_optimizer.generate_forecasting_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de forecasting...")
    dashboard = forecasting_optimizer.create_forecasting_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de forecasting...")
    export_data = forecasting_optimizer.export_forecasting_analysis()
    
    print("✅ Sistema de optimización de forecasting de marketing completado!")




