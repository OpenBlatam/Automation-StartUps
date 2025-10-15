"""
Marketing Brain Predictive Market Analyzer
Sistema avanzado de análisis predictivo de mercado
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import scipy.stats as stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class PredictiveMarketAnalyzer:
    def __init__(self):
        self.market_data = {}
        self.prediction_models = {}
        self.trend_analysis = {}
        self.seasonality_analysis = {}
        self.competitive_analysis = {}
        self.opportunity_analysis = {}
        self.risk_assessment = {}
        
    def load_market_data(self, market_data):
        """Cargar datos de mercado"""
        if isinstance(market_data, str):
            if market_data.endswith('.csv'):
                self.market_data = pd.read_csv(market_data)
            elif market_data.endswith('.json'):
                with open(market_data, 'r') as f:
                    data = json.load(f)
                self.market_data = pd.DataFrame(data)
        else:
            self.market_data = pd.DataFrame(market_data)
        
        print(f"✅ Datos de mercado cargados: {len(self.market_data)} registros")
        return True
    
    def analyze_market_trends(self, time_period='12M'):
        """Analizar tendencias del mercado"""
        if self.market_data.empty:
            return None
        
        # Preparar datos temporales
        if 'date' in self.market_data.columns:
            self.market_data['date'] = pd.to_datetime(self.market_data['date'])
            self.market_data = self.market_data.sort_values('date')
        
        # Análisis de tendencias por período
        if time_period == '12M':
            cutoff_date = datetime.now() - timedelta(days=365)
        elif time_period == '6M':
            cutoff_date = datetime.now() - timedelta(days=180)
        elif time_period == '3M':
            cutoff_date = datetime.now() - timedelta(days=90)
        else:
            cutoff_date = datetime.now() - timedelta(days=30)
        
        recent_data = self.market_data[self.market_data['date'] >= cutoff_date] if 'date' in self.market_data.columns else self.market_data
        
        # Análisis de tendencias
        trends = {}
        
        # Tendencias de volumen
        if 'volume' in recent_data.columns:
            volume_trend = self._calculate_trend(recent_data['volume'])
            trends['volume_trend'] = volume_trend
        
        # Tendencias de precio
        if 'price' in recent_data.columns:
            price_trend = self._calculate_trend(recent_data['price'])
            trends['price_trend'] = price_trend
        
        # Tendencias de demanda
        if 'demand' in recent_data.columns:
            demand_trend = self._calculate_trend(recent_data['demand'])
            trends['demand_trend'] = demand_trend
        
        # Análisis de volatilidad
        if 'price' in recent_data.columns:
            price_volatility = recent_data['price'].std() / recent_data['price'].mean()
            trends['price_volatility'] = price_volatility
        
        # Análisis de crecimiento
        if 'revenue' in recent_data.columns:
            growth_rate = self._calculate_growth_rate(recent_data['revenue'])
            trends['growth_rate'] = growth_rate
        
        # Análisis de estacionalidad
        seasonal_patterns = self._analyze_seasonality(recent_data)
        trends['seasonal_patterns'] = seasonal_patterns
        
        # Análisis de correlaciones
        correlations = self._analyze_correlations(recent_data)
        trends['correlations'] = correlations
        
        self.trend_analysis[time_period] = trends
        return trends
    
    def _calculate_trend(self, data):
        """Calcular tendencia de una serie de datos"""
        if len(data) < 2:
            return {'direction': 'stable', 'slope': 0, 'strength': 0}
        
        # Regresión lineal simple
        x = np.arange(len(data))
        y = data.values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Clasificar tendencia
        if slope > 0.1:
            direction = 'increasing'
        elif slope < -0.1:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': slope,
            'strength': abs(r_value),
            'p_value': p_value,
            'r_squared': r_value ** 2
        }
    
    def _calculate_growth_rate(self, data):
        """Calcular tasa de crecimiento"""
        if len(data) < 2:
            return 0
        
        # Crecimiento compuesto anual
        first_value = data.iloc[0]
        last_value = data.iloc[-1]
        periods = len(data)
        
        if first_value > 0:
            growth_rate = ((last_value / first_value) ** (1 / periods)) - 1
        else:
            growth_rate = 0
        
        return growth_rate
    
    def _analyze_seasonality(self, data):
        """Analizar patrones estacionales"""
        if 'date' not in data.columns:
            return {}
        
        # Extraer componentes temporales
        data['month'] = data['date'].dt.month
        data['quarter'] = data['date'].dt.quarter
        data['day_of_week'] = data['date'].dt.dayofweek
        
        seasonal_patterns = {}
        
        # Análisis mensual
        if 'revenue' in data.columns:
            monthly_avg = data.groupby('month')['revenue'].mean()
            seasonal_patterns['monthly'] = monthly_avg.to_dict()
        
        # Análisis trimestral
        if 'revenue' in data.columns:
            quarterly_avg = data.groupby('quarter')['revenue'].mean()
            seasonal_patterns['quarterly'] = quarterly_avg.to_dict()
        
        # Análisis por día de la semana
        if 'revenue' in data.columns:
            daily_avg = data.groupby('day_of_week')['revenue'].mean()
            seasonal_patterns['daily'] = daily_avg.to_dict()
        
        return seasonal_patterns
    
    def _analyze_correlations(self, data):
        """Analizar correlaciones entre variables"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) < 2:
            return {}
        
        correlation_matrix = data[numeric_columns].corr()
        
        # Encontrar correlaciones fuertes
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Correlación fuerte
                    strong_correlations.append({
                        'variable1': correlation_matrix.columns[i],
                        'variable2': correlation_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations
        }
    
    def build_prediction_models(self, target_variable, features=None):
        """Construir modelos de predicción"""
        if target_variable not in self.market_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        if features is None:
            features = [col for col in self.market_data.columns if col != target_variable and col != 'date']
        
        X = self.market_data[features]
        y = self.market_data[target_variable]
        
        # Codificar variables categóricas
        label_encoders = {}
        for column in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[column] = le.fit_transform(X[column].astype(str))
            label_encoders[column] = le
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar datos
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Entrenar modelos
        models = {}
        
        # Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        rf_pred = rf_model.predict(X_test_scaled)
        
        models['random_forest'] = {
            'model': rf_model,
            'predictions': rf_pred,
            'metrics': {
                'mse': mean_squared_error(y_test, rf_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, rf_pred)),
                'mae': mean_absolute_error(y_test, rf_pred),
                'r2': r2_score(y_test, rf_pred)
            },
            'feature_importance': dict(zip(features, rf_model.feature_importances_))
        }
        
        # Gradient Boosting
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gb_model.fit(X_train_scaled, y_train)
        gb_pred = gb_model.predict(X_test_scaled)
        
        models['gradient_boosting'] = {
            'model': gb_model,
            'predictions': gb_pred,
            'metrics': {
                'mse': mean_squared_error(y_test, gb_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, gb_pred)),
                'mae': mean_absolute_error(y_test, gb_pred),
                'r2': r2_score(y_test, gb_pred)
            },
            'feature_importance': dict(zip(features, gb_model.feature_importances_))
        }
        
        # Seleccionar mejor modelo
        best_model_name = min(models.keys(), key=lambda x: models[x]['metrics']['mse'])
        best_model = models[best_model_name]
        
        self.prediction_models[target_variable] = {
            'models': models,
            'best_model': best_model_name,
            'features': features,
            'label_encoders': label_encoders,
            'scaler': scaler,
            'test_data': {
                'X_test': X_test,
                'y_test': y_test
            }
        }
        
        return self.prediction_models[target_variable]
    
    def predict_market_behavior(self, target_variable, forecast_periods=12):
        """Predecir comportamiento del mercado"""
        if target_variable not in self.prediction_models:
            raise ValueError(f"Modelo para '{target_variable}' no encontrado")
        
        model_info = self.prediction_models[target_variable]
        best_model = model_info['models'][model_info['best_model']]['model']
        features = model_info['features']
        scaler = model_info['scaler']
        
        # Preparar datos para predicción
        if 'date' in self.market_data.columns:
            # Usar datos más recientes para predicción
            recent_data = self.market_data.tail(1)[features]
        else:
            recent_data = self.market_data.tail(1)[features]
        
        # Codificar variables categóricas
        for column in recent_data.select_dtypes(include=['object']).columns:
            if column in model_info['label_encoders']:
                le = model_info['label_encoders'][column]
                recent_data[column] = le.transform(recent_data[column].astype(str))
        
        # Escalar datos
        recent_data_scaled = scaler.transform(recent_data)
        
        # Generar predicciones
        predictions = []
        current_data = recent_data_scaled.copy()
        
        for period in range(forecast_periods):
            # Predecir siguiente período
            pred = best_model.predict(current_data)[0]
            predictions.append(pred)
            
            # Actualizar datos para siguiente predicción (simplificado)
            # En un caso real, esto sería más complejo
            current_data[0][0] = pred  # Asumir que la primera característica es la variable objetivo
        
        # Crear fechas futuras
        if 'date' in self.market_data.columns:
            last_date = self.market_data['date'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_periods, freq='M')
        else:
            future_dates = [datetime.now() + timedelta(days=30*i) for i in range(1, forecast_periods+1)]
        
        # Crear DataFrame de predicciones
        predictions_df = pd.DataFrame({
            'date': future_dates,
            'predicted_value': predictions,
            'confidence_interval_lower': [p * 0.9 for p in predictions],  # Simplificado
            'confidence_interval_upper': [p * 1.1 for p in predictions]   # Simplificado
        })
        
        return predictions_df
    
    def analyze_market_opportunities(self, market_segments=None):
        """Analizar oportunidades de mercado"""
        if market_segments is None:
            market_segments = ['geographic', 'demographic', 'product', 'channel']
        
        opportunities = {}
        
        for segment in market_segments:
            if segment == 'geographic' and 'region' in self.market_data.columns:
                opportunities['geographic'] = self._analyze_geographic_opportunities()
            elif segment == 'demographic' and 'age_group' in self.market_data.columns:
                opportunities['demographic'] = self._analyze_demographic_opportunities()
            elif segment == 'product' and 'product_category' in self.market_data.columns:
                opportunities['product'] = self._analyze_product_opportunities()
            elif segment == 'channel' and 'channel' in self.market_data.columns:
                opportunities['channel'] = self._analyze_channel_opportunities()
        
        # Análisis de gaps de mercado
        market_gaps = self._identify_market_gaps()
        opportunities['market_gaps'] = market_gaps
        
        # Análisis de nichos
        niches = self._identify_market_niches()
        opportunities['market_niches'] = niches
        
        self.opportunity_analysis = opportunities
        return opportunities
    
    def _analyze_geographic_opportunities(self):
        """Analizar oportunidades geográficas"""
        if 'region' not in self.market_data.columns or 'revenue' not in self.market_data.columns:
            return {}
        
        regional_analysis = self.market_data.groupby('region').agg({
            'revenue': ['sum', 'mean', 'count'],
            'growth_rate': 'mean' if 'growth_rate' in self.market_data.columns else lambda x: 0
        }).round(2)
        
        regional_analysis.columns = ['total_revenue', 'avg_revenue', 'market_size', 'growth_rate']
        
        # Identificar regiones de alto potencial
        high_potential_regions = regional_analysis[
            (regional_analysis['growth_rate'] > regional_analysis['growth_rate'].mean()) &
            (regional_analysis['total_revenue'] < regional_analysis['total_revenue'].quantile(0.8))
        ]
        
        return {
            'regional_analysis': regional_analysis.to_dict('index'),
            'high_potential_regions': high_potential_regions.to_dict('index')
        }
    
    def _analyze_demographic_opportunities(self):
        """Analizar oportunidades demográficas"""
        if 'age_group' not in self.market_data.columns or 'revenue' not in self.market_data.columns:
            return {}
        
        demographic_analysis = self.market_data.groupby('age_group').agg({
            'revenue': ['sum', 'mean', 'count'],
            'satisfaction_score': 'mean' if 'satisfaction_score' in self.market_data.columns else lambda x: 0
        }).round(2)
        
        demographic_analysis.columns = ['total_revenue', 'avg_revenue', 'segment_size', 'satisfaction']
        
        # Identificar segmentos subatendidos
        underserved_segments = demographic_analysis[
            demographic_analysis['total_revenue'] < demographic_analysis['total_revenue'].quantile(0.3)
        ]
        
        return {
            'demographic_analysis': demographic_analysis.to_dict('index'),
            'underserved_segments': underserved_segments.to_dict('index')
        }
    
    def _analyze_product_opportunities(self):
        """Analizar oportunidades de producto"""
        if 'product_category' not in self.market_data.columns or 'revenue' not in self.market_data.columns:
            return {}
        
        product_analysis = self.market_data.groupby('product_category').agg({
            'revenue': ['sum', 'mean', 'count'],
            'profit_margin': 'mean' if 'profit_margin' in self.market_data.columns else lambda x: 0
        }).round(2)
        
        product_analysis.columns = ['total_revenue', 'avg_revenue', 'product_count', 'profit_margin']
        
        # Identificar categorías de alto potencial
        high_potential_categories = product_analysis[
            (product_analysis['profit_margin'] > product_analysis['profit_margin'].mean()) &
            (product_analysis['total_revenue'] < product_analysis['total_revenue'].quantile(0.7))
        ]
        
        return {
            'product_analysis': product_analysis.to_dict('index'),
            'high_potential_categories': high_potential_categories.to_dict('index')
        }
    
    def _analyze_channel_opportunities(self):
        """Analizar oportunidades de canal"""
        if 'channel' not in self.market_data.columns or 'revenue' not in self.market_data.columns:
            return {}
        
        channel_analysis = self.market_data.groupby('channel').agg({
            'revenue': ['sum', 'mean', 'count'],
            'conversion_rate': 'mean' if 'conversion_rate' in self.market_data.columns else lambda x: 0
        }).round(2)
        
        channel_analysis.columns = ['total_revenue', 'avg_revenue', 'channel_usage', 'conversion_rate']
        
        # Identificar canales subutilizados
        underutilized_channels = channel_analysis[
            (channel_analysis['conversion_rate'] > channel_analysis['conversion_rate'].mean()) &
            (channel_analysis['channel_usage'] < channel_analysis['channel_usage'].quantile(0.5))
        ]
        
        return {
            'channel_analysis': channel_analysis.to_dict('index'),
            'underutilized_channels': underutilized_channels.to_dict('index')
        }
    
    def _identify_market_gaps(self):
        """Identificar gaps de mercado"""
        gaps = []
        
        # Gap de precio
        if 'price' in self.market_data.columns and 'demand' in self.market_data.columns:
            price_demand_corr = self.market_data['price'].corr(self.market_data['demand'])
            if price_demand_corr > -0.5:  # Demanda no muy sensible al precio
                gaps.append({
                    'type': 'price_gap',
                    'description': 'Oportunidad para productos premium',
                    'potential': 'high'
                })
        
        # Gap de servicio
        if 'satisfaction_score' in self.market_data.columns:
            avg_satisfaction = self.market_data['satisfaction_score'].mean()
            if avg_satisfaction < 4.0:  # Escala 1-5
                gaps.append({
                    'type': 'service_gap',
                    'description': 'Oportunidad para mejorar servicio al cliente',
                    'potential': 'medium'
                })
        
        # Gap de innovación
        if 'product_category' in self.market_data.columns:
            category_counts = self.market_data['product_category'].value_counts()
            if len(category_counts) < 5:  # Pocas categorías
                gaps.append({
                    'type': 'innovation_gap',
                    'description': 'Oportunidad para nuevas categorías de producto',
                    'potential': 'high'
                })
        
        return gaps
    
    def _identify_market_niches(self):
        """Identificar nichos de mercado"""
        niches = []
        
        # Nicho de alto valor
        if 'revenue' in self.market_data.columns and 'customer_segment' in self.market_data.columns:
            segment_revenue = self.market_data.groupby('customer_segment')['revenue'].mean()
            high_value_segments = segment_revenue[segment_revenue > segment_revenue.quantile(0.8)]
            
            for segment in high_value_segments.index:
                niches.append({
                    'type': 'high_value_niche',
                    'segment': segment,
                    'avg_revenue': high_value_segments[segment],
                    'potential': 'high'
                })
        
        # Nicho de crecimiento rápido
        if 'growth_rate' in self.market_data.columns and 'region' in self.market_data.columns:
            regional_growth = self.market_data.groupby('region')['growth_rate'].mean()
            fast_growing_regions = regional_growth[regional_growth > regional_growth.quantile(0.8)]
            
            for region in fast_growing_regions.index:
                niches.append({
                    'type': 'fast_growing_niche',
                    'region': region,
                    'growth_rate': fast_growing_regions[region],
                    'potential': 'high'
                })
        
        return niches
    
    def assess_market_risks(self):
        """Evaluar riesgos del mercado"""
        risks = []
        
        # Riesgo de volatilidad
        if 'price' in self.market_data.columns:
            price_volatility = self.market_data['price'].std() / self.market_data['price'].mean()
            if price_volatility > 0.2:
                risks.append({
                    'type': 'price_volatility',
                    'severity': 'high' if price_volatility > 0.3 else 'medium',
                    'description': f'Alta volatilidad de precios: {price_volatility:.2%}',
                    'mitigation': 'Implementar estrategias de cobertura de precios'
                })
        
        # Riesgo de concentración
        if 'customer_segment' in self.market_data.columns:
            segment_concentration = self.market_data['customer_segment'].value_counts(normalize=True)
            max_concentration = segment_concentration.max()
            if max_concentration > 0.4:
                risks.append({
                    'type': 'customer_concentration',
                    'severity': 'high' if max_concentration > 0.6 else 'medium',
                    'description': f'Alta concentración en un segmento: {max_concentration:.2%}',
                    'mitigation': 'Diversificar base de clientes'
                })
        
        # Riesgo de competencia
        if 'market_share' in self.market_data.columns:
            avg_market_share = self.market_data['market_share'].mean()
            if avg_market_share < 0.1:
                risks.append({
                    'type': 'competitive_risk',
                    'severity': 'high',
                    'description': f'Baja participación de mercado: {avg_market_share:.2%}',
                    'mitigation': 'Mejorar diferenciación y posicionamiento'
                })
        
        # Riesgo de estacionalidad
        if 'date' in self.market_data.columns and 'revenue' in self.market_data.columns:
            self.market_data['month'] = pd.to_datetime(self.market_data['date']).dt.month
            monthly_revenue = self.market_data.groupby('month')['revenue'].mean()
            revenue_volatility = monthly_revenue.std() / monthly_revenue.mean()
            if revenue_volatility > 0.3:
                risks.append({
                    'type': 'seasonality_risk',
                    'severity': 'medium',
                    'description': f'Alta estacionalidad en ingresos: {revenue_volatility:.2%}',
                    'mitigation': 'Desarrollar productos/servicios contra-estacionales'
                })
        
        self.risk_assessment = risks
        return risks
    
    def create_market_dashboard(self):
        """Crear dashboard de análisis de mercado"""
        if not self.market_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Tendencias del Mercado', 'Predicciones',
                          'Oportunidades', 'Análisis de Riesgos'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de tendencias
        if self.trend_analysis:
            for period, trends in self.trend_analysis.items():
                if 'volume_trend' in trends:
                    trend_data = trends['volume_trend']
                    fig.add_trace(
                        go.Scatter(
                            x=[period],
                            y=[trend_data['slope']],
                            mode='markers',
                            name=f'Volume Trend ({period})'
                        ),
                        row=1, col=1
                    )
        
        # Gráfico de predicciones
        if self.prediction_models:
            for target, model_info in self.prediction_models.items():
                predictions = model_info['models'][model_info['best_model']]['predictions']
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(predictions))),
                        y=predictions,
                        mode='lines',
                        name=f'{target} Predictions'
                    ),
                    row=1, col=2
                )
        
        # Gráfico de oportunidades
        if self.opportunity_analysis:
            opportunity_types = list(self.opportunity_analysis.keys())
            opportunity_counts = [len(opp) if isinstance(opp, (list, dict)) else 1 for opp in self.opportunity_analysis.values()]
            
            fig.add_trace(
                go.Bar(x=opportunity_types, y=opportunity_counts, name='Market Opportunities'),
                row=2, col=1
            )
        
        # Gráfico de riesgos
        if self.risk_assessment:
            risk_types = [risk['type'] for risk in self.risk_assessment]
            risk_severities = [risk['severity'] for risk in self.risk_assessment]
            
            severity_scores = {'low': 1, 'medium': 2, 'high': 3}
            risk_scores = [severity_scores.get(severity, 1) for severity in risk_severities]
            
            fig.add_trace(
                go.Bar(x=risk_types, y=risk_scores, name='Risk Assessment'),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Dashboard de Análisis Predictivo de Mercado",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_market_analysis(self, filename='predictive_market_analysis.json'):
        """Exportar análisis de mercado"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'trend_analysis': self.trend_analysis,
            'prediction_models': {k: {**v, 'model': None} for k, v in self.prediction_models.items()},  # Excluir modelos
            'opportunity_analysis': self.opportunity_analysis,
            'risk_assessment': self.risk_assessment,
            'summary': {
                'total_data_points': len(self.market_data),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de mercado exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de mercado
    market_analyzer = PredictiveMarketAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=365, freq='D'),
        'revenue': np.random.normal(10000, 2000, 365),
        'volume': np.random.normal(1000, 200, 365),
        'price': np.random.normal(50, 10, 365),
        'demand': np.random.normal(500, 100, 365),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 365),
        'age_group': np.random.choice(['18-25', '26-35', '36-45', '46-55'], 365),
        'product_category': np.random.choice(['Electronics', 'Fashion', 'Home', 'Sports'], 365),
        'channel': np.random.choice(['Online', 'Retail', 'Wholesale'], 365),
        'customer_segment': np.random.choice(['Premium', 'Standard', 'Budget'], 365),
        'satisfaction_score': np.random.uniform(1, 5, 365),
        'growth_rate': np.random.normal(0.05, 0.02, 365),
        'market_share': np.random.uniform(0.05, 0.25, 365),
        'profit_margin': np.random.uniform(0.1, 0.3, 365),
        'conversion_rate': np.random.uniform(0.02, 0.08, 365)
    })
    
    # Cargar datos de mercado
    print("📊 Cargando datos de mercado...")
    market_analyzer.load_market_data(sample_data)
    
    # Analizar tendencias
    print("📈 Analizando tendencias del mercado...")
    trends = market_analyzer.analyze_market_trends('12M')
    
    # Construir modelos de predicción
    print("🔮 Construyendo modelos de predicción...")
    prediction_model = market_analyzer.build_prediction_models('revenue')
    
    # Predecir comportamiento del mercado
    print("🎯 Prediciendo comportamiento del mercado...")
    predictions = market_analyzer.predict_market_behavior('revenue', 12)
    
    # Analizar oportunidades
    print("💡 Analizando oportunidades de mercado...")
    opportunities = market_analyzer.analyze_market_opportunities()
    
    # Evaluar riesgos
    print("⚠️ Evaluando riesgos del mercado...")
    risks = market_analyzer.assess_market_risks()
    
    # Crear dashboard
    print("📊 Creando dashboard de mercado...")
    dashboard = market_analyzer.create_market_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de mercado...")
    export_data = market_analyzer.export_market_analysis()
    
    print("✅ Sistema de análisis predictivo de mercado completado!")




