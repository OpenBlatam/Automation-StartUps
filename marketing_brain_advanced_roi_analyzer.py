"""
Marketing Brain Advanced ROI Analyzer
Sistema avanzado de análisis de ROI y métricas de marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import scipy.stats as stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class AdvancedROIAnalyzer:
    def __init__(self):
        self.campaign_data = {}
        self.roi_metrics = {}
        self.attribution_models = {}
        self.lifetime_value_analysis = {}
        self.customer_acquisition_cost = {}
        self.optimization_recommendations = {}
        self.forecasting_models = {}
        
    def load_campaign_data(self, campaign_data):
        """Cargar datos de campañas"""
        if isinstance(campaign_data, str):
            if campaign_data.endswith('.csv'):
                self.campaign_data = pd.read_csv(campaign_data)
            elif campaign_data.endswith('.json'):
                with open(campaign_data, 'r') as f:
                    data = json.load(f)
                self.campaign_data = pd.DataFrame(data)
        else:
            self.campaign_data = pd.DataFrame(campaign_data)
        
        print(f"✅ Datos de campañas cargados: {len(self.campaign_data)} registros")
        return True
    
    def calculate_roi_metrics(self, campaign_id=None):
        """Calcular métricas de ROI"""
        if campaign_id:
            data = self.campaign_data[self.campaign_data['campaign_id'] == campaign_id]
        else:
            data = self.campaign_data
        
        # Métricas básicas de ROI
        total_revenue = data['revenue'].sum()
        total_cost = data['cost'].sum()
        total_conversions = data['conversions'].sum()
        total_clicks = data['clicks'].sum()
        total_impressions = data['impressions'].sum()
        
        # Cálculos de ROI
        roi = (total_revenue - total_cost) / total_cost if total_cost > 0 else 0
        roas = total_revenue / total_cost if total_cost > 0 else 0
        cpa = total_cost / total_conversions if total_conversions > 0 else 0
        cpc = total_cost / total_clicks if total_clicks > 0 else 0
        cpm = (total_cost / total_impressions) * 1000 if total_impressions > 0 else 0
        
        # Métricas de conversión
        conversion_rate = total_conversions / total_clicks if total_clicks > 0 else 0
        click_through_rate = total_clicks / total_impressions if total_impressions > 0 else 0
        
        # Métricas de engagement
        engagement_rate = data['engagements'].sum() / total_impressions if total_impressions > 0 else 0
        
        roi_metrics = {
            'campaign_id': campaign_id,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'roi': roi,
            'roas': roas,
            'cpa': cpa,
            'cpc': cpc,
            'cpm': cpm,
            'conversion_rate': conversion_rate,
            'click_through_rate': click_through_rate,
            'engagement_rate': engagement_rate,
            'total_conversions': total_conversions,
            'total_clicks': total_clicks,
            'total_impressions': total_impressions
        }
        
        if campaign_id:
            self.roi_metrics[campaign_id] = roi_metrics
        else:
            self.roi_metrics['overall'] = roi_metrics
        
        return roi_metrics
    
    def calculate_customer_lifetime_value(self, customer_data):
        """Calcular valor de vida del cliente (CLV)"""
        clv_analysis = {}
        
        # Análisis por cohorte
        customer_data['cohort'] = pd.to_datetime(customer_data['first_purchase']).dt.to_period('M')
        cohort_analysis = customer_data.groupby('cohort').agg({
            'customer_id': 'count',
            'total_revenue': 'sum',
            'total_orders': 'sum'
        }).reset_index()
        
        cohort_analysis['avg_revenue_per_customer'] = cohort_analysis['total_revenue'] / cohort_analysis['customer_id']
        cohort_analysis['avg_orders_per_customer'] = cohort_analysis['total_orders'] / cohort_analysis['customer_id']
        
        # Cálculo de CLV histórico
        historical_clv = customer_data.groupby('customer_id').agg({
            'total_revenue': 'sum',
            'total_orders': 'sum',
            'days_since_first_purchase': 'max'
        })
        
        historical_clv['avg_order_value'] = historical_clv['total_revenue'] / historical_clv['total_orders']
        historical_clv['purchase_frequency'] = historical_clv['total_orders'] / (historical_clv['days_since_first_purchase'] / 365)
        
        # CLV promedio
        avg_clv = historical_clv['total_revenue'].mean()
        median_clv = historical_clv['total_revenue'].median()
        
        # Segmentación por CLV
        clv_segments = pd.cut(
            historical_clv['total_revenue'],
            bins=[0, 100, 500, 1000, float('inf')],
            labels=['Low', 'Medium', 'High', 'VIP']
        )
        
        segment_analysis = historical_clv.groupby(clv_segments).agg({
            'total_revenue': ['count', 'mean', 'sum'],
            'total_orders': 'mean',
            'purchase_frequency': 'mean'
        })
        
        clv_analysis = {
            'cohort_analysis': cohort_analysis.to_dict('records'),
            'historical_clv': historical_clv.to_dict('index'),
            'avg_clv': avg_clv,
            'median_clv': median_clv,
            'segment_analysis': segment_analysis.to_dict(),
            'total_customers': len(historical_clv),
            'total_revenue': historical_clv['total_revenue'].sum()
        }
        
        self.lifetime_value_analysis = clv_analysis
        return clv_analysis
    
    def calculate_customer_acquisition_cost(self, acquisition_data):
        """Calcular costo de adquisición de clientes (CAC)"""
        cac_analysis = {}
        
        # CAC por canal
        channel_cac = acquisition_data.groupby('channel').agg({
            'cost': 'sum',
            'new_customers': 'sum'
        }).reset_index()
        
        channel_cac['cac'] = channel_cac['cost'] / channel_cac['new_customers']
        
        # CAC por campaña
        campaign_cac = acquisition_data.groupby('campaign_id').agg({
            'cost': 'sum',
            'new_customers': 'sum'
        }).reset_index()
        
        campaign_cac['cac'] = campaign_cac['cost'] / campaign_cac['new_customers']
        
        # CAC promedio
        total_cost = acquisition_data['cost'].sum()
        total_new_customers = acquisition_data['new_customers'].sum()
        avg_cac = total_cost / total_new_customers if total_new_customers > 0 else 0
        
        # Análisis de tendencia
        acquisition_data['date'] = pd.to_datetime(acquisition_data['date'])
        daily_cac = acquisition_data.groupby('date').agg({
            'cost': 'sum',
            'new_customers': 'sum'
        }).reset_index()
        
        daily_cac['cac'] = daily_cac['cost'] / daily_cac['new_customers']
        
        # CAC por segmento de cliente
        if 'customer_segment' in acquisition_data.columns:
            segment_cac = acquisition_data.groupby('customer_segment').agg({
                'cost': 'sum',
                'new_customers': 'sum'
            }).reset_index()
            
            segment_cac['cac'] = segment_cac['cost'] / segment_cac['new_customers']
        else:
            segment_cac = pd.DataFrame()
        
        cac_analysis = {
            'channel_cac': channel_cac.to_dict('records'),
            'campaign_cac': campaign_cac.to_dict('records'),
            'avg_cac': avg_cac,
            'daily_cac': daily_cac.to_dict('records'),
            'segment_cac': segment_cac.to_dict('records') if not segment_cac.empty else [],
            'total_cost': total_cost,
            'total_new_customers': total_new_customers
        }
        
        self.customer_acquisition_cost = cac_analysis
        return cac_analysis
    
    def build_attribution_model(self, attribution_data, model_type='last_click'):
        """Construir modelo de atribución"""
        attribution_models = {}
        
        if model_type == 'last_click':
            # Atribución de último clic
            last_click_attribution = attribution_data.groupby('customer_id').last().reset_index()
            last_click_attribution['attribution_weight'] = 1.0
            
            attribution_models['last_click'] = last_click_attribution
        
        elif model_type == 'first_click':
            # Atribución de primer clic
            first_click_attribution = attribution_data.groupby('customer_id').first().reset_index()
            first_click_attribution['attribution_weight'] = 1.0
            
            attribution_models['first_click'] = first_click_attribution
        
        elif model_type == 'linear':
            # Atribución lineal
            touchpoint_counts = attribution_data.groupby('customer_id').size()
            attribution_data['attribution_weight'] = attribution_data['customer_id'].map(
                lambda x: 1.0 / touchpoint_counts[x]
            )
            
            attribution_models['linear'] = attribution_data
        
        elif model_type == 'time_decay':
            # Atribución con decaimiento temporal
            attribution_data['days_since_touchpoint'] = (
                datetime.now() - pd.to_datetime(attribution_data['touchpoint_date'])
            ).dt.days
            
            # Peso basado en decaimiento exponencial
            attribution_data['attribution_weight'] = np.exp(-attribution_data['days_since_touchpoint'] / 30)
            
            # Normalizar pesos por cliente
            customer_weights = attribution_data.groupby('customer_id')['attribution_weight'].sum()
            attribution_data['attribution_weight'] = attribution_data.apply(
                lambda row: row['attribution_weight'] / customer_weights[row['customer_id']], axis=1
            )
            
            attribution_models['time_decay'] = attribution_data
        
        # Calcular métricas de atribución
        for model_name, model_data in attribution_models.items():
            channel_attribution = model_data.groupby('channel').agg({
                'attribution_weight': 'sum',
                'conversion_value': 'sum'
            }).reset_index()
            
            channel_attribution['attributed_conversions'] = (
                channel_attribution['attribution_weight'] * model_data['converted'].sum()
            )
            
            attribution_models[model_name] = {
                'data': model_data,
                'channel_attribution': channel_attribution.to_dict('records')
            }
        
        self.attribution_models = attribution_models
        return attribution_models
    
    def optimize_budget_allocation(self, budget_data):
        """Optimizar asignación de presupuesto"""
        # Preparar datos para optimización
        channels = budget_data['channel'].unique()
        n_channels = len(channels)
        
        # Función objetivo: maximizar ROI
        def objective(x):
            # x es el vector de asignación de presupuesto
            total_roi = 0
            for i, channel in enumerate(channels):
                channel_data = budget_data[budget_data['channel'] == channel]
                if len(channel_data) > 0:
                    # ROI estimado basado en datos históricos
                    avg_roi = channel_data['roi'].mean()
                    total_roi += x[i] * avg_roi
            return -total_roi  # Minimizar el negativo para maximizar
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}  # Suma debe ser 1
        ]
        
        # Límites (cada canal debe recibir al menos 5% y máximo 50%)
        bounds = [(0.05, 0.5) for _ in range(n_channels)]
        
        # Punto inicial (distribución uniforme)
        x0 = np.ones(n_channels) / n_channels
        
        # Optimización
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        # Resultados de optimización
        optimal_allocation = {}
        for i, channel in enumerate(channels):
            optimal_allocation[channel] = {
                'allocation_percentage': result.x[i] * 100,
                'estimated_roi': budget_data[budget_data['channel'] == channel]['roi'].mean(),
                'current_allocation': budget_data[budget_data['channel'] == channel]['budget_percentage'].mean()
            }
        
        # Recomendaciones de optimización
        recommendations = []
        for channel, allocation in optimal_allocation.items():
            current = allocation['current_allocation']
            optimal = allocation['allocation_percentage']
            
            if optimal > current * 1.1:  # Aumentar más del 10%
                recommendations.append({
                    'channel': channel,
                    'action': 'increase',
                    'current_allocation': current,
                    'recommended_allocation': optimal,
                    'change_percentage': optimal - current,
                    'reason': 'High ROI potential'
                })
            elif optimal < current * 0.9:  # Disminuir más del 10%
                recommendations.append({
                    'channel': channel,
                    'action': 'decrease',
                    'current_allocation': current,
                    'recommended_allocation': optimal,
                    'change_percentage': optimal - current,
                    'reason': 'Low ROI efficiency'
                })
        
        optimization_results = {
            'optimal_allocation': optimal_allocation,
            'recommendations': recommendations,
            'expected_roi_improvement': -result.fun - budget_data['roi'].mean(),
            'optimization_status': result.success
        }
        
        self.optimization_recommendations = optimization_results
        return optimization_results
    
    def forecast_roi(self, historical_data, forecast_periods=12):
        """Predecir ROI futuro"""
        # Preparar datos para forecasting
        historical_data['date'] = pd.to_datetime(historical_data['date'])
        monthly_data = historical_data.groupby(
            historical_data['date'].dt.to_period('M')
        ).agg({
            'roi': 'mean',
            'revenue': 'sum',
            'cost': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        monthly_data['date'] = monthly_data['date'].astype(str)
        
        # Modelo de forecasting para ROI
        X = np.arange(len(monthly_data)).reshape(-1, 1)
        y = monthly_data['roi'].values
        
        # Entrenar modelo
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Predecir ROI futuro
        future_periods = np.arange(len(monthly_data), len(monthly_data) + forecast_periods).reshape(-1, 1)
        predicted_roi = model.predict(future_periods)
        
        # Predecir revenue y cost
        revenue_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        cost_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        revenue_model.fit(X, monthly_data['revenue'].values)
        cost_model.fit(X, monthly_data['cost'].values)
        
        predicted_revenue = revenue_model.predict(future_periods)
        predicted_cost = cost_model.predict(future_periods)
        
        # Crear forecast
        forecast_dates = pd.date_range(
            start=monthly_data['date'].iloc[-1],
            periods=forecast_periods + 1,
            freq='M'
        )[1:]
        
        forecast_data = pd.DataFrame({
            'date': forecast_dates,
            'predicted_roi': predicted_roi,
            'predicted_revenue': predicted_revenue,
            'predicted_cost': predicted_cost,
            'predicted_conversions': predicted_revenue / (monthly_data['revenue'] / monthly_data['conversions']).mean()
        })
        
        # Calcular intervalos de confianza (simplificado)
        roi_std = np.std(monthly_data['roi'])
        forecast_data['roi_confidence_lower'] = forecast_data['predicted_roi'] - 1.96 * roi_std
        forecast_data['roi_confidence_upper'] = forecast_data['predicted_roi'] + 1.96 * roi_std
        
        # Métricas del modelo
        model_metrics = {
            'r2_score': r2_score(y, model.predict(X)),
            'mse': mean_squared_error(y, model.predict(X)),
            'historical_avg_roi': monthly_data['roi'].mean(),
            'forecast_avg_roi': predicted_roi.mean()
        }
        
        forecasting_results = {
            'forecast_data': forecast_data.to_dict('records'),
            'model_metrics': model_metrics,
            'historical_data': monthly_data.to_dict('records')
        }
        
        self.forecasting_models = forecasting_results
        return forecasting_results
    
    def create_roi_dashboard(self):
        """Crear dashboard de ROI"""
        if not self.roi_metrics and not self.lifetime_value_analysis:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Métricas de ROI', 'Análisis de CLV',
                          'Costo de Adquisición', 'Forecasting de ROI'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # Gráfico de métricas de ROI
        if self.roi_metrics:
            metrics = self.roi_metrics.get('overall', {})
            metric_names = ['ROI', 'ROAS', 'CPA', 'CPC']
            metric_values = [
                metrics.get('roi', 0),
                metrics.get('roas', 0),
                metrics.get('cpa', 0),
                metrics.get('cpc', 0)
            ]
            
            fig.add_trace(
                go.Bar(x=metric_names, y=metric_values, name='ROI Metrics'),
                row=1, col=1
            )
        
        # Gráfico de CLV
        if self.lifetime_value_analysis:
            clv_data = self.lifetime_value_analysis.get('cohort_analysis', [])
            if clv_data:
                cohorts = [item['cohort'] for item in clv_data]
                avg_revenue = [item['avg_revenue_per_customer'] for item in clv_data]
                
                fig.add_trace(
                    go.Bar(x=cohorts, y=avg_revenue, name='Average CLV by Cohort'),
                    row=1, col=2
                )
        
        # Gráfico de CAC
        if self.customer_acquisition_cost:
            cac_data = self.customer_acquisition_cost.get('channel_cac', [])
            if cac_data:
                channels = [item['channel'] for item in cac_data]
                cac_values = [item['cac'] for item in cac_data]
                
                fig.add_trace(
                    go.Scatter(x=channels, y=cac_values, mode='markers+lines', name='CAC by Channel'),
                    row=2, col=1
                )
        
        # Gráfico de forecasting
        if self.forecasting_models:
            forecast_data = self.forecasting_models.get('forecast_data', [])
            if forecast_data:
                dates = [item['date'] for item in forecast_data]
                predicted_roi = [item['predicted_roi'] for item in forecast_data]
                
                fig.add_trace(
                    go.Scatter(x=dates, y=predicted_roi, mode='lines', name='ROI Forecast'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Análisis de ROI Avanzado",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_roi_analysis(self, filename='advanced_roi_analysis.json'):
        """Exportar análisis de ROI"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'roi_metrics': self.roi_metrics,
            'lifetime_value_analysis': self.lifetime_value_analysis,
            'customer_acquisition_cost': self.customer_acquisition_cost,
            'attribution_models': self.attribution_models,
            'optimization_recommendations': self.optimization_recommendations,
            'forecasting_models': self.forecasting_models,
            'summary': {
                'total_campaigns': len(self.roi_metrics),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de ROI exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de ROI
    roi_analyzer = AdvancedROIAnalyzer()
    
    # Datos de ejemplo para campañas
    campaign_data = pd.DataFrame({
        'campaign_id': np.random.randint(1, 10, 1000),
        'channel': np.random.choice(['email', 'social', 'search', 'display'], 1000),
        'revenue': np.random.normal(1000, 300, 1000),
        'cost': np.random.normal(200, 50, 1000),
        'conversions': np.random.poisson(5, 1000),
        'clicks': np.random.poisson(100, 1000),
        'impressions': np.random.poisson(10000, 1000),
        'engagements': np.random.poisson(50, 1000)
    })
    
    # Cargar datos de campañas
    print("📊 Cargando datos de campañas...")
    roi_analyzer.load_campaign_data(campaign_data)
    
    # Calcular métricas de ROI
    print("💰 Calculando métricas de ROI...")
    roi_metrics = roi_analyzer.calculate_roi_metrics()
    
    # Datos de ejemplo para CLV
    customer_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 500, 1000),
        'first_purchase': pd.date_range('2023-01-01', periods=1000, freq='D'),
        'total_revenue': np.random.normal(500, 200, 1000),
        'total_orders': np.random.poisson(3, 1000),
        'days_since_first_purchase': np.random.randint(1, 365, 1000)
    })
    
    # Calcular CLV
    print("👤 Calculando valor de vida del cliente...")
    clv_analysis = roi_analyzer.calculate_customer_lifetime_value(customer_data)
    
    # Datos de ejemplo para CAC
    acquisition_data = pd.DataFrame({
        'channel': np.random.choice(['email', 'social', 'search'], 100),
        'campaign_id': np.random.randint(1, 20, 100),
        'cost': np.random.normal(1000, 200, 100),
        'new_customers': np.random.poisson(10, 100),
        'date': pd.date_range('2023-01-01', periods=100, freq='D')
    })
    
    # Calcular CAC
    print("💸 Calculando costo de adquisición...")
    cac_analysis = roi_analyzer.calculate_customer_acquisition_cost(acquisition_data)
    
    # Datos de ejemplo para atribución
    attribution_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 200, 500),
        'channel': np.random.choice(['email', 'social', 'search'], 500),
        'touchpoint_date': pd.date_range('2023-01-01', periods=500, freq='D'),
        'converted': np.random.choice([0, 1], 500, p=[0.7, 0.3]),
        'conversion_value': np.random.normal(100, 30, 500)
    })
    
    # Construir modelo de atribución
    print("🎯 Construyendo modelo de atribución...")
    attribution_models = roi_analyzer.build_attribution_model(attribution_data, 'time_decay')
    
    # Datos de ejemplo para optimización de presupuesto
    budget_data = pd.DataFrame({
        'channel': ['email', 'social', 'search', 'display'],
        'roi': [3.2, 2.8, 4.1, 2.5],
        'budget_percentage': [25, 30, 35, 10]
    })
    
    # Optimizar asignación de presupuesto
    print("🎯 Optimizando asignación de presupuesto...")
    optimization_results = roi_analyzer.optimize_budget_allocation(budget_data)
    
    # Datos de ejemplo para forecasting
    historical_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=12, freq='M'),
        'roi': np.random.normal(2.5, 0.5, 12),
        'revenue': np.random.normal(100000, 20000, 12),
        'cost': np.random.normal(40000, 8000, 12),
        'conversions': np.random.poisson(500, 12)
    })
    
    # Predecir ROI futuro
    print("🔮 Prediciendo ROI futuro...")
    forecast_results = roi_analyzer.forecast_roi(historical_data)
    
    # Crear dashboard
    print("📈 Creando dashboard de ROI...")
    dashboard = roi_analyzer.create_roi_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de ROI...")
    export_data = roi_analyzer.export_roi_analysis()
    
    print("✅ Sistema de análisis de ROI avanzado completado!")






