"""
Marketing Brain Marketing Mix Optimizer
Motor avanzado de optimización de marketing mix
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

class MarketingMixOptimizer:
    def __init__(self):
        self.mix_data = {}
        self.optimization_models = {}
        self.channel_analysis = {}
        self.budget_optimization = {}
        self.attribution_models = {}
        self.mix_insights = {}
        self.optimization_results = {}
        
    def load_mix_data(self, mix_data):
        """Cargar datos de marketing mix"""
        if isinstance(mix_data, str):
            if mix_data.endswith('.csv'):
                self.mix_data = pd.read_csv(mix_data)
            elif mix_data.endswith('.json'):
                with open(mix_data, 'r') as f:
                    data = json.load(f)
                self.mix_data = pd.DataFrame(data)
        else:
            self.mix_data = pd.DataFrame(mix_data)
        
        print(f"✅ Datos de marketing mix cargados: {len(self.mix_data)} registros")
        return True
    
    def analyze_marketing_mix(self):
        """Analizar marketing mix"""
        if self.mix_data.empty:
            return None
        
        # Análisis por canal
        channel_analysis = self.mix_data.groupby('channel').agg({
            'budget': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'revenue': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        # Calcular métricas de performance
        channel_analysis['ctr'] = (channel_analysis['clicks'] / channel_analysis['impressions']) * 100
        channel_analysis['conversion_rate'] = (channel_analysis['conversions'] / channel_analysis['clicks']) * 100
        channel_analysis['roi'] = (channel_analysis['revenue'] - channel_analysis['cost']) / channel_analysis['cost']
        channel_analysis['roas'] = channel_analysis['revenue'] / channel_analysis['cost']
        channel_analysis['cpa'] = channel_analysis['cost'] / channel_analysis['conversions']
        channel_analysis['cpc'] = channel_analysis['cost'] / channel_analysis['clicks']
        
        # Análisis de eficiencia
        efficiency_analysis = self._analyze_channel_efficiency(channel_analysis)
        
        # Análisis de sinergias
        synergy_analysis = self._analyze_channel_synergies()
        
        # Análisis de estacionalidad
        seasonality_analysis = self._analyze_seasonality()
        
        mix_results = {
            'channel_analysis': channel_analysis.to_dict('records'),
            'efficiency_analysis': efficiency_analysis,
            'synergy_analysis': synergy_analysis,
            'seasonality_analysis': seasonality_analysis,
            'total_budget': channel_analysis['budget'].sum(),
            'total_revenue': channel_analysis['revenue'].sum(),
            'overall_roi': (channel_analysis['revenue'].sum() - channel_analysis['cost'].sum()) / channel_analysis['cost'].sum()
        }
        
        self.channel_analysis = mix_results
        return mix_results
    
    def _analyze_channel_efficiency(self, channel_analysis):
        """Analizar eficiencia de canales"""
        efficiency_metrics = {}
        
        # Score de eficiencia basado en múltiples métricas
        for _, channel in channel_analysis.iterrows():
            efficiency_score = 0
            
            # ROI (40% del score)
            roi = channel['roi']
            if roi > 3:
                efficiency_score += 40
            elif roi > 2:
                efficiency_score += 30
            elif roi > 1:
                efficiency_score += 20
            else:
                efficiency_score += 10
            
            # Conversion rate (30% del score)
            conversion_rate = channel['conversion_rate']
            if conversion_rate > 5:
                efficiency_score += 30
            elif conversion_rate > 3:
                efficiency_score += 20
            elif conversion_rate > 1:
                efficiency_score += 10
            
            # CTR (20% del score)
            ctr = channel['ctr']
            if ctr > 3:
                efficiency_score += 20
            elif ctr > 2:
                efficiency_score += 15
            elif ctr > 1:
                efficiency_score += 10
            
            # Cost efficiency (10% del score)
            cpa = channel['cpa']
            if cpa < 50:
                efficiency_score += 10
            elif cpa < 100:
                efficiency_score += 7
            elif cpa < 200:
                efficiency_score += 5
            
            efficiency_metrics[channel['channel']] = {
                'efficiency_score': efficiency_score,
                'roi': roi,
                'conversion_rate': conversion_rate,
                'ctr': ctr,
                'cpa': cpa
            }
        
        # Clasificar canales por eficiencia
        efficiency_categories = {
            'high_efficiency': [],
            'medium_efficiency': [],
            'low_efficiency': []
        }
        
        for channel, metrics in efficiency_metrics.items():
            score = metrics['efficiency_score']
            if score >= 80:
                efficiency_categories['high_efficiency'].append(channel)
            elif score >= 60:
                efficiency_categories['medium_efficiency'].append(channel)
            else:
                efficiency_categories['low_efficiency'].append(channel)
        
        return {
            'efficiency_metrics': efficiency_metrics,
            'efficiency_categories': efficiency_categories
        }
    
    def _analyze_channel_synergies(self):
        """Analizar sinergias entre canales"""
        if 'date' not in self.mix_data.columns:
            return {}
        
        # Análisis de correlaciones entre canales
        channel_correlations = {}
        
        # Crear matriz de canales por fecha
        self.mix_data['date'] = pd.to_datetime(self.mix_data['date'])
        daily_mix = self.mix_data.groupby(['date', 'channel'])['revenue'].sum().unstack(fill_value=0)
        
        # Calcular correlaciones
        correlation_matrix = daily_mix.corr()
        
        # Identificar sinergias fuertes
        strong_synergies = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if corr_value > 0.7:  # Correlación fuerte
                    strong_synergies.append({
                        'channel1': correlation_matrix.columns[i],
                        'channel2': correlation_matrix.columns[j],
                        'correlation': corr_value,
                        'synergy_type': 'positive'
                    })
                elif corr_value < -0.7:  # Correlación negativa fuerte
                    strong_synergies.append({
                        'channel1': correlation_matrix.columns[i],
                        'channel2': correlation_matrix.columns[j],
                        'correlation': corr_value,
                        'synergy_type': 'negative'
                    })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_synergies': strong_synergies,
            'total_synergies': len(strong_synergies)
        }
    
    def _analyze_seasonality(self):
        """Analizar estacionalidad del marketing mix"""
        if 'date' not in self.mix_data.columns:
            return {}
        
        # Análisis de estacionalidad por canal
        self.mix_data['month'] = pd.to_datetime(self.mix_data['date']).dt.month
        self.mix_data['quarter'] = pd.to_datetime(self.mix_data['date']).dt.quarter
        
        seasonal_analysis = {}
        
        # Análisis mensual
        monthly_analysis = self.mix_data.groupby(['channel', 'month']).agg({
            'revenue': 'sum',
            'cost': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Análisis trimestral
        quarterly_analysis = self.mix_data.groupby(['channel', 'quarter']).agg({
            'revenue': 'sum',
            'cost': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Identificar patrones estacionales
        seasonal_patterns = {}
        for channel in self.mix_data['channel'].unique():
            channel_data = monthly_analysis[monthly_analysis['channel'] == channel]
            if len(channel_data) > 0:
                revenue_variance = channel_data['revenue'].var()
                seasonal_patterns[channel] = {
                    'revenue_variance': revenue_variance,
                    'seasonality_strength': 'high' if revenue_variance > 1000000 else 'medium' if revenue_variance > 100000 else 'low'
                }
        
        return {
            'monthly_analysis': monthly_analysis.to_dict('records'),
            'quarterly_analysis': quarterly_analysis.to_dict('records'),
            'seasonal_patterns': seasonal_patterns
        }
    
    def build_mix_optimization_model(self, target_variable='revenue'):
        """Construir modelo de optimización de marketing mix"""
        if target_variable not in self.mix_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos para modelado
        # Crear variables dummy para canales
        channel_dummies = pd.get_dummies(self.mix_data['channel'], prefix='channel')
        
        # Combinar variables
        feature_columns = ['budget', 'impressions', 'clicks', 'cost']
        available_features = [col for col in feature_columns if col in self.mix_data.columns]
        
        X = pd.concat([self.mix_data[available_features], channel_dummies], axis=1)
        y = self.mix_data[target_variable]
        
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
            'feature_importance': dict(zip(X.columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.optimization_models['mix_optimizer'] = {
            'model': model,
            'feature_columns': X.columns.tolist(),
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def optimize_budget_allocation(self, total_budget, optimization_goal='revenue'):
        """Optimizar asignación de presupuesto"""
        if 'mix_optimizer' not in self.optimization_models:
            raise ValueError("Modelo de optimización de marketing mix no encontrado")
        
        model_info = self.optimization_models['mix_optimizer']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        scaler = model_info['scaler']
        
        # Obtener canales únicos
        channels = self.mix_data['channel'].unique()
        n_channels = len(channels)
        
        # Función objetivo
        def objective(x):
            # x es el vector de asignación de presupuesto por canal
            total_revenue = 0
            
            for i, channel in enumerate(channels):
                # Crear fila de datos para predicción
                prediction_data = np.zeros(len(feature_columns))
                
                # Asignar presupuesto
                budget_idx = feature_columns.index('budget')
                prediction_data[budget_idx] = x[i]
                
                # Asignar otras variables basadas en datos históricos
                channel_data = self.mix_data[self.mix_data['channel'] == channel]
                if len(channel_data) > 0:
                    avg_data = channel_data.mean()
                    
                    if 'impressions' in feature_columns:
                        impressions_idx = feature_columns.index('impressions')
                        prediction_data[impressions_idx] = avg_data.get('impressions', 0)
                    
                    if 'clicks' in feature_columns:
                        clicks_idx = feature_columns.index('clicks')
                        prediction_data[clicks_idx] = avg_data.get('clicks', 0)
                    
                    if 'cost' in feature_columns:
                        cost_idx = feature_columns.index('cost')
                        prediction_data[cost_idx] = x[i]  # Costo = presupuesto
                
                # Activar canal correspondiente
                channel_col = f'channel_{channel}'
                if channel_col in feature_columns:
                    channel_idx = feature_columns.index(channel_col)
                    prediction_data[channel_idx] = 1
                
                # Escalar datos
                prediction_data_scaled = scaler.transform([prediction_data])
                
                # Predecir revenue
                predicted_revenue = model.predict(prediction_data_scaled)[0]
                total_revenue += predicted_revenue
            
            if optimization_goal == 'revenue':
                return -total_revenue  # Maximizar revenue
            elif optimization_goal == 'roi':
                total_cost = sum(x)
                roi = (total_revenue - total_cost) / total_cost if total_cost > 0 else 0
                return -roi  # Maximizar ROI
            else:
                return -total_revenue
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}  # Suma debe ser igual al presupuesto total
        ]
        
        # Límites (cada canal debe recibir al menos 5% y máximo 50%)
        bounds = [(total_budget * 0.05, total_budget * 0.5) for _ in range(n_channels)]
        
        # Punto inicial (distribución uniforme)
        x0 = np.ones(n_channels) * (total_budget / n_channels)
        
        # Optimización
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        # Resultados de optimización
        optimal_allocation = {}
        for i, channel in enumerate(channels):
            optimal_allocation[channel] = {
                'allocated_budget': result.x[i],
                'allocation_percentage': (result.x[i] / total_budget) * 100,
                'current_budget': self.mix_data[self.mix_data['channel'] == channel]['budget'].sum(),
                'current_percentage': (self.mix_data[self.mix_data['channel'] == channel]['budget'].sum() / total_budget) * 100
            }
        
        # Calcular impacto esperado
        expected_revenue = -result.fun
        expected_roi = (expected_revenue - total_budget) / total_budget
        
        optimization_results = {
            'optimal_allocation': optimal_allocation,
            'expected_revenue': expected_revenue,
            'expected_roi': expected_roi,
            'optimization_goal': optimization_goal,
            'total_budget': total_budget,
            'optimization_status': result.success
        }
        
        self.budget_optimization = optimization_results
        return optimization_results
    
    def build_attribution_model(self, model_type='shapley'):
        """Construir modelo de atribución"""
        if 'customer_id' not in self.mix_data.columns:
            return None
        
        # Preparar datos para atribución
        customer_data = self.mix_data.groupby('customer_id').agg({
            'channel': lambda x: list(x),
            'revenue': 'sum',
            'cost': 'sum',
            'conversions': 'sum'
        })
        
        if model_type == 'shapley':
            attribution_results = self._calculate_shapley_attribution(customer_data)
        elif model_type == 'linear':
            attribution_results = self._calculate_linear_attribution(customer_data)
        elif model_type == 'time_decay':
            attribution_results = self._calculate_time_decay_attribution(customer_data)
        else:
            attribution_results = self._calculate_first_click_attribution(customer_data)
        
        self.attribution_models[model_type] = attribution_results
        return attribution_results
    
    def _calculate_shapley_attribution(self, customer_data):
        """Calcular atribución de Shapley"""
        channel_contributions = {}
        
        for customer_id, data in customer_data.iterrows():
            channels = data['channel']
            if len(channels) > 1:
                # Distribuir crédito equitativamente entre canales
                credit_per_channel = data['revenue'] / len(channels)
                
                for channel in channels:
                    if channel not in channel_contributions:
                        channel_contributions[channel] = 0
                    channel_contributions[channel] += credit_per_channel
        
        return {
            'model_type': 'shapley',
            'channel_contributions': channel_contributions,
            'total_attributed_revenue': sum(channel_contributions.values())
        }
    
    def _calculate_linear_attribution(self, customer_data):
        """Calcular atribución lineal"""
        channel_contributions = {}
        
        for customer_id, data in customer_data.iterrows():
            channels = data['channel']
            if len(channels) > 1:
                # Distribuir crédito linealmente
                credit_per_channel = data['revenue'] / len(channels)
                
                for channel in channels:
                    if channel not in channel_contributions:
                        channel_contributions[channel] = 0
                    channel_contributions[channel] += credit_per_channel
        
        return {
            'model_type': 'linear',
            'channel_contributions': channel_contributions,
            'total_attributed_revenue': sum(channel_contributions.values())
        }
    
    def _calculate_time_decay_attribution(self, customer_data):
        """Calcular atribución con decaimiento temporal"""
        channel_contributions = {}
        
        for customer_id, data in customer_data.iterrows():
            channels = data['channel']
            if len(channels) > 1:
                # Aplicar decaimiento temporal (más peso a canales recientes)
                total_weight = sum(range(1, len(channels) + 1))
                
                for i, channel in enumerate(channels):
                    weight = (i + 1) / total_weight
                    credit = data['revenue'] * weight
                    
                    if channel not in channel_contributions:
                        channel_contributions[channel] = 0
                    channel_contributions[channel] += credit
        
        return {
            'model_type': 'time_decay',
            'channel_contributions': channel_contributions,
            'total_attributed_revenue': sum(channel_contributions.values())
        }
    
    def _calculate_first_click_attribution(self, customer_data):
        """Calcular atribución de primer clic"""
        channel_contributions = {}
        
        for customer_id, data in customer_data.iterrows():
            channels = data['channel']
            if len(channels) > 0:
                # Dar todo el crédito al primer canal
                first_channel = channels[0]
                
                if first_channel not in channel_contributions:
                    channel_contributions[first_channel] = 0
                channel_contributions[first_channel] += data['revenue']
        
        return {
            'model_type': 'first_click',
            'channel_contributions': channel_contributions,
            'total_attributed_revenue': sum(channel_contributions.values())
        }
    
    def generate_mix_insights(self):
        """Generar insights de marketing mix"""
        insights = []
        
        # Insights de eficiencia de canales
        if self.channel_analysis:
            efficiency_analysis = self.channel_analysis.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            low_efficiency = efficiency_categories.get('low_efficiency', [])
            if low_efficiency:
                insights.append({
                    'category': 'Channel Efficiency',
                    'insight': f'{len(low_efficiency)} canales con baja eficiencia',
                    'recommendation': 'Revisar y optimizar canales de baja eficiencia',
                    'priority': 'high'
                })
        
        # Insights de sinergias
        if self.channel_analysis:
            synergy_analysis = self.channel_analysis.get('synergy_analysis', {})
            strong_synergies = synergy_analysis.get('strong_synergies', [])
            
            if strong_synergies:
                insights.append({
                    'category': 'Channel Synergies',
                    'insight': f'{len(strong_synergies)} sinergias fuertes identificadas',
                    'recommendation': 'Aprovechar sinergias entre canales para maximizar impacto',
                    'priority': 'medium'
                })
        
        # Insights de optimización de presupuesto
        if self.budget_optimization:
            budget_opt = self.budget_optimization
            if budget_opt['optimization_status']:
                expected_roi = budget_opt.get('expected_roi', 0)
                insights.append({
                    'category': 'Budget Optimization',
                    'insight': f'ROI esperado con optimización: {expected_roi:.1%}',
                    'recommendation': 'Implementar nueva asignación de presupuesto',
                    'priority': 'high'
                })
        
        # Insights de atribución
        if self.attribution_models:
            attribution = self.attribution_models.get('shapley', {})
            if attribution and 'channel_contributions' in attribution:
                contributions = attribution['channel_contributions']
                top_contributor = max(contributions, key=contributions.get)
                insights.append({
                    'category': 'Attribution',
                    'insight': f'{top_contributor} es el mayor contribuidor según modelo Shapley',
                    'recommendation': 'Aumentar inversión en canales de alto impacto',
                    'priority': 'medium'
                })
        
        self.mix_insights = insights
        return insights
    
    def create_mix_dashboard(self):
        """Crear dashboard de optimización de marketing mix"""
        if not self.mix_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Channel Performance', 'Budget Optimization',
                          'Attribution Analysis', 'Channel Synergies'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Gráfico de performance de canales
        if self.channel_analysis:
            channel_analysis = self.channel_analysis.get('channel_analysis', [])
            if channel_analysis:
                channels = [channel['channel'] for channel in channel_analysis]
                roi_values = [channel['roi'] for channel in channel_analysis]
                
                fig.add_trace(
                    go.Bar(x=channels, y=roi_values, name='Channel ROI'),
                    row=1, col=1
                )
        
        # Gráfico de optimización de presupuesto
        if self.budget_optimization:
            budget_opt = self.budget_optimization.get('optimal_allocation', {})
            if budget_opt:
                channels = list(budget_opt.keys())
                allocations = [budget_opt[channel]['allocation_percentage'] for channel in channels]
                
                fig.add_trace(
                    go.Pie(labels=channels, values=allocations, name='Budget Allocation'),
                    row=1, col=2
                )
        
        # Gráfico de análisis de atribución
        if self.attribution_models:
            attribution = self.attribution_models.get('shapley', {})
            if attribution and 'channel_contributions' in attribution:
                contributions = attribution['channel_contributions']
                channels = list(contributions.keys())
                values = list(contributions.values())
                
                fig.add_trace(
                    go.Bar(x=channels, y=values, name='Channel Attribution'),
                    row=2, col=1
                )
        
        # Gráfico de sinergias entre canales
        if self.channel_analysis:
            synergy_analysis = self.channel_analysis.get('synergy_analysis', {})
            strong_synergies = synergy_analysis.get('strong_synergies', [])
            if strong_synergies:
                synergy_names = [f"{syn['channel1']}-{syn['channel2']}" for syn in strong_synergies]
                synergy_values = [syn['correlation'] for syn in strong_synergies]
                
                fig.add_trace(
                    go.Scatter(x=synergy_names, y=synergy_values, mode='markers', name='Channel Synergies'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Optimización de Marketing Mix",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_mix_analysis(self, filename='marketing_mix_optimization_analysis.json'):
        """Exportar análisis de marketing mix"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'channel_analysis': self.channel_analysis,
            'optimization_models': {k: {'metrics': v['metrics']} for k, v in self.optimization_models.items()},
            'budget_optimization': self.budget_optimization,
            'attribution_models': self.attribution_models,
            'mix_insights': self.mix_insights,
            'summary': {
                'total_channels': len(self.mix_data['channel'].unique()) if 'channel' in self.mix_data.columns else 0,
                'total_budget': self.mix_data['budget'].sum() if 'budget' in self.mix_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de marketing mix exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de marketing mix
    mix_optimizer = MarketingMixOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'channel': np.random.choice(['Google Ads', 'Facebook', 'Instagram', 'Email', 'SMS', 'Website'], 1000),
        'customer_id': np.random.randint(1, 500, 1000),
        'budget': np.random.normal(10000, 2000, 1000),
        'impressions': np.random.poisson(100000, 1000),
        'clicks': np.random.poisson(5000, 1000),
        'conversions': np.random.poisson(500, 1000),
        'revenue': np.random.normal(50000, 10000, 1000),
        'cost': np.random.normal(15000, 3000, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de marketing mix
    print("📊 Cargando datos de marketing mix...")
    mix_optimizer.load_mix_data(sample_data)
    
    # Analizar marketing mix
    print("📈 Analizando marketing mix...")
    mix_analysis = mix_optimizer.analyze_marketing_mix()
    
    # Construir modelo de optimización
    print("🔮 Construyendo modelo de optimización...")
    optimization_model = mix_optimizer.build_mix_optimization_model()
    
    # Optimizar asignación de presupuesto
    print("💰 Optimizando asignación de presupuesto...")
    budget_optimization = mix_optimizer.optimize_budget_allocation(100000, 'revenue')
    
    # Construir modelo de atribución
    print("🎯 Construyendo modelo de atribución...")
    attribution_model = mix_optimizer.build_attribution_model('shapley')
    
    # Generar insights de marketing mix
    print("💡 Generando insights de marketing mix...")
    mix_insights = mix_optimizer.generate_mix_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de marketing mix...")
    dashboard = mix_optimizer.create_mix_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de marketing mix...")
    export_data = mix_optimizer.export_mix_analysis()
    
    print("✅ Sistema de optimización de marketing mix completado!")






