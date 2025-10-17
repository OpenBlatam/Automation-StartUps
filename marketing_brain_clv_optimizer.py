"""
Marketing Brain Customer Lifetime Value Optimizer
Motor avanzado de optimización de Customer Lifetime Value
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class CLVOptimizer:
    def __init__(self):
        self.clv_data = {}
        self.clv_models = {}
        self.clv_segments = {}
        self.clv_forecasting = {}
        self.optimization_strategies = {}
        self.clv_insights = {}
        self.optimization_results = {}
        
    def load_clv_data(self, clv_data):
        """Cargar datos de CLV"""
        if isinstance(clv_data, str):
            if clv_data.endswith('.csv'):
                self.clv_data = pd.read_csv(clv_data)
            elif clv_data.endswith('.json'):
                with open(clv_data, 'r') as f:
                    data = json.load(f)
                self.clv_data = pd.DataFrame(data)
        else:
            self.clv_data = pd.DataFrame(clv_data)
        
        print(f"✅ Datos de CLV cargados: {len(self.clv_data)} registros")
        return True
    
    def calculate_clv_metrics(self):
        """Calcular métricas de CLV"""
        if self.clv_data.empty:
            return None
        
        # Calcular métricas básicas de CLV
        clv_metrics = self.clv_data.groupby('customer_id').agg({
            'revenue': 'sum',
            'orders': 'sum',
            'signup_date': 'min',
            'last_activity_date': 'max',
            'cost': 'sum'
        }).reset_index()
        
        # Calcular duración de vida
        clv_metrics['lifetime_days'] = (clv_metrics['last_activity_date'] - clv_metrics['signup_date']).dt.days
        
        # Calcular métricas adicionales
        clv_metrics['avg_order_value'] = clv_metrics['revenue'] / clv_metrics['orders']
        clv_metrics['purchase_frequency'] = clv_metrics['orders'] / (clv_metrics['lifetime_days'] / 365)
        clv_metrics['profit'] = clv_metrics['revenue'] - clv_metrics['cost']
        clv_metrics['profit_margin'] = clv_metrics['profit'] / clv_metrics['revenue']
        
        # Calcular CLV usando diferentes métodos
        clv_metrics['clv_simple'] = clv_metrics['revenue']
        clv_metrics['clv_profit'] = clv_metrics['profit']
        clv_metrics['clv_discounted'] = self._calculate_discounted_clv(clv_metrics)
        clv_metrics['clv_predictive'] = self._calculate_predictive_clv(clv_metrics)
        
        # Análisis de segmentos de CLV
        clv_metrics['clv_segment'] = pd.cut(
            clv_metrics['clv_predictive'],
            bins=[0, 100, 500, 1000, float('inf')],
            labels=['Low', 'Medium', 'High', 'VIP']
        )
        
        # Análisis por segmento
        segment_analysis = clv_metrics.groupby('clv_segment').agg({
            'revenue': ['count', 'mean', 'sum'],
            'orders': 'mean',
            'lifetime_days': 'mean',
            'purchase_frequency': 'mean',
            'profit_margin': 'mean'
        }).round(2)
        
        segment_analysis.columns = [
            'customer_count', 'avg_clv', 'total_revenue',
            'avg_orders', 'avg_lifetime_days', 'avg_purchase_frequency', 'avg_profit_margin'
        }
        
        clv_results = {
            'clv_metrics': clv_metrics.to_dict('records'),
            'segment_analysis': segment_analysis.to_dict('index'),
            'overall_metrics': {
                'total_customers': len(clv_metrics),
                'avg_clv': clv_metrics['clv_predictive'].mean(),
                'median_clv': clv_metrics['clv_predictive'].median(),
                'total_revenue': clv_metrics['revenue'].sum(),
                'total_profit': clv_metrics['profit'].sum(),
                'avg_lifetime_days': clv_metrics['lifetime_days'].mean()
            }
        }
        
        return clv_results
    
    def _calculate_discounted_clv(self, clv_metrics, discount_rate=0.1):
        """Calcular CLV con descuento"""
        clv_discounted = []
        
        for _, row in clv_metrics.iterrows():
            lifetime_years = row['lifetime_days'] / 365
            annual_revenue = row['revenue'] / lifetime_years if lifetime_years > 0 else 0
            
            # Calcular CLV descontado
            if lifetime_years > 0:
                clv = annual_revenue * (1 - (1 + discount_rate) ** (-lifetime_years)) / discount_rate
            else:
                clv = 0
            
            clv_discounted.append(clv)
        
        return clv_discounted
    
    def _calculate_predictive_clv(self, clv_metrics):
        """Calcular CLV predictivo"""
        clv_predictive = []
        
        for _, row in clv_metrics.iterrows():
            # Fórmula predictiva: (Avg Order Value × Purchase Frequency × Customer Lifespan)
            avg_order_value = row['avg_order_value']
            purchase_frequency = row['purchase_frequency']
            lifetime_years = row['lifetime_days'] / 365
            
            # Ajustar por profit margin
            profit_margin = row['profit_margin']
            
            clv = avg_order_value * purchase_frequency * lifetime_years * profit_margin
            clv_predictive.append(clv)
        
        return clv_predictive
    
    def build_clv_prediction_model(self, target_variable='clv_predictive'):
        """Construir modelo de predicción de CLV"""
        # Calcular métricas de CLV si no existen
        if 'clv_predictive' not in self.clv_data.columns:
            clv_metrics = self.calculate_clv_metrics()
            if clv_metrics:
                clv_df = pd.DataFrame(clv_metrics['clv_metrics'])
                self.clv_data = self.clv_data.merge(clv_df[['customer_id', target_variable]], on='customer_id', how='left')
        
        # Preparar datos
        feature_columns = [col for col in self.clv_data.columns if col != target_variable and col != 'customer_id' and col not in ['signup_date', 'last_activity_date']]
        X = self.clv_data[feature_columns]
        y = self.clv_data[target_variable]
        
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
        
        # Entrenar modelo
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test_scaled)
        
        model_metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.clv_models['clv_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def predict_clv(self, customer_data):
        """Predecir CLV de clientes"""
        if 'clv_predictor' not in self.clv_models:
            raise ValueError("Modelo de predicción de CLV no encontrado")
        
        model_info = self.clv_models['clv_predictor']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        label_encoders = model_info['label_encoders']
        scaler = model_info['scaler']
        
        # Preparar datos
        X = customer_data[feature_columns]
        
        # Codificar variables categóricas
        for column in X.select_dtypes(include=['object']).columns:
            if column in label_encoders:
                le = label_encoders[column]
                X[column] = le.transform(X[column].astype(str))
        
        # Escalar datos
        X_scaled = scaler.transform(X)
        
        # Predecir CLV
        clv_predictions = model.predict(X_scaled)
        
        return clv_predictions
    
    def create_clv_segments(self):
        """Crear segmentos de CLV"""
        if self.clv_data.empty:
            return None
        
        # Calcular métricas de CLV
        clv_metrics = self.calculate_clv_metrics()
        if not clv_metrics:
            return None
        
        clv_df = pd.DataFrame(clv_metrics['clv_metrics'])
        
        # Segmentación usando clustering
        features = ['clv_predictive', 'purchase_frequency', 'avg_order_value', 'lifetime_days', 'profit_margin']
        X = clv_df[features].fillna(0)
        
        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Clustering K-means
        kmeans = KMeans(n_clusters=5, random_state=42)
        clv_df['clv_cluster'] = kmeans.fit_predict(X_scaled)
        
        # Nombrar clusters
        cluster_names = {
            0: 'Low Value',
            1: 'Medium Value',
            2: 'High Value',
            3: 'Premium',
            4: 'VIP'
        }
        
        clv_df['clv_segment_name'] = clv_df['clv_cluster'].map(cluster_names)
        
        # Análisis de segmentos
        segment_analysis = clv_df.groupby('clv_segment_name').agg({
            'clv_predictive': ['count', 'mean', 'sum'],
            'purchase_frequency': 'mean',
            'avg_order_value': 'mean',
            'lifetime_days': 'mean',
            'profit_margin': 'mean'
        }).round(2)
        
        segment_analysis.columns = [
            'customer_count', 'avg_clv', 'total_clv',
            'avg_purchase_frequency', 'avg_order_value', 'avg_lifetime_days', 'avg_profit_margin'
        }
        
        clv_segments = {
            'customer_segments': clv_df.to_dict('records'),
            'segment_analysis': segment_analysis.to_dict('index'),
            'segment_characteristics': self._analyze_clv_segment_characteristics(clv_df)
        }
        
        self.clv_segments = clv_segments
        return clv_segments
    
    def _analyze_clv_segment_characteristics(self, clv_df):
        """Analizar características de segmentos de CLV"""
        characteristics = {}
        
        for segment in clv_df['clv_segment_name'].unique():
            segment_data = clv_df[clv_df['clv_segment_name'] == segment]
            
            characteristics[segment] = {
                'avg_clv': segment_data['clv_predictive'].mean(),
                'avg_purchase_frequency': segment_data['purchase_frequency'].mean(),
                'avg_order_value': segment_data['avg_order_value'].mean(),
                'avg_lifetime_days': segment_data['lifetime_days'].mean(),
                'avg_profit_margin': segment_data['profit_margin'].mean(),
                'customer_count': len(segment_data),
                'percentage': len(segment_data) / len(clv_df) * 100,
                'total_clv': segment_data['clv_predictive'].sum()
            }
        
        return characteristics
    
    def forecast_clv_trends(self, forecast_periods=12):
        """Predecir tendencias de CLV"""
        if self.clv_data.empty:
            return None
        
        # Calcular métricas de CLV por período
        self.clv_data['signup_month'] = pd.to_datetime(self.clv_data['signup_date']).dt.to_period('M')
        
        monthly_clv = self.clv_data.groupby('signup_month').agg({
            'revenue': 'sum',
            'customer_id': 'nunique',
            'orders': 'sum'
        }).reset_index()
        
        monthly_clv['avg_clv'] = monthly_clv['revenue'] / monthly_clv['customer_id']
        monthly_clv['avg_orders_per_customer'] = monthly_clv['orders'] / monthly_clv['customer_id']
        
        # Análisis de tendencias
        trend_analysis = self._analyze_clv_trends(monthly_clv)
        
        # Forecasting usando regresión lineal simple
        forecast_results = self._forecast_clv_values(monthly_clv, forecast_periods)
        
        clv_forecasting = {
            'monthly_clv': monthly_clv.to_dict('records'),
            'trend_analysis': trend_analysis,
            'forecast_results': forecast_results
        }
        
        self.clv_forecasting = clv_forecasting
        return clv_forecasting
    
    def _analyze_clv_trends(self, monthly_clv):
        """Analizar tendencias de CLV"""
        trends = {}
        
        # Tendencias de CLV promedio
        clv_values = monthly_clv['avg_clv'].values
        if len(clv_values) > 1:
            clv_trend = self._calculate_trend(clv_values)
            trends['clv_trend'] = clv_trend
        
        # Tendencias de número de clientes
        customer_values = monthly_clv['customer_id'].values
        if len(customer_values) > 1:
            customer_trend = self._calculate_trend(customer_values)
            trends['customer_trend'] = customer_trend
        
        # Tendencias de revenue total
        revenue_values = monthly_clv['revenue'].values
        if len(revenue_values) > 1:
            revenue_trend = self._calculate_trend(revenue_values)
            trends['revenue_trend'] = revenue_trend
        
        return trends
    
    def _calculate_trend(self, values):
        """Calcular tendencia de una serie de valores"""
        if len(values) < 2:
            return {'direction': 'stable', 'slope': 0, 'strength': 0}
        
        x = np.arange(len(values))
        y = values
        
        # Regresión lineal
        slope = np.polyfit(x, y, 1)[0]
        correlation = np.corrcoef(x, y)[0, 1]
        
        if slope > 0:
            direction = 'increasing'
        elif slope < 0:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': slope,
            'strength': abs(correlation)
        }
    
    def _forecast_clv_values(self, monthly_clv, forecast_periods):
        """Predecir valores futuros de CLV"""
        # Usar regresión lineal simple para forecasting
        x = np.arange(len(monthly_clv))
        y = monthly_clv['avg_clv'].values
        
        # Ajustar línea de tendencia
        coeffs = np.polyfit(x, y, 1)
        
        # Predecir valores futuros
        future_x = np.arange(len(monthly_clv), len(monthly_clv) + forecast_periods)
        future_y = coeffs[0] * future_x + coeffs[1]
        
        # Crear fechas futuras
        last_date = monthly_clv['signup_month'].iloc[-1]
        future_dates = []
        for i in range(forecast_periods):
            future_date = last_date + i + 1
            future_dates.append(str(future_date))
        
        forecast_results = {
            'forecast_dates': future_dates,
            'forecast_values': future_y.tolist(),
            'trend_coefficients': coeffs.tolist(),
            'forecast_periods': forecast_periods
        }
        
        return forecast_results
    
    def optimize_clv_strategies(self):
        """Optimizar estrategias de CLV"""
        strategies = []
        
        # Estrategias basadas en segmentos
        if self.clv_segments:
            segment_analysis = self.clv_segments.get('segment_analysis', {})
            
            for segment, data in segment_analysis.items():
                customer_count = data.get('customer_count', 0)
                avg_clv = data.get('avg_clv', 0)
                
                if segment == 'Low Value' and customer_count > 0:
                    strategies.append({
                        'segment': segment,
                        'strategy': 'Upselling Campaign',
                        'description': 'Implementar campañas de upselling para aumentar CLV',
                        'priority': 'high',
                        'expected_impact': 'medium'
                    })
                
                elif segment == 'Medium Value':
                    strategies.append({
                        'segment': segment,
                        'strategy': 'Cross-selling Program',
                        'description': 'Desarrollar programa de cross-selling',
                        'priority': 'medium',
                        'expected_impact': 'high'
                    })
                
                elif segment == 'High Value':
                    strategies.append({
                        'segment': segment,
                        'strategy': 'Premium Service',
                        'description': 'Ofrecer servicios premium para retener clientes',
                        'priority': 'medium',
                        'expected_impact': 'high'
                    })
                
                elif segment == 'VIP':
                    strategies.append({
                        'segment': segment,
                        'strategy': 'Exclusive Benefits',
                        'description': 'Proporcionar beneficios exclusivos y personalizados',
                        'priority': 'low',
                        'expected_impact': 'high'
                    })
        
        # Estrategias basadas en tendencias
        if self.clv_forecasting:
            trend_analysis = self.clv_forecasting.get('trend_analysis', {})
            clv_trend = trend_analysis.get('clv_trend', {})
            
            if clv_trend.get('direction') == 'decreasing':
                strategies.append({
                    'segment': 'All',
                    'strategy': 'CLV Recovery Program',
                    'description': 'Implementar programa de recuperación de CLV',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en métricas
        if self.clv_models:
            clv_model = self.clv_models.get('clv_predictor', {})
            if clv_model:
                metrics = clv_model.get('metrics', {})
                r2 = metrics.get('r2', 0)
                
                if r2 > 0.8:
                    strategies.append({
                        'segment': 'All',
                        'strategy': 'Predictive CLV Targeting',
                        'description': 'Usar modelo predictivo para targeting de CLV',
                        'priority': 'medium',
                        'expected_impact': 'high'
                    })
        
        self.optimization_strategies = strategies
        return strategies
    
    def generate_clv_insights(self):
        """Generar insights de CLV"""
        insights = []
        
        # Insights de segmentos
        if self.clv_segments:
            segment_analysis = self.clv_segments.get('segment_analysis', {})
            
            # Analizar segmento VIP
            vip_segment = segment_analysis.get('VIP', {})
            if vip_segment:
                vip_count = vip_segment.get('customer_count', 0)
                vip_clv = vip_segment.get('avg_clv', 0)
                
                if vip_count > 0:
                    insights.append({
                        'category': 'CLV Segmentation',
                        'insight': f'{vip_count} clientes VIP con CLV promedio de ${vip_clv:.2f}',
                        'recommendation': 'Implementar programa VIP para maximizar retención',
                        'priority': 'high'
                    })
            
            # Analizar segmento de bajo valor
            low_value = segment_analysis.get('Low Value', {})
            if low_value:
                low_count = low_value.get('customer_count', 0)
                total_customers = sum(segment.get('customer_count', 0) for segment in segment_analysis.values())
                
                if low_count > 0 and total_customers > 0:
                    low_percentage = low_count / total_customers * 100
                    if low_percentage > 40:
                        insights.append({
                            'category': 'CLV Optimization',
                            'insight': f'{low_percentage:.1f}% de clientes en segmento de bajo valor',
                            'recommendation': 'Implementar estrategias de upselling y cross-selling',
                            'priority': 'high'
                        })
        
        # Insights de tendencias
        if self.clv_forecasting:
            trend_analysis = self.clv_forecasting.get('trend_analysis', {})
            clv_trend = trend_analysis.get('clv_trend', {})
            
            if clv_trend:
                direction = clv_trend.get('direction', 'stable')
                strength = clv_trend.get('strength', 0)
                
                if direction == 'decreasing' and strength > 0.5:
                    insights.append({
                        'category': 'CLV Trends',
                        'insight': f'Tendencia decreciente de CLV con fuerza {strength:.2f}',
                        'recommendation': 'Implementar programa de recuperación de CLV',
                        'priority': 'high'
                    })
                elif direction == 'increasing' and strength > 0.5:
                    insights.append({
                        'category': 'CLV Trends',
                        'insight': f'Tendencia creciente de CLV con fuerza {strength:.2f}',
                        'recommendation': 'Mantener estrategias actuales y escalar',
                        'priority': 'medium'
                    })
        
        # Insights de modelo predictivo
        if self.clv_models:
            clv_model = self.clv_models.get('clv_predictor', {})
            if clv_model:
                metrics = clv_model.get('metrics', {})
                r2 = metrics.get('r2', 0)
                
                if r2 > 0.8:
                    insights.append({
                        'category': 'CLV Prediction',
                        'insight': f'Modelo predictivo de CLV con alta precisión: R² = {r2:.3f}',
                        'recommendation': 'Usar modelo para targeting y personalización',
                        'priority': 'medium'
                    })
        
        self.clv_insights = insights
        return insights
    
    def create_clv_dashboard(self):
        """Crear dashboard de optimización de CLV"""
        if not self.clv_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CLV Segments', 'CLV Trends',
                          'CLV Forecasting', 'CLV Distribution'),
            specs=[[{"type": "pie"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "histogram"}]]
        )
        
        # Gráfico de segmentos de CLV
        if self.clv_segments:
            segment_analysis = self.clv_segments.get('segment_analysis', {})
            if segment_analysis:
                segments = list(segment_analysis.keys())
                customer_counts = [segment_analysis[segment]['customer_count'] for segment in segments]
                
                fig.add_trace(
                    go.Pie(labels=segments, values=customer_counts, name='CLV Segments'),
                    row=1, col=1
                )
        
        # Gráfico de tendencias de CLV
        if self.clv_forecasting:
            monthly_clv = self.clv_forecasting.get('monthly_clv', [])
            if monthly_clv:
                dates = [data['signup_month'] for data in monthly_clv]
                clv_values = [data['avg_clv'] for data in monthly_clv]
                
                fig.add_trace(
                    go.Scatter(x=dates, y=clv_values, mode='lines+markers', name='CLV Trends'),
                    row=1, col=2
                )
        
        # Gráfico de forecasting de CLV
        if self.clv_forecasting:
            forecast_results = self.clv_forecasting.get('forecast_results', {})
            if forecast_results:
                forecast_dates = forecast_results.get('forecast_dates', [])
                forecast_values = forecast_results.get('forecast_values', [])
                
                fig.add_trace(
                    go.Scatter(x=forecast_dates, y=forecast_values, mode='lines+markers', name='CLV Forecast'),
                    row=2, col=1
                )
        
        # Gráfico de distribución de CLV
        if self.clv_segments:
            customer_segments = self.clv_segments.get('customer_segments', [])
            if customer_segments:
                clv_values = [segment['clv_predictive'] for segment in customer_segments]
                
                fig.add_trace(
                    go.Histogram(x=clv_values, name='CLV Distribution'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Optimización de Customer Lifetime Value",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_clv_analysis(self, filename='clv_optimization_analysis.json'):
        """Exportar análisis de CLV"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'clv_segments': self.clv_segments,
            'clv_forecasting': self.clv_forecasting,
            'clv_models': {k: {'metrics': v['metrics']} for k, v in self.clv_models.items()},
            'optimization_strategies': self.optimization_strategies,
            'clv_insights': self.clv_insights,
            'summary': {
                'total_customers': len(self.clv_data['customer_id'].unique()) if 'customer_id' in self.clv_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de CLV exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de CLV
    clv_optimizer = CLVOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 1000, 2000),
        'revenue': np.random.normal(500, 200, 2000),
        'orders': np.random.poisson(5, 2000),
        'cost': np.random.normal(200, 100, 2000),
        'signup_date': pd.date_range('2022-01-01', periods=2000, freq='D'),
        'last_activity_date': pd.date_range('2023-01-01', periods=2000, freq='D'),
        'customer_segment': np.random.choice(['Premium', 'Standard', 'Basic'], 2000),
        'satisfaction_score': np.random.uniform(1, 5, 2000),
        'engagement_score': np.random.uniform(0, 10, 2000)
    })
    
    # Cargar datos de CLV
    print("📊 Cargando datos de CLV...")
    clv_optimizer.load_clv_data(sample_data)
    
    # Calcular métricas de CLV
    print("💰 Calculando métricas de CLV...")
    clv_metrics = clv_optimizer.calculate_clv_metrics()
    
    # Construir modelo de predicción de CLV
    print("🔮 Construyendo modelo de predicción de CLV...")
    clv_model = clv_optimizer.build_clv_prediction_model()
    
    # Crear segmentos de CLV
    print("👥 Creando segmentos de CLV...")
    clv_segments = clv_optimizer.create_clv_segments()
    
    # Predecir tendencias de CLV
    print("📈 Prediciendo tendencias de CLV...")
    clv_forecasting = clv_optimizer.forecast_clv_trends()
    
    # Optimizar estrategias de CLV
    print("🎯 Optimizando estrategias de CLV...")
    clv_strategies = clv_optimizer.optimize_clv_strategies()
    
    # Generar insights de CLV
    print("💡 Generando insights de CLV...")
    clv_insights = clv_optimizer.generate_clv_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de CLV...")
    dashboard = clv_optimizer.create_clv_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de CLV...")
    export_data = clv_optimizer.export_clv_analysis()
    
    print("✅ Sistema de optimización de CLV completado!")






